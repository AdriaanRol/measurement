from measurement.AWG_HW_sequencer_v2 import Sequence

seq = Sequence('preselect')
seq.add_channel('Ex', 'ch1m1', cable_delay=0,high=1)
seq.add_channel('A2', 'ch1m2', cable_delay=604, high=1)
seq.add_channel('ADwin_sync', 'ch3m2', high=2.0, cable_delay =0)
#seq.add_channel('MW_Imod', 'ch1', high=0.9, low=-0.9, cable_delay = 199)
#seq.add_channel('MW_Qmod', 'ch4', high=0.9, low=-0.9, cable_delay = 0)


MW_pulse_mod_risetime = 0

seq.add_element('preselect', event_jump_target = 'wait_for_ADwin')
        
seq.add_pulse('cr1', 'Ex', 'preselect', duration = 1000, 
               amplitude = 1)

seq.add_pulse('cr1_2', 'A2', 'preselect', start = 0, duration = 0, 
              amplitude = 1, start_reference = 'cr1', link_start_to = 'start', 
              duration_reference = 'cr1', link_duration_to = 'duration')

seq.add_pulse('ADwin_ionization_probe', 'ADwin_sync', 'preselect', start = 0, 
              duration = 20000, start_reference = 'cr1', link_start_to = 'start', 
              duration_reference = 'cr1', link_duration_to = 'duration')

seq.add_element('wait_for_ADwin', trigger_wait = True, goto_target = 'readout')
seq.add_pulse('probe1', 'Ex', 'wait_for_ADwin', start=0, duration = 1000, 
               amplitude = 1)
seq.add_pulse('probe2', 'A2', 'wait_for_ADwin', start=0, duration = 1000, 
               amplitude = 1)

seq.set_instrument(AWG)
seq.set_clock(1e9)
seq.set_send_waveforms(True)
seq.set_send_sequence(True)
seq.set_program_channels(True)
seq.set_start_sequence(True)
seq.force_HW_sequencing(True)
seq.send_sequence()


