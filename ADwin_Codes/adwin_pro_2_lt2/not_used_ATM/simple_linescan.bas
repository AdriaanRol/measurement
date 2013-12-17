'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
' Initial_Processdelay           = 10
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' This program is adapted from simple_linescan for the ADwinGold, to perform a linescan.
' 
' 5-12-2011:  It is unclear to me 
'                     1) why we use 4 counters
'                     2) what CNT_SE_DIFF(0000b) should do  
'                     3) what we do with PAR_22 and 23 
'
'
'
'
'
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

DIM v_start AS FLOAT
DIM v_stop AS FLOAT
DIM steptime AS LONG
DIM V AS FLOAT
DIM steps AS LONG
DIM counter AS LONG
DIM axis AS LONG
DIM DATA_1[1000] AS LONG
DIM DATA_2[1000] AS LONG
DIM DATA_3[1000] AS LONG
DIM DATA_4[1000] AS LONG


INIT:
  v_start = FPAR_20
  v_stop = FPAR_21
  steptime = PAR_24
  steps = PAR_20
  axis = PAR_25
  counter = 0
  
  
  PROCESSDELAY = 300000*steptime

  'CONF_DIO(13)                    'configure DIO 08:15 as input, all other ports as output
      
  V=V_start
  IF (axis = 1) THEN
    P2_DAC(DAC_Module,1, V*3277+32768)
    FPAR_27 = V
  ELSE 
    IF (axis = 2) THEN
      P2_DAC(DAC_Module,2, V*3277+32768)
      FPAR_28 = V
    ELSE 
      IF (axis = 3) THEN
        P2_DAC(DAC_Module,8, V*3277+32768)
        FPAR_26 = V
      ENDIF
    ENDIF
  ENDIF
  
  P2_CNT_ENABLE(CTR_Module,0000b)
  P2_CNT_MODE(CTR_Module,1,00001000b)
  P2_CNT_MODE(CTR_Module,2,00001000b)
  P2_CNT_MODE(CTR_Module,3,00001000b)
  P2_CNT_MODE(CTR_Module,4,00001000b)
  'CNT_SE_DIFF(0000b)
  P2_CNT_CLEAR(CTR_Module,1111b)
  P2_CNT_ENABLE(CTR_Module,1111b)
  
  
EVENT:
  INC(counter)

  IF (counter = steps)THEN

    P2_CNT_LATCH(CTR_Module,1111b)
    DATA_1[counter]=P2_CNT_READ_LATCH(CTR_Module,1)*1000/steptime
    DATA_2[counter]=P2_CNT_READ_LATCH(CTR_Module,2)*1000/steptime
    DATA_3[counter]=P2_CNT_READ_LATCH(CTR_Module,3)*1000/steptime
    DATA_4[counter]=P2_CNT_READ_LATCH(CTR_Module,4)*1000/steptime
    P2_CNT_ENABLE(CTR_Module,0000b)
    P2_CNT_CLEAR(CTR_Module,1111b)
    P2_CNT_ENABLE(CTR_Module,1111b)
    PAR_23 = 0
    END
  ENDIF
        
  V = V_start + (V_stop - V_start)/(steps-1) * counter
  IF (axis = 1) THEN
    P2_DAC(DAC_Module,1, V*3277+32768)
    FPAR_27 = V
  ELSE 
    IF (axis = 2) THEN
      P2_DAC(DAC_Module,2, V*3277+32768)
      FPAR_28 = V
    ELSE 
      IF (axis = 3) THEN
        P2_DAC(DAC_Module,8, V*3277+32768)
        FPAR_26 = V
      ENDIF
    ENDIF
  ENDIF

  P2_CNT_LATCH(CTR_Module,1111b)
  DATA_1[counter]=P2_CNT_READ_LATCH(CTR_Module,1)*1000/steptime
  DATA_2[counter]=P2_CNT_READ_LATCH(CTR_Module,2)*1000/steptime
  DATA_3[counter]=P2_CNT_READ_LATCH(CTR_Module,3)*1000/steptime
  DATA_4[counter]=P2_CNT_READ_LATCH(CTR_Module,4)*1000/steptime
  PAR_22 = PAR_22 + DATA_1[counter] + DATA_2[counter]
  P2_CNT_ENABLE(CTR_Module,0000b)
  P2_CNT_CLEAR(CTR_Module,1111b)
  P2_CNT_ENABLE(CTR_Module,1111b)

  
FINISH:

