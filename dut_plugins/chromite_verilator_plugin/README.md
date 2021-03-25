# river_core plugin for Chromite [based on Verilator]

To use this plugin you will need clone the chromite_core generator repo and generate the verilog
required for simulation. Once the verilof has been generated, please do the following changes in the
plugin:

### Things to configure

- In `chromite_verilator_plugin.py`
1. `self.src_dir` = List with strings
[0] - # Verilog Dir [ending with 'build/hw/verilog/']
[1] - # BSC Path [ending with 'lib/Verilog']
[2] - # Wrapper path [ending with 'chromite/bsvwrappers/common_lib']
e.g:
```python
['/scratch/git-repo/incoresemi/core-generators/chromite/build/hw/verilog/',
'/software/open-bsc/lib/Verilog',
'/scratch/git-repo/incoresemi/core-generators/chromite/bsvwrappers/common_lib']
```
2. `self.top_module` = string
'mkTbSoc' [Default] / [Modify if required]
