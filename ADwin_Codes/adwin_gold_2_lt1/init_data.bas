'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 5
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277246  TUD277246\localadmin
'<Header End>

'Linescan:
DIM DATA_1[8] AS FLOAT
DIM DATA_197[8] AS FLOAT
DIM DATA_198[8] AS FLOAT
DIM DATA_199[8] AS FLOAT
DIM DATA_200[8] AS LONG
'DIM DATA_11[100000] AS LONG
'DIM DATA_12[100000] AS LONG
'DIM DATA_13[100000] AS LONG
'DIM DATA_14[100000] AS LONG
'DIM DATA_15[100000] AS FLOAT

'Conditional repump TPQI:
DIM DATA_8[100] AS LONG
DIM DATA_7[100] AS LONG

'Conditional repump:
'DIM DATA_51[10000] AS FLOAT

'Resonant counting, simple counting
DIM DATA_41[10000] AS FLOAT
DIM DATA_42[10000] AS FLOAT
DIM DATA_43[10000] AS FLOAT
DIM DATA_44[10000] AS FLOAT
DIM DATA_45[4] AS LONG

'Singleshot adwin:
DIM DATA_19[1000] AS FLOAT AT EM_LOCAL 
DIM DATA_20[300] AS LONG
DIM DATA_21[300] AS FLOAT
'DIM DATA_22[20000] AS LONG AT EM_LOCAL  ' CR counts before sequence
'DIM DATA_23[20000] AS LONG AT EM_LOCAL  ' CR counts after sequence
'DIM DATA_24[500] AS LONG AT EM_LOCAL      ' SP counts
'DIM DATA_25[1000000] AS LONG AT DRAM_EXTERN  ' SSRO counts
'DIM DATA_26[50] AS LONG AT EM_LOCAL         ' statistics 

INIT:

EVENT:
  END