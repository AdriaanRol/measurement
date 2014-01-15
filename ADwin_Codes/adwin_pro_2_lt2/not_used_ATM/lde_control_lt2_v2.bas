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
' TODO: elegant solution for switching between local / local+remote
' TODO: change lt1-checks to edge detect


' only DIO 1-24 are connected to breakout box (no 0, 25-31)

' LDE master controller program

' modes:
' 0 : do local charge and resonance check
' 1 : do local repumping
' 2 : local CR OK, wait for remote
' 3 : run LDE
' 4 : SSRO

' remote modes:
' 0 : start remote CR check
' 1 : remote CR check running
' 2 : remote CR OK, waiting
' 3 : SSRO

'
' Resources used:
'
' PARs:
' =====
' Inputs:
' 18 : sync gate to modulator (state of the gate)
' 19 : set to 1 if gate should be synced
' 75 : CR threshold (after preparation with green)
' 68 : CR threshold (already prepared)

' Outputs:
' 65 : Number of raw edges detected on PLU DI
' 67 : number of ROs performed
' 69 : cumulative LT1 counts in PSB during tpqi sequence
' 70 : cumulative counts from probe intervals
' 71 : below CR threshold events
' 72 : number of CR checks performed (lt2)
' 73 : number of sequence starts
' 74 : number of non-interrupted sequence runs 
' 76 : cumulative counts during repumping
' 77 : number of OK signals from LT1
' 79 : cumulative LT2 counts in PSB during tpqi sequence
' 80 : number of start triggers to LT1
' 

' FPARs:
' ======
' Inputs:


' DATA:
' =====
' Inputs:
' DATA_20: integer parameters
'   1 : counter
'   2 : green aom channel
'   3 : E aom channel
'   4 : A aom channel
'   5 : CR check steps (no of process cycles)
'   6 : CR threshold (after preparation with green)
'   7 : CR threshold (already prepared)
'   8 : repump steps
'   9 : wait before SSRO (process cycles)
'  10 : SSRO time (process cycles)
'  11 : LDE time before CR check force (process cycles)
'  12 : AWG start DO channel
'  13 : PLU arm DO channel
'  14 : Trigger remote CR DO
'  15 : Remote CR done DI-bit
'  16 : Trigger remote SSRO DO
'  17 : PLU success DI-bit
'  18 : PLU state DI-bit

' DATA_21: float parameters
'   1 : green repump voltage
'   2 : green offset voltage (0V != no laser output)
'   3 : E CR voltage
'   4 : A CR voltage
'   5 : E RO voltage
'   6 : A RO voltage

' Outputs:
' DATA_7[-max_hist_cts] (int) : CR count histogram after unsuccessful entanglement attempts
' DATA_8[-max_hist_cts] (int) : CR count histogram after all attempts
' DATA_22 (int) : SSRO results
' DATA_23 (int) : CR counts
' DATA_24 (int) : PLU Gate results
' DATA_25 (int) : Gate phase at time of SSRO

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' parameters
DIM DATA_20[20] AS LONG               ' integer parameters
DIM DATA_21[6] AS FLOAT              ' float parameters

' general variables
DIM i as long ' counter for array initalization
dim mode as integer
dim remote_mode as integer
dim timer as long

' accumulation of statistics during CR
#define max_hist_cts 100                ' dimension of photon counts histogram for CR
DIM DATA_7[max_hist_cts] as long       ' histogram of counts during 1st CR after interference sequence
DIM DATA_8[max_hist_cts] as long       ' histogram of counts during CR (all attempts)

' settings for CR checks and repumping
DIM counter AS LONG                     ' select internal ADwin counter 1 - 4 for conditional readout (PSB lt2)
DIM green_aom_channel AS LONG           ' DAC channel for green laser AOM
DIM green_voltage AS Float              ' voltage of repump pulse
DIM green_off_voltage AS Float          ' off-voltage of green (0V is not 0W)
dim ex_aom_channel as long
dim ex_cr_voltage as Float
dim a_aom_channel as long
dim a_cr_voltage as Float
dim cr_check_steps as long                      ' how long to check, in units of process cycles (lt2)
dim current_cr_check_counts as long             ' accumulated CR counts (lt2)
dim cr_check_count_threshold_prepare as long    ' initial C&R threshold after repump (lt2)
dim cr_check_count_threshold_probe as long      ' C&R threshold for probe after sequence (lt2)
dim repump_steps as long                        ' how long to rempump w/ green, in process cycles (lt2)
dim current_cr_threshold as long
dim first_cr_probe_after_lde as integer
dim cr_after_ssro as integer 
dim write_to_array as integer

