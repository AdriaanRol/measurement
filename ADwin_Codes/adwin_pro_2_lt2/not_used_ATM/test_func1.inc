'<ADbasic Header, Headerversion 001.001>
'<Header End>
DIM par_tf1 as LONG

SUB init_tf1()
  par_tf1=42
  PAR_71=42
ENDSUB

FUNCTION tfone() As LONG
  tfone=1
  PAR_71=par_tf1+global_par
ENDFUNCTION

  
