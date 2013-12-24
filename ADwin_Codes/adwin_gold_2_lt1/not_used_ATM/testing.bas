'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
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
#INCLUDE ADwinGoldII.inc

dim a as long
dim b as long

INIT:
  a = 499999999
  b = 7
  
  fpar_2=min_long((a / 1000),499)+1
   
  
  
EVENT:
  
FINISH:
  
  
  
