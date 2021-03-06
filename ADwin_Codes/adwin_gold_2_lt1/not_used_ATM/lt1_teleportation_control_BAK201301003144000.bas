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
' Teleportation master controller program. lt1 is in charge, lt2 is remote

' modes:
' 0 : start
' 1 : do local yellow repumping / resonance check
' 2 : do local red CR check
' 3 : wait for N polarization
' 4 : local CR OK, wait for remote
' 5 : run LDE
' 6 : run nitrogen initialization, BSM
' 7 : do SSRO 1 + SP
' 8 : run nitrogen RO pulse
' 9 : do SSRO 2
' 10: run U and RO basis rotation
' 11: wait for remote SSRO
''
' remote modes:
' 0 : start remote CR check
' 1 : remote CR check running
' 2 : remote CR OK, waiting
' 3 : remote SSRO running
' 4 : remote SSRO OK

' run-modes:
' 0 : Teleportation

#INCLUDE ADwinGoldII.inc
#INCLUDE Math.inc

#DEFINE max_repetitions         10000          'the maximum number of datapoints taken
#DEFINE max_red_hist_cts        100            ' dimension of photon counts histogram for red CR
#DEFINE max_repump_hist_cts     100            ' dimension of photon counts histogram for repump hist
#DEFINE max_statistics          15
#DEFINE max_hist_CR_probe_time  500            '*1000 = 0.5 s is max time of CR probe time statistics

' parameters
DIM DATA_20[40] AS LONG                   AT DRAM_EXTERN ' integer parameters
DIM DATA_21[10] AS FLOAT                  AT DRAM_EXTERN ' float parameters
DIM DATA_7[max_red_hist_cts] AS LONG      AT EM_LOCAL ' histogram of counts during 1st red CR after timed-out lde sequence
DIM DATA_8[max_red_hist_cts] AS LONG      AT EM_LOCAL ' histogram of counts during red CR (all attempts)
DIM DATA_9[max_repump_hist_cts] AS LONG   AT EM_LOCAL ' histogram of counts during 1st repump after timed-out lde sequence
DIM DATA_10[max_repump_hist_cts] AS LONG  AT EM_LOCAL ' histogram of counts during repump (all attempts)
DIM DATA_23[max_repetitions] AS LONG      AT DRAM_EXTERN 'CR counts after teleportation
DIM DATA_24[max_repetitions] AS LONG      AT DRAM_EXTERN 'BSM SSRO 1 (electron) results
DIM DATA_25[max_repetitions] AS LONG      AT DRAM_EXTERN 'PLU Bell states
DIM DATA_26[max_repetitions] AS LONG      AT DRAM_EXTERN 'BSM SSRO2 (nitrogen) results
DIM DATA_27[max_repetitions] AS LONG      AT EM_LOCAL    'CR check counts before teleportation event
DIM DATA_28[max_statistics] AS LONG       AT EM_LOCAL    'statistics on entering modes
DIM DATA_29[max_repetitions] AS LONG      AT EM_LOCAL    ' CR timer before LDE element of teleportation event
DIM DATA_30[max_hist_CR_probe_time] AS LONG AT EM_LOCAL  ' CR probe time statistics before LDE sequence
DIM DATA_31[max_hist_CR_probe_time] AS LONG AT EM_LOCAL  ' CR probe time lt2 statistics before LDE sequence

' general variables
DIM i               AS LONG ' counter for array initalization
DIM mode            AS INTEGER
DIM remote_mode     AS INTEGER
DIM timer           AS LONG
DIM CR_timer        AS LONG
DIM wait_time       AS LONG
DIM CR_probe_timer  AS LONG
DIM CR_probe_time   AS LONG
DIM CR_timer_lt2    AS LONG
DIM CR_time_lt2      as LONG

'tuning
DIM tune_duration AS LONG

