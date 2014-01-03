'<ADbasic Header, Headerversion 001.001>
'<Header End>
' this program implements SSRO for ADwin Pro
'
' protocol:
' mode  0:  spin-readout



DIM ssro_timer,ssro_counts AS LONG

SUB init_SSRO()
  ssro_timer = 0
  ssro_counts=0
ENDSUB



FUNCTION SSRO(SSRO_duration) As LONG 
  SSRO=0
  IF (ssro_timer = 0) THEN
    CNT_CLEAR( counter_pattern)    'clear counter
    CNT_ENABLE(counter_pattern)    'turn on counter
    DAC(E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
    DAC(A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
  endif
  IF (ssro_timer = SSRO_duration) THEN
    DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
    DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
    ssro_counts = CNT_READ(counter_channel)
    CNT_ENABLE(0)
    SSRO=1 ' flag such that main program knows that SSRO is done.
    ssro_timer=-1
  ENDIF
  
  inc(ssro_timer)
    
ENDFUNCTION

