#if FSZ==64
  #define LREGF fld
  #define LREGX ld
#else
  #define LREGF flw
  #define LREGX lw
#endif

#define TEST_RR_OP(inst, destreg, freg1, freg2, rm, offset1, offset2) \
    csrrwi x0, frm, rm;   \
    LREGF freg1, offset1(x1); \
    LREGF freg2, offset2(x1); \
    inst destreg, freg1, freg2;\
    csrrs x2, fflags, x0;   \

#define TEST_RRR_OP(inst, destreg, freg1, freg2, freg3, rm, offset1, offset2, offset3) \
    csrrwi x0, frm, rm;   \
    LREGF freg1, offset1(x1); \
    LREGF freg2, offset2(x1); \
    LREGF freg3, offset3(x1); \
    inst destreg, freg1, freg2, freg3;\
    csrrs x2, fflags, x0;   \

#define TEST_R_OP(inst, destreg, freg1, rm, offset1) \
    csrrwi x0, frm, rm;   \
    LREGF freg1, offset1(x1); \
    inst destreg, freg1;\
    csrrs x2, fflags, x0;   \

#define TEST_R2_OP(inst, destreg, reg1, rm, offset1) \
    csrrwi x0, frm, rm;   \
    LREGX reg1, offset1(x1); \
    inst destreg, reg1;\
    csrrs x2, fflags, x0;   \

