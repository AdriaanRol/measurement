'<ADbasic Header, Headerversion 001.001>
' Foldings                       = 170
'<Header End>
' this program implements CR check fully controlled by ADwin Pro II
'
' protocol:
' mode  0:  green pulse, 
'           photon counting just for statistics
' mode  1:  E/A pulse, photon counting  ->  CR check
'           fail: -> mode 0


#DEFINE max_stat           10
#DEFINE max_repetitions 500000
'init
DIM DATA_30[100] AS LONG               ' CR integer parameters
DIM DATA_31[100] AS FLOAT              ' CR float parameters

'return
'used in cr.inc
DIM DATA_22[max_repetitions] AS LONG  ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG ' CR counts after sequence
DIM DATA_26[max_stat] AS LONG         ' statistics

DIM cr_mode, cr_timer, cr_i AS LONG
DIM cr_counts AS LONG
DIM CR_probe, CR_preselect, CR_repump, current_CR_threshold AS LONG
DIM repumps, CR_failed, total_repump_counts AS LONG
DIM repump_duration, CR_duration AS LONG
DIM cr_wait_after_pulse, cr_wait_after_pulse_duration AS LONG
DIM counter_channel, counter_pattern AS LONG
DIM E_laser_DAC_channel, A_laser_DAC_channel, repump_laser_DAC_channel AS LONG

DIM repump_voltage, repump_off_voltage, E_CR_voltage, A_CR_voltage, E_off_voltage, A_off_voltage AS FLOAT

SUB init_CR()
  counter_channel              = DATA_30[1]
  repump_laser_DAC_channel     = DATA_30[2]
  E_laser_DAC_channel          = DATA_30[3] ' this is also used in the main script i.e. MBI_lt2 for ssro, more logical to define there? -machiel 30-12-'13
  A_laser_DAC_channel          = DATA_30[4]
  repump_duration              = DATA_30[5]
  CR_duration                  = DATA_30[6]
  cr_wait_after_pulse_duration = DATA_30[7]
  CR_preselect                 = DATA_30[8]
  CR_probe                     = DATA_30[9]
  CR_repump                    = DATA_30[10]

  repump_voltage               = DATA_31[1]
  repump_off_voltage           = DATA_31[2]
  E_CR_voltage                 = DATA_31[3]
  A_CR_voltage                 = DATA_31[4]
  E_off_voltage                = DATA_31[5]
  A_off_voltage                = DATA_31[6]
  
  FOR cr_i = 1 TO max_repetitions
    DATA_22[i] = 0
    DATA_23[i] = 0
  NEXT cr_i
  FOR cr_i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT cr_i
  
  counter_pattern     = 2 ^ (counter_channel-1)
  total_repump_counts = 0
  CR_failed           = 0
  repumps             = 0
  cr_wait_after_pulse    = 0
  cr_mode = 0
  cr_timer = 0
  
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' number of repumps
  PAR_72 = 0                      ' number of CR checks performed (lt1)
  Par_75 = CR_preselect
  Par_68 = CR_probe
  par_69 = CR_repump
  par_76 = 0                      ' cumulative counts during repumping
  par_79 = 0                      ' CR below treshold events
ENDSUB



FUNCTION CR_check(first_cr, repetition_index) As LONG

  CR_check = 0
  
  IF (cr_wait_after_pulse > 0) THEN
    DEC(cr_wait_after_pulse)
  ELSE

    SELECTCASE cr_mode 
      CASE 0    ' green repump
              
        IF (cr_timer = 0) THEN
          CR_repump                    = PAR_69
          IF (cr_counts < CR_repump)  THEN  'only repump 
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on green
            repumps = repumps + 1
            inc(par_71)
          ELSE
            cr_mode = 1
            cr_timer = -1
            current_CR_threshold = CR_preselect
          ENDIF
        
        ELSE 
          
          IF (cr_timer = repump_duration) THEN
            
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
            cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            P2_CNT_ENABLE(CTR_MODULE,0)
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)
            
            total_repump_counts = total_repump_counts + cr_counts
            PAR_76 = total_repump_counts
            
            cr_mode = 1
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration
            current_cr_threshold = CR_preselect
          ENDIF
        ENDIF
      
      CASE 1    ' E/A laser CR check
        
        IF (cr_timer = 0) THEN
          CR_preselect                 = PAR_75
          CR_probe                     = PAR_68
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_CR_voltage+32768) ' turn on E laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          INC(PAR_72)
        
        ELSE 
          
          IF (cr_timer = CR_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            P2_CNT_ENABLE(CTR_MODULE,0)
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)
            PAR_70 = PAR_70 + cr_counts
            
            IF (first_cr > 0) THEN ' first CR after SSRO sequence
              DATA_23[repetition_index] = cr_counts
            ENDIF
                      
            IF (cr_counts < current_cr_threshold) THEN
              cr_mode = 0
              inc(CR_failed)
              inc(PAR_79)
            ELSE
              cr_mode = 1
              CR_check = 1
              DATA_22[repetition_index+1] = cr_counts  ' CR before nEt SSRO sequence
              current_cr_threshold = CR_probe
            ENDIF
            
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration
          ENDIF
        ENDIF
    ENDSELECT
    inc(cr_timer)
  ENDIF
  
ENDFUNCTION
  
SUB finish_CR()
  DATA_26[1] = repumps
  DATA_26[2] = total_repump_counts
  DATA_26[3] = CR_failed
ENDSUB

