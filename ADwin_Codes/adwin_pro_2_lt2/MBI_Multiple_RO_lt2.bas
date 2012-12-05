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

#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

#DEFINE max_SP_bins       500
#DEFINE max_RO_dim    1000000
#DEFINE max_stat           10

DIM DATA_20[35] AS LONG                           ' integer parameters
DIM DATA_21[10] AS FLOAT                          ' float parameters
DIM DATA_22[1] AS LONG AT EM_LOCAL                ' CR counts before sequence
DIM DATA_23[1] AS LONG AT EM_LOCAL                ' CR counts after sequence
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_RO_dim] AS LONG AT DRAM_EXTERN    ' RO counts
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL         ' statistics
DIM DATA_27[max_RO_dim] AS LONG AT DRAM_EXTERN    ' SSRO counts
DIM DATA_28[max_SP_bins] AS LONG AT EM_LOCAL      ' SP2 counts

DIM counter_channel AS LONG
DIM green_laser_DAC_channel AS LONG
DIM Ex_laser_DAC_channel AS LONG
DIM A_laser_DAC_channel AS LONG
DIM AWG_start_DO_channel AS LONG
DIM AWG_event_jump_DO_channel AS LONG
DIM AWG_done_DI_channel AS LONG
DIM send_AWG_start AS LONG
DIM wait_for_AWG_done AS LONG
DIM green_repump_duration AS LONG
DIM CR_duration AS LONG
DIM SP_E_duration AS LONG
DIM SP_filter_duration AS LONG
DIM MBI_duration AS LONG
DIM sequence_wait_time AS LONG
DIM wait_after_pulse_duration AS LONG
DIM RO_repetitions AS LONG
DIM RO_duration AS LONG
DIM cycle_duration AS LONG
DIM sweep_length AS LONG
DIM wait_for_MBI_pulse AS LONG
DIM SP_A_duration AS LONG
DIM MBI_threshold AS LONG
DIM nr_of_RO_steps AS LONG


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
DIM MBI_failed AS LONG
DIM total_repump_counts AS LONG
DIM counter_pattern AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts AS LONG
DIM first AS LONG
DIM sweep_index AS LONG
DIM gate_good_phase AS INTEGER
DIM stop_MBI AS LONG
DIM MBI_starts AS LONG
DIM RO_cntr AS LONG


DIM current_cr_threshold AS LONG
DIM CR_probe AS LONG
DIM CR_preselect AS LONG
DIM cr_counts AS LONG

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
  SP_E_duration                = DATA_20[11]
  SP_filter_duration           = DATA_20[12]
  sequence_wait_time           = DATA_20[13]
  wait_after_pulse_duration    = DATA_20[14]
  CR_preselect                 = DATA_20[15]
  RO_repetitions               = DATA_20[16]
  RO_duration                  = DATA_20[17]
  sweep_length                 = DATA_20[18]
  cycle_duration               = DATA_20[19]
  CR_probe                     = DATA_20[20]
  AWG_event_jump_DO_channel    = DATA_20[21]
  MBI_duration                 = DATA_20[22]
  wait_for_MBI_pulse           = DATA_20[23]
  SP_A_duration                = DATA_20[24]
  MBI_threshold                = DATA_20[25]
  nr_of_RO_steps               = DATA_20[26]
  
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
  
  FOR i = 1 TO max_SP_bins
    DATA_28[i] = 0
  NEXT i
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  counter_pattern     = 2 ^ (counter_channel-1)
  
  total_repump_counts = 0
  CR_failed           = 0
  MBI_failed          = 0
  MBI_starts          = 0
  repumps             = 0
  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
  stop_MBI            = wait_for_MBI_pulse + MBI_duration
  RO_cntr             = 0
    
  P2_DAC(DAC_MODULE, green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter_channel,00001000b) 'configure counter

  P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

  mode = 0
  timer = 0
  sweep_index = 0
  processdelay = cycle_duration
  
  ' No documentation for this stuff at the top. FIX! --wp, Jun16
  Par_73 = repetition_counter
  PAR_23 = 0
  PAR_25 = 0
  
  PAR_60 = 0                      ' dummy par!!!
  par_68 = CR_probe
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' below CR threshold events
  PAR_72 = 0                      ' number of CR checks performed (lt2)
  PAR_73 = 0                      ' repetition counter
  PAR_74 = 0                      'MBI failed              
  par_75 = CR_preselect
  par_76 = 0                      ' cumulative counts during repumping
  PAR_77 = 0                      ' debug
  PAR_78 = 0                      ' MBI starts
  par_79 = 0                      ' cumulative LT2 counts in PSB during ssro sequence
  PAR_80 = 0                      ' RO_cntr
  
  current_cr_threshold = CR_preselect
  cr_counts = 0
  
