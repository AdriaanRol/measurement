'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.5
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10238  TUD10238\localadmin
'<Header End>
' Sets the output status for DIO given by <channel> to <set>
' channel is the pin no (16 to 31 are configured to be DO's
' set is either 0 or 1

#INCLUDE ADwinGoldII.inc
DIM channel, set AS LONG
DIM mod AS LONG

INIT:
  Conf_DIO(0011b)
  channel=8    'OutputNR can only have values 1,2,3,4 corresponding to DIO28,29,30,31
  set=1
  mod=1
 

  'EVENT:
  ' mod=1-mod
  'digout(channel, set*mod)
EVENT:
  Par_59=DIGIN(16)
  END