' settings for CR checks and repumping
DIM counter AS LONG                      'select internal ADwin counter 1 - 4 for conditional readout (PSB lt1)
DIM repump_aom_channel AS LONG            'DAC channel for repump laser AOM
DIM repump_voltage AS FLOAT               'voltage of repump pulse
DIM repump_tune_voltage AS FLOAT          
DIM repump_off_voltage AS FLOAT           'off-voltage of repump laser (0V is not 0W)
DIM e_aom_channel AS LONG 
DIM e_cr_voltage AS FLOAT
DIM e_sp_voltage AS FLOAT
DIM e_ro_voltage AS FLOAT
DIM e_tune_voltage AS FLOAT
DIM e_off_voltage AS FLOAT
DIM fb_aom_channel AS LONG
DIM fb_cr_voltage AS FLOAT
DIM fb_sp_voltage AS FLOAT
DIM fb_ro_voltage AS FLOAT
DIM fb_tune_voltage AS FLOAT
DIM fb_off_voltage AS FLOAT 
DIM red_cr_check_steps AS LONG                        'how long to check, in units of process cycles (lt1)
DIM current_red_cr_check_counts AS LONG        
DIM current_repump_counts AS LONG 
DIM cr_threshold_prepare AS LONG          ' initial CR threshold for first resonance check (lt1)
DIM cr_threshold_probe AS LONG            'threshold for probe after sequence (charge check) (lt1)
DIM CR_repump AS LONG                                 ' CR repump threshold (typically 1 for yellow, >9000 for green)       
DIM repump_steps AS LONG                       'how long to rempump w/ yellow or green, in process cycles (lt1)
DIM current_cr_threshold AS LONG 
DIM first_cr_probe_after_unsuccessful_lde AS INTEGER  'first CR check after timed out lde sequence
DIM cr_after_teleportation AS INTEGER                 'first CR check after teleportation
DIM time_before_forced_CR AS LONG                     'time before forced CR check on LT1
DIM CR_probe_max_time AS LONG

'LDE sequence
DIM AWG_lt1_trigger_do_channel AS LONG
DIM AWG_lt1_event_do_channel AS LONG
DIM AWG_lt1_di_channel AS LONG
DIM AWG_lt1_di_channel_in_bit AS LONG
DIM AWG_lt2_address0_do_channel AS LONG
DIM AWG_lt2_address1_do_channel AS LONG
DIM AWG_lt2_address2_do_channel AS LONG
DIM AWG_lt2_address3_do_channel AS LONG
DIM AWG_lt2_address_all_in_bit AS LONG
DIM AWG_lt2_address_LDE AS LONG
DIM AWG_lt2_address_LDE_in_bit AS LONG
DIM AWG_lt2_address_U AS LONG
DIM AWG_lt2_address_U1 AS LONG
DIM AWG_lt2_address_U1_in_bit AS LONG
DIM AWG_lt2_address_U2 AS LONG
DIM AWG_lt2_address_U2_in_bit AS LONG
DIM AWG_lt2_address_U3 AS LONG
DIM AWG_lt2_address_U3_in_bit AS LONG
DIM AWG_lt2_address_U4 AS LONG
DIM AWG_lt2_address_U4_in_bit AS LONG
DIM PLU_arm_do_channel AS LONG
DIM PLU_di_channel AS LONG
DIM PLU_di_channel_in_bit AS LONG
DIM PLU_Bell_state AS LONG

'setting for SSRO on lt1
DIM electron_RO_steps AS LONG
DIM electron_RO2_steps AS LONG
DIM RO1_ms_result AS LONG
DIM RO2_ms_result AS LONG
DIM current_RO1_counts AS LONG
DIM current_RO2_counts AS LONG
DIM wait_steps_before_RO1 AS LONG
DIM wait_steps_before_RO2 AS LONG
DIM wait_steps_before_SP AS LONG
DIM spin_pumping_steps AS LONG 

