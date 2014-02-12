'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  TUD277299\localadmin
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\..\configuration.inc
DIM channel, set, i AS LONG
DIM DATA_10[8] AS LONG

INIT:
  P2_Digprog(DIO_MODULE,11) 'configure DIO 16:23 as input, all other ports as output
  FOR i = 1 TO 8
    DATA_10[i]=0
  NEXT i
EVENT:
  set=0
  FOR i = 0 TO 15
    P2_DIGOUT(DIO_MODULE,i, set)   'This sets the digital output with channelnr to the value given by set
  NEXT i

  Par_60=P2_DIGIN_LONG(DIO_MODULE)
  
  END   
