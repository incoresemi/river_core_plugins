# See LICENSE for details

import os
import sys
import pluggy
import shutil
import yaml
import random
import re
import datetime
import pytest
import glob

from river_core.log import logger
from river_core.utils import *

dut_hookimpl = pluggy.HookimplMarker('dut')


class ChromitePlugin(object):
    '''
        Plugin to set chromite as the target
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

        # Check if chromite is installed?
        self.installation = ini_config['installed']
        # Check if dir exists
        # if (os.path.isdir(output_dir)):
        #     logger.debug('Directory exists')
        #     shutil.rmtree(output_dir, ignore_errors=True)
        # os.makedirs(output_dir + '/chromite_plugin')
        # Generic commands
        self.compile_output_path = output_dir + 'chromite_plugin'
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

        # Help setup Chromite, if not set in path
        if self.installation is False:
            logger.info(
                "Attempting to install the core into your home directory")
            logger.info(
                "Please ensure you have installed the requirements from https://chromite.readthedocs.io/en/latest/getting_started.html"
            )
            response = input(
                "Please respond with N/n, if you don't want to install and exit or if you don't have the requirements installed"
            )
            if response == ('n', 'N'):
                raise SystemExit
            else:
                logger.info("Continuing with the installation")
            # TODO Get this from the user maybe?
            os.chdir(os.path.expanduser('~') + '/cores')
            # https://chromite.readthedocs.io/en/latest/getting_started.html#building-the-core
            try:
                sys_command(
                    'git clone https://gitlab.com/incoresemi/core-generators/chromite.git',
                    1000)
                sys_command('cd chromite')
                sys_command('pip install -U -r chromite/requirements.txt', 600)
                # TODO Change this to something that user specifies maybe?
                sys_command(
                    'python -m configure.main -ispec sample_config/default.yaml'
                )
                sys_command('make -j $(nproc) generate_verilog')
                sys_command('make link_verilator')
                logger.info('Setup is now complete')
            except:
                raise SystemExit(
                    'Something went wrong while getting things ready')

    @dut_hookimpl
    def build(self, asm_dir, asm_gen):
        logger.debug('Build Hook')
        make_file = os.path.join(asm_dir, 'Makefile.chromite')
        # Load YAML file
        logger.debug('Load Original YAML file i.e {0}'.format(
            self.yaml_config))
        with open(self.yaml_config, 'r') as cfile:
            chromite_yaml_config = yaml.safe_load(cfile)
            # TODO Check all necessary flags
            # Generic commands
            abi = chromite_yaml_config['abi']
            arch = chromite_yaml_config['arch']
            # GCC Specific
            gcc_compile_bin = chromite_yaml_config['gcc']['command']
            gcc_compile_args = chromite_yaml_config['gcc']['args']
            include_dir = chromite_yaml_config['gcc']['include']
            asm = chromite_yaml_config['gcc']['asm_dir']
            # Linker
            linker_bin = chromite_yaml_config['linker']['ld']
            linker_args = chromite_yaml_config['linker']['args']
            crt_file = chromite_yaml_config['linker']['crt']
            # Spike
            spike_bin = chromite_yaml_config['spike']['command']
            # Disass
            objdump_bin = chromite_yaml_config['objdump']['command']
            objdump_args = chromite_yaml_config['objdump']['args']
            # Elf2hex
            elf2hex_bin = chromite_yaml_config['elf2hex']['command']
            elf2hex_args = chromite_yaml_config['elf2hex']['args']
            # Sim
            sim_bin = chromite_yaml_config['sim']['command']
            sim_args = chromite_yaml_config['sim']['args']
            sim_path = chromite_yaml_config['sim']['path']

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
                makefile.write("\nROOT_DIR := chromite")
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
                makefile.write(
                    "\n\t$(info ===== Now Running on Chromite =====)")
                makefile.write("\n\tmkdir -p $(basename $@)")
                makefile.write("\n\t$(info ===== Creating code.mem ===== )")
                makefile.write("\n\t" + elf2hex_bin + " " +
                               str(elf2hex_args[0]) + " " +
                               str(elf2hex_args[1]) + " $< " +
                               str(elf2hex_args[2]) +
                               " > $(basename $@)/code.mem ")
                makefile.write("\n\tcd $(basename $@)")
                makefile.write(
                    "\n\t $(info ===== Copying chromite_core and files ===== )"
                )
                makefile.write("\n\tln -sf " + sim_path + "boot.mem " + sim_path +
                               "chromite_core .")
                makefile.write(
                    "\n\t$(info ===== Now running chromite core ===== )")
                makefile.write("\n\t ./" + sim_bin + " " + sim_args)
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
        pytest_file = module_dir + '/chromite_plugin/gen_framework.py'
        logger.debug('Pytest file: {0}'.format(pytest_file))

        report_file_name = '{0}/chromite_{1}'.format(
                self.report_dir,
                datetime.datetime.now().strftime("%Y%m%d-%H%M"))

        # TODO Regression list currently removed, check back later
        # TODO The logger doesn't exactly work like in the pytest module
        # pytest.main([pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter), '-v', '--compileconfig={0}'.format(compile_config), '--html=compile.html', '--self-contained-html'])
        pytest.main([
            pytest_file,
            '-n={0}'.format(self.jobs),
            '-k={0}'.format(self.filter),
            # '--html={0}.html'.format(report_file_name),
            '--report-log={0}.json'.format(report_file_name),
            # '--self-contained-html',
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
        log_dir = self.output_dir + 'work/chromite/sim/'
        log_files = glob.glob(log_dir + '*/rtl.dump')
        logger.debug("Detected Chromite Log Files: {0}".format(log_files))
        return log_files
