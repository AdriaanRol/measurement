'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 30000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#Include ADwinPro_All.Inc
#INCLUDE .\configuration.inc

Dim Data_1[10000] As Long
Dim i As Long
Dim num As Long
Dim cycles As Long
Dim temp As Long
Dim counting As Long
Dim APD_pulse As Long
Dim gate_on_time As Long
Dim APD_pulse_time As Long

#define di_gate 010b    ' DIO 1
#define di_counter 100b ' DIO 2

Init:
  P2_Digprog(DIO_MODULE, 0000b)        ' all channels input
  P2_Digin_FIFO_Enable(DIO_MODULE,0)   ' input FIFO with edge detection
  P2_Digin_FIFO_Clear(1)               ' clear FIFO
  P2_Digin_FIFO_Enable(DIO_MODULE,di_counter+di_gate) ' edge detection channels counter and gate
  Par_1 = 0 ' total counts
  Par_2 = 0 ' counts in detection window
  Par_3 = 0
  Par_4 = 0
  Par_5 = 0
  Par_6 = 0
  cycles = 10000
  counting = 0
  APD_pulse = 0
  

Event:
  num = P2_Digin_FIFO_Full(DIO_MODULE) ' number of value pairs in FIFO
  Par_4 = num
  P2_Digin_FIFO_Read_Fast(DIO_MODULE, num, Data_1, 1)
  For i = 1 To num
    temp = (Data_1[2*i-1] and di_gate)/di_gate
    If (temp <> counting) Then  ' gate edge detected
      If (temp = 1) Then        ' rising edge
        Par_5 = Par_5 + 1       ' increment gate counter
        gate_on_time = Data_1[2*i]
      Endif
      counting = temp
    Endif
    temp = (Data_1[2*i-1] and di_counter)/di_counter
    If (temp <> APD_pulse) Then     ' counter edge detected
      If (temp = 1) Then        ' rising edge
        Par_1 = Par_1 + 1       ' increment pulse counter
        If (counting = 1) Then  ' 
          APD_pulse_time = Data_1[2*i] - gate_on_time
          Par_7 = APD_pulse_time
          If ((APD_pulse_time >= 0) and (APD_pulse_time < 30)) Then
            Par_2 = Par_2 + 1     ' spin readout count
          Else
            Par_6 = Par_6 + 1     ' normalization count
          Endif
        Endif
      Endif
      APD_pulse = temp
    Endif
  Next i
  cycles = cycles - 1
  If (cycles = 0) Then
    End
  Endif

