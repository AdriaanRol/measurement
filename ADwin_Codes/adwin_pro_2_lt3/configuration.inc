'<ADbasic Header, Headerversion 001.001>
'<Header End>
'  slot   module    description  address  tico
'    8   CPU T11   Processor    -        -
'    9   CNT-T     4 Counters   1       Yes
'    10  CIO 32    32 TTL DIOs  2       Yes
'    11  AIN 32/18 18bit ADC    3
'    12  AOUT 8/16 16bit DACs   4
'    14  AOUT 8/16 16bit DACs   5

#DEFINE CTR_MODULE 1  'Address of CNT-T
#DEFINE DIO_MODULE 2  'Address of DIO 32
#DEFINE ADC_MODULE 3  'Address of AIN 32/18
#DEFINE DAC_MODULE 4  'Address of AOUT 8/16
#DEFINE DAC_MODULE_2 5  'Address of AOUT 8/16

