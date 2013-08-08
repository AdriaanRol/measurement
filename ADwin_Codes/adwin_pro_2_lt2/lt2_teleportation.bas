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
' this program implements the part of the teleportation protocol controlled by ADwin Pro II
' ADwin Gold II is in charge of the experiment.
'
' protocol:
' mode  0:  green pumping, 
'           photon counting just for statistics
' mode  1:  Ex/A pulse, photon counting  ->  CR check
'           fail: -> mode 0
' mode  2:  CR check OK, waiting
' mode  3:  SSRO
' mode  4:  SSRO OK, waiting

#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc
' #Include Math.inc

#DEFINE max_repetitions   20000
#DEFINE max_CR_hist_bins    100
#DEFINE max_stat             10

DIM DATA_20[25] AS LONG                             ' integer parameters
DIM DATA_21[15] AS FLOAT                            ' float parameters
DIM DATA_22[max_repetitions] AS LONG AT EM_LOCAL    ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG  AT EM_LOCAL   ' CR counts after sequence
DIM DATA_24[max_CR_hist_bins] AS LONG AT EM_LOCAL   ' CR counts
DIM DATA_25[max_repetitions] AS LONG AT DRAM_EXTERN ' SSRO counts
DIM DATA_26[max_stat] AS LONG AT EM_LOCAL           ' statistics

DIM counter_channel AS LONG
DIM repump_laser_DAC_channel AS LONG
DIM Ex_laser_DAC_channel AS LONG
DIM A_laser_DAC_channel AS LONG
DIM ADwin_lt1_di_channel AS LONG       'this is in channel of ADwin Pro, from Adwin lt1
DIM ADwin_lt1_do_channel AS LONG              'this is out channel of ADwin Pro, to Adwin lt1
DIM ADwin_lt1_di_channel_in_bit as LONG
DIM AWG_lt2_di_channel AS LONG
DIM AWG_lt2_di_channel_in_bit AS LONG
DIM repump_duration AS LONG
DIM CR_duration AS LONG
DIM teleportation_repetitions AS LONG
DIM SSRO_duration AS LONG
DIM repump_after_repetitions AS LONG

DIM repump_voltage AS FLOAT
DIM repump_off_voltage AS FLOAT
DIM Ex_CR_voltage AS FLOAT
DIM A_CR_voltage AS FLOAT
DIM Ex_SP_voltage AS FLOAT
DIM A_SP_voltage AS FLOAT
DIM Ex_RO_voltage AS FLOAT
DIM A_RO_voltage AS FLOAT
DIM Ex_off_voltage AS FLOAT
DIM A_off_voltage AS FLOAT

DIM timer, mode, i AS LONG
DIM tele_event_id AS LONG
DIM total_repump_counts AS LONG
DIM counter_pattern AS LONG
DIM counts, cr_counts AS LONG
DIM current_ssro_counts AS LONG
DIM cr_after_teleportation AS LONG
DIM time_start, time_stop AS LONG

'DIM ADwin_switched_to_high AS LONG
DIM ADwin_in_is_high AS LONG
DIM ADwin_in_was_high AS LONG
'DIM AWG_switched_to_high AS LONG
DIM AWG_in_is_high AS LONG
DIM AWG_in_was_high AS LONG
DIM Alternating AS LONG

DIM current_cr_threshold AS LONG
DIM CR_probe AS LONG
DIM CR_preselect AS LONG
DIM CR_repump AS LONG

