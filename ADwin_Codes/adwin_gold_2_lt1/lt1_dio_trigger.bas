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
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#INCLUDE ADwinGoldII.inc
' #INCLUDE configuration.inc
DIM channel AS LONG    ' dio number
DIM startval AS LONG   ' where to set the pulse value at the beginning
DIM waittime AS LONG   ' how long the trigger pulse is
dim pulseval as long

INIT:
  CONF_DIO(13)   
  channel = PAR_61
  startval = par_62
  waittime = par_63
  ' par_61 = 3
  
  if (startval = 0) then
    pulseval = 1
  else
    pulseval = 0
  endif
    
  digout(channel,startval)
  
EVENT:
  digout(channel, pulseval)
  CPU_SLEEP(waittime)
  digout(channel, startval)
  END
