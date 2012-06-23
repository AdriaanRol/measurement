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
' 75 : CR threshold (after preparation with green)
' 68 : CR threshold (already prepared)

' Outputs:
' 69 : cumulative LT1 counts in PSB during tpqi sequence
' 70 : cumulative counts from probe intervals
' 71 : below CR threshold events
' 72 : number of CR checks performed (lt2)
' 73 : number of sequence starts
' 74 : number of sequence runs interrupted
' 76 : cumulative counts during repumping
' 77 : number of OK signals from LT1
' 79 : cumulative LT2 counts in PSB during tpqi sequence
' 80 : number of start triggers to LT1
' 81 : number of ROs performed

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
'  13 : AWG done DI channel
'  14 : PLU arm DO channel
'  15 : Trigger remote CR DO
'  16 : Remote CR done DI-bit
'  17 : Trigger remote SSRO DO
'  18 : PLU success DI-bit

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

#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

' parameters
DIM DATA_20[18] AS LONG               ' integer parameters
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

' remote stuff on lt1
dim is_cr_lt1_OK, was_cr_lt1_OK as integer
dim trigger_cr_dio_in_bit as long
dim trigger_cr_dio_out as long
dim trigger_ssro_dio_out as long

' LDE sequence
dim max_lde_time as long
DIM AWG_done_DI_pattern AS LONG
DIM AWG_start_DO_channel AS LONG
DIM AWG_done_DI_channel AS LONG
dim PLU_arm_DO_channel as LONG
dim PLU_success_dio_in_bit as long
dim is_PLU_success, was_PLU_success as integer

' SSRO
#define max_readouts 10000
dim wait_before_RO as long ' how many cycles to wait before SSRO (to make sure rotations etc are finished)
dim DATA_22[max_readouts] as long
dim DATA_23[max_readouts] as long
dim RO_event_idx as long
dim RO_counts as long
dim ex_ro_voltage as float
dim a_ro_voltage as float
dim RO_steps as long

' misc
DIM counter_pattern AS LONG

INIT:

  ' general
  mode = 0
  remote_mode = 0
  
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
  
  current_cr_check_counts = 0
  current_cr_threshold = cr_check_count_threshold_prepare
  first_cr_probe_after_lde = 0
  
  ' remote stuff
  is_cr_lt1_OK = 0
  trigger_cr_dio_in_bit = data_20[16]
  trigger_cr_dio_out = data_20[15]
  trigger_ssro_dio_out = data_20[17]
  
  ' LDE sequence
  max_lde_time = data_20[11]
  ' completed_lde_attempts = 0
  AWG_start_DO_channel = data_20[12]
  AWG_done_DI_channel = data_20[13]
  PLU_arm_DO_channel = data_20[14]
  PLU_success_dio_in_bit = data_20[18]
  is_PLU_success = 0
  
  ' SSRO
  wait_before_RO = data_20[9]
  RO_event_idx = 1
  RO_steps = data_20[10]
  
  for i=1 to max_readouts
    DATA_22[i] = 0
    DATA_23[i] = 0
  next i
  
  ' misc
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  counter_pattern     = 2 ^ (counter-1)

  ' prepare hardware
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
  par_79 = 0                      ' cumulative LT2 counts in PSB during tpqi sequence
  Par_80 = 0                      ' number of start triggers to LT1
  par_81 = 0                      ' number of readouts performed
  
  P2_DAC(DAC_MODULE, green_aom_channel, 3277*green_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, ex_aom_channel, 32768)
  P2_DAC(DAC_MODULE, a_aom_channel, 32768)
  
  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter,00001000b) 'configure counter
  P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,trigger_cr_dio_out,0)
  P2_DIGOUT(DIO_MODULE,trigger_ssro_dio_out,0)
  
  ' P2_DIGOUT(DIO_MODULE,6,0)

