'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.5
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10238  TUD10238\localadmin
'<Header End>

#INCLUDE ADwinGoldII.inc

DIM repump_AOM_channel AS LONG           ' DAC channel for green laser AOM
DIM repump_AOM_voltage AS FLOAT           ' voltage of repump pulse
DIM repump_duration AS LONG        ' duration of repump pulse in units of 10µs
DIM pp_cycles AS LONG       ' how often to turn on green (N cycles of pump/probe in between)

DIM probe_AOM_channel AS LONG        
DIM probe_AOM_voltage AS FLOAT
DIM probe_duration AS LONG

DIM pump_AOM_channel AS LONG        
DIM pump_AOM_voltage AS FLOAT
DIM pump_duration AS LONG
dim prepump_duration as long

DIM do_repump AS LONG
DIM do_probe AS LONG

dim timer as long
dim avg_timer as long
dim cnt_timer as long
dim pp_cycle_timer as long
DIM i AS LONG
dim mode as long
dim cnts1 as long
dim cnts2 as long
dim cnts3 as long
dim cnts4 as long

dim single_shot as long
dim prepump as long
DIM float_avg AS long            ' Floating average time number of pp cycles

DIM DATA_41[100] AS FLOAT
DIM DATA_42[100] AS FLOAT
DIM DATA_43[100] AS FLOAT
DIM DATA_44[100] AS FLOAT

INIT:
  repump_AOM_channel = par_30
  pump_AOM_channel = par_31
  probe_AOM_channel = par_32
  
  repump_AOM_voltage = fpar_30
  pump_AOM_voltage = fpar_31
  probe_AOM_voltage = fpar_32
  
  repump_duration = par_33
  pump_duration = par_34
  probe_duration = par_35
  
  pp_cycles = par_36
  single_shot = par_37
  prepump = par_38
  prepump_duration = par_39
  
  float_avg = PAR_11
  if ((float_avg < 0) or (float_avg > 100)) then
    float_avg = 100
  endif
  
  DAC(repump_AOM_channel, 32768)
  DAC(pump_AOM_channel, 32768)
  DAC(probe_AOM_channel, 32768)
  
  do_repump = 0
  do_probe = probe_duration
  mode = 0
  cnts1 = 0
  cnts2 = 0
  cnts3 = 0
  cnts4 = 0
  
  timer = 0
  avg_timer = 1
  cnt_timer = 0
  pp_cycle_timer = 0
  
  for i = 1 to 100
    DATA_41[i] = 0
    DATA_42[i] = 0
    DATA_43[i] = 0
    DATA_44[i] = 0
  next i

  CNT_ENABLE(0000b)               'turn off all counters
  CNT_SE_DIFF(0000b)              'configure counters as single ended
  CNT_MODE(1,00001000b)           'configure counter one: 
  CNT_MODE(2,00001000b)           'configure counter one: 
  CNT_MODE(3,00001000b)           'configure counter one: 
  CNT_MODE(4,00001000b)           'configure counter one: 
  CNT_ENABLE(0000b)              
  CNT_CLEAR(1111b)  
  CNT_ENABLE(1111b)    
  'CONF_DIO(13)                    'configure DIO 08:15 as input, all other ports as output

EVENT:
  
  selectcase mode
    case 0 ' repumping
      if (timer = 0) then
        DAC(repump_AOM_channel, 3277*repump_AOM_voltage+32768)
      endif
      
      if (timer = repump_duration) then
        DAC(repump_AOM_channel, 32768)
        if (prepump > 0) then
          DAC(probe_AOM_channel, 3277*probe_AOM_voltage+32768)
        else
          mode = 1
          timer = -1
        endif
      endif
            
      if (prepump > 0) then
        if (timer = (repump_duration+prepump_duration)) then  ' first pump into ms=1 after repumping
          DAC(probe_AOM_channel, 32768)
          mode = 1
          timer = -1
        endif
      endif
      
    case 1 ' pumping
      if (timer = 0) then
        DAC(pump_AOM_channel, 3277*pump_AOM_voltage+32768)
      endif
      
      if (timer = pump_duration) then
        DAC(pump_AOM_channel, 32768)
        mode = 2
        timer = -1
      endif
      
    case 2 ' probing            
      if (timer = 0) then        
        if (pp_cycle_timer = 0) then
          DATA_41[avg_timer] = 0
          DATA_42[avg_timer] = 0
          DATA_43[avg_timer] = 0
          DATA_44[avg_timer] = 0
        endif
                
        CNT_ENABLE(0000b)
        CNT_CLEAR(1111b)
        CNT_ENABLE(1111b)
        
        DAC(probe_AOM_channel, 3277*probe_AOM_voltage+32768)
      endif
           
      if (timer = probe_duration) then
        DAC(probe_AOM_channel, 32768)
                      
        CNT_LATCH(1111b)       
        DATA_41[avg_timer] = DATA_41[avg_timer] + cnt_read_latch(1)
        DATA_42[avg_timer] = DATA_42[avg_timer] + cnt_read_latch(2)
        DATA_43[avg_timer] = DATA_43[avg_timer] + cnt_read_latch(3)
        DATA_44[avg_timer] = DATA_44[avg_timer] + cnt_read_latch(4)
        CNT_ENABLE(0000b)
        CNT_CLEAR(1111b)
               
        if (single_shot > 0) then          
          
          if (pp_cycle_timer = pp_cycles) then
            par_41 = data_41[avg_timer]
            par_42 = data_42[avg_timer]
            par_43 = data_43[avg_timer]
            par_43 = data_43[avg_timer]
            end
          else
            mode = 1
            inc(pp_cycle_timer)
            timer = -1
          endif        
        
        else
                                  
          if (pp_cycle_timer = pp_cycles) then
            
            inc(avg_timer)    
            if (avg_timer = (float_avg+1)) then
              avg_timer = 1
            endif
            
            cnts1 = 0
            cnts2 = 0
            cnts3 = 0
            cnts4 = 0
            for i = 1 to float_avg
              cnts1 = cnts1 + data_41[i]
              cnts2 = cnts2 + data_42[i]
              cnts3 = cnts3 + data_43[i]
              cnts4 = cnts4 + data_44[i]
            next i
            par_41 = cnts1 ' / float_avg
            par_42 = cnts2 ' / float_avg
            par_43 = cnts3 ' / float_avg
            par_44 = cnts4 ' / float_avg
                                  
            mode = 0
            pp_cycle_timer = 0
            timer = -1
          else
            mode = 1
            inc(pp_cycle_timer)
            timer = -1
          endif
        endif
      endif
         
  endselect
  
  inc(timer)
  
  

