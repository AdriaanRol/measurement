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
#INCLUDE .\configuration.inc

Init:
  REM Set channels 0.15 as outputs, 16.31 as inputs
  P2_Digprog(1,0011h)
  P2_Dig_Write_Latch(1,0)       'Set all output bits to 0

Event:
  P2_Dig_Latch(1)               'latch inputs, output content of
  'output latches
  Rem further program
  Par_1 = P2_Dig_Read_Latch(1)   'read input bits and .
  P2_Dig_Write_Latch(1,Par_1)   'output in next event cycle

