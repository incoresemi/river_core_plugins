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


class chromite_cadence_plugin(object):
    '''
        Plugin to set chromite as the target
    '''

    @dut_hookimpl
    def init(self, ini_config, test_list, work_dir, coverage_config,
             plugin_path):
        self.name = 'chromite_cadence'
        logger.info('Pre Compile Stage')

        # TODO: These 2 variables need to be set by user
        self.src_dir = [
            # Verilog Dir
            '/Projects/incorecpu/jyothi.g/chromite/build/hw/verilog',
            # BSC Path
            '/Projects/incorecpu/common/bsc_23.02.2021/bsc/inst/lib/Verilog',
            # Wrapper path
            '/Projects/incorecpu/jyothi.g/chromite/bsvwrappers/common_lib'
        ]
        self.top_module = 'tb_top'

        self.plugin_path = plugin_path + '/'

        self.test_list_name = test_list.split('/')[-1].split('.')[0]

        if coverage_config is not None:
            self.coverage = True
            self.coverage_func = bool(
                distutils.util.strtobool((coverage_config['functional'])))
            self.coverage_struct = bool(
                distutils.util.strtobool((coverage_config['code'])))

        else:
            self.coverage = False
            self.coverage_func = bool(
                distutils.util.strtobool((coverage_config['functional'])))
            self.coverage_struct = bool(
                distutils.util.strtobool((coverage_config['code'])))

        if shutil.which('bsc') is None:
            logger.error('bsc not available in $PATH')
            raise SystemExit
        else:
            self.bsc_path = shutil.which("bsc")[:-7]

        # Get plugin specific configs from ini
        self.jobs = ini_config['jobs']

        self.filter = ini_config['filter']

        self.riscv_isa = ini_config['isa']
        if '64' in self.riscv_isa:
            self.xlen = 64
        else:
            self.xlen = 32
        self.elf = 'dut.elf'

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

        check_utils = ['elf2hex', 'ncvlog', 'ncelab', 'ncvlog', 'imc']

        for exe in check_utils:
            if shutil.which(exe) is None:
                logger.error(exe + ' utility not found in $PATH')
                raise SystemExit

        for path in self.src_dir:
            if not os.path.exists(path):
                logger.error('Source code ' + path + ' does not exist')
                raise SystemExit

        logger.debug('fix path in tb_top')
        tbfile = open(self.plugin_path + self.name + '_plugin/sv_top/tb_top.sv',
                      'r')
        tbfile_read = tbfile.read()
        tbfile_read = tbfile_read.replace(
            'plugin_path', self.plugin_path + self.name + '_plugin/')
        tbfile.close()
        tbfile = open(self.plugin_path + self.name + '_plugin/sv_top/tb_top.sv',
                      'w')
        tbfile.write(tbfile_read)
        tbfile.close()

        orig_path = os.getcwd()
        logger.info("Build using NCVLOG")
        os.chdir(self.sim_path)
        shutil.copy(self.plugin_path+self.name+'_plugin/hdl.var', \
                self.sim_path)
        shutil.copy(self.plugin_path+self.name+'_plugin/cds.lib', \
                self.sim_path)
        os.makedirs(self.sim_path + '/work', exist_ok=True)
        # header_generate = 'mkdir -p bin obj_dir + echo "#define TOPMODULE V{0}" > sim_main.h + echo "#include "V{0}.h"" >> sim_main.h'.format(
        #     self.top_module)
        # sys_command(header_generate)
        ncvlog_cmd = 'ncvlog -64BIT -sv -cdslib ./cds.lib -hdlvar ./hdl.var \
                +define+TOP={0} +define+BSV_RESET_FIFO_HEAD  \
                +define+BSV_RESET_FIFO_ARRAY \
                {4}/sv_top/tb_top.sv \
                {5}/lib/Verilog/main.v \
                -y {1} -y {2} -y {3} '                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  .format( \
                self.top_module, self.src_dir[0], self.src_dir[1], \
                self.src_dir[2], self.plugin_path+self.name+'_plugin', \
                self.bsc_path)
        ncelab_cmd = 'ncelab -64BIT {0} -cdslib ./cds.lib -hdlvar ./hdl.var work.main \
                -timescale 1ns/1ps '

        if self.coverage:
            ncelab_cmd = ncelab_cmd.format('+access+rw')
        else:
            ncelab_cmd = ncelab_cmd.format('')

        if self.coverage_struct and self.coverage_func:
            logger.info("Structural and functional coverage are enabled")
            ncelab_cmd = ncelab_cmd + ' -coverage ALL '
        elif self.coverage_struct and not self.coverage_func:
            logger.info("Structural coverage is enabled")
            ncelab_cmd = ncelab_cmd + ' -coverage ALL  ' + ' -covdut mkccore_axi4 '
        elif self.coverage_func and not self.coverage_struct:
            logger.info("functional coverage is enabled")
            ncelab_cmd = ncelab_cmd + ' -coverage functional '
        else:
            logger.info("coverage is disabled")
            ncelab_cmd = ncelab_cmd.format('')
            #if not self.coverage_func:
            #ncelab_cmd = ncelab_cmd + ' -covdut mkccore_axi4 '

        sys_command(ncvlog_cmd, 500)
        sys_command(ncelab_cmd, 500)
        logger.info("Making ncsim binary")

        for test, attr in self.test_list.items():
            with open('chromite_core_{0}'.format(test), 'w') as f:
                f.write('ncsim -64BIT +rtldump -COVOVERWRITE -covtest ' + test +
                        ' -cdslib ./cds.lib -hdlvar ./hdl.var work.main\n')
                if self.coverage:
                    f.write('imc -exec imc.cmd\n')
            logger.info('Renaming Binary')
            sys_command('chmod +x chromite_core_{0}'.format(test))

        #logger.info('Renaming Binary')
        #sys_command('chmod +x chromite_core')

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
            compile_cmd += ' -o dut.elf && '
            with open(work_dir + '/imc.cmd', 'w') as f:
                f.write('load ' + work_dir + '/cov_work/scope/' + test + '\n')
                f.write(
                    'report -overwrite -out coverage_code.html -html -detail \
                -metrics overall -all -aspect both -assertionStatus \
                -allAssertionCounters -type *\n')
                f.write(
                    'report -overwrite -out coverage_code.rpt -detail -metrics \
                code -all -aspect both -assertionStatus -allAssertionCounters \
                -type *\n')
            sim_setup = 'ln -f -s ' + self.sim_path + '/chromite_core_{0} . && '.format(
                test)
            sim_setup += 'ln -f -s ' + self.sim_path + '/boot.mem . && '
            sim_setup += 'ln -f -s ' + self.sim_path + '/cds.lib . && '
            sim_setup += 'ln -f -s ' + self.sim_path + '/hdl.var . && '
            sim_setup += 'ln -f -s ' + self.sim_path + '/work . && '
            post_process_cmd = 'head -n -4 rtl.dump > dut.dump && rm -f rtl.dump'
            target_cmd = ch_cmd + compile_cmd + self.objdump_cmd +\
                    self.elf2hex_cmd + sim_setup + self.sim_cmd + '_' + test + ' ' + \
                    self.sim_args +' && '+ post_process_cmd
            make.add_target(target_cmd, test)
            self.test_names.append(test)

    @dut_hookimpl
    def run(self, module_dir):
        logger.info('Run Hook')
        logger.debug('Module dir: {0}'.format(module_dir))
        pytest_file = module_dir + '/chromite_cadence_plugin/gen_framework.py'
        logger.debug('Pytest file: {0}'.format(pytest_file))

        report_file_name = '{0}/{1}_{2}'.format(
            self.json_dir, self.name,
            datetime.datetime.now().strftime("%Y%m%d-%H%M"))

        # TODO Regression list currently removed, check back later
        # TODO The logger doesn't exactly work like in the pytest module
        # pytest.main([pytest_file, '-n={0}'.format(self.jobs), '-k={0}'.format(self.filter), '-v', '--compileconfig={0}'.format(compile_config), '--html=compile.html', '--self-contained-html'])
        # breakpoint()
        pytest.main([
            pytest_file,
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

        if self.coverage:
            merge_cmd = 'merge -out ' + self.work_dir + '/reports/' + '/final_coverage '
            rank_cmd = 'rank -out ' + self.work_dir + '/reports/' + '/final_rank -runfile ' + self.work_dir + '/run_list -html'
            logger.info('Initiating Merging of coverage files')
            for test, attr in self.test_list.items():
                test_wd = attr['work_dir']
                merge_cmd += ' ' + test_wd + '/cov_work/scope/' + test + '/'
                #rank_cmd += ' ' + test_wd + '/cov_work/scope/' + test + '/'
                with open(self.work_dir + '/run_list', 'a+') as r:
                    r.write(test_wd + '/cov_work/scope/' + test + '/ \n')
            with open(self.work_dir + '/merge_imc.cmd', 'w') as f:
                f.write(merge_cmd + ' \n')
                f.write('load -run ./reports/final_coverage\n')
                f.write('report -overwrite -out ' + self.work_dir +
                        'reports/final_coverage_html -html -detail \
                -metrics overall -all -aspect both -assertionStatus \
                -allAssertionCounters -type *\n')
                f.write(rank_cmd + '\n')

            orig_path = os.getcwd()
            os.chdir(self.work_dir)
            (ret, out, error) = sys_command('imc -exec merge_imc.cmd')
            os.chdir(orig_path)

            logger.info(
                'Final coverage file is at: {0}'.format(self.work_dir +
                                                        '/final_coverage_html'))
            logger.info('Final rank file is at: {0}'.format(self.work_dir +
                                                            '/final_rank'))
        return report_file_name

    @dut_hookimpl
    def post_run(self, test_dict, config):
        if str_2_bool(config['river_core']['space_saver']):
            logger.debug("Going to remove stuff now")
            for test in test_dict:
                if test_dict[test]['result'] == 'Passed':
                    logger.debug("Removing extra files for Test: " + str(test))
                    work_dir = test_dict[test]['work_dir']
                    # List of all files deemed uncessary to reduce space usage
                    try:
                        os.remove(work_dir + '/app_log')
                        os.remove(work_dir + '/code.mem')
                        os.remove(work_dir + '/coverage_code.rpt')
                        os.remove(work_dir + '/dut.disass')
                        os.remove(work_dir + '/dut.dump')
                        os.remove(work_dir + '/signature')
                        os.remove(work_dir + '/imc.log')
                        os.remove(work_dir + '/imc.cmd')
                        os.remove(work_dir + '/imc.key')
                        os.remove(work_dir + '/mdv.log')
                        os.remove(work_dir + '/ncsim.log')
                    except:
                        logger.info(
                            "Something went wrong trying to remove the files")

    @dut_hookimpl
    def merge_db(self, db_files, output_db, config):

        # Add commands to run here :)
        # TODO: DOC: Ensure plugin developers understand the reason for using final_coverage  and other hardcoded values
        logger.info('Initiating Merging of coverage files')
        merge_cmd = 'merge -overwrite -out ' + str(
            output_db) + '/final_coverage/ '
        rank_cmd = 'rank -overwrite -out ' + str(
            output_db) + '/final_html_rank/ -html '
        for db_file in db_files:
            merge_cmd += ' ' + os.path.dirname(db_file)
            rank_cmd += ' ' + os.path.dirname(db_file)
        with open(output_db + '/final_coverage/final_merge_imc.cmd', 'w') as f:
            f.write(merge_cmd + ' \n')
            f.write('load -run ' + str(output_db) + '/final_coverage/' + '\n')
            f.write('report -overwrite -out ' + str(output_db) + '/final_html/'
                    ' -html -detail \
            -metrics overall -all -aspect both -assertionStatus \
            -allAssertionCounters -type *\n')
            f.write(rank_cmd + ' ' + str(output_db) + '/final_coverage' + '\n')

        orig_path = os.getcwd()
        os.chdir(output_db + '/final_coverage')

        (ret, out, error) = sys_command('imc -exec final_merge_imc.cmd')

        # HTML Web pages
        final_html = output_db + '/final_html/index.html'
        final_rank_html = output_db + '/final_html_rank/rank_sub_dir/rank.html'
        os.chdir(orig_path)

        return final_html, final_rank_html