' remote stuff on lt1
dim is_cr_lt1_OK, was_cr_lt1_OK as integer
dim trigger_cr_dio_in_bit as long
dim trigger_cr_dio_out as long
dim trigger_ssro_dio_out as long
dim RO_steps_lt1 as long
dim cr_check_steps_lt1 as long
' LDE sequence
dim max_lde_time as long
DIM AWG_start_DO_channel AS LONG
dim PLU_arm_DO_channel as LONG
dim PLU_success_dio_in_bit as long
dim PLU_state_dio_in_bit as long
dim is_PLU_success, was_PLU_success as integer

' SSRO
#define max_readouts 500000
dim wait_before_RO as long ' how many cycles to wait before SSRO (to make sure rotations etc are finished)
dim DATA_22[max_readouts] as long
dim DATA_23[max_readouts] as long
dim DATA_24[max_readouts] as long
dim DATA_25[max_readouts] as long
dim RO_event_idx as long
dim RO_counts as long
dim ex_ro_voltage as float
dim a_ro_voltage as float
dim RO_steps as long

' misc
DIM counter_pattern AS LONG
DIM DIO_register AS Long
DIM PLU_trigger_received AS LONG
DIM PLU_state AS LONG
DIM gate_good_phase AS LONG

'debug
Dim timervalue1 as Long
dim timervalue2 as long

dim A as long

INIT:
  ' general
  mode = 0
  remote_mode = 0
  timer = 0
  cr_after_ssro = 0
  write_to_array = 0
  ' init statistics variables
  for i=1 to max_hist_cts
    DATA_7[i] = 0
    DATA_8[i] = 0
  next i

  ' init CR check variables
  counter = data_20[1]
  green_aom_channel = data_20[2]
  ex_aom_channel = data_20[3]
  a_aom_channel = data_20[4]
  cr_check_steps = data_20[5]
  cr_check_count_threshold_prepare = data_20[6]
  cr_check_count_threshold_probe = data_20[7]
  repump_steps = data_20[8]
   
  green_voltage = data_21[1]
  green_off_voltage = data_21[2] 
  ex_cr_voltage = data_21[3]
  a_cr_voltage = data_21[4]
  ex_ro_voltage = data_21[5]
  a_ro_voltage = data_21[6]
  
  current_cr_check_counts = 0
  current_cr_threshold = cr_check_count_threshold_prepare
  first_cr_probe_after_lde = 0
  
  ' remote stuff
  is_cr_lt1_OK = 0
  was_cr_lt1_OK = -1
  trigger_cr_dio_in_bit = data_20[15]
  trigger_cr_dio_out = data_20[14]
  trigger_ssro_dio_out = data_20[16]
  RO_steps_lt1 = data_20[19]
  cr_check_steps_lt1 = data_20[20] 
  
  ' LDE sequence
  max_lde_time = data_20[11]
  ' completed_lde_attempts = 0
  AWG_start_DO_channel = data_20[12]
  PLU_arm_DO_channel = data_20[13]
  PLU_success_dio_in_bit = data_20[17]
  PLU_state_dio_in_bit = data_20[18]
  is_PLU_success = 0
  
  ' SSRO
  wait_before_RO = data_20[9]
  RO_event_idx = 0
  RO_steps = data_20[10]
  PLU_state = -1
  
  for i=1 to max_readouts
    DATA_22[i] = -1
    DATA_23[i] = -1
    DATA_24[i] = -1
    DATA_25[i] = 0
  next i
  
  ' misc
  counter_pattern     = 2 ^ (counter-1)

  ' prepare hardware
  par_60 = 0                    'debug par used for measuring timer
  par_62 = 0                      'debug par used for measuring timer
  par_63 = 0                      'debug par 
  par_64 = 0                      'debug par
  
  par_68 = cr_check_count_threshold_probe
  par_69 = 0                      ' cumulative LT1 counts in PSB during lde sequence
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' below CR threshold events
  PAR_72 = 0                      ' number of CR checks performed (lt2)
  par_73 = 0                      ' number of lde starts
  par_74 = 0                      ' timed out lde attempts
  par_75 = cr_check_count_threshold_prepare
  par_76 = 0                      ' cumulative counts during repumping
  par_77 = 0                      ' number of OK signals from LT1
  par_79 = 0                      ' cumulative LT2 counts in PSB during lde sequence
  Par_80 = 0                      ' number of start cr triggers to LT1
  par_61 = 0                      ' number of start ssro triggers to LT1
  par_67 = 0                      ' number of readouts performed
  par_65 = 0                      ' Number of raw edges detected on PLU DI
    
  P2_DAC(DAC_MODULE, green_aom_channel, 3277*green_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, ex_aom_channel, 32768)
  P2_DAC(DAC_MODULE, a_aom_channel, 32768)
  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter,00001000b) 'configure counter
  P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,trigger_cr_dio_out,0)
  P2_DIGOUT(DIO_MODULE,trigger_ssro_dio_out,0)
  
  ' PLU-DO is high
  P2_DIGOUT(DIO_MODULE,PLU_arm_DO_channel,1)
  
  ' P2_DIGOUT(DIO_MODULE,6,0)

  timervalue1=0
  timervalue2=0
  Par_60=0
