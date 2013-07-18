'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc
#Include Math.inc
#DEFINE max_repump_duration 600
DIM DATA_19[max_repump_duration] AS FLOAT 
DIM DATA_27[max_repump_duration] AS LONG 
DIM i as long
INIT:
  
  FOR i = 1 TO max_repump_duration
    DATA_27[i] = 0
  NEXT i
