## Hydraharp T3 mode test script
## assumes AWG ch1m1 -> HH_ch0
##         AWG ch1m2 -> HH_ch1
##         AWG ch2m1 -> HH_MA3
##         AWG ch2m2 -> HH_sync


from measurement.AWG_HW_sequencer_v2 import Sequence
from matplotlib import pyplot as plt

HH_400.start_T3_mode()
HH_400.calibrate()
HH_400.set_Binning(8)
HH_400.set_SyncDiv(1)

pulse_nr = 100
ch0_delay_time = 40
ch1_delay_time = 40

sync_intervals = ones(pulse_nr,dtype=int)*500    
ch0_events = ones(pulse_nr,dtype=int)        
ch0_delays = ones(pulse_nr,dtype=int)+ch0_delay_time
ch1_events = ones(pulse_nr,dtype=int)
ch1_delays = ones(pulse_nr,dtype=int)+ch1_delay_time
MA3_events = zeros(pulse_nr,dtype=int)
MA3_delays = zeros(pulse_nr,dtype=int)

wait= 1000 #waiting time in 100 us

#for i in arange(pulse_nr):
#    ch0_events[i] = i % 2
#    ch1_events[i] = 1- (i % 2)

#sync_intervals[0] = 421
#sync_intervals[1] = 3463
#sync_intervals[2] = 4544
#sync_intervals[3] = 3333
#sync_intervals[50] = 2343200

#ch0_delays[49] = 2300500
#ch1_delays[49] = 2300500

#ch0_delays[50] = 2300000
#ch1_delays[50] = 2300000

#sync_intervals[5] = 1423
#sync_intervals[6] = 345
#sync_intervals[7] = 6456
#sync_intervals[8] = 453
#sync_intervals[9] = 3463

seq = Sequence('HH400_test')
seq.add_channel('sync', 'ch2m2', cable_delay=20, high=2, low=0)
seq.add_channel('ch0', 'ch1m1', cable_delay=0, high=2, low=0)
seq.add_channel('ch1', 'ch1m2', cable_delay=0, high=2, low=0)
seq.add_channel('ma3', 'ch2m1', cable_delay=0, high=2, low=0)

pulse_duration = 25

# Configure hydraharp
par_binsize_T3 = 8     # resolution of recorded data in HH 1ps*2**binsize_T3

elt = 'hh_test'
seq.add_element(elt, repetitions = 5, goto_target='idle')
seq.add_element('idle', repetitions = wait, goto_target = 'late_ph')
seq.add_element('late_ph')
seq.add_element(elt+'2', repetitions = 5)

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
                duration = pulse_duration, start_reference = name,
                link_start_to='end')
    if ch1_events[i]:
        seq.add_pulse('ch1_'+str(i), 'ch1', elt, start = ch1_delays[i],
                duration = pulse_duration, start_reference = name,
                link_start_to='end')
    if MA3_events[i]:
        seq.add_pulse('ma3_'+str(i), 'ma3', elt, start = MA3_delays[i],
                duration = pulse_duration, start_reference = name,
                link_start_to='end')

seq.add_pulse('empty','ch0','idle',start=0,duration=100000,amplitude=0)

seq.add_pulse('ch0','ch0','late_ph',start=0,duration=25)
seq.add_pulse('ch1','ch1','late_ph',start=0,duration=25)

for i in arange(len(sync_intervals)):
    name = 'sync_'+str(i)
    if i==0:
        seq.add_pulse(name, 'sync', elt+'2', start=0, duration = pulse_duration)
    else:
        seq.add_pulse(name, 'sync', elt+'2', start=0, duration = pulse_duration, 
            start_reference = last, link_start_to='end')
    last = name+'_off'
    seq.add_pulse(last, 'sync', elt+'2', start=pulse_duration, 
            duration = sync_intervals[i]-pulse_duration, amplitude = 0,
            start_reference = name, link_start_to='end')
    if ch0_events[i]:
        seq.add_pulse('ch0_'+str(i), 'ch0', elt+'2', start = ch0_delays[i],
                duration = pulse_duration, start_reference = name,
                link_start_to='end')
    if ch1_events[i]:
        seq.add_pulse('ch1_'+str(i), 'ch1', elt+'2', start = ch1_delays[i],
                duration = pulse_duration, start_reference = name,
                link_start_to='end')
    if MA3_events[i]:
        seq.add_pulse('ma3_'+str(i), 'ma3', elt+'2', start = MA3_delays[i],
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

print('starting HH measurement')
HH_400.StartMeas(2000)
sleep(1)

print('starting AWG sequence')
AWG.start()

ch0_cts = 0
ch1_cts = 0
ofl = 0

while HH_400.get_MeasRunning() == True:
    length, data = HH_400.get_TTTR_Data()
    flags = HH_400.get_Flags()
    if (flags != 0) and (flags != 4):
        print('flag: %s'%flags) 
    warnings = HH_400.get_Warnings()
    if warnings != 0:
        WarningText = HH_400.get_WarningsText(warning)
        print WarningText

    HH_400.get_Warnings()
    if length>0:
#         print length
        for i in arange(length):
            nsync   = data[i] & (2**10 - 1)
            event_time = (data[i] >> 10) & (2**15 - 1)
            channel = (data[i] >> 25) & (2**6 - 1)
            special = (data[i] >> 31) & 1
            if (495<nsync<505):
                print ('%s\t%s\t%s\t%s'%(special,channel,event_time,nsync))
            if channel == 0:
                ch0_cts += 1
#                if event_time != 335:    #335
#                    print ('%s\t%s\t%s\t%s'%(special,channel,event_time,nsync))
            if channel == 1:
                ch1_cts += 1
#                if event_time != 334: #490
#                    print ('%s\t%s\t%s\t%s'%(special,channel,event_time,nsync))
            if channel == 63:
                ofl += 1

print ('ch0: %s, ch1: %s, ofl: %s'%(ch0_cts,ch1_cts,ofl))





