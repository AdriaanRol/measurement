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
' Info_Last_Save                 = TUD10238  TUD10238\localadmin
'<Header End>
' Teleportation master controller program. lt1 is in charge, lt2 is remote

' modes:
' 0 : do local red CR check
' 1 : do local yellow repumping / resonance check
' 2 : wait for N polarization
' 3 : local CR OK, wait for remote
' 4 : run LDE
' 5 : run nitrogen initialization, BSM
' 6 : do SSRO 1 + SP
' 7 : run nitrogen RO pulse
' 8 : do SSRO 2
' 9 : run U and RO basis rotation
' 10: wait for remote SSRO
''
' remote modes:
' 0 : start remote CR check
' 1 : remote CR check running
' 2 : remote CR OK, waiting

'
' Resources used:
'
' PARs:
' =====
' Inputs:
' 75 : CR threshold (first time)
' 76 : CR threshold (already prepared) *not yet included

' Outputs:
' 69 : cumulative counts during red check (LT1)
' 70 : cumulative counts during yellow repumping (LT1)
' 71 : below CR threshold events (LT1)
' 72 : number of CR checks performed (LT1)
' 73 : number of CR OK signals from LT2
' 74 : number of start CR triggers to LT2
' 77 : number of successful attempts
' 78 : number of LDE sequence starts
' 79 : timed out LDE sequences
' 80 : cumulative counts during RO1 (LT1)
' 68 : cumulative counts during RO2 (LT1)

' FPARs:
' ======
' Inputs:


' DATA:
' =====
' Inputs:
' DATA_20: integer parameters
'   1 : counter
'   2 : repump aom channel
'   3 : E aom channel
'   4 : A aom channel
'   5 : red CR check steps (no of process cycles)
'   6 : CR threshold (first time)
'   7 : CR threshold (already prepared)
'   8 : repump steps (no of process cycles)
'   9: LDE time before CR check force (no of process cycles)
'   10: teleportation repetitions
'   11: electron RO steps SSRO 1 (no of process cycles)
'   12: trigger out to ADWIN LT2 channel
'   13: trigger in from ADWIN LT2 channel
'   14: trigger AWG LT1 channel
'   15: sequence done in from AWG LT1 channel
'   16: arm PLU channel
'   17: trigger in from PLU channel
'   18: wait steps before SSRO1 (no of process cycles)
'   19: wait steps before Spin pumping (no of process cycles)
'   20: spin pumping before N readout steps (no of process cycles)
'   21: wait steps before SSRO2 (no of process cycles)
'   22: electron RO steps SSRO 2 (no of process cycles)
'   23: number of repetitions after which to repump 
'   24: CR repump (threshold for repump start)
'   25: AWG lt1 event channel

' DATA_21: float parameters
'   1 : repump voltage
'   2 : repump offset voltage (0V != no laser output (for buffer box -> now velocity 2 i.e. E)
'   3 : E CR voltage    'voltage on the E transition for charge resonance check 
'   4 : FB CR voltage   'voltage  on the forbidden transition for charge resonance check
'   5 : E SP voltage  
'   6 : FB SP voltage
'   7 : E RO voltage    
'   8 : FB RO voltage

' Outputs:
' DATA_7[max_red_hist_cts] (int)      : red CR count histogram after unsuccessful entanglement attempts
' DATA_8[max_red_hist_cts] (int)      : red CR count histogram after all attempts
' DATA_9[max_yellow_hist_cts] (int)   : yellow CR count histogram after unsuccessful entanglement attempts
' DATA_10[max_yellow_hist_cts] (int)  : yellow CR count histogram after all attempts
' DATA_23[max_repetitions] (int)      : CR counts after teleportation
' DATA_24[max_repetitions] (int)      : BSM SSRO 1 (electron) results
' DATA_25[max_repetitions] (int)      : PLU Bell states 
' DATA_26[max_repetitions] (int)      : BSM SSRO 2 (nitrogen) results
' DATA_27[max_repetitions] (int)      : CR counts before teleportation event

#INCLUDE ADwinGoldII.inc
#INCLUDE Math.inc

#DEFINE max_repetitions         10000          'the maximum number of datapoints taken
#DEFINE max_red_hist_cts        100                   ' dimension of photon counts histogram for red CR
#DEFINE max_yellow_hist_cts     100                ' dimension of photon counts histogram for yellow Resonance check

