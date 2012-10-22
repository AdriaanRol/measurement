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
'primary purpose of this program: get count rates of internal ADwin counters 1 - 4 as floating average over last 1..1000ms
 
'set global delay to process time
'once per process time: read counter 1 - 4  (PAR_24: int_time [ms])
'store RATE (cps) in PAR_41 - PAR_44        (averaged over last (int_time/process_time) counts)
'clear counters and restart them

'second task: flip mirrors for alternative excitation path (other dichroic)
'if PAR_34 is set to 1, then set DO 1, DO 2, DO 3 'high', set PAR_34 back to 0
'after 100ms set them back to 'low'


#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc
DIM int_time AS LONG
DIM channels  AS LONG
DIM initialize_ctr AS LONG
'DIM flip_time AS LONG
DIM process_time AS LONG
DIM counter_index AS LONG
'DIM flip_index AS LONG
DIM i AS LONG
DIM DATA_29[4] AS LONG
DIM DATA_28[4] AS LONG

INIT:
  process_time = 1                    '[ms]
  int_time = PAR_24                   '[ms]
  channels = PAR_11                   'LSB channel 1 usw.
  initialize_ctr = PAR_12
  counter_index = 0
  

  PROCESSDELAY = 300000*process_time  '[ms]
  '  CONF_DIO(13)                        'configure DIO 08:15 as input, all other ports as output
  
  IF (initialize_ctr = 1) THEN
    P2_CNT_ENABLE(CTR_MODULE, 15-channels)
    FOR i = 1 to 4 
      IF ((2^(i-1) AND channels) > 0) THEN
        P2_CNT_MODE(CTR_MODULE, i,00001000b)
      ENDIF
    NEXT i
    'CNT_SE_DIFF(0000b)
    P2_CNT_CLEAR(CTR_MODULE, channels)
    P2_CNT_ENABLE(CTR_MODULE, 1111b)
  ENDIF
  P2_CNT_LATCH(CTR_MODULE, channels)
  FOR i = 1 to 4 
    IF ((2^(i-1) AND channels) > 0) THEN
      DATA_29[i] = P2_CNT_READ_LATCH(CTR_MODULE, i)
    ENDIF
  NEXT i
  
EVENT:
  'Counting and floating average
  P2_CNT_LATCH(CTR_MODULE, channels)
  FOR i = 1 to 4 
    IF ((2^(i-1) AND channels) > 0) THEN
      DATA_28[i] = P2_CNT_READ_LATCH(CTR_MODULE, i) - DATA_29[i]
    ENDIF
  NEXT i
  
  counter_index = counter_index + process_time
  
  IF (counter_index = int_time) THEN
    END
  ENDIF
