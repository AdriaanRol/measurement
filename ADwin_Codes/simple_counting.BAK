'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 300000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
'primary purpose of this program: get count rates of internal ADwin counters 1 - 4 as floating average over last 1..1000ms
 
'set global delay to process time
'once per process time: read counter 1 - 4  (PAR_24: int_time [ms])
'store RATE (cps) in PAR_41 - PAR_44        (averaged over last (int_time/process_time) counts)
'clear counters and restart them

'Commented out (only for flow criostat): 
'second task: flip mirrors for alternative excitation path (other dichroic)
'if PAR_34 is set to 1, then set DO 1, DO 2, DO 3 'high', set PAR_34 back to 0
'after 100ms set them back to 'low'


#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc
DIM int_time AS LONG
'DIM flip_time AS LONG
DIM process_time AS LONG
DIM counter_index AS LONG
'DIM flip_index AS LONG
DIM i AS LONG
DIM DATA_41[1000] AS FLOAT
DIM DATA_42[1000] AS FLOAT
DIM DATA_43[1000] AS FLOAT
DIM DATA_44[1000] AS FLOAT

INIT:
  process_time = 1                    '[ms]
  int_time = PAR_24                   '[ms]
  'flip_time = 100                     '[process_time]

  for counter_index = 1 to int_time / process_time
    DATA_41[counter_index] = 0
    DATA_42[counter_index] = 0
    DATA_43[counter_index] = 0
    DATA_44[counter_index] = 0
  next counter_index

  PROCESSDELAY = 300000*process_time  '[ms]
  '  CONF_DIO(13)                        'configure DIO 08:15 as input, all other ports as output
      
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_MODE(CTR_MODULE, 1,00001000b)
  P2_CNT_MODE(CTR_MODULE, 2,00001000b)
  P2_CNT_MODE(CTR_MODULE, 3,00001000b)
  P2_CNT_MODE(CTR_MODULE, 4,00001000b)
  'CNT_SE_DIFF(0000b)
  P2_CNT_CLEAR(CTR_MODULE, 1111b)
  P2_CNT_ENABLE(CTR_MODULE, 1111b)
  
EVENT:
  
  'Counting and floating average
  P2_CNT_LATCH(CTR_MODULE, 1111b)
  DATA_41[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 1)*1000/int_time
  DATA_42[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 2)*1000/int_time
  DATA_43[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 3)*1000/int_time
  DATA_44[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 4)*1000/int_time
  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,1111b)
  P2_CNT_ENABLE(CTR_MODULE,1111b)
  
  PAR_41 = 0
  PAR_42 = 0
  PAR_43 = 0
  PAR_44 = 0
  
  for i = 1 to int_time/process_time
    PAR_41 = PAR_41 + DATA_41[i]
    PAR_42 = PAR_42 + DATA_42[i]
    PAR_43 = PAR_43 + DATA_43[i]
    PAR_44 = PAR_44 + DATA_44[i]
  next i
  
  counter_index = counter_index - 1
  if (counter_index = 0) then
    counter_index = int_time/process_time
  endif
  
  'flip mirrors
  'if (flip_index > 0) then
  'flip_index = flip_index - 1
  'if (flip_index = 0) then
  'DIGOUT(1,0)
  'DIGOUT(2,0)
  'DIGOUT(3,0)
  'endif
  'endif
  
  'if (PAR_34 = 1) then
  'DIGOUT(1,1)
  'DIGOUT(2,1)
  'DIGOUT(3,1)
  'flip_index = flip_time / process_time
  'PAR_34 = 0
  'endif
  
  
  
  
