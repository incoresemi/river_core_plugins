#define RVMODEL_HALT                                              \
  li t1, 1;                                                                   \
  write_tohost:                                                               \
    sw t1, tohost, t4;                                                        \
    j write_tohost;                                                           \
    fence.i;                                                                  \
    li t6,  0x20000;                                                          \
    la t5, begin_rvtest_data;                                                   \
    sw t5, 0(t6);                                                             \
    la t5, end_rvtest_data;                                                     \
    sw t5, 8(t6);                                                             \
    sw t5,  12(t6);                                                           
