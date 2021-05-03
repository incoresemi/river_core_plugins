#if FSZ==64
  #define FTOX fmv.x.d
  #define XTOF fmv.d.x
  #define LREG fld
#else
  #define FTOX fmv.x.w
  #define XTOF fmv.w.x
  #define LREG flw
#endif

#define TEST_AR_OP(inst, destreg, freg1, freg2, rm, correctval, correctflags, val1, val2) \
    li x1, val1;  \
    XTOF freg1, x1;  \
    li x1, val2;  \
    XTOF freg2, x1;  \
    csrrwi x0, frm, rm;   \
    inst destreg, freg1, freg2;\
    csrrs x1, fflags, x0;   \

#define TEST_RR_OP(inst, destreg, freg1, freg2, rm, offset1, offset2) \
    csrrwi x0, frm, rm;   \
    LREG freg1, offset1(x1); \
    LREG freg2, offset2(x1); \
    inst destreg, freg1, freg2;\
    csrrs x1, fflags, x0;   \

#define TEST_CVT_OP(inst, destreg, reg1, rm, correctval, correctflags, val1) \
    li x1, val1;  \
    XTOF reg1, x1;  \
    csrrwi x0, frm, rm;   \
    inst destreg, reg1;   \
    csrrs x1, fflags, x0;

/* TODO */
#define TEST_MIN_MAX_OP(inst, destreg, freg1, freg2, correctval, correctflags, val1, val2) \
    li x1, val1;  \
    XTOF freg1, x1;  \
    li x1, val2;  \
    XTOF freg2, x1;  \
    csrrwi x0, frm, rm;   \
    inst destreg, freg1, freg2;   \
    csrrs x1, fflags, x0;
