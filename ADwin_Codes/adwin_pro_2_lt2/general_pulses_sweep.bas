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
#INCLUDE .\configuration.inc


#DEFINE max_elements 10 'max cases: this is the maximum number of different pulse/counting combinations.
#DEFINE max_dacs 3
#DEFINE max_sweeps 100
#DEFINE max_counts 100
#DEFINE max_repetitions 100

DIM DATA_20[25] AS LONG               ' integer parameters, sequence definition, dac channels etc

' dac voltages for each element
DIM DATA_21[max_elements] AS FLOAT AT EM_LOCAL            ' float parameters dac1
DIM DATA_22[max_elements] AS FLOAT AT EM_LOCAL            ' float parameters dac2
DIM DATA_23[max_elements] AS FLOAT AT EM_LOCAL            ' float parameters dac3

' counter element (on/off) for each element
DIM DATA_24[max_elements] AS LONG AT EM_LOCAL             ' integer parameter counter

'duractions of each element
DIM DATA_25[max_elements] AS LONG AT EM_LOCAL 

'sweep dac voltage
DIM DATA_26[max_sweeps] AS FLOAT          

'sweep duration
DIM DATA_27[max_sweeps] AS FLOAT

'result data
DIM DATA_30[1000] AS LONG    ' counts acquired duting each element for each sweep_var 
'SIZE IS max_sweeps*max_elements

'result histogram
DIM DATA_31[10001] AS LONG    ' counts acquired duting each element for each sweep_var 
'SIZE IS max_sweeps*max_counts+1

'counts during exp
DIM DATA_32[max_elements] AS LONG AT EM_LOCAL
'SIZE is max_elements


DIM dac1_channel AS LONG
DIM dac2_channel AS LONG
DIM dac3_channel AS LONG
DIM sweep_channel AS LONG

DIM counter_channel AS LONG
DIM counter_pattern AS LONG

DIM sweep_element AS LONG
DIM max_element AS LONG
DIM max_sweep AS LONG
DIM do_sweep_duration AS LONG

DIM element AS LONG
DIM timer AS LONG
DIM cur_timer_max AS LONG
DIM sweep_index AS LONG
DIM i AS LONG
DIM modulator AS LONG

DIM counts AS lONG

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
  max_sweep                    = DATA_20[8]
  sweep_channel                = DATA_20[9]
  do_sweep_duration            = DATA_20[10]
  sweep_element                = DATA_20[11]

  
  FOR i = 1 TO max_sweeps*max_elements
    DATA_30[i] = 0
  NEXT i
  
  FOR i = 1 TO max_sweeps*max_counts+1
    DATA_31[i] = 0
  NEXT i
  
  FOR i = 1 TO max_elements
    DATA_32[i] = 0
  NEXT i

  element = 1
  timer = 0
  sweep_index=1
  modulator = 1
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
  Par_73 = 0 'repetition_counter
  Par_15 = 0 'total counts
  
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
      ENDIF
      
      cur_timer_max=DATA_25[element]
      
      IF (element = sweep_element) THEN
        IF (do_sweep_duration=0)  THEN
          P2_DAC(DAC_MODULE,sweep_channel, 3277*DATA_26[sweep_index]+32768)
        ELSE
          cur_timer_max=DATA_27[sweep_index]
        ENDIF
      ENDIF
        
    ELSE
      IF (timer = cur_timer_max) THEN
        
        IF(DATA_24[element] > 0) THEN   
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          Par_15=Par_15+counts
          i=(element-1)*max_sweep+sweep_index   
          DATA_30[i] = DATA_30[i] + counts
          i=(sweep_index-1)*max_counts+MIN_LONG(counts,max_counts-1)+1        
          DATA_31[i]=DATA_31[i]+1
          DATA_32[element] = counts
          P2_CNT_ENABLE(CTR_MODULE,0)
        ENDIF

        IF (element = sweep_element) THEN
          'DATA_33[sweep_index]=DATA_33[sweep_index]+1
          IF (do_sweep_duration=0)  THEN
            P2_DAC(DAC_MODULE,sweep_channel, 32768)
          ENDIF
          
          'turn around at the end of the sweep_index ranges
          sweep_index=sweep_index+modulator
          IF (sweep_index = 1) THEN
            IF (modulator = 0) THEN
              modulator=1
            ELSE
              modulator=0
            ENDIF
          ENDIF
          IF (sweep_index = max_sweep) THEN
            IF (modulator = 0) THEN
              modulator=-1
            ELSE
              modulator=0
            ENDIF
          ENDIF   
                       
        ENDIF
                
        IF (element= max_element) THEN
          element = 1
          INC(Par_73)
        ELSE
          INC(element)
        ENDIF
       
        timer = -1
        wait_after_pulse=wait_after_pulse_duration
      ENDIF
          
     
    ENDIF
    timer = timer + 1
  ENDIF
  
        
