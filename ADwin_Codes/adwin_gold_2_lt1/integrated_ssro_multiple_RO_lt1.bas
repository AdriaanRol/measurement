'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277246  TUD277246\localadmin
'<Header End>
' this program implements CR check and N times |SP - AWG sequence - integrated SSRO |
' controlled by ADwin Pro
'
' protocol:
' mode  0:  CR check
' mode  2:  spin pumping with Ex or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with Ex or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  SSRO -> mode 1, data saved is binary number for each Nth RO step

#INCLUDE ADwinGoldII.inc
#INCLUDE .\cr.inc
#INCLUDE .\SSRO.inc

#DEFINE max_SP_bins        500 

'init
DIM DATA_20[100] AS LONG      ' integer parameters
DIM DATA_21[100] AS FLOAT     ' float parameters

'return

DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts 
DIM DATA_25[max_repetitions] AS LONG AT DRAM_EXTERN    ' SSRO counts


DIM AWG_start_DO_channel, AWG_done_DI_channel AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG
DIM SP_duration AS LONG
DIM SSRO_repetitions, SSRO_duration, SSRO_stop_after_first_photon AS LONG ' stop_after.. for dynamical-stop RO, not used atm.
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT

DIM timer, aux_timer, mode, i, sweep_index,sweep_length AS LONG
DIM AWG_done AS LONG
DIM first AS LONG

DIM repetition_counter AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts AS LONG

INIT:  
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  send_AWG_start               = DATA_20[3]
  wait_for_AWG_done            = DATA_20[4]
  SP_duration                  = DATA_20[5]
  sequence_wait_time           = DATA_20[6]
  wait_after_pulse_duration    = DATA_20[7]
  SSRO_repetitions             = DATA_20[8]
  SSRO_duration                = DATA_20[9] 
  SSRO_stop_after_first_photon = DATA_20[10] ' for dynamical-stop RO, not used atm
  cycle_duration               = DATA_20[11] '(in processor clock cycles, 3.333ns)
  'sweep_length                 = DATA_20[12]
  
  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  par_80 = SSRO_stop_after_first_photon
  
  FOR i = 1 TO max_SP_bins
    DATA_24[i] = 0          ' counts during SP
  NEXT i
  
  FOR i = 1 TO SSRO_repetitions
    DATA_25[i] = 0          'result of ssro's
  NEXT i
   
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel

  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
      
  DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off repump
  DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
  DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  CNT_ENABLE(0000b) 'turn off all counters
  CNT_MODE(counter_channel, 00001000b) 'configure counter

  CONF_DIO(11)
  DIGOUT(AWG_start_DO_channel,0)

  sweep_length= SSRO_repetitions ' for now, only 1 CR check with N ssro reps, if later we want M times this, sweep length should be changed.
  sweep_index = 1
  mode = 0
  timer = 0
  processdelay = cycle_duration  
  
  Par_73 = repetition_counter
  Par_74 = mode


EVENT:
  PAR_74=mode
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
          DAC(E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          CNT_CLEAR( counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
        else
          CNT_CLEAR( counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          counts = CNT_READ(counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts
        Endif

        IF (timer = SP_duration) THEN
          CNT_ENABLE(0)
          DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
          DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser                
          
          IF ((send_AWG_start > 0) or (sequence_wait_time > 0)) THEN
            mode = 3
          ELSE
            mode = 4
          ENDIF
          
          wait_after_pulse = wait_after_pulse_duration
          timer = -1
        ENDIF
      
      CASE 3    '  wait for AWG sequence or for fixed duration
        IF (timer = 0) THEN
          IF (send_AWG_start > 0) THEN
            DIGOUT(AWG_start_DO_channel,1)  ' AWG trigger
            CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            DIGOUT(AWG_start_DO_channel,0)
          ENDIF
          aux_timer = 0
          AWG_done = 0
        endif
         
        IF (wait_for_AWG_done > 0) THEN 
          IF (AWG_done = 0) THEN
            IF (DIGIN(AWG_done_DI_channel) > 0) THEN
              AWG_done = 1
              IF (sequence_wait_time > 0) THEN
                aux_timer = timer
              ELSE
                mode = 4
                timer = -1
                wait_after_pulse = 0
              ENDIF
            ENDIF
          ELSE
            IF (timer - aux_timer >= sequence_wait_time) THEN
              mode = 4
              timer = -1
              wait_after_pulse = 0
            ENDIF
          ENDIF
        ELSE
          IF (timer >= sequence_wait_time) THEN
            mode = 4
            timer = -1
            wait_after_pulse = 0
            'ELSE
            'CPU_SLEEP(9)
          ENDIF
        ENDIF
     
      CASE 4    ' spin readout
        IF (SSRO(SSRO_duration) > 0) THEN
          if (ssro_counts > 0) then
            inc(data_25[sweep_index])
          endif
          
          inc(sweep_index)
          if (sweep_index > sweep_length) then
            sweep_index = 1
          endif
          
          mode = 2 
          timer = -1
          wait_after_pulse = wait_after_pulse_duration
          inc(repetition_counter)
          Par_73 = repetition_counter
          IF (repetition_counter = SSRO_repetitions) THEN
            END
          ENDIF
          first = 1

        ENDIF
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


