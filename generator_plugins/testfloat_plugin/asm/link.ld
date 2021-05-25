OUTPUT_ARCH( "riscv" )
ENTRY(rvtest_entry_point)

SECTIONS
{
  . = 0x80000000;
  .text.init : { *(.text.init) }
  .text : { *(.text) }

  /* data segment */
  .data : { *(begin_rvtest_data*) }


  . = ALIGN(0x100);
  .tohost : { *(.tohost) }
  .rodata : { *(rodata) }

  /* End of uninitalized data segement */
  _end = .;
}
