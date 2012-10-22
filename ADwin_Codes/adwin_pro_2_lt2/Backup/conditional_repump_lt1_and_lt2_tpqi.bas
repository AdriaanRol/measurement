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

' this program repumps the NV center with a green pulse, 
' then counts photons for during 'probe duration'
' conditional on the count rate, either the AWG sequence is started or the repump pulse is repeated

#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

#DEFINE max_hist_cts 100                ' dimension of photon counts histogram for CR
DIM DATA_71[max_hist_cts] as long       ' histogram of counts during 1st CR after interference sequence
DIM DATA_72[max_hist_cts] as long       ' histogram of counts during CR (all attempts)
DIM i as long
DIM cr_prepared as long                 ' set to 1 if both NVs are prepared, reset to 0 after first CR.

#DEFINE count_psb_during_tpqi 0         'can be switched off for process-time reduction
#DEFINE LT1_PSB_counter 3

DIM counter AS LONG                     ' select internal ADwin counter 1 - 4 for conditional readout
DIM green_aom_channel AS LONG           ' DAC channel for green laser AOM
DIM green_aom_voltage AS Float           ' voltage of repump pulse
DIM green_aom_off_voltage AS Float       ' off-voltage of green (0V is not 0W)
dim ex_aom_channel as long
dim ex_aom_voltage as Float
dim a_aom_channel as long
dim a_aom_voltage as Float

'DIM AWG_wait AS LONG
'DIM DATA_51[10000] AS FLOAT

dim do_cr_lt1_check, do_cr_lt2_check as integer ' whether charge and resonance (c&r) on lt1/2 needs to be checked
dim do_cr_check as integer
dim cr_check_steps as long                      ' how long to check, in units of process cycles (lt2)
dim cr_check_count_threshold as long            ' C&R threshold for checking (lt2)
dim current_cr_check_step as long
dim current_cr_check_counts as long

dim is_cr_lt1_check_running as integer
dim is_cr_lt1_OK, was_cr_lt1_OK as integer

dim cr_time_limit_steps as long                 ' how long (in pr. cycles) before forcing C&R check
dim current_cr_time_limit_step as long

dim do_repump as integer                        ' whether we need to apply a green pulse (lt2)
dim repump_steps as long
dim current_repump_step as long

dim is_tpqi_running as integer

#DEFINE trigger_dio_in_bit 256      'par_32 later maybe as a variable
#DEFINE trigger_dio_out 16          'par_33 later maybe as a variable

INIT:

  for i=1 to max_hist_cts
    DATA_71[i] = 0
    DATA_72[i] = 0
  next i

  counter = PAR_78         '1 'P78?
  green_aom_channel = par_26
  green_aom_voltage = fpar_30
  green_aom_off_voltage = fpar_33
  ex_aom_channel = par_30
  ex_aom_voltage = fpar_31
  a_aom_channel = par_31
  a_aom_voltage = fpar_32
 
  P2_DAC(DAC_MODULE, green_aom_channel, 3277*green_aom_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, ex_aom_channel, 32768)
  P2_DAC(DAC_MODULE, a_aom_channel, 32768)
  
  do_cr_lt1_check = 1
  do_cr_lt2_check = 1
  cr_check_steps = par_28
  cr_check_count_threshold = par_75
  current_cr_check_step = 0
  current_cr_check_counts = 0
  is_cr_lt1_check_running = 0
  
  cr_time_limit_steps = PAR_29 ' in multiples of processor cycles. should be a multiple of the AWG tpqi sequence time
  current_cr_time_limit_step = 0

  do_repump = 0
  repump_steps = par_27
  current_repump_step = 0
  
  is_tpqi_running = 0
  is_cr_lt1_OK = 0
  
  par_69 = 0                      ' cumulative LT1 counts in PSB during tpqi sequence
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' below CR threshold events
  PAR_72 = 0                      ' number of CR checks performed (lt2)
  par_73 = 0                      ' number of tpqi starts
  par_74 = 0                      ' number of tpqi runs interrupted
  par_76 = 0                      ' cumulative counts during repumping
  par_77 = 0                      ' number of OK signals from LT1
  par_79 = 0                      ' cumulative LT2 counts in PSB during tpqi sequence
  Par_80 = 0                      ' number of start triggers to LT1

  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter,00001000b) 'configure counter

  P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,trigger_dio_out,0)
  P2_DIGOUT(DIO_MODULE,6,0)
  
