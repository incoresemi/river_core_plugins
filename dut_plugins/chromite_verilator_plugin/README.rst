Refer here: https://river-core.readthedocs.io/en/stable/dut_plugins.html#chromite-dut For how to setup the chromite verilator plugin

Checking logs using **uarch_test**:
-----------------------------------

Add this line to the `chromite_verilator` section of you ini file. When check_logs is **true** (case agnostic) as well as the generator is `uarch_test`, the post_run phase will invoke uarch_test to check the logs genrated from the DUT. 
```
check_logs = True
```
