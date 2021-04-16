interface chromite_intf(input bit CLK,RST_N);
logic [74:0]decoder_func_32;
logic EN_update_eEpoch;
logic EN_update_wEpoch;

//mkstage0 signals
logic rg_eEpoch;
logic rg_wEpoch;
logic rg_fence;
logic rg_sfence;
logic rg_pc_EN;
logic [63:0]rg_pc_D_IN;
logic [63:0]rg_pc;
logic [64:0]rg_delayed_redirect;
logic [65:0]ma_flush_fl;
logic [65:0]bpu_mav_prediction_response_r;
logic [31 : 0] decoder_func_32_inst;

//fn_decompress signal
logic [15:0]fn_decompress_inst;
logic [31:0]fn_decompress;

///--------coverpoints for functional coverage -------////

covergroup decoder_cg @(posedge CLK);
option.per_instance=1;
//option.get_inst_coverage=1;
   rs1addr: coverpoint decoder_func_32[73:69] {
                   bins rs1_addr_bin[32] = { [0:31] } iff (decoder_func_32[53:52] == 2'b0);
   						} 
    
   rs2addr: coverpoint decoder_func_32[68:54] {
                   bins rs2_addr_bin[32] = { [0:31] } iff (decoder_func_32[51:49] == 2'b0);
   						} 

   rs3addr:  coverpoint decoder_func_32[58:54] {
			bins raddr_bin[32] ={[0:31]};
						}

   rdaddr:  coverpoint decoder_func_32[63:59] {
			bins raddr_bin[32] ={[0:31]};
						}

decoder_func_32_inst_cp: coverpoint decoder_func_32_inst {

//RV32I Base Instruction Set
                wildcard bins LUI  	 = {32'bxxxxxxxxxxxxxxxxxxxxxxxxx0110111};
		wildcard bins AUIPC	 = {32'bxxxxxxxxxxxxxxxxxxxxxxxxx0010111};
		wildcard bins JAL  	 = {32'bxxxxxxxxxxxxxxxxxxxxxxxxx1101111};
		wildcard bins JALR 	 = {32'bxxxxxxxxxxxxxxxxxxxxxxxxx1100111};
		wildcard bins BEQ  	 = {32'bxxxxxxxxxxxxxxxxx000xxxxx1100011};
		wildcard bins BNE  	 = {32'bxxxxxxxxxxxxxxxxx001xxxxx1100011};
		wildcard bins BLT  	 = {32'bxxxxxxxxxxxxxxxxx100xxxxx1100011};
		wildcard bins BGE  	 = {32'bxxxxxxxxxxxxxxxxx101xxxxx1100011};
		wildcard bins BLTU 	 = {32'bxxxxxxxxxxxxxxxxx110xxxxx1100011};
		wildcard bins BGEU 	 = {32'bxxxxxxxxxxxxxxxxx111xxxxx1100011};
		wildcard bins LB   	 = {32'bxxxxxxxxxxxxxxxxx000xxxxx0000011};
		wildcard bins LH   	 = {32'bxxxxxxxxxxxxxxxxx001xxxxx0000011};
		wildcard bins LW   	 = {32'bxxxxxxxxxxxxxxxxx010xxxxx0000011};
		wildcard bins LBU  	 = {32'bxxxxxxxxxxxxxxxxx100xxxxx0000011};
		wildcard bins LHU  	 = {32'bxxxxxxxxxxxxxxxxx101xxxxx0000011};
		wildcard bins SB   	 = {32'bxxxxxxxxxxxxxxxxx000xxxxx0100011};
		wildcard bins SH   	 = {32'bxxxxxxxxxxxxxxxxx001xxxxx0100011};
		wildcard bins SW   	 = {32'bxxxxxxxxxxxxxxxxx010xxxxx0100011};
		wildcard bins ADDI 	 = {32'bxxxxxxxxxxxxxxxxx000xxxxx0010011};
		wildcard bins SLTI  	 = {32'bxxxxxxxxxxxxxxxxx010xxxxx0010011};
		wildcard bins SLTIU	 = {32'bxxxxxxxxxxxxxxxxx011xxxxx0010011};
		wildcard bins XORI 	 = {32'bxxxxxxxxxxxxxxxxx100xxxxx0010011};
		wildcard bins ORI  	 = {32'bxxxxxxxxxxxxxxxxx110xxxxx0010011};
		wildcard bins ANDI 	 = {32'bxxxxxxxxxxxxxxxxx111xxxxx0010011};
		wildcard bins SLLI 	 = {32'b0000000xxxxxxxxxx001xxxxx0010011};
		wildcard bins SRLI 	 = {32'b0000000xxxxxxxxxx101xxxxx0010011};
		wildcard bins SRAI 	 = {32'b0100000xxxxxxxxxx101xxxxx1010011};
		wildcard bins ADD  	 = {32'b0000000xxxxxxxxxx000xxxxx0110011};
		wildcard bins SUB  	 = {32'b0100000xxxxxxxxxx000xxxxx0110011};
		wildcard bins SLL  	 = {32'b0000000xxxxxxxxxx001xxxxx0110011};
		wildcard bins SLT  	 = {32'b0000000xxxxxxxxxx010xxxxx0110011};
		wildcard bins SLTU 	 = {32'b0000000xxxxxxxxxx011xxxxx0110011};
		wildcard bins XOR  	 = {32'b0000000xxxxxxxxxx100xxxxx0110011};
		wildcard bins SRL  	 = {32'b0000000xxxxxxxxxx101xxxxx0110011};
		wildcard bins SRA   	 = {32'b0100000xxxxxxxxxx101xxxxx0110011};
		wildcard bins OR    	 = {32'b0000000xxxxxxxxxx110xxxxx0110011};
		wildcard bins AND   	 = {32'b0000000xxxxxxxxxx111xxxxx0110011};
		wildcard bins FENCE      = {32'bxxxxxxxxxxxxxxxxx000xxxxx0001111};
		wildcard bins FENCE_TSO  = {32'b10000011001100000000000000001111};
		wildcard bins PAUSE      = {32'b00000001000000000000000000001111};
		wildcard bins ECALL      = {32'b00000000000000000000000001110011};
		wildcard bins EBREAK     = {32'b00000000000100000000000001110011};
//RV64I Base Instruction Set
		wildcard bins LWU        = {32'bxxxxxxxxxxxxxxxxx110xxxxx0000011};
		wildcard bins LD         = {32'bxxxxxxxxxxxxxxxxx011xxxxx0000011};
		wildcard bins SD         = {32'bxxxxxxxxxxxxxxxxx011xxxxx0100011};
		wildcard bins SLLI_64    = {32'b000000xxxxxxxxxxx001xxxxx0010011};
		wildcard bins SRLI_64    = {32'b000000xxxxxxxxxxx101xxxxx0010011};
		wildcard bins SRAI_64    = {32'b010000xxxxxxxxxxx101xxxxx0010011};
		wildcard bins ADDIW  	 = {32'bxxxxxxxxxxxxxxxxx000xxxxx0011011};
		wildcard bins SLLIW      = {32'b0000000xxxxxxxxxx001xxxxx0011011};
		wildcard bins SRLIW      = {32'b0000000xxxxxxxxxx101xxxxx0011011};
		wildcard bins SRAIW      = {32'b0000000xxxxxxxxxx101xxxxx0011011};
		wildcard bins ADDW       = {32'b0000000xxxxxxxxxx000xxxxx0111011};
		wildcard bins SUBW       = {32'b0100000xxxxxxxxxx000xxxxx0111011};
		wildcard bins SLLW       = {32'b0000000xxxxxxxxxx001xxxxx0111011};
		wildcard bins SRLW       = {32'b0000000xxxxxxxxxx101xxxxx0111011};
		wildcard bins SRAW       = {32'b0100000xxxxxxxxxx101xxxxx0111011};

//RV32/RV64 Zifencei Standard Extension
		wildcard bins FENCE_I  	 = {32'bxxxxxxxxxxxxxxxxx001xxxxx0001111};

//RV32/RV64 Zicsr Standard Extension
		wildcard bins CSRRW  	 = {32'bxxxxxxxxxxxxxxxxx001xxxxx1110011};
		wildcard bins CSRRS  	 = {32'bxxxxxxxxxxxxxxxxx010xxxxx1110011};
		wildcard bins CSRRC  	 = {32'bxxxxxxxxxxxxxxxxx011xxxxx1110011};
		wildcard bins CSRRWI  	 = {32'bxxxxxxxxxxxxxxxxx101xxxxx1110011};
		wildcard bins CSRRSI  	 = {32'bxxxxxxxxxxxxxxxxx110xxxxx1110011};
		wildcard bins CSRRCI  	 = {32'bxxxxxxxxxxxxxxxxx111xxxxx1110011};

//RV32M Standard Extension		
		wildcard bins MUL        = {32'b0000001xxxxxxxxxx000xxxxx0110011};
		wildcard bins MULH       = {32'b0000001xxxxxxxxxx001xxxxx0110011};
		wildcard bins MULHSU     = {32'b0000001xxxxxxxxxx010xxxxx0110011};
		wildcard bins MULHU      = {32'b0000001xxxxxxxxxx011xxxxx0110011};
		wildcard bins DIV        = {32'b0000001xxxxxxxxxx100xxxxx0110011};
		wildcard bins DIVU       = {32'b0000001xxxxxxxxxx101xxxxx0110011};
		wildcard bins REM        = {32'b0000001xxxxxxxxxx110xxxxx0110011};
		wildcard bins REMU       = {32'b0000001xxxxxxxxxx111xxxxx0110011};

//RV64M Standard Extension		
		wildcard bins MULW       = {32'b0000001xxxxxxxxxx000xxxxx0111011};
		wildcard bins DIVW       = {32'b0000001xxxxxxxxxx100xxxxx0111011};
		wildcard bins DIVUW      = {32'b0000001xxxxxxxxxx101xxxxx0111011};
		wildcard bins REMW       = {32'b0000001xxxxxxxxxx110xxxxx0111011};
		wildcard bins REMUW      = {32'b0000001xxxxxxxxxx111xxxxx0111011};

//RV32A Standard Extension		
		wildcard bins LR_W       = {32'b00010xx00000xxxxx010xxxxx0101111};
		wildcard bins SC_W       = {32'b00011xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOSWAP_W  = {32'b00001xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOADD_W   = {32'b00000xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOXOR_W   = {32'b00100xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOAND_W   = {32'b01100xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOOR_W    = {32'b01000xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOMIN_W   = {32'b10000xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOMAX_W   = {32'b10100xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOMINU_W  = {32'b11000xxxxxxxxxxxx010xxxxx0101111};
		wildcard bins AMOMAXU_W  = {32'b11100xxxxxxxxxxxx010xxxxx0101111};

//RV64A Standard Extension		
		wildcard bins LR_D       = {32'b00010xx00000xxxxx011xxxxx0101111};
		wildcard bins SC_D       = {32'b00011xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOSWAP_D  = {32'b00001xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOADD_D   = {32'b00000xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOXOR_D   = {32'b00100xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOAND_D   = {32'b01100xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOOR_D    = {32'b01000xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOMIN_D   = {32'b10000xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOMAX_D   = {32'b10100xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOMINU_D  = {32'b11000xxxxxxxxxxxx011xxxxx0101111};
		wildcard bins AMOMAXU_D  = {32'b11100xxxxxxxxxxxx011xxxxx0101111};

//RV32F Standard Extension
		wildcard bins FLW  	 = {32'bxxxxxxxxxxxxxxxxx010xxxxx0000111};
		wildcard bins FSW  	 = {32'bxxxxxxxxxxxxxxxxx010xxxxx0100111};
		wildcard bins FMADD_S 	 = {32'bxxxxx00xxxxxxxxxxxxxxxxxx1000011};
		wildcard bins FMSUB_S  	 = {32'bxxxxx00xxxxxxxxxxxxxxxxxx1000111};
		wildcard bins FNMSUB_S   = {32'bxxxxx00xxxxxxxxxxxxxxxxxx1001011};
		wildcard bins FNMADD_S 	 = {32'bxxxxx00xxxxxxxxxxxxxxxxxx1001111};
		wildcard bins FADD_S  	 = {32'b0000000xxxxxxxxxxxxxxxxxx1010011};
		wildcard bins FSUB_S  	 = {32'b0000100xxxxxxxxxxxxxxxxxx1010011};
		wildcard bins FMUL_S  	 = {32'b0001000xxxxxxxxxxxxxxxxxx1010011};
		wildcard bins FDIV_S  	 = {32'b0001100xxxxxxxxxxxxxxxxxx1010011};
		wildcard bins FSQRT_S  	 = {32'b010110000000xxxxxxxxxxxxx1010011};
		wildcard bins FSGNJ_S  	 = {32'b0010000xxxxxxxxxx000xxxxx1010011};
		wildcard bins FSGNJN_S 	 = {32'b0010000xxxxxxxxxx001xxxxx1010011};
		wildcard bins FSGNJX_S 	 = {32'b0010000xxxxxxxxxx010xxxxx1010011};
		wildcard bins FMIN_S  	 = {32'b0010100xxxxxxxxxx000xxxxx1010011};
		wildcard bins FMAX_S 	 = {32'b0010100xxxxxxxxxx001xxxxx1010011};
		wildcard bins FCVT_W_S 	 = {32'b110000000000xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_WU_S	 = {32'b110000000001xxxxxxxxxxxxx1010011};
		wildcard bins FMV_X_W  	 = {32'b111000000000xxxxx000xxxxx1010011};
		wildcard bins FEQ_S 	 = {32'b1010000xxxxxxxxxx010xxxxx1010011};
		wildcard bins FLT_S  	 = {32'b1010000xxxxxxxxxx001xxxxx1010011};
		wildcard bins FLE_S  	 = {32'b1010000xxxxxxxxxx000xxxxx1010011};
		wildcard bins FCLASS_S 	 = {32'b111000000000xxxxx001xxxxx1010011};
		wildcard bins FCVT_S_W 	 = {32'b110100000000xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_S_WU	 = {32'b110100000001xxxxxxxxxxxxx1010011};
		wildcard bins FMV_W_X  	 = {32'b111100000000xxxxx000xxxxx1010011};

//RV64F Standard Extension
		wildcard bins FCVT_L_S 	 = {32'b110000000010xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_LU_ 	 = {32'b110000000011xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_S_L 	 = {32'b110100000010xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_S_LU	 = {32'b110100000011xxxxxxxxxxxxx1010011};

//RV32D Standard Extension

		wildcard bins FLD  	 = {32'bxxxxxxxxxxxxxxxxx011xxxxx0000111};
		wildcard bins FSD  	 = {32'bxxxxxxxxxxxxxxxxx011xxxxx0100111};

		wildcard bins FMADD_D 	 = {32'bxxxxx01xxxxxxxxxxxxxxxxxx1000011};
		wildcard bins FMSUB_D  	 = {32'bxxxxx01xxxxxxxxxxxxxxxxxx1000111};
		wildcard bins FNMSUB_D   = {32'bxxxxx01xxxxxxxxxxxxxxxxxx1001011};
		wildcard bins FNMADD_D 	 = {32'bxxxxx01xxxxxxxxxxxxxxxxxx1001111};

		wildcard bins FADD_D  	 = {32'b0000001xxxxxxxxxxxxxxxxxx1010011};
		wildcard bins FSUB_D  	 = {32'b0000101xxxxxxxxxxxxxxxxxx1010011};
		wildcard bins FMUL_D  	 = {32'b0001001xxxxxxxxxxxxxxxxxx1010011};
		wildcard bins FDIV_D  	 = {32'b0001101xxxxxxxxxxxxxxxxxx1010011};

		wildcard bins FSQRT_D  	 = {32'b010110100000xxxxxxxxxxxxx1010011};

		wildcard bins FSGNJ_D  	 = {32'b0010001xxxxxxxxxx000xxxxx1010011};
		wildcard bins FSGNJN_D 	 = {32'b0010001xxxxxxxxxx001xxxxx1010011};
		wildcard bins FSGNJX_D 	 = {32'b0010001xxxxxxxxxx010xxxxx1010011};
		wildcard bins FMIN_D  	 = {32'b0010101xxxxxxxxxx000xxxxx1010011};
		wildcard bins FMAX_D 	 = {32'b0010101xxxxxxxxxx001xxxxx1010011};

		wildcard bins FCVT_S_D 	 = {32'b010000000001xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_D_S	 = {32'b010000100000xxxxxxxxxxxxx1010011};

		wildcard bins FEQ_D 	 = {32'b1010001xxxxxxxxxx010xxxxx1010011};
		wildcard bins FLT_D  	 = {32'b1010001xxxxxxxxxx001xxxxx1010011};
		wildcard bins FLE_D  	 = {32'b1010001xxxxxxxxxx000xxxxx1010011};

		wildcard bins FCLASS_D 	 = {32'b111000100000xxxxx001xxxxx1010011};
		wildcard bins FCVT_W_D 	 = {32'b110000100000xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_WU_D	 = {32'b110000100001xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_D_W 	 = {32'b110100100000xxxxxxxxxxxxx1010011};
		wildcard bins FCVT_D_WU  = {32'b110100100001xxxxxxxxxxxxx1010011};

//RV64D Standard Extension

		wildcard bins FCVT_L_D 	 = {32'b110000100010xxxxx001xxxxx1010011};
		wildcard bins FCVT_LU_D  = {32'b110000100011xxxxx001xxxxx1010011};
		wildcard bins FMV_X_D 	 = {32'b111000100000xxxxx001xxxxx1010011};
		wildcard bins FCVT_D_L 	 = {32'b110100100010xxxxx001xxxxx1010011};
		wildcard bins FCVT_D_LU	 = {32'b110100100011xxxxx001xxxxx1010011};
		wildcard bins FMV_D_X	 = {32'b111100100000xxxxx001xxxxx1010011};
						}
endgroup 

// MSTAGE0 module coverpoints
covergroup mkstage0_cg @(posedge CLK);
option.per_instance=1;
//Covpt-1: register rg_eEpoch must have toggled from 0->1 and 1->0.
 reg_eEpoch: coverpoint rg_eEpoch {
	bins rg_eEpoch_0to1_1to0 =(0=>1);
	bins rg_eEpoch_1to0 =(1=>0);
				  }

//Covpt-2: register rg_wEpoch must have toggled from 0->1 and 1->0.
reg_wEpoch: coverpoint rg_wEpoch {
	bins rg_wEpoch_0to1 =(0=>1);
	bins rg_wEpoch_1to0 =(1=>0);
				   }

///Covpt-3: Both rg_eEpoch and rg_wEpoch toggle (any direction) in the same cycle.				}
rg_eEpoch : coverpoint rg_eEpoch {
	bins rg_eEpoch_0to1_1to0 =(0=>1),(1=>0);
				  }
rg_wEpoch : coverpoint rg_wEpoch {
	bins rg_wEpoch_0to1_1to0 =(0=>1),(1=>0);
				  }
cross_rg_eEpoch_rg_wEpoch: cross rg_eEpoch,rg_wEpoch;
 


//Covpt-4: register rg_fence must go from 0->1
reg_fence: coverpoint rg_fence {
	bins rg_fence_0to1 =(0=>1);
				}

//Covpt-5: register rg_sfence must go from 0->1
reg_sfence: coverpoint rg_sfence {
	bins rg_sfence_0to1 =(0=>1);

}
//Covpt-6: number of times rg_pc was incremented by 4. This can be achieved by checking if the difference between rg_pc_DIN and rg_pc is 4 when rg_pc_EN is set.
rg_pc_increment_4:coverpoint((rg_pc_D_IN-rg_pc=='d4) && (rg_pc_EN==1'b1)) {
    bins rg_pc_increment_4_bin ={1};
}

//Covpt-7: similar to above, but check if rg_pc_DIN is the same as the upper 64-bits of bpu_mav_prediction_response_r.
rg_pc_DIN_increment_4:coverpoint(( bpu_mav_prediction_response_r[65:2]==rg_pc_D_IN) && (rg_pc_EN==1'b1)) {
    bins rg_pc_DIN_increment_4_bin ={1};
}

//Covpt-8: number of times rg_pc was assigned the value held in the lower 64 bits of "rg_delayed_redirect"
rg_delayed_redirect :coverpoint (rg_pc==rg_delayed_redirect[63:0] && (rg_pc_EN==1'b1)){
     bins rg_delayed_redirect_bin ={1};
}

//Covpt-9: upper 64-bits of ma_flush_fl input signal is 2 byte (0th bit is reset and 1st bit is set) aligned atleast once.
ma_flush_fl_2byte_aligned:coverpoint ma_flush_fl[3:2]
 {
      bins ma_flush_fl_2byte_aligned ={2'b10} iff  (ma_flush_fl[65:2] %2 ==1'b0 && ((ma_flush_fl[65:2] %4 !=1'b0)) );

} 

//Cover-10 upper 64-bits of ma_flush_fl input signal is 4 byte (0th bit is set and 1st bit is set) aligned atleast once.
ma_flush_fl_4byte_aligned:coverpoint ma_flush_fl[3:2]
 {
      bins ma_flush_fl_4byte_aligned ={2'b11} iff  (ma_flush_fl[65:2] %4 ==1'b0/* && ((ma_flush_fl[65:2] %8 !=1'b0))*/);

} 

endgroup

//mkstag1 covergroup
covergroup mkstage1_cg @(posedge CLK);
option.per_instance=1;
//---RVC, Quadrant 0 instructions----//

fn_decompress_inst_cp : coverpoint fn_decompress_inst { 

	wildcard bins ILLEGAL    = {16'b0};
	wildcard bins C_ADDI4SPN = {16'b000_xxxxxxxx_xxx_00};//(RES, nzuimm=0)
	wildcard bins C_FLD	 = {16'b001_xxx_xxx_xx_xxx_00};
	wildcard bins C_LW 	 = {16'b010_xxx_xxx_xx_xxx_00};
	wildcard bins C_FSD	 = {16'b101_xxx_xxx_xx_xxx_00};
	wildcard bins C_SW	 = {16'b110_xxx_xxx_xx_xxx_00};
`ifdef RV32	
        wildcard bins C_FSW	 = {16'b111_xxx_xxx_xx_xxx_00}; 
	wildcard bins C_FLW	 = {16'b011_xxx_xxx_xx_xxx_00};
`endif
`ifdef RV64
	wildcard bins C_SD	 = {16'b111_xxx_xxx_xx_xxx_00};
	wildcard bins C_LD	 = {16'b011_xxx_xxx_xx_xxx_00};
`endif


//---RVC, Quadrant 1 instructions----//
	wildcard bins C_NOP	 = {16'b000_x_00000_xxxxx_01};//(HINT, nzimm! = 0)
	wildcard bins C_ADDI	 = {16'b000_x_xxxxx_xxxxx_01} iff (fn_decompress_inst[11:7]!=5'b0);//(HINT, nzimm = 0)
 	// only rd!=0 HOW TO GET rd
	wildcard bins C_LI	 = {16'b010_x_xxxxx_xxxxx_01} iff (fn_decompress_inst[11:7]!=5'b0);//(HINT, rd=0)
	wildcard bins C_ADDI16SP = {16'b011_x_00010_xxxxx_01} ;//(RES, nzimm=0)
	wildcard bins C_LUI      = {16'b011_x_xxxxx_xxxxx_01} iff (fn_decompress_inst[11:7]!=5'b0 && fn_decompress_inst[11:7]!=5'd2);//(RES, nzimm=0; HINT, rd=0)
	wildcard bins C_ANDI	 = {16'b100_x_10_xxx_xxxxx_01};
 	wildcard bins C_SUB	 = {16'b100_0_11_xxx_00_xxx_01};
 	wildcard bins C_XOR	 = {16'b100_0_11_xxx_01_xxx_01};
 	wildcard bins C_OR	 = {16'b100_0_11_xxx_10_xxx_01};
 	wildcard bins C_AND	 = {16'b100_0_11_xxx_11_xxx_01};
	wildcard bins C_J	 = {16'b101_x_xx_xxx_xx_xxx_01};
	wildcard bins C_BEQZ	 = {16'b110_xxx_xxx_xxxxx_01};
	wildcard bins C_BNEZ	 = {16'b111_xxx_xxx_xxxxx_01};
	// CHECK:TO move under RV64
 	wildcard bins C_SRLI64	 = {16'b100_0_00_xxx_00000_01};//(RV128; RV32/64 HINT)
	// CHECK:TO move under RV64
	wildcard bins C_SRAI64	 = {16'b100_0_01_xxx_00000_01};//(RV128; RV32/64 HINT)

`ifdef RV32	
	wildcard bins C_JAL	 = {16'b001_xxxxxxxxxxx_01};//(RV32)
	wildcard bins C_SRLI	 = {16'b100_1_00_xxx_xxxxx_01};//(RV32 Custom, nzuimm[5]=1) //change
	wildcard bins C_SRAI	 = {16'b100_1_01_xxx_xxxxx_01};//(RV32 Custom, nzuimm[5]=1)
`endif

`ifdef RV64
	wildcard bins C_ADDIW	 = {16'b001_x_xxxxx_xxxxx_01} iff (fn_decompress_inst[11:7]!=5'b0);//(RV64/128; RES, rd=0)
	wildcard bins C_SUBW	 = {16'b100_1_11_xxx_00_xxx_01};//(RV64/128; RV32 RES)
	wildcard bins C_ADDW	 = {16'b100_1_11_xxx_01_xxx_01};//(RV64/128; RV32 RES)

`endif

//---RVC, Quadrant 2 instructions---//

	wildcard bins C_SLLI64	 = {16'b000_0_xxxxx_00000_10} iff (fn_decompress_inst[11:7]!=5'b0); //(RV128; RV32/64 HINT; HINT, rd=0)
	wildcard bins C_FLDSP	 = {16'b001_x_xxxxx_xxxxx_10};//( RV32/64)
	wildcard bins C_LWSP	 = {16'b010_x_xxxxx_xxxxx_10}  iff (fn_decompress_inst[11:7]!=5'b0); //(RES, rd=0)
	wildcard bins C_JR	 = {16'b100_0_xxxxx_00000_10}  iff (fn_decompress_inst[11:7]!=5'b0); //(RES, rs1=0)
	wildcard bins C_MV	 = {16'b100_0_xxxxx_xxxxx_10}  iff (fn_decompress_inst[11:7]!=5'b0 && (fn_decompress_inst[6:2]!=5'b0) ); //(HINT, rd=0)
	wildcard bins C_EBREAK	 = {16'b100_1_00000_00000_10};
	wildcard bins C_JALR	 = {16'b100_1_xxxxx_00000_10}  iff (fn_decompress_inst[11:7]!=5'b0);
	wildcard bins C_ADD	 = {16'b100_1_xxxxx_xxxxx_10}  iff (fn_decompress_inst[11:7]!=5'b0 && (fn_decompress_inst[6:2]!=5'b0) );//(HINT, rd=0)

	wildcard bins C_FSDSP	 = {16'b101_xxxxxx_xxxxx_10};//(RV32/64)
	wildcard bins C_SWSP	 = {16'b110_xxxxxx_xxxxx_10};//(RV32/64)
	

`ifdef RV32	
	wildcard bins C_SLLI	 = {16'b000_x_xxxxx_xxxxx_10} iff (fn_decompress_inst[11:7]!=5'b0);//(HINT, rd=0; RV32 Custom, nzuimm[5]=1)
	wildcard bins C_FLWSP	 = {16'b011_x_xxxxx_xxxxx_10};//(RV32)
	wildcard bins C_FSWSP	 = {16'b11_xxxxxx_xxxxx_10};//(RV32)
`endif

`ifdef RV64	
	wildcard bins C_LDSP	 = {16'b011_x_xxxxx_xxxxx_10} iff (fn_decompress_inst[11:7]!=5'b0);//(RV64/128; RES, rd=0)
	wildcard bins C_SDSP	 = {16'b111_xxxxxx_xxxxx_10};//(RV64/128)
`endif

}
endgroup
decoder_cg  dec_cg=new();
mkstage0_cg mks0_cg=new();
mkstage1_cg mks1_cg =new();
initial
 begin
dec_cg.sample();
mks0_cg.sample();
mks1_cg.sample();
end


		//--------assertions for chromite core---------//

//Assertion-1: rg_pc[0] must always be 0
always@(posedge CLK) 
begin
 if(RST_N==1'b1) assert(!rg_pc[0]);
end

//Assertion-2: When either rg_eEpoch or rg_wEpoch toggle, the msb bit of rg_delayed_redirect must be reset to 0 in the next cycle
property rg_delayed_redirect_prop;
//@(rg_eEpoch or rg_wEpoch) (1) |-> ##1 rg_delayed_redirect[64]==1'b0;

@(posedge CLK) ($rose(rg_eEpoch) || $rose(rg_wEpoch)|| $fell(rg_eEpoch)|| $fell(rg_wEpoch) ) |-> ##1 rg_delayed_redirect[64]==1'b0;
endproperty

always @(posedge CLK)
rg_delayed_redirect_assert: assert property (rg_delayed_redirect_prop);

cover property(rg_delayed_redirect_prop);


property fn_decomp_reserved_prop;
@(posedge CLK) fn_decompress_inst==(16'b010_x_00000_xxxxx_10)  |-> fn_decompress==32'b0 ;
endproperty

always @(posedge CLK)
fn_decomp_reserved_assert: assert property (fn_decomp_reserved_prop);

endinterface

