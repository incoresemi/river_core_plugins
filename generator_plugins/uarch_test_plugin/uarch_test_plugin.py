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
import uarch_test

from river_core.log import logger
import river_core.utils as utils
from river_core.constants import *

gen_hookimpl = pluggy.HookimplMarker("generator")


class uarch_test_plugin(object):

    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        """
           Spec Config will send in the yaml file as a 
           dictionary for the uarch_test generator to use
           uarch_test has not been configured to run mulitple jobs, YET
           as uarch test is ISA agnostic, we do not need those either
        """
        logger.debug("uArch test generator, Pre-Gen.")
        self.name = 'uarch_test'
        output_dir = os.path.abspath(output_dir)
        if os.path.isdir(output_dir) and os.path.exists(output_dir):
            logger.debug('Output Directory exists. Removing Contents.')
            rmtree(output_dir)
        os.mkdir(output_dir)
        self.jobs = int(spec_config['jobs'])
        self.seed = spec_config['seed']
        self.count = int(spec_config['count'])
        self.uarch_dir = os.path.dirname(uarch_test.__file__)
        default_work_dir = os.path.abspath(
            os.path.join(self.uarch_dir, '../work/'))
        logger.warn('uarch_dir is {0}'.format(self.uarch_dir))
        logger.warn('output_dir is {0}'.format(output_dir))
        self.work_dir = spec_config['work_dir']
        if self.work_dir:
            if (self.work_dir == 'work'):
                self.work_dir = output_dir
            else:
                self.work_dir = spec_config['work_dir']
        else:
            self.work_dir = default_work_dir
            logger.warn('Defaulting to {0} as work_dir'.format(self.work_dir))
        logger.debug("work dir is {0}".format(self.work_dir))
        self.linker_dir = spec_config['linker_dir']
        if self.linker_dir:
            self.linker_dir = spec_config['linker_dir']
        else:
            self.linker_dir = self.work_dir
            logger.warn(
                'Default linker is used, uarch_test will generate the linker')
        logger.debug('linker_dir is {0}'.format(self.linker_dir))
        self.modules = spec_config['modules']
        # uarch_test requires the modules to be specified as a string and not a list
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
        logger.debug("uArch test generator, Completed Pre-Gen Phase")

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
            try:
                self.modules = [
                    f.name for f in os.scandir(self.modules_dir) if f.is_dir()
                ]
            except FileNotFoundError as e:
                logger.error("The modules_dir cannot be empty.")
                exit(0)

        logger.debug('the modules are {0}'.format(self.modules))
        output_dir = os.path.abspath(output_dir)
        logger.debug("uArch test generator, Gen. phase")
        module_dir = os.path.join(module_dir, "uarch_test_plugin/")
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
            '--configfile={0}'.format(self.dut_config_file), '-v',
            '--html={0}/reports/uarch_test.html'.format(output_dir),
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
        pass
