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
' mode  3:  optional: trigger for AWG or wait time
' mode  4:  conditional segmented RO, stops either when detecting a photon or after full read-out time (with no photon detected)
' mode  5:  optional AWG trigger
' mode  6:  full electron RO
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
'  16       SSRO_repetitions
'  17       SSRO_duration
'  18       SSRO_stop_after_first_photon
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
' Data_22[repetitions]                 CR counts before sequence
' Data_23[repetitions]                 CR counts after sequence
' Data_24[SP_duration]                 time dependence SP
' Data_25[SSRO_duration*repetitions]   spin readout
' Data_26[...]                         statistics
'   1   repumps
'   2   CR_failed
'   3   CR_failed

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

#DEFINE max_repetitions 20000
#DEFINE max_SP_bins       500
#DEFINE max_SSRO_dim   1000000
#DEFINE max_stat           10

DIM DATA_20[25] AS LONG               ' integer parameters
DIM DATA_21[10] AS FLOAT              ' float parameters
DIM DATA_22[max_repetitions] AS LONG AT EM_LOCAL  ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG  AT EM_LOCAL  ' CR counts after sequence
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_SSRO_dim] AS LONG AT DRAM_EXTERN  ' SSRO counts (final full read-out)
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL         ' statistics
DIM DATA_27[max_repetitions] AS LONG AT EM_LOCAL  ' segment number of the detected click (0=no click within read-out time)

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
DIM SSRO_repetitions AS LONG
DIM SSRO_duration AS LONG
DIM SSRO_stop_after_first_photon AS LONG
DIM cycle_duration AS LONG

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
DIM counts, old_counts AS LONG
DIM first AS LONG
DIM gate_good_phase AS INTEGER

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
  SSRO_repetitions             = DATA_20[16]
  SSRO_duration                = DATA_20[17]
  SSRO_stop_after_first_photon = DATA_20[18]
  cycle_duration               = DATA_20[19]
  
  green_repump_voltage         = DATA_21[1]
  green_off_voltage            = DATA_21[2]
  Ex_CR_voltage                = DATA_21[3]
  A_CR_voltage                 = DATA_21[4]
  Ex_SP_voltage                = DATA_21[5]
  A_SP_voltage                 = DATA_21[6]
  Ex_RO_voltage                = DATA_21[7]
  A_RO_voltage                 = DATA_21[8]
  
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
  
  FOR i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT i
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  counter_pattern     = 2 ^ (counter_channel-1)
  
  total_repump_counts = 0
  CR_failed           = 0
  repumps             = 0
  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
    
  P2_DAC(DAC_MODULE, green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter_channel,00001000b) 'configure counter

  P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

  mode = 0
  timer = 0
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
  
  par_60 = 0
  par_61 = 0
  par_62 = 0
  
EVENT:
  gate_good_phase = par_15*par_18-2*(par_19-1)
  
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
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE, green_laser_DAC_channel, 3277*green_repump_voltage+32768) ' turn on green
          repumps = repumps + 1
        ELSE 
          IF (timer = green_repump_duration) THEN
            P2_DAC(DAC_MODULE, green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
            counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            P2_CNT_ENABLE(CTR_MODULE, 0)
            total_repump_counts = total_repump_counts + counts
            PAR_76 = total_repump_counts
            mode = 1
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
      CASE 1    ' Ex/A laser CR check
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_CR_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          INC(PAR_72)
        ELSE 
          IF (timer = CR_duration) THEN
            counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            P2_CNT_ENABLE(CTR_MODULE, 0)
            
            IF (gate_good_phase > 0) THEN
              PAR_70 = PAR_70 + counts
            ENDIF
            
            IF (first > 0) THEN ' first CR after SSRO sequence
              DATA_23[repetition_counter] = counts
              first = 0
            ENDIF
            IF (counts < CR_preselect) THEN
              mode = 0
              INC(CR_failed)
              PAR_71 = CR_failed
              'PAR_25 = CR_preselect
              'PAR_26 = counts
            ELSE
              P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
              P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
              mode = 2
              DATA_22[repetition_counter+1] = counts  ' CR before next SSRO sequence
              'PAR_25 = CR_preselect
              'PAR_26 = counts
            ENDIF
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
      
      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          old_counts = 0
        ELSE 
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts
          
          if (counts < 0) then
            par_60 = par_60 + 1
          endif
          if (old_counts < 0) then
            par_61 = par_61 + 1
          endif
          if (counts < old_counts) then
            par_62 = par_62 + 1
          endif     
          
          old_counts = counts
          IF (timer = SP_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE, 0)
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
            IF ((send_AWG_start > 0) or (sequence_wait_time > 0)) THEN
              mode = 3
            ELSE
              mode = 4
            ENDIF
            wait_after_pulse = wait_after_pulse_duration
            timer = -1
          ENDIF
        ENDIF
        
      CASE 3    '  wait for AWG sequence or for fixed duration
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
              IF (((P2_DIGIN_LONG(DIO_MODULE)) AND (AWG_done_DI_pattern)) > 0) THEN
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
        ENDIF
      
      CASE 4    ' conditional spin readout
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        ELSE 
          IF ((timer = SSRO_duration) OR (P2_CNT_READ(CTR_MODULE, counter_channel) > 0)) THEN
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
            i = timer + repetition_counter * SSRO_duration
            ' in data_27 we store the segment number for th edetected click. If no click was detected, then we store -1
            DATA_27[i] = timer
            IF (P2_CNT_READ(CTR_MODULE, counter_channel) < 1) THEN
              DATA_27[i] = -1
            ENDIF
            P2_CNT_ENABLE(CTR_MODULE, 0)
            mode = 5
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            repetition_counter = repetition_counter + 1
            Par_73 = repetition_counter
            IF (repetition_counter = SSRO_repetitions) THEN
              END
            ENDIF
            first = 1
          ENDIF
        ENDIF

      CASE 5    ' wait for AWG sequence or for fixed duration
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
              IF (((P2_DIGIN_LONG(DIO_MODULE)) AND (AWG_done_DI_pattern)) > 0) THEN
                AWG_done = 1
                IF (sequence_wait_time > 0) THEN
                  aux_timer = timer
                ELSE
                  mode = 6
                  timer = -1
                  wait_after_pulse = 0
                ENDIF
              ENDIF
            ELSE
              IF (timer - aux_timer >= sequence_wait_time) THEN
                mode = 6
                timer = -1
                wait_after_pulse = 0
              ENDIF
            ENDIF
          ELSE
            IF (timer >= sequence_wait_time) THEN
              mode = 6
              timer = -1
              wait_after_pulse = 0
              'ELSE
              'CPU_SLEEP(9)
            ENDIF
          ENDIF
        ENDIF
      
      CASE 6    ' full spin readout
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        ELSE 
          IF (timer = SSRO_duration) THEN
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
            counts = P2_CNT_READ(CTR_MODULE, counter_channel) - old_counts
            old_counts = counts
            PAR_79 = PAR_79 + counts
            i = timer + repetition_counter * SSRO_duration
            DATA_25[i] = counts
            P2_CNT_ENABLE(CTR_MODULE, 0)
            mode = 1
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            repetition_counter = repetition_counter + 1
            Par_73 = repetition_counter
            IF (repetition_counter = SSRO_repetitions) THEN
              END
            ENDIF
            first = 1
          ELSE
            counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            i = timer + repetition_counter * SSRO_duration
            DATA_25[i] = counts - old_counts
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
  


