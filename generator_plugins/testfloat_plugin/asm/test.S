#include "test.h"
#include "model.h"

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:

inst_0:
TEST_FPRR_OP(fadd.s, f31, f22, f1, 2, 0x90000, 0x13, 0x9, 0x10000)

inst_1:
TEST_FPRR_OP(fadd.s, f31, f22, f1, 2, 0x90000, 0x13, 0x9, 0x10000)

rvtest_code_end:
RVMODEL_HALT

