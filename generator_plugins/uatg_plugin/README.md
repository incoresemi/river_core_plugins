## changes to be made in river_core.ini to enable uatg generator
```
[uatg]
jobs = 4
count = 1
seed = random
dut_config_yaml = /path/to/config.yaml/file/of/dut
modules_dir = /path/to/modulesdir
work_dir = /user's/preferred/workdir
linker_dir = /the/directory/containing/link.ld/and/model_test.h/files
modules = all
generate_covergroups = true
alias_file = /path/to/aliasing/file 
check_logs = True
```

In addition to this change, update the generator parameter to select uatg as shown.
```
generator = uatg
```
