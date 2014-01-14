'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 300000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  TUD277299\localadmin
'<Header End>
' primary purpose of this program: 
' get count rates of internal ADwin counters 1 - 4 as 
' floating average over last 1..1000ms
 
' input:
' - averaging steps : PAR_24 = over how many periods to do the floating avg
' - integration time (ms) : PAR_23
' - single run (bool) : PAR_25 = if true, only measure one shot (1 avg interval) then end
' 
' output:
' - PAR_41--44 : floating average of countrate (Hz)
' - DATA_45[1--4] : counts of the most recent count interval (int time)

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

DIM int_time AS LONG        ' in ms
DIM avg_steps AS LONG       ' multiples of int_time
DIM counter_index AS LONG   ' 1--4
DIM single_run AS INTEGER   ' if 1, measure only once, then stop
DIM i AS LONG               ' tmp index
DIM DATA_41[10000] AS LONG  ' for floating average of counter 1
DIM DATA_42[10000] AS LONG  ' .. counter 2
DIM DATA_43[10000] AS LONG  ' .. counter 3
DIM DATA_44[10000] AS LONG  ' .. counter 4
DIM DATA_45[4] AS LONG     ' for the counts of the last int_time period


INIT:
  int_time = PAR_23                  ' [ms]
  avg_steps = PAR_24                 ' averaging periods
  single_run = PAR_25
  
  if (single_run > 0) then
    avg_steps = 1
  endif
    
  for counter_index = 1 to avg_steps
    DATA_41[counter_index] = 0
    DATA_42[counter_index] = 0
    DATA_43[counter_index] = 0
    DATA_44[counter_index] = 0
  next counter_index

  PROCESSDELAY = 300000*int_time  '[ms]      
    
  ' init counter
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_MODE(CTR_MODULE, 1,000010000b)
  P2_CNT_MODE(CTR_MODULE, 2,000010000b)
  P2_CNT_MODE(CTR_MODULE, 3,000010000b)
  P2_CNT_MODE(CTR_MODULE, 4,000010000b)
  'CNT_SE_DIFF(0000b)
  P2_CNT_CLEAR(CTR_MODULE, 1111b)
  P2_CNT_ENABLE(CTR_MODULE, 1111b)
  
EVENT:
  
  'get counts
  P2_CNT_LATCH(CTR_MODULE, 1111b)
  DATA_41[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 1)
  DATA_42[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 2)
  DATA_43[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 3)
  DATA_44[counter_index] = P2_CNT_READ_LATCH(CTR_MODULE, 4)
  DATA_45[1] = DATA_41[counter_index]
  DATA_45[2] = DATA_42[counter_index]
  DATA_45[3] = DATA_43[counter_index]
  DATA_45[4] = DATA_44[counter_index]
  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,1111b)
  P2_CNT_ENABLE(CTR_MODULE,1111b)
  
  ' floating average
  PAR_41 = 0
  PAR_42 = 0
  PAR_43 = 0
  PAR_44 = 0
  for i = 1 to avg_steps
    PAR_41 = PAR_41 + DATA_41[i]*1000/(avg_steps*int_time)
    PAR_42 = PAR_42 + DATA_42[i]*1000/(avg_steps*int_time)
    PAR_43 = PAR_43 + DATA_43[i]*1000/(avg_steps*int_time)
    PAR_44 = PAR_44 + DATA_44[i]*1000/(avg_steps*int_time)
  next i
  
  if (single_run > 0) then
    end
  endif
    
  counter_index = counter_index - 1
  if (counter_index = 0) then
    counter_index = avg_steps
  endif
