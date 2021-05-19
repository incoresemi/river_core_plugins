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


def gen_cmd_list(gen_config, jobs, randomize, isa, output_dir, module_dir):

    run_command = []
    logger.debug('Now generating commands for gen plugin')
    logger.debug("Generating tests for ISA: "+str(isa))
    if not os.path.exists(str(gen_config)):
        logger.error(str(gen_config)+" : File doesn't exist.")
        raise SystemExit
    config = utils.load_yaml(gen_config)
    try:
        config_node = config[isa]
    except Exception as e:
        logger.error("Error while accessing config node. Error Details: "+str(e))
        raise SystemExit

    logger.debug(config_node)

    if config_node['cgfs']:
        if config_node['absolute']:
            cgf_files = config_node['cgfs']
        else:
            cgf_files = [os.path.join(module_dir,x) for x in config_node['cgfs']]
    else:
        logger.error("No CGFs listed.")
        raise SystemExit

    run_command.append('riscv_ctg -v info -bi {0} -d {1} -p {2}'.format(config_node['bisa'], output_dir, jobs)+('' if not randomize else ' -r ') + ' -cf ' + ' -cf '.join(cgf_files))

    return run_command


def idfnc(val):
    template_match = re.finditer('-cf ([^\s]+)', '{0}'.format(val))
    logger.debug('{0}'.format(val))
    return 'Generating tests using cgf files: {0}'.format(" , ".join([x.group(1) for x in template_match]))


def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        test_list = gen_cmd_list(metafunc.config.getoption("configfile"),
                                 metafunc.config.getoption("jobs"),
                                 metafunc.config.getoption("randomize"),
                                 metafunc.config.getoption("isa"),
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("module_dir"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request, autouse=True):
    program = request.param
    (ret, out, err) = utils.sys_command(program,timeout=3000)
    return ret


def test_eval(test_input):
    assert test_input == 0
