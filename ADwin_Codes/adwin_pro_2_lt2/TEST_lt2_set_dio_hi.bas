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
#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

init:
  P2_Digprog(DIO_MODULE,13)
  P2_DIGOUT(DIO_MODULE,16,1)

event:
  par_2 = ( P2_DIGIN_LONG(DIO_MODULE) and (2^8) ) 
  par_3 = par_3 + 1
  P2_DIGOUT(DIO_MODULE,16,1)
  
