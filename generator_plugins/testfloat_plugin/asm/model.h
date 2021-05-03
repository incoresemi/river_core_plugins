  
#define RVMODEL_HALT                                              \
  li x1, 1;                                                                   \
  write_tohost:                                                               \
    fence.i;                                                                  \
    li t6,  0x20000;                                                          \
    sw t5,  12(t6);                                                           \

