from measurement.AWG_HW_sequencer import Sequence

f_mod = -5e6
period = 1000 if f_mod == 0 else abs((1/f_mod)*1e9)

MW_pulse_mod_risetime = 20

seq = Sequence('IQ')
seq.add_channel('MW_Imod', 'ch3', high=2.25, low=-2.25, cable_delay = 120)
seq.add_channel('MW_Qmod', 'ch4', high=2.25, low=-2.25, cable_delay = 120)
seq.add_channel('MW_pulsemod', 'ch4m2', high=2.0, cable_delay = 120)

seq.add_element('iq', goto_target='iq')


seq.add_IQmod_pulse(name='mw', channel=('MW_Imod', 'MW_Qmod'), 
    element='iq', start = 0, duration = 50*period, frequency=f_mod,
    amplitude=2.25)

seq.add_pulse('mwon', 'MW_pulsemod', 'iq', start=0, duration=50*period, 
        amplitude=1.)

seq.set_instrument(AWG)
seq.set_clock(1e9)
seq.set_send_waveforms(True)
seq.set_send_sequence(True)
seq.set_program_channels(True)
seq.set_start_sequence(True)
seq.force_HW_sequencing(True)
seq.send_sequence()


