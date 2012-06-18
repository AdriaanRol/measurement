'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 5
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
#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

DIM DATA_5[65536] AS LONG
DIM DATA_6[65536] AS FLOAT
DIM DATA_7[65536] AS LONG

DIM T_INT             AS LONG   ' integration time (unit?)
DIM U_Start           AS FLOAT  ' start voltage (V)
DIM Steps             AS LONG   ' no of steps
DIM U_Step            AS FLOAT  ' step voltage (V)
DIM Counter           AS LONG   ' counter channel
DIM Index             AS LONG   '  ???

INIT:
  T_INT   = PAR_5
  U_Start = FPAR_5
  Steps   = PAR_6
  U_step  = FPAR_6
  Counter = PAR_7

  ' no gate modulation here
  PROCESSDELAY = 300000 * T_INT
  
  P2_CNT_ENABLE(CTR_Module,0000b)               'turn off all counters
  P2_SE_DIFF(CTR_Module,0000b)              'configure counters as single ended
  IF (counter<5) THEN
    P2_CNT_MODE(CTR_Module,Counter,00001000b)
  ELSE
    P2_CNT_MODE(CTR_Module, 1, 00001000b)
    P2_CNT_MODE(CTR_Module, 2, 00001000b)
  ENDIF
  
  P2_CNT_CLEAR(CTR_Module, 1111b)                'clear counters
  P2_CNT_ENABLE(CTR_Module, 1111b)               'enable counters

  P2_DAC(DAC_Module, 5,3277*U_Start+32768) ' set start voltage
  P2_Digprog(DIO_MODULE, PAR_63)   'configure DIO-16 to DIO 31 as outputs, the rest are inputs
  
EVENT:
  ' WTF is that!?
  'DIGOUT(DIO_Module,4,1) 
  'CPU_SLEEP(50)
  'DIGOUT(DIO_Module,4,0)
   
  P2_CNT_LATCH(CTR_Module,1111b)
  IF (PAR_9 = 1) THEN
    IF (counter < 5) THEN
      DATA_5[Index+1]=DATA_5[Index+1] + P2_CNT_READ_LATCH(CTR_Module,Counter)
    ELSE
      DATA_5[Index+1]=DATA_5[Index+1] + P2_CNT_READ_LATCH(CTR_Module,1) + P2_CNT_READ_LATCH(CTR_Module,2)
    ENDIF
    DATA_6[Index+1]= FPAR_7
  ENDIF
  
  P2_CNT_ENABLE(CTR_Module,0000b)               'disable all counters
  P2_CNT_CLEAR(CTR_Module, 1111b)                'clear counters
  P2_CNT_ENABLE(CTR_Module, 1111b)               'enable counters

  IF (ModulationCounter = ModulationPeriod) THEN
    IF (PAR_4 = 0) THEN
      Index = Index + 1
    ENDIF
  
    PAR_8 = Index
    IF (Index = Steps) THEN
      END
    ENDIF	

    IF (Gate_sweep = 1) THEN              ' gatesweep
      IF (PAR_2 = 1) THEN            ' gate number
        IF (Gate_modulation = 1) THEN          ' gate modulation
          P2_DAC(DAC_Module,3,3277*(U_Start+(Index*((-1)^Index))*U_Step)+32768)
        ELSE
          P2_DAC(DAC_Module,3,3277*(U_Start+Index*U_Step)+32768)
        ENDIF
      ELSE
        IF (Gate_modulation = 1) THEN          ' gate modulation
          P2_DAC(DAC_Module,6,3277*(U_Start+(Index*((-1)^Index))*U_Step)+32768)
        ELSE
          P2_DAC(DAC_Module,6,3277*(U_Start+Index*U_Step)+32768)
        ENDIF
      ENDIF
    ELSE                             ' laser scan
      P2_DAC(DAC_Module,5,3277*(U_Start+Index*U_Step)+32768)
    ENDIF
    ModulationCounter = 0
  ENDIF
  
FINISH:
  
  
