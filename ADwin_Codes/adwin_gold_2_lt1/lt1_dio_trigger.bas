'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' Sets the output status for DIO given by <channel> to <set>
' channel is the pin no (16 to 31 are configured to be DO's
' set is either 0 or 1

#INCLUDE ADwinGoldII.inc
#INCLUDE configuration.inc
DIM channel AS LONG

INIT:
  CONF_DIO(13)   'configure DIO-24 to DIO 31 as outputs, the rest are inputs
  channel=PAR_61    'OutputNR can only have values 1,2,3,4 corresponding to DIO28,29,30,31
  par_61 = 3
  digout(channel,0)
  

EVENT:
  digout(channel, 1)
  CPU_SLEEP(9)
  digout(channel, 0)
  END
