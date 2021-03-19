`define BSV_RESET_NAME RST_N
`include "/Projects/incorecpu/vinay.kariyanna/rc_new/river_core_plugins/dut_plugins/sv_top/interface.sv"
module tb_top(input CLK,RST_N);
 chromite_intf intf(CLK,RST_N);
 mkTbSoc mktbsoc(.CLK(intf.CLK),.RST_N(intf.RST_N));
//bit [65:0]decoder_func_32; 
always @(posedge CLK)
begin
if(!RST_N)
begin
intf.decoder_func_32 =75'b0;
end
else 
begin
 intf.decoder_func_32 = mktbsoc.soc.ccore.riscv.stage2.instance_decoder_func_32_2.decoder_func_32;
 intf.EN_update_eEpoch=mktbsoc.soc.ccore.riscv.stage2.EN_update_eEpoch;
 intf.EN_update_wEpoch=mktbsoc.soc.ccore.riscv.stage2.EN_update_wEpoch;
end
end

initial
  begin
    $recordfile("tb_top.trn");
    $recordvars();
  end
endmodule
