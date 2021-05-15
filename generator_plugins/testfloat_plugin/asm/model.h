#define RVMODEL_HALT                                              \
  li t1, 1;                                                                   \
  write_tohost:                                                               \
    sw t1, tohost, t4;                                                        \
    li t6,  0x20000;                                                          \
    sw t5,  12(t6);                                                           \
    j write_tohost
