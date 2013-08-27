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
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
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
'DIM DATA_22[10000] AS LONG AT EM_LOCAL  
'DIM DATA_23[10000] AS LONG AT EM_LOCAL  
'DIM DATA_24[500] AS LONG AT EM_LOCAL      
'DIM DATA_25[500000] AS LONG AT DRAM_EXTERN 
'DIM DATA_26[10] AS LONG AT EM_LOCAL     

INIT:

EVENT:
  END
