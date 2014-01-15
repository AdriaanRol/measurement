'<ADbasic Header, Headerversion 001.001>
'<Header End>
#DEFINE number  23
DIM tf2_timer,par_tf2 as LONG

SUB init_tf2()
  par_tf2=42
  PAR_73=0
  tf2_timer=0
ENDSUB

FUNCTION tftwo(local_par) As LONG
  IF (tf2_timer=0) THEN
    tftwo=1  
    'PAR_73=1
  ENDIF
  
  IF (tf2_timer=175)THEN
    PAR_74=tf2_timer+1000+number
    tf2_timer=0
  ENDIF
  
  inc(tf2_timer)
  'PAR_73=tf2_timer
  
ENDFUNCTION

  
