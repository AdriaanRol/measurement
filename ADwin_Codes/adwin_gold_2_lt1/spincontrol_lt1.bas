'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' this program implements spin readout based on the ssro protocol, 
' but integrated over repetitions and readout time.
' the measurement protocol is fully controlled by ADwin Pro II.
'
' protocol:
' mode  0:  green pulse, 
'           photon counting just for statistics
' mode  1:  Ex/A pulse, photon counting  ->  CR check
'           fail: -> mode 0
' mode  2:  spin pumping with Ex or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with Ex or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  Ex pulse and photon counting for spin-readout with time dependence
'           -> mode 1
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
'   7       send_AWG_start
'   8       wait_for_AWG_done
'   9       green_repump_duration       (durations in process cycles)
'  10       CR_duration
'  11       SP_duration
'  12       SP_filter_duration
'  13       sequence_wait_time
'  14       wait_after_pulse_duration
'  15       CR_preselect
'  16       RO_repetitions
'  17       RO_duration
'  18       sweep_length
'  19       cycle_duration              (in processor clock cycles, 3.333ns)

' float parameters: DATA_21[i]
' index i   description
'   1       green_repump_voltage
'   2       green_off_voltage
'   3       Ex_CR_voltage
'   4       A_CR_voltage
'   5       Ex_SP_voltage
'   6       A_SP_voltage
'   7       Ex_RO_voltage
'   8       A_RO_voltage

' return values:
' Data_22[1]                 CR counts before sequence
' Data_23[1]                 CR counts after sequence
' Data_24[SP_duration]                 time dependence SP
' Data_25[RO_duration]                 spin readout
' Data_26[...]                         statistics
'   1   repumps
'   2   CR_failed
'   3   CR_failed

#INCLUDE ADwinGoldII.inc

#DEFINE max_SP_bins       500
#DEFINE max_RO_dim    1000000
#DEFINE max_stat           10

DIM DATA_20[25] AS LONG                           ' integer parameters
DIM DATA_21[10] AS FLOAT                          ' float parameters
DIM DATA_22[1] AS LONG AT EM_LOCAL                ' CR counts before sequence
DIM DATA_23[1] AS LONG AT EM_LOCAL                ' CR counts after sequence
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_RO_dim] AS LONG AT DRAM_EXTERN    ' RO counts
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL         ' statistics
DIM DATA_27[max_RO_dim] AS LONG AT DRAM_EXTERN    ' SSRO spin states  

DIM counter_channel AS LONG
DIM green_laser_DAC_channel AS LONG
DIM Ex_laser_DAC_channel AS LONG
DIM A_laser_DAC_channel AS LONG
DIM AWG_start_DO_channel AS LONG
DIM AWG_done_DI_channel AS LONG
DIM send_AWG_start AS LONG
DIM wait_for_AWG_done AS LONG
DIM green_repump_duration AS LONG
DIM CR_duration AS LONG
DIM SP_duration AS LONG
DIM SP_filter_duration AS LONG
DIM sequence_wait_time AS LONG
DIM wait_after_pulse_duration AS LONG
DIM CR_preselect AS LONG
DIM RO_repetitions AS LONG
DIM RO_duration AS LONG
DIM cycle_duration AS LONG
DIM sweep_length AS LONG

DIM green_repump_voltage AS FLOAT
DIM green_off_voltage AS FLOAT
DIM Ex_CR_voltage AS FLOAT
DIM A_CR_voltage AS FLOAT
DIM Ex_SP_voltage AS FLOAT
DIM A_SP_voltage AS FLOAT
DIM Ex_RO_voltage AS FLOAT
DIM A_RO_voltage AS FLOAT

DIM timer, mode, i AS LONG
DIM aux_timer AS LONG
DIM AWG_done AS LONG
DIM wait_after_pulse AS LONG
DIM repetition_counter AS LONG
DIM repumps AS LONG
DIM CR_failed AS LONG
DIM total_repump_counts AS LONG
DIM counter_pattern AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts, counts_CR AS LONG
DIM first AS LONG
DIM sweep_index AS LONG

