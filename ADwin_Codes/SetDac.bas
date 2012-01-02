'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
'DIM ret_val AS INTEGER
#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc
DIM value, time AS LONG

' The current position
DIM DATA_1[3] AS FLOAT
EVENT:
  value=FPar_20*3276.8+32768  'Convert voltage to bit value
  time=READ_TIMER()
  P2_DAC(DAC_Module,Par_20, value)           'PAR_20 = DAC number
  DATA_1[Par_20]=FPar_20
  Par_21=READ_TIMER()-time
  END
