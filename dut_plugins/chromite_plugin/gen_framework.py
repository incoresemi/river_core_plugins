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
import filecmp
import glob

from river_core.log import logger
from river_core.utils import *


def compile_cmd_list(asm_dir, yaml_config, gen_suite):

    run_commands = []
    make_file = os.path.join(asm_dir, 'Makefile.chromite')
    # Load YAML file
    logger.debug('Load Original YAML file i.e {0}'.format(yaml_config))
    with open(yaml_config, 'r') as cfile:
        chromite_yaml_config = yaml.safe_load(cfile)
        # TODO Check all necessary flags
        # Generic commands
        abi = chromite_yaml_config['abi']
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
    if gen_suite == 'aapg':
        make_file = make_file+'.aapg'
        with open(make_file, "w") as makefile:
            makefile.write("# auto generated makefile created by river_core compile for aapg based asm files")
            makefile.write("\n# generated on: {0}\n".format(datetime.datetime.now()))
            # get the variables into the file
            makefile.write("\nASM_SRC_DIR := " + asm_dir + asm)
            makefile.write("\nCRT_FILE := " + asm_dir + crt_file)
            makefile.write("\nBIN_DIR := bin")
            makefile.write("\nOBJ_DIR := objdump")
            makefile.write("\nSIM_DIR := sim")
            makefile.write("\nBASE_SRC_FILES := $(wildcard $(ASM_SRC_DIR)/*.S) \nSRC_FILES := $(filter-out $(wildcard $(ASM_SRC_DIR)/*template.S),$(BASE_SRC_FILES))\nBIN_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(BIN_DIR)/%.riscv, $(SRC_FILES))\nOBJ_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(OBJ_DIR)/%.objdump, $(SRC_FILES))\nSIM_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(SIM_DIR)/%.log, $(SRC_FILES))")
            # Add all section
            makefile.write("\n\nall: build objdump sim")
            makefile.write("\n\t$(info ===== All steps are now finished ====== )")
            # Main part for compliing
            makefile.write("\n\nbuild: $(BIN_FILES)")
            makefile.write("\n\t$(info ===== Build complete ====== )")
            makefile.write("\n\n$(BIN_DIR)/%.riscv: $(ASM_SRC_DIR)/%.S")
            makefile.write("\n\t$(info ================ Compiling asm to binary ============)")
            makefile.write("\n\t" + gcc_compile_bin + " " + gcc_compile_args + " -I " + asm_dir + include_dir + " -o $@ $< $(CRT_FILE) " + linker_args + " $(<D)/$*.ld")
            # Create an objdump file
            makefile.write("\n\nobjdump: $(OBJ_FILES)")
            makefile.write("\n\t$(info ========= Objdump Completed ============)")
            makefile.write("\n\t$(info )")

            makefile.write("\n$(OBJ_DIR)/%.objdump: $(BIN_DIR)/%.riscv")
            makefile.write("\n\t$(info ========== Disassembling binary ===============)")
            makefile.write("\n\t" + objdump_bin + " " + objdump_args + " " + "$< > $@")
            # Run on target
            makefile.write("\n\n.ONESHELL:")
            makefile.write("\nsim: $(SIM_FILES)")
            makefile.write("\n$(SIM_DIR)/%.log: $(BIN_DIR)/%.riscv")
            makefile.write("\n\t$(info ===== Now Running on Chromite =====)")
            makefile.write("\n\tmkdir -p sim/$<")
            makefile.write("\n\t$(info ===== Creating code.mem ===== )")
            makefile.write("\n\t" + elf2hex_bin + " " + str(elf2hex_args[0]) + " " + str(elf2hex_args[1]) + " $< " + str(elf2hex_args[2]) + " > sim/$</code.mem ")
            makefile.write("\n\tcd sim/$<")
            makefile.write("\n\t $(info ===== Copying chromite_core and files ===== )")
            makefile.write("\n\tcp " + sim_path + "boot.mem " + sim_path + "chromite_core .")
            makefile.write("\n\t$(info ===== Now running chromite core ===== )")
            makefile.write("\n\t ./" + sim_bin + " " + sim_args)
            # makefile.write("\n\n.PHONY : build")

    if gen_suite == 'microtesk':
        make_file = make_file+'.microtesk'
        # TODO This implementation is still broken, because of file naming
        # difference in microtesk generation :
        with open(make_file, "w") as makefile:
            makefile.write("# Auto generated makefile created by river_core compile for microtesk based ASM files")
            makefile.write("\n# Generated on: {0}\n".format(datetime.datetime.now()))
            # Get simple data
            makefile.write("\nASM_SRC_DIR := asm")
            makefile.write("\nBIN_DIR := bin")
            makefile.write("\nSRC_FILES := $(wildcard $(ASM_SRC_DIR)/*.S)")
            makefile.write("\nBIN_FILES := $(patsubst $(ASM_SRC_DIR)/%.S, $(BIN_DIR)/%.riscv, $(SRC_FILES))")
            # Main part for compliing
            makefile.write("\n\nbuild: $(BIN_FILES)")
            makefile.write("\n\t$(info ===== Build complete ====== )")
            makefile.write("\n\n$(BIN_DIR)/%.riscv: $(ASM_SRC_DIR)/%.S")
            makefile.write("\n\t$(info ================ Compiling asm to binary ============)")
            makefile.write("\n\t" + gcc_compile_bin + " " + gcc_compile_args + " -o $@ " + linker_args + " $(<D)/$*.ld")
            makefile.write("\n\n.PHONY : build")
    # TODO Improve Logging for the following steps
    run_commands.append('make -f {0} build'.format(make_file))
    run_commands.append('make -f {0} objdump'.format(make_file))
    run_commands.append('make -f {0} sim'.format(make_file))
    return run_commands


def idfnc(val):
    return val


def pytest_generate_tests(metafunc):

    if 'test_input' in metafunc.fixturenames:
        logger.debug('Generating commands from pytest_framework')
        test_list = compile_cmd_list(
                                 # metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("asm_dir"),
                                 metafunc.config.getoption("yaml_config"),
                                 metafunc.config.getoption("gen_suite"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


# def run_list(cmd_list, program):
#     result = 0
#     # TODO Change
#     logger.debug('Generating commands from os pytest_framework')
#     for i in range(len(cmd_list)):
#         result, out, err = eval(cmd_list[i])
#         if result:
#             cmd = cmd_list[i]
#             if re.search('-gcc', cmd):
#                 sys_command('touch STATUS_FAIL_COMPILE')
#             elif re.search('spike ', cmd):
#                 sys_command('touch STATUS_FAIL_MODEL')
#             else:
#                 sys_command('touch STATUS_FAIL_STEPS')
#             return 1
#     return result


@pytest.fixture
def test_input(request):
    # compile tests
    logger.debug('Generating commands from test_input fixture')
    program = request.param
    (ret, out, err) = sys_command(program)
    return ret
    # if run_list(compile_cmd_list[program], program):
    #     # TODO Change
    # sys_command('touch STATUS_PASSED')
    # return 0
    # else:
    #     return 1


def test_eval(test_input):
    assert test_input == 0
