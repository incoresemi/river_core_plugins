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

#define TEST_CMP_OP(inst, destreg, freg1, freg2, rm, correctval, correctflags, val1, val2) \
    li x1, val1;  \
    XTOF freg1, x1;  \
    li x1, val2;  \
    XTOF freg2, x1;  \
    csrrwi x0, frm, rm;   \
    inst destreg, freg1, freg2;   \
    csrrs x1, fflags, x0;

#define TEST_FMADD_OP(inst, destreg, freg1, freg2, freg3, rm, correctval, correctflags, val1, val2, val3) \
    li x1, val1;  \
    XTOF freg1, x1;  \
    li x1, val2;  \
    XTOF freg2, x1;  \
    li x1, val3;  \
    XTOF freg3, x1;  \
    csrrwi x0, frm, rm;   \
    inst destreg, freg1, freg2, freg3;   \
    li x2, correctval;  \
    FTOX x1, destreg;  \
    bne x1, x2, rvtest_code_end; \
    csrrs x1, fflags, x0;   \
    li x2, correctflags;  \
    bne x1, x2, rvtest_code_end;
