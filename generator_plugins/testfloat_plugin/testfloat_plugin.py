# See LICENSE for details

#import riscv_config.checker as riscv_config
#from riscv_config.errors import ValidationError
import os
import sys
import pluggy
import shutil
import random
import re
import datetime
import pytest
import glob
from river_core.log import logger
import river_core.utils as utils
from river_core.constants import *
import re

gen_hookimpl = pluggy.HookimplMarker("generator")


class testfloat_plugin(object):
    """ Generator hook implementation """

    # creates gendir and any setup related things
    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        '''

         Pre-Gen Stage.

         Check if the output_dir exists

         Add load plugin specific config

        '''

        logger.debug('TestFloat Plugin Pre Gen Stage')
        output_dir = os.path.abspath(output_dir)
        self.name = 'testfloat'

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

        # Load plugin YAML
        self.gen_config = spec_config['config_yaml']

        self.json_dir = output_dir + '/../.json/'
        logger.debug(self.json_dir)
        # Check if dir exists
        if (os.path.isdir(self.json_dir)):
            logger.debug(self.json_dir + ' Directory exists')
        else:
            os.makedirs(self.json_dir)

    @gen_hookimpl
    def gen(self, module_dir, output_dir):

        logger.debug('TestFloat Plugin gen phase')
        logger.debug(module_dir)
        pytest_file = module_dir + '/testfloat_plugin/gen_framework.py'
        logger.debug(pytest_file)

        output_dir = os.path.abspath(output_dir)

        report_file_name = '{0}/{1}_{2}'.format(
            self.json_dir, self.name,
            datetime.datetime.now().strftime("%Y%m%d-%H%M"))
        pytest.main([
            pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(
                self.filter), '--configlist={0}'.format(self.gen_config), '-v',
            '--seed={0}'.format(self.seed), '--count={0}'.format(self.count),
            '--html={0}/reports/testfloat.html'.format(output_dir),
            '--report-log={0}.json'.format(report_file_name),
            '--self-contained-html', '--output_dir={0}'.format(output_dir),
            '--module_dir={0}'.format(module_dir)
        ])
        # Generate Test List
        # Get the aapg dir from output
        asm_dir = output_dir + '/testfloat/asm/'
        test_list = {}
        asm_test_list = glob.glob(asm_dir + '**/*[!_template].S')
        # asm_templates = glob.glob(asm_dir+'/**/*.S')
        for test in asm_test_list:
            isa = set()
            isa.add('i')
            xlen = 64 if '64' in self.isa else 32
            if 'm' in self.isa:
                isa.add('m')
            if 'a' in self.isa:
                isa.add('a')
            if 'f' in self.isa:
                isa.add('f')
            if 'd' in self.isa:
                isa.add('d')
            if 'c' in self.isa:
                isa.add('c')
            canonical_order = {'i': 0, 'm': 1, 'a': 2, 'f': 3, 'd': 4, 'c': 5}
            canonical_isa = sorted(list(isa), key=lambda d: canonical_order[d])

            march_str = 'rv' + str(xlen) + "".join(canonical_isa)
            if xlen == 64:
                mabi_str = 'lp64'
            elif 'd' not in march_str:
                mabi_str = 'ilp32d'

            # split the test-file name to extract the instruction
            instr = test.split('_')[3:-5]
            fsize = 64 if 'd' in instr else 32 # if d n name then fxlen=64

            base_key = os.path.basename(test)[:-2]
            test_list[base_key] = {}
            test_list[base_key][
                'work_dir'] = output_dir + '/testfloat/asm/' + base_key
            test_list[base_key]['generator'] = self.name
            test_list[base_key]['isa'] = self.isa
            test_list[base_key]['march'] = march_str
            test_list[base_key]['mabi'] = mabi_str
            test_list[base_key]['cc'] = 'riscv64-unknown-elf-gcc'
            test_list[base_key][
                'cc_args'] = ' -mcmodel=medany -static -std=gnu99 -O2 -fno-common -fno-builtin-printf -fvisibility=hidden '
            test_list[base_key][
                'linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
            test_list[base_key][
                'linker_file'] = output_dir + '/testfloat/asm/' + base_key + '/' + base_key + '.ld'
            test_list[base_key][
                'asm_file'] = output_dir + '/testfloat/asm/' + base_key + '/' + base_key + '.S'
            test_list[base_key]['include'] = [
                module_dir + '/testfloat_plugin/asm'
            ]
            test_list[base_key]['extra_compile'] = []
            test_list[base_key]['compile_macros'] = ['FSZ='+str(fsize)]
            test_list[base_key]['result'] = 'Unavailable'

        return test_list

    # generates the regress list from the generation
    @gen_hookimpl
    def post_gen(self, output_dir):
        pass
