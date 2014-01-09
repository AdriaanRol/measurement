'<ADbasic Header, Headerversion 001.001>
' Foldings                       = 313
'<Header End>
' this program implements CR check fully controlled by ADwin Pro II
'
' protocol:
' mode  0:  green pulse, 
'           photon counting just for statistics
' mode  1:  E/A pulse, photon counting  ->  CR check
'           fail: -> mode 0


#DEFINE max_stat           10
#DEFINE max_repetitions 500000
#DEFINE max_CR_duration   250
#DEFINE max_repump_duration 2000
#DEFINE position_scan_length 100
#DEFINE pos_mod_min_dac 1
#DEFINE pos_mod_max_dac 3
#DEFINE pos_mod_min_dac_v 0.0
#DEFINE pos_mod_max_dac_v 10.0

'init
DIM DATA_30[100] AS LONG               ' CR integer parameters
DIM DATA_31[100] AS FLOAT              ' CR float parameters

DIM DATA_17[position_scan_length] AS FLOAT 'repump freq voltage sine
DIM DATA_18[max_repump_duration] AS FLOAT 'AT EM_LOCAL 'repump freq voltage sine
DIM DATA_19[max_CR_duration] AS FLOAT 'AT EM_LOCAL 'CR gate voltage sine

'return
'used in cr.inc
DIM DATA_22[max_repetitions] AS LONG  ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG ' CR counts after sequence
DIM DATA_26[max_stat] AS LONG         ' statistics

DIM cr_mode, cr_timer, cr_i AS LONG
DIM cr_counts, cr_old_counts AS LONG
DIM CR_probe, CR_preselect, CR_repump, current_CR_threshold AS LONG
DIM repumps, CR_failed, total_repump_counts AS LONG
DIM repump_duration, CR_duration AS LONG
DIM cr_wait_after_pulse, cr_wait_after_pulse_duration AS LONG
DIM counter_channel, counter_pattern AS LONG
DIM E_laser_DAC_channel, A_laser_DAC_channel, repump_laser_DAC_channel AS LONG

DIM repump_mod_DAC_channel, cr_mod_DAC_channel AS LONG
DIM repump_mod_activated, cr_mod_activated AS LONG
DIM pos_mod_DAC_channel, pos_mod_timer, pos_mod_activated AS LONG

DIM repump_voltage, repump_off_voltage, E_CR_voltage, A_CR_voltage, E_off_voltage, A_off_voltage AS FLOAT

DIM cr_mod_control_offset, cr_mod_control_amp, cr_mod_control AS FLOAT
DIM repump_mod_control,repump_mod_control_offset, repump_mod_control_amp AS FLOAT
DIM pos_mod_control_offset, pos_mod_control_amp, pos_mod_control, pos_mod_fb AS FLOAT
DIM pos_mod_control_offset_x, pos_mod_control_offset_y, pos_mod_control_offset_z AS FLOAT
DIM pos_mod_err, pos_mod_min_err AS FLOAT


