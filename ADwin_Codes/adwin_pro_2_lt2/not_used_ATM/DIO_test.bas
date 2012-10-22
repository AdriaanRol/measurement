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

INIT:
  P2_Digprog(1,0)                'Set DIO31:00 as inputs
EVENT:
  PAR_65 = P2_DIGIN_LONG(DIO_MODULE)
  'PAR_65 = readout
  'PAR_67 = 75
  'boolean = 0
  'if (readout AND 100000000b > 0) then
  '  boolean=1
  'endif
  'PAR_66 = boolean
  END
