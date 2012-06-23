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
DIM AOM_voltage AS FLOAT           ' voltage of repump pulse
DIM AOM_duration AS LONG          ' duration of AOM pulse in units of 10µs
DIM probe_duration AS LONG        ' duration of probe pulse in units of 10µs

DIM do_repump AS LONG
DIM do_probe AS LONG

DIM timer1 AS LONG
DIM timer2 AS LONG
DIM i AS LONG

DIM float_avg AS FLOAT            ' Floating average time in ms (10 sec max)

DIM DATA_41[100] AS FLOAT
DIM DATA_42[100] AS FLOAT
DIM DATA_43[100] AS FLOAT
DIM DATA_44[100] AS FLOAT


INIT:
  
  AOM_channel = PAR_63     '4
  AOM_voltage = FPAR_64    '7.0
  AOM_duration = PAR_73+1    '1
  probe_duration = PAR_74+1  '10
  
  float_avg=FPAR_11
  if (float_avg < 0) then
    float_avg = 100
  endif
  
  DAC(AOM_channel,32768)
  
  do_repump = 0
  do_probe = probe_duration
  
  for i = 1 to 100
    DATA_41[i] = 0
    DATA_42[i] = 0
    DATA_43[i] = 0
    DATA_44[i] = 0
  next i
  
  timer1 = 0
  timer2 = 1

  CNT_ENABLE(0000b)               'turn off all counters
  CNT_SE_DIFF(0000b)              'configure counters as single ended
  CNT_MODE(1,00001000b)           'configure counter one: 
  CNT_MODE(2,00001000b)           'configure counter one: 
  CNT_MODE(3,00001000b)           'configure counter one: 
  CNT_MODE(4,00001000b)           'configure counter one: 
  CNT_ENABLE(0000b)              
  CNT_CLEAR(1111b)  
  CNT_ENABLE(1111b)    
  'CONF_DIO(13)                    'configure DIO 08:15 as input, all other ports as output

EVENT:

  'no linescan mode availabla

  if (do_probe > 0) then
    if (do_probe=probe_duration) then
      CNT_ENABLE(1111b)               'enable counters
    else
      timer1 = timer1 + 1
    endif
    
    do_probe = do_probe - 1
    
    if (do_probe = 0) then
      CNT_LATCH(1111b)
      DATA_41[timer2] = DATA_41[timer2] + CNT_READ_LATCH(1)
      DATA_42[timer2] = DATA_42[timer2] + CNT_READ_LATCH(2)
      DATA_43[timer2] = DATA_43[timer2] + CNT_READ_LATCH(3)
      DATA_44[timer2] = DATA_44[timer2] + CNT_READ_LATCH(4)
      CNT_ENABLE(0000b)              
      CNT_CLEAR(1111b)                'clear counter 1
      
      do_repump = AOM_duration
      DAC(AOM_channel,3277*AOM_voltage+32768)
    endif
    
    if (timer1 >= 100) then
      
      PAR_41 = Par_41 * (1-1/float_avg) + (1000*DATA_41[timer2]) * 1/float_avg 
      PAR_42 = Par_42 * (1-1/float_avg) + (1000*DATA_42[timer2]) * 1/float_avg 
      PAR_43 = Par_43 * (1-1/float_avg) + (1000*DATA_43[timer2]) * 1/float_avg 
      PAR_44 = Par_44 * (1-1/float_avg) + (1000*DATA_44[timer2]) * 1/float_avg 
      timer2 = timer2 + 1
      if (timer2 = float_avg + 1) then
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
    endif
  endif
 
