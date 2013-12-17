'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 30000
' Eventsource                    = External
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

#define ctr_nr 01b                     ' use counter 1 from counter module
#define floating_sum_cycles 100         ' how much readout pulses should be summed

Dim Data_1[10000] As Long               ' spin readout counts
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
  P2_Cnt_Mode(CTR_MODULE,ctr_nr,1000)
  P2_Cnt_Clear(CTR_MODULE,ctr_nr)
  
  cycles = 10000

  sum_index = 1
  For i = 1 To floating_sum_cycles
    Data_1[i] = 0
  Next i

Event:
  P2_Cnt_Enable(CTR_MODULE,ctr_nr)
  CPU_Sleep(30)
  P2_Cnt_Enable(CTR_MODULE,0)
  
  cycles = cycles - 1
  If (cycles = 0) Then
    End
  Endif

Finish:
  P2_Cnt_Latch(CTR_MODULE,ctr_nr)
  Par_1 = P2_Cnt_Read_Latch(CTR_MODULE,ctr_nr)
