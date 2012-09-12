## PLU test script
## assumes AWG ch1m1 -> APD1
##         AWG ch1m2 -> APD2
##         AWG ch2m1 -> ADWIN reset
##         AWG ch2m2 -> AWGclk


from measurement.AWG_HW_sequencer_v2 import Sequence
from matplotlib import pyplot as plt
from numpy import random

pulse_nr = 300
ch0_delay_time = -30
#ch0_delay_time=[random.randint(-20,20) for r in range(pulse_nr)]
ch1_delay_time = -30
#ch1_delay_time=[random.randint(-20,20) for r in range(pulse_nr)]
reset_delay_time = -700

sync_intervals = ones(pulse_nr,dtype=int)*130    
ch0_events = zeros(pulse_nr,dtype=int)
ch0_events_wait = ones(pulse_nr,dtype=int)
ch0_delays = ones(pulse_nr,dtype=int)+ch0_delay_time
ch1_events = zeros(pulse_nr,dtype=int)
ch1_events_wait = ones(pulse_nr,dtype=int)
ch1_delays = ones(pulse_nr,dtype=int)+ch1_delay_time
reset_events = zeros(pulse_nr,dtype=int)
reset_delays = ones(pulse_nr,dtype=int)+reset_delay_time

reset_events[0]=1

photon_pulse_nr=[random.random() for r in range(pulse_nr)]

events=0
for i in arange(pulse_nr):
    
    if (i+1)%3==0:sync_intervals[i]=100
    if (i+1)%4==0:sync_intervals[i]=1000
    if (i+1)%4==0:reset_events[i]=1
    if photon_pulse_nr[i]>0.5:
        if (i+1)%4==0:
            ch0_events[i-3]=1
            ch0_events[i-2]=1
            events+=1



#    else:
#        ch1_events[i]=1

#ch0_events[8]=1
#ch1_events[8]=0
#ch0_events[9]=1

#ch0_events[12]=0
#ch0_events[13]=1


seq = Sequence('PLU_test')
seq.add_channel('sync', 'ch2m2', cable_delay=0, high=2, low=0)
seq.add_channel('ch0', 'ch1m1', cable_delay=0, high=2, low=0)
seq.add_channel('ch1', 'ch1m2', cable_delay=0, high=2, low=0)
seq.add_channel('ma3', 'ch2m1', cable_delay=40, high=2, low=0)
seq.add_channel('hhsync','ch3m1', cable_delay=000, high=2, low=0)

pulse_duration = 70

photon_duration = 20

elt = 'plu_test'
wait = 'wait'
elt2 = 'plu_test2'

seq.add_element(elt, repetitions = 1, goto_target = 'wait')
seq.add_element(wait, repetitions = 1, goto_target = 'elt2')
seq.add_element(elt2, repetitions = 1)

last = 'none'

for i in arange(len(sync_intervals)):
    name = 'sync_'+str(i)
    if i==0:
        seq.add_pulse(name, 'sync', elt, start=0, duration = pulse_duration)
        
    else:
        seq.add_pulse(name, 'sync', elt, start=0, duration = pulse_duration, 
            start_reference = last, link_start_to='end')

    if (i+2)%4==0:seq.add_pulse('sync'+str(i), 'hhsync', elt, start_reference = name, link_start_to='end', duration = pulse_duration)
        

    last = name+'_off'
    seq.add_pulse(last, 'sync', elt, start=pulse_duration, 
            duration = sync_intervals[i]-pulse_duration, amplitude = 0,
            start_reference = name, link_start_to='end')
    if ch0_events[i]:
        seq.add_pulse('ch0_'+str(i), 'ch0', elt, start = ch0_delays[i],
                duration = photon_duration, start_reference = name,
                link_start_to='end')
    if ch1_events[i]:
        seq.add_pulse('ch1_'+str(i), 'ch1', elt, start = ch1_delays[i],
                duration = photon_duration, start_reference = name,
                link_start_to='end')
    if reset_events[i]:
        seq.add_pulse('ma3_'+str(i), 'ma3', elt, start = reset_delays[i],
                duration = pulse_duration, start_reference = name,
                link_start_to='end')

seq.add_pulse('wait','ma3', wait, start=0, duration = 10000, amplitude =0)

for i in arange(len(sync_intervals)):
    name = 'sync_'+str(i)
    if i==0:
        seq.add_pulse(name, 'sync', wait, start=0, duration = pulse_duration,amplitude = 0)
        seq.add_pulse('sync', 'hhsync', wait, start=0, duration = pulse_duration)
    else:
        seq.add_pulse(name, 'sync', wait, start=0, duration = pulse_duration ,amplitude = 0, 
            start_reference = last, link_start_to='end')      
    last = name+'_off'
    seq.add_pulse(last, 'sync', wait, start=pulse_duration, 
            duration = sync_intervals[i]-pulse_duration, amplitude = 0,
            start_reference = name, link_start_to='end')
    if ch0_events_wait[i]:
        seq.add_pulse('ch0_'+str(i), 'ch0', wait, start = ch0_delays[i],
                duration = photon_duration, start_reference = name,
                link_start_to='end')
    if ch1_events_wait[i]:
        seq.add_pulse('ch1_'+str(i), 'ch1', wait, start = ch1_delays[i],
                duration = photon_duration, start_reference = name,
                link_start_to='end')
    if reset_events[i]:
#ch0_delay_time=[random.randint(-20,20) for r in range(pulse_nr)]
        seq.add_pulse('ma3_'+str(i), 'ma3', wait, start = reset_delays[i],
                duration = pulse_duration, start_reference = name,
                link_start_to='end')  

last = 'none'

for i in arange(len(sync_intervals)):
    name = 'sync_'+str(i)
    if i==0:
        seq.add_pulse(name, 'sync', elt2, start=0, duration = pulse_duration)
        
    else:
        seq.add_pulse(name, 'sync', elt2, start=0, duration = pulse_duration, 
            start_reference = last, link_start_to='end')
    if (i+2)%4==0:seq.add_pulse('sync'+str(i), 'hhsync', elt2, start_reference = name, link_start_to='end', duration = pulse_duration)
        #print 'addnig hh'
       
    last = name+'_off'
    seq.add_pulse(last, 'sync', elt2, start=pulse_duration, 
            duration = sync_intervals[i]-pulse_duration, amplitude = 0,
            start_reference = name, link_start_to='end')
    if ch0_events[i]:
        seq.add_pulse('ch0_'+str(i), 'ch0', elt2, start = ch0_delays[i],
                duration = photon_duration, start_reference = name,
                link_start_to='end')
    if ch1_events[i]:
        seq.add_pulse('ch1_'+str(i), 'ch1', elt2, start = ch1_delays[i],
                duration = photon_duration, start_reference = name,
                link_start_to='end')
    if reset_events[i]:
        seq.add_pulse('ma3_'+str(i), 'ma3', elt2, start = reset_delays[i],
                duration = pulse_duration, start_reference = name,
                link_start_to='end')        

seq.set_instrument(AWG)
seq.set_clock(1e9)
seq.set_send_waveforms(True)
seq.set_send_sequence(True)
seq.set_program_channels(True)
seq.set_start_sequence(False)
seq.force_HW_sequencing(True)
seq.send_sequence()

sleep(2)



print('starting AWG sequence')
AWG.start()

print 'events', events
