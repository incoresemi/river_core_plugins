# See LICENSE for details

import os
import sys
import pluggy
import shutil
import subprocess
import random
import re
import datetime
import pytest
import glob
import re

from river_core.log import logger
import river_core.utils as utils
from river_core.constants import *

gen_hookimpl = pluggy.HookimplMarker("generator")

this = os.path.abspath(os.path.dirname(__file__))


class ctg_plugin(object):

    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        '''
            Spec Config Fields and their meanings.
            cgf_files: a list of comma or newline separated file paths which point to the list of cgf files for ctg.
            jobs: number of parallel processes to spawn for ctg
            isa: The isa for the tests. The key should exist in the ctg configuration file.
            ctg_gen_config: A yaml file where the nodes are accessed using the isa and the node supplies details pertaining to base isa and cgf files for CTG.
            riscof_config: config file for riscof
            randomize: Specify the SAT solver to use in ctg.
        '''
        logger.debug("RISCV-CTG Pre Gen.")
        self.name = 'ctg'
        output_dir = os.path.abspath(output_dir)
        if (os.path.isdir(output_dir)):
            logger.debug('Output Directory exists. Removing Contents.')
            shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir)
        self.jobs = int(spec_config['jobs'])
        self.randomize = bool(spec_config['randomize'])
        self.isa = str(spec_config['isa'])
        self.config_isa = str(spec_config['test_cfg'])
        self.gen_config = os.path.abspath(spec_config['ctg_gen_config'])
        # self.config_file = os.path.abspath(spec_config['riscof_config'])

    @gen_hookimpl
    def gen(self, module_dir, output_dir):
        output_dir = os.path.abspath(output_dir)
        logger.debug("CTG Gen phase.")
        asm_path = os.path.join(output_dir, "ctg/asm/")
        pytest_file = os.path.join(this, 'gen_framework.py')
        os.makedirs(asm_path)
        report_file_name = '{0}/{1}_{2}'.format(
            os.path.join(output_dir, ".json/"), self.name,
            datetime.datetime.now().strftime("%Y%m%d-%H%M"))
        pytest.main([
            pytest_file, '-n={0}'.format(self.jobs),
            '--configfile={0}'.format(self.gen_config), '-v',
            '--isa={0}'.format(self.config_isa), '--jobs={0}'.format(self.jobs),
            '--html={0}/reports/ctg.html'.format(output_dir),
            '--report-log={0}.json'.format(report_file_name),
            '--self-contained-html', '--output_dir={0}'.format(asm_path),
            '--module_dir={0}'.format(this),
            ('' if not self.randomize else '--randomize')
        ])
        # work_dir = os.path.join(output_dir, "ctg/riscof_work/")
        includes = os.path.join(output_dir, "ctg/asm/env/")
        test_list = {}
        asm_test_list = glob.glob(asm_path + '*.S')
        # asm_templates = glob.glob(asm_dir+'/**/*.S')
        for test in asm_test_list:
            with open(test, 'r') as file:
                test_asm = file.read()
            isa = set()
            isa.add('i')
            xlen = 64
            dist_list = re.findall(r'^#\s*(rel_.*?)$', test_asm, re.M | re.S)
            for dist in dist_list:
                ext = dist.split(':')[0][4:].split('.')[0]
                ext_count = int(dist.split(':')[1])

                if ext_count != 0:
                    if 'rv64' in ext:
                        xlen = 64
                    if 'm' in ext:
                        isa.add('m')
                    if 'a' in ext:
                        isa.add('a')
                    if 'f' in ext:
                        isa.add('f')
                    if 'd' in ext:
                        isa.add('d')
                    if 'c' in ext:
                        isa.add('c')
            canonical_order = {'i': 0, 'm': 1, 'a': 2, 'f': 3, 'd': 4, 'c': 5}
            canonical_isa = sorted(list(isa), key=lambda d: canonical_order[d])

            march_str = 'rv' + str(xlen) + "".join(canonical_order)
            if xlen == 64:
                mabi_str = 'lp64'
            elif 'd' not in march_str:
                mabi_str = 'ilp32d'

            base_key = os.path.basename(test)[:-2]
            test_list[base_key] = {}
            test_list[base_key]['generator'] = self.name
            test_list[base_key]['include'] = [includes]
            test_list[base_key]['work_dir'] = output_dir + '/ctg/asm/'
            test_list[base_key][
                'asm_file'] = output_dir + '/ctg/asm/' + base_key + '.S'
            test_list[base_key]['isa'] = self.isa
            test_list[base_key]['march'] = march_str
            test_list[base_key]['mabi'] = mabi_str
            test_list[base_key]['cc'] = 'riscv64-unknown-elf-gcc'
            test_list[base_key][
                'cc_args'] = ' -mcmodel=medany -static -std=gnu99 -O2 -fno-common -fno-builtin-printf -fvisibility=hidden '
            test_list[base_key]['linker_args'] = ''
            test_list[base_key]['linker_file'] = ''
            test_list[base_key]['extra_compile'] = []
            test_list[base_key]['result'] = 'Unavailable'

        return test_list

    @gen_hookimpl
    def post_gen(self, output_dir):
        pass