INIT:
  counter_channel              = DATA_20[1]
  repump_laser_DAC_channel     = DATA_20[2]
  Ex_laser_DAC_channel         = DATA_20[3]
  A_laser_DAC_channel          = DATA_20[4]
  repump_duration              = DATA_20[5]
  CR_duration                  = DATA_20[6]
  CR_preselect                 = DATA_20[7]
  teleportation_repetitions    = DATA_20[8]
  SSRO_duration                = DATA_20[9]
  CR_probe                     = DATA_20[10]
  repump_after_repetitions     = DATA_20[11]
  CR_repump                    = DATA_20[12]
  ADwin_lt1_do_channel         = DATA_20[13]
  ADwin_lt1_di_channel         = DATA_20[14]
  AWG_lt2_di_channel           = DATA_20[15]
    
  repump_voltage               = DATA_21[1]
  repump_off_voltage           = DATA_21[2]
  Ex_CR_voltage                = DATA_21[3]
  A_CR_voltage                 = DATA_21[4]
  Ex_SP_voltage                = DATA_21[5]
  A_SP_voltage                 = DATA_21[6]
  Ex_RO_voltage                = DATA_21[7]
  A_RO_voltage                 = DATA_21[8]
  Ex_off_voltage               = DATA_21[9]
  A_off_voltage                = DATA_21[10]
   
  FOR i = 1 TO max_repetitions
    DATA_22[i] = 0
    DATA_23[i] = 0
    DATA_25[i] = 0
  NEXT i
  
  FOR i = 1 TO max_CR_hist_bins
    DATA_24[i] = 0
  NEXT i

  FOR i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT i
  
  counter_pattern = 2 ^ (counter_channel-1)
  ADwin_lt1_di_channel_in_bit = 2^ADwin_lt1_di_channel
  AWG_lt2_di_channel_in_bit = 2^AWG_lt2_di_channel
  
  total_repump_counts     = 0
  tele_event_id           = 0
  cr_after_teleportation  = 0
  current_ssro_counts     = 0
  counts                  = 0
  cr_counts               = 0
  
  ADwin_in_was_high      = 0
  ADwin_in_is_high       = 0
  AWG_in_was_high      = 0
  AWG_in_is_high       = 0
  Alternating           = 0
  'ADwin_switched_to_high = 0

  P2_DAC(DAC_MODULE, repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter_channel,00001000b) 'configure counter
  P2_Digprog(DIO_MODULE, 11)
  P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 0)

  mode = 2
  timer = 0
  
  fpar_63 = 0                      ' debug fpars
  fpar_64 = 0       
  fpar_65 = 0
  
  par_64 = 0                      ' current mode
  par_65 = 0                      ' timer value
  par_66 = 0                      ' number of repumps
  par_67 = 0                      ' number of CR times CR failed.
  par_68 = CR_probe
  par_69 = CR_repump  
  PAR_70 = 0                      ' cumulative counts during red CR check (LT2)
  PAR_71 = 0                      ' below CR threshold events (LT2)
  PAR_72 = 0                      ' number of CR checks performed (LT2)
  PAR_73 = 0                      ' number of CR OK signals to ADwin LT1
  PAR_74 = 0                      ' number of start CR triggers from ADwin LT1
  par_75 = CR_preselect
  par_76 = 0                      ' cumulative counts during repumping
  Par_77 = 0                      ' teleportation_repetitions
  Par_78 = 0                      ' number of start SSRO triggers from AWG LT2
  Par_79 = 0                      ' cumulative counts during SSRO (LT2)
  Par_80 = 0                      ' number of SSRO done signals to ADwin LT1

  current_cr_threshold = CR_preselect
  
