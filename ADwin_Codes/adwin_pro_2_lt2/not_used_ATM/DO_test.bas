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
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
DIM i AS INTEGER

EVENT:
  P2_Digprog(DIO_MODULE, 13)
  '13: configure DIO 08:15 as input, all other ports as output
  
  'FOR i = 0 to 31
  'P2_DIGOUT(DIO_MODULE,24,1)
  'NEXT i
  
  END
