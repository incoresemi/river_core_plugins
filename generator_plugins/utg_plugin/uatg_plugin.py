# See LICENSE for details

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


class utg_plugin(object):

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
        os.mkdir(output_dir)
        self.jobs = int(spec_config['jobs'])
        self.seed = spec_config['seed']
        self.count = int(spec_config['count'])
        self.uarch_dir = os.path.dirname(utg.__file__) 
        logger.warn('UATG_dir is {0}'.format(self.uarch_dir))
        logger.warn('output_dir is {0}'.format(output_dir))
        self.work_dir = spec_config['work_dir']
        logger.debug("work dir is {0}".format(self.work_dir))
        self.linker_dir = spec_config['linker_dir']
        if self.linker_dir:
            self.linker_dir = spec_config['linker_dir']
        else:
            self.linker_dir = self.work_dir
            logger.warn(
                'Default linker is used, uatg will generate the linker')
        logger.debug('linker_dir is {0}'.format(self.linker_dir))
        self.modules = spec_config['modules']
        # utg requires the modules to be specified as a string and not a list
        self.modules_str = self.modules
        # converting self.modules into a list from string
        self.modules = [x.strip() for x in self.modules.split(',')]
        self.modules_dir = spec_config['modules_dir']
        self.dut_config_file = spec_config['dut_config_yaml']
        self.alias_file = spec_config['alias_file']
        if ((spec_config['generate_covergroups']).lower() == 'true'):
            self.cvg = '--gen_cvg'
            logger.debug('Generating covergroups')
        else:
            self.cvg = ''
            logger.debug('Not generating covergroups')
        logger.debug("Uarch Test Generator, Completed Pre-Gen Phase")

    @gen_hookimpl
    def gen(self, module_dir, output_dir):
        """
          gen phase for the test generator
        """
        try:
            with open(self.dut_config_file) as f:
                pass
        except IOError:
            logger.error(
                "The DUT Config file does not exist. Check and try again")
            exit(0)

        if ('all' in self.modules):
            logger.debug('Checking {0} for modules'.format(self.modules_dir))
            self.modules = list_of_modules(self.modules_dir, 'error')
            
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
            pytest_file, '-n=1',
            '--dut_config={0}'.format(self.dut_config_file), '-v',
            '--html={0}/reports/utg.html'.format(output_dir),
            '--report-log={0}.json'.format(report_file_name),
            '--self-contained-html', '--output_dir={0}'.format(output_dir),
            '--module_dir={0}'.format(module_dir), '--work_dir={0}'.format(
                self.work_dir), '--linker_dir={0}'.format(self.linker_dir),
            '--module={0}'.format(self.modules_str), '--gen_cvg={0}'.format(
                self.cvg), '--modules_dir={0}'.format(self.modules_dir),
            '--alias_file={0}'.format(self.alias_file)
        ])

        test_list = {}
        for module in self.modules:
            asm_dir = self.work_dir + '/' + module
            asm_test_list = glob.glob(asm_dir + '/**/*.S')
            env_dir = os.path.join(self.uarch_dir, 'env/')
            target_dir = self.work_dir

            for test in asm_test_list:
                logger.debug("Current test is {0}".format(test))
                base_key = os.path.basename(test)[:-2]
                test_list[base_key] = {}
                test_list[base_key]['generator'] = self.name
                test_list[base_key]['work_dir'] = asm_dir + '/' + base_key
                test_list[base_key]['isa'] = 'rv64imafdc'
                test_list[base_key]['march'] = 'rv64imafdc'
                test_list[base_key]['mabi'] = 'lp64'
                test_list[base_key]['cc'] = 'riscv64-unknown-elf-gcc'
                test_list[base_key][
                    'cc_args'] = ' -mcmodel=medany -static -std=gnu99 -O2 -fno-common -fno-builtin-printf -fvisibility=hidden '
                test_list[base_key][
                    'linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
                test_list[base_key][
                    'linker_file'] = target_dir + '/' + 'link.ld'
                test_list[base_key][
                    'asm_file'] = asm_dir + '/' + base_key + '/' + base_key + '.S'
                test_list[base_key]['include'] = [env_dir, target_dir]
                test_list[base_key]['compile_macros'] = ['XLEN=64']
                test_list[base_key]['extra_compile'] = []
                test_list[base_key]['result'] = 'Unavailable'

        return test_list

    @gen_hookimpl
    def post_gen(self, output_dir):
        """Post gen phase for the UTG"""
        logger.info("Completed Test Generation using UATG")
        pass