EVENT:
  
  cr_check_count_threshold = par_75
  do_cr_check = do_cr_lt1_check or do_cr_lt2_check
   
  if (do_cr_check > 0) then
    if ((is_cr_lt1_check_running = 0) and (do_cr_lt1_check > 0)) then
      Inc(Par_80)
      P2_DIGOUT(DIO_MODULE,trigger_dio_out,1) ' trigger lt1 do to CR check
      is_cr_lt1_check_running = 1
    endif
    
    if (do_cr_lt2_check > 0) then
      if (current_cr_check_step = 1) then
        
        'XXX debug --------
        'P2_DAC(DAC_MODULE, 4, 3277*1+32768)
        '-----------
        
        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
        P2_CNT_ENABLE(CTR_MODULE, 1111b) ' enable counter
              
        P2_DAC(DAC_MODULE, ex_aom_channel, 3277*ex_aom_voltage+32768) ' turn on the red lasers
        P2_DAC(DAC_MODULE, a_aom_channel, 3277*a_aom_voltage+32768)
      endif
      
      current_cr_check_step = current_cr_check_step + 1
      
      if (current_cr_check_step > cr_check_steps+1) then
        P2_CNT_LATCH(CTR_MODULE, 1111b)
        current_cr_check_counts = P2_CNT_READ_LATCH(CTR_MODULE, counter)        
        par_70 = par_70 + current_cr_check_counts
        Inc(par_72)
        
        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
       
        'XXX debug --------
        'P2_DAC(DAC_MODULE, 4, 32768)
        '-----------

        do_cr_lt2_check = 0
        if (current_cr_check_counts < cr_check_count_threshold) then
          do_repump = 1
          Inc(par_71)
        else  
          P2_DAC(DAC_MODULE, ex_aom_channel, 32768) ' turn off the red lasers
          P2_DAC(DAC_MODULE, a_aom_channel, 32768)
        endif
        
        if (cr_prepared = 1) then
          if (current_cr_check_counts < max_hist_cts) then
            Inc(DATA_71[current_cr_check_counts+1])
          endif
          cr_prepared = 0
        endif
        if (current_cr_check_counts < max_hist_cts) then
          Inc(DATA_72[current_cr_check_counts+1])
        endif
        
        current_cr_check_step = 0
        current_cr_check_counts = 0

      endif
    endif
    
          
    if (((is_cr_lt1_check_running=1) and (do_cr_lt1_check=1))) then
      was_cr_lt1_OK = is_cr_lt1_OK
      is_cr_lt1_OK = ((P2_DIGIN_LONG(DIO_MODULE)) AND (trigger_dio_in_bit)) ' check whether LT1 is OK   
      if ((was_cr_lt1_OK = 0) and (is_cr_lt1_OK > 0)) then
        do_cr_lt1_check = 0
        is_cr_lt1_check_running = 0
        P2_DIGOUT(DIO_MODULE,trigger_dio_out,0) ' remover HI-trigger for lt1
        Inc(par_77) 
      endif
      
    endif
    
  endif
      
  if (do_repump > 0) then
    if (current_repump_step = 0) then

      P2_CNT_ENABLE(CTR_MODULE, 0000b)
      P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
      P2_CNT_ENABLE(CTR_MODULE, 1111b) ' enable counter
      
      P2_DAC(DAC_MODULE, green_aom_channel, 3277*green_aom_voltage+32768)
    
    endif
    
    current_repump_step = current_repump_step + 1
    if (current_repump_step > repump_steps) then
      
      P2_DAC(DAC_MODULE, green_aom_channel, 3277*green_aom_off_voltage+32768) ' turn off green
      
      P2_CNT_LATCH(CTR_MODULE, 1111b)
      par_76 = par_76 + P2_CNT_READ_LATCH(CTR_MODULE, counter)
      
      do_repump = 0
      do_cr_lt2_check = 1
      current_repump_step = 0
    endif
    
  endif

  if (is_tpqi_running=1) then
    if (current_cr_time_limit_step=0) then
      if (count_psb_during_tpqi>0) then
        P2_CNT_ENABLE(CTR_MODULE, 0000b)
        P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
        P2_CNT_ENABLE(CTR_MODULE, 1111b) ' enable counter
      endif
          
      P2_DIGOUT(DIO_MODULE,6,1)  ' AWG event jump (should be to tpqi sequence element)
      CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
      P2_DIGOUT(DIO_MODULE,6,0)
    endif
    
    current_cr_time_limit_step = current_cr_time_limit_step + 1
    
    if (current_cr_time_limit_step > cr_time_limit_steps) then
      is_tpqi_running = 0
      do_cr_lt2_check = 1
      do_cr_lt1_check = 1
      Inc(par_74)
      if (count_psb_during_tpqi>0) then
        P2_CNT_LATCH(CTR_MODULE, 1111b)
        par_79 = par_79 + P2_CNT_READ_LATCH(CTR_MODULE, counter)
        par_69 = par_69 + P2_CNT_READ_LATCH(CTR_MODULE, LT1_PSB_counter)
      endif
    endif
  endif
  
  if (((do_cr_lt1_check=0) and (do_cr_lt2_check=0)) and ((do_repump=0) and (is_tpqi_running=0))) then
    is_tpqi_running = 1
    Inc(par_73)
    current_cr_time_limit_step = 0
    cr_prepared = 1
  endif
  