EVENT:
  cr_check_count_threshold_prepare = par_75
  cr_check_count_threshold_probe = par_68

  selectcase remote_mode
    case 0
      Inc(Par_80)
      P2_DIGOUT(DIO_MODULE,trigger_cr_dio_out,1) ' trigger lt1 do to CR check
      remote_mode = 1

    case 1
      was_cr_lt1_OK = is_cr_lt1_OK
      is_cr_lt1_OK = ((P2_DIGIN_LONG(DIO_MODULE)) AND (trigger_cr_dio_in_bit))
      if ((was_cr_lt1_OK = 0) and (is_cr_lt1_OK > 0)) then
        remote_mode = 2
        P2_DIGOUT(DIO_MODULE,trigger_cr_dio_out,0) ' remover HI-trigger for lt1
        Inc(par_77)
      endif
    
  endselect

  selectcase mode
    case 0
      if (timer = 0) then
        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
        P2_CNT_ENABLE(CTR_MODULE, 1111b) ' enable counter

        P2_DAC(DAC_MODULE, ex_aom_channel, 3277*ex_cr_voltage+32768) ' turn on the Ex and A1 lasers
        P2_DAC(DAC_MODULE, a_aom_channel, 3277*a_cr_voltage+32768)
      endif

      if (timer = cr_check_steps) then
        P2_CNT_LATCH(CTR_MODULE, 1111b)
        current_cr_check_counts = P2_CNT_READ_LATCH(CTR_MODULE, counter)
        DATA_23[RO_event_idx] = current_cr_check_counts
        par_70 = par_70 + current_cr_check_counts
        Inc(par_72)

        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter

        if (current_cr_check_counts < current_cr_threshold) then
          mode = 1
          timer = -1
          Inc(par_71)
        else
          P2_DAC(DAC_MODULE, ex_aom_channel, 32768) ' turn off the red lasers
          P2_DAC(DAC_MODULE, a_aom_channel, 32768)
          mode = 2
          timer = -1
          current_cr_threshold = cr_check_count_threshold_probe
        endif

        if (current_cr_check_counts < max_hist_cts) then
          if (first_cr_probe_after_lde > 0) then
            Inc(DATA_7[current_cr_check_counts+1])
          endif
          Inc(DATA_8[current_cr_check_counts+1])
        endif
        
        first_cr_probe_after_lde = 0
      endif

    case 1
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

    case 2
      if (remote_mode = 2) then
        mode = 3
        timer = -1
      endif
    
      ' run LDE sequence     
    case 3
      if (timer = 0) then
        inc(par_73)
        
        P2_DIGOUT(DIO_MODULE,PLU_arm_DO_channel,1)  ' PLU arming trigger
        CPU_SLEEP(9)               ' need >= 30ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        P2_DIGOUT(DIO_MODULE,PLU_arm_DO_channel,0)
        
        P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
        CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
      
      else
        was_PLU_success = is_PLU_success
        is_PLU_success = ((P2_DIGIN_LONG(DIO_MODULE)) AND (PLU_success_dio_in_bit))
        
        if ((was_PLU_success = 0) and (is_PLU_success > 0)) then
          mode = 4
          timer = -1
          inc(par_81)
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
        
        
      ' SSRO
    case 4
      if (timer = wait_before_RO) then
        P2_DIGOUT(DIO_MODULE,trigger_ssro_dio_out,1) ' trigger lt1 do to SSRO
        remote_mode = 3
        
        P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
        P2_CNT_ENABLE(CTR_MODULE, counter_pattern)	  'turn on counter
        P2_DAC(DAC_MODULE, ex_aom_channel, 3277*ex_ro_voltage+32768) ' turn on Ex laser
        P2_DAC(DAC_MODULE, a_aom_channel, 3277*a_ro_voltage+32768) ' turn on A laser
      endif
      
      if (timer = wait_before_RO+RO_steps) then
        P2_DIGOUT(DIO_MODULE,trigger_ssro_dio_out,0) ' remove trigger lt1 do to SSRO
      
        P2_DAC(DAC_MODULE, ex_aom_channel, 32768) ' turn off Ex laser
        P2_DAC(DAC_MODULE, a_aom_channel, 32768) ' turn off A laser
        
        data_22[RO_event_idx] = P2_CNT_READ(CTR_MODULE, counter)
        P2_CNT_ENABLE(CTR_MODULE, 0)
        
        inc(RO_event_idx)
        mode = 0
        remote_mode = 0
        timer = -1
      endif
      
  endselect
  timer = timer + 1
