interface chromite_intf(input bit CLK,RST_N);
logic [74:0]decoder_func_32;
logic EN_update_eEpoch;
logic EN_update_wEpoch;


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
endgroup
decoder_cg  cg=new();
initial
 begin
cg.sample();
end




		//--------assertions for chromite core---------//
/*sequence s1;
@(posedge CLK) ((decoder_func_32[63:59]==5'b1)  ##[1:4] ((decoder_func_32[73:69] || decoder_func_32[68:64] )&&!decoder_func_32[63:59]));
endsequence 

sequence s2;
@(posedge CLK) ((decoder_func_32[63:59]==5'b1)  ##1 (!EN_update_eEpoch && !EN_update_wEpoch)[*4]);
endsequence

property p;
    s1 and s2; 
endproperty

property p;
   @(posedge CLK) (decoder_func_32[63:59]||decoder_func_32[63:59]==5'b0) |=> ##[0:3]( ((decoder_func_32[73:69]==decoder_func_32[63:59]) ||(decoder_func_32[68:64]==decoder_func_32[63:59])) &&(!$stable(decoder_func_32[63:59])) );
endproperty

//In these 4 cycles EN_update_eEpoch and EN_update_wEpoch should be held low always. last condition
property p1;
@(posedge CLK) ((decoder_func_32[63:59]) |-> ##1 (!EN_update_eEpoch && !EN_update_wEpoch)[*4]);
endproperty

///when rdaddr==25 --> rdaddr != 2
property p2;
 @(posedge CLK) (decoder_func_32[63:59]||decoder_func_32[63:59]==5'b0) |-> ##[1:4] (!$stable(decoder_func_32[63:59])); 
endproperty



always @(posedge CLK)begin
  a_1: assert property(p)
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
  a_2: assert property(p1);
end

//asserting property p2
always @(posedge CLK)begin
  a_3: assert property(p2);
end

*/


endinterface