SUB init_CR()
  counter_channel              = DATA_30[1]
  repump_laser_DAC_channel     = DATA_30[2]
  E_laser_DAC_channel          = DATA_30[3] ' this is also used in the main script i.e. MBI_lt2 for ssro, more logical to define there? -machiel 30-12-'13
  A_laser_DAC_channel          = DATA_30[4]
  repump_duration              = DATA_30[5]
  CR_duration                  = DATA_30[6]
  cr_wait_after_pulse_duration = DATA_30[7]
  CR_preselect                 = DATA_30[8]
  CR_probe                     = DATA_30[9]
  CR_repump                    = DATA_30[10]
  repump_mod_DAC_channel       = DATA_30[11] '4
  cr_mod_DAC_channel           = DATA_31[12] '5

  repump_voltage               = DATA_31[1]
  repump_off_voltage           = DATA_31[2]
  E_CR_voltage                 = DATA_31[3]
  A_CR_voltage                 = DATA_31[4]
  E_off_voltage                = DATA_31[5]
  A_off_voltage                = DATA_31[6]
  repump_mod_control_offset    = DATA_31[7]  '5.0
  repump_mod_control_amp       = DATA_31[8]  '1.0 - 2.0
  cr_mod_control_offset        = DATA_31[9]  '0.0
  cr_mod_control_amp           = DATA_31[10] '0.1 
  pos_mod_control_offset_x     = DATA_31[11]  
  pos_mod_control_offset_y     = DATA_31[12]
  pos_mod_control_offset_z     = DATA_31[13]
  pos_mod_control_amp          = DATA_31[14] '0.03
  pos_mod_fb                   = DATA_31[15] '0.1
  pos_mod_min_err              = DATA_31[16] '300
  
  FOR cr_i = 1 TO max_repetitions
    DATA_22[i] = 0
    DATA_23[i] = 0
  NEXT cr_i
  FOR cr_i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT cr_i
  'fill data_18 with a sine for repump mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR cr_i = 1 TO repump_duration
    DATA_18[i] = Sin(-3.14+2*3.14*i/repump_duration)
  NEXT cr_i
  'fill data_19 with a sine for cr mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR cr_i = 1 TO CR_duration
    DATA_19[i] = Sin(-3.14+2*3.14*i/CR_duration)
  NEXT cr_i
  'fill data_17 with a sine for repump mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR cr_i = 1 TO position_scan_length
    DATA_17[i] = Sin(-3.14+2*3.14*i/position_scan_length)
  NEXT cr_i
  pos_mod_timer = 0
  
  counter_pattern     = 2 ^ (counter_channel-1)
  total_repump_counts = 0
  CR_failed           = 0
  repumps             = 0
  cr_wait_after_pulse    = 0
  cr_mode = 0
  cr_timer = 0
  
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' number of repumps
  PAR_72 = 0                      ' number of CR checks performed (lt1)
  Par_75 = CR_preselect
  Par_68 = CR_probe
  par_69 = CR_repump
  par_76 = 0                      ' cumulative counts during repumping
  par_79 = 0                      ' CR below treshold events
  
  
  FPar_78 = 0.0                   ' current repump modulation error signal
  FPar_79 = 0.0                   ' current CR modulation error signal
  par_62 = 0                      ' activate repump modulation
  par_63 = 0                      ' activate cr gate modulation
  
  par_60 = pos_mod_min_dac        ' current position modulation dac
  par_61 = 0                      ' activate position modulation
  FPar_60 = 0.0                   ' current position modulation error signal
ENDSUB