INIT:
  counter_channel              = DATA_20[1]
  green_laser_DAC_channel      = DATA_20[2]
  Ex_laser_DAC_channel         = DATA_20[3]
  A_laser_DAC_channel          = DATA_20[4]
  AWG_start_DO_channel         = DATA_20[5]
  AWG_done_DI_channel          = DATA_20[6]
  send_AWG_start               = DATA_20[7]
  wait_for_AWG_done            = DATA_20[8]
  green_repump_duration        = DATA_20[9]
  CR_duration                  = DATA_20[10]
  SP_duration                  = DATA_20[11]
  SP_filter_duration           = DATA_20[12]
  sequence_wait_time           = DATA_20[13]
  wait_after_pulse_duration    = DATA_20[14]
  CR_preselect                 = DATA_20[15]
  RO_repetitions               = DATA_20[16]
  RO_duration                  = DATA_20[17]
  sweep_length = DATA_20[18]
  cycle_duration               = DATA_20[19]
  
  green_repump_voltage         = DATA_21[1]
  green_off_voltage            = DATA_21[2]
  Ex_CR_voltage                = DATA_21[3]
  A_CR_voltage                 = DATA_21[4]
  Ex_SP_voltage                = DATA_21[5]
  A_SP_voltage                 = DATA_21[6]
  Ex_RO_voltage                = DATA_21[7]
  A_RO_voltage                 = DATA_21[8]
  
  DATA_22[1] = 0
  DATA_23[1] = 0
  
  FOR i = 1 TO max_SP_bins
    DATA_24[i] = 0
  NEXT i
  
  FOR i = 1 TO max_RO_dim
    DATA_25[i] = 0
  NEXT i
  
  FOR i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT i
  
  FOR i = 1 to max_RO_dim
    DATA_27[i] = 0
  NEXT i
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  counter_pattern     = 2 ^ (counter_channel-1)
  
  total_repump_counts = 0
  CR_failed           = 0
  repumps             = 0
  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
    
  DAC(green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
  DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
  DAC(A_laser_DAC_channel, 32768) ' turn off Ex laser

  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter

  CONF_DIO(13) 'P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  DIGOUT(AWG_start_DO_channel,0)

  mode = 0
  timer = 0
  sweep_index = 0
  processdelay = cycle_duration
  Par_73 = repetition_counter
  PAR_23 = 0
  PAR_25 = 0
  
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' below CR threshold events
  PAR_72 = 0                      ' number of CR checks performed (lt2)
  par_75 = CR_preselect
  par_76 = 0                      ' cumulative counts during repumping
  par_79 = 0                      ' cumulative LT2 counts in PSB during ssro sequence
  
  
EVENT:
  CR_preselect                 = PAR_75
  'PAR_22 = mode
  'PAR_23 = PAR_23 + 1
  'PAR_24 = timer
  IF (wait_after_pulse > 0) THEN
    wait_after_pulse = wait_after_pulse - 1
  ELSE
    SELECTCASE mode
      CASE 0    ' green repump
        IF (timer = 0) THEN
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
          DAC(green_laser_DAC_channel, 3277*green_repump_voltage+32768) ' turn on green
          repumps = repumps + 1
        ELSE 
          IF (timer = green_repump_duration) THEN
            DAC(green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
            counts = CNT_READ(counter_channel)
            CNT_ENABLE(0)
            total_repump_counts = total_repump_counts + counts
            PAR_76 = total_repump_counts
            mode = 1
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
      CASE 1    ' Ex/A laser CR check
        IF (timer = 0) THEN
          DAC(Ex_laser_DAC_channel, 3277*Ex_CR_voltage+32768) ' turn on Ex laser
          DAC(A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
          INC(PAR_72)
        ELSE 
          IF (timer = CR_duration) THEN
            counts_CR = CNT_READ(counter_channel)
            CNT_ENABLE(0)
            PAR_70 = PAR_70 + counts_CR
            IF (first > 0) THEN ' first CR after SSRO sequence
              DATA_23[1] = DATA_23[1] + counts_CR
              first = 0
            ENDIF
            IF (counts_CR < CR_preselect) THEN
              mode = 0
              INC(CR_failed)
              PAR_71 = CR_failed
              'PAR_25 = CR_preselect
              'PAR_26 = counts
            ELSE
              DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
              DAC(A_laser_DAC_channel, 32768) ' turn off A laser
              mode = 2
              DATA_22[1] = DATA_22[1] + counts_CR  ' CR before next SSRO sequence
              'PAR_25 = CR_preselect
              'PAR_26 = counts
            ENDIF
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
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
            CNT_ENABLE(0)
            IF (SP_filter_duration = 0) THEN
              DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
              DAC(A_laser_DAC_channel, 32768) ' turn off A laser
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
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
        ELSE 
          IF (timer = SP_filter_duration) THEN
            DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            DAC(A_laser_DAC_channel, 32768) ' turn off A laser
            counts = CNT_READ(counter_channel)
            CNT_ENABLE(0)
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
            DIGOUT(AWG_start_DO_channel,1)  ' AWG trigger
            CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            DIGOUT(AWG_start_DO_channel,0)
          ENDIF
          aux_timer = 0
          AWG_done = 0
        ELSE 
          IF (wait_for_AWG_done > 0) THEN 
            IF (AWG_done = 0) THEN
              IF (DIGIN(AWG_done_DI_channel) > 0) THEN
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
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)	  'turn on counter
          DAC(Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on Ex laser
          DAC(A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        ELSE 
          IF (timer = RO_duration) THEN
            DAC(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            DAC(A_laser_DAC_channel, 32768) ' turn off A laser
            counts = CNT_READ(counter_channel) - old_counts
            old_counts = counts
            
            IF (CNT_READ(counter_channel) > 0) THEN
              DATA_27[i] = DATA_27[i] + 1
            ENDIF             
       
            PAR_79 = PAR_79 + counts
            i = timer + RO_duration * sweep_index
            DATA_25[i] = DATA_25[i] + counts
            CNT_ENABLE(0)
            mode = 1
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            repetition_counter = repetition_counter + 1
            Par_73 = repetition_counter
            INC(sweep_index)
            IF (sweep_index = sweep_length) THEN
              sweep_index = 0
            ENDIF
            
            IF (repetition_counter = RO_repetitions) THEN
              END
            ENDIF
            first = 1
          ELSE
            counts = CNT_READ(counter_channel)
            i = timer + RO_duration * sweep_index
            DATA_25[i] = DATA_25[i] + counts - old_counts
            old_counts = counts
          ENDIF
        ENDIF
    ENDSELECT
    
    timer = timer + 1
  ENDIF
  
FINISH:
  DATA_26[1] = repumps
  DATA_26[2] = total_repump_counts
  DATA_26[3] = CR_failed

