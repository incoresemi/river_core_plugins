#if FSZ==64
  #define LREG fld
#else
  #define LREG flw
#endif

#define TEST_RR_OP(inst, destreg, freg1, freg2, rm, offset1, offset2) \
    csrrwi x0, frm, rm;   \
    LREG freg1, offset1(x1); \
    LREG freg2, offset2(x1); \
    inst destreg, freg1, freg2;\
    csrrs x2, fflags, x0;   \

#define TEST_RRR_OP(inst, destreg, freg1, freg2, freg3, rm, offset1, offset2, offset3) \
    csrrwi x0, frm, rm;   \
    LREG freg1, offset1(x1); \
    LREG freg2, offset2(x1); \
    LREG freg3, offset3(x1); \
    inst destreg, freg1, freg2, freg3;\
    csrrs x2, fflags, x0;   \

#define TEST_R_OP(inst, destreg, freg1, rm, offset1) \
    csrrwi x0, frm, rm;   \
    LREG freg1, offset1(x1); \
    inst destreg, freg1;\
    csrrs x2, fflags, x0;   \

