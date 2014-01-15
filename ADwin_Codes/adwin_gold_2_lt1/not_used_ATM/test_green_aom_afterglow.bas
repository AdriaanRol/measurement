'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277246  TUD277246\localadmin
'<Header End>
#INCLUDE ADwinGoldII.inc
#Include Math.inc

DIM DATA_21[21] AS FLOAT AT EM_LOCAL
DIM DATA_22[40001] AS LONG AT EM_LOCAL 

DIM first_real_timer,real_timer,timer, mode,i,ii, last_counts, counts, counter_channel, counter_pattern AS LONG


INIT:
  
  FOR i = 1 TO 40001
    DATA_22[i] = 0
  NEXT i

  counter_channel=1
  counter_pattern     = 2 ^ (counter_channel-1)
  
  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter
  CNT_CLEAR(counter_pattern)    'clear counter
  CNT_ENABLE(counter_pattern)    'turn on counte
  
  timer = 0
  
  mode=0
  counts=0
  Par_22=0
 
  
EVENT:
  
  SELECTCASE mode
      
    CASE 0
      IF (timer = 0) THEN
        counts=0
        CNT_CLEAR(counter_pattern)    'clear counter
        CNT_ENABLE(counter_pattern)    'turn on counter
        i=Mod(Par_22,20)+1
        DAC(4, 3277*DATA_21[i]+32768)
      ENDIF
      IF (timer = 980) THEN
        DAC(4, 3277*(-0.3)+32768)
      ENDIF
      
      IF (timer = 1000) THEN
        counts = CNT_READ(counter_channel)
        CNT_ENABLE(0)
        DAC(4, 3277*(-0.0)+32768)
        'IF (counts < 100) THEN
        mode = 1
        timer=-1

        'ELSE
        '  timer = -1
        'ENDIF
      ENDIF
      
      
    CASE 1
      IF (timer = 0) THEN
        counts=0
        last_counts=0
        CNT_CLEAR(counter_pattern)    'clear counter
        CNT_ENABLE(counter_pattern)    'turn on counter
        Inc(par_22)


      ELSE
        
        if (timer = 2000) THEN 
          mode = 0
          timer=-1
        ELSE
          counts = CNT_READ(counter_channel)
          ii = (i-1)*2000+timer
          DATA_22[ii]=DATA_22[ii]+counts-last_counts
          last_counts=counts         
        ENDIF
      ENDIF
      
    CASE 2
      IF (timer = 0) THEN
        counts=0
        CNT_CLEAR(counter_pattern)    'clear counter
        CNT_ENABLE(counter_pattern)    'turn on counter
        
      ENDIF
      IF (timer = 1000) THEN
        counts = CNT_READ(counter_channel)
        CNT_ENABLE(0)
        IF (counts > 100) THEN
          mode = 0
          timer=-1
        ELSE
          timer = -1
        ENDIF
      ENDIF
      
  ENDSELECT
    
  Inc(timer)
     
