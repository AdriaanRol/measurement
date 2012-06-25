from measurement.AWG_HW_sequencer_v2 import Sequence
from matplotlib import pyplot as plt

HH_400.start_T3_mode()
HH_400.calibrate()
HH_400.set_Binning(8)



seq = Sequence('HH400_test')
seq.add_channel('sync', 'ch2m2', cable_delay=20, high=2, low=0)
seq.add_channel('ch0', 'ch1m1', cable_delay=0, high=2, low=0)
seq.add_channel('ch1', 'ch1m2', cable_delay=0, high=2, low=0)

pulses_in_element = 500
period = 200
pulse_duration = 25
pulse_ch0_offset = 25
pulse_ch1_offset = 25
extra_coincidence_element = False

# Configure hydraharp
par_binsize_T3 = 8     # resolution of recorded data in HH 1ps*2**binsize_T3
par_binsize_sync=0     # bintime = 1ps * 2**(binsize_T3 + binsize_sync)
par_range_sync=4*50    # bins
par_binsize_g2=0       # bintime = 1ps * 2**(binsize_g2 + binsize_T3)
par_range_g2=4*1000    # bins
par_sync_period = period  # ns

elt = 'coincidence'
seq.add_element(elt)

name = 'laser_0'
seq.add_pulse(name, 'sync', elt, start=0, duration=pulse_duration)
seq.add_pulse(name+'_off', 'sync', elt, start=pulse_duration, 
        duration=period-pulse_duration, amplitude = 0)
seq.add_pulse('start_0', 'ch0', elt, start=0+pulse_ch1_offset, duration=pulse_duration,
        start_reference=name, link_start_to='start')
#seq.add_pulse('stop_0', 'ch1', elt, start=0+pulse_ch0_offset, duration=pulse_duration,
#        start_reference=name, link_start_to='start')
photons_ch0 = 0
photons_ch1 = 0
for i in arange(pulses_in_element-1):
    seq.add_pulse('laser_'+str(i+1), 'sync', elt, start=period, duration=pulse_duration,
            start_reference=name, link_start_to='start')
    seq.add_pulse('laser_'+str(i+1)+'_off', 'sync', elt, start=period+pulse_duration, 
            duration=period-pulse_duration, amplitude = 0,
            start_reference=name, link_start_to='start')
    if random.random() < 1:
        photons_ch0 += 1
        decay_time = int(random.exponential(10))
        seq.add_pulse('start_'+str(i+1), 'ch0', elt, start=0+pulse_ch0_offset+decay_time, duration=pulse_duration,
            start_reference=name, link_start_to='start')
    if random.random() < 1:
        photons_ch1 += 1
        decay_time = int(random.exponential(10))
        seq.add_pulse('stop_'+str(i+1), 'ch1', elt, start=0+pulse_ch1_offset+decay_time, duration=pulse_duration,
            start_reference=name, link_start_to='start')
    name = 'laser_'+str(i+1)

#    seq.add_pulse('start_'+str(i+1), 'ch0', elt, start=0, duration=pulse_duration,
#            start_reference=name, link_start_to='start')
#    seq.add_pulse('stop_'+str(i+1), 'ch1', elt, start=0, duration=pulse_duration,
#            start_reference=name, link_start_to='start')

elt = 'no_coincidence'
seq.add_element(elt, goto_target = 'coincidence', repetitions = 1)
print 'number of photons on channel 0' , photons_ch0
print 'number of photons on channel 1' , photons_ch1
name = 'laser_0'
seq.add_pulse(name, 'sync', elt, start=0, duration=pulse_duration)
seq.add_pulse(name+'_off', 'sync', elt, start=pulse_duration, 
        duration=period-pulse_duration, amplitude = 0)
#seq.add_pulse('start_0', 'ch0', elt, start=0, duration=pulse_duration,
#        start_reference=name, link_start_to='start')
#seq.add_pulse('stop_0', 'ch1', elt, start=0, duration=pulse_duration,
#        start_reference=name, link_start_to='start')

for i in arange(10-1):
    seq.add_pulse('laser_'+str(i+1), 'sync', elt, start=period, duration=pulse_duration,
            start_reference=name, link_start_to='start')
    seq.add_pulse('laser_'+str(i+1)+'_off', 'sync', elt, start=period+pulse_duration, 
            duration=period-pulse_duration, amplitude = 0,
            start_reference=name, link_start_to='start')
    name = 'laser_'+str(i+1)

