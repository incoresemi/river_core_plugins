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

from river_core.log import logger
from river_core.utils import *

compile_hookimpl = pluggy.HookimplMarker('compile')


class ChromitePlugin(object):
    '''
        Plugin to set chromite as the target
    '''

    @compile_hookimpl
    def pre_compile(self, ini_config, yaml_config, output_dir):
        logger.debug('Pre Compile Stage')
        # Get plugin specific configs from ini
        self.jobs = ini_config['jobs']
        # self.seed = ini_config['seed']
        self.filter = ini_config['filter']
        # TODO Might  be useful later on
        # Eventually add support for riscv_config
        self.isa = ini_config['isa']
        # Check if dir exists
        if (os.path.isdir(output_dir)):
            logger.debug('Directory exists')
            shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir + '/chromite_plugin')
        # Generic commands
        self.compile_output_path = output_dir + 'chromite_plugin'
        self.regress_list = '{0}/regresslist.yaml'.format(self.compile_output_path)
        self.output_dir = output_dir + '/chromite_plugin'
        # Save YAML to load again in gen_framework.yaml
        self.yaml_config = yaml_config

    @compile_hookimpl
    def compile(self, compile_config, module_dir, asm_dir):
        logger.debug('Compile Hook')
        logger.debug('Module dir: {0}'.format(module_dir))
        pytest_file = module_dir + '/chromite_plugin/gen_framework.py'
        logger.debug('Pytest file: {0}'.format(pytest_file))

        # TODO Regression list currently removed, check back later
        # TODO The logger doesn't exactly work like in the pytest module
        # pytest.main([pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter), '-v', '--compileconfig={0}'.format(compile_config), '--html=compile.html', '--self-contained-html'])
        pytest.main([pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter), '--html={0}/compile.html'.format(self.compile_output_path), '--self-contained-html', '--output_dir={0}'.format(self.output_dir), '--asm_dir={0}'.format(asm_dir), '--yaml_config={0}'.format(self.yaml_config)])
        # , '--regress_list={0}'.format(self.regress_list), '-v', '--compile_config={0}'.format(compile_config),

    @compile_hookimpl
    def post_compile(self):
        logger.debug('post compile')
