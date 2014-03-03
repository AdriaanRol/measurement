'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 3000000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
DIM channel, set, wait_steps, shutter_open_time, timer, mode AS LONG

INIT:
  P2_Digprog(DIO_MODULE,13)  'configure DIO 08:15 as input, all other ports as output
  channel =7        'Number of DIO to set 
  set     =1        'can be 1 or 0
  
  wait_steps        = 10      'number of iterations to wait between pulses, 1 iteration corresponds to 10 ms 
  shutter_open_time = 50 00000  'time that the shutter is open in 10 ns (first number is ms)
  
  timer = 0 
  mode  = 0
EVENT:
  SELECTCASE mode
      
    CASE 0
      P2_DIGOUT(DIO_Module,channel, 0)   'This sets the digital output with channelnr to the value given by set
      CPU_SLEEP(10000)
      P2_DIGOUT(DIO_Module,channel, 1)   'This sets the digital output with channelnr to the value given by set
      CPU_SLEEP(shutter_open_time)
      P2_DIGOUT(DIO_Module,channel, 0)   'This sets the digital output with channelnr to the value given by set
      mode = 1
      timer = -1
      
    CASE 1
      IF (timer < wait_steps) THEN 
      
      ELSE
        mode = 0
        timer = -1
      ENDIF
      
  ENDSELECT
  Inc(timer)  
