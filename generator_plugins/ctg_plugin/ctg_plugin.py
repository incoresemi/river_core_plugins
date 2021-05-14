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
from riscv_ctg.main import cli

from riscof.utils import shellCommand

gen_hookimpl = pluggy.HookimplMarker("generator")

this = os.path.abspath(os.path.dirname(__file__))
class ctg_plugin(object):
    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        '''
            Spec Config Fields and their meanings.
            cgf_files: a list of comma or newline separated file paths which point to the list of cgf files for ctg.
            jobs: number of parallel processes to spawn for ctg
            xlen: xlen of the tests
            base_isa: The base isa for the tests. One of [rv32e,rv32i,rv64i]
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
        self.cgf_files = [os.path.abspath(x.strip()) for x in re.split('\n|,',spec_config['cgf_files'])]
        for entry in self.cgf_files:
            if not os.path.exists(entry):
                logger.error(entry + " path does not exist.")
                raise SystemExit
        self.xlen = int(spec_config['xlen'])
        self.jobs = int(spec_config['jobs'])
        self.randomize = bool(spec_config['randomize'])
        self.base_isa = str(spec_config['base_isa'])
        self.config_file = os.path.abspath(spec_config['riscof_config'])

    @gen_hookimpl
    def gen(self, gen_config, module_dir, output_dir):
        output_dir = os.path.abspath(output_dir)
        logger.debug("CTG Gen phase.")
        asm_path = os.path.join(output_dir,"ctg/asm/")
        os.makedirs(asm_path)
        # ctg("debug",os.path.join(output_dir,asm_path), self.randomize, self.xlen, self.cgf_files, self.jobs, self.base_isa)
        ctg_command = 'riscv_ctg -v info -bi {0} -d {1} -p {2}'.format(self.base_isa, asm_path, self.jobs)+('' if not self.randomize else ' -r ') + '-cf ' + ' -cf '.join(self.cgf_files)
        print(shellCommand(ctg_command).run(cwd=os.path.join(output_dir,"ctg/")))
        work_dir = os.path.join(output_dir,"ctg/riscof_work/")
        includes = os.path.join(output_dir,"ctg/asm/env/")
        riscof_command = "riscof testlist --config {0} --suite {1}".format(self.config_file,asm_path)
        shellCommand(riscof_command).run(cwd=os.path.join(output_dir,"ctg/"))
        riscof_test_list = utils.load_yaml(os.path.join(work_dir,"test_list.yaml"))
        test_list = {}
        for entry in riscof_test_list.keys():
            key = os.path.basename(entry)[:-2]
            new_entry = {}
            new_entry["isa"] = riscof_test_list[entry]["isa"]
            new_entry['work_dir'] = riscof_test_list[entry]['work_dir']
            new_entry['asm_file'] = riscof_test_list[entry]['test_path']
            new_entry['coverage_labels'] = riscof_test_list[entry]['coverage_labels']
            new_entry['generator'] = self.name
            new_entry['include'] = [includes]
            new_entry['cc'] = 'riscv64-unknown-elf-gcc'
            new_entry['result'] = "Unavailable"
            new_entry['cc_args'] = ' -mcmodel=medany -static -std=gnu99 -O2 -fno-common -fno-builtin-printf -fvisibility=hidden '
            new_entry['linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
            new_entry['linker_file'] = ''
            new_entry['mabi'] = ''
            new_entry['march'] = new_entry['isa']
            test_list[key] = new_entry
        return test_list

    @gen_hookimpl
    def post_gen(self, output_dir, regressfile):
        pass
