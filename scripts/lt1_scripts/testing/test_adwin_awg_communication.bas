'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.5
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10238  TUD10238\localadmin
'<Header End>
' a simple program to check whether the communication with the awg works
' sends a trigger to the awg, and waits for the awg to to signal the end of its 
' sequence by a TTL pulse. 
' then repeats the sequence.

#INCLUDE ADwinGoldII.inc

dim timer as long
dim start_sequence as long
dim trigger_DO as long
dim awg_signal_DI as long
dim jump_DO as long
dim awg_signal_received as long

init:
  
  timer = 0
  start_sequence = 1
  trigger_DO = 0
  awg_signal_DI = 9
  jump_DO = 6
  awg_signal_received = 0
  
  par_1 = 0 ' number of sequences started
  par_2 = 0 ' number of triggers from awg received
  par_3 = 0 ' number of times we ran the program
  
  CONF_DIO(13) 'configure DIO 08:15 as input, all other ports as output
  DIGOUT(trigger_DO,0)

event:
  
  par_3 = timer
  
  ' if we have detected an awg signal, enable triggering start again
  if(awg_signal_received > 0) then
    start_sequence = 1
    awg_signal_received = 0
  endif
    
  ' check if we got a falling edge (argument '0') on the awg DI
  if((digin_edge(0) AND 2^awg_signal_DI) > 0) then
    par_2 = par_2 + 1
    awg_signal_received = 1
  endif
    
  if(start_sequence>0) then
    par_1 = par_1 + 1
  
    ' send sequence trigger to AWG and disable starting next sequence
    DIGOUT(trigger_DO,1)
    CPU_SLEEP(9)
    DIGOUT(trigger_DO,0)
    start_sequence = 0  
  endif
   
  timer = timer + 1
  
  if(par_2 = 1000) then
    end
  endif
  
  