if extra_coincidence_element:
    elt = 'coincidence2'
    seq.add_element(elt,goto_target = 'no_coincidence2')

    name = 'laser_0'
    seq.add_pulse(name, 'sync', elt, start=0, duration=pulse_duration)
    seq.add_pulse(name+'_off', 'sync', elt, start=pulse_duration, 
            duration=period-pulse_duration, amplitude = 0)
    seq.add_pulse('start_0', 'ch0', elt, start=0+pulse_ch0_offset, duration=pulse_duration,
            start_reference=name, link_start_to='start')
    seq.add_pulse('stop_0', 'ch1', elt, start=0+pulse_ch1_offset, duration=pulse_duration,
        start_reference=name, link_start_to='start')
    for i in arange(pulses_in_element-1):
        seq.add_pulse('laser_'+str(i+1), 'sync', elt, start=period, duration=pulse_duration,
                start_reference=name, link_start_to='start')
        seq.add_pulse('laser_'+str(i+1)+'_off', 'sync', elt, start=period+pulse_duration, 
                duration=period-pulse_duration, amplitude = 0,
                start_reference=name, link_start_to='start')
        name = 'laser_'+str(i+1)

    elt = 'no_coincidence2'
    seq.add_element(elt, goto_target = 'coincidence', repetitions = 350)

    name = 'laser_0'
    seq.add_pulse(name, 'sync', elt, start=0, duration=pulse_duration)
    seq.add_pulse(name+'_off', 'sync', elt, start=pulse_duration, 
            duration=period-pulse_duration, amplitude = 0)
#seq.add_pulse('start_0', 'ch0', elt, start=0, duration=pulse_duration,
#        start_reference=name, link_start_to='start')
#seq.add_pulse('stop_0', 'ch1', elt, start=0, duration=pulse_duration,
#        start_reference=name, link_start_to='start')

    for i in arange(pulses_in_element-1):
        seq.add_pulse('laser_'+str(i+1), 'sync', elt, start=period, duration=pulse_duration,
                start_reference=name, link_start_to='start')
        seq.add_pulse('laser_'+str(i+1)+'_off', 'sync', elt, start=period+pulse_duration, 
                duration=period-pulse_duration, amplitude = 0,
                start_reference=name, link_start_to='start')
        name = 'laser_'+str(i+1)

seq.set_instrument(AWG)
seq.set_clock(1e9)
seq.set_send_waveforms(True)
seq.set_send_sequence(True)
seq.set_program_channels(True)
seq.set_start_sequence(True)
seq.force_HW_sequencing(True)
seq.send_sequence()

sleep(1)

HH_400.StartMeas(2000)
#histogram, hist_ch0, hist_ch1, hist_ch1_long = HH_400.get_T3_pulsed_g2_2DHistogram_v2(
#        binsize_T3 = par_binsize_T3,
#        binsize_sync = par_binsize_sync,
#        range_sync = par_range_sync,
#        binsize_g2 = par_binsize_g2,
#        range_g2 = par_range_g2,
#        sync_period = period,
#        )
histogram, hist_ch0, hist_ch1, hist_ch1_long = HH_400.get_T3_pulsed_g2_2DHistogram_v3(
        binsize_sync = par_binsize_sync,
        range_sync = par_range_sync,
        binsize_g2 = par_binsize_g2,
        range_g2 = par_range_g2,
        sync_period = period,
        )
        
        
dt = 2**(par_binsize_g2+par_binsize_T3) * linspace(-par_range_g2/2,par_range_g2/2,par_range_g2)/ 1e3
sync = 2**(par_binsize_sync+par_binsize_T3) * arange(par_range_sync) / 1e3
hist_1D = zeros(len(histogram[0,:]))
for i in arange(200):
    hist_1D += histogram[i,:]
plt.figure(1)
fig = plt.figure()
plt.plot(dt, hist_1D)
fig.show()
hist_1D_sync = zeros(len(histogram[:,0]))
for i in arange(4000):
    hist_1D_sync += histogram[:,i]

plt.figure(2)
fig2 = plt.figure()
plt.plot(sync,hist_1D_sync)
fig2.show()

