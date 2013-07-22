'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 1500000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277246  TUD277246\localadmin
'<Header End>
' scan the gate voltage in small steps to the desired value

#INCLUDE ADwinGoldII.inc

#define step_size 0.001 ' per process cycle

dim current_voltage as float
dim target_voltage as float
dim diff_voltage as float
dim gate_dac as long

init:
  current_voltage = fpar_50
  gate_dac = par_50
  
event:
  target_voltage = fpar_51
  diff_voltage = (target_voltage - current_voltage) 
  if (diff_voltage > step_size) then
    diff_voltage = step_size
  else
    if (diff_voltage < (-step_size)) then
      diff_voltage = -step_size
    endif
  endif
    
  current_voltage = current_voltage + diff_voltage
  dac(gate_dac, 3277 * current_voltage + 32768)
  fpar_50 = current_voltage
  