EVENT:
  
  timervalue1=timervalue2
  timervalue2=Read_timer()
  Par_60 = Max_long((timervalue2-timervalue1),Par_60)
  
  gate_good_phase = par_15*par_18-2*(par_19-1)
  
  cr_check_count_threshold_prepare = par_75
  cr_check_count_threshold_probe = par_68
  
  DIO_register = P2_DIGIN_EDGE(DIO_MODULE,1)
  PLU_trigger_received = ((DIO_register) AND (PLU_success_dio_in_bit))
  if (PLU_trigger_received >0) then
    inc(par_65)
    inc(RO_event_idx) 
  endif
  
  if (((DIO_register) AND (trigger_cr_dio_in_bit)) > 0) then
    inc(par_64)
    'if we want to prevent the problem that lt1 waits to long during the wrong gate phase, comment this out (has to be tested)
    'if gate_good_phase < 0 then
    '  remote_mode = 0 'keep checking LT1 while in bad gate phase
    'endif
  endif
  

  if (par_67 = max_readouts) then
    end
  endif
  
  ' If only one setup is used, remote_mode may be set to 2.
 
  
  selectcase remote_mode
    case 0 'send LT1 CR start signal
      Inc(Par_80)
      P2_DIGOUT(DIO_MODULE,trigger_cr_dio_out,1) ' trigger lt1 do to CR check
      remote_mode = 1
      
    case 1 'waiting for LT1 CR ok signal
      if (((DIO_register) AND (trigger_cr_dio_in_bit)) > 0) then
        remote_mode = 2
        P2_DIGOUT(DIO_MODULE,trigger_cr_dio_out,0) ' remover HI-trigger for lt1
        Inc(par_77)
      endif   
  
  endselect

  selectcase mode
    case 0 'do local charge and resonance check
      if (timer = 0) then

        P2_DIGOUT(DIO_MODULE,PLU_arm_DO_channel,1)
        
        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
        P2_CNT_ENABLE(CTR_MODULE, 1111b) ' enable counter
        
        P2_DAC(DAC_MODULE, ex_aom_channel, 3277*ex_cr_voltage+32768) ' turn on the Ex and A1 lasers
        P2_DAC(DAC_MODULE, a_aom_channel, 3277*a_cr_voltage+32768)
        
      endif

      if (timer >= cr_check_steps) then
        P2_CNT_LATCH(CTR_MODULE, 1111b)
        
        if (gate_good_phase > 0) then
          current_cr_check_counts = P2_CNT_READ_LATCH(CTR_MODULE, counter) 'NOTE here gets decided if green during bad phase
          par_70 = par_70 + current_cr_check_counts
          INC(PAR_72)
        endif
        
        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
        
        if (cr_after_ssro > 0) then 'this is to keep sync between the adwins after SSRO and CR_after_SSRO
          if (write_to_array > 0) then
            DATA_23[RO_event_idx] = current_cr_check_counts
            write_to_array = 0 'make sure that it does not write multiple times to same RO_events_idx: can occur if LT2 waits for LT1.
          endif
          P2_DAC(DAC_MODULE, ex_aom_channel, 32768) ' turn off the red lasers
          P2_DAC(DAC_MODULE, a_aom_channel, 32768)
          if ((timer > cr_check_steps ) and (timer > cr_check_steps_lt1)) then ' wait for both adwins to be finished with cr after ssro
            remote_mode = 0
            cr_after_ssro = 0
            timer = -1
            'Inc(par_60)
          endif
        else
          'Inc(par_72)
          if (current_cr_check_counts < current_cr_threshold) then
            mode = 1
            timer = -1
            Inc(par_71)
          else
            
            if (gate_good_phase > 0) then
              P2_DAC(DAC_MODULE, ex_aom_channel, 32768) ' turn off the red lasers
              P2_DAC(DAC_MODULE, a_aom_channel, 32768)
              mode = 2
              current_cr_threshold = cr_check_count_threshold_probe
            endif
            timer = -1
            
          endif

          if (current_cr_check_counts < max_hist_cts) then
            if (first_cr_probe_after_lde > 0) then
              Inc(DATA_7[current_cr_check_counts+1])
            endif
            if (gate_good_phase > 0) then
              Inc(DATA_8[current_cr_check_counts+1])
            endif
          endif
        
          first_cr_probe_after_lde = 0
        endif
      endif
      
        

    case 1 'do local repumping
      if (timer = 0) then
        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
        P2_CNT_ENABLE(CTR_MODULE, 1111b) ' enable counter
        P2_DAC(DAC_MODULE, green_aom_channel, 3277*green_voltage+32768)
      endif

      if (timer = repump_steps) then
        P2_DAC(DAC_MODULE, green_aom_channel, 3277*green_off_voltage+32768) ' turn off green
        P2_CNT_LATCH(CTR_MODULE, 1111b)
        par_76 = par_76 + P2_CNT_READ_LATCH(CTR_MODULE, counter)
        mode = 0
        timer = -1
        current_cr_threshold = cr_check_count_threshold_prepare
      endif

    case 2 'local CR OK, wait for remote

      if (remote_mode = 2) then
        if (gate_good_phase > 0) then
          mode = 3
        else 
          'remote_mode = 0
          mode = 0
        endif
        
        timer = -1
      endif
    
         
    case 3 ' run LDE sequence  
      P2_DIGOUT(DIO_MODULE,PLU_arm_DO_channel,0)

      if (timer = 0) then        
        P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
        CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0) 
        inc(par_73)     
      else

        if (PLU_trigger_received > 0) then
          PLU_state = ((DIO_register) AND (PLU_state_dio_in_bit))
          mode = 4
          timer = -1
          inc(par_67)
        else        
          if (timer = max_lde_time) then
            mode = 0
            remote_mode = 0
            timer = -1
            first_cr_probe_after_lde = 1
            inc(par_74)
          endif
        endif
      endif
        
        
      
    case 4 ' SSRO
            
      if (timer = wait_before_RO) then
        P2_DIGOUT(DIO_MODULE,trigger_ssro_dio_out,1) ' trigger lt1 do to SSRO
        inc(par_61)
        remote_mode = 3
        
        P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
        P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
        P2_DAC(DAC_MODULE, ex_aom_channel, 3277*ex_ro_voltage+32768) ' turn on Ex laser
        P2_DAC(DAC_MODULE, a_aom_channel, 3277*a_ro_voltage+32768) ' turn on A laser
      endif
      
      'write the state of the PLU
      if (timer = wait_before_RO+RO_steps-1) then
        data_24[RO_event_idx] = PLU_state
        PLU_state = -1 '-1 should not occur in the data, if it does, something is wrong with the progam flow
      endif
            
      if (timer = wait_before_RO+RO_steps) then
        P2_DIGOUT(DIO_MODULE,trigger_ssro_dio_out,0) ' remove trigger lt1 do to SSRO
      
        P2_DAC(DAC_MODULE, ex_aom_channel, 32768) ' turn off Ex laser
        P2_DAC(DAC_MODULE, a_aom_channel, 32768) ' turn off A laser
        
        data_22[RO_event_idx] = P2_CNT_READ(CTR_MODULE, counter)
        data_25[RO_event_idx] = gate_good_phase
        P2_CNT_ENABLE(CTR_MODULE, 0)
        'inc(RO_event_idx)  => moved to edge detection

      endif
      if ((timer > wait_before_RO+RO_steps) and (timer > wait_before_RO+RO_steps_lt1)) then ' making sure that SSRO is finished before new round starts
        mode = 0
        cr_after_ssro = 1
        write_to_array = 1
        timer = -1
      endif
          
      
  endselect
  
  timer = timer + 1

