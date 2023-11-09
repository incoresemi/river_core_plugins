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
import subprocess
import shlex
from glob import *
import pprint

gen_hookimpl = pluggy.HookimplMarker("generator")


class riscv_tests_plugin(object):
    """ Generator hook implementation """

    # creates gendir and any setup related things
    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        '''

         Pre-Gen Stage.

         Check if the output_dir exists

         Add load plugin specific config

        '''

        logger.debug('RISCV-TESTS Plugin Pre Gen Stage')
        output_dir = os.path.abspath(output_dir)
        self.output_dir = output_dir
        self.name = 'riscv_tests'

        logger.debug('Extracting info from list')
        # Extract plugin specific info
        self.jobs = spec_config['jobs']
        self.filter = spec_config['filter']
        self.pmp_enabled = True if str(spec_config['pmp_enabled']).lower() == "true" else False

        if not os.path.isdir(f'{self.output_dir}'):
            subprocess.call(shlex.split(f'git clone --recursive \
               https://github.com/riscv/riscv-tests.git {self.output_dir}/'))
            cwd = os.getcwd()
            os.chdir(f'{self.output_dir}/')
            subprocess.call(shlex.split(f'git checkout \
93208aa5492263d43a3576d879900854ed3fef42'))
            os.chdir(f'{self.output_dir}/env')
            subprocess.call(shlex.split('git checkout master'))
            os.chdir(cwd)

        self.isa_dir = self.output_dir + '/isa'

        # TODO Might  be useful later on
        # Eventually add support for riscv_config
        self.isa = spec_config['isa']

        self.json_dir = output_dir + '/../.json/'
        logger.debug(self.json_dir)
        # Check if dir exists
        if (os.path.isdir(self.json_dir)):
            logger.debug(self.json_dir + ' Directory exists')
        else:
            os.makedirs(self.json_dir)
        march = self.isa.replace('S','').replace('U','').replace('H','').lower()
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

        cwd = os.getcwd()
        os.chdir(f'{self.output_dir}/env')
        patch_name = "init_pmp.patch" if self.pmp_enabled else "patch"
        result = subprocess.run(shlex.split(f'git apply --check {module_dir}/{self.name}_plugin/{patch_name}'), capture_output=True, text=True)
        if not result.stdout:
            logger.debug('applying patch')
            result = subprocess.run(shlex.split(f'git apply {module_dir}/{self.name}_plugin/{patch_name}'), capture_output=True, text=True)
        os.chdir(cwd)

        logger.debug(f'isa_dir : {self.isa_dir}')
        isas = []
        for mydir in os.listdir(self.isa_dir):
            if mydir.startswith(f"rv{self.xlen}"):
                (xlen,mode,isa) = re.findall(r'rv(?P<xlen>64|32)(?P<mode>m|u|s)(?P<name>.*)$',mydir)[0]
                isa = isa.capitalize()
                mode = mode.capitalize()
                if int(xlen,0) == self.xlen and isa in self.isa and (mode == 'M' or mode in self.isa):
                    isas.append(mydir)

        logger.debug(f'found : {isas}')
        test_list = {}
        for i in isas:
            with open(f'{self.isa_dir}/{i}/Makefrag', 'r') as file:
                data = file.read()
                if re.findall(r'.*_v_tests',data) and 'S' in self.isa:
                    virtual = True
                else:
                    virtual = False

            for t in os.listdir(self.isa_dir + '/' + i):
                if 'breakpoint' in t or ('wfi' in t):
                    continue
                if 'sbreak' in t and 'S' not in self.isa:
                    continue
                if self.xlen == 32 and 'D' in self.isa:
                    if i == 'rv32ud' and 'move' in t:
                        continue
                if t.endswith('.S'):
                    work_dir = f'{self.isa_dir}/p/{i}-{t[:-2]}'
                    base_key = f'{i}-{t[:-2]}-p'
                    test_list[base_key] = {}
                    test_list[base_key]['work_dir']= work_dir
                    test_list[base_key]['generator'] = self.name
                    test_list[base_key]['isa'] = self.isa
                    test_list[base_key]['march'] = self.march
                    test_list[base_key]['mabi'] = self.mabi
                    test_list[base_key]['cc'] = f'riscv{self.xlen}-unknown-elf-gcc'
                    test_list[base_key]['cc_args'] = '-static -std=gnu99 -O2 -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles'
                    test_list[base_key]['linker_args'] = '-lm -lgcc -T'
                    test_list[base_key]['linker_file'] = f'{self.output_dir}/env/p/link.ld'
                    test_list[base_key]['asm_file'] = f'{self.isa_dir}/{i}/{t}'
                    test_list[base_key]['include'] = [\
                            f'{self.output_dir}/env/p/',
                            f'{self.isa_dir}/macros/scalar',]
                    test_list[base_key]['extra_compile'] = []
                    test_list[base_key]['compile_macros'] = []
                    test_list[base_key]['result'] = 'Unavailable'
                    test_list[base_key]['ignore_lines'] = 4
                    if (os.path.isdir(work_dir)):
                        logger.debug(f'{work_dir} exists')
                        shutil.rmtree(work_dir, ignore_errors=True)
                    os.makedirs(work_dir)
                    if virtual:
                        march = self.march
                        if 'f' not in march:
                            if 'a' in march:
                                march = march[:march.index('a')+1]+'f'+march[march.index('a')+1:]

                            elif 'm' in march:
                                march = march[:march.index('m')+1]+'f'+march[march.index('m')+1:]
                            elif 'i' in march:
                                march = march[:march.index('i')+1]+'f'+march[march.index('i')+1:]

                        work_dir = f'{self.isa_dir}/v/{i}-{t[:-2]}'
                        entropy = 'bf12e4d'
                        base_key = f'{i}-{t[:-2]}-v'
                        test_list[base_key] = {}
                        test_list[base_key]['work_dir']= work_dir
                        test_list[base_key]['generator'] = self.name
                        test_list[base_key]['isa'] = self.isa
                        test_list[base_key]['march'] = march
                        test_list[base_key]['mabi'] = self.mabi
                        test_list[base_key]['cc'] = f'riscv{self.xlen}-unknown-elf-gcc'
                        test_list[base_key]['cc_args'] = '-static -std=gnu99 -O2 -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles'
                        test_list[base_key]['linker_args'] = '-lm -lgcc -T'
                        test_list[base_key]['linker_file'] = f'{self.output_dir}/env/v/link.ld'
                        test_list[base_key]['asm_file'] = f'{self.isa_dir}/{i}/{t}'
                        test_list[base_key]['include'] = [\
                                f'{self.output_dir}/env/v/',
                                f'{self.isa_dir}/macros/scalar',]
                        test_list[base_key]['extra_compile'] = [\
                                f'{self.output_dir}/env/v/vm.c',
                                f'{self.output_dir}/env/v/string.c',
                                f'{self.output_dir}/env/v/entry.S']
                        test_list[base_key]['compile_macros'] = [f'ENTROPY=0x{entropy}']
                        test_list[base_key]['result'] = 'Unavailable'
                        test_list[base_key]['ignore_lines'] = 13
                        if (os.path.isdir(work_dir)):
                            logger.debug(f'{work_dir} exists')
                            shutil.rmtree(work_dir, ignore_errors=True)
                        os.makedirs(work_dir)

        return test_list

    # generates the regress list from the generation
    @gen_hookimpl
    def post_gen(self, output_dir):
        pass

