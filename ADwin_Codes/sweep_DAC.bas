'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 6
' Initial_Processdelay           = 300000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' sweeps DAC voltage at a rate of 1 kHz
' PAR_63:  DAC number
' FPAR_69: sweep start voltage
' FPAR_64: sweep stop voltage
' FPAR_65: sweep rate (in V/s)

#INCLUDE ADwinPro_All.inc
#INCLUDE configuration.inc

DIM DAC_NR AS INTEGER
DIM U_START AS FLOAT
DIM U_STOP AS FLOAT
DIM U_NOW AS FLOAT
DIM U_STEP AS FLOAT
DIM SWEEP_RATE AS FLOAT   ' in V / s
DIM COUNTER AS LONG

INIT:
  DAC_NR = PAR_63
  U_START = FPAR_69
  U_STOP = FPAR_64
  
  SWEEP_RATE = FPAR_65

  IF (U_START > U_STOP) THEN
    U_STEP = -SWEEP_RATE / 1000.0
  ELSE
    U_STEP = SWEEP_RATE / 1000.0
  ENDIF
      
  COUNTER = 0
  P2_DAC(DAC_MODULE,PAR_63,U_START*3277+32768)
  
EVENT:
  COUNTER = COUNTER + 1
  U_NOW = U_START + COUNTER * U_STEP
  P2_DAC(DAC_MODULE,PAR_63,U_NOW*3277+32768)
  FPAR_69 = U_NOW
  
  IF (COUNTER >= (U_STOP-U_START)/U_STEP) THEN
    END
  ENDIF
  
  
  
    
