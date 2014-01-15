'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' This program does a multidimensional line scan; it needs to be given the 
' involved DACs, their start voltage, their end voltage and the number of steps
' (including start and stop)
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' scan settings
DIM NoOfDACs, i, CurrentStep, NoOfSteps AS INTEGER
DIM PxTime, StepSize AS FLOAT

' what to do for each pixel; 1=counting, 0=nothing, 2=counting + record supplemental data per px from fpar2
DIM PxAction AS INTEGER

' The numbers of the involved DACs (adwin only has 8)
DIM DATA_200[8] AS INTEGER
' The start voltages
DIM DATA_199[8] AS FLOAT
' The end voltages
DIM DATA_198[8] AS FLOAT
' The stepsizes
DIM DATA_197[8] AS FLOAT
' The current position
DIM DATA_1[8] AS FLOAT

' keeping track of timing
DIM TimeCntROStart, TimeCntROStop AS INTEGER

' Setting voltages
DIM DACVoltage AS FLOAT
DIM DACBinaryVoltage AS INTEGER

'DIM DACVoltage,StartVoltage, EndVoltage, stepsize, now,idletime1,idletime2,frequency1,temp1,temp2,frequency2 AS FLOAT
'DIM DACno ,NOfVoltSteps, pixeltime,totaltime,i,n,m,DACBinaryVoltage,time_1,time_2,time_3,time_4,val,val1,retval1,retval2,Counts1,Counts2 AS INTEGER

DIM DATA_11[100000] AS LONG
DIM DATA_12[100000] AS LONG
DIM DATA_13[100000] AS LONG

' supplemental data; used when PxAction is set to 2
DIM DATA_15[100000] AS FLOAT

INIT:
  
  CurrentStep = 1
  
  ' set the pixel clock, but start from zero
  PAR_4 = CurrentStep - 1   
  
  ' get all involved DACs and set to start voltages
  NoOfDACs = PAR_1
  NoOfSteps = PAR_2
  PxTime = FPAR_1
  PxAction = PAR_3
   
  'Processtime is in units of clockcycles for pixeltime in ms
  PROCESSDELAY = PxTime * 300000    
  
  FOR i = 1 TO NoOfDACs
    DACVoltage = DATA_199[i]
    DACBinaryVoltage = DACVoltage * 3276.8 + 32768    
    
    P2_DAC(DAC_Module,DATA_200[i], DACBinaryVoltage)
    DATA_1[DATA_200[i]]   = DACVoltage 
    DATA_197[i] = (DATA_198[i] - DATA_199[i]) / (NoOfSteps - 1) 
  
    ' debug;
    PAR_5 = DATA_200[i]
    FPar_5 = DATA_199[i]

  NEXT i
  
  FOR i = 1 TO 100000
    DATA_11[i] = 0
    DATA_12[i] = 0
    DATA_13[i] = 0
    DATA_15[i] = 0
  NEXT i
  
  IF ((PxAction = 1) OR (PxAction = 2)) THEN
    P2_CNT_ENABLE(CTR_Module,000b)                                        'Stop counter 1, 2 and 3
    P2_CNT_MODE(CTR_Module,1, 00001000b)                                  '
    P2_CNT_MODE(CTR_Module,2, 00001000b)
    P2_CNT_MODE(CTR_Module,3, 00001000b)
    P2_SE_DIFF(CTR_Module,000b)                                           'All counterinputs single ended (not differential)
    P2_CNT_CLEAR(CTR_Module,111b)                                         'Set all counters to zero
    P2_CNT_ENABLE(CTR_Module,111b)                                        'Start counter 1 and 2
  ENDIF
    
 
EVENT:
  
  IF ((PxAction = 1) OR (PxAction = 2)) THEN
    ' DEBUG FPar_23 = 42.0
    ' Read out counters 1, 2 and 3 and reset them
    TimeCntROStart = READ_TIMER()
    P2_CNT_LATCH(CTR_Module,1111b)                                         'latch counters
    DATA_11[CurrentStep] = P2_CNT_READ_LATCH(CTR_Module,1)                 'read latch A of counter 1
    DATA_12[CurrentStep] = P2_CNT_READ_LATCH(CTR_Module,2)                 'read latch A of counter 2
    DATA_13[CurrentStep] = P2_CNT_READ_LATCH(CTR_Module,3)                 'read latch A of counter 3
    P2_CNT_ENABLE(CTR_Module,000b)                                        'Stop counters
    P2_CNT_CLEAR(CTR_Module,111b)                                         'Clear counters
    P2_CNT_ENABLE(CTR_Module,111b)                                        'Start counters again
    TimeCntROStop = READ_TIMER()
    FPar_21 = (TimeCntROStart - TimeCntROStop) / 300.0      ' Time the RO took in us
  ENDIF
  IF (PxAction = 2) THEN
    ' DEBUG FPar_24 = 42.0
    DATA_15[CurrentStep] = FPar_2
  ENDIF
  

  ' Set the voltage on all involved DACs
  FOR i = 1 TO NoOfDACs
    'Increase DAC voltage by one step (first value will be neglected)
    DACVoltage = DATA_199[i] + (CurrentStep - 1) * DATA_197[i]
    FPar_7 = DATA_199[i]
    FPar_8 = CurrentStep-1
    FPar_9 = DATA_197[i]   
    DACBinaryVoltage = DACVoltage * 3276.8 + 32768
    P2_DAC(DAC_Module,DATA_200[i], DACBinaryVoltage)
    DATA_1[DATA_200[i]]   = DACVoltage
    FPar_5 = DACVoltage

  NEXT i
  inc(CurrentStep)
    
  IF (CurrentStep > NoOfSteps + 1) THEN                     ' Stop when end of line is reached
    'FOR i = 1 TO NoOfDACs
    '  DACVoltage = (DATA_199[i])
    '  DACBinaryVoltage = DACVoltage * 3276.8 + 32768        ' Go back to start of the line
    '  P2_DAC(DAC_Module,DATA_200[i], DACBinaryVoltage)
    '  DATA_1[DATA_200[i]]   = DACVoltage
    '
    'NEXT i
    END                                                     'End program
  ENDIF
  
  ' update the pixel clock; put after the line end check so we have a maximum
  ' that corresponds to the number of steps
  Par_4 = CurrentStep - 1
  
FINISH:  
