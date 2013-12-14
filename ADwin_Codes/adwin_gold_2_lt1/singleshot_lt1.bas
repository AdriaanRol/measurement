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
' Info_Last_Save                 = TUD200823  TUD200823\localadmin
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

#INCLUDE ADwinGoldII.inc
#INCLUDE .\cr.inc

#DEFINE max_SP_bins       2000
#DEFINE max_SSRO_dim      1000000

'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT

'return
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_SSRO_dim] AS LONG  ' SSRO counts spin readout

DIM AWG_start_DO_channel, AWG_done_DI_channel, APD_gate_DO_channel AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG

DIM SP_duration, SP_filter_duration AS LONG
DIM SSRO_repetitions, SSRO_duration, SSRO_stop_after_first_photon AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT

DIM timer, mode, i AS LONG
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
  APD_gate_DO_channel          = DATA_20[13]

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
    
  DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
  DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off E laser

  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter

  CONF_DIO(13)      'configure DIO 08:15 as input, all other ports as output
  DIGOUT(AWG_start_DO_channel,0)

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
        
      CASE 2    ' E or A laser spin pumping
        IF (timer = 0) THEN
          DAC(E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on E laser
          DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          old_counts = 0
        
        ELSE 
          counts = CNT_READ(counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts
          old_counts = counts
          
          IF (timer = SP_duration) THEN
            DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            
            CNT_ENABLE(0)
            CNT_CLEAR(counter_pattern)         
            
            mode = 5
            wait_after_pulse = wait_after_pulse_duration
            timer = -1
          ENDIF
        ENDIF   
    
      CASE 5    ' spin readout
        
        IF (timer = 0) THEN
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          DAC(E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on E laser
          DAC(A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        
        ELSE 
          
          IF (timer = SSRO_duration) THEN
            DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            counts = CNT_READ(counter_channel) - old_counts
            old_counts = counts
            PAR_74 = PAR_74 + counts
            i = timer + repetition_counter * SSRO_duration
            DATA_25[i] = counts
            CNT_ENABLE(0)
            
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
            
            counts = CNT_READ(counter_channel)
            i = timer + repetition_counter * SSRO_duration
            
            IF ((SSRO_stop_after_first_photon > 0 ) and (counts > 0)) THEN
              
              DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
              DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
              CNT_ENABLE(0)
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
  
  


