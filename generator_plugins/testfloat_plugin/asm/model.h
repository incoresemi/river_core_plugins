#define RVMODEL_HALT                                              \
   li gp,1; \
   sw gp, tohost, t5; \
   fence.i; \
   li t6,  0x20000; \
   la t5, begin_rvtest_data; \
   sw t5, 0(t6); \
   la t5, begin_rvtest_data+8; \
   sw t5, 8(t6); \
   sw t5,  12(t6); \

//  li t1, 1;                                                                   \
  write_tohost:                                                               \
    sw t1, tohost, t4;                                                        \
    li t6,  0x20000;                                                          \
    sw t5,  12(t6);                                                           \
    j write_tohost
