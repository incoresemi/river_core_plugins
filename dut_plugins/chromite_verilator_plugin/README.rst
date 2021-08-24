Refer `here <https://river-core.readthedocs.io/en/stable/dut_plugins.html#chromite-dut>`_ for how to setup the chromite verilator plugin

Checking logs using **utg**:
-----------------------------------

Add this line to the ``chromite_verilator`` section of you ini file. ::
  
  check_logs = True

When check_logs is **true** (case agnostic) as well as the generator is ``utg``, the post_run phase will invoke utg to check the logs genrated from the DUT. 
