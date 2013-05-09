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
' this program implements a spin manipulation sequence, where ADwin controls lasers and AWG the MW and RF, timing is controlled by ADwin Pro II
'
' protocol:
' mode  0:  green pulse, 
'           photon counting just for statistics
' mode  1:  optional: trigger for AWG sequence, or static wait time
' mode  2:  Green pulse and photon counting for spin-readout with time dependence
'           -> mode 0
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
'  20       green_readout_duration
'  21       datapoints


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
'   9       green_readout_voltage

' return values:
' Data_22[repetitions]                 CR counts before sequence
' Data_23[repetitions]                 CR counts after sequence
' Data_24[SP_duration]                 time dependence SP
' Data_25[SSRO_duration*repetitions]   spin readout
' Data_26[...]                         statistics
' Data_27[datapoints]                  green spin readout
'   1   repumps
'   2   CR_failed
'   3   CR_failed

#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc
#INCLUDE Math.inc

#DEFINE max_repetitions 10000
#DEFINE max_SP_bins       500
#DEFINE max_SSRO_dim   500000
#DEFINE max_stat           10
#DEFINE max_datapoints  10000

DIM DATA_20[25] AS LONG                             ' integer parameters
DIM DATA_21[10] AS FLOAT                            ' float parameters
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL        ' SP counts
DIM DATA_25[max_SSRO_dim] AS LONG AT DRAM_EXTERN    ' SSRO counts
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL           ' Statistics
DIM DATA_27[max_datapoints] AS LONG                 ' Green spin readout counts

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
DIM CR_probe  AS LONG
DIM green_readout_duration AS LONG
DIM datapoints AS LONG

DIM green_repump_voltage AS FLOAT
DIM green_off_voltage AS FLOAT
DIM Ex_CR_voltage AS FLOAT
DIM A_CR_voltage AS FLOAT
DIM Ex_SP_voltage AS FLOAT
DIM A_SP_voltage AS FLOAT
DIM Ex_RO_voltage AS FLOAT
DIM A_RO_voltage AS FLOAT
DIM green_readout_voltage AS FLOAT

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
  CR_probe                     = DATA_20[20]
  green_readout_duration       = DATA_20[21]
  datapoints                   = DATA_20[22]
  
  green_repump_voltage         = DATA_21[1]
  green_off_voltage            = DATA_21[2]
  Ex_CR_voltage                = DATA_21[3]
  A_CR_voltage                 = DATA_21[4]
  Ex_SP_voltage                = DATA_21[5]
  A_SP_voltage                 = DATA_21[6]
  Ex_RO_voltage                = DATA_21[7]
  A_RO_voltage                 = DATA_21[8]
  green_readout_voltage        = DATA_21[9]
  'FOR i = 1 TO SSRO_repetitions
  '  DATA_22[i] = 0
  '  DATA_23[i] = 0
  'NEXT i
  
  'FOR i = 1 TO max_SP_bins
  '  DATA_24[i] = 0
  'NEXT i
  
  'FOR i = 1 TO SSRO_repetitions*SSRO_duration
  '  DATA_25[i] = 0
  'NEXT i
  
  FOR i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT i
  
  FOR i = 1 to datapoints
    data_27[i] = 0
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
  P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser

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
  
  
EVENT:
  IF (wait_after_pulse > 0) THEN
    wait_after_pulse = wait_after_pulse - 1
  ELSE
    SELECTCASE mode
      CASE 0    ' green repump
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
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
      CASE 1    '  wait for AWG sequence or for fixed duration
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
                  mode = 2
                  timer = -1
                  wait_after_pulse = 0
                ENDIF
              ENDIF
            ELSE
              IF (timer - aux_timer >= sequence_wait_time) THEN
                mode = 2
                timer = -1
                wait_after_pulse = 0
              ENDIF
            ENDIF
          ELSE
            IF (timer >= sequence_wait_time) THEN
              mode = 2
              timer = -1
              wait_after_pulse = 0
              'ELSE
              'CPU_SLEEP(9)
            ENDIF
          ENDIF
        ENDIF
      
      CASE 2    ' spin readout with green
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
          P2_DAC(DAC_MODULE, green_laser_DAC_channel, 3277*green_readout_voltage+32768) ' turn on Green laser
          old_counts = 0 'this is only necessary if you want counts per run or so...
        ELSE 
          IF (timer = green_readout_duration) THEN
            'P2_DAC(DAC_MODULE, green_laser_DAC_channel, 32768) ' turn off Green laser
            
            counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            
            i=Mod(repetition_counter,datapoints)+1
            PAR_79 = PAR_79 + counts
            DATA_27[i] = DATA_27[i] + counts
            P2_CNT_ENABLE(CTR_MODULE, 0)
            mode = 0
            timer = -1
            repetition_counter = repetition_counter + 1
            Par_73 = repetition_counter
            
            IF (repetition_counter = SSRO_repetitions) THEN
              END
            ENDIF
          ENDIF
        ENDIF
    ENDSELECT
    Par_80 = mode
    Par_81 = timer
    timer = timer + 1
  ENDIF
  
FINISH:
  DATA_26[1] = repumps
  DATA_26[2] = total_repump_counts
  DATA_26[3] = CR_failed
  


