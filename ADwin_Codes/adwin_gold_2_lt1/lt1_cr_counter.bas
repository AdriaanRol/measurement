'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' count photons during different pump/probe intervals. 
' keep count number for each interval

#INCLUDE ADwinGoldII.inc

#DEFINE max_cycles 20000

dim data_22[max_cycles] AS LONG AT EM_LOCAL ' probe photons
dim data_23[max_cycles] AS LONG AT EM_LOCAL ' pump photons

dim cycles as long
dim mode as long
dim i as long
dim current_cycle as long
dim timer as long

dim pump_aom_dac as long
dim probe_aom1_dac as long
dim probe_aom2_dac as long

dim pump_aom_voltage as float
dim probe_aom1_voltage as float
dim probe_aom2_voltage as float

dim pump_time as long
dim post_pump_time as long
dim probe_time as long
dim post_probe_time as long

dim counter_channel as long
dim counter_pattern as long

init:
  cycles = par_60
  current_cycle = 1
  
  pump_aom_dac = par_61
  probe_aom1_dac = par_62
  probe_aom2_dac = par_63
  
  pump_aom_voltage = fpar_61
  probe_aom1_voltage = fpar_62
  probe_aom2_voltage = fpar_63
  
  pump_time = par_64
  post_pump_time = par_65
  probe_time = par_66
  post_probe_time = par_67
  
  counter_channel = 1
  counter_pattern = 2^(counter_channel-1)
  
  for i = 1 to max_cycles:
    data_22[i] = 0
    data_23[i] = 0
  next i
  
  mode = 0
  timer = 0
  
  DAC(pump_aom_dac, 32768)
  DAC(probe_aom1_dac, 32768)
  DAC(probe_aom2_dac, 32768)
  
  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter
  
event:
  par_80 = current_cycle
  par_79 = mode
  par_78 = timer
  
  selectcase mode
    case 0 ' pump
      if (timer = 0) then
        CNT_CLEAR(counter_pattern)
        CNT_ENABLE(counter_pattern)
        DAC(pump_aom_dac, 3277*pump_aom_voltage+32768)
      endif
      
      if (timer = pump_time) then
        DAC(pump_aom_dac, 32768)
        data_22[current_cycle] = CNT_READ(counter_channel)
        CNT_ENABLE(0)
        
        mode = 1
        timer = -1
      endif
      
    case 1
      if (timer = post_pump_time) then
        mode = 2
        timer = -1
      endif
      
    case 2 ' probe
      if (timer = 0) then
        CNT_CLEAR(counter_pattern)
        CNT_ENABLE(counter_pattern)
        DAC(probe_aom1_dac, 3277*probe_aom1_voltage+32768)
        DAC(probe_aom2_dac, 3277*probe_aom2_voltage+32768)
      endif
      
      if (timer = pump_time) then
        DAC(probe_aom1_dac, 32768)
        DAC(probe_aom2_dac, 32768)
        data_23[current_cycle] = CNT_READ(counter_channel)
        CNT_ENABLE(0)
                
        mode = 3
        timer = -1
      endif 
      
    case 3
      if (timer = post_probe_time) then
        inc(current_cycle)
        if (current_cycle > cycles) then
          end
        endif
        
        mode = 0
        timer = -1
      endif
        
  endselect
    
  inc(timer)
  
finish:
  
  

