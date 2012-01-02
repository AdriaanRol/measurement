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
#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

EVENT:
  IF (PAR_64 = 1) THEN
    PAR_64 = 0
    CPU_DIGOUT(PAR_63,1)
    CPU_SLEEP PAR_65
    CPU_DIGOUT(PAR_63,0)
  ELSE
    CPU_DIGOUT(PAR_63,PAR_65)
  ENDIF
  
  END
