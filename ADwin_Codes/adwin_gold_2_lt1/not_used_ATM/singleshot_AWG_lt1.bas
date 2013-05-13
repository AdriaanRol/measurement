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
' this program implements single-shot readout fully controlled by ADwin Gold II
'
' protocol:
' mode  0:  green pulse, 
'           photon counting just for statistics
' mode  1:  Ex/A pulse, photon counting  ->  CR check
'           fail: -> mode 0
' mode  2:  spin pumping with Ex or A pulse, photon counting for time dependence of SP
' mode  3:  start trigger to AWG (supposed to do a RO pulse)
'           wait until done, read counter, -> mode 1
'
' parameters:
' integer parameters: DATA_20[i]
' index i   description
'   1       counter_channel
'   2       green_laser_DAC_channel
'   3       Ex_laser_DAC_channel
'   4       A_laser_DAC_channel
'   5       AWG_start_DO_channel
'   6       AWG_done_DI_channel
'   7       number of sweep pts
'   8       green_repump_duration       (durations in process cycles)
'   9       CR_duration
'  10       SP_duration
'  11       wait_after_pulse_duration
'  12       CR_preselect
'  13       SSRO_repetitions
'  14       cycle_duration              (in processor clock cycles, 3.333ns)
'  15       CR_probe

' float parameters: DATA_21[i]
' index i   description
'   1       green_repump_voltage
'   2       green_off_voltage
'   3       Ex_CR_voltage
'   4       A_CR_voltage
'   5       Ex_SP_voltage
'   6       A_SP_voltage

' return values:
' Data_22[repetitions]                 CR counts before sequence
' Data_23[repetitions]                 CR counts after sequence
' Data_24[SP_duration]                 time dependence SP
' Data_25[pts*repetitions]   spin readout
' Data_26[...]                         statistics

#INCLUDE ADwinGoldII.inc

#DEFINE max_repetitions   20000
#DEFINE max_SP_bins         500
#DEFINE max_SSRO_dim    1000000
#DEFINE max_stat             10

DIM DATA_20[25] AS LONG               ' integer parameters
DIM DATA_21[10] AS FLOAT              ' float parameters
DIM DATA_22[max_repetitions] AS LONG AT EM_LOCAL  ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG AT EM_LOCAL  ' CR counts after sequence
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_SSRO_dim] AS LONG AT DRAM_EXTERN  ' SSRO counts
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL         ' statistics

DIM counter_channel AS LONG
DIM green_laser_DAC_channel AS LONG
DIM Ex_laser_DAC_channel AS LONG
DIM A_laser_DAC_channel AS LONG
DIM AWG_start_DO_channel AS LONG
DIM AWG_done_DI_channel AS LONG
DIM green_repump_duration AS LONG
DIM CR_duration AS LONG
DIM SP_duration AS LONG
DIM wait_after_pulse_duration AS LONG
DIM SSRO_repetitions AS LONG
DIM pts AS LONG
DIM cycle_duration AS LONG

DIM green_repump_voltage AS FLOAT
DIM green_off_voltage AS FLOAT
DIM Ex_CR_voltage AS FLOAT
DIM A_CR_voltage AS FLOAT
DIM Ex_SP_voltage AS FLOAT
DIM A_SP_voltage AS FLOAT

DIM timer, mode, i AS LONG
DIM wait_after_pulse AS LONG
DIM repetition_counter, total_repetitions AS LONG
DIM counter_pattern AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts AS LONG
DIM first AS LONG

DIM current_cr_threshold AS LONG
DIM CR_probe AS LONG
DIM CR_preselect AS LONG

dim awg_in_is_hi, awg_in_was_hi, awg_in_switched_to_hi as long

