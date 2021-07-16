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
        ## Add support for modules and link file generation
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
            os.path.join(self.uarch_dir, 'modules/branch_predictor/tests/'))
        logger.warn('uarch_dir is {0}'.format(self.uarch_dir))
        logger.warn('output_dir is {0}'.format(output_dir))
        # reading work dir fromthe config file
        self.work_dir = spec_config['work_dir']
        if self.work_dir:
            if (self.work_dir == 'work'):
                self.work_dir = output_dir
            else:
                self.work_dir = spec_config['work_dir']
        else:
            self.work_dir = default_work_dir  #os.path.join(self.uarch_dir,_temp)
            logger.warn('Defaulting to {0} as work_dir'.format(self.work_dir))
        logger.debug("work dir is {0}".format(self.work_dir))
        # reading the path to linker file from the ini file
        self.linker_dir = spec_config['linker_dir']
        if self.linker_dir:
            self.linker_dir = spec_config['linker_dir']
        else:
            self.linker_dir = self.work_dir
            logger.warn(
                'Default linker is used, uarch_test will generate the linker')
        logger.debug('linker_dir is {0}'.format(self.linker_dir))
        # reading the modules form the config file
        self.modules = spec_config['modules']
        # the DUT config YAML file
        self.dut_config_file = spec_config['dut_config_yaml']
        logger.debug("uArch test generator, Completed Pre-Gen Phase")

    @gen_hookimpl
    def gen(self, module_dir, output_dir):
        """
          gen phase for the test generator
        """
        if (self.modules == 'all'):
            logger.debug('Checking {0} for modules'.format(
                os.path.join(self.uarch_dir, 'modules')))
            self.modules = [
                f.name
                for f in os.scandir(os.path.join(self.uarch_dir, 'modules'))
                if f.is_dir()
            ]
        # uarch_test requires the modules to be specified in a comma separated string
        modules_str = ','.join(self.modules)
        logger.debug('the modules are {0}'.format(self.modules))
        logger.debug('the module string {0}'.format(modules_str))
        output_dir = os.path.abspath(output_dir)
        logger.debug("uArch test generator, Gen. phase")
        #temp_dir = os.path.dirname(uarch_test.__file__)
        asm_dir = self.work_dir
        #asm_dir = os.path.join(output_dir,"uarch_test/asm/")
        module_dir = os.path.join(module_dir, "uarch_test_plugin/")
        logger.debug('Module dir is {0}'.format(module_dir))
        logger.debug('Output dir is {0}'.format(output_dir))
        logger.debug('work_dir is {0}'.format(self.work_dir))
        pytest_file = os.path.join(module_dir, 'gen_framework.py')
        os.makedirs(asm_dir, exist_ok=True)

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
            '--module={0}'.format(modules_str)
        ])

        #work_dir = os.path.join(output_dir,"uarch_test/work/")
        #includes = os.path.dirname(uarch_test.__file__)+'/env'
        #model_include

        test_list = {}
        asm_test_list = glob.glob(asm_dir + '/**/*[!_template].S')
        # To-Do The Asm dir and target dir will be udated
        env_dir = os.path.join(self.uarch_dir, "env/")
        target_dir = os.path.join(self.uarch_dir, "target/")

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
            test_list[base_key]['linker_file'] = target_dir + 'link.ld'
            test_list[base_key][
                'asm_file'] = asm_dir + '/' + base_key + '/' + base_key + '.S'

            #            test_list[base_key][
            #                'linker_file'] = output_dir + '/uarch_test/asm/' + base_key + '/' + base_key + '.ld'
            #            test_list[base_key][
            #                'asm_file'] = output_dir + '/uarch_test/asm/' + base_key + '/' + base_key + '.S'
            test_list[base_key]['include'] = [env_dir, target_dir]
            test_list[base_key]['compile_macros'] = ['XLEN=64']
            test_list[base_key]['extra_compile'] = []
            test_list[base_key]['result'] = 'Unavailable'

        return test_list

    @gen_hookimpl
    def post_gen(self, output_dir):
        pass
