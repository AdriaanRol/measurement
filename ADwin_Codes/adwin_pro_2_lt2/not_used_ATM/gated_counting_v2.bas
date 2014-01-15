'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 30000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 2
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#Include ADwinPro_All.Inc
#INCLUDE .\configuration.inc

#define di_gate 010b                    ' DIO 1
#define di_counter 100b                 ' DIO 2
#define floating_sum_cycles 100         ' how much readout pulses should be summed

Dim Data_1[10000] As Long               ' readout buffer
Dim Data_2[floating_sum_cycles] As Long ' spin readout counts
Dim Data_3[floating_sum_cycles] As Long ' normalization counts
Dim i As Long
Dim sum_index As Long
Dim num As Long
Dim cycles As Long
Dim temp As Long
Dim counting As Long
Dim APD_pulse As Long
Dim gate_on_time As Long
Dim APD_pulse_time As Long

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
  Par_10= 0
  Par_11= 0
  cycles = 10000
  counting = 0
  APD_pulse = 0
  sum_index = 1
  For i = 1 To floating_sum_cycles
    Data_2[i] = 0
    Data_3[i] = 0
  Next i

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
        Par_10 = Par_10 + Data_2[sum_index]
        Par_11 = Par_11 + Data_3[sum_index]
        sum_index = sum_index + 1
        If (sum_index = floating_sum_cycles + 1) Then
          sum_index = 1
        Endif
        Par_10 = Par_10 - Data_2[sum_index]
        Par_11 = Par_11 - Data_3[sum_index]
        Data_2[sum_index] = 0
        Data_3[sum_index] = 0
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
            Data_2[sum_index] = Data_2[sum_index] + 1
          Else
            Par_6 = Par_6 + 1     ' normalization count
            Data_3[sum_index] = Data_3[sum_index] + 1
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

