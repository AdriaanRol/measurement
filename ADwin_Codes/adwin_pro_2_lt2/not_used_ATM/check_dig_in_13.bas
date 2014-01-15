'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
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

#DEFINE trigger_dio_in_bit 8192     '2^13
#DEFINE trigger_dio_out 16          '

DIM AWG_start_DO_channel AS LONG
DIM trigger_received AS LONG



INIT:
  P2_Digprog(DIO_MODULE, 13)      'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  AWG_start_DO_channel = 1
  PAR_65 = 0
  
EVENT:
  trigger_received = ((P2_DIGIN_EDGE(DIO_MODULE,1)) AND (trigger_dio_in_bit))
  
  IF (trigger_received > 0) THEN ' check whether a high signal arrived at dio 13.
    'P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
    'CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
    'P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
    INC(PAR_65)
  ENDIF
    
  
