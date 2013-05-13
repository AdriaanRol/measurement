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
#INCLUDE ADwinGoldII.inc

#DEFINE max_hist_cts 100                ' dimension of photon counts histogram for CR
DIM DATA_7[max_hist_cts] as long       ' histogram of counts during 1st CR after interference sequence
DIM DATA_8[max_hist_cts] as long       ' histogram of counts during CR (all attempts)
DIM i as long
DIM cr_prepared as integer              ' set to 1 if NV is prepared, reset to 0 after first CR.

DIM counter AS LONG                     ' select internal ADwin counter 1 - 4 for conditional readout
DIM green_aom_channel AS LONG           ' DAC channel for green laser AOM
DIM green_aom_voltage AS Float           ' voltage of repump pulse
dim ex_aom_channel as long
dim ex_aom_voltage as Float
dim a_aom_channel as long
dim a_aom_voltage as Float

dim trigger_dio_in, trigger_dio_out as integer

'DIM AWG_wait AS LONG
'DIM DATA_51[10000] AS FLOAT

dim was_triggered, is_triggered as integer
dim do_cr_check as integer
dim cr_check_steps as long                      ' how long to check, in units of process cycles (lt1)
dim cr_check_count_threshold_prepare as long    ' initial C&R threshold after repump (lt1)
dim cr_check_count_threshold_probe as long      ' C&R threshold for probe after sequence (lt1)
dim current_cr_check_step as long
dim current_cr_check_counts as long

dim is_idle_counter_running as integer          ' keeps track of the counter that runs when no cr check or repump

dim do_repump as integer                        ' whether we need to apply a green pulse (lt1)
dim repump_steps as long
dim current_repump_step as long

dim cr_OK as integer

init:
  for i=1 to max_hist_cts
    DATA_7[i] = 0
    DATA_8[i] = 0
  next i

  counter = PAR_78         '1 'P78?
  green_aom_channel = par_26
  green_aom_voltage = fpar_30
  ex_aom_channel = par_30
  ex_aom_voltage = fpar_31
  a_aom_channel = par_31
  a_aom_voltage = fpar_32
  
  trigger_dio_in = 10 'par_32 later maybe as a variable
  trigger_dio_out = 1 'par_33 later maybe as a variable
  
  ' set dacs to zero
  DAC(green_aom_channel, 32768)
  DAC(ex_aom_channel, 32768)
  DAC(a_aom_channel, 32768)
  
  
  do_cr_check = 0
  cr_check_steps = par_28
  cr_check_count_threshold_probe = par_68
  cr_check_count_threshold_prepare = par_75
  current_cr_check_step = 0
  current_cr_check_counts = 0
  
  do_repump = 0
  repump_steps = par_27
  current_repump_step = 0
  cr_prepared = 0
  
  is_triggered = 0
  is_idle_counter_running = 0
  
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' below CR threshold events
  PAR_72 = 0                      ' number of CR checks performed (lt1)
  par_76 = 0                      ' cumulative counts during repumping
  par_77 = 0                      ' number of ok pulses sent to lt2
  Par_79 = 0                      'number of start pulses received from lt2
  Par_80 = 0                      ' cumulative counts in PSB when not CR chekging or repummping 
  
  CNT_ENABLE(0000b)
  CNT_MODE(1,00001000b)
  CNT_MODE(2,00001000b)
  CNT_MODE(3,00001000b)
  CNT_MODE(4,00001000b)
  CNT_SE_DIFF(0000b)
  CNT_CLEAR(1111b)
  CNT_ENABLE(1111b)
  
  CONF_DIO(13)
  DIGOUT(trigger_dio_out, 0)
  
event:
  cr_check_count_threshold_probe = par_68
  cr_check_count_threshold_prepare = par_75
  
  was_triggered = is_triggered
  is_triggered = DIGIN(trigger_dio_in)
  
  if ((was_triggered = 0) and (is_triggered > 0)) then
    do_cr_check = 1
    do_repump = 0
    ' cr_OK = 0
    Par_79 = Par_79 + 1
    DIGOUT(trigger_dio_out, 0)
    CNT_LATCH(1111b)
    Par_80=Par_80 + CNT_READ_LATCH(counter)
    is_idle_counter_running = 0
  endif
  
  if (do_cr_check > 0) then
    if (current_cr_check_step = 0) then
            
      CNT_ENABLE(0000b)
      CNT_CLEAR(1111b)
      CNT_ENABLE(1111b)
        
      DAC(ex_aom_channel, 3277*ex_aom_voltage+32768) ' turn on the red lasers
      DAC(a_aom_channel, 3277*a_aom_voltage+32768)
    endif
      
    current_cr_check_step = current_cr_check_step + 1
      
    if (current_cr_check_step > cr_check_steps) then
      CNT_LATCH(1111b)
      current_cr_check_counts = CNT_READ_LATCH(counter)
           
      par_70 = par_70 + current_cr_check_counts
      par_72 = par_72 + 1
        
      CNT_ENABLE(0000b)
      CNT_CLEAR(1111b) ' clear counter
        
      'DAC(ex_aom_channel, 32768) ' turn off the red lasers
      'DAC(a_aom_channel, 32768)        
        
      do_cr_check = 0
      
      if (cr_prepared = 1) then
        if (current_cr_check_counts < max_hist_cts) then
          DATA_7[current_cr_check_counts+1] = DATA_7[current_cr_check_counts+1] + 1
        endif
        cr_prepared = 0
        if (current_cr_check_counts < cr_check_count_threshold_probe) then
          do_repump = 1
          par_71 = par_71 + 1
        else
          'XXX
          DAC(ex_aom_channel, 32768) ' turn off the red lasers
          DAC(a_aom_channel, 32768)
        
          DIGOUT(trigger_dio_out, 1)
          par_77 = par_77 + 1
          cr_prepared = 1
        endif
      else
        if (current_cr_check_counts < cr_check_count_threshold_prepare) then
          do_repump = 1
          par_71 = par_71 + 1
        else
          'XXX
          DAC(ex_aom_channel, 32768) ' turn off the red lasers
          DAC(a_aom_channel, 32768)
        
          DIGOUT(trigger_dio_out, 1)
          par_77 = par_77 + 1
          cr_prepared = 1
        endif
      endif
      
      if (current_cr_check_counts < max_hist_cts) then
        DATA_8[current_cr_check_counts+1] = DATA_8[current_cr_check_counts+1] + 1
      endif
            

      current_cr_check_step = 0
      current_cr_check_counts = 0
    endif
  endif
  
    
  if (do_repump > 0) then
    if (current_repump_step = 0) then
      
      CNT_ENABLE(0000b)
      CNT_CLEAR(1111b)
      CNT_ENABLE(1111b)
      
      DAC(green_aom_channel, 3277*green_aom_voltage+32768)    
    endif
    
    current_repump_step = current_repump_step + 1
    if (current_repump_step > repump_steps) then
      
      DAC(green_aom_channel, 32768) ' turn off green
      
      CNT_LATCH(1111b)
      par_76 = par_76 + CNT_READ_LATCH(counter)      
      do_repump = 0
      do_cr_check = 1
      current_repump_step = 0
    endif    
  endif
  
  if (((do_repump = 0) and (do_cr_check = 0)) and (is_idle_counter_running = 0)) then
    CNT_ENABLE(0000b)
    CNT_CLEAR(1111b)
    CNT_ENABLE(1111b)
    is_idle_counter_running = 1
  endif
    
    
  
  
  
    
