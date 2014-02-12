'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  TUD277299\localadmin
'<Header End>
#INCLUDE ADwinGoldII.inc
' #INCLUDE configuration.inc
DIM channel, set AS LONG

INIT:
  CONF_DIO(11)        'configure DIO 16:23 as input, all other ports as output
  channel=PAR_61
  set=PAR_62
 

EVENT:
  digout(channel, set)
  END
