# See LICENSE.incore for details
# Author Name: Alenkruth K M
# Author Email id: alenkruth.km@incoresemi.com
# Author Company: InCore Semiconductors Pvt. Ltd.

import os
import sys
import pluggy
from shutil import rmtree
import subprocess
import random
import re
import datetime
import pytest
import glob
import re
import configparser
import uatg

from uatg.utils import list_of_modules

from river_core.log import logger
import river_core.utils as utils
from river_core.constants import *

gen_hookimpl = pluggy.HookimplMarker("generator")


class uatg_plugin(object):

    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        """
           Spec Config will send in the yaml file as a 
           dictionary for the utg generator to use
           utg has not been configured to run mulitple jobs, YET
           as uarch test is ISA agnostic, we do not need those either
        """
        logger.debug("μArchitectural Test Generator, Pre-Gen.")
        self.name = 'uatg'
        output_dir = os.path.abspath(output_dir)
        if os.path.isdir(output_dir) and os.path.exists(output_dir):
            logger.debug('Output Directory exists. Removing Contents.')
            rmtree(output_dir)
        os.makedirs(output_dir)
        self.jobs = int(spec_config['jobs'])
        self.uarch_dir = os.path.dirname(uatg.__file__)
        logger.warn('UATG_dir is {0}'.format(self.uarch_dir))
        logger.warn('output_dir is {0}'.format(output_dir))
        self.work_dir = spec_config['work_dir']
        logger.debug("work dir is {0}".format(self.work_dir))
        self.linker_dir = os.path.abspath(spec_config['linker_dir'])
        if self.linker_dir:
            self.linker_dir = os.path.abspath(spec_config['linker_dir'])
        else:
            self.linker_dir = self.work_dir
            logger.warn('Default linker is used, uatg will generate the linker')
        logger.debug('linker_dir is {0}'.format(self.linker_dir))
        self.modules = spec_config['modules']
        # utg requires the modules to be specified as a string and not a list
        self.modules_str = self.modules
        # converting self.modules into a list from string
        self.modules = [x.strip() for x in self.modules.split(',')]
        self.modules_dir = os.path.abspath(spec_config['modules_dir'])
        self.config = []
        self.config.append(os.path.abspath(spec_config['config_isa']))
        self.config.append(os.path.abspath(spec_config['config_core']))
        self.config.append(os.path.abspath(spec_config['config_custom']))
        self.config.append(os.path.abspath(spec_config['config_csr_grouping']))
        self.config.append(os.path.abspath(spec_config['config_debug']))
        self.index_file = os.path.abspath(spec_config['index_file'])
        self.alias_file = os.path.abspath(spec_config['alias_file'])
        if 'paging_modes' not in spec_config:
            self.paging_modes = None
        else:
            self.paging_modes = spec_config['paging_modes']
        self.isa = spec_config['isa']
        if ((spec_config['generate_covergroups']).lower() == 'true'):
            self.cvg = '--gen_cvg'
            logger.debug('Generating covergroups')
        else:
            self.cvg = ''
            logger.debug('Not generating covergroups')
        logger.debug("μArchitectural Test Generator, Completed Pre-Gen Phase")

        march = self.isa.replace('S','').replace('U','').replace('Zicsr','').lower()
        if '32' in self.isa:
            self.xlen = 32
            self.mabi = 'ilp32'
            self.march = march
        else:
            self.xlen = 64
            self.march = march
            self.mabi = 'lp64'

    @gen_hookimpl
    def gen(self, module_dir, output_dir):
        """
          gen phase for the test generator
        """
        for yaml_file in self.config:
            try:
                with open(yaml_file) as f:
                    pass
            except IOError:
                logger.error(
                    f"The {yaml_file} file does not exist. Check and try again")
                exit(0)

        if ('all' in self.modules):
            logger.debug('Checking {0} for modules'.format(self.modules_dir))
            self.modules = list_of_modules(self.modules_dir)

        logger.debug('the modules are {0}'.format(self.modules))
        output_dir = os.path.abspath(output_dir)
        logger.debug("μArchitectural Test Generator, Gen. phase")
        module_dir = os.path.join(module_dir, "uatg_plugin/")
        logger.debug('Module dir is {0}'.format(module_dir))
        logger.debug('Output dir is {0}'.format(output_dir))
        logger.debug('Work_dir is {0}'.format(self.work_dir))
        pytest_file = os.path.join(module_dir, 'gen_framework.py')
        os.makedirs(self.work_dir, exist_ok=True)

        # report file
        report_file_name = '{0}/{1}_{2}'.format(
            os.path.join(output_dir, ".json/"), self.name,
            datetime.datetime.now().strftime("%Y%m%d-%H%M"))

        # pytest for test generation
        pytest.main([
            pytest_file, 
            '-n=1', 
            '--config={0}'.format(str(self.config)[1:-1]), 
            '-v',
            '--jobs={0}'.format(self.jobs),
            '--index_file={0}'.format(self.index_file),
            '--html={0}/reports/utg.html'.format(output_dir),
            '--report-log={0}.json'.format(report_file_name),
            '--self-contained-html', 
            '--output_dir={0}'.format(output_dir),
            '--module_dir={0}'.format(module_dir), 
            '--work_dir={0}'.format(self.work_dir), 
            '--linker_dir={0}'.format(self.linker_dir),
            '--module={0}'.format(self.modules_str), 
            '--gen_cvg={0}'.format(self.cvg), 
            '--modules_dir={0}'.format(self.modules_dir),
            '--alias_file={0}'.format(self.alias_file),
            '--paging_modes={0}'.format(self.paging_modes)
        ])

        test_list = utils.load_yaml(f'{self.work_dir}/test_list.yaml')
        return test_list

    @gen_hookimpl
    def post_gen(self, output_dir):
        """Post gen phase for the UTG"""
        logger.info(
            "Completed Test Generation using μArchitectural Test Generator")
        pass
