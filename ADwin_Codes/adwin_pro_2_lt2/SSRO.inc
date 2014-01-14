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
    P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
    P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
    P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
    P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
  endif
  IF (ssro_timer = SSRO_duration) THEN
    P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
    P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
    ssro_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
    P2_CNT_ENABLE(CTR_MODULE,0)
    SSRO=1 ' flag such that main program knows that SSRO is done.
    ssro_timer=-1
  ENDIF
  
  inc(ssro_timer)
    
ENDFUNCTION