EVENT:
  CR_preselect                 = PAR_75
  CR_probe                     = PAR_68
  CR_repump                    = PAR_69
  
  par_64 = mode
  par_65 = timer
  
  fpar_63 = repump_voltage
  fpar_64 = A_CR_voltage
  fpar_65 = Ex_CR_voltage 
  
  
  if (timer = 0) then
    INC(DATA_26[mode+1]) 'gather statistics on how often entered this mode.
  endif
    
  SELECTCASE mode
    
    CASE 0' repump
            
      IF (timer = 0) THEN
        inc(par_66)
        
        IF (cr_counts < CR_repump)  THEN  'only repump after x SSRO repetitions
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE, repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on green
        ELSE
          mode = 1
          timer = -1
          current_CR_threshold = CR_preselect
        ENDIF
                
      ELSE 
        
        IF (timer = repump_duration) THEN
          P2_DAC(DAC_MODULE, repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          P2_CNT_ENABLE(CTR_MODULE, 0)
          total_repump_counts = total_repump_counts + counts
          PAR_76 = total_repump_counts
          
          mode = 1
          timer = -1
          current_CR_threshold = CR_preselect
        ENDIF
      
      ENDIF
    
    CASE 1    ' Ex/A laser CR check
                  
      IF (timer = 0) THEN
        P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_CR_voltage+32768) ' turn on Ex laser
        P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
        P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
        P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
        inc(par_72)       'total CR checks performed
      ELSE 
        
        IF (timer = CR_duration) THEN
          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
          P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
          cr_counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          P2_CNT_ENABLE(CTR_MODULE, 0)  'turn off counter
          PAR_70 = PAR_70 + cr_counts
                    
          IF (cr_after_teleportation > 0) THEN ' first CR after lt2 SSRO i.e. teleportation
            DATA_23[tele_event_id] = cr_counts
            cr_after_teleportation = 0
          ENDIF
                  
          IF (cr_counts < current_cr_threshold) THEN
            mode = 0
            inc(par_71)
          ELSE
            DATA_22[tele_event_id+1] = counts  ' CR before next SSRO sequence
            P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 1)
            mode = 2
            current_cr_threshold = CR_probe
          ENDIF
                  
          timer = -1
        ENDIF      
      ENDIF
     
    case 2      'CR ok, waiting
      
      IF (Alternating = 0) THEN 
        
        'checking all the time if adwin switched to high during last round. 
        Alternating = 1     
        ADwin_in_was_high = ADwin_in_is_high    'copies information from last round
        ADwin_in_is_high = ((P2_DIGIN_LONG(DIO_MODULE)) AND (ADwin_lt1_di_channel_in_bit))
                
        IF ((ADwin_in_was_high = 0) AND (ADwin_in_is_high > 0)) THEN 'Adwin triggers to start CR
          P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 0) ' stop triggering CR done
          INC(par_74)     'Triggers to start CR
          mode = 1
          timer = -1
        ENDIF
                        
      ELSE
        
        Alternating = 0    
        AWG_in_was_high = AWG_in_is_high    'copies information from last round
        AWG_in_is_high = ((P2_DIGIN_LONG(DIO_MODULE)) AND (AWG_lt2_di_channel_in_bit))
                 
        ' TODO: we need a flag whether to do SSRO (not needed for TPQI, for instance)
        IF ((AWG_in_was_high = 0) AND (AWG_in_is_high > 0)) THEN  'AWG triggers to start SSRO
          P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 0)
          INC(par_78) 'Triggers to start SSRO
          mode = 3
          timer = -1                              
        ENDIF
        
      ENDIF              
                 
    case 3
      
      if (timer = 0) then
        P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    ' clear counter
        ' P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
        ' P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on readout laser
      
      else
      
        IF (timer = SSRO_duration) THEN
          P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 1) ' Notify ADwin LT1 that we're done.
          INC(Par_80)   ' number of SSRO done signals to ADwin lt1.
          INC(par_77)   ' number of succesful teleportations.
          INC(tele_event_id)
          
          IF (tele_event_id = teleportation_repetitions) THEN
            END
          ENDIF
          
          cr_after_teleportation = 1
          mode = 4
          timer = -1
        endif
                
      endif
      
    case 4
                 
      'checking all the time if adwin switched to high during last round.       
      ADwin_in_was_high = ADwin_in_is_high    'copies information from last round       
      ADwin_in_is_high = ((P2_DIGIN_LONG(DIO_MODULE)) AND (ADwin_lt1_di_channel_in_bit))

      IF ((ADwin_in_was_high = 0) AND (ADwin_in_is_high > 0)) THEN 'Adwin triggers to start CR
        P2_DIGOUT( DIO_MODULE, ADwin_lt1_do_channel, 0)
        INC(par_74)     'Triggers to start CR
        mode = 0
        timer = -1
      ENDIF
          
      '      IF (timer = 0) THEN
      '        P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
      '        P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
      '        P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_RO_voltage+32768) ' turn on readout laser
      '      ELSE
      '        IF (timer = SSRO_duration) THEN
      '          current_ssro_counts = P2_CNT_READ(CTR_MODULE, counter_channel)
      '          P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off readout laser
      '          P2_CNT_ENABLE(CTR_MODULE, 0)    'turn off counter
      '
      '          par_68 = par_68 + current_ssro_counts 'accumulated SSRO counts
      '          IF (current_ssro_counts > 0) THEN
      '            INC(DATA_25[tele_event_id]) 'here I save 1 for 'click', which is thus m_s=0, (m_I=0). Agrees with current analysis scripts
      '          ENDIF
      '          P2_DIGOUT( DIO_MODULE, ADwin_lt1_do_channel, 1)
      '          INC(Par_80)   ' number of SSRO done signals to ADwin lt1.
      '          INC(par_77)   ' number of succesful teleportations.
      '          INC(tele_event_id)
      '          IF (tele_event_id = teleportation_repetitions) THEN
      '            END
      '          ENDIF
      '          cr_after_teleportation = 1
      '          mode = 4
      '          timer = -1
      '        ENDIF
      '      ENDIF
      '      
      '    case 4
      '      INC(DATA_26[mode+1]) 'gather statistics on how often entered this mode.
      '      
      '      IF (ADwin_switched_to_high > 0) THEN  'Adwin triggers to start CR
      '        P2_DIGOUT( DIO_MODULE, ADwin_lt1_do_channel, 0)
      '        INC(par_74)     'Triggers to start CR
      '        mode = 0
      '        timer = -1
      '      ENDIF
      '
     
  endselect
  
  INC(timer)
        
FINISH:
  P2_DAC(DAC_MODULE, repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE, Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser
  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 0)
