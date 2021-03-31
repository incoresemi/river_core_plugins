# See LICENSE for details

import os
import sys
import pluggy
import shutil
from river_core.log import logger
import river_core.utils as utils
from river_core.constants import *
import random
import re
import datetime
import pytest
from envyaml import EnvYAML

# Output globals.
# This is done, because writing to file is complicated business
test_file = []
parameter_list = []
folder_dir = ''
file_ctr = 0

# ASM Filter
header = '''#include "test.h"
#include "model.h"
.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:'''
footer = '''rvtest_code_end:
RVMODEL_HALT'''


def create_asm(gen_file):
    work_dir = os.path.dirname(os.path.realpath(gen_file))
    local_folder_dir = folder_dir + '/testfloat_plugin/asm/'
    # copy stuff for asm
    logger.info('Copying Header files')
    shutil.copy(local_folder_dir + 'test.h',
                os.path.splitext(gen_file)[0] + '.h')
    shutil.copy(local_folder_dir + 'model.h',
                os.path.splitext(gen_file)[0] + '-model.h')
    shutil.copy(local_folder_dir + 'link.ld',
                os.path.splitext(gen_file)[0] + '.ld')

    # Parsing from parameters
    asm_inst = parameter_list[file_ctr][0]
    # TODO check if this needs to change
    # Can come from the inst as well
    dest_reg = 'f' + str(parameter_list[file_ctr][1])
    reg_1 = 'f' + str(parameter_list[file_ctr][2])
    reg_2 = 'f' + str(parameter_list[file_ctr][3])
    mode = parameter_list[file_ctr][4]
    # Create test.S
    # Clean up the file data
    with open(gen_file, 'r') as gen_file_data:
        logger.debug('Reading gen files')
        gen_data = gen_file_data.read().splitlines()
    # Add steps to write to file
    assembly_file = os.path.splitext(gen_file)[0] + '.S'
    with open(assembly_file, 'w+') as asm_file_pointer:
        logger.info('Generating in the ASM file')
        asm_file_pointer.write(header)
        for case_index in range(0, len(gen_data)):
            case_data = gen_data[case_index].split(' ')
            value_1 = '0x' + str(case_data[0])
            value_2 = '0x' + str(case_data[1])
            expected_result = '0x' + str(case_data[2])
            exception_flag = '0x' + str(case_data[3])
            generated_asm_inst = '\ninst_{0}:\nTEST_FPRR_OP({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9})\n'.format(
                case_index, asm_inst, dest_reg, reg_1, reg_2, mode,
                expected_result, exception_flag, value_1, value_2)
            asm_file_pointer.write(generated_asm_inst)
        asm_file_pointer.write(footer)


def gen_cmd_list(gen_config, seed, count, output_dir, module_dir):

    global folder_dir
    global parameter_list
    folder_dir = module_dir
    logger.debug('Now generating commands for gen plugin')
    try:
        env_gen_list = EnvYAML(gen_config)
    except:
        logger.error("Is your plugin YAML file properly configured?")
        raise SystemExit

    inst_yaml_list = utils.load_yaml(gen_config)
    setup_dir = ''
    testfloat_bin = ''
    run_command = []
    global test_file
    for key, value in inst_yaml_list.items():
        if key == 'gen_binary_path':
            testfloat_bin = inst_yaml_list[key]
        dirname = output_dir + '/testfloat'

        if re.search('^instructions', key):

            inst_list = inst_yaml_list[key]['inst']
            # Using index so as to ensure that we can iterate both
            for inst_index in range(0, len(inst_list)):
                rounding_mode_gen = ''
                rounding_mode_int = 0
                param_list = []
                inst = inst_list[inst_index]
                param_list.append(inst)
                # Get precision
                inst_prefix = ''
                if '.s' in inst:
                    inst_prefix = 'f32'
                if '.d' in inst:
                    inst_prefix = 'f64'
                if '.q' in inst:
                    inst_prefix = 'f128'
                # Dest
                dest = inst_yaml_list[key]['dest'].split(',')
                dest = random.randint(int(dest[0]), int(dest[1]))
                param_list.append(dest)
                dest_reg = 'f' + str(dest)
                # Register 1
                reg1 = inst_yaml_list[key]['reg1'].split(',')
                reg1 = random.randint(int(reg1[0]), int(reg1[1]))
                param_list.append(reg1)
                reg1_reg = 'f' + str(reg1)
                # Register 2
                reg2 = inst_yaml_list[key]['reg2'].split(',')
                reg2 = random.randint(int(reg2[0]), int(reg2[1]))
                param_list.append(reg2)
                reg2_reg = 'f' + str(reg2)
                rounding_mode = inst_yaml_list[key]['rounding-mode']
                tests_per_instruction = int(
                    inst_yaml_list[key]['tests_per_instruction'])
                # Convert the string to values
                if rounding_mode == 'RNE':
                    rounding_mode_int = 0
                    rounding_mode_gen = '-rnear_even'
                elif rounding_mode == 'RTZ':
                    rounding_mode_int = 1
                    rounding_mode_gen = '-rminMag'
                elif rounding_mode == 'RDN':
                    rounding_mode_int = 2
                    rounding_mode_gen = '-rmin'
                elif rounding_mode == 'RUP':
                    rounding_mode_int = 3
                    rounding_mode_gen = '-rmax'
                elif rounding_mode == 'RMM':
                    rounding_mode_int = 4
                    rounding_mode_gen = '-rnear_maxMag'
                # Get other info
                template_name = os.path.basename(inst)
                param_list.append(rounding_mode_int)
                for i in range(int(count)):
                    if seed == 'random':
                        gen_seed = random.randint(0, 10000)
                    else:
                        gen_seed = int(seed)

                    now = datetime.datetime.now()
                    gen_prefix = '{0:06}_{1}'.format(
                        gen_seed, now.strftime('%d%m%Y%H%M%S%f'))
                    test_prefix = 'testfloat_{0}_{1}_{2:05}'.format(
                        template_name, gen_prefix, i)
                    testdir = '{0}/asm/{1}/'.format(dirname, test_prefix)
                    # TODO Need to find a way to fix this, can't write to file this way
                    try:
                        os.makedirs(testdir, exist_ok=True)
                    except:
                        logger.error(
                            "Unable to create a directory, exiting tests")
                        raise SystemExit
                    run_command.append(
                        '{0} -seed {1} -n {2} {3} {4}_{5}'.format(
                            testfloat_bin, gen_seed, tests_per_instruction,
                            rounding_mode_gen, inst_prefix, inst[1:-2],
                            test_prefix))
                    test_file.append(testdir + test_prefix + '.gen')
                    parameter_list.append(param_list)

    return run_command


def idfnc(val):
    return val


def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        test_list = gen_cmd_list(metafunc.config.getoption("configlist"),
                                 metafunc.config.getoption("seed"),
                                 metafunc.config.getoption("count"),
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("module_dir"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request):
    # compile tests
    global file_ctr
    logger.debug('Generating commands from test_input fixture')
    program = request.param
    (ret, out, err) = utils.sys_command_file(program, test_file[file_ctr])
    create_asm(test_file[file_ctr])
    file_ctr = file_ctr + 1
    return ret, err


def test_eval(test_input):
    assert test_input[0] == 0
