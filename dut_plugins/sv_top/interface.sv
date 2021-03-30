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

///Covpt-3: Both rg_eEpoch and rg_wEpoch toggle (any direction) in the same cycle.

///--------coverpoints for functional coverage -------////

covergroup decoder_cg @(posedge CLK);
option.per_instance=1;
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
//Covpt-1: register rg_eEpoch must have toggled from 0->1 and 1->0.
 reg_eEpoch: coverpoint rg_eEpoch {
	bins rg_eEpoch_0to1 =(0=>1);
	bins rg_eEpoch_1to0 =(1=>0);
				  }

//Covpt-2: register rg_wEpoch must have toggled from 0->1 and 1->0.
reg_wEpoch: coverpoint rg_wEpoch {
	bins rg_wEpoch_0to1 =(0=>1);
	bins rg_wEpoch_1to0 =(1=>0);
				   }

//Covpt-4: register rg_fence must go from 0->1
reg_fence: coverpoint rg_fence {
	bins rg_fence_0to1 =(0=>1);
				}

//Covpt-5: register rg_sfence must go from 0->1
reg_sfence: coverpoint rg_sfence {
	bins rg_sfence_0to1 =(0=>1);
				}

rg_eEpoch : coverpoint rg_eEpoch {
	bins rg_eEpoch_0to1_1to0 =(0=>1),(1=>0);
				  }
rg_wEpoch : coverpoint rg_wEpoch {
	bins rg_wEpoch_0to1_1to0 =(0=>1),(1=>0);
				  }


cross_rg_eEpoch_rg_wEpoch: cross rg_eEpoch,rg_wEpoch;
 


/*rg_pc0: coverpoint rg_pc[0] {
 bins rg_pc0={1'b0};
			   }*/


/*ma_flush_fl_2byte_aligned:coverpoint (ma_flush_fl[65:2] %2 ==64'b0 && ma_flush_fl[0]==1'b0 && ma_flush_fl[1]==1'b1)
 {
      bins ma_flush_fl_2byte_aligned ={0};
}
 
ma_flush_fl_4byte_aligned:coverpoint  (ma_flush_fl[65:2] %4 ==64'b0 && ma_flush_fl[0]==1'b1 && ma_flush_fl[1]==1'b1)

 {
      bins ma_flush_fl_4byte_aligned ={0};

} */


//Covpt-9: upper 64-bits of ma_flush_fl input signal is 2 byte (0th bit is reset and 1st bit is set) aligned atleast once.
ma_flush_fl_2byte_aligned:coverpoint ma_flush_fl[3:2]
 {
      bins ma_flush_fl_2byte_aligned ={2'b10} iff  (ma_flush_fl[65:2] %2 ==1'b0 && ((ma_flush_fl[65:2] %4 !=1'b0)) );

} 

//Cover-10 upper 64-bits of ma_flush_fl input signal is 4 byte (0th bit is set and 1st bit is set) aligned atleast once.
ma_flush_fl_4byte_aligned:coverpoint ma_flush_fl[3:2]
 {
      bins ma_flush_fl_4byte_aligned ={2'b11} iff  (ma_flush_fl[65:2] %4 ==1'b0 && ((ma_flush_fl[65:2] %8 !=1'b0)));

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
endgroup

decoder_cg  cg=new();
initial
 begin
cg.sample();
end


		//--------assertions for chromite core---------//

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


///Covpt-3: Both rg_eEpoch and rg_wEpoch toggle (any direction) in tEhe same cycle.
property rg_eEpoch_wEpoch_toggle_same_cycle ;
@(posedge CLK) (1) |-> (($rose(rg_eEpoch) && $fell(rg_wEpoch)) ||  ($rose(rg_eEpoch) && $rose(rg_wEpoch)) ||  ($fell(rg_eEpoch) && $rose(rg_wEpoch))|| ($fell(rg_eEpoch)&& $fell(rg_wEpoch))) ;
endproperty

/*always @(posedge CLK)
rg_eEpoch_wEpoch_toggle_same_cycle_assert: assert property(rg_eEpoch_wEpoch_toggle_same_cycle);*/


/*sequence s1;
@(posedge CLK) ((decoder_func_32[63:59])  ##[1:4] (((decoder_func_32[73:69]==decoder_func_32[63:59]) || (decoder_func_32[68:64]==decoder_func_32[63:59])) ));
endsequence 

sequence s2;
@(posedge CLK) ((decoder_func_32[63:59])  ##1 (!EN_update_eEpoch && !EN_update_wEpoch)[*4]);
endsequence


//when rdaddr==25 check if in the next 4 cycles rs1addr or rs2addr == 25 and rdaddr != 25. In these 4 cycles EN_update_eEpoch and EN_update_wEpoch should be held low always.

//-------------//
//when rdaddr==25 check if in the next 4 cycles rs1addr or rs2addr == 25 first condition
property p1;
   int v;
			//rdaddr ==0 to 31
   @(posedge CLK) ((decoder_func_32[63:59] inside {[0:31]}, v =decoder_func_32[63:59],$display($time,"\t%d v value",v) )) |=> ##[0:3](
(v inside {decoder_func_32[73:69],decoder_func_32[68:64]},$display($time,"\t%drs2 ,%d rs1 %d v",decoder_func_32[73:69],decoder_func_32[68:64],v)) && (decoder_func_32[63:59] != v));

// @(posedge CLK) first_match((decoder_func_32[63:59] inside {[1:31]}, v =decoder_func_32[63:59],$display($time,"\t%d v value",v) )) |=> ##[0:3](
//(v inside {decoder_func_32[73:69],decoder_func_32[68:64]},$display($time,"\t%drs2 ,%d rs1 %d v",decoder_func_32[73:69],decoder_func_32[68:64],v)))[*0:3];

endproperty

//In these 4 cycles EN_update_eEpoch and EN_update_wEpoch should be held low always. last condition
property p2;
@(posedge CLK) ((decoder_func_32[63:59]inside{[0:31]}) |=> (!EN_update_eEpoch && !EN_update_wEpoch)[*4]);
endproperty

///when rdaddr==25 --> rdaddr != 25
property p3;
int vv;
@(posedge CLK) first_match((decoder_func_32[63:59] inside {[0:31]}, vv =decoder_func_32[63:59]))|=>  ((decoder_func_32[63:59] != vv))[*4];

// @(posedge CLK) (decoder_func_32[63:59]||decoder_func_32[63:59]==5'b0) |-> ##[1:4] (!$stable(decoder_func_32[63:59])); 
endproperty


//calling assert property p
always @(posedge CLK)begin
  a_1: assert property(p1);
c_1:cover property(p1);
 begin
	if((decoder_func_32[73:69]==decoder_func_32[63:59]) || (decoder_func_32[68:64]==decoder_func_32[63:59]))
	$display($time,"pass rd %d,rs1 %d,rs2 %d,",decoder_func_32[63:59],decoder_func_32[73:69],decoder_func_32[68:64]);
end
else
//if((decoder_func_32[73:69]!=decoder_func_32[63:59]) && (decoder_func_32[68:64]!=decoder_func_32[63:59]))
	$display($time,"fail rd %d,rs1 %d,rs2 %d,",decoder_func_32[63:59],decoder_func_32[73:69],decoder_func_32[68:64]);
end

//asserting property p1
always @(posedge CLK)begin
  a_2: assert property(p2);
c_2:cover property(p2);
end

//asserting property p2
always @(posedge CLK)begin
  a_3: assert property(p3);
c3:cover property(p3);
end
*/
endinterface

