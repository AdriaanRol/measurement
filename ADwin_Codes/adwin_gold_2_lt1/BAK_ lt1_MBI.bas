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
' MBI with the adwin, with dynamic CR-preparation, dynamic MBI-success/fail
' recognition, and SSRO at the end. 
'
' protocol:
' 
' modes:
'   0 : Green repump
'   1 : E/A CR check
'   2 : E spin pumping into ms=0
'   3 : MBI
'   4 : A-pumping
'   5 : wait for AWG
'   6 : spin-readout
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
'   7       green_repump_duration       (durations in process cycles)
'   8       CR_duration 
'   9       SP_E_duration               (pumping time into +/-1 at the beginning)
'  10       wait_after_pulse_duration   (waiting time after MBI AWG pulse ??)
'  11       CR_preselect                (count threshold right after repump)
'  12       RO_repetitions              
'  13       sweep_length                (= number of data points)
'  14       cycle_duration              (in processor clock cycles, 3.333ns)
'  15       CR_probe                    (count threshold after surpassing the threshold in the prev. rd.)
'  16       AWG_event_jump_DO_channel
'  17       MBI_duration                (duration of the MBI pulse (so far Adwin AOM pulse))
'  18       wait_for_MBI_pulse          (how long to wait before assuming the AWG mbi pulse is done)
'  19       MBI_threshold               (photon threshold to assume success (given n, >= n is accepted))
'  20       nr_of_ROsequences           (how many sequences we run after MBI, each of them can contain pumping back on A and readout on E)
'  21       wait_after_RO_pulse_duration

' float parameters: DATA_21[i]
' index i   description
'   1       green_repump_voltage
'   2       green_off_voltage
'   3       Ex_CR_voltage
'   4       A_CR_voltage
'   5       Ex_SP_voltage
'   6       Ex_MBI_voltage

' return values:
' Data_22[1]                 CR counts before sequence
' Data_23[1]                 CR counts after sequence
' Data_24[SP_duration]                 time dependence SP
' Data_25[RO_duration]                 spin readout
' Data_26[...]                         statistics
'   1   repumps
'   XXX 2   CR_failed
'   XXX 3   CR_failed

#INCLUDE ADwinGoldII.inc

#DEFINE max_SP_bins       500
#DEFINE max_RO_dim    1000000
#DEFINE max_stat           10
#DEFINE max_sequences     100

DIM DATA_20[35] AS LONG                           ' integer parameters
DIM DATA_21[10] AS FLOAT                          ' float parameters
DIM DATA_22[1] AS LONG AT EM_LOCAL                ' CR counts before sequence
DIM DATA_23[1] AS LONG AT EM_LOCAL                ' CR counts after sequence
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL         ' statistics
DIM DATA_27[max_RO_dim] AS LONG AT DRAM_EXTERN    ' SSRO counts
DIM DATA_28[max_sequences] AS LONG                ' A SP durations
DIM DATA_29[max_sequences] AS LONG                ' E RO durations
DIM DATA_30[max_sequences] AS FLOAT               ' A SP voltages
DIM DATA_31[max_sequences] AS FLOAT               ' E RO voltages
DIM DATA_32[max_sequences] AS LONG                ' send AWG start
DIM DATA_33[max_sequences] AS LONG                ' wait for AWG done
DIM DATA_34[max_sequences] AS LONG                ' sequence wait times
' DIM DATA_35[max_sequences] AS LONG                ' sequence RO_repetitions

DIM counter_channel AS LONG
DIM green_laser_DAC_channel AS LONG
DIM Ex_laser_DAC_channel AS LONG
DIM A_laser_DAC_channel AS LONG
DIM AWG_start_DO_channel AS LONG
DIM AWG_event_jump_DO_channel AS LONG
DIM AWG_done_DI_channel AS LONG
DIM send_AWG_start AS LONG
' DIM wait_for_AWG_done AS LONG
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
DIM A_SP_duration AS LONG
DIM MBI_threshold AS LONG
DIM nr_of_ROsequences AS LONG
DIM wait_after_RO_pulse_duration AS LONG

DIM green_repump_voltage AS FLOAT
DIM green_off_voltage AS FLOAT
DIM Ex_CR_voltage AS FLOAT
DIM A_CR_voltage AS FLOAT
DIM Ex_SP_voltage AS FLOAT
DIM A_SP_voltage AS FLOAT
DIM Ex_RO_voltage AS FLOAT
DIM A_RO_voltage AS FLOAT
DIM Ex_MBI_voltage AS FLOAT

