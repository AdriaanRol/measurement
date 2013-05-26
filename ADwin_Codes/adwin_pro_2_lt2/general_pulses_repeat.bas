'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
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


#DEFINE max_elements 10 'max cases: this is the maximum number of different pulse/counting combinations.
#DEFINE max_dacs 3
#DEFINE max_histogram_length 100
#DEFINE max_repetitions 100000

DIM DATA_20[25] AS LONG               ' integer parameters, sequence definition, dac channels etc

' dac voltages for each element
DIM DATA_21[max_elements] AS FLOAT AT EM_LOCAL            ' float parameters dac1
DIM DATA_22[max_elements] AS FLOAT AT EM_LOCAL            ' float parameters dac2
DIM DATA_23[max_elements] AS FLOAT AT EM_LOCAL            ' float parameters dac3

' counter element (on/off) for each element
DIM DATA_24[max_elements] AS LONG AT EM_LOCAL             ' integer parameter counter

'duractions of each element
DIM DATA_25[max_elements] AS LONG AT EM_LOCAL 

'result data
DIM DATA_30[1000000] AS LONG    ' counts acquired duting each element for each repetition 
'SIZE IS max_repetitions*max_elements

'result histogram
DIM DATA_31[10000000] AS LONG
'SIZE IS max_repetitions*max_histogram_length
'first count during timee element
DIM DATA_32[max_repetitions] AS LONG
'SIZE is max_elements


DIM dac1_channel AS LONG
DIM dac2_channel AS LONG
DIM dac3_channel AS LONG
DIM sweep_channel AS LONG

DIM counter_channel AS LONG
DIM counter_pattern AS LONG

DIM timed_element AS LONG
DIM max_element AS LONG
DIM max_repetition AS LONG
DIM do_sweep_duration AS LONG

DIM element AS LONG
DIM timer AS LONG
DIM cur_timer_max AS LONG
DIM repetition_counter AS LONG
DIM i AS LONG
DIM modulator AS LONG

DIM counts AS lONG
DIM counts_total AS lONG

DIM cycle_duration AS LONG
DIM wait_after_pulse AS LONG
DIM wait_after_pulse_duration AS LONG

INIT:
  
  counter_channel              = DATA_20[1]
  dac1_channel                 = DATA_20[2]
  dac2_channel                 = DATA_20[3]
  dac3_channel                 = DATA_20[4]
  max_element                  = DATA_20[5]
  cycle_duration               = DATA_20[6]
  wait_after_pulse_duration    = DATA_20[7]
  max_repetition               = DATA_20[8]
  timed_element                = DATA_20[9]
  
  FOR i = 1 TO max_repetitions*max_elements
    DATA_30[i] = 0
  NEXT i
  
  FOR i = 1 TO max_histogram_length*max_repetitions
    DATA_31[i] = 0
  NEXT i
   
  FOR i = 1 TO max_repetitions
    DATA_32[i] = 0
  NEXT i

  element = 1
  timer = 0
  repetition_counter=1
  cur_timer_max=10
  wait_after_pulse=0
  processdelay = cycle_duration
 
  counter_pattern     = 2 ^ (counter_channel-1)
  P2_CNT_ENABLE(CTR_MODULE,0000b) 'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,00001000b) 'configure counter
  
  'turn off all dacs
  P2_DAC(DAC_MODULE,dac1_channel, 32768) 
  P2_DAC(DAC_MODULE,dac2_channel, 32768) 
  P2_DAC(DAC_MODULE,dac3_channel, 32768) 
  
  'pars
  Par_72 = 0 'repetition_counter
  Par_70 = 0 'total counts
  
  
EVENT:
  
  'Par_10=element
  'Par_11=timer
  'Par_12=sweep_index
  'Par_13=wait_after_pulse
  'Par_14=cur_timer_max
  
  IF (wait_after_pulse > 0) THEN
    IF (wait_after_pulse = wait_after_pulse_duration) THEN
      P2_DAC(DAC_MODULE,dac1_channel, 32768) 
      P2_DAC(DAC_MODULE,dac2_channel, 32768) 
      P2_DAC(DAC_MODULE,dac3_channel, 32768)
    ENDIF
    wait_after_pulse = wait_after_pulse - 1
  ELSE
    IF (timer=0) THEN
      P2_DAC(DAC_MODULE,dac1_channel, 3277*DATA_21[element]+32768) 
      P2_DAC(DAC_MODULE,dac2_channel, 3277*DATA_22[element]+32768) 
      P2_DAC(DAC_MODULE,dac3_channel, 3277*DATA_23[element]+32768)
      
      IF(DATA_24[element] > 0) THEN      
        P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
        P2_CNT_ENABLE(CTR_MODULE,counter_pattern)	  'turn on counter
        counts=0
        counts_total=0
      ENDIF
      
      cur_timer_max=DATA_25[element]
             
    ELSE
      IF (timer = cur_timer_max) THEN
        
        IF(DATA_24[element] > 0) THEN   
          counts_total = P2_CNT_READ(CTR_MODULE,counter_channel)
          Par_70=Par_70+counts_total
          i=(max_element-1)*repetition_counter+element  
          DATA_30[i] = DATA_30[i] + counts_total
          P2_CNT_ENABLE(CTR_MODULE,0)
        ENDIF
              
        IF (element= max_element) THEN
          element = 1
          INC(repetition_counter)
          INC(Par_72)
          IF(repetition_counter>max_repetition) THEN
            END
          ENDIF
        ELSE
          INC(element)
        ENDIF
       
        timer = -1
        wait_after_pulse=wait_after_pulse_duration
      
      ELSE
        IF (element=timed_element) THEN
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          i= (MIN_LONG(cur_timer_max,max_histogram_length))*repetition_counter+MIN_LONG(timer,max_histogram_length)
          DATA_31[i]=DATA_31[i]+counts-counts_total
          IF ((counts_total=0) AND (counts>0)) THEN
            DATA_32[repetition_counter]=timer
          ENDIF
          
          counts_total = counts       
        ENDIF
        
      ENDIF     
     
    ENDIF
    timer = timer + 1
  ENDIF
  
        
