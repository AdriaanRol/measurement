## PLU test script
## assumes AWG ch1m1 -> APD1
##         AWG ch1m2 -> APD2
##         AWG ch2m1 -> ADWIN reset
##         AWG ch2m2 -> AWGclk


from measurement.AWG_HW_sequencer_v2 import Sequence
from matplotlib import pyplot as plt

pulse_nr = 20
ch0_delay_time = -20
ch1_delay_time = -20
reset_delay_time = -700

sync_intervals = ones(pulse_nr,dtype=int)*130    
ch0_events = zeros(pulse_nr,dtype=int)        
ch0_delays = ones(pulse_nr,dtype=int)+ch0_delay_time
ch1_events = zeros(pulse_nr,dtype=int)
ch1_delays = ones(pulse_nr,dtype=int)+ch1_delay_time
reset_events = zeros(pulse_nr,dtype=int)
reset_delays = ones(pulse_nr,dtype=int)+reset_delay_time

reset_events[0]=1

for i in arange(pulse_nr):
    if (i+1)%4==0:
#        ch0_events[i]=1
#        reset_events[i]=1
        sync_intervals[i]=1000
#    else:
#        ch1_events[i]=1

ch0_events[8]=0
ch1_events[9]=1
ch0_events[9]=0

ch0_events[12]=0
ch0_events[13]=1


seq = Sequence('PLU_test')
seq.add_channel('sync', 'ch2m2', cable_delay=0, high=2, low=0)
seq.add_channel('ch0', 'ch1m1', cable_delay=0, high=2, low=0)
seq.add_channel('ch1', 'ch1m2', cable_delay=0, high=2, low=0)
seq.add_channel('ma3', 'ch2m1', cable_delay=0, high=2, low=0)

pulse_duration = 50
photon_duration = 20

elt = 'plu_test'
seq.add_element(elt, repetitions = 1, goto_target=elt)


last = 'none'

for i in arange(len(sync_intervals)):
    name = 'sync_'+str(i)
    if i==0:
        seq.add_pulse(name, 'sync', elt, start=0, duration = pulse_duration)
    else:
        seq.add_pulse(name, 'sync', elt, start=0, duration = pulse_duration, 
            start_reference = last, link_start_to='end')
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



seq.set_instrument(AWG)
seq.set_clock(1e9)
seq.set_send_waveforms(True)
seq.set_send_sequence(True)
seq.set_program_channels(True)
seq.set_start_sequence(True)
seq.force_HW_sequencing(True)
seq.send_sequence()

sleep(2)



print('starting AWG sequence')
AWG.start()