EVENT:
  gate_good_phase = par_15*par_18-2*(par_19-1)
  CR_preselect = PAR_75
  CR_probe = PAR_68
  PAR_77 = mode
  
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
            current_cr_threshold = CR_preselect
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
                      
            IF (gate_good_phase > 0) THEN
              cr_counts = P2_CNT_READ(CTR_MODULE, counter_channel)
              PAR_70 = PAR_70 + cr_counts
              INC(PAR_72)
            ENDIF
            
            P2_CNT_ENABLE(CTR_MODULE, 0)
            
            IF (first > 0) THEN ' first CR after SSRO sequence
              DATA_23[1] = DATA_23[1] + cr_counts
              first = 0
            ENDIF
            IF (cr_counts < current_cr_threshold) THEN
              mode = 0
              if (current_cr_threshold < 999) THEN
                INC(CR_failed)
                PAR_71 = CR_failed
              ENDIF
              
              'PAR_25 = CR_preselect
              'PAR_26 = counts
            ELSE
              IF (gate_good_phase > 0) THEN
                P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
                P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
                DATA_22[1] = DATA_22[1] + cr_counts  ' CR before next SSRO sequence
                mode = 2
                current_cr_threshold = CR_probe
                'ELSE
                'mode = 0
              ENDIF
            ENDIF
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_SP_voltage+32768) ' turn on Ex laser
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
          old_counts = 0
        ELSE 
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          'DATA_24[timer] = DATA_24[timer] + counts - old_counts
          old_counts = counts
          IF (timer = SP_E_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE, 0)
            IF (SP_filter_duration = 0) THEN
              P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
              P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
              mode = 4
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
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
            counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            P2_CNT_ENABLE(CTR_MODULE, 0)
            IF (counts > 0) THEN
              mode = 1
            ELSE
              mode = 4
            ENDIF
            timer=-1
            wait_after_pulse = wait_after_pulse_duration
          ENDIF
        ENDIF
        
      CASE 4    ' MBI
        IF(timer=0) THEN 
          INC(MBI_starts) 
          PAR_78 = MBI_starts
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
        ENDIF
        IF (timer = wait_for_MBI_pulse) THEN
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        ELSE 
          IF (timer = stop_MBI) THEN
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
            counts = P2_CNT_READ(CTR_MODULE, counter_channel)
            
            IF (counts > (MBI_threshold-1)) THEN 'Check if MBI worked
              'Send event jump to AWG !!!!!!!!!!!!!!!!!
              P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
              CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)
              mode=5
              
            ELSE  
              INC(MBI_failed)
              PAR_74 = MBI_failed
              mode = 1 '(check resonance and start over)
            ENDIF
              
            P2_CNT_ENABLE(CTR_MODULE, 0)
            timer = -1
            wait_after_pulse = wait_after_pulse_duration +3
          ELSE
            ' In principle we can allready check for counts here!
          ENDIF
        ENDIF
        
      CASE 5    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
          old_counts = 0
        ELSE 
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts
          old_counts = counts
          IF (timer = SP_A_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE, 0)
            P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
            mode = 6
            wait_after_pulse = wait_after_pulse_duration            
            timer = -1
          ENDIF
        ENDIF  
      CASE 6    '  wait for AWG sequence or for fixed duration
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
                  mode = 7
                  timer = -1
                  wait_after_pulse = 0
                ENDIF
              ENDIF
            ELSE
              IF (timer - aux_timer >= sequence_wait_time) THEN
                mode = 7
                timer = -1
                wait_after_pulse = 0
              ENDIF
            ENDIF
          ELSE
            IF (timer >= sequence_wait_time) THEN
              mode = 7
              timer = -1
              wait_after_pulse = 0
              'ELSE
              'CPU_SLEEP(9)
            ENDIF
          ENDIF
        ENDIF
      
      CASE 7    ' spin readout
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        ELSE 
          IF ((timer = RO_duration) OR (P2_CNT_READ(CTR_MODULE, counter_channel) > 0)) THEN
          'IF (timer = RO_duration) THEN
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 32768) ' turn off Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 32768) ' turn off A laser
            
          PAR_60 = PAR_60 + P2_CNT_READ(CTR_MODULE, counter_channel) 'total spin-RO counts
            
          counts = P2_CNT_READ(CTR_MODULE, counter_channel) - old_counts
          old_counts = counts
            
          i = sweep_length*RO_cntr+sweep_index+1
          IF (P2_CNT_READ(CTR_MODULE, counter_channel) > 0) THEN
            DATA_27[i] = DATA_27[i] + 1
          ENDIF
          inc(RO_cntr)
          PAR_80 = i

          PAR_79 = PAR_79 + counts
            
           
          P2_CNT_ENABLE(CTR_MODULE, 0)

          IF (RO_cntr=nr_of_RO_steps) THEN
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
            RO_cntr=0
          ELSE
            mode = 5
            timer=-1
          ENDIF
            
        ELSE
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
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

