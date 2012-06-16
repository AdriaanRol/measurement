"""
Module contains sequence snippets and elements relevant for SSRO measurements.
"""

def spinpumping_element(sequence, element_name='spinpumping', **kw):

    startpulse = kw.pop('startpulse', True)
    duration = kw.pop('duration', 200000)
    spinfilter = kw.pop('spinfilter', True)
    spinfilter_duration = kw.pop('spinfilter_duration', 50000)
    chan_exlaser = kw.pop('chan_exlaser', 'AOM_Matisse')
    chan_alaser = kw.pop('chan_alaser', 'AOM_Newfocus')
    chan_start = kw.pop('chan_start', 'PH_start')
    ex_amplitude = kw.pop('ex_amplitude', 0.)
    a_amplitude = kw.pop('a_amplitude', 0.)
    waitattheend = kw.pop('waitattheend', 1500)


    sequence.add_element(element_name)

    sequence.add_pulse('wait', chan_exlaser, element_name, start = 0, 
            duration = 500, amplitude = 0)

    sequence.add_pulse('sp_Ex', chan_exlaser, element_name, start = 0, 
            duration = duration, amplitude = ex_amplitude, 
            start_reference = 'wait', link_start_to = 'end')

    sequence.add_pulse('sp_A', chan_alaser, element_name, start = 0, 
            duration = 0, amplitude = a_amplitude, start_reference = 'sp_Ex', 
            link_start_to = 'start', duration_reference = 'sp_Ex', 
            link_duration_to = 'duration')

    if startpulse:
        sequence.add_pulse('start_sp', chan_start, element_name,
                start = -100, duration = 50, start_reference = 'sp_Ex',
                link_start_to = 'start')

    if spinfilter:
        sequence.add_pulse('start_sp_filter', chan_start, element_name, 
                start = -100-spinfilter_duration, duration = 50, 
                start_reference = 'sp_Ex',  link_start_to = 'end')

    sequence.add_pulse('waitattheend', chan_exlaser, element_name, start = 0, 
            duration = waitattheend, amplitude = 0, start_reference='sp_Ex',
            link_start_to='end')

    return 'waitattheend'

# FIXME this could potentially be too short. make sure we will in the front
# in this case
def mbi_element(sequence, element_name='mbi', **kw):

    chan_mwI = kw.pop('chan_mwI', 'MW_Imod')
    chan_mwQ = kw.pop('chan_mwQ', 'MW_Qmod')
    chan_exlaser = kw.pop('chan_exlaser', 'AOM_Matisse')
    chan_alaser = kw.pop('chan_alaser', 'AOM_Newfocus')
    chan_start = kw.pop('chan_start', 'PH_start')
    ex_amplitude = kw.pop('ex_amplitude', 0.)
    a_amplitude = kw.pop('a_amplitude', 0.)
    duration = kw.pop('duration', 300)
    startpulse = kw.pop('startpulse', True)
    selective_pi_frequency = kw.pop('selective_pi_frequency', 2.877e9)
    selective_pi_amplitude = kw.pop('selective_pi_amplitude', 0.)
    selective_pi_duration = kw.pop('selective_pi_duration', 1000)
    repump_duration = kw.pop('repump_duration', 0)
    repump_ex_amplitude = kw.pop('repump_ex_amplitude', 0.)
    repump_a_amplitude = kw.pop('repump_a_amplitude', 0.)
    waitattheend = kw.pop('waitattheend', 1500)
    chan_mwpulsemod = kw.pop('chan_mwpulsemod', 'MW_pulsemod')
    MW_pulse_mod_risetime = kw.pop('MW_pulse_mod_risetime', 20)
    shelvingmw = kw.pop('shelvingmw', True)
    shelvingmw_amplitude = kw.pop('shelvingmw_amplitude', 1.12)
    shelvingmw_duration = kw.pop('shelvingmw_duration', 400)
    
    sequence.add_element(element_name)

    sequence.add_IQmod_pulse('selective_pi', channel=(chan_mwI,chan_mwQ), 
            element=element_name, start=0, frequency=selective_pi_frequency,
            duration=selective_pi_duration, amplitude=selective_pi_amplitude)

    sequence.add_pulse('mbi_Ex', chan_exlaser, element_name, start=200, 
            duration=duration, amplitude=ex_amplitude, 
            start_reference='selective_pi-I', link_start_to='end')
            
    sequence.add_pulse('mbi_A', chan_alaser, element_name, start =0, 
            duration = 0, amplitude=a_amplitude, start_reference = 'mbi_Ex',
            link_start_to = 'start', duration_reference = 'mbi_Ex',
            link_duration_to = 'duration')

    sequence.add_pulse('start_mbi', chan_start, element_name, start = -100, 
            duration=50, start_reference='mbi_Ex', link_start_to='start')

    sequence.add_pulse('repump_Ex', chan_exlaser, element_name, start = 500, 
            duration = repump_duration, amplitude = repump_ex_amplitude, 
            start_reference = 'mbi_Ex', link_start_to = 'end')

    sequence.add_pulse('repump_A', chan_alaser, element_name, start = 0, 
            duration = 0, amplitude = repump_a_amplitude,  
            start_reference = 'repump_Ex', link_start_to = 'start', 
            duration_reference = 'repump_Ex', link_duration_to = 'duration')
    
    if shelvingmw:
        sequence.add_IQmod_pulse('shelving', channel=(chan_mwI,chan_mwQ), 
                element=element_name, start=1500, frequency=selective_pi_frequency,
                duration=shelvingmw_duration, amplitude=shelvingmw_amplitude,
                start_reference='repump_Ex', link_start_to='end')
        lastelement='shelving-I'
    else:
        lastelement='repump_Ex'

    sequence.add_pulse('waitattheend', chan_exlaser, element_name, start = 0, 
            duration=waitattheend, amplitude=0, start_reference=lastelement,
            link_start_to='end')

    sequence.clone_channel(chan_mwpulsemod, chan_mwI, element_name, 
            start = -MW_pulse_mod_risetime,
            duration = 2 * MW_pulse_mod_risetime,
            link_start_to = 'start', link_duration_to = 'duration', 
            amplitude = 2.0)

    return 'waitattheend'

