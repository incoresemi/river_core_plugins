# See LICENSE for details

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
from river_core.utils import *

dut_hookimpl = pluggy.HookimplMarker('dut')


class chromite_verilator_plugin(object):
    '''
        Plugin to set chromite as the target
    '''

    @dut_hookimpl
    def init(self, ini_config, test_list, work_dir, coverage_config,
             plugin_path):
        self.name = 'chromite_verilator'
        logger.info('Pre Compile Stage')

        self.src_dir = ini_config['src_dir'].split(',')

        self.top_module = ini_config['top_module']

        self.plugin_path = plugin_path + '/'

        if coverage_config:
            self.coverage = True
        else:
            self.coverage = False

        # Get plugin specific configs from ini
        self.jobs = ini_config['jobs']

        self.filter = ini_config['filter']

        self.riscv_isa = ini_config['isa']
        if '64' in self.riscv_isa:
            self.xlen = 64
        else:
            self.xlen = 32
        self.elf = 'dut.elf'

        if coverage_config:
            logger.warn('Hope RTL binary has coverage enabled')

        self.elf2hex_cmd = 'elf2hex {0} 4194304 dut.elf 2147483648 > code.mem && '.format(
            str(int(self.xlen / 8)))
        self.objdump_cmd = 'riscv{0}-unknown-elf-objdump -D dut.elf > dut.disass && '.format(
            self.xlen)
        self.sim_cmd = './chromite_core'
        self.sim_args = '+rtldump > /dev/null'

        self.work_dir = os.path.abspath(work_dir) + '/'

        self.sim_path = self.work_dir + self.name
        os.makedirs(self.sim_path, exist_ok=True)

        self.test_list = load_yaml(test_list)

        self.json_dir = self.work_dir + '/.json/'

        # Check if dir exists
        if (os.path.isdir(self.json_dir)):
            logger.debug(self.json_dir + ' Directory exists')
        else:
            os.makedirs(self.json_dir)

        if not os.path.exists(self.sim_path):
            logger.error('Sim binary Path ' + self.sim_path + ' does not exist')
            raise SystemExit

        for path in self.src_dir:
            if not os.path.exists(path):
                logger.error('Source code ' + path + ' does not exist')
                raise SystemExit

        if shutil.which('elf2hex') is None:
            logger.error('elf2hex utility not found in $PATH')
            raise SystemExit

        if shutil.which('verilator') is None:
            logger.error('verilator utility not found in $PATH')
            raise SystemExit

        if shutil.which('bsc') is None:
            logger.error('bsc toolchain not found in $PATH')
            raise SystemExit

        if shutil.which('riscv64-unknown-elf-gcc') is None and \
                shutil.which('riscv32-unknown-elf-gcc') is None:
            logger.error('riscv-* toolchain not found in $PATH')
            raise SystemExit
        # Build verilator again

        self.verilator_speed = 'OPT_SLOW="-O3" OPT_FAST="-O3"'

        orig_path = os.getcwd()
        logger.info("Build verilator")
        os.chdir(self.sim_path)
        # header_generate = 'mkdir -p bin obj_dir + echo "#define TOPMODULE V{0}" > sim_main.h + echo "#include "V{0}.h"" >> sim_main.h'.format(
        #     self.top_module)
        # sys_command(header_generate)
        verilator_command = 'verilator {0} -O3 -LDFLAGS \
                "-static" --x-assign fast  --x-initial fast \
                --noassert sim_main.cpp --bbox-sys -Wno-STMTDLY  \
                -Wno-UNOPTFLAT -Wno-WIDTH -Wno-lint -Wno-COMBDLY \
                -Wno-INITIALDLY  --autoflush   --threads 1 \
                -DBSV_RESET_FIFO_HEAD  -DBSV_RESET_FIFO_ARRAY \
                --output-split 20000  --output-split-ctrace 10000 \
                --cc '+ self.top_module + '.v  -y ' + self.src_dir[0] + \
                ' -y ' + self.src_dir[1] + ' -y ' + self.src_dir[2] + \
                ' --exe'
        if coverage_config:
            logger.info(
                "Coverage is enabled, compiling the chromite with coverage")
            verilator_command = verilator_command.format('--coverage-line')
        else:
            logger.info(
                "Coverage is disabled, compiling the chromite with usual options"
            )
            verilator_command = verilator_command.format('')

        # create simulation header files
        sim_header = open(self.sim_path + '/sim_main.h', 'w')
        sim_header.write('#define TOPMODULE V{0}\n'.format(self.top_module))
        sim_header.write('#include "V{0}.h"\n'.format(self.top_module))
        sim_header.close()

        # copy the sim_main.cpp testbench from the plugin folder
        shutil.copy(self.plugin_path + self.name + '_plugin/sim_main.cpp',
                    self.sim_path)

        sys_command(verilator_command, 500)
        logger.info("Linking verilator simulation sources")
        sys_command("ln -f -s ../sim_main.cpp obj_dir/sim_main.cpp")
        sys_command("ln -f -s ../sim_main.h obj_dir/sim_main.h")
        make_command = 'make ' + self.verilator_speed + ' VM_PARALLEL_BUILDS=1 -j' + self.jobs + ' -C obj_dir -f V' + self.top_module + '.mk'
        logger.info("Making verilator binary")
        sys_command(make_command, 500)
        logger.info('Renaming verilator Binary')
        shutil.copy(self.sim_path + '/obj_dir/V{0}'.format(self.top_module),
                    self.sim_path + '/chromite_core')

        logger.info('Creating boot-files')
        sys_command('make -C {0} XLEN={1}'.format(
            self.plugin_path + self.name + '_plugin/boot/', str(self.xlen)))
        shutil.copy(self.plugin_path+self.name+'_plugin/boot/boot.hex' , \
                self.sim_path+'/boot.mem')

        os.chdir(orig_path)
        if not os.path.isfile(self.sim_path + '/' + self.sim_cmd):
            logger.error(self.sim_cmd + ' binary does not exist in ' +
                         self.sim_path)
            raise SystemExit

    @dut_hookimpl
    def build(self):
        logger.info('Build Hook')
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

            ch_cmd = 'cd {0} && '.format(work_dir)
            compile_cmd = '{0} {1} -march={2} -mabi={3} {4} {5} {6}'.format(\
                    cc, cc_args, arch, abi, link_args, link_file, asm_file)
            for x in attr['extra_compile']:
                compile_cmd += ' ' + x
            for x in attr['include']:
                compile_cmd += ' -I ' + str(x)
            compile_cmd += ' '.join(map(' -D{0}'.format, attr['compile_macros']))
            compile_cmd += ' -o dut.elf && '
            sim_setup = 'ln -f -s ' + self.sim_path + '/chromite_core . && '
            sim_setup += 'ln -f -s ' + self.sim_path + '/boot.mem . && '
            post_process_cmd = 'head -n -4 rtl.dump > dut.dump && rm -f rtl.dump'
            target_cmd = ch_cmd + compile_cmd + self.objdump_cmd +\
                    self.elf2hex_cmd + sim_setup + self.sim_cmd + ' ' + \
                    self.sim_args +' && '+ post_process_cmd
            make.add_target(target_cmd, test)
            self.test_names.append(test)

    @dut_hookimpl
    def run(self, module_dir):
        logger.info('Run Hook')
        logger.debug('Module dir: {0}'.format(module_dir))
        pytest_file = module_dir + '/chromite_verilator_plugin/gen_framework.py'
        logger.debug('Pytest file: {0}'.format(pytest_file))

        report_file_name = '{0}/{1}_{2}'.format(
            self.json_dir, self.name,
            datetime.datetime.now().strftime("%Y%m%d-%H%M"))

        # TODO Regression list currently removed, check back later
        # TODO The logger doesn't exactly work like in the pytest module
        pytest_state = pytest.main([
            pytest_file,
            '-x',  # Stop on first failure 
            '-n={0}'.format(self.jobs),
            '-k={0}'.format(self.filter),
            '--html={0}.html'.format(self.work_dir + '/reports/' + self.name),
            '--report-log={0}.json'.format(report_file_name),
            '--work_dir={0}'.format(self.work_dir),
            '--make_file={0}'.format(self.make_file),
            '--key_list={0}'.format(self.test_names),
            '--log-cli-level=DEBUG',
            '-o log_cli=true',
        ])
        # , '--regress_list={0}'.format(self.regress_list), '-v', '--compile_config={0}'.format(compile_config),
        if pytest_state == (pytest.ExitCode.INTERRUPTED or
                            pytest.ExitCode.TESTS_FAILED):
            logger.error(
                'DuT Plugin failed to compile tests, exiting river_core')
            raise SystemExit

        if self.coverage:
            final_cov_file = self.work_dir + '/final_coverage.dat'
            coverage_cmd = 'verilator_coverage -write {0}'.format(
                final_cov_file)
            logger.info('Initiating Merging of coverage files')
            if shutil.which('verilator_coverage') is None:
                logger.error('verilator_coverage missing from $PATH')
                raise SystemExit
            for test, attr in self.test_list.items():
                test_wd = attr['work_dir']
                if not os.path.exists(test_wd + '/coverage.dat'):
                    logger.error(\
                            'Coverage enabled but coverage file for test: '+\
                            test + ' is missing')
                else:
                    coverage_cmd += ' ' + test_wd + '/coverage.dat'
            (ret, out, error) = sys_command(coverage_cmd)
            logger.info('Final coverage file is at: {0}'.format(final_cov_file))
            logger.info('Annotating source files with final_coverage.dat')
            (ret, out, error) = sys_command(\
                'verilator_coverage {0} --annotate {1}'.format(final_cov_file,
                    self.work_dir+'/annotated_src/'))
            logger.info(
                'Annotated source available at: {0}/annotated_src'.format(
                    self.work_dir))
        return report_file_name

    @dut_hookimpl
    def post_run(self, test_dict, config):

        if config['river_core']['generator'] == 'uarch_test': 
            if (config['chromite_verilator']['check_logs']).lower() == 'true':
                logger.info('Invoking uarch_test for checking logs')
                config_file = config['uarch_test']['dut_config_yaml']
                check_log_command = 'uarch_test -cf {0} -vt'.format(config_file)
                sys_command(check_log_command)
            else:
                logger.info('Not checking logs')

        if str_2_bool(config['river_core']['space_saver']):
            logger.debug("Removing artifacts for Chromite")
            for test in test_dict:
                if test_dict[test]['result'] == 'Passed':
                    logger.debug("Removing extra files for Test: " + str(test))
                    work_dir = test_dict[test]['work_dir']
                    try:
                        os.remove(work_dir + '/app_log')
                        os.remove(work_dir + '/code.mem')
                        os.remove(work_dir + '/dut.disass')
                        os.remove(work_dir + '/dut.dump')
                        os.remove(work_dir + '/signature')
                    except:
                        logger.info(
                            "Something went wrong trying to remove the files")
