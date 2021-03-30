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
from envyaml import EnvYAML


def gen_cmd_list(gen_config, seed, count, output_dir, module_dir):

    logger.debug('Now generating commands for gen plugin')
    try:
        env_gen_list = EnvYAML(gen_config)
    except:
        logger.error("Is your plugin YAML file properly configured?")
        raise SystemExit

    inst_yaml_list = utils.load_yaml(gen_config)
    setup_dir = ''
    run_command = []
    for key, value in inst_yaml_list.items():
        if key == 'gen_binary_path':
            testfloat_bin = inst_yaml_list[key]
        dirname = output_dir + '/testfloat'

        if re.search('^instructions', key):

            rounding_mode_gen = ''
            inst_list = inst_yaml_list[key]['inst']
            # Using index so as to ensure that we can iterate both
            for inst_index in range(0, len(inst_list)):
                inst = inst_list[inst_index]
                # Get precision
                if '.s' in inst:
                    inst_prefix = 'f32'
                if '.d' in inst:
                    inst_prefix = 'f64'
                if '.q' in inst:
                    inst_prefix = 'f128'
                # Dest
                dest = inst_yaml_list[key]['dest'].split(',')
                dest = random.randint(int(dest[0]), int(dest[1]))
                dest_reg = 'f' + str(dest)
                # Register 1
                reg1 = inst_yaml_list[key]['reg1'].split(',')
                reg1 = random.randint(int(reg1[0]), int(reg1[1]))
                reg1_reg = 'f' + str(reg1)
                # Register 2
                reg2 = inst_yaml_list[key]['reg2'].split(',')
                reg2 = random.randint(int(reg2[0]), int(reg2[1]))
                reg2_reg = 'f' + str(reg2)
                rounding_mode = inst_yaml_list[key]['rounding-mode']
                tests_per_instruction = inst_yaml_list[key][
                    'tests_per_instruction']
                # Convert the string to values
                if rounding_mode == 'RNE':
                    rounding_mode = 0
                    rounding_mode_gen = '-rnear_even'
                elif rounding_mode == 'RTZ':
                    rounding_mode = 1
                    rounding_mode_gen = '-rminMag'
                elif rounding_mode == 'RDN':
                    rounding_mode = 2
                    rounding_mode_gen = '-rmin'
                elif rounding_mode == 'RUP':
                    rounding_mode = 3
                    rounding_mode_gen = '-rmax'
                elif rounding_mode == 'RMM':
                    rounding_mode = 4
                    rounding_mode_gen = '-rnear_maxMag'
                # Get other info
                template_name = os.path.basename(inst)
                for i in range(int(count)):
                    if seed == 'random':
                        gen_seed = random.randint(0, 10000)
                    else:
                        gen_seed = int(seed)

                    now = datetime.datetime.now()
                    gen_prefix = '{0:06}_{1}'.format(
                        gen_seed, now.strftime('%d%m%Y%H%M%S%f'))
                    test_prefix = 'testfloat_{0}_{1}_{2:05}'.format(
                        template_name, gen_prefix, i)
                    testdir = '{0}/asm/{1}'.format(dirname, test_prefix)
                    # Need to find a way to fix this, can't write to file this way
                    run_command.append('{0} \
                                        -seed {1} \
                                        -n {2} \
                                        {3} \
                                        {4}_{5} >> test '.format(
                        testfloat_bin, gen_seed, tests_per_instruction,
                        rounding_mode_gen, inst_prefix, inst[2:-2],
                        test_prefix))

    return run_command


def idfnc(val):
    return val


def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        test_list = gen_cmd_list(metafunc.config.getoption("configlist"),
                                 metafunc.config.getoption("seed"),
                                 metafunc.config.getoption("count"),
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("module_dir"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request):
    # compile tests
    logger.debug('Generating commands from test_input fixture')
    program = request.param
    (ret, out, err) = utils.sys_command(program)
    return ret, err


def test_eval(test_input):
    assert test_input == 0
