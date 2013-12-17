'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
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
' only DIO 1-24 are connected to breakout box (no 0, 25-31)

' this program repumps the NV center with a green pulse, 
' then counts photons for during 'probe duration'
' conditional on the count rate, either the AWG sequence is started or the repump pulse is repeated

' PAR_70: counter for repump pulses
' PAR_71: counter for CR2 failed
' PAR_72: sequence probe events

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

DIM counter AS LONG               ' select internal ADwin counter 1 - 4 for conditional readout
DIM AOM_channel AS LONG           ' DAC channel for green laser AOM
DIM AOM_voltage AS LONG           ' voltage of repump pulse
DIM AOM_duration AS LONG          ' duration of AOM pulse in units of 10µs
DIM probe_duration AS LONG        ' duration of probe pulse in units of 10µs
DIM threshold AS LONG             ' only start AWG sequence if more than 'threshold' counts are detected during probe pulse
DIM probe_threshold AS LONG

DIM do_repump AS LONG
DIM do_probe AS LONG
DIM do_probe_while_measuring AS LONG
DIM counts AS LONG
DIM AWG_wait AS LONG
DIM DATA_41[10000] AS FLOAT
DIM index AS INTEGER
DIM i AS INTEGER


INIT:
  counter = PAR_45         '1 'P?
  AOM_channel = PAR_63     '4 'P26
  AOM_voltage = FPAR_64    '7.0 'FP30
  AOM_duration = PAR_73    '5 'P27
  probe_duration = PAR_74  '10 'P28
  threshold = PAR_75       'sequence CR threshold
  probe_threshold = PAR_76
  P2_DAC(DAC_MODULE,AOM_channel,32768)
  PAR_77 = 0
  
  do_repump = 0
  do_probe = 0
  do_probe_while_measuring = 0
  index = 0
  
  PAR_70 = 0                      'counts probe intervals
  PAR_71 = 0                      'below CR threshold events
  PAR_72 = 0                      'counts total repetitions
  
  P2_CNT_ENABLE(CTR_MODULE, 0000b)'turn off all counters
  IF (counter = 5) THEN
    P2_CNT_MODE(CTR_MODULE, 1,00001000b)
    P2_CNT_MODE(CTR_MODULE, 2,00001000b)
  ELSE
    P2_CNT_MODE(CTR_MODULE, counter,00001000b) 'configure counter
  ENDIF
      
  
  P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  

EVENT:
  if ((P2_DIGIN_EDGE(DIO_MODULE, 1) AND 2^9) > 0) then
    P2_CNT_ENABLE(CTR_MODULE, 0000b)
    P2_CNT_CLEAR(CTR_MODULE,  1111b)'clear counter
    P2_CNT_ENABLE(CTR_MODULE, 1111b)'enable counter
    do_probe_while_measuring = 1
    PAR_72 = PAR_72 + 1
  endif
  
  if ((P2_DIGIN_EDGE(DIO_MODULE, 0) AND 2^9) > 0) then
    do_probe_while_measuring = 0
    P2_CNT_LATCH(CTR_MODULE, 1111b)
    if (counter = 5) then
      counts = P2_CNT_READ_LATCH(CTR_MODULE, 1) + P2_CNT_READ_LATCH(CTR_MODULE, 2)
    else
      counts = P2_CNT_READ_LATCH(CTR_MODULE, counter)
    endif
        
    P2_CNT_ENABLE(CTR_MODULE, 0000b)
    P2_CNT_CLEAR(CTR_MODULE,  1111b)'clear counter
      
    if (counts < PAR_75) then
      P2_DIGOUT(DIO_MODULE,6,1)  ' force AWG to wait for trigger
      CPU_SLEEP(50)
      P2_DIGOUT(DIO_MODULE,6,0)

      PAR_71 = PAR_71 + 1
      do_repump = PAR_73
      P2_DAC(DAC_MODULE,AOM_channel,3277*AOM_voltage+32768)
      P2_CNT_ENABLE(CTR_MODULE, 1111b)
    endif
    PAR_41 = counts ' P51
    index = index + 1
    DATA_41[index] = counts 'D51
    if (index = 1000) then index = 0
    PAR_42 = 0 'P52
    for i = 1 to 1000
      PAR_42 = PAR_42 + DATA_41[i] 'P52, D51
    next i
  endif
  
  if (do_probe > 0) then  'switch on of pulse
    do_probe = do_probe - 1
    if (do_probe = 0) then
      P2_CNT_LATCH(CTR_MODULE, 1111b)
      if (counter = 5) then
        counts = P2_CNT_READ_LATCH(CTR_MODULE, 1) + P2_CNT_READ_LATCH(CTR_MODULE, 2)
      else
        counts = P2_CNT_READ_LATCH(CTR_MODULE, counter)
      endif
        
      P2_CNT_ENABLE(CTR_MODULE, 0000b)
      P2_CNT_CLEAR(CTR_MODULE,  1111b)'clear counter
      if (counts > PAR_76) then
        P2_DIGOUT(DIO_MODULE,1,1)     ' trigger AWG start
        CPU_SLEEP(50)
        P2_DIGOUT(DIO_MODULE,1,0)
      else
        PAR_70 = PAR_70 + 1
        do_repump = PAR_73
        P2_DAC(DAC_MODULE,AOM_channel,3277*AOM_voltage+32768)
        P2_CNT_ENABLE(CTR_MODULE, 1111b)
      endif
    endif
  endif
  
  if (do_repump > 0) then
    do_repump = do_repump-1
    if (do_repump = 0) then  'switch off of pulse
      P2_DAC(DAC_MODULE,AOM_channel,32768)
      do_probe = PAR_74
      P2_CNT_LATCH(CTR_MODULE, 1111b)
      PAR_77 = PAR_77 + P2_CNT_READ_LATCH(CTR_MODULE, 1) + P2_CNT_READ_LATCH(CTR_MODULE, 2) + P2_CNT_READ_LATCH(CTR_MODULE, 3) + P2_CNT_READ_LATCH(CTR_MODULE, 4)
      P2_CNT_ENABLE(CTR_MODULE, 0000b)
      P2_CNT_CLEAR(CTR_MODULE,  1111b)'clear counter
      P2_CNT_ENABLE(CTR_MODULE, 1111b)
    endif
  endif
