// Top-level driver for "verilated" objects (Verilog compiled with verilator)

#include <verilated.h>

#include <verilated_vcd_c.h>

#include "sim_main.h"

vluint64_t main_time = 0;    // Current simulation time

double sc_time_stamp () {    // Called by $time in Verilog
    return main_time;
}

int main (int argc, char **argv, char **env) {
    
    // Prevent unused variable warnings
    if (0 && argc && argv && env) {}

    Verilated::commandArgs (argc, argv);    // remember args
    
    // Set debug level, 0 is off, 9 is highest presently used
    Verilated::debug(0);

    // Randomization reset policy
    Verilated::randReset(2);


    TOPMODULE* top = new TOPMODULE;    // create instance of model

#if VM_TRACE
    // If verilator was invoked with --trace argument,
    // and if at run time passed the +trace argument, turn on tracing
    VerilatedVcdC* tfp = NULL;
    const char* flag = Verilated::commandArgsPlusMatch("trace");
    if (flag && 0==strcmp(flag, "+trace")) {
        Verilated::traceEverOn(true);  // Verilator must compute traced signals
        VL_PRINTF("Enabling waves into logs/vlt_dump.vcd...\n");
        tfp = new VerilatedVcdC;
        top->trace(tfp, 99);  // Trace 99 levels of hierarchy
        Verilated::mkdir("logs");
        tfp->open("logs/vlt_dump.vcd");  // Open the dump file
    }
#endif

    top->RST_N = !0;    // assert reset
    top->CLK = 0;

  while (! Verilated::gotFinish ()) {
	  main_time++;

        if ((main_time % 10) == 5) {
            top->CLK = 1;
        }
        if ((main_time % 10) == 0) {
            top->CLK = 0;
        }
        if (main_time > 1 && main_time < 107) {
            top->RST_N = !1;  // Assert reset
        } else {
            top->RST_N = !0;  // Deassert reset
        }


	  top->eval ();
#if VM_TRACE
    if (tfp) tfp->dump (main_time);
#endif
    }

    top->final ();    // Done simulating
#if VM_TRACE
    if (tfp) { tfp->close(); tfp = NULL; }
#endif

#if VM_COVERAGE
    VerilatedCov::write("coverage.dat");
#endif
    delete top;
    top = NULL;

    exit (0);
}
