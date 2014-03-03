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
' Info_Last_Save                 = TUD277299  TUD277299\localadmin
'<Header End>
' this program implements single-shot readout fully controlled by ADwin Gold II
'
' protocol:
' mode  0: CR check
' mode  2:  spin pumping with E or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with E or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  E pulse and photon counting for spin-readout with time dependence
'           -> mode 1
'

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc

#DEFINE max_SP_bins       2000
#DEFINE max_SSRO_dim      1000000

'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT

'return
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_SSRO_dim] AS LONG  ' SSRO counts spin readout

DIM AWG_start_DO_channel, AWG_done_DI_channel AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG

DIM SP_duration, SP_filter_duration AS LONG
DIM SSRO_repetitions, SSRO_duration, SSRO_stop_after_first_photon AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT

DIM timer, aux_timer, mode, i AS LONG
DIM AWG_done AS LONG
DIM first AS LONG

DIM repetition_counter AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts AS LONG

INIT:
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  send_AWG_start               = DATA_20[3]
  wait_for_AWG_done            = DATA_20[4]
  SP_duration                  = DATA_20[5]
  SP_filter_duration           = DATA_20[6]
  sequence_wait_time           = DATA_20[7]
  wait_after_pulse_duration    = DATA_20[8]
  SSRO_repetitions             = DATA_20[9]
  SSRO_duration                = DATA_20[10]
  SSRO_stop_after_first_photon = DATA_20[11]
  cycle_duration               = DATA_20[12] '(in processor clock cycles, 3.333ns)

  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  
  FOR i = 1 TO SSRO_repetitions
    DATA_22[i] = 0
    DATA_23[i] = 0
  NEXT i
  
  FOR i = 1 TO max_SP_bins
    DATA_24[i] = 0
  NEXT i
  
  FOR i = 1 TO SSRO_repetitions*SSRO_duration
    DATA_25[i] = 0
  NEXT i
    
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  
  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
    
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off E laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,000010000b) 'configure counter

  P2_Digprog(DIO_MODULE,13)      'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

  mode = 0
  timer = 0
  processdelay = cycle_duration
  
  'live updated pars
  Par_73 = repetition_counter     ' SSRO repetitions
  par_74 = 0                      ' SSRO cumulative counts

EVENT:


  IF (wait_after_pulse > 0) THEN
    DEC(wait_after_pulse)
  ELSE
    SELECTCASE mode
      
      CASE 0 'CR check
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 2
          timer = -1
          first = 0
        ENDIF
        
      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          'P2_DAC(DAC_MODULE, repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on Ex laser XXXXXX
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          old_counts = 0
        ELSE 
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts

          old_counts = counts
          IF (timer = SP_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE, 0)
            IF (SP_filter_duration = 0) THEN
              P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*0+32768) ' turn off Ex laser XXXXXX
              P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
              P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
              IF ((send_AWG_start > 0) or (sequence_wait_time > 0)) THEN
                mode = 4
              ELSE
                mode = 5
              ENDIF
              wait_after_pulse = wait_after_pulse_duration
            ELSE
              mode = 3
              wait_after_pulse = 0
            ENDIF
            timer = -1
          ENDIF
        ENDIF
      CASE 3    ' SP filter (postselection)
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
        ELSE 
          IF (timer = SP_filter_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            P2_CNT_ENABLE(CTR_MODULE, 0)
            IF (counts > 0) THEN
              mode = 1
            ELSE
              IF ((send_AWG_start > 0) or (sequence_wait_time > 0)) THEN
                mode = 4
              ELSE
                mode = 5
              ENDIF
            ENDIF
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
      CASE 4    '  wait for AWG sequence or for fixed duration
        IF (timer = 0) THEN
          IF (send_AWG_start > 0) THEN
            P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
            CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
          ENDIF
          aux_timer = 0
          AWG_done = 0
        ELSE 
          IF (wait_for_AWG_done > 0) THEN 
            IF (AWG_done = 0) THEN
              IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN
                AWG_done = 1
                IF (sequence_wait_time > 0) THEN
                  aux_timer = timer
                ELSE
                  mode = 5
                  timer = -1
                  wait_after_pulse = 0
                ENDIF
              ENDIF
            ELSE
              IF (timer - aux_timer >= sequence_wait_time) THEN
                mode = 5
                timer = -1
                wait_after_pulse = 0
              ENDIF
            ENDIF
          ELSE
            IF (timer >= sequence_wait_time) THEN
              mode = 5
              timer = -1
              wait_after_pulse = 0
              'ELSE
              'CPU_SLEEP(9)
            ENDIF
          ENDIF
        ENDIF
    
      CASE 5    ' spin readout
        
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on E laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        
        ELSE 
          
          IF (timer = SSRO_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            counts = P2_CNT_READ(CTR_MODULE,counter_channel) - old_counts
            old_counts = counts
            PAR_74 = PAR_74 + counts
            i = timer + repetition_counter * SSRO_duration
            DATA_25[i] = counts
            P2_CNT_ENABLE(CTR_MODULE,0)
            
            mode = 0
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            repetition_counter = repetition_counter + 1
            Par_73 = repetition_counter
            
            IF (repetition_counter = SSRO_repetitions) THEN
              END
            ENDIF
            
            first = 1
          
          ELSE
            
            counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            i = timer + repetition_counter * SSRO_duration
            
            IF ((SSRO_stop_after_first_photon > 0 ) and (counts > 0)) THEN
              
              P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
              P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
              P2_CNT_ENABLE(CTR_MODULE,0)
              PAR_74 = PAR_74 + counts
              
              mode = 0
              timer = -1
              wait_after_pulse = wait_after_pulse_duration
              repetition_counter = repetition_counter + 1
              Par_73 = repetition_counter
              DATA_25[i] = counts
              
              IF (repetition_counter = SSRO_repetitions) THEN
                END
              ENDIF
              
              first = 1
            ENDIF
            
            DATA_25[i] = counts - old_counts
            old_counts = counts
          
          ENDIF
        ENDIF
    ENDSELECT
    
    Inc(timer)
    
  ENDIF
  
FINISH:
  finish_CR()
  
  


