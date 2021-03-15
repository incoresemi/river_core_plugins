interface chromite_intf(input bit CLK,RST_N);
logic [65:0]decoder_func_32;
logic EN_update_eEpoch;
logic EN_update_wEpoch;

///--------coverpoints for functional coverage -------////
covergroup decoder_cg @(posedge CLK);
option.per_instance=1;
   rs1addr: coverpoint decoder_func_32[65:61] {
                   bins rs1_addr_bin[32] = { [0:31] } iff (decoder_func_32[50] == 1'b0);
   } 
    
rs2addr: coverpoint decoder_func_32[60:56] {
                   bins rs2_addr_bin[32] = { [0:31] } iff (decoder_func_32[49:48] == 2'b0);
   } 
rdaddr:  coverpoint decoder_func_32[55:51] {
			bins raddr_bin[32] ={[0:31]};
}
endgroup
decoder_cg  cg=new();
initial
 begin
cg.sample();
end


		//--------assertions for chromite core---------//
sequence s1;
@(posedge CLK) ((decoder_func_32[55:51]==5'b1)  ##[1:4] ((decoder_func_32[65:61] || decoder_func_32[60:56] )&&!decoder_func_32[55:51]));
endsequence 

sequence s2;
@(posedge CLK) ((decoder_func_32[55:51]==5'b1)  ##1 (!EN_update_eEpoch && !EN_update_wEpoch)[*4]);
endsequence

property p;
    s1 and s2; 
endproperty

//calling assert propert
initial begin
  a_1: assert property(p);  
end

endinterface
