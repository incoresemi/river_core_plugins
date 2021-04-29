
//`define RV32

`ifndef RV64
`define RV64

`define BSV_RESET_NAME RST_N
`include "interface.sv"
module tb_top(input CLK,RST_N);
 chromite_intf intf(CLK,RST_N);
 mkTbSoc mktbsoc(.CLK(intf.CLK),.RST_N(intf.RST_N));
//bit [65:0]decoder_func_32; 
always @(posedge CLK)
begin
if(!RST_N) begin
//intf.decoder_func_32 =75'b0;
intf.decoder_func_32 = mktbsoc.soc.ccore.riscv.stage2.instance_decoder_func_32_2.decoder_func_32;
 intf.decoder_func_32_inst =mktbsoc.soc.ccore.riscv.stage2.instance_decoder_func_32_2.decoder_func_32_inst;
intf.fn_decompress_inst =mktbsoc.soc.ccore.riscv.stage1.instance_fn_decompress_0.fn_decompress_inst ;
 intf.fn_decompress      =mktbsoc.soc.ccore.riscv.stage1.instance_fn_decompress_0.fn_decompress ;
intf.rg_eEpoch=mktbsoc.soc.ccore.riscv.stage0.rg_eEpoch;
 intf.rg_wEpoch=mktbsoc.soc.ccore.riscv.stage0.rg_wEpoch;
 intf.rg_fence=mktbsoc.soc.ccore.riscv.stage0.rg_fence;
 intf.rg_sfence=mktbsoc.soc.ccore.riscv.stage0.rg_sfence;
 intf.rg_pc_D_IN=mktbsoc.soc.ccore.riscv.stage0.rg_pc_D_IN;
 intf.rg_pc=mktbsoc.soc.ccore.riscv.stage0.rg_pc;
 intf.rg_pc_EN=mktbsoc.soc.ccore.riscv.stage0.rg_pc_EN;
 intf.rg_delayed_redirect=mktbsoc.soc.ccore.riscv.stage0.rg_delayed_redirect;
 intf.ma_flush_fl=mktbsoc.soc.ccore.riscv.stage0.ma_flush_fl;
 intf.bpu_mav_prediction_response_r=mktbsoc.soc.ccore.riscv.stage0.bpu_mav_prediction_response_r;
end
else begin
//decoder_func_32 signal
 intf.decoder_func_32 = mktbsoc.soc.ccore.riscv.stage2.instance_decoder_func_32_2.decoder_func_32;
 intf.decoder_func_32_inst =mktbsoc.soc.ccore.riscv.stage2.instance_decoder_func_32_2.decoder_func_32_inst;

//fn_decompress signal 
 intf.fn_decompress_inst =mktbsoc.soc.ccore.riscv.stage1.instance_fn_decompress_0.fn_decompress_inst ;
 intf.fn_decompress      =mktbsoc.soc.ccore.riscv.stage1.instance_fn_decompress_0.fn_decompress ;

//mkstage2 signals
 intf.EN_update_eEpoch=mktbsoc.soc.ccore.riscv.stage2.EN_update_eEpoch;
 intf.EN_update_wEpoch=mktbsoc.soc.ccore.riscv.stage2.EN_update_wEpoch;
//mkstage0 signals
 intf.rg_eEpoch=mktbsoc.soc.ccore.riscv.stage0.rg_eEpoch;
 intf.rg_wEpoch=mktbsoc.soc.ccore.riscv.stage0.rg_wEpoch;
 intf.rg_fence=mktbsoc.soc.ccore.riscv.stage0.rg_fence;
 intf.rg_sfence=mktbsoc.soc.ccore.riscv.stage0.rg_sfence;
 intf.rg_pc_D_IN=mktbsoc.soc.ccore.riscv.stage0.rg_pc_D_IN;
 intf.rg_pc=mktbsoc.soc.ccore.riscv.stage0.rg_pc;
 intf.rg_pc_EN=mktbsoc.soc.ccore.riscv.stage0.rg_pc_EN;
 intf.rg_delayed_redirect=mktbsoc.soc.ccore.riscv.stage0.rg_delayed_redirect;
 intf.ma_flush_fl=mktbsoc.soc.ccore.riscv.stage0.ma_flush_fl;
 intf.bpu_mav_prediction_response_r=mktbsoc.soc.ccore.riscv.stage0.bpu_mav_prediction_response_r;

end
end
initial
  begin
   // $recordfile("tb_top.trn");
    //$recordvars();
  end
endmodule
`endif



		


