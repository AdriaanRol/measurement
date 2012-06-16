'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 7
' Initial_Processdelay           = 3000000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc
DIM gate_channel AS Long           ' DAC channel for gate modulation
DIM gate_voltage AS Float          ' voltage of the gate modulation
DIM modulation_period AS Long      ' period of 1/2 modulation in units of ms
DIM modulation_on as long          ' bool, if >0 mod on.

DIM modulator AS Float

INIT:
  modulator=1.0
EVENT:
  PROCESSDELAY = modulation_period * 300000
  modulation_on=Par_14
  
  gate_channel = Par_12
  gate_voltage = FPar_12
  modulation_period = Par_13
  
  P2_DAC(DAC_MODULE,gate_channel,gate_voltage*modulator*3277+32768)
  if (modulation_on > 0) then
    modulator=-(modulator)
  else
    modulator = 1.0
  endif
 
