'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#INCLUDE ADwinGoldII.inc
#INCLUDE configuration.inc
INIT:
  
  Par_40=0
  Par_41=0
  
  PROCESSDELAY = 300000*1000  '[s]
  ' init counter
  CNT_ENABLE(0000b)
  CNT_MODE(1,00001000b)
  CNT_MODE(2,00001000b)
  CNT_MODE(3,00001000b)
  CNT_MODE(4,00001000b)
  CNT_SE_DIFF(0000b)
  CNT_CLEAR(1111b)
  CNT_ENABLE(1111b)
  
  
EVENT:
  
  Inc(Par_40)
  'get counts
  CNT_LATCH(1111b)
  Par_41 = Par_41+ CNT_READ_LATCH(2)
  
  CNT_ENABLE(0000b)
  CNT_CLEAR(1111b)
  CNT_ENABLE(1111b)