DIM timer, mode, i AS LONG
' DIM aux_timer AS LONG
' DIM AWG_done AS LONG
DIM wait_time AS LONG
DIM repetition_counter AS LONG
DIM repumps AS LONG
' DIM CR_failed AS LONG
DIM MBI_failed AS LONG
' DIM total_repump_counts AS LONG
DIM counter_pattern AS LONG
DIM counts AS LONG
DIM first AS LONG
' DIM sweep_index AS LONG
DIM stop_MBI AS LONG
DIM MBI_starts AS LONG
DIM ROseq_cntr AS LONG
' dim seq_reps as long
' dim seq_rep_cntr as long

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
  green_repump_duration        = DATA_20[7]
  CR_duration                  = DATA_20[8]
  SP_E_duration                = DATA_20[9]
  wait_after_pulse_duration    = DATA_20[10]
  CR_preselect                 = DATA_20[11]
  RO_repetitions               = DATA_20[12]
  sweep_length                 = DATA_20[13]
  cycle_duration               = DATA_20[14]
  CR_probe                     = DATA_20[15]
  AWG_event_jump_DO_channel    = DATA_20[16]
  MBI_duration                 = DATA_20[17]
  wait_for_MBI_pulse           = DATA_20[18]
  MBI_threshold                = DATA_20[19]
  nr_of_ROsequences            = DATA_20[20]
  wait_after_RO_pulse_duration = DATA_20[21]
  
  green_repump_voltage         = DATA_21[1]
  green_off_voltage            = DATA_21[2]
  Ex_CR_voltage                = DATA_21[3]
  A_CR_voltage                 = DATA_21[4]
  Ex_SP_voltage                = DATA_21[5]
  Ex_MBI_voltage               = DATA_21[6]
  
  DATA_22[1] = 0
  DATA_23[1] = 0
  
  FOR i = 1 TO max_RO_dim
    DATA_27[i] = 0
  NEXT i
  
  FOR i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT i
  
  counter_pattern     = 2 ^ (counter_channel-1)
  ' CR_failed           = 0
  MBI_failed          = 0
  MBI_starts          = 0
  repumps             = 0
  repetition_counter  = 0
  first               = 0
  wait_time           = 0
  stop_MBI            = wait_for_MBI_pulse + MBI_duration
  ROseq_cntr          = 1
  par_80 = ROseq_cntr
      
  dac(green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
  dac(Ex_laser_DAC_channel, 32768) ' turn off Ex laser
  dac(A_laser_DAC_channel, 32768) ' turn off Ex laser

  cnt_enable(0000b)'turn off all counters
  cnt_mode(counter_channel,00001000b) 'configure counter

  conf_dio( 13)      'configure DIO 08:15 as input, all other ports as output
  digout(AWG_start_DO_channel,0)

  mode = 0
  timer = 0
  ' sweep_index = 0
  processdelay = cycle_duration
  
  ' init parameters
  ' Y after the comment means I (wolfgang) checked whether they're actually used
  ' during the modifications of 2013/01/11
  par_68 = CR_probe               ' Y
  PAR_70 = 0                      ' cumulative counts from probe intervals Y
  PAR_71 = 0                      ' below CR threshold events Y
  PAR_72 = 0                      ' number of CR checks performed Y
  PAR_73 = 0                      ' repetition counter
  PAR_74 = 0                      ' MBI failed Y
  par_75 = CR_preselect           ' Y
  par_76 = 0                      ' cumulative counts during repumping Y
  PAR_77 = 0                      ' current mode Y
  PAR_78 = 0                      ' MBI starts Y
  par_79 = 0                      ' timer Y
  PAR_80 = 0                      ' ROseq_cntr Y 
  
  ' some for debugging
  par_60 = 0
  par_61 = 0
  par_62 = 0
  par_63 = 0
  
  current_cr_threshold = CR_preselect
  cr_counts = 0
  
EVENT:
  
  ' communication with the outside world for user convenience
  CR_preselect = PAR_75
  CR_probe = PAR_68
  PAR_77 = mode
  
  IF (wait_time > 0) THEN
    wait_time = wait_time - 1
  ELSE
    
    SELECTCASE mode
      
      CASE 0    ' green repump
        
        ' turn on the green laser and start counting
        IF (timer = 0) THEN
          cnt_clear(counter_pattern)    'clear counter
          cnt_enable(counter_pattern)	  'turn on counter
          dac(green_laser_DAC_channel, 3277*green_repump_voltage+32768) ' turn on green
          repumps = repumps + 1
        
        ELSE 
          
          ' turn off the green laser and get the counts
          ' in any case, we proceed to the CR checking
          IF (timer = green_repump_duration) THEN
            dac( green_laser_DAC_channel, 3277*green_off_voltage+32768) ' turn off green
            counts = cnt_read( counter_channel)
            cnt_enable(0)
            par_76 = par_76 + counts
            mode = 1
            timer = -1
            wait_time = wait_after_pulse_duration
            current_cr_threshold = CR_preselect
          ENDIF
        
        ENDIF
      
      CASE 1    ' Ex/A laser CR check
        
        ' turn on both lasers and start counting
        IF (timer = 0) THEN
          dac( Ex_laser_DAC_channel, 3277*Ex_CR_voltage+32768) ' turn on Ex laser
          dac( A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          cnt_clear(  counter_pattern)    'clear counter
          cnt_enable( counter_pattern)	  'turn on counter
          
        ELSE 
          
          ' turn off the lasers, and read the counter
          ' let the user know the accumulated counts and how often we checked
          IF (timer = CR_duration) THEN
            cr_counts = cnt_read(counter_channel)
            cnt_enable(0)
            PAR_70 = PAR_70 + cr_counts
            INC(PAR_72)
            
            dac( Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            dac( A_laser_DAC_channel, 32768) ' turn off A laser
            DATA_22[1] = DATA_22[1] + cr_counts  ' CR before next SSRO sequence
                        
            ' if it's the first attempt after a full sequence, we save it.
            ' this allows post-selection on events that where still non-ionized/on resonance
            ' after the run
            IF (first > 0) THEN ' first CR after SSRO sequence
              DATA_23[1] = DATA_23[1] + cr_counts
              first = 0
            ENDIF
            
            ' if the counts are below the threshold, we go back to green repumping
            IF (cr_counts < current_cr_threshold) THEN
              mode = 0
              
              ' if the threshold is 999 or above, this means we ignore it (good for debugging/tuning)
              ' if (current_cr_threshold < 999) THEN
              '  ' INC(CR_failed)
              '  PAR_71 = par_71 + 1
              ' ENDIF
            
              ' else, we proceed to pumping on the E line, into m_s = +/-1,
              ' and set the threshold to probing
            else
              mode = 2
              current_cr_threshold = CR_probe
            ENDIF
                        
            timer = -1
            wait_time = wait_after_pulse_duration
          ENDIF
        ENDIF
      
      CASE 2    ' E spin pumping
        
        ' turn on both lasers and start counting
        IF (timer = 0) THEN
          dac( Ex_laser_DAC_channel, 3277*Ex_SP_voltage+32768) ' turn on Ex laser
          cnt_clear(  counter_pattern)    'clear counter
          cnt_enable( counter_pattern)	  'turn on counter
        
        ELSE 
          ' counts = cnt_read( counter_channel)
          
          ' turn off the lasers, and read the counter
          IF (timer = SP_E_duration) THEN
            cnt_enable(0)
            dac( Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            dac( A_laser_DAC_channel, 32768) ' turn off A laser
            
            mode = 3
            wait_time = wait_after_pulse_duration
            timer = -1
          ENDIF
        ENDIF
              
      CASE 3    ' MBI
        
        ' MBI starts now; we first need to trigger the AWG to do the selective pi-pulse
        ' then wait until we can assume this is done
        IF(timer=0) THEN 
          INC(MBI_starts) 
          PAR_78 = MBI_starts
          digout(AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          digout(AWG_start_DO_channel,0)
        
        else
          ' we expect a trigger from the AWG once it has done the MW pulse
          ' as soon as we assume the AWG has done the MW pulse, we turn on the E-laser,
          ' and start counting
          if((digin_edge(0) AND 2^AWG_done_DI_channel) > 0) then
            stop_MBI = timer + MBI_duration + 1
            
            cnt_clear(  counter_pattern)    'clear counter
            cnt_enable( counter_pattern)	  'turn on counter
            dac( Ex_laser_DAC_channel, 3277*Ex_MBI_voltage+32768) ' turn on Ex laser
          else
                        
            ' MBI readout finished: turn off laser, read counter
            IF (timer = stop_MBI) THEN
              dac( Ex_laser_DAC_channel, 32768) ' turn off Ex laser
              counts = cnt_read( counter_channel)
              cnt_enable(0)
            
              ' MBI succeeds if the counts surpass the threshold;
              ' we then trigger an AWG jump (sequence has to be long enough!) and move on to SP on A
              IF (counts > (MBI_threshold-1)) THEN
                digout(AWG_event_jump_DO_channel,1)  ' AWG trigger
                CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
                digout(AWG_event_jump_DO_channel,0)
                mode = 4
            
                ' if MBI failes we continue with checking CR again
              ELSE  
                INC(MBI_failed)
                PAR_74 = MBI_failed
                mode = 1 '(check resonance and start over)
              ENDIF

              timer = -1
              wait_time = wait_after_pulse_duration ' + 3
            ENDIF          
          endif
        ENDIF
        
      CASE 4    ' A laser spin pumping
        A_SP_voltage = DATA_30[ROseq_cntr]
        A_SP_duration = DATA_28[ROseq_cntr]
       
        ' turn on A laser; we don't need to count here for the moment
        IF (timer = 0) THEN
          dac(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   
        
        ELSE 
          
          ' when we're done, turn off the laser and proceed to the sequence
          IF (timer = A_SP_duration) THEN
            dac( Ex_laser_DAC_channel, 32768) ' turn off Ex laser
            dac( A_laser_DAC_channel, 32768) ' turn off A laser
            wait_time = wait_after_pulse_duration
            
            mode = 5
            timer = -1
          ENDIF
        ENDIF      
      
      CASE 5    '  wait for AWG sequence or for fixed duration
        send_AWG_start = DATA_32[ROseq_cntr]
        sequence_wait_time = DATA_34[ROseq_cntr]
        
        ' two options: either run an AWG sequence...
        if(send_AWG_start > 0) then
          IF (timer = 0) THEN
            digout(AWG_start_DO_channel, 1)  ' AWG trigger
            CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            digout(AWG_start_DO_channel, 0)
          else            
            ' we wait for the sequence to be finished. the AWG needs to tell us by a pulse,
            ' of which we detect the falling edge.
            ' we then move on to readout
            if((digin_edge(0) AND 2^AWG_done_DI_channel) > 0) then
              mode = 6
              timer = -1
              wait_time = 0
            endif         
          
          ENDIF
        
        else       
          ' if we do not run an awg sequence, we just wait the specified time, and go then to readout
          mode = 6
          timer = -1
          wait_time = sequence_wait_time       
        endif
        
        
      CASE 6    ' readout on the E line
        RO_duration = DATA_29[ROseq_cntr]
        Ex_RO_Voltage = DATA_31[ROseq_cntr]
        
        IF (timer = 0) THEN
          cnt_clear(counter_pattern)    'clear counter
          cnt_enable(counter_pattern)	  'turn on counter
          dac(Ex_laser_DAC_channel, 3277 * Ex_RO_voltage + 32768) ' turn on Ex laser
        
        ELSE
          counts = cnt_read( counter_channel)          
          
          IF ((timer = RO_duration) OR counts > 0) THEN
            dac(Ex_laser_DAC_channel, 32768) ' turn off Ex laser

            i = repetition_counter + 1 'sweep_length*(ROseq_cntr-1)+sweep_index+1
            IF (counts > 0) THEN
              DATA_27[i] = DATA_27[i] + 1
            ENDIF
                    
            wait_time = wait_after_RO_pulse_duration
            cnt_enable(0)
           
            inc(ROseq_cntr)
            par_80 = ROseq_cntr
            
            IF (ROseq_cntr = nr_of_ROsequences+1) THEN ' this means we're done with one full run
              mode = 1
              timer = -1

              'INC(sweep_index) ' set the new sweep index (only needed for saving data)
              'IF (sweep_index = sweep_length) THEN
              'sweep_index = 0              
              'ENDIF
            
              repetition_counter = repetition_counter + 1
              Par_73 = repetition_counter 
              
              ' we're done once we're at the last repetition and the last RO step
              IF (repetition_counter = RO_repetitions) THEN
                END
              ENDIF
                
              first = 1
              ROseq_cntr = 1
              
            ELSE ' means we're starting the next ROsequence
              mode = 4
              timer = -1
            ENDIF
          ENDIF
        endif
    endselect
    
    timer = timer + 1
    par_79 = timer
    
  endif
  
FINISH:
  DATA_26[1] = repumps
  ' DATA_26[2] = total_repump_counts
  ' DATA_26[3] = CR_failed