' parameters
DIM DATA_20[25] AS LONG               ' integer parameters
DIM DATA_21[10] AS FLOAT               ' float parameters
DIM DATA_7[max_red_hist_cts] AS LONG           ' histogram of counts during 1st red CR after timed-out lde sequence
DIM DATA_8[max_red_hist_cts] AS LONG           ' histogram of counts during red CR (all attempts)
DIM DATA_9[max_yellow_hist_cts] AS LONG        ' histogram of counts during 1st yellow CR after timed-out lde sequence
DIM DATA_10[max_yellow_hist_cts] AS LONG       ' histogram of counts during yellow CR (all attempts)
DIM DATA_23[max_repetitions] AS LONG    'CR counts after teleportation
DIM DATA_24[max_repetitions] AS LONG    'BSM SSRO 1 (electron) results
DIM DATA_25[max_repetitions] AS LONG    'PLU Bell states
DIM DATA_26[max_repetitions] AS LONG    'BSM SSRO2 (nitrogen) results
DIM DATA_27[max_repetitions] AS LONG    'CR check counts before teleportation event

' general variables
DIM i AS LONG ' counter for array initalization
DIM mode AS INTEGER
DIM remote_mode AS INTEGER
DIM timer AS LONG
DIM CR_timer AS LONG

' settings for CR checks and repumping
DIM counter AS LONG                      'select internal ADwin counter 1 - 4 for conditional readout (PSB lt1)
DIM repump_aom_channel AS LONG            'DAC channel for repump laser AOM
DIM repump_voltage AS FLOAT               'voltage of repump pulse
DIM repump_off_voltage AS FLOAT           'off-voltage of repump laser (0V is not 0W)
DIM e_aom_channel AS LONG 
DIM e_cr_voltage AS FLOAT
DIM e_sp_voltage AS FLOAT
DIM e_ro_voltage AS FLOAT
DIM fb_aom_channel AS LONG
DIM fb_cr_voltage AS FLOAT
DIM fb_sp_voltage AS FLOAT
DIM fb_ro_voltage AS FLOAT
DIM red_cr_check_steps AS LONG                        'how long to check, in units of process cycles (lt1)
DIM current_red_cr_check_counts AS LONG        
DIM current_repump_counts AS LONG 
DIM cr_check_count_threshold_prepare AS LONG          ' initial CR threshold for first resonance check (lt1)
DIM cr_check_count_threshold_probe AS LONG            'threshold for probe after sequence (charge check) (lt1)
DIM CR_repump AS LONG                                 ' CR repump threshold (typically 1 for yellow, >9000 for green)       
DIM repump_steps AS LONG                       'how long to rempump w/ yellow or green, in process cycles (lt1)
DIM current_cr_threshold AS LONG 
DIM first_cr_probe_after_unsuccessful_lde AS INTEGER  'first CR check after timed out lde sequence
DIM cr_after_teleportation AS INTEGER                 'first CR check after teleportation
DIM time_before_forced_CR AS LONG                     'time before forced CR check on LT1
DIM repump_after_repetitions AS LONG                  'number of max successive red CR checks, after which repump

'LDE sequence
DIM AWG_lt1_trigger_do_channel AS LONG
DIM AWG_lt1_event_do_channel AS LONG
DIM AWG_lt1_di_channel_in_bit AS LONG
DIM PLU_arm_do_channel AS LONG
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
DIM trigger_cr_dio_in_bit AS LONG 
DIM trigger_cr_dio_out AS LONG 
DIM strobe_input AS LONG  ' this is calculated from a function of RO1_ms_result, RO2_ms_result, PLU_Bell_state

' Teleportation
DIM tele_event_id AS LONG 
DIM teleportation_repetitions AS LONG

' misc
DIM DIO_register AS LONG 

'debug
DIM timervalue1 AS LONG
DIM timervalue2 AS LONG

DIM debug_CR_only AS LONG       'CR checking only
DIM debug_eSSRO_only AS LONG    'CR checking, one AWG sequence ('LDE'), and e SSRO only
DIM debug_NSSRO_only AS LONG    'CR checking, one AWG sequence ('LDE'), and CNOT + SSRO2 only

DIM A AS LONG

