  
#define RVMODEL_HALT                                              \
  li x1, 1;                                                                   \
  write_tohost:                                                               \
    sw x1, tohost, t5;                                                        \
    j write_tohost;                                                           \
    fence.i;                                                                  \
    li t6,  0x20000;                                                          \
    la t5, begin_signature;                                                   \
    sw t5, 0(t6);                                                             \
    la t5, end_signature;                                                     \
    sw t5, 8(t6);                                                             \
    sw t5,  12(t6);                                                           \

