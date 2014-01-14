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
' Info_Last_Save                 = TUD277246  TUD277246\localadmin
'<Header End>
' MBI with the adwin, with dynamic CR-preparation, dynamic MBI-success/fail
' recognition, and SSRO at the end. 
'
' protocol:
' 
' modes:
'   0 : CR check
'   2 : E spin pumping into ms=0
'   3 : MBI
'   4 : A-pumping
'   5 : wait for AWG
'   6 : spin-readout
'

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc

#DEFINE max_SP_bins       500 ' not used anymore? Machiel 23-12-'13
#DEFINE max_sequences     100
#DEFINE max_time        10000
#DEFINE max_mbi_steps     100

'init
DIM DATA_20[100] AS LONG                           ' integer parameters
DIM DATA_21[100] AS FLOAT                          ' float parameters
DIM DATA_33[max_sequences] AS LONG                ' A SP durations
DIM DATA_34[max_sequences] AS LONG                ' E RO durations
DIM DATA_35[max_sequences] AS FLOAT               ' A SP voltages
DIM DATA_36[max_sequences] AS FLOAT               ' E RO voltages
DIM DATA_37[max_sequences] AS LONG                ' send AWG start
DIM DATA_38[max_sequences] AS LONG                ' sequence wait times

'return
DIM DATA_24[max_repetitions] AS LONG ' number of MBI attempts needed in the successful cycle
DIM DATA_25[max_repetitions] AS LONG ' number of cycles before success
DIM DATA_27[max_repetitions] AS LONG ' SSRO counts
DIM DATA_28[max_repetitions] AS LONG ' time needed until mbi success (in process cycles)

DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_event_jump_DO_channel AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM A_SP_duration, SP_E_duration, SP_filter_duration, MBI_duration AS LONG
DIM sequence_wait_time, wait_after_pulse_duration AS LONG
DIM RO_repetitions, RO_duration AS LONG
DIM cycle_duration AS LONG
DIM sweep_length AS LONG
DIM wait_for_MBI_pulse AS LONG
DIM MBI_threshold AS LONG
DIM nr_of_ROsequences AS LONG
DIM wait_after_RO_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM E_MBI_voltage AS FLOAT
dim E_N_randomize_voltage, A_N_randomize_voltage, repump_N_randomize_voltage AS FLOAT

DIM timer, mode, i, tmp AS LONG
DIM wait_time AS LONG
DIM repetition_counter AS LONG
dim seq_cntr as long
DIM MBI_failed AS LONG
DIM counts AS LONG
DIM first AS LONG
DIM stop_MBI AS LONG
DIM MBI_starts AS LONG
DIM ROseq_cntr AS LONG

' MBI stuff
dim next_MBI_stop, next_MBI_laser_stop as long
dim current_MBI_attempt as long
dim MBI_attempts_before_CR as long
dim mbi_timer as long
dim trying_mbi as long
dim N_randomize_duration as long

dim awg_in_is_hi, awg_in_was_hi, awg_in_switched_to_hi as long

INIT:
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  SP_E_duration                = DATA_20[3]
  wait_after_pulse_duration    = DATA_20[4]
  RO_repetitions               = DATA_20[5]
  sweep_length                 = DATA_20[6] ' not used? -machiel 23-12-'13
  cycle_duration               = DATA_20[7]
  AWG_event_jump_DO_channel    = DATA_20[8]
  MBI_duration                 = DATA_20[9]
  MBI_attempts_before_CR       = DATA_20[10]
  MBI_threshold                = DATA_20[11]
  nr_of_ROsequences            = DATA_20[12]
  wait_after_RO_pulse_duration = DATA_20[13]
  N_randomize_duration         = DATA_20[14]
  
  E_SP_voltage                 = DATA_21[1]
  E_MBI_voltage                = DATA_21[2]  
  E_N_randomize_voltage        = DATA_21[3]
  A_N_randomize_voltage        = DATA_21[4]
  repump_N_randomize_voltage   = DATA_21[5]
  
  ' initialize the data arrays
  FOR i = 1 TO max_repetitions
    DATA_24[i] = 0
    DATA_25[i] = 0
    DATA_28[i] = 0
    DATA_27[i] = 0
  NEXT i
        
  MBI_failed          = 0
  MBI_starts          = 0
  repetition_counter  = 1
  first               = 0
  wait_time           = 0
  stop_MBI            = -2 ' wait_for_MBI_pulse + MBI_duration
  ROseq_cntr          = 1
  seq_cntr            = 1
  
  next_MBI_stop = -2
  current_MBI_attempt = 1
  next_MBI_laser_stop = -2
      
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,00001000b) 'configure counter

  P2_Digprog(DIO_MODULE,11) ' in  is now 16:23   'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  
  tmp = P2_Digin_Edge(DIO_MODULE,0)
  mode = 0
  timer = 0
  mbi_timer = 0
  trying_mbi = 0
  processdelay = cycle_duration
  
  awg_in_is_hi = 0
  awg_in_was_hi = 0
  awg_in_switched_to_hi = 0
  
  ' init parameters
  ' Y after the comment means I (wolfgang) checked whether they're actually used
  ' during the modifications of 2013/01/11
  PAR_73 = 0                      ' repetition counter
  PAR_74 = 0                      ' MBI failed Y
  PAR_77 = 0                      ' current mode Y
  PAR_78 = 0                      ' MBI starts Y
  PAR_80 = 0                      ' ROseq_cntr Y 
  
