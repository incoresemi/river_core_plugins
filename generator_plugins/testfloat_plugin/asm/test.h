#if FSZ==64
  #define FTOX fmv.x.d
  #define XTOF fmv.d.x
#else
  #define FTOX fmv.x.w
  #define XTOF fmv.w.x
#endif

#define TEST_FPRR_OP(inst, destreg, freg1, freg2, rm, correctval, correctflags, val1, val2) \
    li x1, val1;  \
    XTOF freg1, x1;  \
    li x1, val2;  \
    XTOF freg2, x1;  \
    csrrwi x0, frm, rm;   \
    inst destreg, freg1, freg2;   \
    li x2, correctval;  \
    FTOX x1, destreg;  \
    bne x1, x2, rvtest_code_end; \
    csrrs x1, fflags, x0;   \
    li x2, correctflags;  \
    bne x1, x2, rvtest_code_end;

