import os
import re
import shutil
import subprocess
import shlex
import logging
import random
import string
from string import Template
import sys

import riscof.utils as utils
from riscof.pluginTemplate import pluginTemplate
import riscof.constants as constants

logger = logging.getLogger()

map = {
    'rv32i': 'rv32i',
    'rv32im': 'rv32im',
    'rv32ic': 'rv32ic',
    'rv32ia': 'rv32ia',
    'rv64i' : 'rv64i',
    'rv64im': 'rv64im'
}


class azurite(pluginTemplate):
    __model__ = "azurite"
    __version__ = "0.5.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        config = kwargs.get('config')
        if config is None:
            print("Please enter azuritebin path in configuration.")
            raise SystemExit
        else:
            self.azuritebin = config['azuritebin']

        path = os.path.abspath(os.path.dirname(__file__))
        self.isa_spec = os.path.abspath(config['ispec'])
        self.platform_spec = os.path.abspath(config['pspec'])
        self.pluginpath = os.path.abspath(config['pluginpath'])

        self.user_target = "azurite"
        self.user_sign = "sign"

    def initialise(self, suite, work_dir, compliance_env):
        self.suite = suite
        self.work_dir = work_dir
        self.compile_cmd = 'riscv{1}-unknown-elf-gcc -march={0} \
         -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles\
         -T '+self.pluginpath+'/env/link.ld\
         -I '+self.pluginpath+'/env/\
         -I ' + compliance_env
        self.objdump = "riscv{1}-unknown-elf-" + 'objdump -D rtl.elf > {0}.disass'

    def build(self, isa_yaml, platform_yaml):
        ispec = utils.load_yaml(isa_yaml)
        self.xlen = ('64' if 64 in ispec['hart0']['supported_xlen'] else '32')
        self.isa = 'rv' + self.xlen
        self.compile_cmd = self.compile_cmd+' -mabi='+('lp64 ' if 64 in ispec['hart0']['supported_xlen'] else 'ilp32 ')
        if "I" in ispec['hart0']["ISA"]:
            self.isa += 'i'
        if "M" in ispec['hart0']["ISA"]:
            self.isa += 'm'
        if "C" in ispec['hart0']["ISA"]:
            self.isa += 'c'

    def runTests(self, testList):
        make = utils.makeUtil(makefilePath=os.path.join(self.work_dir, "Makefile." + self.name[:-1]))
        make.makeCommand = 'make -j10'
        for file in testList:
            testentry = testList[file]
            test = testentry['test_path']
            test_dir = testentry['work_dir']
            
            elf = 'rtl.elf'

            execute = "cd "+testentry['work_dir']+";"

            cmd = self.compile_cmd.format(testentry['isa'].lower(),
                self.xlen) + ' ' + test + ' -o ' + elf
            compile_cmd = cmd + ' -D' + " -D".join(testentry['macros'])
            execute+=compile_cmd+";"
            execute+=self.objdump.format(test, self.xlen) + ';'
            
            test_dir = testentry['work_dir']
            d = dict(elf=elf,
                     testDir=test_dir,
                     isa=self.isa,
                     azuritebin=self.azuritebin)

            command = Template(
                '''ln -sf ${azuritebin}/* ${testDir}/. ; elf2hex 8 4194304 $elf 2147483648 > ${testDir}/code.mem'''
            ).safe_substitute(d)

            execute+=command+';'

            command = "cd " + testentry['work_dir'] + '; timeout 30s ./azurite_core +rtldump'
            execute += command+';'
            sign_file = os.path.join(test_dir,
                                     self.name[:-1] + ".signature")
            execute += "cat " + os.path.join(test_dir,
                                       "signature") + " > " + sign_file + ';'

            #makefile.write("\n\t" + cp)
            make.add_target(execute)
        make.execute_all(self.work_dir)
