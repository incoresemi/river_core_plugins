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
    def init(self, ini_config, test_list, work_dir, coverage_config):
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
        self.output_dir = asm_dir.replace('work/', '')
        self.compile_output_path = self.output_dir + 'chromite_plugin'
        self.regress_list = '{0}/chromite-regresslist.yaml'.format(
            self.compile_output_path)
        # Save YAML to load again in gen_framework.yaml
        self.test_list_yaml = test_list
        # Report output directory
        self.report_dir = self.output_dir + 'reports'
        # Check if dir exists
        if (os.path.isdir(self.report_dir)):
            logger.debug('Report Directory exists')
            # shutil.rmtree(output_dir, ignore_errors=True)
        else:
            os.makedirs(self.report_dir)

        self.coverage_config = coverage_config
        # Loading Coverage info if passed 
        if coverage_config:
            self.code_coverage = coverage_config['code']
            self.functional_coverage = coverage_config['functional']
            if self.code_coverage:
                logger.info("Code Coverage is enabled for this plugin")
            if self.functional_coverage:
                logger.info("Functional Coverage is enabled for this plugin")

        else:
            self.code_coverage =  ''
            self.functional_coverage = ''


    @dut_hookimpl
    def build(self) :
        logger.debug('Build Hook')
        make_file = os.path.join(asm_dir, 'Makefile.chromite')
        # Load YAML files
        logger.debug('Loading the plugin specific YAML from {0}'.format(
            self.config_yaml))
        config_file = open(self.config_yaml, 'r')
        config_yaml_data = yaml.safe_load(config_file)
        config_file.close()
        logger.debug('Load Test-List YAML file i.e {0}'.format(
            self.test_list_yaml))
        with open(self.test_list_yaml, 'r') as cfile:
            test_list_yaml_data = yaml.safe_load(cfile)
            # TODO Check all necessary flags
            # Generic commands
            key_list = list(test_list_yaml_data.keys())
            self.key_list = key_list
            # Load common things from config.yaml
            # Disass
            objdump_bin = config_yaml_data['objdump']['command']
            objdump_args = config_yaml_data['objdump']['args']
            # Elf2hex
            elf2hex_bin = config_yaml_data['elf2hex']['command']
            elf2hex_args = config_yaml_data['elf2hex']['args']
            # Sim
            sim_bin = config_yaml_data['sim']['command']
            sim_args = config_yaml_data['sim']['args']
            sim_path = config_yaml_data['sim']['path']
            cadence_bsv_lib_path = config_yaml_data['cadence'][
                'bs_verilog_lib']
            cadence_verilog_dir_path = config_yaml_data['cadence'][
                'verilog_dir']
            cadence_bsv_wrapper_lib_path = config_yaml_data['cadence'][
                'bsv_wrapper_path']
            sv_tb_top_path = config_yaml_data['sv_tb_top']['path']


            # Load teh Makefile
            os.chdir(asm_dir)
            make_file = make_file
            with open(make_file, "w") as makefile:
                makefile.write(
                    "# Auto generated makefile created by river_core compile based on test list yaml"
                )
                makefile.write("\n# generated on: {0}\n".format(
                    datetime.datetime.now()))
                # get the variables into the file
                # makefile.write("\nASM_SRC_DIR := " + asm_dir + asm)
                # makefile.write("\nCRT_FILE := " + asm_dir + crt_file)
                makefile.write("\nBIN_DIR := bin")
                makefile.write("\nOBJ_DIR := objdump")
                makefile.write("\nSIM_DIR := sim")
                makefile.write("\nBS_VERILOG_LIB :=" + cadence_bsv_lib_path)
                makefile.write("\nVERILOGDIR := " + cadence_verilog_dir_path)
                makefile.write("\nBSV_WRAPPER_PATH := " +cadence_bsv_wrapper_lib_path)
                makefile.write("\nSV_TB_TOP_PATH := " + sv_tb_top_path )

                # ROOT Dir for resutls
                makefile.write("\nROOT_DIR := chromite")
                for key in key_list:
                    abi = test_list_yaml_data[key]['mabi']
                    arch = test_list_yaml_data[key]['march']
                    isa = test_list_yaml_data[key]['isa']
                    work_dir = test_list_yaml_data[key]['work_dir']
                    file_name = key
                    # GCC Specific
                    gcc_compile_bin = test_list_yaml_data[key]['cc']
                    gcc_compile_args = test_list_yaml_data[key]['cc_args']
                    asm_file = test_list_yaml_data[key]['asm_file']
                    # Linker
                    linker_args = test_list_yaml_data[key]['linker_args']
                    linker_file = test_list_yaml_data[key]['linker_file']
                    crt_file = test_list_yaml_data[key]['crt_file']

                    # # Get files from the directory
                    # asm_files = glob.glob(asm_dir+'*.S')
                    # makefile.write(
                    #     "\nBASE_SRC_FILES := $(wildcard $(ASM_SRC_DIR)/*.S) \nSRC_FILES := $(filter-out $(wildcard $(ASM_SRC_DIR)/*template.S),$(BASE_SRC_FILES))\nBIN_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(ROOT_DIR)/$(BIN_DIR)/%.riscv, $(SRC_FILES))\nOBJ_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(ROOT_DIR)/$(OBJ_DIR)/%.objdump, $(SRC_FILES))\nSIM_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(ROOT_DIR)/$(SIM_DIR)/%.log, $(SRC_FILES))"
                    # )
                    # Add all section
                    # makefile.write("\n\nall: build objdump sim")
                    # makefile.write(
                    #     "\n\t$(info ===== All steps are now finished ====== )")
                    # Build for part one
                    makefile.write("\n\n{0}-build:".format(file_name))
                    makefile.write(
                        "\n\t$(info ================ Compiling asm to binary ============)"
                    )
                    makefile.write(
                        "\n\tmkdir -p $(ROOT_DIR)/$(BIN_DIR)/{0}".format(
                            file_name))
                    makefile.write("\n\t" + gcc_compile_bin + " " +
                                   gcc_compile_args +
                                   " -o $(ROOT_DIR)/$(BIN_DIR)/{0}/{0}.bin ".
                                   format(file_name) +
                                   "asm/{0}/{0}.S ".format(file_name) +
                                   crt_file + " " + linker_args + " " +
                                   "asm/{0}/".format(file_name) + linker_file)
                    # Create an objdump file
                    makefile.write("\n\n{0}-objdump:".format(file_name))
                    makefile.write(
                        "\n\t$(info ========== Disassembling binary ===============)"
                    )
                    makefile.write(
                        "\n\tmkdir -p $(ROOT_DIR)/$(OBJ_DIR)/{0}".format(
                            file_name))
                    makefile.write(
                        "\n\t" + objdump_bin + " " + objdump_args + " " +
                        "$(ROOT_DIR)/$(BIN_DIR)/{0}/{0}.bin > $(ROOT_DIR)/$(OBJ_DIR)/{0}/{0}.objdump"
                        .format(file_name))
                    # Run on target
                    makefile.write("\n\n.ONESHELL:")
                    makefile.write("\n{0}-sim:".format(file_name))
                    makefile.write(
                        "\n\tmkdir -p $(ROOT_DIR)/$(SIM_DIR)/{0}".format(
                            file_name))
                    # Add this extra portion to avoid waiting the simulation if already run,
                    # Remove later cause bad idea :)
                    makefile.write(
                        "\n\tif [ -f $(ROOT_DIR)/$(SIM_DIR)/{0}/rtl.dump ]".
                        format(file_name))
                    makefile.write("\n\tthen")
                    makefile.write("\n\t\texit")
                    makefile.write("\n\tfi")
                    makefile.write(
                        "\n\t$(info ===== Creating code.mem ===== )")
                    makefile.write("\n\t" + elf2hex_bin + " " +
                                   str(elf2hex_args[0]) + " " +
                                   str(elf2hex_args[1]) +
                                   " $(ROOT_DIR)/$(BIN_DIR)/{0}/{0}.bin ".
                                   format(file_name) + str(elf2hex_args[2]) +
                                   " > $(ROOT_DIR)/$(SIM_DIR)/{0}/code.mem ".
                                   format(file_name))
                    makefile.write(
                        "\n\tcd $(ROOT_DIR)/$(SIM_DIR)/{0}".format(file_name))
                    makefile.write(
                        "\n\t $(info ===== Copying chromite_core and files ===== )"
                    )
                    makefile.write(
                        "\n\t ls $(BSV_WRAPPER_PATH)*nc.v $(BSV_WRAPPER_PATH)*mul.v >$(BSV_WRAPPER_PATH)/bsvfilelist.txt"
                    )
                    makefile.write("\n\tln -sf " + sim_path + "boot.mem " +
                                   sim_path + "chromite_core .")
                    makefile.write("\n\t mkdir -p  work")
                    makefile.write("\n\techo \"define work ./work\" > cds.lib")
                    makefile.write("\n\techo \"define WORK work\" > hdl.var")
                    makefile.write(
                        "\n\tncvlog -64BIT -sv -cdslib ./cds.lib -hdlvar ./hdl.var +define+TOP=tb_top $(SV_TB_TOP_PATH)/tb_top.sv  $(BS_VERILOG_LIB)/main.v -v $(VERILOGDIR)/*.v -f $(BSV_WRAPPER_PATH)/bsvfilelist.txt -y $(BS_VERILOG_LIB)"
                    )
                # TODO change this to make with and without coverage - MOD
                    if self.code_coverage:
                        makefile.write(
                            "\n\t ncelab  -coverage ALL -cdslib ./cds.lib -hdlvar ./hdl.var work.main -timescale 1ns/1ps"
                        )
                    else:
                        makefile.write(
                            "\n\t ncelab -cdslib ./cds.lib -hdlvar ./hdl.var work.main -timescale 1ns/1ps"
                        )
                    makefile.write(
                        "\n\t echo \'ncsim +rtldump -cdslib ./cds.lib -hdlvar ./hdl.var work.main #> /dev/null\' > chromite_core"
                    )
                # TODO change this to make with and without coverage - MOD
                    if self.code_coverage:
                        # Coverage case
                        makefile.write("\n\t echo \'load "+ self.output_dir+ "$(ROOT_DIR)/$(SIM_DIR)/{0}/cov_work/scope/test/\' > imc_report.cmd".format(file_name))
                        makefile.write("\n\t echo \'exec mkdir -p coverage/reports\' >> imc_report.cmd")
                        makefile.write("\n\t echo \'exec mkdir -p coverage/report_html\' >> imc_report.cmd")
                        makefile.write("\n\t echo \'report -overwrite -out coverage/report_html -html -detail -metrics overall -all -aspect both -assertionStatus -allAssertionCounters -type *\' >>imc_report.cmd")
                        makefile.write("\n\t echo \'report -overwrite -out coverage/reports/coverage.fun_rpt -detail -metrics functional -all -aspect both -assertionStatus -allAssertionCounters -type *\' >> imc_report.cmd")
                        makefile.write("\n\t echo \'report -overwrite -out coverage/reports/coverage.code_rpt -detail -metrics code -all -aspect both -assertionStatus -allAssertionCounters -type *\' >> imc_report.cmd") 
                        makefile.write("\n\t echo \'imc -exec imc_report.cmd' >>chromite_core")
                    else:
                        # Non-coverage case
                        makefile.write("\n\t echo \'load "+ self.output_dir+ "$(ROOT_DIR)/$(SIM_DIR)/{0}/cov_work/scope/test/\' > imc_report.cmd".format(file_name))
                        makefile.write("\n\t echo \'exec mkdir -p coverage/reports\' >> imc_report.cmd")
                        makefile.write("\n\t echo \'exec mkdir -p coverage/report_html\' >> imc_report.cmd")
                        makefile.write("\n\t echo \'report -overwrite -out coverage/report_html -html -detail -metrics overall -all -aspect both -assertionStatus -allAssertionCounters -type *\' >>imc_report.cmd")
                        makefile.write("\n\t echo \'report -overwrite -out coverage/reports/coverage.fun_rpt -detail -metrics functional -all -aspect both -assertionStatus -allAssertionCounters -type *\' >> imc_report.cmd")
                        makefile.write("\n\t echo \'report -overwrite -out coverage/reports/coverage.code_rpt -detail -metrics code -all -aspect both -assertionStatus -allAssertionCounters -type *\' >> imc_report.cmd") 
                        makefile.write("\n\t echo \'imc -exec imc_report.cmd' >>chromite_core")

                    makefile.write(
                        "\n\t$(info ===== Now running chromite core ===== )")
                    #makefile.write("\n\t chmod +x chromite_core")
                    makefile.write("\n\t ./" + sim_bin + " " + sim_args +
                                   " > output_log")
                    makefile.write(
                        "\n\t cp rtl.dump {0}-dut_rc.dump".format(file_name))
                    # makefile.write("\n\n.PHONY : build")
                    makefile.write("\n\t cp -rf coverage"+" "+ self.output_dir+ "reports")
        raise SystemExit
        self.make_file = make_file

    @dut_hookimpl
    def run(self, module_dir, asm_dir):
        logger.debug('Run Hook')
        logger.debug('Module dir: {0}'.format(module_dir))
        pytest_file = module_dir + '/chromite_cadence_plugin/gen_framework.py'
        logger.debug('Pytest file: {0}'.format(pytest_file))

        report_file_name = '{0}/chromite_cadence_{1}'.format(
            self.report_dir,
            datetime.datetime.now().strftime("%Y%m%d-%H%M"))

        # TODO Regression list currently removed, check back later
        # TODO The logger doesn't exactly work like in the pytest module
        # pytest.main([pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter), '-v', '--compileconfig={0}'.format(compile_config), '--html=compile.html', '--self-contained-html'])
        # breakpoint()
        pytest.main([
            pytest_file,
            '-n={0}'.format(self.jobs),
            '-k={0}'.format(self.filter),
            # '--html={0}.html'.format(report_file_name),
            '--report-log={0}.json'.format(report_file_name),
            # '--self-contained-html',
            '--asm_dir={0}'.format(asm_dir),
            '--make_file={0}'.format(self.make_file),
            '--key_list={0}'.format(self.key_list),
            # TODO Debug parameters, remove later on
            '--log-cli-level=DEBUG',
            '-o log_cli=true',
        ])
        # , '--regress_list={0}'.format(self.regress_list), '-v', '--compile_config={0}'.format(compile_config),
        return report_file_name

    @dut_hookimpl
    def post_run(self):
        logger.debug('Post Run')
        log_dir = self.output_dir + 'chromite/sim/'
        log_files = glob.glob(log_dir + '*/*dut_rc.dump')
        logger.debug("Detected Chromite Log Files: {0}".format(log_files))
        return log_files
