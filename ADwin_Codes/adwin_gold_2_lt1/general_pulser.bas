'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.5
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10238  TUD10238\localadmin
'<Header End>
#INCLUDE ADwinGoldII.inc 
'#INCLUDE ADwinPro_All.inc
'#INCLUDE configuration.inc


#DEFINE max_modes 10 'max cases: this is the maximum number of different pulse/counting combinations.
#DEFINE max_dacs 3
#DEFINE max_sweeps 100
#DEFINE max_counts 100

DIM DATA_20[25] AS LONG               ' integer parameters, sequence definition, dac channels etc

' dac voltages for each mode
DIM DATA_21[max_modes] AS FLOAT AT EM_LOCAL             ' float parameters dac1
DIM DATA_22[max_modes] AS FLOAT AT EM_LOCAL            ' float parameters dac2
DIM DATA_23[max_modes] AS FLOAT AT EM_LOCAL            ' float parameters dac3

' counter mode (on/off) for each mode
DIM DATA_24[max_modes] AS LONG AT EM_LOCAL             ' integer parameter counter

'duractions of each mode
DIM DATA_25[max_modes] AS LONG AT EM_LOCAL 

'sweep variable
DIM DATA_26[max_sweeps] AS FLOAT          

'result data
DIM DATA_30[1000] AS LONG    ' counts acquired duting each mode for each sweep_var 
'SIZE IS max_sweeps*max_modes

'result histogram
DIM DATA_31[10000] AS LONG    ' counts acquired duting each mode for each sweep_var 
'SIZE IS max_sweeps*max_counts

'counts during exp
DIM DATA_45[max_modes] AS LONG AT EM_LOCAL

DIM dac1_channel AS LONG
DIM dac2_channel AS LONG
DIM dac3_channel AS LONG
DIM sweep_channel AS LONG

DIM counter_channel AS LONG
DIM counter_pattern AS LONG

DIM sweep_mode AS LONG
DIM max_mode AS LONG
DIM max_sweep AS LONG

DIM mode AS LONG
DIM timer AS LONG
DIM sweep_index AS LONG
DIM i AS LONG

DIM counts AS lONG

DIM cycle_duration AS LONG
DIM wait_after_pulse AS LONG
DIM wait_after_pulse_duration AS LONG

INIT:
  
  counter_channel              = DATA_20[1]
  dac1_channel                 = DATA_20[2]
  dac2_channel                 = DATA_20[3]
  dac3_channel                 = DATA_20[4]
  max_mode                     = DATA_20[5]
  cycle_duration               = DATA_20[6]
  wait_after_pulse_duration    = DATA_20[7]
  max_sweep                    = DATA_20[8]
  sweep_channel                = DATA_20[9]

  
  FOR i = 1 TO max_sweeps*max_modes
    DATA_30[i] = 0
  NEXT i

  mode = 1
  timer = 0
  sweep_index=1
  processdelay = cycle_duration
 
  counter_pattern     = 2 ^ (counter_channel-1)
  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter
  
  'turn off all dacs
  DAC(dac1_channel, 32768) 
  DAC(dac2_channel, 32768) 
  DAC(dac3_channel, 32768) 
  
  'pars
  Par_73 = 0 'repetition_counter
  
EVENT:
  
  IF (wait_after_pulse > 0) THEN
    IF (wait_after_pulse = wait_after_pulse_duration) THEN
      DAC(dac1_channel, 32768) 
      DAC(dac2_channel, 32768) 
      DAC(dac3_channel, 32768)
    ENDIF
    wait_after_pulse = wait_after_pulse - 1
  ELSE
    IF (timer=0) THEN
      DAC(dac1_channel, 3277*DATA_21[mode]+32768) 
      DAC(dac2_channel, 3277*DATA_22[mode]+32768) 
      DAC(dac3_channel, 3277*DATA_23[mode]+32768)
      
      IF(DATA_24[mode] > 0) THEN      
        CNT_CLEAR(counter_pattern)    'clear counter
        CNT_ENABLE(counter_pattern)	  'turn on counter
      ENDIF
      IF (mode = sweep_mode) THEN
        DAC(sweep_channel, 3277*DATA_26[sweep_index]+32768)
      ENDIF
    ELSE
      IF (timer = DATA_25[mode]) THEN
        
        IF(DATA_24[mode] > 0) THEN   
          counts = CNT_READ(counter_channel)   
          DATA_30[mode*sweep_index] = DATA_30[mode*sweep_index] + counts
          IF (counts >= max_counts) THEN
            DATA_31[sweep_index*max_counts]=DATA_31[sweep_index*max_counts]+1
          ELSE
            DATA_31[sweep_index*counts]=DATA_31[sweep_index*counts]+1
          ENDIF
          DATA_45[mode] = counts
          CNT_ENABLE(0)
        ENDIF

        IF (mode = sweep_mode) THEN
          DAC(sweep_channel, 32768)
          IF(sweep_index = max_sweep) THEN
            sweep_index = 1 
          ELSE
            INC(sweep_index)
          ENDIF
        ENDIF
                
        IF (mode= max_mode) THEN
          mode = 1
          INC(Par_73)
        ELSE
          INC(mode)
        ENDIF
       
        timer = -1
        wait_after_pulse=wait_after_pulse_duration
      ENDIF
          
      timer = timer + 1
    ENDIF
  ENDIF
  
        
