from measurement.config import awgchannels_lt2 as awgcfg
from measurement.AWG_HW_sequencer_v2 import Sequence

seq = Sequence('argh')

os.chdir('D:/measuring/qtlab/')
reload(awgcfg)
os.chdir('D:/measuring/user/scripts/lt2_scripts/')

awgcfg.configure_sequence(seq,'mw','optical_rabi','hydraharp')

#seq.add_channel('PH_start', 'ch4m2', cable_delay=0)
#seq.add_channel('Green', 'ch2m1', cable_delay=604, high=0.5)
#seq.add_channel('MW_pulsemod', 'ch2m2', high=2.0, cable_delay = 0)
#seq.add_channel('MW_Imod', 'ch1', high=0.9, low=-0.9)
#seq.add_channel('MW_Qmod', 'ch4', high=0.9, low=-0.9, cable_delay = 0)
#seq.add_channel('pm','ch1m1', high=2.0, cable_delay=27)

MW_pulse_mod_risetime = 10#6 = correct for LT2, 2 =  correct for LT1
MW_Imod_duration = 1000

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

seq.add_pulse(name='trigger', channel = 'HH_sync', element=elt, 
        start = 0, duration = 50)

#seq.add_pulse(name='mat_eom', channel = 'EOM_Matisse', element = elt, start = 0, 
#        duration = 50, amplitude = 0.0, start_reference = 'trigger',
#        link_start_to = 'end')
#seq.add_pulse(name='mat_aom', channel = 'EOM_AOM_Matisse', element = elt, 
#        start = 0, duration = 50, amplitude = 0.0,start_reference = 'trigger',
#        link_start_to = 'end')
#seq.add_pulse(name='newf_aom', channel = 'AOM_Newfocus', element = elt, 
#        start = 0, duration = 50, amplitude = 0.7, start_reference = 'trigger',
#        link_start_to = 'end')



#seq.add_pulse(name='trigger', channel = 'trigger', element=elt, 
#        start = 0, duration = 50 )
#seq.add_pulse(name='wait', channel = 'trigger', element=elt, 
#        start_reference='trigger',link_start_to='end', duration = 948, amplitude = 0)
seq.add_pulse(name='MW_Imod', channel = 'MW_Imod_lt1',element = elt, duration = MW_Imod_duration, 
        start_reference='trigger',link_start_to = 'end', start=500,amplitude = 1)
seq.add_pulse(name = 'MW_Pmod', channel = 'MW_pulsemod', element = elt,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'MW_Imod', link_start_to = 'start', duration_reference = 'MW_Imod', link_duration_to = 'duration')
seq.add_pulse(name='wait', channel = 'PLU_Gate', element = elt, start = 0,
        amplitude=0, duration = 10000,start_reference = 'trigger',
        link_start_to = 'end')

#print 'MW pulse mod duration = ',(2*MW_pulse_mod_risetime+MW_Imod_duration)
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


