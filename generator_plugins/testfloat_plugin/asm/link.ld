OUTPUT_ARCH( "riscv" )
ENTRY(rvtest_entry_point)

SECTIONS
{
  . = 2147483648;
  .text.init : { *(.text.init) }
  .text : { *(.text) }

  /* data segment */
  .data : { *(begin_rvtest_data*) }


  . = ALIGN(0x100000);
  .tohost : { *(.tohost) }
  .rodata : { *(rodata) }

  /* End of uninitalized data segement */
  _end = .;
}
