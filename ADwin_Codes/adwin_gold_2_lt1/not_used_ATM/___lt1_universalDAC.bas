'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 6
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
#INCLUDE ADwinGoldII.inc

EVENT:
  IF (PAR_64 = 1) THEN
    PAR_64 = 0
    DAC(PAR_63,FPAR_64*3277+32768)
    CPU_SLEEP PAR_65*100
  ENDIF
  
  DAC(PAR_63,FPAR_63*3277+32768)
  END
