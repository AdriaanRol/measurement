'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 6
' Initial_Processdelay           = 30000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

EVENT:
  FPAR_63 = (P2_ADC(ADC_MODULE,PAR_63)-32768.0)/65536.0*20.0
  END
