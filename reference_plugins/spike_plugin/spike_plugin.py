# See LICENSE for details

import os
import sys
import pluggy
import shutil
import yaml
import random
import re
import glob
import datetime
import pytest

from river_core.log import logger
from river_core.utils import *

dut_hookimpl = pluggy.HookimplMarker('dut')


class SpikePlugin(object):
    '''
        Plugin to set Spike as ref
    '''
    @dut_hookimpl
    def init(self, ini_config, yaml_config, output_dir):
        logger.debug('Pre Compile Stage')
        # Get plugin specific configs from ini
        self.jobs = ini_config['jobs']
        # self.seed = ini_config['seed']
        self.filter = ini_config['filter']
        # TODO Might  be useful later on
        # Eventually add support for riscv_config
        self.isa = ini_config['isa']

        # Check if Spike is installed?
        self.installation = ini_config['installed']
        # Check if dir exists
        # if (os.path.isdir(output_dir)):
        #     logger.debug('Directory exists')
        #     shutil.rmtree(output_dir, ignore_errors=True)
        # os.makedirs(output_dir + '/chromite_plugin')
        # Generic commands
        self.compile_output_path = output_dir + 'spike_plugin'
        self.regress_list = '{0}/regresslist.yaml'.format(
            self.compile_output_path)
        self.output_dir = output_dir
        # Save YAML to load again in gen_framework.yaml
        self.yaml_config = yaml_config
        # Report output directory
        self.report_dir = self.output_dir + 'reports'
        # Check if dir exists
        if (os.path.isdir(self.report_dir)):
            logger.debug('Report Directory exists')
            # shutil.rmtree(output_dir, ignore_errors=True)
        else:
            os.makedirs(self.report_dir)

        # Help setup Spike, if not set in path
        # FIXME Get this checked by Neel and Pavan, could be some uncessary installtion.
        if self.installation is False:
            logger.info(
                "Attempting to install the spike into your home directory")
            logger.info(
                "Please ensure you have RISCV Toolchain installed in your path"
            )
            response = input(
                "Please respond with N/n, if you don't want to install and exit or if you don't have the requirements installed.\n IMP: If you have no standard install, or want to customize the installation, please go for manual mode of installation."
            )
            if response == ('n', 'N'):
                raise SystemExit
            else:
                logger.info("Continuing with the installation")
                logger.info('Setting the RISCV path to /opt/riscv')
            # TODO Get this from the user maybe?
            os.chdir(os.path.expanduser('~') + '/references')
            # https://chromite.readthedocs.io/en/latest/getting_started.html#building-the-core
            try:
                sys_command(
                    'git clone https://gitlab.com/shaktiproject/tools/mod-spike.git',
                    1000)
                sys_command('cd mod-spike')
                sys_command('git checkout bump-to-latest')
                sys_command(
                    'git clone https://github.com/riscv/riscv-isa-sim.git',
                    1000)
                sys_command('cd riscv-isa-sim')
                sys_command(
                    'git checkout 6d15c93fd75db322981fe58ea1db13035e0f7add')
                sys_command('git apply ../shakti.patch')
                logger.info('Setting the RISCV path to /opt/riscv')
                sys_command('export RISCV=/opt/riscv')
                sys_command('mkdir build')
                sys_command('cd build')
                sys_command('../configure --prefix=$RISCV')
                sys_command('make')
                logger.info(
                    'One tiny step is left, open a shell instance and complete the setup by running, sudo make install.'
                )
            except:
                raise SystemExit(
                    'Something went wrong while getting things ready')

    @dut_hookimpl
    def build(self, asm_dir, asm_gen):
        logger.debug('Build Hook')
        make_file = os.path.join(asm_dir, 'Makefile.spike')
        # Load YAML file
        logger.debug('Load Original YAML file i.e {0}'.format(
            self.yaml_config))
        with open(self.yaml_config, 'r') as cfile:
            spike_yaml_config = yaml.safe_load(cfile)
            # TODO Check all necessary flags
            # Generic commands
            abi = spike_yaml_config['abi']
            arch = spike_yaml_config['arch']
            # GCC Specific
            gcc_compile_bin = spike_yaml_config['gcc']['command']
            gcc_compile_args = spike_yaml_config['gcc']['args']
            include_dir = spike_yaml_config['gcc']['include']
            asm = spike_yaml_config['gcc']['asm_dir']
            # Linker
            linker_bin = spike_yaml_config['linker']['ld']
            linker_args = spike_yaml_config['linker']['args']
            crt_file = spike_yaml_config['linker']['crt']
            # Disass
            objdump_bin = spike_yaml_config['objdump']['command']
            objdump_args = spike_yaml_config['objdump']['args']
            # Elf2hex
            elf2hex_bin = spike_yaml_config['elf2hex']['command']
            elf2hex_args = spike_yaml_config['elf2hex']['args']
            # Sim
            sim_bin = spike_yaml_config['sim']['command']
            sim_args = spike_yaml_config['sim']['args']
            sim_path = spike_yaml_config['sim']['path']

            # # Get files from the directory
            # asm_files = glob.glob(asm_dir+'*.S')
        os.chdir(asm_dir)
        if asm_gen == 'aapg':
            make_file = make_file + '.aapg'
            with open(make_file, "w") as makefile:
                makefile.write(
                    "# auto generated makefile created by river_core compile for aapg based asm files"
                )
                makefile.write("\n# generated on: {0}\n".format(
                    datetime.datetime.now()))
                # get the variables into the file
                makefile.write("\nASM_SRC_DIR := " + asm_dir + asm)
                makefile.write("\nCRT_FILE := " + asm_dir + crt_file)
                makefile.write("\nBIN_DIR := bin")
                makefile.write("\nOBJ_DIR := objdump")
                makefile.write("\nSIM_DIR := sim")
                # ROOT Dir for resutls
                makefile.write("\nROOT_DIR := spike")
                makefile.write(
                    "\nBASE_SRC_FILES := $(wildcard $(ASM_SRC_DIR)/*.S) \nSRC_FILES := $(filter-out $(wildcard $(ASM_SRC_DIR)/*template.S),$(BASE_SRC_FILES))\nBIN_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(ROOT_DIR)/$(BIN_DIR)/%.riscv, $(SRC_FILES))\nOBJ_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(ROOT_DIR)/$(OBJ_DIR)/%.objdump, $(SRC_FILES))\nSIM_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(ROOT_DIR)/$(SIM_DIR)/%.log, $(SRC_FILES))"
                )
                # Add all section
                makefile.write("\n\nall: build objdump sim")
                makefile.write(
                    "\n\t$(info ===== All steps are now finished ====== )")
                # Main part for compliing
                makefile.write("\n\nbuild: $(BIN_FILES)")
                makefile.write("\n\t$(info ===== Build complete ====== )")
                makefile.write(
                    "\n\n$(ROOT_DIR)/$(BIN_DIR)/%.riscv: $(ASM_SRC_DIR)/%.S")
                makefile.write(
                    "\n\t$(info ================ Compiling asm to binary ============)"
                )
                makefile.write("\n\tmkdir -p $(ROOT_DIR)/$(BIN_DIR)")
                makefile.write("\n\t" + gcc_compile_bin + " " + "-march=" +
                               arch + " " + "-mabi=" + abi + " " +
                               gcc_compile_args + " -I " + asm_dir +
                               include_dir + " -o $@ $< $(CRT_FILE) " +
                               linker_args + " $(<D)/$*.ld")
                # Create an objdump file
                makefile.write("\n\nobjdump: $(OBJ_FILES)")
                makefile.write(
                    "\n\t$(info ========= Objdump Completed ============)")
                makefile.write("\n\t$(info )")

                makefile.write(
                    "\n$(ROOT_DIR)/$(OBJ_DIR)/%.objdump: $(ROOT_DIR)/$(BIN_DIR)/%.riscv"
                )
                makefile.write(
                    "\n\t$(info ========== Disassembling binary ===============)"
                )
                makefile.write("\n\tmkdir -p $(ROOT_DIR)/$(OBJ_DIR)")
                makefile.write("\n\t" + objdump_bin + " " + objdump_args +
                               " " + "$< > $@")
                # Run on target
                makefile.write("\n\n.ONESHELL:")
                makefile.write("\nsim: $(SIM_FILES)")
                makefile.write(
                    "\n$(ROOT_DIR)/$(SIM_DIR)/%.log: $(ROOT_DIR)/$(BIN_DIR)/%.riscv"
                )
                makefile.write("\n\t$(info ===== Now Running on Spike =====)")
                makefile.write("\n\tmkdir -p $(basename $@)")
                makefile.write("\n\t$(info ===== Creating binary  ===== )")
                # makefile.write("\n\tcp $< $(ROOT_DIR)/$(SIM_DIR)/$<")
                makefile.write("\n\tcd $(basename $@)")
                makefile.write("\n\t" + sim_bin + " " + sim_args + " --isa=" +
                               arch + " ../../../$< 2> ../../../$@ ")
                # makefile.write("\n\n.PHONY : build")

        if asm_gen == 'microtesk':
            make_file = make_file + '.microtesk'
            # TODO This implementation is still broken, because of file naming
            # difference in microtesk generation :
            with open(make_file, "w") as makefile:
                makefile.write(
                    "# Auto generated makefile created by river_core compile for microtesk based ASM files"
                )
                makefile.write("\n# Generated on: {0}\n".format(
                    datetime.datetime.now()))
                # Get simple data
                makefile.write("\nASM_SRC_DIR := asm")
                makefile.write("\nBIN_DIR := bin")
                makefile.write("\nSRC_FILES := $(wildcard $(ASM_SRC_DIR)/*.S)")
                makefile.write(
                    "\nBIN_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(BIN_DIR)/%.riscv, $(SRC_FILES))"
                )
                # Main part for compliing
                makefile.write("\n\nbuild: $(BIN_FILES)")
                makefile.write("\n\t$(info ===== Build complete ====== )")
                makefile.write("\n\n$(BIN_DIR)/%.riscv: $(ASM_SRC_DIR)/%.S")
                makefile.write(
                    "\n\t$(info ================ Compiling asm to binary ============)"
                )
                makefile.write("\n\t" + gcc_compile_bin + " " +
                               gcc_compile_args + " -o $@ " + linker_args +
                               " $(<D)/$*.ld")
                makefile.write("\n\n.PHONY : build")

        self.make_file = make_file

    @dut_hookimpl
    def run(self, module_dir, asm_dir):
        logger.debug('Run Hook')
        logger.debug('Module dir: {0}'.format(module_dir))
        pytest_file = module_dir + '/spike_plugin/gen_framework.py'
        logger.debug('Pytest file: {0}'.format(pytest_file))

        report_file_name = '{0}/spike_{1}'.format(
                self.report_dir,
                datetime.datetime.now().strftime("%Y%m%d-%H%M"))

        # TODO Regression list currently removed, check back later
        # TODO The logger doesn't exactly work like in the pytest module
        # pytest.main([pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter), '-v', '--compileconfig={0}'.format(compile_config), '--html=compile.html', '--self-contained-html'])
        pytest.main([
            pytest_file,
            '-n={0}'.format(self.jobs),
            '-k={0}'.format(self.filter),
            '--html={0}.html'.format(report_file_name),
            '--self-contained-html',
            '--report-log={0}.json'.format(report_file_name),
            '--asm_dir={0}'.format(asm_dir),
            '--make_file={0}'.format(self.make_file),
            # TODO Debug parameters, remove later on
            '--log-cli-level=DEBUG',
            '-o log_cli=true'
        ])
        # , '--regress_list={0}'.format(self.regress_list), '-v', '--compile_config={0}'.format(compile_config),
        return report_file_name

    @dut_hookimpl
    def post_run(self):
        logger.debug('Post Run')
        log_dir = self.output_dir + 'work/spike/sim/'
        log_files = glob.glob(log_dir + '*/spike.dump')
        logger.debug("Detected Spike Log Files:{0}".format(log_files))
        return log_files