INIT:
  counter_channel              = DATA_20[1]
  green_laser_DAC_channel      = DATA_20[2]
  Ex_laser_DAC_channel         = DATA_20[3]
  A_laser_DAC_channel          = DATA_20[4]
  AWG_start_DO_channel         = DATA_20[5]
  AWG_done_DI_channel          = DATA_20[6]
  pts                          = DATA_20[7]
  green_repump_duration        = DATA_20[8]
  CR_duration                  = DATA_20[9]
  SP_duration                  = DATA_20[10]
  wait_after_pulse_duration    = DATA_20[11]
  CR_preselect                 = DATA_20[12]
  SSRO_repetitions             = DATA_20[13]
  cycle_duration               = DATA_20[14]
  CR_probe                     = DATA_20[15]
  
  green_repump_voltage         = DATA_21[1]
  green_off_voltage            = DATA_21[2]
  Ex_CR_voltage                = DATA_21[3]
  A_CR_voltage                 = DATA_21[4]
  Ex_SP_voltage                = DATA_21[5]
  A_SP_voltage                 = DATA_21[6]
  
  FOR i = 1 TO SSRO_repetitions
    DATA_22[i] = 0
    DATA_23[i] = 0
  NEXT i
  
  FOR i = 1 TO max_SP_bins
    DATA_24[i] = 0
  NEXT i
  
  FOR i = 1 TO SSRO_repetitions*pts
    DATA_25[i] = 0
  NEXT i
  
  FOR i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT i
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  counter_pattern     = 2 ^ (counter_channel-1)
  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
  total_repetitions   = pts * SSRO_repetitions
    
  DAC(green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
  DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
  DAC(A_laser_DAC_channel, 32768) ' turn off Ex laser

  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter
  CONF_DIO(13)      'configure DIO 08:15 as input, all other ports as output
  DIGOUT(AWG_start_DO_channel,0)

  mode = 0
  timer = 0
  processdelay = cycle_duration
  
  Par_73 = repetition_counter
  PAR_70 = 0                      ' cumulative counts from probe intervals
  Par_75 = CR_preselect
  Par_68 = CR_probe
  par_76 = 0                      ' cumulative counts during repumping
  par_79 = 0                      ' timer
  par_77 = 0                      ' mode
  
  ' some for debugging
  par_59 = 0
  par_60 = 0
  par_61 = 0
  par_62 = 0
  par_63 = 0
  par_64 = 0
  
  current_cr_threshold = CR_preselect
  
EVENT:
  awg_in_was_hi = awg_in_is_hi
  awg_in_is_hi = digin(AWG_done_DI_channel)
  if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
    awg_in_switched_to_hi = 1
  else
    awg_in_switched_to_hi = 0
  endif
  
  par_77 = mode  
  CR_preselect = PAR_75
  CR_probe     = PAR_68

  IF (wait_after_pulse > 0) THEN
    wait_after_pulse = wait_after_pulse - 1
  ELSE
    SELECTCASE mode
      CASE 0    ' green repump
        IF (timer = 0) THEN
          inc(data_26[mode+1])
          CNT_CLEAR( counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
          DAC(green_laser_DAC_channel, 3277*green_repump_voltage+32768) ' turn on green
        
        ELSE 
          IF (timer = green_repump_duration) THEN
            DAC(green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
            counts = CNT_READ(counter_channel)
            CNT_ENABLE(0)
            PAR_76 = par_76 + counts
            mode = 1
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            current_cr_threshold = CR_preselect
          ENDIF
        ENDIF
      
      CASE 1    ' Ex/A laser CR check
        IF (timer = 0) THEN
          inc(data_26[mode+1])
          DAC(Ex_laser_DAC_channel, 3277*Ex_CR_voltage+32768) ' turn on Ex laser
          DAC(A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
        
        ELSE 
          IF (timer = CR_duration) THEN
            DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            DAC(A_laser_DAC_channel, 32768) ' turn off A laser
            counts = CNT_READ(counter_channel)
            CNT_ENABLE(0)
            PAR_70 = PAR_70 + counts
            
            IF (first > 0) THEN ' first CR after SSRO sequence
              ' DATA_23[repetition_counter] = counts
              first = 0
            ENDIF
            
            IF (counts < current_cr_threshold) THEN
              mode = 0
            ELSE
              mode = 2
              ' DATA_22[repetition_counter+1] = counts  ' CR before next SSRO sequence
              current_cr_threshold = CR_probe
            ENDIF
            
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
      
      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          inc(data_26[mode+1])
          DAC(Ex_laser_DAC_channel, 3277*Ex_SP_voltage+32768) ' turn on Ex laser
          DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
          old_counts = 0
        
        ELSE 
          counts = CNT_READ(counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts
          old_counts = counts
          IF (timer = SP_duration) THEN
            DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            DAC(A_laser_DAC_channel, 32768)   ' turn off A laser
            
            CNT_ENABLE(0)
            mode = 3
            wait_after_pulse = wait_after_pulse_duration
            
            timer = -1
          ENDIF
        ENDIF

      case 3 ' Ex readout with AWG; counting here, though.
        IF (timer = 0) THEN
          inc(data_26[mode+1])
                    
          DIGOUT(AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          DIGOUT(AWG_start_DO_channel,0)
          
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
        
        else
          if(awg_in_switched_to_hi > 0) then
            counts = CNT_READ(counter_channel)
            inc(repetition_counter)
            
            DATA_25[repetition_counter] = counts            
            Par_73 = repetition_counter
            CNT_ENABLE(0)
            CNT_CLEAR(counter_pattern)
            
            IF (repetition_counter = total_repetitions) THEN
              END
            ENDIF
            
            first = 1
            mode = 1
            timer = -1
          endif
        endif
        
    ENDSELECT
    
    timer = timer + 1
    par_79 = timer
    
  ENDIF
  
FINISH:
  'DATA_26[1] = repumps
  'DATA_26[2] = total_repump_counts
  'DATA_26[3] = CR_failed
  


