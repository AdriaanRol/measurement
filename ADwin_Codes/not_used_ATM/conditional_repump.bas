'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.5
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10238  TUD10238\localadmin
'<Header End>
' this program repumps the NV center with a green pulse, 
' then counts photons for during 'probe duration'
' conditional on the count rate, either the AWG sequence is started or the repump pulse is repeated



#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

DIM AOM_channel AS LONG           ' DAC channel for green laser AOM
DIM AOM_voltage AS LONG           ' voltage of repump pulse
DIM AOM_duration AS LONG          ' duration of AOM pulse in units of 10µs
DIM probe_duration AS LONG        ' duration of probe pulse in units of 10µs
DIM threshold AS LONG             ' only start AWG sequence if more than 'threshold' counts are detected during probe pulse
DIM do_repump AS LONG
DIM do_probe AS LONG
DIM do_probe_while_measuring AS LONG
DIM counts_during_probe AS LONG

DIM counter_number AS LONG
DIM DIO_Trigger AS LONG
DIM timer1 AS LONG
DIM timer2 AS LONG
DIM i AS LONG



INIT:
  AOM_channel = PAR_23     '4
  AOM_voltage = FPAR_30    '7.0
  AOM_duration = PAR_24    '1
  probe_duration = PAR_25  '10
  threshold = PAR_75       '-1
  DIO_Trigger = 9           ' Number of trigger input (standard # 9 for now)
  counter_number = 1        ' counter number (for now it is standard counter 1)
  
  P2_DAC(DAC_Module, AOM_channel, 32768)
  
  do_repump = 0
  do_repump = 0
  do_probe = 0
  do_probe_while_measuring = 0
  counts_during_probe=0
  
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_MODE(CTR_MODULE, 1,00001000b)
  P2_CNT_MODE(CTR_MODULE, 2,00001000b)
  P2_CNT_MODE(CTR_MODULE, 3,00001000b)
  P2_CNT_MODE(CTR_MODULE, 4,00001000b)
  
  timer1 = 0
  timer2 = 1
  P2_Digprog(DIO_MODULE, 0001b)         'DIO # 0-8 are outputs, 9-32 are inputs
  P2_Digin_FIFO_Enable(DIO_Module,0)    ' input FIFO with edge detection
  P2_Digin_FIFO_Clear(DIO_Module)       ' Clear FIFO
  P2_Digin_FIFO_Enable(DIO_Module,DIO_Trigger) ' edge detection on DIO Trigger input

EVENT:
  if (P2_Digin_FIFO_FULL(DIO_Module) > 0) then
    do_probe=probe_duration
    P2_Digin_FIFO_Clear(DIO_Module)
  endif
  
  P2_CNT_ENABLE(0000b)              
  P2_CNT_CLEAR(1111b)                'clear counter
  P2_CNT_ENABLE(1111b)               'enable counter  
  
  if (do_probe > 0) then
    timer1 = timer1 + 1
    do_probe = do_probe - 1
   
    if (do_probe = 0) then
      P2_CNT_LATCH(CTR_MODULE, 1111b)
      counts_during_probe = P2_CNT_READ_LATCH(CTR_Module,counter_number)
      if (counts_during_probe < threshold) then
        do_repump = AOM_duration
        P2_DAC(DAC_Module, AOM_channel, 3277*AOM_voltage+32768)
      else  
        P2_DIGOUT(DIO_Module,0,1)     ' trigger AWG start
        CPU_SLEEP(50)
        P2_DIGOUT(DIO_Module,0,0)

      endif
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
 
