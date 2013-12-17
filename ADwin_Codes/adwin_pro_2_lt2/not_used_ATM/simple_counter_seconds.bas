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
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
INIT:
  
  Par_40=0
  Par_41=0
  
  PROCESSDELAY = 300000*1000  '[s]
  ' init counter
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_MODE(CTR_MODULE, 1,00001000b)
  P2_CNT_MODE(CTR_MODULE, 2,00001000b)
  P2_CNT_MODE(CTR_MODULE, 3,00001000b)
  P2_CNT_MODE(CTR_MODULE, 4,00001000b)
  'CNT_SE_DIFF(0000b)
  P2_CNT_CLEAR(CTR_MODULE, 1111b)
  P2_CNT_ENABLE(CTR_MODULE, 1111b)
  
  
EVENT:
  
  Inc(Par_40)
  'get counts
  P2_CNT_LATCH(CTR_MODULE, 1111b)
  Par_41 = Par_41+ P2_CNT_READ_LATCH(CTR_MODULE, 1)
  
  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,1111b)
  P2_CNT_ENABLE(CTR_MODULE,1111b)
