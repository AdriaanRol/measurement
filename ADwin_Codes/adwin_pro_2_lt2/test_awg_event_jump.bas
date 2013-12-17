'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' Sets the output status for DIO given by <channel> to <set>
' channel is the pin no (16 to 31 are configured to be DO's
' set is either 0 or 1

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#Include Math.inc

DIM strobe as Long
DIM ev0 as Long
DIM ev1 as Long
DIM trigger as Long
DIM timer, seq_length as Long

INIT:
  P2_Digprog(DIO_MODULE, 11) 'configure DIO 16:23 as input, all other ports as output
  'dio 8 = strobe
  'dio 9 = event 0
  'dio 10 = event 1
  'dio 11 = trigger
  strobe = 0
  ev0 = 0
  ev1 = 0
  trigger = 0
  timer = 0
  seq_length = 25 'sequence length
  
  par_50 = 0
  par_51 = 0 'first bit of address
  par_52 = 0 'second bit of address

EVENT: 
  
  P2_DIGOUT(DIO_MODULE,8, strobe)
  P2_DIGOUT(DIO_MODULE,9, ev0)
  P2_DIGOUT(DIO_MODULE,10, ev1)
  P2_DIGOUT(DIO_MODULE,11, trigger)
  
  par_50 = timer
  
  if (timer = 1) then
    trigger = 1
  else
    trigger = 0
  endif
  
  if (timer = 6) then
    ev0 = par_51
    ev1 = par_52
  endif
  
  if (timer = 9) then
    ev0 = 0
    ev1 = 0
  endif
  
  if (timer = 7) then
    strobe = 1
  else
    strobe = 0
  endif
  
  if (timer = seq_length) then
    timer = 0
  endif

  inc(timer)