' remote things on lt2
DIM ADwin_LT2_di_channel AS LONG 
DIM ADwin_LT2_di_channel_in_bit AS LONG 
DIM ADwin_LT2_trigger_do_channel AS LONG 
DIM AWG_LT1_address_U AS LONG  ' this is calculated from a function of RO1_ms_result, RO2_ms_result, PLU_Bell_state
DIM ADwin_in_is_high AS LONG
DIM ADwin_in_was_high AS LONG
DIM ADwin_switched_to_high AS LONG

' for the N polarization on LT1, AWG needs to tell us it's done
DIM AWG_LT1_in_is_high AS LONG
DIM AWG_LT1_in_was_high AS LONG
DIM AWG_LT1_switched_to_high AS LONG

' Teleportation
DIM tele_event_id AS LONG 

' process control
DIM max_successful_repetitions AS LONG
DIM successful_repetitions as LONG
DIM max_CR_starts AS LONG
DIM CR_starts AS LONG
DIM remote_delay as long


dim do_remote as long
dim do_N_polarization as long
dim do_sequences as long
dim set_do_sequences as long

' misc and temporary variables
DIM DIO_register AS LONG 

' debug
DIM timervalue1 AS LONG
DIM timervalue2 AS LONG

DIM A AS LONG

INIT:
  ' general
  mode                    = 0
  remote_mode             = 0
  timer                   = 0
  cr_after_teleportation  = 0
  tele_event_id           = 0
  remote_delay            = 5
  
  max_successful_repetitions = -1
  successful_repetitions = 0
  max_CR_starts = -1
  CR_starts = 0
    
  ' init statistics variables
  for i=1 to max_red_hist_cts
    DATA_7[i] = 0
    DATA_8[i] = 0
  next i
    
  for i=1 to max_repump_hist_cts
    DATA_9[i] = 0
    DATA_10[i] = 0
  next i
    
  for i=1 to max_repetitions
    DATA_23[i] = 0    'CR check counts after teleportation
    DATA_24[i] = 0    'SSRO1 results
    DATA_25[i] = 0    'PLU Bell state
    DATA_26[i] = 0    'SSRO2 results
    DATA_27[i] = 0    'CR check counts before event
    DATA_29[i] = 0    'CR timer before LDE element of teleportation event
  next i
     
  for i=1 to max_statistics
    DATA_28[i] = 0    'statistics
  next i     
  
  for i=1 to max_hist_CR_probe_time
    DATA_30[i] = 0   'lt1 CR probe timer
    DATA_31[i] = 0   'lt2 CR probe timer
  next i
      
  ' init variables
  counter                       = DATA_20[1]
  repump_aom_channel            = DATA_20[2]
  e_aom_channel                 = DATA_20[3]
  fb_aom_channel                = DATA_20[4]
  red_cr_check_steps            = DATA_20[5]
  cr_threshold_prepare          = DATA_20[6]
  cr_threshold_probe            = DATA_20[7]
  repump_steps                  = DATA_20[8]
  time_before_forced_CR         = DATA_20[9]
  max_successful_repetitions    = DATA_20[10]
  electron_RO_steps             = DATA_20[11]
  ADwin_LT2_trigger_do_channel  = DATA_20[12]
  ADwin_LT2_di_channel          = DATA_20[13]
  AWG_lt1_trigger_do_channel    = DATA_20[14]
  AWG_lt1_di_channel            = DATA_20[15]
  PLU_arm_do_channel            = DATA_20[16]
  PLU_di_channel                = DATA_20[17]  
  wait_steps_before_RO1         = DATA_20[18]
  wait_steps_before_SP          = DATA_20[19]
  spin_pumping_steps            = DATA_20[20]
  wait_steps_before_RO2         = DATA_20[21]
  electron_RO2_steps            = DATA_20[22]
  CR_repump                     = DATA_20[23]
  AWG_lt1_event_do_channel      = DATA_20[24]
  max_CR_starts                 = DATA_20[25]
  AWG_lt2_address0_do_channel   = DATA_20[26]
  AWG_lt2_address1_do_channel   = DATA_20[27]
  AWG_lt2_address2_do_channel   = DATA_20[28]
  AWG_lt2_address3_do_channel   = DATA_20[29] 
  AWG_lt2_address_LDE           = DATA_20[30]
  AWG_lt2_address_U1            = DATA_20[31]
  AWG_lt2_address_U2            = DATA_20[32]
  AWG_lt2_address_U3            = DATA_20[33]
  AWG_lt2_address_U4            = DATA_20[34]
  do_remote                     = DATA_20[35]
  do_N_polarization             = DATA_20[36]
  set_do_sequences              = DATA_20[37]
  CR_probe_max_time             = DATA_20[38]
  
    
  repump_voltage                = DATA_21[1]
  repump_off_voltage            = DATA_21[2]
  e_cr_voltage                  = DATA_21[3]
  fb_cr_voltage                 = DATA_21[4]
  e_sp_voltage                  = DATA_21[5]
  fb_sp_voltage                 = DATA_21[6]
  e_ro_voltage                  = DATA_21[7]
  fb_ro_voltage                 = DATA_21[8]
  e_off_voltage                 = DATA_21[9]
  fb_off_voltage                = DATA_21[10] 

  do_sequences = set_do_sequences
  current_red_cr_check_counts   = 0
  current_repump_counts         = 0
  current_cr_threshold          = cr_threshold_prepare
  first_cr_probe_after_unsuccessful_lde = 0
  cr_after_teleportation        = 0
  PLU_Bell_state                = -1
  current_RO1_counts            = 0
  current_RO2_counts            = 0
  RO1_ms_result                 = 0
  RO2_ms_result                 = 0
  ADwin_in_is_high              = 0
  ADwin_in_was_high             = 0
  ADwin_switched_to_high        = 0
  CR_timer                      = 0
  CR_probe_timer                = 0
  AWG_LT1_in_is_high            = 0
  AWG_LT1_in_was_high           = 0
  AWG_LT1_switched_to_high      = 0

      
  ' prepare hardware 
  par_58 = 0
  par_59 = 0                      'tune (1 is tuning, 0 is running)
  
  par_60 = 0                      'debug par used for measuring timer
  par_62 = 0                      'debug: remote mode
  par_63 = CR_probe_max_time      'debug: CR probe timer 
  par_64 = 0                      'debug: mode
  par_65 = 0                      'debug: timer
  par_66 = 0                      'debug par
    
  Par_69 = cr_repump              
  Par_67 = 0                      ' cumulative counts during RO2 (LT1)
  Par_70 = 0                      ' cumulative counts during red CR check (LT1)
  Par_76 = 0                      ' cumulative counts during yellow repumping (LT1)
  par_71 = 0                      ' cumulative number of repumps
  par_72 = 0                      ' number of red CR checks performed (LT1)
  par_73 = 0                      ' number of CR OK signals from LT2
  par_74 = 0                      ' number of start CR triggers to LT2
  par_75 = cr_threshold_prepare
  Par_68 = cr_threshold_probe
  par_77 = 0                      ' number of successful attempts
  par_78 = 0                      ' number of LDE sequence starts
  par_79 = 0                      ' CR below threshold events (LT1)
  par_80 = 0                      ' cumulative counts during RO1 (LT1)
  
  ADwin_LT2_di_channel_in_bit = 2^ADwin_LT2_di_channel 
  AWG_LT1_di_channel_in_bit = 2^AWG_LT1_di_channel
  
  '  PLU_di_channel_in_bit = 2^PLU_di_channel
  '  AWG_lt2_address_all_in_bit = 2^(AWG_lt2_address0_do_channel)+ 2^(AWG_lt2_address1_do_channel)+ 2^(AWG_lt2_address2_do_channel)+2^(AWG_lt2_address3_do_channel)
  '  
  '  '' The below specifies the addresses of the AWG lt2 in bits, for easier handling later on. The lines are too long to be on one line.
  '  AWG_lt2_address_LDE_in_bit = (AWG_lt2_address_LDE AND 8)/8 * 2^(AWG_lt2_address3_do_channel) + (AWG_lt2_address_LDE AND 4)/4 * 2^(AWG_lt2_address2_do_channel) 
  '  AWG_lt2_address_LDE_in_bit = AWG_lt2_address_LDE + (AWG_lt2_address_LDE AND 2)/2 * 2^(AWG_lt2_address1_do_channel) + (AWG_lt2_address_LDE AND 1)/1 * 2^(AWG_lt2_address0_do_channel)
  '  
  '  AWG_lt2_address_U1_in_bit = (AWG_lt2_address_U1 AND 8)/8 * 2^(AWG_lt2_address3_do_channel) + (AWG_lt2_address_U1 AND 4)/4 * 2^(AWG_lt2_address2_do_channel) 
  '  AWG_lt2_address_U1_in_bit = AWG_lt2_address_U1_in_bit + (AWG_lt2_address_U1 AND 2)/2 * 2^(AWG_lt2_address1_do_channel) + (AWG_lt2_address_U1 AND 1)/1 * 2^(AWG_lt2_address0_do_channel)
  '  
  '  AWG_lt2_address_U2_in_bit = (AWG_lt2_address_U2 AND 8)/8 * 2^(AWG_lt2_address3_do_channel) + (AWG_lt2_address_U2 AND 4)/4 * 2^(AWG_lt2_address2_do_channel) 
  '  AWG_lt2_address_U2_in_bit = AWG_lt2_address_U2_in_bit + (AWG_lt2_address_U2 AND 2)/2 * 2^(AWG_lt2_address1_do_channel) + (AWG_lt2_address_U2 AND 1)/1 * 2^(AWG_lt2_address0_do_channel)
  '  
  '  AWG_lt2_address_U3_in_bit = (AWG_lt2_address_U3 AND 8)/8 * 2^(AWG_lt2_address3_do_channel) + (AWG_lt2_address_U3 AND 4)/4 * 2^(AWG_lt2_address2_do_channel) 
  '  AWG_lt2_address_U3_in_bit = AWG_lt2_address_U3_in_bit + (AWG_lt2_address_U3 AND 2)/2 * 2^(AWG_lt2_address1_do_channel) + (AWG_lt2_address_U3 AND 1)/1 * 2^(AWG_lt2_address0_do_channel)
  '  
  '  AWG_lt2_address_U4_in_bit = (AWG_lt2_address_U4 AND 8)/8 * 2^(AWG_lt2_address3_do_channel) + (AWG_lt2_address_U4 AND 4)/4 * 2^(AWG_lt2_address2_do_channel) 
  '  AWG_lt2_address_U4_in_bit = AWG_lt2_address_U4_in_bit + (AWG_lt2_address_U4 AND 2)/2 * 2^(AWG_lt2_address1_do_channel) + (AWG_lt2_address_U4 AND 1)/1 * 2^(AWG_lt2_address0_do_channel)
       
  
  DAC(repump_aom_channel, 3277*repump_off_voltage+32768)   'turn off repump laser
  DAC(e_aom_channel, 3277*e_off_voltage + 32768)           'turn off Ey aom 
  DAC(fb_aom_channel, 3277*fb_off_voltage + 32768)         'turn off FB aom
  CNT_ENABLE(0000b)                          'turn off all counters
  CNT_MODE(counter,00001000b)                'configure counter
  CONF_DIO(11)                               'configure DIO 16:23 as input, all other ports as output
  DIGOUT(ADwin_LT2_trigger_do_channel,0)     'trigger to ADwin LT2
  DIGOUT(AWG_lt1_trigger_do_channel, 0)      'trigger to AWG LT1
  DIGOUT(AWG_lt1_event_do_channel, 0)        'event to AWG LT1
  DIGOUT(PLU_arm_do_channel, 0)              'PLU is not armed until just before LDE start trigger **????
  DIGOUT_BITS(0, AWG_lt2_address_all_in_bit) 'clear the output on the DO's that input to the strobe
  
  'debug 
  timervalue1=0
  timervalue2=0
    
  
