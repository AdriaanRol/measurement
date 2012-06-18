'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
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

Dim timervalue1 as Long
dim timervalue2 as long
dim timervalue3 as long
Dim counter as long
DIm DATA_2[10001] as LONG
DIm DATA_3[10001] as LONG
dim carr[4] as long
dim diod as long

INIT:
  timervalue1=0
  timervalue2=0
  timervalue3=0
  counter=0
  Par_2=0
  Par_3=0
  Par_4=0
  Par_5=0
  par_6=0
  par_7=0
  par_8=0
  
  diod=8
  
  FPar_2=0.0
  Fpar_3=0.0
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_CLEAR(CTR_MODULE,  1111b) ' clear counter
  P2_CNT_ENABLE(CTR_MODULE, 1111b) ' enable counter

EVENT:
  if (counter < 10000) then
    
    timervalue1=Read_timer()
    Par_2=Par_2+P2_CNT_READ_LATCH(CTR_MODULE, 1)
    Par_3=Par_3+P2_CNT_READ_LATCH(CTR_MODULE, 4)
    timervalue2=Read_timer()

    
    par_4=Max_long(par_4,timervalue2-timervalue1)
    FPar_2=0.5*FPar_2+0.5*(timervalue2-timervalue1)
    
    timervalue1=Read_timer()
   
    P2_Cnt_Read_Latch4(CTR_MODULE, carr, 1)
    Par_7=Par_7+carr[1]
    Par_8=Par_8+carr[4]
    
    timervalue2=Read_timer()
    Par_16=2^diod
    timervalue3=Read_timer()
    par_5=Max_long(par_5,timervalue2-timervalue1)
    par_6=Max_long(par_6,timervalue3-timervalue2)
    FPar_3=0.5*FPar_2+0.5*(timervalue2-timervalue1)
    inc(counter)
  else
    END
  endif
  
