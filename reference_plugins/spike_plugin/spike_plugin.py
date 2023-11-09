# See LICENSE for details

import os
import sys
import pluggy
import shutil
import random
import re
import glob
import datetime
import pytest

from river_core.log import logger
from river_core.utils import *

dut_hookimpl = pluggy.HookimplMarker('dut')


class spike_plugin(object):
    '''
        Plugin to set Spike as ref
    '''
    @dut_hookimpl
    def init(self, ini_config, test_list, work_dir, plugin_path):
        self.name = 'spike'
        logger.debug('Pre Compile Stage')

        # Get plugin specific configs from ini
        self.jobs = ini_config['jobs']

        self.filter = ini_config['filter']

        self.riscv_isa = ini_config['isa']
        self.isa = ini_config['isa']
        self.pmp_regions = ini_config['pmp_regions']
        self.pmp_granularity = ini_config['pmp_granularity']
        self.pmp_enabled = True if str(self.pmp_regions) != "0" else False
        if '64' in self.riscv_isa:
            self.xlen = 64
        else:
            self.xlen = 32
        self.elf = 'ref.elf'

        self.objdump_cmd = ''#riscv{0}-unknown-elf-objdump -D ref.elf > ref.disass && '.format( self.xlen)
        self.sim_cmd = 'spike'
        self.sim_args = '--log ref.dump --log-commits --priv={0} --isa={1} --pmpregions={2} --pmpgranularity={3} {4}'

        self.work_dir = os.path.abspath(work_dir) + '/'
        self.test_list = load_yaml(test_list)

        self.json_dir = self.work_dir + '/.json/'
        # Check if dir exists
        if (os.path.isdir(self.json_dir)):
            logger.debug(self.json_dir + ' Directory exists')
        else:
            os.makedirs(self.json_dir)

        if shutil.which('spike') is None:
            logger.error('Spike not available in $PATH')
            raise SystemExit

    @dut_hookimpl
    def build(self):
        logger.debug('Build Hook')
        make = makeUtil(makefilePath=os.path.join(self.work_dir,"Makefile." +\
            self.name))
        make.makeCommand = 'make -j1'
        self.make_file = os.path.join(self.work_dir, 'Makefile.' + self.name)
        self.test_names = []

        for test, attr in self.test_list.items():
            logger.debug('Creating Make Target for ' + str(test))
            abi = attr['mabi']
            arch = attr['march']
            isa = attr['isa']
            work_dir = attr['work_dir']
            link_args = attr['linker_args']
            link_file = attr['linker_file']
            cc = attr['cc']
            cc_args = attr['cc_args']
            asm_file = attr['asm_file']

            spike_isa = 'rv' + str(self.xlen) + 'i'
            spike_isa += 'm' if 'M' in self.isa or 'G' in self.isa else ''
            spike_isa += 'a' if 'A' in self.isa or 'G' in self.isa else ''
            spike_isa += 'f' if 'F' in self.isa or 'G' in self.isa else ''
            spike_isa += 'd' if 'D' in self.isa or 'G' in self.isa else ''
            spike_isa += 'c' if 'C' in self.isa or 'G' in self.isa else ''
            spike_isa += 'h' if 'H' in self.isa else ''
            spike_isa += '_zba' if 'Zba' in self.isa else ''
            spike_isa += '_zbb' if 'Zbb' in self.isa else ''
            spike_isa += '_zbc' if 'Zbc' in self.isa else ''
            spike_isa += '_zbs' if 'Zbs' in self.isa else ''

            spike_priv = 'm'
            if 'S' in isa:
                spike_priv += 'su'
            elif 'U' in isa:
                spike_priv += 'u'

            ch_cmd = 'cd {0} && '.format(work_dir)
            compile_cmd = '{0} {1} -march={2} -mabi={3} {4} {5} {6}'.format(\
                    cc, cc_args, arch, abi, link_args, link_file, asm_file)
            for x in attr['extra_compile']:
                compile_cmd += ' ' + x
            for x in attr['include']:
                compile_cmd += ' -I '+str(x)
            compile_cmd += ' '.join(map(' -D{0}'.format, attr['compile_macros']))
            compile_cmd += ' -o ref.elf && '
            post_process_cmd = ''
            target_cmd = ch_cmd + compile_cmd + self.objdump_cmd +\
                    self.sim_cmd + ' ' + \
                    self.sim_args.format(spike_priv, spike_isa, self.pmp_regions, self.pmp_granularity, self.elf)
            make.add_target(target_cmd, test)
            self.test_names.append(test)

    @dut_hookimpl
    def run(self, module_dir):
        logger.debug('Run Hook')
        logger.debug('Module dir: {0}'.format(module_dir))
        pytest_file = module_dir + '/spike_plugin/gen_framework.py'
        logger.debug('Pytest file: {0}'.format(pytest_file))

        report_file_name = '{0}/{1}_{2}'.format(
            self.json_dir, self.name,
            datetime.datetime.now().strftime("%Y%m%d-%H%M"))

        # TODO Regression list currently removed, check back later
        # TODO The logger doesn't exactly work like in the pytest module
        pytest.main([
            pytest_file,
            '-n={0}'.format(self.jobs),
            '-k={0}'.format(self.filter),
            '--html={0}.html'.format(self.work_dir + '/reports/' + self.name),
            '--report-log={0}.json'.format(report_file_name),
            '--work_dir={0}'.format(self.work_dir),
            '--make_file={0}'.format(self.make_file),
            '--key_list={0}'.format(self.test_names),
            # TODO Debug parameters, remove later on
            '--log-cli-level=DEBUG',
            '-o log_cli=true'
        ])
        # , '--regress_list={0}'.format(self.regress_list), '-v', '--compile_config={0}'.format(compile_config),
        return report_file_name

    @dut_hookimpl
    def post_run(self, test_dict, config):
        if str_2_bool(config['river_core']['space_saver']):
            logger.debug("Removing artifacts for Spike")
            for test in test_dict:
                if test_dict[test]['result'] == 'Passed':
                    logger.debug("Removing extra files for Test: " + str(test))
                    work_dir = test_dict[test]['work_dir']
                    try:
                        os.remove(work_dir + '/ref.disass')
                        os.remove(work_dir + '/ref.dump')
                    except:
                        pass
#                        logger.info(
#                            "Something went wrong trying to remove the files")
