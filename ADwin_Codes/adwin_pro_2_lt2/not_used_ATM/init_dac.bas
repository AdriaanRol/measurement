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
#INCLUDE .\configuration.inc

DIM U AS FLOAT
DIM DAC_no as INTEGER

EVENT:
  U = 4.0
  DAC_no = 7
  P2_DAC(DAC_MODULE,DAC_no,U*3277+32768)
  END
