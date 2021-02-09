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


def compile_cmd_list(make_file, asm_dir):

    run_commands = []
    os.chdir(asm_dir)
    # TODO Improve Logging for the following steps
    run_commands.append('make -B -f {0} build'.format(make_file))
    run_commands.append('make -B -f {0} objdump'.format(make_file))
    run_commands.append('make -f {0} sim'.format(make_file))
    return run_commands


def idfnc(val):
    return val


def pytest_generate_tests(metafunc):

    if 'test_input' in metafunc.fixturenames:
        logger.debug('Generating commands from pytest_framework')
        test_list = compile_cmd_list(
            # metafunc.config.getoption("output_dir"),
            metafunc.config.getoption("make_file"),
            metafunc.config.getoption("asm_dir"))
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
