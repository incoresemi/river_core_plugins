Testfloat Generator Plugin for river_core
=========================================

Installation:
------------
Download `TestFloat <http://www.jhauser.us/arithmetic/TestFloat.html>`_ and `SoftFloat <http://www.jhauser.us/arithmetic/SoftFloat.html>`_.

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
    Ignored for ``cmp`` operations
- tests_per_instruction: Number of instructions to generate per test (Needs to be above 50000, and above 6133248 for MulAdd)
- num_tests: Number of tests to generate 

Ideally total number of tests would be = num_tests * tests_per_instruction * len(rounding-mode) 