INIT:
  ' general
  mode = 0
  remote_mode = 0
  timer = 0
  cr_after_teleportation = 0
  tele_event_id = 1
  
  ' init statistics variables
  for i=1 to max_red_hist_cts
    DATA_7[i] = 0
    DATA_8[i] = 0
  next i
  
  for i=1 to max_yellow_hist_cts
    DATA_9[i] = 0
    DATA_10[i] = 0
  next i
  
  for i=1 to teleportation_repetitions
    DATA_23[i] = 0    'CR check counts after teleportation
    DATA_24[i] = 0    'SSRO1 results
    DATA_25[i] = 0    'PLU Bell state
    DATA_26[i] = 0    'SSRO2 results
    DATA_27[i] = 0    'CR check counts before event
  next i
  
  ' init variables
  counter = DATA_20[1]
  repump_aom_channel = DATA_20[2]
  e_aom_channel = DATA_20[3]
  fb_aom_channel = DATA_20[4]
  red_cr_check_steps = DATA_20[5]
  cr_check_count_threshold_prepare = DATA_20[6]
  cr_check_count_threshold_probe = DATA_20[7]
  repump_steps = DATA_20[8]
  time_before_forced_CR = DATA_20[9]
  teleportation_repetitions = DATA_20[10]
  electron_RO_steps = DATA_20[11]
  trigger_cr_dio_out = DATA_20[12]
  trigger_cr_dio_in_bit = DATA_20[13]
  AWG_lt1_trigger_do_channel = DATA_20[14]
  AWG_lt1_di_channel_in_bit = DATA_20[15]
  PLU_arm_do_channel = DATA_20[16]
  PLU_di_channel_in_bit = DATA_20[17]  
  wait_steps_before_RO1 = DATA_20[18]
  wait_steps_before_SP = DATA_20[19]
  spin_pumping_steps = DATA_20[20]
  wait_steps_before_RO2 = DATA_20[21]
  electron_RO2_steps = DATA_20[22]
  repump_after_repetitions = DATA_20[23]
  CR_repump = DATA_20[24]
  AWG_lt1_event_do_channel = DATA_20[25]
  
  repump_voltage = DATA_21[1]
  repump_off_voltage = DATA_21[2]
  e_cr_voltage = DATA_21[3]
  fb_cr_voltage = DATA_21[4]
  e_sp_voltage = DATA_21[5]
  fb_sp_voltage = DATA_21[6]
  e_ro_voltage = DATA_21[7]
  fb_ro_voltage = DATA_21[8]
  
  current_red_cr_check_counts = 0
  current_repump_counts = 0
  current_cr_threshold = cr_check_count_threshold_prepare
  first_cr_probe_after_unsuccessful_lde = 0
  cr_after_teleportation = 0
  PLU_Bell_state = -1
  current_RO1_counts = 0
  current_RO2_counts = 0
  RO1_ms_result = 0
  RO2_ms_result = 0
  


  ' prepare hardware
  par_60 = 0                      'debug par used for measuring timer
  par_62 = 0                      'debug par used for measuring timer
  par_63 = 0                      'debug par 
  par_64 = 0                      'debug par
  
  par_67 = cr_repump              
  par_68 = 0                      ' cumulative counts during RO2 (LT1)
  par_69 = 0                      ' cumulative counts during red CR check (LT1)
  par_70 = 0                      ' cumulative counts during yellow repumping (LT1)
  par_71 = 0                      ' CR below threshold events (LT1)
  par_72 = 0                      ' number of red CR checks performed (LT1)
  par_73 = 0                      ' number of CR OK signals from LT2
  par_74 = 0                      ' number of start CR triggers to LT2
  par_75 = cr_check_count_threshold_prepare
  par_76 = cr_check_count_threshold_probe
  par_77 = 0                      ' number of successful attempts
  par_78 = 0                      ' number of LDE sequence starts
  par_79 = 0                      ' number of timed out LDE sequences
  par_80 = 0                      ' cumulative counts during RO1 (LT1)

  DAC( repump_aom_channel, 3277*repump_off_voltage+32768) ' turn off green
  DAC( e_aom_channel, 32768)
  DAC( fb_aom_channel, 32768)
  CNT_ENABLE( 0000b)               'turn off all counters
  CNT_MODE( counter,00001000b)     'configure counter
  CONF_DIO( 11)                    'configure DIO 16:23 as input, all other ports as output
  DIGOUT( trigger_cr_dio_out,0)    'trigger to ADwin LT2
  DIGOUT( AWG_lt1_trigger_do_channel, 0) 'trigger to AWG LT1
  DIGOUT( AWG_lt1_event_do_channel, 0) 'trigger to AWG LT1
  DIGOUT( PLU_arm_do_channel, 0)   'PLU is not armed until just before LDE start trigger **????

  'debug
  timervalue1=0
  timervalue2=0
  par_60=0
  
  'pick one of the following debug modes (or set all to zero for the real thing)
  debug_CR_only = 1     'if 1: debug - CR checking only
  debug_eSSRO_only = 1 'if 1: debug - CR checking, single AWG sequence, and SSRO1 only
  
