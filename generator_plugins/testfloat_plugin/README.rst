Testfloat Generator Plugin for river_core
=========================================

Will be removed in final commit
-------------------------------


Things to note here:
- testfloat_gen creates a file containing values:
   C010FFFF7FFFFFFE | BCAFFFFF00001FFE | C010FFFF7FFFFFFE | 01
   Operand 1          Operand 2           Expected Value    Exception Flags

- According to the documentation
    On each line, the first two numbers are the operands for the floating-point addition, and the third and fourth numbers are the expected floating-point result (the sum) and the exception flags raised. Exception flags are encoded with one bit per flag as follows:
    bit 0   inexact exception
    bit 1   underflow exception
    bit 2   overflow exception
    bit 3   infinite exception (“divide by zero”)
    bit 4   invalid exception

- Plugin design 
  
  The testfloat binary would be configured in config.yaml.
  - PreGen
    Check if all things exists, get info from the config.ini.
    Check for the ISA values, if ISA doesn't match then, raiseError
  - Gen
    1. Check if the binary exists, else raiseError exit.
    2. Then create folder for `asm` similar to AAPG with test name and time.
    3. Generate ASM files, I guess rest of the files can be copied into the folder, similar to what chromite_verilator does.
    4. Create a possible Makefile ?
  - PostGen
    Nothing planned at the moment