FUNCTION CR_check(first_cr, repetition_index) As LONG

  CR_check = 0
  
  IF (cr_wait_after_pulse > 0) THEN
    DEC(cr_wait_after_pulse)
  ELSE

    SELECTCASE cr_mode 
      CASE 0    ' green repump
              
        IF (cr_timer = 0) THEN
          CR_repump                    = PAR_69
          PAR_60                       = pos_mod_DAC_channel 
          pos_mod_activated            = PAR_61
          repump_mod_activated         = PAR_62
          FPar_60                      = pos_mod_err
          
          IF (cr_counts < CR_repump)  THEN  'only repump 
            CNT_CLEAR(counter_pattern)    'clear counter
            CNT_ENABLE(counter_pattern)    'turn on counter
            DAC(repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on green
            repumps = repumps + 1
            inc(par_71)
            '------------repump modulation control
            cr_old_counts = 0
            cr_i=2
            repump_mod_control_amp = -1.0*repump_mod_control_amp
            '--------------------------------
          ELSE
            cr_mode = 1
            cr_timer = -1
            current_CR_threshold = CR_preselect
          ENDIF
          
          '------------pos modulation control
          IF (pos_mod_activated > 0) THEN
            IF (pos_mod_timer< position_scan_length) THEN
              INC(pos_mod_timer)
            ELSE
              IF ((pos_mod_err< pos_mod_min_err) AND (pos_mod_err > (-1.0*pos_mod_min_err))) THEN
                pos_mod_err = 0.0
                IF (pos_mod_DAC_channel < pos_mod_max_dac) THEN
                  INC(pos_mod_DAC_channel)
                ELSE
                  pos_mod_DAC_channel = pos_mod_min_dac
                  PAR_61 = 0 'pos_mod_activated = 0
                ENDIF
              ENDIF
              pos_mod_timer = 1
            ENDIF
            pos_mod_control = DATA_17[pos_mod_timer]
            pos_mod_control_offset = pos_mod_control_offset + (pos_mod_fb * pos_mod_err / repump_duration / 10000000. )
            IF ((pos_mod_control_offset > pos_mod_min_dac_v) AND (pos_mod_control_offset < pos_mod_max_dac_v)) THEN
              DAC(pos_mod_DAC_channel, 3277*(pos_mod_control_amp*pos_mod_control+pos_mod_control_offset)+32768) ' put current voltage on freq mod aom
            ENDIF
          ELSE
            IF (pos_mod_timer > 1) THEN
              pos_mod_timer = 1
              DAC(pos_mod_DAC_channel, 3277*(pos_mod_control_offset)+32768)
            ENDIF
          ENDIF
          '--------------------------------
        
        ELSE 
          
          IF (cr_timer = repump_duration) THEN
            
            DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
            cr_counts = CNT_READ(counter_channel)
            CNT_ENABLE(0)
            CNT_CLEAR(counter_pattern)
            
            total_repump_counts = total_repump_counts + cr_counts
            PAR_76 = total_repump_counts
            
            cr_mode = 1
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration
            current_cr_threshold = CR_preselect
            
            'pos mod control---------
            IF (pos_mod_activated > 0)  THEN
              pos_mod_err = pos_mod_err*0.9999+pos_mod_control*(cr_counts)
            ENDIF
            '------------------------
            
          ELSE 
            IF (repump_mod_activated>0) THEN
              '------------repump modulation control
              IF (cr_i = 0) THEN
                cr_i = 2
                repump_mod_control=DATA_18[cr_timer]
                DAC(repump_mod_DAC_channel, 3277*(repump_mod_control_amp*repump_mod_control+repump_mod_control_offset)+32768) ' put current voltage on freq mod aom
              ELSE
                cr_counts = CNT_READ(counter_channel)
                FPar_78=FPar_78*0.9999+repump_mod_control*(cr_counts-cr_old_counts)
                cr_old_counts=cr_counts
              ENDIF
              DEC(cr_i)
            ENDIF          
          ENDIF
        ENDIF
      
      CASE 1    ' E/A laser CR check
        
        IF (cr_timer = 0) THEN
          CR_preselect                 = PAR_75
          CR_probe                     = PAR_68
          cr_mod_activated             = PAR_63
          DAC(E_laser_DAC_channel, 3277*E_CR_voltage+32768) ' turn on E laser
          DAC(A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          INC(PAR_72)
          '------------cr modulation control
          cr_old_counts = 0
          cr_mod_control_amp = -1.0*cr_mod_control_amp
          cr_i=2
          '-------
        ELSE 
          
          IF (cr_timer = CR_duration) THEN
            DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            cr_counts = CNT_READ(counter_channel)
            CNT_ENABLE(0)
            CNT_CLEAR(counter_pattern)
            PAR_70 = PAR_70 + cr_counts
            
            IF (first_cr > 0) THEN ' first CR after SSRO sequence
              DATA_23[repetition_index] = cr_counts
            ENDIF
                      
            IF ((cr_counts < current_cr_threshold) OR (par_61 > 0)) THEN
              cr_mode = 0
              inc(CR_failed)
              inc(PAR_79)
            ELSE
              cr_mode = 1
              CR_check = 1
              DATA_22[repetition_index+1] = cr_counts  ' CR before nEt SSRO sequence
              current_cr_threshold = CR_probe
            ENDIF
            
            'pos mod control---------
            IF (pos_mod_activated > 0)  THEN
              pos_mod_err = pos_mod_err*0.9999+pos_mod_control*(cr_counts)
            ENDIF
            '------------------------
            
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration
          ELSE
            IF (cr_mod_activated > 0) THEN
              '------------cr modulation control
              IF (cr_i = 0) THEN
                cr_i = 2
                cr_mod_control=DATA_19[cr_timer] 
                DAC(cr_mod_DAC_channel, 3277*(cr_mod_control_amp*cr_mod_control+cr_mod_control_offset)+32768) ' put current voltage on gate
              ELSE
                cr_counts = CNT_READ(counter_channel)
                FPar_79 = FPar_79*0.99999+cr_mod_control*(cr_counts-cr_old_counts)
                cr_old_counts=cr_counts
              ENDIF
              DEC(cr_i)
            ENDIF
          ENDIF
        ENDIF
    ENDSELECT
    inc(cr_timer)
  ENDIF
  
ENDFUNCTION
  
SUB finish_CR()
  DATA_26[1] = repumps
  DATA_26[2] = total_repump_counts
  DATA_26[3] = CR_failed
ENDSUB