# sequence already needs to exist for this one
def readout(sequence, element_name, **kw):

    start_reference = kw.pop('start_reference', '')
    start = kw.pop('start', 0)
    suffix = kw.pop('suffix', '')
    chan_exlaser = kw.pop('chan_exlaser', 'AOM_Matisse')
    chan_alaser = kw.pop('chan_alaser', 'AOM_Newfocus')
    chan_start = kw.pop('chan_start', 'PH_start')
    ex_amplitude = kw.pop('ex_amplitude', 0.)
    a_amplitude = kw.pop('a_amplitude', 0.)
    duration = kw.pop('duration', 10000)
    startpulse = kw.pop('startpulse', True)
    waitattheend = kw.pop('waitattheend', 1500)

    sequence.add_pulse('ro_Ex'+suffix, chan_exlaser, element_name, 
            start=start, duration = duration, amplitude = ex_amplitude, 
            start_reference = start_reference, link_start_to = 'end')

    sequence.add_pulse('ro_A'+suffix, chan_alaser, element_name, 
            start = 0, duration = 0, amplitude = a_amplitude, 
            start_reference = 'ro_Ex'+suffix, link_start_to = 'start', 
            duration_reference = 'ro_Ex'+suffix, link_duration_to = 'duration')

    if startpulse:
        sequence.add_pulse('start_ro'+suffix, chan_start, element_name, 
                start = -100, duration = 50, start_reference = 'ro_Ex'+suffix,
                link_start_to = 'start')
    
    sequence.add_pulse('waitattheend'+suffix, chan_exlaser, element_name, start = 0, 
            duration=waitattheend, amplitude=0, start_reference='ro_Ex'+suffix,
            link_start_to='end')

    return 'waitattheend'+suffix


def chargereadout_element(sequence, element_name='cr', **kw):
    
    adwin_conditional_repump = kw.pop('adwin_conditional_repump', True)
    chan_exlaser = kw.pop('chan_exlaser', 'AOM_Matisse')
    chan_alaser = kw.pop('chan_alaser', 'AOM_Newfocus')
    chan_start = kw.pop('chan_start', 'PH_start')
    chan_adwinsync = 'ADwin_sync'
    ex_amplitude = kw.pop('ex_amplitude', 0.)
    a_amplitude = kw.pop('a_amplitude', 0.)
    duration = kw.pop('duration', 100000)
    goto_target = kw.pop('goto_target', 'initialize')

    ejt = 'wait_for_ADwin' if adwin_conditional_repump else ''
    sequence.add_element(element_name, goto_target=goto_target,
            event_jump_target=ejt)

    sequence.add_pulse('cr_Ex', chan_exlaser, element_name, start=0, 
            duration = duration, amplitude = ex_amplitude)

    sequence.add_pulse('cr_A', chan_alaser, element_name, start = 0, 
            duration = 0, amplitude = a_amplitude, 
            start_reference = 'cr_Ex', link_start_to = 'start',
            duration_reference = 'cr_Ex', link_duration_to = 'duration')

    sequence.add_pulse('start_cr', chan_start, element_name, start = -100, 
            duration = 50, start_reference = 'cr_Ex', 
            link_start_to = 'start')

    if adwin_conditional_repump:
        sequence.add_pulse('ADwin_ionization_probe', chan_adwinsync, 
                element_name, start = 0, duration = -20000, 
                start_reference = 'cr_Ex', link_start_to = 'start', 
                duration_reference = 'cr_Ex', link_duration_to = 'duration')

        sequence.add_element('wait_for_ADwin', trigger_wait = True, 
                goto_target = goto_target)

        sequence.add_pulse('probe1', chan_exlaser, 'wait_for_ADwin', start=0, 
                duration = 1000, amplitude = ex_amplitude)
        
        # FIXME correction for cable delay should not be hardcoded!
        sequence.add_pulse('probe2', chan_alaser, 'wait_for_ADwin', start=-125, 
                duration = 1000, amplitude = a_amplitude)

    return None
