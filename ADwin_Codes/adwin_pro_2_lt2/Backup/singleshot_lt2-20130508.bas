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
' this program implements single-shot readout fully controlled by ADwin Pro II
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
'  16       SSRO_repetitions
'  17       SSRO_duration
'  18       SSRO_stop_after_first_photon
'  19       cycle_duration              (in processor clock cycles, 3.333ns)
'  20       CR_probe                   
'  21       repump_after_repetitions

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
#Include Math.inc


#DEFINE max_repetitions 20000
#DEFINE max_SP_bins       500
#DEFINE max_SSRO_dim   4000000
#DEFINE max_stat           10

DIM DATA_20[25] AS LONG               ' integer parameters
DIM DATA_21[20] AS FLOAT              ' float parameters
DIM DATA_22[max_repetitions] AS LONG AT EM_LOCAL  ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG  AT EM_LOCAL  ' CR counts after sequence
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_SSRO_dim] AS LONG AT DRAM_EXTERN  ' SSRO counts
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL         ' statistics

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
DIM SSRO_repetitions AS LONG
DIM SSRO_duration AS LONG
DIM SSRO_stop_after_first_photon AS LONG
DIM cycle_duration AS LONG
DIM repump_after_repetitions AS LONG

DIM green_repump_voltage AS FLOAT
DIM green_off_voltage AS FLOAT
DIM Ex_CR_voltage AS FLOAT
DIM A_CR_voltage AS FLOAT
DIM Ex_SP_voltage AS FLOAT
DIM A_SP_voltage AS FLOAT
DIM Ex_RO_voltage AS FLOAT
DIM A_RO_voltage AS FLOAT
DIM Ex_off_voltage AS FLOAT
DIM A_off_voltage AS FLOAT

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
DIM counts, old_counts, cr_counts AS LONG
DIM first AS LONG
DIM gate_good_phase AS INTEGER
DIM time_start, time_stop AS LONG

DIM current_cr_threshold AS LONG
DIM CR_probe AS LONG
DIM CR_preselect AS LONG

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
  repump_after_repetitions     = DATA_20[21]
  
  green_repump_voltage         = DATA_21[1]
  green_off_voltage            = DATA_21[2]
  Ex_CR_voltage                = DATA_21[3]
  A_CR_voltage                 = DATA_21[4]
  Ex_SP_voltage                = DATA_21[5]
  A_SP_voltage                 = DATA_21[6]
  Ex_RO_voltage                = DATA_21[7]
  A_RO_voltage                 = DATA_21[8]
  Ex_off_voltage            = DATA_21[9]
  A_off_voltage            = DATA_21[10]
  
  current_cr_threshold = CR_preselect
  
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
  cr_counts           = 0
  counts              = 0
  old_counts          = 0
    
  P2_DAC(DAC_MODULE, green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

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
  par_68 = CR_probe
  par_76 = 0                      ' cumulative counts during repumping
  par_79 = 0                      ' cumulative LT2 counts in PSB during ssro sequence
  
  par_60 = 0
  par_61 = 0
  par_62 = 0
  par_63 = 0 'par to check the total process time
  
EVENT:
  gate_good_phase = par_15*par_18-2*(par_19-1)
  time_start = Read_Timer()
  
  
  CR_preselect                 = PAR_75
  CR_probe                     = PAR_68
  'PAR_22 = mode
  'PAR_23 = PAR_23 + 1
  'PAR_24 = timer
  IF (wait_after_pulse > 0) THEN
    wait_after_pulse = wait_after_pulse - 1
  ELSE
    SELECTCASE mode
      CASE 0    ' green repump
        IF (timer = 0) THEN
          IF (Mod(repetition_counter,repump_after_repetitions)=0) THEN  'only repump after x SSRO repetitions
            P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
            P2_DAC(DAC_MODULE, green_laser_DAC_channel, 3277*green_repump_voltage+32768) ' turn on green
            repumps = repumps + 1
          ELSE
            mode = 1
            timer = -1
            current_CR_threshold = CR_preselect
          ENDIF
          
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
            current_CR_threshold = CR_preselect
          ENDIF
        ENDIF
      CASE 1    ' Ex/A laser CR check
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_CR_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
        ELSE 
          IF (timer = CR_duration) THEN
            'cr_counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            'P2_CNT_ENABLE(CTR_MODULE, 0)
            
            IF (gate_good_phase > 0) THEN
              cr_counts = P2_CNT_READ(CTR_MODULE, counter_channel)
              PAR_70 = PAR_70 + cr_counts
              INC(PAR_72)
            ENDIF
            
            P2_CNT_ENABLE(CTR_MODULE, 0)
            
            IF (first > 0) THEN ' first CR after SSRO sequence
              DATA_23[repetition_counter] = cr_counts
              first = 0
            ENDIF
            
            IF (cr_counts < current_cr_threshold) THEN
              mode = 0
              INC(CR_failed)
              PAR_71 = CR_failed
              'PAR_25 = CR_preselect
              'PAR_26 = cr_counts
            ELSE
              IF (gate_good_phase > 0) THEN
                P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
                P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
                mode = 2
                DATA_22[repetition_counter+1] = cr_counts  ' CR before next SSRO sequence
                current_cr_threshold = CR_probe
                'PAR_25 = CR_preselect
                'PAR_26 = cr_counts
                'ELSE
                ' mode = 0
                ' INC(CR_failed)
                ' PAR_71 = CR_failed
              ENDIF
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
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
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
            IF (SP_filter_duration = 0) THEN
              P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
              P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
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
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
        ELSE 
          IF (timer = SP_filter_duration) THEN
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
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
              IF (((P2_DIGIN_LONG(DIO_MODULE)) AND (AWG_done_DI_pattern)) > 0) THEN
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
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        ELSE 
          IF (timer = SSRO_duration) THEN
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
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
            IF ((SSRO_stop_after_first_photon > 0 ) and (counts > 0)) THEN
              P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
              P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
              P2_CNT_ENABLE(CTR_MODULE, 0)
              PAR_79 = PAR_79 + counts
              mode = 1
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
    
    timer = timer + 1
  ENDIF
  time_stop = Read_Timer()
  par_63 = Max_long(par_63,(time_stop-time_start))
FINISH:
  DATA_26[1] = repumps
  DATA_26[2] = total_repump_counts
  DATA_26[3] = CR_failed
  


