=============================
Cadence Plugin for RiVer_Core
=============================

Checking logs using **uarch_test**:
-----------------------------------

Add this line to the ``chromite_cadence`` section of you ini file. ::
  
  check_logs = True

When check_logs is **true** (case agnostic) as well as the generator is ``uarch_test``, the post_run phase will invoke uarch_test to check the logs genrated from the DUT. 
