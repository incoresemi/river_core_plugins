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

        subprocess.call(shlex.split(f'git clone --recursive \
            https://github.com/riscv/riscv-tests.git {self.output_dir}/'))

        self.isa_dir = self.output_dir + '/isa'
        print(self.isa_dir)

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
        if '32' in self.isa:
            self.xlen = 32
            self.mabi = 'ilp32'
            self.march = 'rv32g'
        else:
            self.xlen = 64
            self.march = 'rv64g'
            self.mabi = 'lp64'

    @gen_hookimpl
    def gen(self, module_dir, output_dir):

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
                if re.findall(r'.*_v_tests',data):
                    virtual = True
                else:
                    virtual = False

            for t in os.listdir(self.isa_dir + '/' + i):
                if t.endswith('.S'):
                    work_dir = f'{self.isa_dir}/p/{i}-{t[:-2]}'
                    base_key = f'{i}-{t[:-2]}-p'
                    test_list[base_key] = {}
                    test_list[base_key]['work_dir']= work_dir
                    test_list[base_key]['generator'] = self.name
                    test_list[base_key]['isa'] = self.isa
                    test_list[base_key]['march'] = self.march
                    test_list[base_key]['mabi'] = self.mabi
                    test_list[base_key]['cc'] = 'riscv64-unknown-elf-gcc'
                    test_list[base_key]['cc_args'] = '-static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles' 
                    test_list[base_key]['linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
                    test_list[base_key]['linker_file'] = f'{self.output_dir}/env/p/link.ld'
                    test_list[base_key]['asm_file'] = f'{self.isa_dir}/{i}/{t}'
                    test_list[base_key]['include'] = [\
                            f'{self.output_dir}/env/p/',
                            f'{self.isa_dir}/macros/scalar',]
                    test_list[base_key]['extra_compile'] = []
                    test_list[base_key]['compile_macros'] = []
                    test_list[base_key]['result'] = 'Unavailable'
                    if (os.path.isdir(work_dir)):
                        logger.debug(f'{work_dir} exists')
                        shutil.rmtree(work_dir, ignore_errors=True)
                    os.makedirs(work_dir)
                    if virtual:
                        work_dir = f'{self.isa_dir}/v/{i}-{t[:-2]}'
                        entropy = 'bf12e4d'
                        base_key = f'{i}-{t[:-2]}-v'
                        test_list[base_key] = {}
                        test_list[base_key]['work_dir']= work_dir
                        test_list[base_key]['generator'] = self.name
                        test_list[base_key]['isa'] = self.isa
                        test_list[base_key]['march'] = self.march
                        test_list[base_key]['mabi'] = self.mabi
                        test_list[base_key]['cc'] = 'riscv64-unknown-elf-gcc'
                        test_list[base_key]['cc_args'] = '-static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles' 
                        test_list[base_key]['linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
                        test_list[base_key]['linker_file'] = f'{self.output_dir}/env/v/link.ld'
                        test_list[base_key]['asm_file'] = f'{self.isa_dir}/{i}/{t}'
                        test_list[base_key]['include'] = [\
                                f'{self.output_dir}/env/v/',
                                f'{self.isa_dir}/macros/scalar',]
                        test_list[base_key]['extra_compile'] = [\
                                f'{self.output_dir}/env/v/vm.c',
                                f'{self.output_dir}/env/v/string.c']
                        test_list[base_key]['compile_macros'] = [f'ENTROPY=0x{entropy}']
                        test_list[base_key]['result'] = 'Unavailable'
                        if (os.path.isdir(work_dir)):
                            logger.debug(f'{work_dir} exists')
                            shutil.rmtree(work_dir, ignore_errors=True)
                        os.makedirs(work_dir)

        return test_list

    # generates the regress list from the generation
    @gen_hookimpl
    def post_gen(self, output_dir):
        pass

