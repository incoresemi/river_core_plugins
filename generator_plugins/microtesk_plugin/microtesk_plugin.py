# See LICENSE for details

#import riscv_config.checker as riscv_config
#from riscv_config.errors import ValidationError
import os
import sys
import pluggy
import shutil
import yaml
import random
import re
import datetime
import pytest
import glob
from river_core.log import logger
from river_core.utils import *
from river_core.constants import *

gen_hookimpl = pluggy.HookimplMarker("generator")


class MicroTESKPlugin(object):
    """ Generator hook implementation """

    #@gen_hookimpl
    #def load_config(self, isa, platform):
    #    pwd = os.getcwd()

    #    try:
    #        isa_file, platform_file = riscv_config.check_specs(
    #                                    isa, platform, pwd, True)
    #    except ValidationError as msg:
    #        #logger.error(msg)
    #        print('error')
    #        sys.exit(1)

    # creates gendir and any setup related things
    @gen_hookimpl
    def pre_gen(self, spec_config, output_dir):
        '''

         Pre-Gen Stage.

         Check if the output_dir exists

         Add load plugin specific config

        '''

        # Check if the path exists or not
        logger.debug('Microtesk Pre Gen Stage')
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

    @gen_hookimpl
    def gen(self, gen_config, module_dir, output_dir):

        logger.debug('Microtesk Gen Stage')
        logger.debug(module_dir)
        pytest_file = module_dir + '/microtesk_plugin/gen_framework.py'
        logger.debug(pytest_file)

        # if norun:
        #     # to display test items
        #     pytest.main([pytest_file, '--collect-only', '-n={0}'.format(jobs), '-k={0}'.format(filter), '--configlist={0}'.format(gen_config), '-v', '--seed={0}'.format(seed), '--count={0}'.format(count),'--html=microtesk_gen.html', '--self-contained-html'])
        # else:
        pytest.main([
            pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(
                self.filter), '--configlist={0}'.format(gen_config), '-v',
            '--seed={0}'.format(self.seed), '--count={0}'.format(self.count),
            '--html={0}/microtesk_gen.html'.format(output_dir),
            '--self-contained-html', '--output_dir={0}'.format(output_dir),
            '--module_dir={0}'.format(module_dir)
        ])

        # Generate Test List
        # Get the aapg dir from output
        asm_dir = output_dir + 'microtesk/asm/'
        test_list = {}
        asm_test_list = glob.glob(asm_dir + '**/*.S')
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

            # Create the base key for the test i.e. the main file under which everything is stored
            # NOTE: Here we expect the developers to probably have the proper GCC and the args, objdump as well
            base_key = os.path.basename(test)[:-2]
            test_list[base_key] = {}
            test_list[base_key][
                'work_dir'] = output_dir + 'microtesk/asm/' + base_key
            test_list[base_key]['isa'] = self.isa
            test_list[base_key]['march'] = march_str
            test_list[base_key]['mabi'] = mabi_str
            # test_list[base_key]['gcc_cmd'] = gcc_compile_bin + " " + "-march=" + arch + " " + "-mabi=" + abi + " " + gcc_compile_args + " -I " + asm_dir + include_dir + " -o $@ $< $(CRT_FILE) " + linker_args + " $(<D)/$*.ld"
            test_list[base_key]['cc'] = 'riscv64-unknown-elf-gcc'
            test_list[base_key][
                'cc_args'] = '-march=' + march_str + ' -mabi=' + mabi_str + ' -mcmodel=medany -static -std=gnu99 -O2 -fno-common -fno-builtin-printf'
            test_list[base_key][
                'linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
            # NOTE: Microtesk removes _0000 in LD files so here changing that
            linker_base = base_key[:-5]
            test_list[base_key]['linker_file'] = linker_base + '.ld'
            test_list[base_key]['asm_file'] = base_key + '.S'
            test_list[base_key]['crt_file'] = ''

        return test_list

    # generates the regress list from the generation
    @gen_hookimpl
    def post_gen(self, output_dir, regressfile):
        logger.debug('Microtesk Post Gen Stage')
        test_dict = dict()
        test_files = []
        test_file = ''
        ld_file = ''
        test_dict['microtesk'] = {}
        """
        Overwrites the microtesk entries in the regressfile with the latest present in the gendir
        """
        logger.debug(output_dir)
        logger.debug(regressfile)
        remove_list = dict()
        if os.path.isdir(output_dir):
            output_dir_list = []
            for dir, _, _ in os.walk(output_dir):
                output_dir_list.extend(
                    glob.glob(os.path.join(dir, 'microtesk_*/*.S')))
            logger.debug('Generated S files:{0}'.format(output_dir_list))
            testdir = ''
            for gentest in output_dir_list:
                testdir = os.path.dirname(gentest)
                testname = os.path.basename(gentest).replace('.S', '')
                ldname = os.path.basename(testdir)
                test_gen_dir = '{0}/../{1}'.format(testdir, testname)
                os.makedirs(test_gen_dir)
                logger.debug('created {0}'.format(test_gen_dir))
                sys_command('cp {0}/{1}.ld {2}'.format(testdir, ldname,
                                                       test_gen_dir))
                sys_command('mv {0}/{1}.S {2}'.format(testdir, testname,
                                                      test_gen_dir))
                remove_list[testdir] = 0

            for key in remove_list.keys():
                logger.debug('Removing directory: {0}'.format(testdir))
                shutil.rmtree(key)

        testdirs = os.listdir(output_dir)
        test_dict['microtesk']['microtesk_global_testpath'] = output_dir
        for testdir in testdirs:
            test_dict['microtesk'][testdir] = {'testname': '', 'ld': ''}
            testpath = output_dir + '/' + testdir
            tests = os.listdir(testpath)
            for file in tests:
                name = testpath + '/' + file
                if name.endswith('.S'):
                    test_dict['microtesk'][testdir]['testname'] = file
                elif name.endswith('.ld'):
                    test_dict['microtesk'][testdir]['ld'] = file

        if os.path.isfile(regressfile):
            with open(regressfile, 'r') as rgfile:
                testlist = yaml.safe_load(rgfile)
                testlist['microtesk'].update(test_dict)
            rgfile.close()

        rgfile = open(regressfile, 'w')

        print(test_dict)
        yaml.safe_dump(test_dict, rgfile, default_flow_style=False)