EVENT:
 
  awg_in_was_hi = awg_in_is_hi
  awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_channel)
  
  if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
    awg_in_switched_to_hi = 1
  else
    awg_in_switched_to_hi = 0
  endif
    
  PAR_77 = mode
  
  if(trying_mbi > 0) then
    inc(mbi_timer)
  endif   
  
  IF (wait_time > 0) THEN
    wait_time = wait_time - 1
  ELSE
    
    SELECTCASE mode
           
      CASE 0 'CR check
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 2 
          timer = -1 
          first = 0 
        ENDIF 
      
      CASE 2    ' E spin pumping
        
        ' turn on both lasers and start counting
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
        
        ELSE          
          ' turn off the lasers, and read the counter
          IF (timer = SP_E_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE,0)
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            
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
                       
          if (current_MBI_attempt = 1) then
            if(data_25[seq_cntr] = 0) then
              trying_mbi = 1
            endif
            INC(data_25[seq_cntr]) ' number of cycles to success
          endif
          
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
       
          ' make sure we don't accidentally think we're done before getting the trigger
          next_MBI_stop = -2
        
        else
          ' we expect a trigger from the AWG once it has done the MW pulse
          ' as soon as we assume the AWG has done the MW pulse, we turn on the E-laser,
          ' and start counting
          if(awg_in_switched_to_hi > 0) then
            
            next_MBI_stop = timer + MBI_duration
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_MBI_voltage+32768) ' turn on Ex laser
                      
          else            
            IF (timer = next_MBI_stop) THEN
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              counts = P2_CNT_READ(CTR_MODULE, counter_channel)
              P2_CNT_ENABLE(CTR_MODULE,0)
                              
              ' MBI succeeds if the counts surpass the threshold;
              ' we then trigger an AWG jump (sequence has to be long enough!) and move on to SP on A
              ' if MBI fails, we
              ' - try again (until max. number of attempts, after some scrambling)
              ' - go back to CR checking if max number of attempts is surpassed
              
              IF (counts < MBI_threshold) THEN
                INC(MBI_failed)
                PAR_74 = MBI_failed
      
                if (current_MBI_attempt = MBI_attempts_before_CR) then
                  current_cr_threshold = cr_preselect
                  mode = 0 '(check resonance and start over)
                  current_MBI_attempt = 1
                else
                  mode = 7
                  INC(current_MBI_attempt)
                endif                
                timer = -1      
              
              else               
                P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
                CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
                P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)
                
                DATA_24[seq_cntr] = current_MBI_attempt ' number of attempts needed in the successful cycle
                mode = 4
                current_MBI_attempt = 1
                trying_mbi = 0
                ' we want to save the time MBI takes
                DATA_28[seq_cntr] = mbi_timer
                mbi_timer = 0
              
              endif
              timer = -1
            endif          
          endif
        ENDIF
        
      CASE 4    ' A laser spin pumping
        A_SP_voltage = DATA_35[ROseq_cntr]
        A_SP_duration = DATA_33[ROseq_cntr]
       
        ' turn on A laser; we don't need to count here for the moment
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768)
        ELSE 
          
          ' when we're done, turn off the laser and proceed to the sequence
          IF (timer = A_SP_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            wait_time = wait_after_pulse_duration
            
            mode = 5
            timer = -1
          ENDIF
        ENDIF      
      
      CASE 5    '  wait for AWG sequence or for fixed duration
        send_AWG_start = DATA_37[ROseq_cntr]
        sequence_wait_time = DATA_38[ROseq_cntr]
        
        IF (timer = 0) THEN

        endif       
       
        ' two options: either run an AWG sequence...
        if(send_AWG_start > 0) then
          
          IF (timer = 0) THEN
            P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel, 1)  ' AWG trigger
            CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel, 0)          
          else
            
            ' we wait for the sequence to be finished. the AWG needs to tell us by a pulse,
            ' of which we detect the falling edge.
            ' we then move on to readout
            if(awg_in_switched_to_hi > 0) then          
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
        RO_duration = DATA_34[ROseq_cntr]
        E_RO_Voltage = DATA_36[ROseq_cntr]
        
        IF (timer = 0) THEN
          
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277 * E_RO_voltage + 32768) ' turn on Ex laser
        
        ELSE
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          
          IF ((timer = RO_duration) OR counts > 0) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser

            IF (counts > 0) THEN
              i = repetition_counter
              INC(DATA_27[i])
            ENDIF
                    
            wait_time = wait_after_RO_pulse_duration
            P2_CNT_ENABLE(CTR_MODULE,0)
                        
            INC(ROseq_cntr)
            par_80 = ROseq_cntr
            
            INC(repetition_counter)
            Par_73 = repetition_counter
                      
            IF (ROseq_cntr = nr_of_ROsequences+1) THEN ' this means we're done with one full run
              INC(seq_cntr)
              mode = 0
              timer = -1                
              first = 1
              ROseq_cntr = 1
              
              ' we're done once we're at the last repetition and the last RO step
              IF (repetition_counter = RO_repetitions+1) THEN
                DEC(repetition_counter)
                Par_73 = repetition_counter
                END
              ENDIF
                 
            ELSE
              ' means we're starting the next ROsequence
              mode = 4
              timer = -1
            ENDIF
          ENDIF
        endif
        
      case 7 ' turn on the lasers to (hopefully) randomize the N-spin state before re-trying MBI
        
        if (timer = 0) then
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_N_randomize_voltage+32768)
        else
          if (timer = N_randomize_duration) then
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768)
            P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_off_voltage+32768)
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_off_voltage+32768)
            
            mode = 2
            timer = -1
            wait_time = wait_after_pulse_duration
          endif                    
        endif
                  
    endselect
    
    INC(timer)
    
  endif
  
    
FINISH:
  finish_CR()

