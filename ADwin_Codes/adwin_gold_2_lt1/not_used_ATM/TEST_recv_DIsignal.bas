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
#INCLUDE ADwinGoldII.inc

init:
  par_2 = 0
  ' DIGOUT(1,1)
  CONF_DIO(13)
  DIGOUT(1,1)
  
event:
  par_2 = DIGIN(10)
  par_3 = par_3 + 1
  DIGOUT(1,0)
