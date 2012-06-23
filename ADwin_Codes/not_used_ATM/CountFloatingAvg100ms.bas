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
#INCLUDE configuration.inc
DIM start, stop, time AS LONG
DIM index, i AS LONG
DIM DATA_41[100] AS FLOAT
DIM DATA_42[100] AS FLOAT
DIM DATA_43[100] AS FLOAT
DIM DATA_44[100] AS FLOAT

INIT:
  PROCESSDELAY = 300000 
  P2_CNT_ENABLE(CTR_Module,0000b)               'turn off all counters
  P2_SE_DIFF(CTR_Module,0000b)              'configure counters as single ended
  P2_CNT_MODE(CTR_Module,1, 00001000b)           'configure counter one: 
  P2_CNT_MODE(CTR_Module,2, 00001000b)
  P2_CNT_MODE(CTR_Module,3, 00001000b)
  P2_CNT_MODE(CTR_Module,4, 00001000b)
  '                                 - mode: clock/direction, 
  '                                 - count up for input B/DIR = low
  '                                 - disable CLR/LATCH input
  P2_CNT_CLEAR(CTR_Module,1111b)                'clear counter 1
  P2_CNT_ENABLE(CTR_Module,1111b)               'enable counter 1
  start = READ_TIMER()
  for index = 1 to 100
    DATA_41[index] = 0
    DATA_42[index] = 0
    DATA_43[index] = 0
    DATA_44[index] = 0
  next index
  index = 0  

EVENT:
  P2_CNT_LATCH(CTR_Module,1111b)
  stop = READ_TIMER()
  time = stop - start
  index = index + 1
  if (index = 101) then 
    index = 1
  endif
  DATA_41[index] = P2_CNT_READ_LATCH(CTR_Module,1) / time * 3000000.0
  DATA_42[index] = P2_CNT_READ_LATCH(CTR_Module,2) / time * 3000000.0
  DATA_43[index] = P2_CNT_READ_LATCH(CTR_Module,3) / time * 3000000.0
  DATA_44[index] = P2_CNT_READ_LATCH(CTR_Module,4) / time * 3000000.0
  P2_CNT_ENABLE(CTR_Module,0000b)               'disable all counters
  P2_CNT_CLEAR(CTR_Module,1111b)                'clear counter 1
  PAR_41 = 0
  PAR_42 = 0
  PAR_43 = 0
  PAR_44 = 0
  for i = 1 to 100
    PAR_41 = PAR_41 + DATA_41[i]
    PAR_42 = PAR_42 + DATA_42[i]
    PAR_43 = PAR_43 + DATA_43[i]
    PAR_44 = PAR_44 + DATA_44[i]
  next i
  P2_CNT_ENABLE(CTR_Module,1111b)               'enable counter 1
  start = READ_TIMER()
