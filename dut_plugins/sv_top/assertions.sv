
//when rdaddr==1 check if in the next 4 cycles rs1addr or rs2addr == 1 and rdaddr != 1. In these 4 cycles EN_update_eEpoch and EN_update_wEpoch should be held low always.

sequence s1;
@(posedge clk) decoder_func_32[55:51]==5'b1 |->##[1:4] ((decoder_func_32[65:61] || decoder_func_32[60:56] )&&!decoder_func_32[55:51])
endsequence 

sequence s2;
@(posedge clk) decoder_func_32[55:51]==5'b1 |-> ##1 (!EN_update_eEpoch && !EN_update_wEpoch)[*4]
endsequence

property p;
    s1 AND s2; 
endproperty

//calling assert property
  a_1: assert property(p);
else
   $error("assertion got failed");
  

    
