'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 10
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
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

DIM U_max_x AS FLOAT
DIM U_max_y AS FLOAT
DIM U_max_z AS FLOAT
DIM U_min_x AS FLOAT
DIM U_min_y AS FLOAT
DIM U_min_z AS FLOAT
DIM U_x AS FLOAT
DIM U_y AS FLOAT
DIM U_z AS FLOAT
DIM U_x_now AS FLOAT
DIM U_y_now AS FLOAT
DIM U_z_now AS FLOAT
DIM Speed AS FLOAT
DIM Reached_X AS INTEGER
DIM Reached_Y AS INTEGER
DIM Reached_Z AS INTEGER
' The current position
DIM DATA_1[3] AS FLOAT


INIT:
  U_max_x = 10
  U_min_x = 0
  U_max_y = 10
  U_min_y = 0
  U_max_z = 10
  U_min_z = 0
  U_x_now = DATA_1[1]
  U_y_now = DATA_1[2]
  U_z_now = DATA_1[3]
  Speed = FPAR_29   'in mV/s
  Reached_X = 0
  Reached_Y = 0
  Reached_Z = 0
  U_x = FPAR_22
  U_y = FPAR_23
  U_z = FPAR_24

EVENT:
  IF ((U_x < U_min_x) OR (U_x > U_max_x)) THEN
    END
  ENDIF
  IF ((U_y < U_min_y) OR (U_y > U_max_y)) THEN
    END
  ENDIF
  IF ((U_z < U_min_z) OR (U_z > U_max_z)) THEN
    END
  ENDIF

  IF (Reached_X = 0) THEN
    IF ((U_x_now - U_x) > (Speed/1000000.0)) THEN
      U_x_now = U_x_now - (Speed/1000000.0)
    ENDIF
    
    IF ((U_x_now - U_x) < (Speed/1000000.0)) THEN
      U_x_now = U_x_now + (Speed/1000000.0)
    ENDIF
    
    IF (ABSF(U_x_now - U_x) < 2*(Speed/1000000.0)) THEN
      U_x_now = U_x
      Reached_X = 1
    ENDIF
    P2_DAC(DAC_Module,1, U_x_now*3277+32768)
    DATA_1[1] = U_x_now
   
  ENDIF
  
  IF (Reached_Y = 0) THEN
    IF ((U_y_now - U_y) > (Speed/1000000.0)) THEN
      U_y_now = U_y_now - (Speed/1000000.0)
    ENDIF
    
    IF ((U_y_now - U_y) < (Speed/1000000.0)) THEN
      U_y_now = U_y_now + (Speed/1000000.0)
    ENDIF
    
    IF (ABSF(U_y_now - U_y) < 2*(Speed/1000000.0)) THEN
      U_y_now = U_y
      Reached_Y = 1
    ENDIF
    P2_DAC(DAC_Module,2, U_y_now*3277+32768)
    DATA_1[2] = U_y_now
   
  ENDIF
  
  IF (Reached_Z = 0) THEN
    IF ((U_z_now - U_z) > (Speed/1000000.0)) THEN
      U_z_now = U_z_now - (Speed/1000000.0)
    ENDIF
    
    IF ((U_z_now - U_z) < (Speed/1000000.0)) THEN
      U_z_now = U_z_now + (Speed/1000000.0)
    ENDIF
    
    IF (ABSF(U_z_now - U_z) < 2*(Speed/1000000.0)) THEN
      U_z_now = U_z
      Reached_Z = 1
    ENDIF
    P2_DAC(DAC_Module,3, U_z_now*3277+32768)
    DATA_1[3] = U_z_now
   
  ENDIF
  
  IF (((Reached_X = 1) AND (Reached_Y = 1)) AND (Reached_Z = 1)) THEN
    Data_1[1] = U_x
    Data_1[2] = U_y
    Data_1[3] = U_z
    END
  ENDIF
  
  ' Piezo scanner: 0..60V (300K), 0..150V (4K)

