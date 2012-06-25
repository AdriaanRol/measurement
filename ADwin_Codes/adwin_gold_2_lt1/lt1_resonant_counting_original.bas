'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' this program repumps the NV center with a green pulse, 
' then counts photons for during 'probe duration'
' PAR_41 - PAR_44 contains a floating average of the count rate at counter 1 - 4 over the last 100ms

#INCLUDE ADwinGoldII.inc

DIM AOM_channel AS LONG           ' DAC channel for green laser AOM
DIM AOM_voltage AS LONG           ' voltage of repump pulse
DIM AOM_duration AS LONG          ' duration of AOM pulse in units of 10µs
DIM probe_duration AS LONG        ' duration of probe pulse in units of 10µs

DIM do_repump AS LONG
DIM do_probe AS LONG

DIM timer1 AS LONG
DIM timer2 AS LONG
DIM i AS LONG

DIM DATA_41[100] AS FLOAT
DIM DATA_42[100] AS FLOAT
DIM DATA_43[100] AS FLOAT
DIM DATA_44[100] AS FLOAT


INIT:
  Par_64=1
  AOM_channel = PAR_63     '4
  AOM_voltage = FPAR_64    '7.0
  AOM_duration = PAR_73    '1
  probe_duration = PAR_74  '10
  DAC(AOM_channel,32768)
  Par_64=Par_64+1
  do_repump = 0
  do_probe = probe_duration
  Par_64=Par_64+1
  CNT_ENABLE(0000b)               'turn off all counters
  CNT_SE_DIFF(0000b)              'configure counters as single ended
  CNT_MODE(1,00001000b)           'configure counter one: 
  CNT_MODE(2,00001000b)           'configure counter one: 
  CNT_MODE(3,00001000b)           'configure counter one: 
  CNT_MODE(4,00001000b)           'configure counter one: 
  Par_64=Par_64+1
  CONF_DIO(13)                    'configure DIO 08:15 as input, all other ports as output
  Par_64=Par_64+1
  for i = 1 to 100
    DATA_41[i] = 0
    DATA_42[i] = 0
    DATA_43[i] = 0
    DATA_44[i] = 0
  next i
  Par_64=Par_64+1
  timer1 = 0
  timer2 = 1
  Par_64=Par_64+1

EVENT:
  Par_64=Par_64+1
  if (do_probe > 0) then
    timer1 = timer1 + 1
    do_probe = do_probe - 1
    
    CNT_LATCH(1111b)
    DATA_41[timer2] = DATA_41[timer2] + CNT_READ_LATCH(1)
    DATA_42[timer2] = DATA_42[timer2] + CNT_READ_LATCH(2)
    DATA_43[timer2] = DATA_43[timer2] + CNT_READ_LATCH(3)
    DATA_44[timer2] = DATA_44[timer2] + CNT_READ_LATCH(4)
    CNT_ENABLE(0000b)              
    CNT_CLEAR(1111b)                'clear counter 1
    if (do_probe = 0) then
      do_repump = AOM_duration
      DAC(AOM_channel,3277*AOM_voltage+32768)
    else
      CNT_ENABLE(1111b)              
    endif
    
    if (timer1 = 100) then
      
      PAR_41 = 0
      PAR_42 = 0
      PAR_43 = 0
      PAR_44 = 0
  
      for i = 1 to 100
        PAR_41 = PAR_41 + DATA_41[i] * 10
        PAR_42 = PAR_42 + DATA_42[i] * 10
        PAR_43 = PAR_43 + DATA_43[i] * 10
        PAR_44 = PAR_44 + DATA_44[i] * 10
      next i
      
      timer2 = timer2 + 1
      
      if (timer2 = 101) then
        timer2 = 1
      endif
      
      DATA_41[timer2] = 0
      DATA_42[timer2] = 0
      DATA_43[timer2] = 0
      DATA_44[timer2] = 0
      timer1 = 0
      
    endif
  endif
  
  if (do_repump > 0) then
    do_repump = do_repump-1
    if (do_repump = 0) then
      DAC(AOM_channel,32768)
      do_probe = probe_duration
      CNT_ENABLE(1111b)               'enable counter 1
    endif
  endif
 