EVENT:

  'timervalue1=timervalue2
  'timervalue2=Read_timer()
  'par_60 = Max_long((timervalue2-timervalue1),par_60)
    
  cr_threshold_prepare = par_75
  cr_threshold_probe = Par_68
  cr_repump = Par_69
  
  par_61 = CR_probe_timer
  par_64 = mode
  par_65 = timer
  par_62 = remote_mode
      
  ' If only one setup is used, remote_mode is set to 2 => always ready.
  if (do_remote = 0) then
    remote_mode = 2
  endif
  
  selectcase remote_mode
    
    case 0 'start remote CR check
            
      ' remote delay because it can happen that after getting the signal here that LT2 is done,
      ' we immediately send a start again. this can lead to LT2 missing the step where the
      ' the DO is low (because it's very short). therefore wait a tiny bit before sending
      ' signals.
      if (remote_delay = 0) then      
        INC(par_74)
        DIGOUT(ADwin_LT2_trigger_do_channel, 1)
        remote_mode = 1
        remote_delay = 5
      else
        dec(remote_delay)
      endif
                                      
    case 1 'remote CR check running
      ' check state of other adwin and whether it has changed to ready
      ADwin_in_was_high = ADwin_in_is_high
      ADwin_in_is_high = DIGIN(ADwin_LT2_di_channel)
             
      IF ((ADwin_in_was_high = 0) AND (ADwin_in_is_high > 0)) THEN ' ADwin switched to high during last round. 
        DIGOUT(ADwin_LT2_trigger_do_channel, 0)
        remote_mode = 2
        INC(par_73)
        CR_timer_lt2 = 0
      ENDIF
      
    case 2 'remote CR OK, waiting
      
      '    case 3 'remote SSRO running
      '      ADwin_in_was_high = ADwin_in_is_high
      '      ADwin_in_is_high = DIGIN(ADwin_LT2_di_channel)
      '             
      '      IF ((ADwin_in_was_high = 0) AND (ADwin_in_is_high > 0)) THEN ' ADwin switched to high during last round. 
      '        remote_mode = 4
      '      ENDIF
      '        
      '    case 4 'remote SSRO OK, waiting
      
  endselect 
    
  
  if (timer=0) then
    INC(DATA_28[mode+1])  'increment for each time mode is entered
  endif
  
  selectcase mode
        
    case 0
      ' CR checking.
      ' in this mode we always start the checking on LT2 (green!)
      ' CR checking on LT1 is only started after a certain time
            
      if (timer = 0) then
      
        if (par_59 = 1) then 'only do this if timer = 0 to prevent switching between AWG triggers/events
          do_sequences = 0 ' this is the tune mode
          CR_timer = 1
        else
          do_sequences = set_do_sequences 
        endif
    
        if (do_sequences > 0) then
          if(wait_time > 0) then
            timer = -1
            dec(DATA_28[mode+1]) ' correct statistics
          else
            DIGOUT(AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start the waiting sequence (decide element)
            CPU_SLEEP(9)
            DIGOUT(AWG_lt1_trigger_do_channel, 0)
          endif
        endif
                        
        INC(CR_starts) ' number of times we started the CR decision mode
        par_66 = CR_starts
      
      else
          
        IF (CR_timer < 1) THEN
          mode = 2
          timer = -1
          CR_timer = time_before_forced_CR
        ELSE
          
          if (do_sequences > 0) then
            DIGOUT(AWG_lt1_event_do_channel, 1) ' event jump to AWG to jump to LDE sequence.
            CPU_SLEEP(9)
            DIGOUT(AWG_lt1_event_do_channel, 0)
          endif
          
          mode = 4  ' go to wait for both ready; do not check CR, do not polarize N (it is still polarized)
          timer = -1
        ENDIF
      
      endif
              
    case 1 'yellow repump / resonance check

      IF (timer = 0) THEN
        
        IF (current_red_cr_check_counts < CR_repump)  THEN    
          CNT_ENABLE(0000b)    'turn off counter
          CNT_CLEAR(1111b)     'clear counter    
          CNT_ENABLE(1111b)    'enable counter       
          DAC(repump_aom_channel, 3277*repump_voltage+32768)
          inc(par_71)
        ELSE
          mode = 2
          timer = -1
          current_CR_threshold = CR_threshold_prepare
        ENDIF
      
      ELSE
        
        IF (timer = repump_steps) THEN
          CNT_ENABLE(0000b)     'turn off counter
          current_repump_counts = CNT_READ(counter)
          Par_76 = Par_76 + current_repump_counts
          DAC(repump_AOM_channel, 3277*repump_off_voltage+32768)
                          
          IF (current_repump_counts < max_repump_hist_cts) THEN      'make histograms
            
            IF (first_cr_probe_after_unsuccessful_lde > 0) THEN
              INC(DATA_9[current_repump_counts+1])
            ENDIF
            
            INC(DATA_10[current_repump_counts+1])
          ENDIF
          
          first_CR_probe_after_unsuccessful_LDE = 0       'reset
          current_CR_threshold = CR_threshold_prepare
          mode = 2
          timer = -1
        ENDIF
      
      ENDIF
      
    case 2 'do local red CR check
      
      IF (timer = 0) THEN
        INC(par_72)          'number of red CR checks performed
        CNT_ENABLE(0000b)    'turn off counter
        CNT_CLEAR(1111b)     'clear counter
        CNT_ENABLE(1111b)    'enable counter
                          
        DAC(e_aom_channel, 3277*e_cr_voltage+32768)  'turn on red lasers
        DAC(fb_aom_channel, 3277*fb_cr_voltage+32768)
        'DAC(repump_aom_channel, 3277*repump_voltage+32768) 
                       
      ELSE
        
        IF (timer = red_cr_check_steps) THEN
          
          CNT_ENABLE(0000b)
          current_red_cr_check_counts = CNT_READ(counter)
          Par_70 = Par_70 + current_red_cr_check_counts
                            
          DAC(e_aom_channel,  3277*e_off_voltage +32768)   'turn off red lasers
          DAC(fb_aom_channel, 3277*fb_off_voltage+32768)
          'DAC(repump_aom_channel, 3277*repump_off_voltage+32768) 
                        
          IF (cr_after_teleportation > 0) THEN    ' save the number of CR counts with teleportation event
            DATA_23[tele_event_id] = current_red_cr_check_counts
            cr_after_teleportation = 0
          ENDIF
                            
          IF (current_red_cr_check_counts < max_red_hist_cts) THEN      'make histograms
            ' FIXME -- else into last bin 
            
            IF (first_cr_probe_after_unsuccessful_lde > 0) THEN
              INC(DATA_7[current_red_cr_check_counts+1]) 'make histogram for only after unsuccessful lde
            ENDIF
            
            INC(DATA_8[current_red_cr_check_counts+1]) 'make histogram for all attempts
          ENDIF
          
          IF (cr_probe_timer > CR_probe_max_time) THEN
            current_cr_threshold = CR_threshold_prepare
            cr_probe_timer = 0
          ENDIF
                                      
          IF (current_red_cr_check_counts < current_cr_threshold) THEN
            INC(par_79)     'CR below threshold events
            mode = 1
            timer = -1
          ELSE
            first_cr_probe_after_unsuccessful_lde = 0
            CR_timer = time_before_forced_CR
            DATA_27[tele_event_id + 1] = current_red_cr_check_counts
            
            if ((do_N_polarization = 0) or (do_sequences = 0)) then
              mode = 4
            else
              mode = 3
            endif
                        
            timer = -1  
          ENDIF
        
        ENDIF
      
      ENDIF
      
    case 3 ' N polarization
      
      if (timer = 0) then
        DIGOUT(AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start the waiting sequence (decide element)
        CPU_SLEEP(9)
        DIGOUT(AWG_lt1_trigger_do_channel, 0)
      else
      
        AWG_LT1_in_was_high = AWG_LT1_in_is_high
        AWG_LT1_in_is_high = DIGIN(AWG_LT1_di_channel)
             
        IF ((AWG_LT1_in_was_high = 0) AND (AWG_LT1_in_is_high > 0)) THEN
          mode = 4
          timer = -1
        endif
        
      endif      
         
    case 4 'local CR OK, wait for remote
      
      ' todo: we could save the waiting times, or at least averages of them.
      IF (remote_mode = 2) THEN
        if (do_sequences = 0) then
          mode = 0 
          remote_mode = 0
        else      
          mode = 5
          wait_time = 5 ' we need to make sure that the AWG is receptive for triggering now!
          DATA_29[tele_event_id + 1] = CR_probe_timer   ' save CR timer just before LDE sequence -> put to after LDE later?
                    
          CR_time_lt2 = Min_long(CR_timer_lt2/1000, max_hist_CR_probe_time-1)+1
          INC(DATA_31[CR_time_lt2])
          
          CR_probe_time = Min_long(CR_probe_timer/1000, max_hist_CR_probe_time-1)+1
          INC(DATA_30[CR_probe_time])
          
        endif        
        timer = -1
      ENDIF      
    
    case 5
      
      if (timer = 0) then
        
        if (wait_time > 0) then
          timer = -1
          dec(DATA_28[mode+1]) ' correct statistics
        else
          inc(par_78)
          DIGOUT(AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start LDE
          CPU_SLEEP(9)
          DIGOUT(AWG_lt1_trigger_do_channel, 0)
        endif
        
      else
        
        AWG_LT1_in_was_high = AWG_LT1_in_is_high
        AWG_LT1_in_is_high = DIGIN(AWG_LT1_di_channel)
             
        IF ((AWG_LT1_in_was_high = 0) AND (AWG_LT1_in_is_high > 0)) THEN

          first_cr_probe_after_unsuccessful_lde = 1
          mode = 0
          timer = -1
          remote_mode = 0
          wait_time = 5
        endif
        
      endif
        
            
        
                    
    
  ENDSELECT
  '          
  INC(timer)
  Inc(CR_probe_timer)
  Inc(CR_timer_lt2)
  DEC(CR_timer)
  if (CR_timer < 0) then
    CR_timer = 0
  endif
  
  if (wait_time > 0) then
    dec(wait_time)
  endif
      
  'some criteria for stopping
  if (max_CR_starts > -1) then
    if (CR_starts >= max_CR_starts) then
      end
    endif
  endif
  
  if (max_successful_repetitions > -1) then
    if ((successful_repetitions >= max_successful_repetitions) or (successful_repetitions >= max_repetitions)) then
      end
    endif
  endif
  
  inc(par_60) ' the total time
  
FINISH:
  DAC(repump_aom_channel, 3277*repump_off_voltage+32768)   'turn off repump laser
  DAC(e_aom_channel, 3277*e_off_voltage + 32768)           'turn off Ey aom 
  DAC(fb_aom_channel, 3277*fb_off_voltage + 32768)         'turn off FB aom
  CNT_ENABLE(0000b)                          'turn off all counters
  DIGOUT(ADwin_LT2_trigger_do_channel,0)     'trigger to ADwin LT2
  DIGOUT(AWG_lt1_trigger_do_channel, 0)      'trigger to AWG LT1
  DIGOUT(AWG_lt1_event_do_channel, 0)        'event to AWG LT1
  DIGOUT(PLU_arm_do_channel, 0)              'PLU is not armed until just before LDE start trigger **????
  DIGOUT_BITS(0, AWG_lt2_address_all_in_bit) 'clear the output on the DO's that input to the strobe
  
