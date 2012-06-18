from measurement.AWG_HW_sequencer_v2 import Sequence

seq = Sequence('argh')
seq.add_channel('PH_start', 'ch4m2', cable_delay=0)
seq.add_channel('Green', 'ch2m1', cable_delay=604, high=0.5)
seq.add_channel('MW_pulsemod', 'ch2m2', high=2.0, cable_delay = 0)
seq.add_channel('MW_Imod', 'ch1', high=0.9, low=-0.9)
#seq.add_channel('MW_Qmod', 'ch4', high=0.9, low=-0.9, cable_delay = 0)
seq.add_channel('trigger','ch1m2', high=2.0)
seq.add_channel('pm','ch1m1', high=2.0, cable_delay=27)


MW_pulse_mod_risetime = 0

elt = 'test'
seq.add_element(elt, goto_target = elt)
#seq.add_pulse('PH', 'PH_start', elt, start=0, duration=50)

#seq.add_pulse('Green', 'Green', elt, start=0, amplitude = 1, duration=5000,start_reference = 'PH',link_start_to='end')
#seq.add_pulse('Wait', 'Green', elt, start=0, amplitude=1,duration=750,start_reference = 'Green',link_start_to='end')

#seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod','MW_Qmod'), 
#                    element=elt, start = 2000, duration = 1500, 
#                    start_reference = 'Green', 
#                    link_start_to = 'start', frequency=0)

#seq.clone_channel('MW_pulsemod', 'MW_Imod', elt, 
#                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
#                link_start_to = 'start', link_duration_to = 'duration', 
#                amplitude = 2.0)
seq.add_pulse(name='trigger', channel = 'trigger', element=elt, 
        start = 0, duration = 50 )
seq.add_pulse(name='wait', channel = 'trigger', element=elt, 
        start_reference='trigger',link_start_to='end', duration = 848, amplitude = 0)
seq.add_pulse(name='pm', channel = 'pm', element=elt, 
        start_reference='wait',link_start_to='end', duration = 500)
seq.add_pulse(name='MW_Imod', channel = 'MW_Imod',element = elt, duration = 10, start_reference='pm',link_start_to = 'start', start=50,amplitude = 1)
##seq.add_pulse(name='MWpulse', channel = 'pm', element=elt, 
##        start_reference='wait',link_start_to='end', duration = 100)


seq.set_instrument(AWG)
seq.set_clock(1e9)
seq.set_send_waveforms(True)
seq.set_send_sequence(True)
seq.set_program_channels(True)
seq.set_start_sequence(True)
seq.force_HW_sequencing(True)
seq.send_sequence()


