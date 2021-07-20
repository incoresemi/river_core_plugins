# See LICENSE for details

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


def gen_cmd_list(dut_config_file, work_dir, linker_dir, module, output_dir,
                 module_dir, gen_cvg):

    logger.debug('Generating commands for gen plugin')
    run_command = []
    run_command.append(
        "uarch_test --verbose debug --config_file {0} --gen_test --work_dir {1} --modules {2} --linker_dir {3} {4}"
        .format(dut_config_file, work_dir, module, linker_dir, gen_cvg))
    logger.debug(run_command)
    return run_command


def idfnc(val):
    return 'Generating Test-list using uarch_test'


def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        test_list = gen_cmd_list(metafunc.config.getoption("configfile"),
                                 metafunc.config.getoption("work_dir"),
                                 metafunc.config.getoption("linker_dir"),
                                 metafunc.config.getoption("module"),
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("module_dir"),
                                 metafunc.config.getoption("gen_cvg"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request, autouse=True):
    program = request.param
    (ret, out, err) = utils.sys_command(program, timeout=3000)
    return ret


def test_eval(test_input):
    assert test_input == 0