EVENT:
  
  timervalue1=timervalue2
  timervalue2=Read_timer()
  par_60 = Max_long((timervalue2-timervalue1),par_60)
  
  cr_check_count_threshold_prepare = par_75
  cr_check_count_threshold_probe = par_76
  
  DIO_register = DIGIN_EDGE(1)

  IF (((DIO_register) AND (trigger_cr_dio_in_bit)) > 0) THEN
    inc(par_64) 'debugging: this means that a trigger comes from ADWIN lt2 
  ENDIF 
  
  IF (((DIO_register) AND (PLU_di_channel_in_bit)) > 0) THEN
    inc(par_63) 'debugging: this means that a trigger comes from the PLU
  ENDIF 
  
  'If only one setup is used, remote_mode may be set to 2
  remote_mode = 2
  
  IF (par_77 = teleportation_repetitions) THEN
    END
  ENDIF
  
  selectcase remote_mode
    case 0 'start remote CR check
      INC(par_74)
      DIGOUT(trigger_cr_dio_out, 1)
      remote_mode = 1
                        
    case 1 'remote CR check running
      IF (((DIO_register) AND (trigger_cr_dio_in_bit)) > 0) THEN
        DIGOUT(trigger_cr_dio_out, 0)
        remote_mode = 2
        INC(par_73)
      ENDIF
    
    case 2 'remote CR OK, waiting
    
  endselect
  
  selectcase mode
    case 0 'do local red CR check
      INC(par_63)
      IF (timer = 0) THEN
        DIGOUT( AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start the waiting sequence
        CPU_SLEEP(9)      'sleep time is defined in units of 10 ns. We need >= 20 ns pulse width. 
        'adwin needs a value >= 9, so we set 9*10 ns sleep time
        DIGOUT( AWG_lt1_trigger_do_channel, 0) ' stop the trigger
      ENDIF       
      
      IF (((CR_timer > time_before_forced_CR) OR (cr_after_teleportation > 0)) OR (debug_CR_only > 0)) THEN
        IF (timer = 0) THEN
          INC(par_72)            'number of red CR checks performed
          CNT_ENABLE(0000b)    'turn off counter
          CNT_CLEAR(1111b)     'clear counter    
          CNT_ENABLE(1111b)    'enable counter
                
          DAC(e_aom_channel, 3277*e_cr_voltage+32768)   'turn on red lasers
          DAC(fb_aom_channel, 3277*fb_cr_voltage+32768)  
        ENDIF
        
        IF (timer = red_cr_check_steps) THEN
          CNT_ENABLE(0000b)
          current_red_cr_check_counts = CNT_READ(counter)
          par_69 = par_69 + current_red_cr_check_counts
                
          DAC(e_aom_channel, 32768)   'turn off red lasers
          DAC(fb_aom_channel, 32768) 
            
          IF (cr_after_teleportation > 0) THEN    'save the number of CR counts with teleportation event
            DATA_23[tele_event_id] = current_red_cr_check_counts
            cr_after_teleportation = 0
          ENDIF
                
          IF (current_red_cr_check_counts < max_red_hist_cts) THEN      'make histograms
            IF (first_cr_probe_after_unsuccessful_lde > 0) THEN
              INC(DATA_7[current_red_cr_check_counts+1]) 'make histogram for only after unsuccessful lde
            ENDIF
            INC(DATA_8[current_red_cr_check_counts+1]) 'make histogram for all attempts
          ENDIF
                
          IF (current_red_cr_check_counts < current_cr_threshold) THEN
            INC(par_71)     'CR below threshold events
            mode = 1        'go to yellow repumping
            timer = -1
          ELSE
            first_cr_probe_after_unsuccessful_lde = 0   'reset
            CR_timer = -1                               'reset the CR timer
            DATA_27[tele_event_id + 1] = current_red_cr_check_counts
            IF ((debug_CR_only > 0) OR (debug_eSSRO_only > 0)) THEN        'debug without N pol
              mode = 3         'skip nitrogen polarization and go to sequence.
              IF (debug_CR_only > 0) THEN
                INC(par_77)   'par_77 is the number of successful attempts. 
                'For debug_CR_only a success is performing a CR check on LT1.
                'Later this could be changed to a successful CR check.
              ENDIF
            ELSE
              mode = 2         'go to wait for N polarization
            ENDIF
            timer = -1
          ENDIF
        ENDIF
      ELSE 
        
        mode = 3        'we do not need to check CR if we are not timed out!
        timer = -1
      ENDIF
    
    case 1 'yellow repump / resonance check
      IF (timer = 0) THEN
        IF ((Mod(teleportation_repetitions,repump_after_repetitions)=0) OR (current_red_cr_check_counts < CR_repump))  THEN  'only repump after x SSRO repetition          CNT_ENABLE(0000b)    'turn off counter
          CNT_CLEAR(1111b)     'clear counter    
          CNT_ENABLE(1111b)    'enable counter       
          DAC( repump_aom_channel, 3277*repump_voltage+32768)
        ENDIF
      ELSE
        IF (timer = repump_steps) THEN
          CNT_ENABLE( 0000b)     'turn off counter
          current_repump_counts = CNT_READ( counter)
          par_70 = par_70 + current_repump_counts 
          DAC( repump_aom_channel, 3277*repump_voltage+32768)
                    
          IF (current_repump_counts < max_yellow_hist_cts) THEN      'make histograms
            IF (first_cr_probe_after_unsuccessful_lde > 0) THEN
              INC(DATA_9[current_repump_counts+1])
            ENDIF
            INC(DATA_10[current_repump_counts+1])
          ENDIF
          first_cr_probe_after_unsuccessful_lde = 0       'reset
          mode = 0 
          timer = -1
        ENDIF
      ENDIF             
    
    case 2 'wait for N polarization
      IF (timer = 0) THEN
        DIGOUT( AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start the waiting sequence
        CPU_SLEEP(9)      'sleep time is defined in units of 10 ns. We need >= 20 ns pulse width. 
        'adwin needs a value >= 9, so we set 9*10 ns sleep time
        DIGOUT( AWG_lt1_trigger_do_channel, 0) ' stop the trigger
      ELSE       
        IF (((DIO_register) AND (AWG_lt1_di_channel_in_bit)) > 0) THEN 
          mode = 3
          timer = -1
        ENDIF      
      ENDIF
          
    case 3 'local CR OK, wait for remote
      IF (remote_mode = 2) THEN
        IF (debug_CR_only = 1) THEN
          mode = 0
          remote_mode = 0
        ELSE
          mode = 4
        ENDIF
        timer = -1
      ENDIF  
    
    
    case 4 'run LDE
      IF (timer = 0) THEN
        'DIGOUT_BITS( strobe_channel_LDE, 1)   ' put a voltage on the right strobe channel
        DIGOUT( PLU_arm_do_channel, 1)         ' arm the PLU - or should this happen earlier?
        DIGOUT( AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start the waiting sequence
        CPU_SLEEP(9)      'sleep time is defined in units of 10 ns. We need >= 20 ns pulse width. 
        'adwin needs a value >= 9, so we set 9*10 ns sleep time
        DIGOUT( AWG_lt1_trigger_do_channel, 0) ' stop the trigger
        INC(par_78)       'number of LDE sequence starts
        IF (debug_eSSRO_only = 1) THEN 'go to mode 5 'wait for AWG done' without waiting for PLU trigger
          mode = 5 
          timer = -1
        ENDIF
        
      ELSE
        IF (((DIO_register) AND (PLU_di_channel_in_bit)) > 0) THEN 'receive trigger from PLU
          PLU_Bell_state = ((DIO_register) AND (PLU_di_channel_in_bit))  'this supposedly tells us which Bell state is generated
          DATA_25[tele_event_id] = PLU_Bell_state
          timer = -1
          mode = 5 'go to N init, BSM
        ELSE
          IF (((DIO_register) AND (AWG_lt1_di_channel_in_bit)) > 0) THEN 'receive trigger from AWG 1
            INC(par_79)
            first_cr_probe_after_unsuccessful_LDE = 1
            mode = 0 'try if CR_LT1 time > max_LDE_time, and then CR check
            remote_mode = 0 'CR check on LT2
            timer = -1
          ENDIF
        ENDIF
      ENDIF
            
    case 5 'run nitrogen initialization, BSM
      IF (((DIO_register) AND (AWG_lt1_di_channel_in_bit)) > 0) THEN 
        mode = 6 'got to SSRO 1 + SP
        timer = -1
      ENDIF
      
    
    case 6 'do SSRO 1 + SP
      IF (timer = wait_steps_before_RO1) THEN
        CNT_ENABLE(0000b)    'turn off counter
        CNT_CLEAR(1111b)     'clear counter    
        CNT_ENABLE(1111b)    'enable counter
        DAC(e_aom_channel,3277*e_ro_voltage+32768)
      ENDIF
      
      IF (timer =  wait_steps_before_RO1 + electron_ro_steps) THEN
        CNT_ENABLE(0000b)    'turn off counter
        DAC(e_aom_channel,32768)
        current_RO1_counts = CNT_READ(counter)
        par_80 = par_80 + current_RO1_counts 'accumulated SSRO counts
        IF (current_RO1_counts > 0) THEN
          INC(DATA_24[tele_event_id]) 'here I save 1 for 'click', which is thus m_s=0. Agrees with current analysis scripts
          RO1_ms_result = 0           'this on contrary is the ms state m_s=0
        ELSE
          RO1_ms_result = 1           'this is the ms state m_s=-1
        ENDIF
        IF (debug_eSSRO_only = 1) THEN
          cr_after_teleportation = 1
          INC(par_77)
          INC(tele_event_id)
          mode = 0
          remote_mode = 0
          timer =-1
        ENDIF
      ENDIF
      
      IF (timer = wait_steps_before_RO1 + electron_ro_steps + wait_steps_before_SP) THEN
        DAC(e_aom_channel,3277*fb_sp_voltage+32768)
      ENDIF
      
      IF (timer = wait_steps_before_RO1 + electron_ro_steps + wait_steps_before_SP + spin_pumping_steps) THEN
        DAC(e_aom_channel,32768)
        mode = 7 'got to nitrogen RO pulse
        timer = -1
      ENDIF

        
    case 7 'run nitrogen RO pulse
      IF (timer = 0) THEN
        DIGOUT( AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start the waiting sequence
        CPU_SLEEP(9)      'sleep time is defined in units of 10 ns. We need >= 20 ns pulse width. 
        'adwin needs a value >= 9, so we set 9*10 ns sleep time
        DIGOUT( AWG_lt1_trigger_do_channel, 0) ' stop the trigger
      
      ELSE
        IF (((DIO_register) AND (AWG_lt1_di_channel_in_bit)) > 0) THEN 'receive trigger from AWG 1
          mode = 8
          timer = -1
        ENDIF
      ENDIF
        
    case 8 'do SSRO 2
      IF (timer = wait_steps_before_RO2) THEN
        CNT_ENABLE(0000b)    'turn off counter
        CNT_CLEAR(1111b)     'clear counter    
        CNT_ENABLE(1111b)    'enable counter
        DAC(e_aom_channel,3277*e_ro_voltage+32768)
      ENDIF
      
      IF (timer =  wait_steps_before_RO2 + electron_RO2_steps) THEN
        CNT_ENABLE(0000b)    'turn off counter
        DAC(e_aom_channel,32768)
        current_RO2_counts = CNT_READ(counter)
        par_68 = par_68 + current_RO1_counts 'accumulated SSRO counts
        IF (current_RO2_counts > 0) THEN
          INC(DATA_26[tele_event_id]) 'here I save 1 for 'click', which is thus m_s=0, (m_I=0). Agrees with current analysis scripts
          RO2_ms_result = 0           'this on contrary is the ms state m_s=0
        ELSE
          RO2_ms_result = 1           'this is the ms state m_s=-1
        ENDIF
        IF (debug_NSSRO_only = 1) THEN
          cr_after_teleportation = 1
          INC(par_77)
          INC(tele_event_id)
          mode = 0
          remote_mode = 0
          timer = -1
        ELSE
          mode = 9 
          timer = -1
        ENDIF
      ENDIF
            
    case 9 'run U and RO basis rotation
      IF (timer = 0) THEN
        strobe_input = 1 ' this should be a function of RO1_ms_result, RO2_ms_result, PLU_Bell_state
        'DIGOUT( strobe_channel_right_U, 1)              ' put a voltage on the right strobe channel
      ENDIF
     
    case 10'wait for remote SSRO

  endselect
  
  
  INC(timer)
  INC(CR_timer)
  
  


  
  
