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
'test to see how params are passed using functions (inc files) -machiel 30-12-'13

#INCLUDE ADwinPro_All.inc
#INCLUDE .\test_func1.inc
#INCLUDE .\test_func2.inc


dim global_par as long

INIT:
  PAR_70=0
  PAR_71=0
  PAR_72=1
  PAR_73=0
  PAR_74=0
  global_par=42
  init_tf1()
  init_tf2()
  
  
EVENT:
  PAR_70=5
  IF (tfone() > 0) THEN
    PAR_70=global_par+number

  ENDIF
  if (tftwo(75) >175) THEN  
    PAR_74=global_par
    END
  ENDIF
  
  
  
FINISH:
  
