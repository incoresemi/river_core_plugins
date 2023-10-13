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


def compile_cmd_list(make_file, work_dir, key_list):

    run_commands = []

    # Hmm here the key_list becomes a string need to do some magic to get into proper list
    # RE Magic here
    replacements = {"[": "", "]": "", "'": "", " ": ""}
    replacements = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(replacements.keys()))
    str_key_list = pattern.sub(lambda m: replacements[re.escape(m.group(0))],
                               key_list)
    key_list = str_key_list.split(",")

    for file_name in key_list:
        logger.debug(
            "Creating Makefile command for {0} to build ASM files".format(
                file_name))
        run_commands.append('make -f {0} {1}'.format(
            make_file, file_name))
    return run_commands


def idfnc(val):
    return val


def pytest_generate_tests(metafunc):

    if 'test_input' in metafunc.fixturenames:
        logger.debug('Generating commands from pytest_framework')
        test_list = compile_cmd_list(
            # metafunc.config.getoption("output_dir"),
            metafunc.config.getoption("make_file"),
            metafunc.config.getoption("work_dir"),
            metafunc.config.getoption("key_list"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request):
    # compile tests
    logger.debug('Generating commands from test_input fixture')
    program = request.param
    stage = program.split()[-1]
    (ret, out, err) = sys_command(program, timeout=5000)
    return ret, err, stage

def test_eval(test_input):
    assert test_input[
        0] == 0, "Tests failed because of {0} at {1} stage".format(
            test_input[1], test_input[2])