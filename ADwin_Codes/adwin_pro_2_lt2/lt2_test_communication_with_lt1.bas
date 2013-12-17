'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' a simple program to test the communication between the LT1 and LT2 adwins.
' this is the LT2 side.

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#Include Math.inc

DIM ADwin_switched_to_high AS LONG
DIM ADwin_in_is_high AS LONG
DIM ADwin_in_was_high AS LONG

DIM ADwin_lt1_di_channel AS LONG       'this is in channel of ADwin Pro, from Adwin lt1
DIM ADwin_lt1_di_channel_in_bit as LONG
DIM ADwin_lt1_do_channel AS LONG       'this is out channel of ADwin Pro, to Adwin lt1

INIT:
  ADwin_lt1_di_channel = 17
  ADwin_lt1_di_channel_in_bit = 2^ADwin_lt1_di_channel
  ADwin_lt1_do_channel = 2
  
  ADwin_in_is_high              = 0
  ADwin_in_was_high             = 0
  ADwin_switched_to_high        = 0
  
  P2_Digprog(DIO_MODULE, 11)      'configure DIO 16:23 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 0)

EVENT:
  ADwin_in_was_high = ADwin_in_is_high    'copies information from last round
  
  IF (((P2_DIGIN_LONG(DIO_MODULE)) AND (ADwin_lt1_di_channel_in_bit)) > 0) THEN
    ADwin_in_is_high = 1
  ELSE
    ADwin_in_is_high = 0
  ENDIF
  
  IF ((ADwin_in_was_high = 0) AND (ADwin_in_is_high > 0)) THEN  'adwin switched to high during last round.
    ADwin_switched_to_high = 1
    inc(par_1)
  ELSE
    ADwin_switched_to_high = 0
  ENDIF
  
  if (par_2 > 0) then
    par_3 = 1
    P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 1)
  else
    par_3 = 0
    P2_DIGOUT(DIO_MODULE, ADwin_lt1_do_channel, 0)
  endif
  

