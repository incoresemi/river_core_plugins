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
import re

gen_hookimpl = pluggy.HookimplMarker("generator")


class AapgPlugin(object):
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
        logger.debug('AAPG Pre Gen Stage')
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

    # gets the yaml file with list of configs; test count; parallel
    @gen_hookimpl
    def gen(self, gen_config, module_dir, output_dir):

        logger.debug('AAPG Plugin gen phase')
        logger.debug(module_dir)
        pytest_file = module_dir + '/aapg_plugin/gen_framework.py'
        logger.debug(pytest_file)

        # if norun:
        #     # to display test items
        #     pytest.main([pytest_file, '--collect-only', '-n={0}'.format(jobs), '-k={0}'.format(filter), '--configlist={0}'.format(gen_config), '-v',  '--seed={0}'.format(seed), '--count={0}'.format(count), '--html=aapg_gen.html', '--self-contained-html'])
        # else:
        pytest.main([
            pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter),
            '--configlist={0}'.format(gen_config), '-v',
            '--seed={0}'.format(self.seed), '--count={0}'.format(self.count),
            '--html={0}/aapg_gen.html'.format(output_dir),
            '--self-contained-html', '--output_dir={0}'.format(output_dir),
            '--module_dir={0}'.format(module_dir)
        ])
        # Generate Test List
        # Get the aapg dir from output
        asm_dir = output_dir + '/aapg/asm/'
        test_list = {}
        asm_test_list = glob.glob(asm_dir+'**/*[!_template].S')
        # asm_templates = glob.glob(asm_dir+'/**/*.S')
        for test in asm_test_list:
            with open(test,'r') as file:
                test_asm = file.read()
            isa = set()
            isa.add('i')
            xlen = 64
            dist_list = re.findall(r'^#\s*(rel_.*?)$',test_asm,re.M|re.S)
            for dist in dist_list:
                ext = dist.split(':')[0][4:].split('.')[0]
                ext_count = int(dist.split(':')[1])

                if ext_count != 0:
                    if 'rv64' in ext :
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
            canonical_order = {'i':0, 'm':1, 'a':2, 'f':3, 'd':4, 'c':5}
            canonical_isa = sorted(list(isa), key=lambda d: canonical_order[d])
            march_str = 'rv'+str(xlen)+"".join(canonical_order)

            # Create the base key for the test i.e. the main file under which everything is stored
            # NOTE: Here we expect the developers to probably have the proper GCC and the args, objdump as well
            base_key = os.path.basename(test)
            test_list[base_key]={}
            test_list[base_key]['work_dir'] = output_dir+'/aapg/asm/'+str(base_key)[:-2]
            test_list[base_key]['isa'] = self.isa
            test_list[base_key]['path'] = test
            test_list[base_key]['march'] = march_str
            # test_list[base_key]['gcc_cmd'] = gcc_compile_bin + " " + "-march=" + arch + " " + "-mabi=" + abi + " " + gcc_compile_args + " -I " + asm_dir + include_dir + " -o $@ $< $(CRT_FILE) " + linker_args + " $(<D)/$*.ld"
        testfile = open(output_dir+'/test_list.yaml','w')
        yaml.safe_dump(test_list, testfile, default_flow_style=False)
        testfile.close()

        return test_list
    # generates the regress list from the generation
    @gen_hookimpl
    def post_gen(self, output_dir, regressfile):
        test_dict = dict()
        test_files = []
        test_file = ''
        ld_file = ''
        test_dict['aapg'] = {}
        """
        Overwrites the aapg entries in the regressfile with the latest present in the gendir
        """
        remove_list = dict()
        test_dict['aapg']['aapg_global_testpath'] = output_dir
        if os.path.isdir(output_dir):
            output_dir_list = []
            for dirname in os.listdir(output_dir):
                if re.match('^aapg_.*', dirname):
                    test_dict['aapg'][dirname] = {
                        'testname': '',
                        'ld': '',
                        'template': ''
                    }
                    test_dict['aapg'][dirname]['testname'] = dirname + '.S'
                    test_dict['aapg'][dirname]['ld'] = dirname + '.ld'
                    test_dict['aapg'][dirname][
                        'template'] = dirname + '_template.S'

        if os.path.isfile(regressfile):
            with open(regressfile, 'r') as rgfile:
                testlist = yaml.safe_load(rgfile)
                testlist['aapg'].update(test_dict)
            rgfile.close()

        rgfile = open(regressfile, 'w')

        yaml.safe_dump(test_dict, rgfile, default_flow_style=False)
