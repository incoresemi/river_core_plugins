# See LICENSE for details

#import riscv_config.checker as riscv_config
#from riscv_config.errors import ValidationError
import os
import sys
import pluggy
import shutil
import yaml
import random
import re
import datetime
import pytest
from glob import glob
from river_core.log import logger
from river_core.utils import *
from river_core.constants import *

gen_hookimpl = pluggy.HookimplMarker("generator")


class AapgPlugin(object):
    """ Generator hook implementation """

    #@gen_hookimpl
    #def load_config(self, isa, platform):
    #    pwd = os.getcwd()

    #    try:
    #        isa_file, platform_file = riscv_config.check_specs(
    #                                    isa, platform, pwd, True)
    #    except ValidationError as msg:
    #        #logger.error(msg)
    #        print('error')
    #        sys.exit(1)

    # creates gendir and any setup related things
    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        '''

         Pre-Gen Stage.

         Check if the output_dir exists

         Add load plugin specific config

        '''

        # Check if the path exists or not
        logger.debug('AAPG Pre Gen Stage')
        if (os.path.isdir(output_dir)):
            logger.debug('exists')
            shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir)
        logger.debug('Extracting info from list')
        # Extract plugin specific info
        self.jobs = spec_config['jobs']
        self.seed = spec_config['seed']
        self.count = spec_config['count']
        self.filter = spec_config['filter']
        # TODO Might  be useful later on
        # Eventually add support for riscv_config
        self.isa = spec_config['isa']

    # gets the yaml file with list of configs; test count; parallel
    @gen_hookimpl
    def gen(self, gen_config, module_dir, output_dir):

        logger.debug('AAPG Plugin gen phase')
        logger.debug(module_dir)
        pytest_file = module_dir + '/aapg_plugin/gen_framework.py'
        logger.debug(pytest_file)

        # if norun:
        #     # to display test items
        #     pytest.main([pytest_file, '--collect-only', '-n={0}'.format(jobs), '-k={0}'.format(filter), '--configlist={0}'.format(gen_config), '-v',  '--seed={0}'.format(seed), '--count={0}'.format(count), '--html=aapg_gen.html', '--self-contained-html'])
        # else:
        pytest.main([
            pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter),
            '--configlist={0}'.format(gen_config), '-v',
            '--seed={0}'.format(self.seed), '--count={0}'.format(self.count),
            '--html={0}/aapg_gen.html'.format(output_dir),
            '--self-contained-html', '--output_dir={0}'.format(output_dir),
            '--module_dir={0}'.format(module_dir)
        ])

    # generates the regress list from the generation
    @gen_hookimpl
    def post_gen(self, output_dir, regressfile):
        test_dict = dict()
        test_files = []
        test_file = ''
        ld_file = ''
        test_dict['aapg'] = {}
        """
        Overwrites the aapg entries in the regressfile with the latest present in the gendir
        """
        remove_list = dict()
        test_dict['aapg']['aapg_global_testpath'] = output_dir
        if os.path.isdir(output_dir):
            output_dir_list = []
            for dirname in os.listdir(output_dir):
                if re.match('^aapg_.*', dirname):
                    test_dict['aapg'][dirname] = {
                        'testname': '',
                        'ld': '',
                        'template': ''
                    }
                    test_dict['aapg'][dirname]['testname'] = dirname + '.S'
                    test_dict['aapg'][dirname]['ld'] = dirname + '.ld'
                    test_dict['aapg'][dirname][
                        'template'] = dirname + '_template.S'

        if os.path.isfile(regressfile):
            with open(regressfile, 'r') as rgfile:
                testlist = yaml.safe_load(rgfile)
                testlist['aapg'].update(test_dict)
            rgfile.close()

        rgfile = open(regressfile, 'w')

        print(test_dict)
        yaml.safe_dump(test_dict, rgfile, default_flow_style=False)
