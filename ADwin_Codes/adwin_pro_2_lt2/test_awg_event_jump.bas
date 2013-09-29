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
' Info_Last_Save                 = TUD276198  TUD276198\localadmin
'<Header End>
' Sets the output status for DIO given by <channel> to <set>
' channel is the pin no (16 to 31 are configured to be DO's
' set is either 0 or 1

#INCLUDE ADwinGoldII.inc
'#INCLUDE configuration.inc
DIM strobe as Long
DIM some_float as Float
DIM ev0 as Long
DIM ev1 as Long
DIM ev2 as Long
DIM ev3 as Long
DIM b as Long
DIM c as Long
DIM d as Long

INIT:
  CONF_DIO(1111b)   
  'dio 6 = strobe
  'dio 1 = event 1
  'dio 2 = event 2
  'dio 4 = event 3
  'dio 5= event 0
  strobe = 0
  ev0 = 0
  ev1 = 0
  ev2 = 0
  ev3 = 0
  b = 6
  c = 6
  d = 6
  some_float = 0.0

EVENT:
  digout(1, ev1)
  digout(2, ev2)
  digout(4, ev3)
  digout(5, ev0)
  digout(6, strobe)
  'ev1 is the trigger!
  if (d = 5) then 
    ev1 = 1 - ev1
  endif
  if (d = 4) then
    ev1 = 1 - ev1
  endif
  if (d = 0) then
    d = 6
  endif
  d = d - 1
  'has to be the same as ev1 just goes to the start of the card
  if (c = 5) then
    ev2 = 1 - ev2
  endif
  if (c = 4) then
    ev2 = 1 - ev2
  endif
  if (c = 0) then
    c = 6
  endif
  c = c - 1
    
  if (b = 4) then
    strobe = 1 - strobe
  endif
  if (b = 3) then
    strobe = 1 - strobe
  endif
  if (b = 0) then
    b = 6
  endif
  b = b - 1
  
  

