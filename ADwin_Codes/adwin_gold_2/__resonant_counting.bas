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
' PAR_41 - PAR_44 contains a floating average of the count rate at counter 1 - 4 over the FPAR_1 ms

#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

DIM AOM_channel AS LONG           ' DAC channel for green laser AOM
DIM AOM_voltage AS LONG           ' voltage of repump pulse
DIM AOM_duration AS LONG          ' duration of AOM pulse in units of 10�s
DIM probe_duration AS LONG        ' duration of probe pulse in units of 10�s

DIM do_repump AS LONG
DIM do_probe AS LONG
DIM start, stop AS FLOAT
DIM timer1 AS LONG
DIM timer2 AS LONG
DIM i AS LONG

DIM float_avg AS FLOAT            ' Floating average time in ms (10 sec max)

DIM DATA_41[10000] AS FLOAT         ' Maximum floating average is 10 seconds
DIM DATA_42[10000] AS FLOAT
DIM DATA_43[10000] AS FLOAT
DIM DATA_44[10000] AS FLOAT

DIM cnt1,cnt2,cnt3,cnt4 AS INTEGER         ' intermediate variable to store countrates of counters




INIT:
  'if (PAR_25 < 1) then
  '  FPAR_25 = 1
  'endif
  
  'if (PAR_24 < 1) then
  '  FPAR_24 = 1
  'endif
  
  
  AOM_channel = PAR_23     '4
  AOM_voltage = FPAR_30    '7.0
  AOM_duration = PAR_24    '1 
  probe_duration = PAR_25  '10 
  
  if (FPAR_1 < 0) then
    FPAR_1 = 100
  endif
  
  P2_DAC(DAC_Module, AOM_channel, 32768)
  
  do_repump = 0
  do_probe = probe_duration
  
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_MODE(CTR_MODULE, 1,00001000b)
  P2_CNT_MODE(CTR_MODULE, 2,00001000b)
  P2_CNT_MODE(CTR_MODULE, 3,00001000b)
  P2_CNT_MODE(CTR_MODULE, 4,00001000b)
  
  for i = 1 to 10000
    DATA_41[i] = 0
    DATA_42[i] = 0
    DATA_43[i] = 0
    DATA_44[i] = 0
  next i

  timer1 = 0
  timer2 = 1

EVENT:
  'if (FPAR_1 > 0) then
  '  float_avg = FPAR_1 ' 100 ms
  'else
  'float_avg = 100
  'endif
  float_avg=100'FPAR_1

  if (do_probe > 0) then
    timer1 = timer1 + 1
    do_probe = do_probe - 1
    
    P2_CNT_LATCH(CTR_MODULE, 1111b)
    DATA_41[timer2] = DATA_41[timer2] + P2_CNT_READ_LATCH(CTR_MODULE,1)
    DATA_42[timer2] = DATA_42[timer2] + P2_CNT_READ_LATCH(CTR_MODULE,2)
    DATA_43[timer2] = DATA_43[timer2] + P2_CNT_READ_LATCH(CTR_MODULE,3)
    DATA_44[timer2] = DATA_44[timer2] + P2_CNT_READ_LATCH(CTR_MODULE,4)
    P2_CNT_CLEAR(CTR_MODULE, 1111b)
    P2_CNT_ENABLE(CTR_MODULE, 0000b)
    if (do_probe = 0) then
      do_repump = AOM_duration
      P2_DAC(DAC_Module, AOM_channel, 3277*AOM_voltage+32768)
    else
      P2_CNT_ENABLE(CTR_MODULE, 1111b)
    endif
    
    if (timer1 = 100) then
                
      cnt1 = 0
      cnt2 = 0
      cnt3 = 0
      cnt4 = 0
  
      for i = 1 to float_avg
        cnt1 = cnt1 + DATA_41[i]
        cnt2 = cnt2 + DATA_42[i]
        cnt3 = cnt3 + DATA_43[i]
        cnt4 = cnt4 + DATA_44[i]
        
      next i
      PAR_41 = cnt1 * 1000/float_avg
      PAR_42 = cnt2 * 1000/float_avg
      PAR_43 = cnt3 * 1000/float_avg
      PAR_44 = cnt4 * 1000/float_avg
      
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
      P2_DAC(DAC_Module, AOM_channel, 32768)
      do_probe = probe_duration
      P2_CNT_ENABLE(CTR_MODULE, 1111b)               'enable counter 1
    endif
  endif
 
