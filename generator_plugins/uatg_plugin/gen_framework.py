# See LICENSE.incore for details
# Author Name: Alenkruth K M
# Author Email id: alenkruth.km@incoresemi.com
# Author Company: InCore Semiconductors Pvt. Ltd.

import os
import sys
import pluggy
import shutil
from river_core.log import logger
import river_core.utils as utils
from river_core.constants import *
import random
import re
import datetime
import pytest


def gen_cmd_list(config, work_dir, linker_dir, module, output_dir, module_dir,
                 gen_cvg, modules_dir, alias_file):

    logger.debug('Generating commands for gen plugin')
    run_command = []
    run_command.append(
        "uatg generate --verbose debug --configuration {0} --configuration {1} --configuration {2} --configuration {3} --module_dir {4} --work_dir {5} --modules {6} --linker_dir {7} --alias_file {8} {9}"
        .format(config[0], config[1], config[2], config[3], modules_dir,
                work_dir, module, linker_dir, alias_file, gen_cvg))
    logger.debug(run_command)
    return run_command


def idfnc(val):
    return 'Generating Test-list using UATG'


def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        test_list = gen_cmd_list(metafunc.config.getoption("config"),
                                 metafunc.config.getoption("work_dir"),
                                 metafunc.config.getoption("linker_dir"),
                                 metafunc.config.getoption("module"),
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("module_dir"),
                                 metafunc.config.getoption("gen_cvg"),
                                 metafunc.config.getoption("modules_dir"),
                                 metafunc.config.getoption("alias_file"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request, autouse=True):
    program = request.param
    (ret, out, err) = utils.sys_command(program, timeout=3000)
    return ret


def test_eval(test_input):
    assert test_input == 0
