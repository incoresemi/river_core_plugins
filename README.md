# river_core_plugins

## changes to be made in river_core.ini to enable uarch_test generator
```
[uarch_test]
jobs = 4
count = 1
seed = random
dut_config_yaml = /path/to/config.yaml/file/of/dut
work_dir = /users/preferred/workdir
linker_dir = /the/directory/containing/link.ld/and/model_test.h/files
modules = all
```
Here, 
- dut_config_yaml should be an absolute path
- work_dir should be an absolute path to the work_dir the user prefers, if nothing is specified, uarch_test's default dir will be used.
- linker_dir should be an absolute path to the directory containing **link.ld** and **model_test.h** files. if nothing is specified, uarch_test will create the files in the work_dir
- modules should be a comma separated string listing the modules of dut for which the tests are needed. This is a required parameter. **all** creates tests for all the modules

In addition to this change, update the generator parameter to select uarch_test as shown.
```
generator = uarch_test
```
