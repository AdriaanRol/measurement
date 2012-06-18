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
DIM DATA_5[65536] AS LONG
DIM DATA_6[65536] AS FLOAT
DIM DATA_7[65536] AS LONG

DIM T_INT             AS LONG
DIM U_Start           AS FLOAT
DIM Steps             AS LONG
DIM U_Step            AS FLOAT
DIM Counter           AS LONG
DIM Index             AS LONG
DIM ModulationPeriod  AS LONG
DIM ModulationCounter AS LONG
DIM Polarity          AS LONG

INIT:
  T_INT   = PAR_5
  U_Start = FPAR_5
  Steps   = PAR_6
  U_step  = FPAR_6
  Counter = PAR_7
  
  Index   = 0
  
  IF (PAR_3 = 0) THEN               'no gate modulation
    PROCESSDELAY = 300000 * T_INT
    ModulationPeriod = 1
  ELSE
    IF (PAR_1 = 1) THEN             'gate sweep
      PROCESSDELAY = 300000 * T_INT
      ModulationPeriod = 1
    ELSE                          'laser sweep
      PROCESSDELAY = 300 * PAR_80
      ModulationPeriod = T_INT * 2000 / PAR_80
    ENDIF
  ENDIF
  
  P2_CNT_ENABLE(CTR_Module,0000b)               'turn off all counters
  P2_SE_DIFF(CTR_Module,0000b)              'configure counters as single ended
  IF (counter<5) THEN
    P2_CNT_MODE(CTR_Module,Counter,00001000b)
  ELSE
    P2_CNT_MODE(CTR_Module, 1, 00001000b)
    P2_CNT_MODE(CTR_Module, 2, 00001000b)
  ENDIF
  
  CNT_CLEAR(1111b)                'clear counters
  CNT_ENABLE(1111b)               'enable counters

  IF (PAR_1 = 0) THEN
    IF (PAR_3 = 0) THEN
      DAC(5,3277*U_Start+32768)
    ELSE
      DAC(5,3277*U_Start+32768)
      DAC(3,32768+Polarity*3277*FPAR_79)
      DAC(6,32768+Polarity*3277*FPAR_80)
    ENDIF
  ELSE
    IF (PAR_2 = 1) THEN            ' gate number
      DAC(3,3277*U_Start+32768)
    ELSE
      DAC(6,3277*U_Start+32768)
    ENDIF
  ENDIF

  CONF_DIO(13)                    'configure DIO 08:15 as input, all other ports as output
  
  Polarity = 1
  ModulationCounter = 0

EVENT:
  DIGOUT(4,1)
  CPU_SLEEP(50)
  DIGOUT(4,0)
  
  IF ((PAR_1 = 0) AND (PAR_3 = 1)) THEN
    Polarity = -Polarity
    DAC(3,32768+Polarity*3277*FPAR_79)
    DAC(6,32768+Polarity*3277*FPAR_80)
  ENDIF
  
  ModulationCounter = ModulationCounter + 1
  IF (ModulationCounter = 1) THEN
    DATA_5[Index+1] = 0
  ENDIF
 
  CNT_LATCH(1111b)

  IF ((PAR_9 = 1) AND (Polarity = 1)) THEN
    IF (counter < 5) THEN
      DATA_5[Index+1]=DATA_5[Index+1] + CNT_READ_LATCH(Counter)
    ELSE
      DATA_5[Index+1]=DATA_5[Index+1] + CNT_READ_LATCH(1) + CNT_READ_LATCH(2)
    ENDIF
    DATA_6[Index+1]= FPAR_7
  ENDIF
  
  CNT_ENABLE(0000b)               'disable all counters
  CNT_CLEAR(1111b)                'clear counters
  CNT_ENABLE(1111b)               'enable counters

  IF (ModulationCounter = ModulationPeriod) THEN
    IF (PAR_4 = 0) THEN
      Index = Index + 1
    ENDIF
  
    PAR_8 = Index
    IF (Index = Steps) THEN
      END
    ENDIF	

    IF (PAR_1 = 1) THEN              ' gatesweep
      IF (PAR_2 = 1) THEN            ' gate number
        IF (PAR_3 = 1) THEN          ' gate modulation
          DAC(3,3277*(U_Start+(Index*((-1)^Index))*U_Step)+32768)
        ELSE
          DAC(3,3277*(U_Start+Index*U_Step)+32768)
        ENDIF
      ELSE
        IF (PAR_3 = 1) THEN          ' gate modulation
          DAC(6,3277*(U_Start+(Index*((-1)^Index))*U_Step)+32768)
        ELSE
          DAC(6,3277*(U_Start+Index*U_Step)+32768)
        ENDIF
      ENDIF
    ELSE                             ' laser scan
      DAC(5,3277*(U_Start+Index*U_Step)+32768)
    ENDIF
    ModulationCounter = 0
  ENDIF
  
FINISH:
  IF ((PAR_1 = 0) AND (PAR_3 = 1)) THEN
    DAC(3,32768)
    DAC(6,32768)
  ENDIF
  
