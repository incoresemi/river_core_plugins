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
import shlex

def gen_cmd_list(config, work_dir, linker_dir, module, output_dir, module_dir,
                 gen_cvg, modules_dir, alias_file, index_file, jobs):


    config = config.split(', ')
    logger.debug('Generating commands for gen plugin')
    
    uatg_command = (f"uatg generate --verbose debug"
                    f" --jobs {jobs}"
                    f" --index_file {index_file}"
                    f" --modules {module}"
                    f" --work_dir {work_dir}"
                    f" --linker_dir {linker_dir}"
                    f" --gen_test_list"
                    f" --module_dir {modules_dir}"
                    f" --configuration {config[0]}"
                    f" --configuration {config[1]}"
                    f" --configuration {config[2]}"
                    f" --configuration {config[3]}"
                    f" --configuration {config[4]}"
                    f" --alias_file {alias_file}")
    run_command = []
    run_command.append(uatg_command)
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
                                 metafunc.config.getoption("alias_file"),
                                 metafunc.config.getoption("index_file"),
                                 metafunc.config.getoption("jobs")
                                 )
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request, autouse=True):
    program = request.param
    (ret, out, err) = utils.sys_command(program, timeout=3000)
    return ret


def test_eval(test_input):
    assert test_input == 0
