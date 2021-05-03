Testfloat Generator Plugin for river_core
=========================================

Will be removed in final commit
-------------------------------

Things to note here:
- .s -> indicates Single Precision
  .d -> indicates Double Precision
- TODO: Get the programs compiling, probably missing something in `-march` or `-mabi`
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

- Genframework

- Mon Apr 12 10:08:01 IST 2021
  Instructions supported
    6.1. Conversion Operations
        dest res1 res2 rm
    6.2. Basic Arithmetic Operations
        dest res1 res2 rm
    6.3. Fused Multiply-Add Operations
        dest res1 res2 res3 rm
    6.6. Comparison Operations
        dest res1 res2 
    6.4. Remainder Operations
    6.5. Round-to-Integer Operations
  

  Get stuff from config yaml, create folder with testfloat name, copy stuff model.H, linker to folder

Installation:
------------
1. Download `TestFloat <http://www.jhauser.us/arithmetic/TestFloat.html>`_ and `SoftFloat <http://www.jhauser.us/arithmetic/SoftFloat.html>`_.
2. Extract the archive and move to the `Build` directory.
   
    Add code block here
3. Run `make`
4. Edit the `config.yaml` with necesarry info.

Config YAML Options:
-------------------
Options to configure while using ``testfloat`` plugin:

- inst: [List] - Of instructions [Supports (Arthimetic, Fused Add, Comparison, Conversion Operations)]
- dest: (A,B) - 2 values showing the range of values to select from while creating the ASM program, this will act as the destination register
- regX: (A,B) - 2 values showing the range of values to select from while creating the ASM program, this will act as the source register(s)
- rounding-mode: List - Type of rounding mode to use for operations. Used only where applicable.
  Possible values:
    - RNE Round to nearest, ties to Even -> 0
    - RTZ Rount to Zero -> 1
    - RDN Round Down -> 2
    - RUP Round Up -> 3
    - RMM Round to Nearest, ties to Max Magnitude -> 4
    Not applicable for ``cmp`` operations
- tests_per_instruction: Number of instructions to generate per test (Needs to be above 50000, and above 6133248 for MulAdd)
- num_tests: Number of tests to generate 

Ideally total number of tests would be = num_tests * tests_per_instruction * len(rounding-mode) 
.. code-block:: yaml

        # Configuration in YAML
        set_2:
            inst: [fadd.s, fmul.s] 
            dest: 0,31
            reg1: 0,31
            reg2: 0,31
            rounding-mode: [RNE, RTZ, RDN]
            # Needs to be above 46464
            tests_per_instruction: 50000
            num_tests: 1 

        set_5:
            inst: [fmadd.s]
            dest: 0,9
            reg1: 0,12
            reg2: 0,10
            reg3: 0,10
            rounding-mode: [RUP]
            tests_per_instruction: 6133248
            num_tests: 1


