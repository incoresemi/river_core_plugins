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


def compile_cmd_list(output_dir, asm_dir, yaml_config):

    run_commands = []
    make_file = os.path.join(output_dir, 'Makefile.chromite')
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
        # Elf2hex
        elf2hex_bin = chromite_yaml_config['elf2hex']['command']
        # Sim
        sim_bin = chromite_yaml_config['sim']['command']

        # # Get files from the directory
        # asm_files = glob.glob(asm_dir+'*.S')
    os.chdir(output_dir)
    with open(make_file, "w") as makefile:
        makefile.write("ASM_SRC_DIR := " + asm_dir + asm)
        makefile.write("\nCRT_FILE := " + asm_dir + crt_file)
        makefile.write("\n\nchromite-build: $ASM_SRC_DIR/%.S")
        makefile.write("\n     $(info ===== Starting build ====== )")
        makefile.write("\n     " + gcc_compile_bin + " " + gcc_compile_args + " -I " + asm_dir + include_dir + " -o $@ $< $(CRT_FILE) " + linker_args + " $(<D)/$*.ld")
        makefile.write("\n\n.PHONY : chromite-build")
        logger.debug('Generating commands from gen_framework')
    return run_commands


def idfnc(val):
    return val


def pytest_generate_tests(metafunc):

    if 'test_input' in metafunc.fixturenames:
        # TODO Change
        logger.debug('Generating commands from pytest_framework')
        test_list = compile_cmd_list(
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("asm_dir"),
                                 metafunc.config.getoption("yaml_config"))
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
    # if run_list(compile_cmd_list[program], program):
    #     # TODO Change
    # sys_command('touch STATUS_PASSED')
    return 0
    # else:
    #     return 1


def test_eval(test_input):
    assert test_input == 0
