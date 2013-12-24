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
' this program simply does CR checking and repumping, based on SSRO
'
' protocol:
' mode  0:  green pulse, 
'           photon counting just for statistics
' mode  1:  Ex/A pulse, photon counting  ->  CR check
'           fail: -> mode 0
'

#INCLUDE ADwinGoldII.inc
#Include Math.inc

DIM DATA_20[25] AS LONG               ' integer parameters
DIM DATA_21[20] AS FLOAT              ' float parameters

DIM counter_channel AS LONG
DIM repump_laser_DAC_channel AS LONG
DIM Ex_laser_DAC_channel AS LONG
DIM A_laser_DAC_channel AS LONG
DIM repump_duration AS LONG
DIM CR_duration AS LONG
DIM cycle_duration AS LONG
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
DIM aux_timer AS LONG
DIM repumps AS LONG
DIM CR_failed AS LONG
DIM total_repump_counts AS LONG
DIM counter_pattern AS LONG
DIM counts, old_counts, cr_counts AS LONG
DIM first AS LONG

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
  cycle_duration               = DATA_20[8]
  CR_probe                     = DATA_20[9]
  repump_after_repetitions     = DATA_20[10]
  CR_repump                    = DATA_20[11]
  
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
  
  counter_pattern     = 2 ^ (counter_channel-1)
  total_repump_counts = 0
  CR_failed           = 0
  repumps             = 0
  first               = 0
    
  DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  DAC(Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
  DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter
  CONF_DIO(13)      'configure DIO 08:15 as input, all other ports as output

  mode = 0
  timer = 0
  processdelay = cycle_duration  

  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' below CR threshold events
  PAR_72 = 0                      ' number of CR checks performed (lt1)
  Par_75 = CR_preselect
  Par_68 = CR_probe
  par_69 = CR_repump
  par_76 = 0                      ' cumulative counts during repumping
  Par_80 = 0                      ' cumulative counts in PSB when not CR chekging or repummping 
 
  current_cr_threshold = CR_preselect
EVENT:
  CR_preselect                 = PAR_75
  CR_probe                     = PAR_68
  CR_repump                    = PAR_69

  SELECTCASE mode
    CASE 0    ' green repump
      IF (timer = 0) THEN
        IF (cr_counts < CR_repump)  THEN  'only repump after x SSRO repetitions
          CNT_CLEAR( counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          DAC(repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on green
          repumps = repumps + 1
        ELSE
          mode = 1
          timer = -1
          current_CR_threshold = CR_preselect
        ENDIF
      ELSE 
        IF (timer = repump_duration) THEN
          DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
          counts = CNT_READ(counter_channel)
          CNT_ENABLE(0)
          total_repump_counts = total_repump_counts + counts
          PAR_76 = total_repump_counts
          mode = 1
          timer = -1
          current_cr_threshold = CR_preselect
        ENDIF
      ENDIF
      
    CASE 1    ' Ex/A laser CR check
      IF (timer = 0) THEN
        DAC(Ex_laser_DAC_channel, 3277*Ex_CR_voltage+32768) ' turn on Ex laser
        DAC(A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
        CNT_CLEAR( counter_pattern)    'clear counter
        CNT_ENABLE(counter_pattern)    'turn on counter
        INC(PAR_72)
        
      ELSE 
        IF (timer = CR_duration) THEN
          DAC(Ex_laser_DAC_channel, 3277*Ex_off_voltage+32768) ' turn off Ex laser
          DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
          cr_counts = CNT_READ(counter_channel)
          CNT_ENABLE(0)
          PAR_70 = PAR_70 + cr_counts
                       
          IF (cr_counts < current_cr_threshold) THEN
            mode = 0
            inc(PAR_71)
          ELSE
            mode = 1
            current_cr_threshold = CR_probe
          ENDIF
            
          timer = -1
        ENDIF
      ENDIF
      
  ENDSELECT    
  timer = timer + 1
  
