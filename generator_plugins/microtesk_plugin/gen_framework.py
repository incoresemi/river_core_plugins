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

    logger.debug('gen plugin')
    pwd = os.getcwd()
    try:
        env_gen_list = EnvYAML(gen_config)
    except:
        logger.error(
            "It seems that the MICROTESK_HOME is not exported\nPlease export for the current session of the shell"
        )
        raise SystemExit

    gen_list = utils.load_yaml(gen_config)
    gen_list['global_home'] = env_gen_list['global_home']
    ## schema validator should be here
    out = ''
    command = ''
    config_path = ''
    args = ''
    run_command = []
    for key, value in gen_list.items():
        if key == 'global_config_path':
            ## Here's the moduledir being used, earlier code a value from constant being loaded
            config_path = module_dir + gen_list[key]
        if key == 'global_command':
            command = 'bash {0}/bin/{1}'.format(gen_list['global_home'],
                                                gen_list[key])
        if key == 'global_args':
            args = gen_list[key]
        dirname = output_dir + '/microtesk'
        if not re.search('^global_', key):
            config_file_path = config_path + '/' + gen_list[key]['path']
            logger.debug(key)
            config_file = config_file_path + '/' + key + '.rb'

            logger.debug(config_file)
            template_name = os.path.basename(config_file)

            for i in range(int(count)):
                if seed == 'random':
                    gen_seed = random.randint(0, 1000000)
                else:
                    gen_seed = int(seed)

                now = datetime.datetime.now()
                gen_prefix = '{0:06}_{1}'.format(gen_seed,
                                                 now.strftime('%d%m%Y%H%M%S%f'))
                test_prefix = 'microtesk_{0}_{1}_{2:05}'.format(
                    template_name.replace('.rb', ''), gen_prefix, i)
                testdir = '{0}/asm/{1}'.format(dirname, test_prefix)
                run_command.append('{0} {1} \
                                    --code-file-extension S \
                                    --output-dir {2} \
                                    --code-file-prefix {3} \
                                    --rs {4} -g \
                                    '.format(command, config_file, testdir,
                                             test_prefix, gen_seed))

    return run_command


def idfnc(val):
    template_match = re.search('riscv (.*).rb', '{0}'.format(val))
    logger.debug('{0}'.format(val))
    return 'Generating {0}'.format(template_match.group(1))


def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        test_list = gen_cmd_list(metafunc.config.getoption("configlist"),
                                 metafunc.config.getoption("seed"),
                                 metafunc.config.getoption("count"),
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("module_dir"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request, autouse=True):
    # compile tests
    program = request.param
    template_match = re.search('riscv (.*).rb', program)
    if os.path.isfile('{0}.rb'.format(template_match.group(1))):
        (ret, out, err) = utils.sys_command(program)
        return ret
    else:
        logger.error('File not found {0}'.format(template_match.group(1)))
        return 1


def test_eval(test_input):
    assert test_input == 0
