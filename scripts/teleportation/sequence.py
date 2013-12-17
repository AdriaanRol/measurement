from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import qt
import numpy as np

import parameters as tparams
reload(tparams)


def pulse_defs_lt2(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)

    msmt.TIQ = pulse.SquarePulse(channel='MW_Imod',
        length = 10e-9, amplitude = 0)

    # some not yet specified pulse on the electron
    msmt.e_pulse = pulselib.MW_IQmod_pulse('MW pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt2['MW_pulse_mod_risetime'])

    msmt.CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',    
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt2['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt2['CORPSE_pi_mod_frq'],
        amplitude = msmt.params_lt2['CORPSE_amp'],
        rabi_frequency = msmt.params_lt2['CORPSE_rabi_frequency'],
        eff_rotation_angle = 180)

    msmt.CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi2-pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt2['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt2['CORPSE_pi2_mod_frq'],
        amplitude = msmt.params_lt2['CORPSE_pi2_amp'],
        rabi_frequency = msmt.params_lt2['CORPSE_rabi_frequency'],
        eff_rotation_angle = 90)

    ### synchronizing, etc
    msmt.adwin_lt2_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2) #only used for calibrations!!

    ### LDE attempt
    msmt.eom_aom_pulse = pulselib.EOMAOMPulse('Eom Aom Pulse', 
        eom_channel = 'EOM_Matisse',
        aom_channel = 'EOM_AOM_Matisse',
        eom_pulse_duration = msmt.params_lt2['eom_pulse_duration'],
        eom_off_duration = msmt.params_lt2['eom_off_duration'],
        eom_off_amplitude = msmt.params_lt2['eom_off_amplitude'],
        eom_pulse_amplitude = msmt.params_lt2['eom_pulse_amplitude'],
        eom_overshoot_duration1 = msmt.params_lt2['eom_overshoot_duration1'],
        eom_overshoot1 = msmt.params_lt2['eom_overshoot1'],
        eom_overshoot_duration2 = msmt.params_lt2['eom_overshoot_duration2'],
        eom_overshoot2 = msmt.params_lt2['eom_overshoot2'],
        aom_risetime = msmt.params_lt2['aom_risetime'])
    
    msmt.short_eom_aom_pulse = pulselib.short_EOMAOMPulse('Eom Aom Pulse', 
        eom_channel = 'EOM_Matisse',
        aom_channel = 'EOM_AOM_Matisse',
        eom_off_duration = msmt.params_lt2['eom_off_duration'],
        eom_off_amplitude = msmt.params_lt2['eom_off_amplitude'],
        eom_off_2_amplitude  = 2.65, #msmt.params_lt2['eom_off_2_amplitude'],
        eom_overshoot_duration1 = msmt.params_lt2['eom_overshoot_duration1'],
        eom_overshoot1 = 0.0, #msmt.params_lt2['eom_overshoot1'],
        eom_overshoot_duration2 = msmt.params_lt2['eom_overshoot_duration2'],
        eom_overshoot2 = 0.0, #msmt.params_lt2['eom_overshoot2'],
        aom_risetime = msmt.params_lt2['aom_risetime'])    

    msmt.HH_sync = pulse.SquarePulse(channel = 'HH_sync', length = 50e-9, amplitude = 1.0)
    msmt.eom_trigger = pulse.SquarePulse(channel = 'EOM_trigger', length = 100e-9, amplitude = 1.0)
    msmt.SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
    # msmt.yellow_pulse = pulse.SquarePulse(channel = 'AOM_Yellow', amplitude = 1.0)
    msmt.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = 1.0, 
                                    length = msmt.params_lt2['PLU_gate_duration'])
    
    msmt.HH_marker = pulse.SquarePulse(channel = 'HH_MA1', length = 50e-9, amplitude = 1.0)

    ### LDE attempt

    return True

def pulse_defs_lt1(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)

    msmt.TIQ = pulse.SquarePulse(channel='MW_Imod',
        length = 10e-9, amplitude = 0)

    # mw pulses
    msmt.e_pulse = pulselib.MW_IQmod_pulse('MW pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'])

    msmt.fast_pi = pulselib.MW_IQmod_pulse('MW pi pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['fast_pi_mod_frq'],
        amplitude = msmt.params_lt1['fast_pi_amp'],
        length = msmt.params_lt1['fast_pi_duration'])

    msmt.fast_pi2 = pulselib.MW_IQmod_pulse('MW pi2 pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['fast_pi2_mod_frq'],
        amplitude = msmt.params_lt1['fast_pi2_amp'],
        length = msmt.params_lt1['fast_pi2_duration'])

    msmt.slow_pi = pulselib.MW_IQmod_pulse('slow pi',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['selective_pi_mod_frq'],
        amplitude = msmt.params_lt1['selective_pi_amp'],
        length = msmt.params_lt1['selective_pi_duration'])

    msmt.shelving_pulse = pulselib.MW_IQmod_pulse('MBI shelving pulse',
        I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        frequency = msmt.params_lt1['AWG_MBI_MW_pulse_mod_frq'],
        amplitude = msmt.params_lt1['fast_pi_amp'],
        length = msmt.params_lt1['fast_pi_duration'],
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'])
        # CORPSE pi pulse

    msmt.CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime =  msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['CORPSE_pi_mod_frq'],
        amplitude = msmt.params_lt1['CORPSE_pi_amp'],
        length_60 = msmt.params_lt1['CORPSE_pi_60_duration'],
        length_m300 = msmt.params_lt1['CORPSE_pi_m300_duration'],
        length_420 = msmt.params_lt1['CORPSE_pi_420_duration'])

    # CNOT operations on the electron
    msmt.pi2pi_m1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['pi2pi_mIm1_mod_frq'],
        amplitude = msmt.params_lt1['pi2pi_mIm1_amp'],
        length = msmt.params_lt1['pi2pi_mIm1_duration'])

    msmt.pi2pi_0 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=0',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['pi2pi_mI0_mod_frq'],
        amplitude = msmt.params_lt1['pi2pi_mI0_amp'],
        length = msmt.params_lt1['pi2pi_mI0_duration'])

    # rf pulses
    msmt.TN = pulse.SquarePulse(channel='RF',
        length = 100e-9, amplitude = 0)

    msmt.N_pulse = pulselib.RF_erf_envelope(
        channel = 'RF',
        frequency = msmt.params_lt1['N_0-1_splitting_ms-1'])

    msmt.N_pi = pulselib.RF_erf_envelope(
        channel = 'RF',
        frequency = msmt.params_lt1['N_0-1_splitting_ms-1'],
        length = msmt.params_lt1['N_pi_duration'],
        amplitude = msmt.params_lt1['N_pi_amp'])

    msmt.N_pi2 = pulselib.RF_erf_envelope(
        channel = 'RF',
        frequency = msmt.params_lt1['N_0-1_splitting_ms-1'],
        length = msmt.params_lt1['N_pi2_duration'],
        amplitude = msmt.params_lt1['N_pi2_amp'])


    ### synchronizing, etc
    msmt.adwin_lt1_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 10e-6, amplitude = 2)

    msmt.adwin_lt1_trigger_pulse_mbi = pulse.SquarePulse(channel = 'adwin_sync',
        length = 17e-6, amplitude = 2) 
        # mbi pulse trigger should be longer, because it needs to receive a jump from the ADwin while still going. 
        # it also needs to be short enough such that it is finished when the ADWin triggers the next element
        
    msmt.AWG_LT2_trigger_pulse = pulse.SquarePulse(channel='AWG_LT2_trigger',
        length = 10e-9, amplitude = 2)

    msmt.HH_sync = pulse.SquarePulse(channel = 'HH_sync', length = 50e-9, amplitude = 1.0)

    # light
    msmt.SP_pulse = pulse.SquarePulse(channel = 'Velocity1AOM', amplitude = 1.0)
    msmt.yellow_pulse = pulse.SquarePulse(channel = 'YellowAOM', amplitude = 1.0 )


#************************ Sequence elements LT1   ******************************

#this is used to couple to phases of two different-frequency pulses
def phaseref(frequency, time, offset=0):
    return ((frequency*time + offset/360.) % 1) * 360.

def _lt1_mbi_element(msmt):
    """
    this generates the MBI element, with the (slow) CNOT pulse and adwin trigger
    """
    e = element.Element('MBI CNOT', pulsar=msmt.pulsar_lt1)
    e.append(pulse.cp(msmt.T,
        length = 10e-9))
    e.append(msmt.slow_pi)
    e.append(msmt.adwin_lt1_trigger_pulse_mbi)

    return e

def _lt1_N_polarization_decision_element(msmt):
    """
    This is just an empty element that needs to be long enough for the
    adwin to decide whether we need to do CR (then it times out) or
    jump to the LDE sequence.
    """

    e = element.Element('N_pol_decision', pulsar = msmt.pulsar_lt1)
    e.append(pulse.cp(msmt.T, length=10e-6))

    return e

def _lt1_N_pol_element(msmt):
    """
    This is the element we will run to polarize the nuclear spin after each CR
    checking.
    """
    e = element.Element('N_pol', pulsar = msmt.pulsar_lt1)

    # TODO not yet implemented
    e.append(pulse.cp(msmt.T, length=1e-6))

    return e

def _lt1_start_LDE_element(msmt):
    """
    This element triggers the LDE sequence on LT2.
    """
    e = element.Element('start_LDE', pulsar = msmt.pulsar_lt1)
    e.append(pulse.cp(msmt.AWG_LT2_trigger_pulse, 
        length = 1e-6,
        amplitude = 0))
    e.append(msmt.AWG_LT2_trigger_pulse)

    return e

def _lt1_LDE_element(msmt):
    """
    This element contains the LDE part for LT1, i.e., spin pumping and MW pulses
    for the LT1 NV in the real experiment.
    """
    e = element.Element('LDE_LT1', pulsar = msmt.pulsar_lt1, global_time = True)

    # this pulse to ensure that the element has equal length as the lt2 element
    e.add(pulse.cp(msmt.SP_pulse,
            amplitude = 0,
            length = msmt.params['LDE_element_length']))
    #
    #1 SP
    e.add(pulse.cp(msmt.SP_pulse,
                amplitude = 0, 
                length = msmt.params_lt1['initial_delay']), 
            name = 'initial_delay')
    
    e.add(pulse.cp(msmt.SP_pulse, 
                length = msmt.params['LDE_SP_duration'], 
                amplitude = 1.0),
            name = 'spinpumping',
            refpulse = 'initial_delay')

    e.add(pulse.cp(msmt.yellow_pulse, 
                length = msmt.params['LDE_SP_duration_yellow'], 
                amplitude = 1. if msmt.params_lt1['AWG_yellow_use']  else 0.), 
            name = 'spinpumpingyellow', 
            refpulse = 'initial_delay')

    #2 MW pi/2
    if msmt.params_lt1['MW_during_LDE'] == 1:
        e.add(msmt.fast_pi2, name = 'mw_pi2_pulse', 
                start = msmt.params_lt1['MW_wait_after_SP'],
                refpulse = 'spinpumping', refpoint = 'end', refpoint_new = 'start')

    #3 MW pi
    if msmt.params_lt1['MW_during_LDE'] == 1:
        e.add(msmt.fast_pi, name = 'mw_pi_pulse',
                start = msmt.params_lt1['MW_separation'],
                refpulse = 'mw_pi2_pulse', refpoint = 'end', refpoint_new = 'start')
        
    ################
    
    if e.length() != msmt.params['LDE_element_length']:
        raise Exception('LDE element length' + e.name+' is not as specified - granularity issue?')
    return e

def _lt1_adwin_LT1_trigger_element(msmt):
    """
    sends a trigger to Adwin LT1 to notify we go back to CR.
    """
    e = element.Element('adwin_LT1_trigger', pulsar = msmt.pulsar_lt1)
    e.append(msmt.adwin_lt1_trigger_pulse)
    return e

def _lt1_dummy_element(msmt):
    """
    This is a dummy element. It contains nothing. 
    It replaces the LDE element if we do not want to do LDE.
    """
    e = element.Element('dummy', pulsar = msmt.pulsar_lt1, global_time = True)
    
    e.append(pulse.cp(msmt.T, length=10e-6))

    return e

def _lt1_N_RO_elt(msmt):
    """
    This is an element with spin pumping to ms=0 and a (pi-2pi) CNOT pulse for the nitrogen readout.
    """
    N_RO_elt = element.Element('N-RO', pulsar=msmt.pulsar_lt1)
    N_RO_elt.append(pulse.cp(msmt.T,
                              length=1000e-9))    
    N_RO_elt.append(pulse.cp(msmt.SP_pulse,
                             length = msmt.params_lt1['N_RO_SP_duration']))
    N_RO_elt.append(pulse.cp(msmt.T,
                             length=2000e-9))
    N_RO_elt.append(msmt.pi2pi_m1)

    return N_RO_elt

def _lt1_wait_1us_elt(msmt):
    wait_1us_elt = element.Element('1us_delay', pulsar=msmt.pulsar_lt1)
    wait_1us_elt.append(pulse.cp(msmt.T, length=1e-6))

    return wait_1us_elt


##################
##### UNROT basis element 
##################
def _lt1_UNROT_element(msmt, name,
    N_pulse, evolution_time, time_offset, **kw):
    """
    creates an unconditional operation:
    start at some zero-time, add the operation, and fill up
    with waiting time according to the specified
    'evolution_time' (measure to/from the center of the pi pulse).
    Then do a CORPSE pi pulse, and repeat the operation. fill up time
    after again such that the to evolution times are the same.
    
    for correct rotating frames we need a time offset. 
    electron pulse phase will be computed accordingly.
    For the N phase to match, we'll insert waiting time.
    """

    #include the possibility to do only one Nitrogen pulse (no CORPSE or 2nd):
    first_N_pulse_only = kw.pop('first_N_pulse_only', False)
    #include the possibility to do no second Nitrogen pulse (only 1st and CORPSE):
    no_second_N_pulse = kw.pop('no_second_N_pulse', False)

    # to make sure that the zero-time of the element
    # is zero-time on the IQ channels (and not of the N pulse due to delays).
    # So it should be longer than the maximum difference between channel delays of all channels with pulses
    start_buffer = kw.pop('start_buffer', 200e-9)

    # verbosity: if verbose, print info about all phases and lengths
    verbose = kw.pop('verbose', False)

    CORPSE_pi_phase_shift = kw.pop('CORPSE_pi_phase_shift',
        msmt.params_lt1['CORPSE_pi_phase_shift'])

    # optionally add time at the beginning, (for the N init to start at the spin echo)
    begin_offset_time = kw.pop('begin_offset_time', 0)

    # optionally add/omit time at the end, which might facilitate
    # timing calculations for the next element. for the start this
    # is not required, on one side we just use the evolution time.
    end_offset_time = kw.pop('end_offset_time', 0)

    # the shiny new element
    elt = element.Element(name, pulsar=msmt.pulsar_lt1,
        global_time = True, time_offset = time_offset)
    
    delay1_name = elt.append(pulse.cp(msmt.TIQ, 
        length = begin_offset_time + evolution_time))
    
    if N_pulse != None:
        
        # support for lists of pulses -- we need this for the H gate
        if type(N_pulse) != list:
                        
            op1_name = elt.add(N_pulse, start=start_buffer)

        else:
            for i,op in enumerate(N_pulse):
                if i == 0:
                    start = start_buffer
                else:
                    start += N_pulse[i-1].length

                n = elt.add(op, start = start)

                if i == 0:
                    first_op_name = n
    
    if first_N_pulse_only == True:
        elt.add(msmt.TIQ)

    else:

        # the CORPSE pi-pulse
        delta_t_CORPSE = - msmt.CORPSE_pi.effective_length()/2. + \
        msmt.params_lt1['CORPSE_pi_center_shift']
    
        # want to have the CORPSE phase as a shift with respect to the current
        # rotating frame phase.
        CORPSE_phase = phaseref(msmt.params_lt1['e_ref_frq'],
            elt.pulse_global_end_time(delay1_name, msmt.TIQ.channel) + delta_t_CORPSE) \
            + CORPSE_pi_phase_shift

        pi_name = elt.add(pulse.cp(msmt.CORPSE_pi,
            phaselock = False,
            phase = CORPSE_phase),
            start = delta_t_CORPSE,
            refpulse = delay1_name)

        if no_second_N_pulse == True:
            elt.add(msmt.TIQ)
        else:
            # second part of the evolution starts at the measured center of the
            # pi pulse. (note that delta_t_CORPSE is negative)
            delta_t_delay2 = msmt.CORPSE_pi.effective_length() + delta_t_CORPSE
            elt.add(pulse.cp(msmt.TIQ, 
                length = evolution_time + end_offset_time),
                start = -delta_t_delay2,
                refpulse = pi_name)

            if N_pulse != None:
                # second Nitrogen operation; start at evolution time
                # after the start of the first. We add half of the corpse pulse length to make 
                # sure it doies not overlap with the corpse.
        
                if type(N_pulse) != list:
            
                    t_op2 = evolution_time + msmt.CORPSE_pi.effective_length()/2.
            
                    # op2_phase = op1_phase + phaseref(N_pulse.frequency, t_op2)

                    elt.add(N_pulse,
                        start = t_op2,
                        refpulse = op1_name,
                        refpoint = 'start')
                else:
                    for i,op in enumerate(N_pulse):
                        if i == 0:
                            t_op = evolution_time + \
                                msmt.CORPSE_pi.effective_length()/2.
                        else:
                            t_op += N_pulse[i-1].length

                        elt.add(op,
                            start = t_op,
                            refpulse = first_op_name,
                            refpoint = 'start')
    return elt

##################
##### Nitrogen initialization element
##################
def _lt1_N_init_element(msmt, name, basis = 'Y', **kw):
    echo_time_after_LDE = kw.pop('echo_time_after_LDE', msmt.params_lt1['echo_time_after_LDE'])
    end_offset_time = kw.pop('end_offset_time',-msmt.params_lt1['buffer_time_for_CNOT'])
    #end_offset time: to compensate for CNOT time in next element 

    if basis == '-Z':
        N_pulse = pulse.cp(msmt.TN) # waiting time only -> change as little as possible
    
    elif basis == 'Y':
        N_pulse = pulse.cp(msmt.N_pi2, 
            phase = 90) #pulse along x onto y (starting in -z)
    
    elif basis == 'X':
        N_pulse = pulse.cp(msmt.N_pi2, 
            phase = 180) #pulse along -y onto x (starting in -z)
    
    elif basis == 'Z':
        N_pulse = pulse.cp(msmt.N_pi) #pulse onto z (starting in -z)
    
    elif basis == '-Y':
        N_pulse = pulse.cp(msmt.N_pi2, 
            phase = -90)
    
    elif basis == '-X':
        N_pulse = pulse.cp(msmt.N_pi2, 
            phase = 0)

    else :
        raise Exception('Basis state not recognised')
                            
    UNROT_N_init_elt = _lt1_UNROT_element(msmt, name,
        N_pulse, 
        evolution_time = msmt.params_lt1['pi2_evolution_time'], 
        time_offset = msmt.params['LDE_element_length'], 
        begin_offset_time = echo_time_after_LDE,
        end_offset_time = end_offset_time)
        
    return UNROT_N_init_elt

##################
##### BSM elements (CNOT + UNROT with Hadamard)
##################
def _lt1_BSM_elements(msmt, name, time_offset, **kw):
    CNOT_phase_shift = kw.pop('CNOT_phase_shift', 0)
    evo_time = kw.pop('evolution_time', msmt.params_lt1['H_evolution_time'])
    H_phase = kw.pop('H_phase', 0)

    start_buffer_time = msmt.params_lt1['buffer_time_for_CNOT']
    evo_offset = 1000e-9
    
    eff_evo_time = evo_time - evo_offset

    # we make the evolution time a bit shorter ( evo_offset = 1000 ns), 
    # then make an extra
    # element of length start_buffer_time plus this offset.
    # in this element we put the CNOT pulse such that it's centered
    # at the start of the effective evolution time (end - 1000 ns).
    CNOT_elt = element.Element('{}_BSM-CNOT'.format(name), 
        pulsar = msmt.pulsar_lt1,
        global_time = True,
        time_offset = time_offset)

    t_CNOT = start_buffer_time - msmt.pi2pi_m1.effective_length()/2.
    
    CNOT_elt.append(pulse.cp(msmt.TIQ, 
        length = t_CNOT))
    CNOT_elt.append(pulse.cp(msmt.pi2pi_m1,
        phase = CNOT_phase_shift))
    CNOT_elt.append(pulse.cp(msmt.TIQ,
        length = evo_offset - msmt.pi2pi_m1.effective_length()/2.))

   
    #do the BSM with just a pi/2 along the y axis.
    H_pulses = [ pulse.cp(msmt.N_pi2, phase=H_phase) ]#,
    #    pulse.cp(msmt.N_pi, phase= H_phase+90.) ]

    UNROT_elt = _lt1_UNROT_element(msmt, '{}_BSM-UNROT-H'.format(name),
        H_pulses, eff_evo_time, time_offset+CNOT_elt.length(), **kw)

    return CNOT_elt, UNROT_elt

def _lt1_N_init_and_BSM_for_teleportation(msmt):
    N_init_elt = _lt1_N_init_element(msmt, 
        name ='N_init', 
        basis = msmt.params['source_state_basis'])
    BSM_elts = _lt1_BSM_elements(msmt, 
        name = 'Teleportation', 
        time_offset = msmt.params['LDE_element_length'] + N_init_elt.length())

    return N_init_elt, BSM_elts[0], BSM_elts[1]



#************************ Sequence elements LT2   ******************************

#### single elements
def _lt2_sequence_finished_element(msmt):
    """
    last element of a two-setup sequence. Sends a trigger to ADwin LT2.
    """
    e = element.Element('LT2_finished', pulsar = qt.pulsar)
    e.append(msmt.adwin_lt2_trigger_pulse)
    return e

def _lt2_dummy_element(msmt):
    """
    A 1us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('Dummy', pulsar = qt.pulsar)
    e.append(pulse.cp(msmt.T, length=10e-6))
    return e

def _lt2_wait_1us_element(msmt):
    """
    A 1us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('wait_1_us', 
        pulsar = qt.pulsar)
    e.append(pulse.cp(msmt.T, length=1e-6))
    return e

def _lt2_LDE_element(msmt, **kw):
    """
    This element contains the LDE part for LT2, i.e., spin pumping and MW pulses
    for the LT2 NV and the optical pi pulses as well as all the markers for HH and PLU.
    """

    # variable parameters
    name = kw.pop('name', 'LDE_LT2')
    pi2_pulse_phase = kw.pop('pi2_pulse_phase', 0)
    if kw.pop('use_short_eom_pulse',False):
        eom_pulse=pulse.cp(msmt.short_eom_aom_pulse,
            aom_on=msmt.params_lt2['eom_aom_on'])
    else:
        eom_pulse=pulse.cp(msmt.eom_aom_pulse,
            eom_pulse_amplitude = msmt.params_lt2['eom_pulse_amplitude'],
            aom_on=msmt.params_lt2['eom_aom_on'])

    ###
    e = element.Element(name, 
        pulsar = qt.pulsar, 
        global_time = True)
    e.add(pulse.cp(msmt.SP_pulse,
            amplitude = 0,
            length = msmt.params['LDE_element_length']))

    #1 SP
    e.add(pulse.cp(msmt.SP_pulse, 
            amplitude = 0, 
            length = msmt.params_lt2['initial_delay']), 
        name = 'initial delay')
    
    e.add(pulse.cp(msmt.SP_pulse, 
            length = msmt.params['LDE_SP_duration'], 
            amplitude = 1.0), 
        name = 'spinpumping', 
        refpulse = 'initial delay')

    # e.add(pulse.cp(msmt.yellow_pulse, 
    #         length = msmt.params['LDE_SP_duration_yellow'], 
    #         amplitude = 1.0), 
    #     name = 'spinpumpingyellow', 
    #     refpulse = 'initial delay')

    
    for i in range(msmt.params['opt_pi_pulses']):
        name = 'opt pi {}'.format(i+1)
        refpulse = 'opt pi {}'.format(i) if i > 0 else 'spinpumping'
        start = msmt.params_lt2['opt_pulse_separation'] if i > 0 else msmt.params['wait_after_sp']
        refpoint = 'start' if i > 0 else 'end'

        e.add(eom_pulse,        
            name = name, 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)
        e.add(msmt.eom_trigger,
            name = name+'_trigger', 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)
    #4 MW pi/2
    if msmt.params_lt2['MW_during_LDE'] == 1 :
        e.add(pulse.cp(msmt.CORPSE_pi2, 
            phase = pi2_pulse_phase), 
            start = -msmt.params_lt2['MW_opt_puls1_separation'],
            refpulse = 'opt pi 1', 
            refpoint = 'start', 
            refpoint_new = 'end')
    #5 HHsync
    syncpulse_name = e.add(msmt.HH_sync, refpulse = 'opt pi 1', refpoint = 'start', refpoint_new = 'end')
    
    #6 plugate 1
    e.add(msmt.plu_gate, name = 'plu gate 1', 
        refpulse = 'opt pi 1',
        start = msmt.params_lt2['PLU_1_delay'])

    #8 MW pi
    if msmt.params_lt2['MW_during_LDE'] == 1:
        e.add(msmt.CORPSE_pi, 
            start = - msmt.params_lt2['MW_opt_puls2_separation'],
            refpulse = 'opt pi 2', 
            refpoint = 'start', 
            refpoint_new = 'end')
    
    #10 plugate 2
    e.add(msmt.plu_gate, 
        name = 'plu gate 2',
        refpulse = 'opt pi {}'.format(msmt.params['opt_pi_pulses']),
        start = msmt.params_lt2['PLU_2_delay']) 

    #11 plugate 3
    e.add(pulse.cp(msmt.plu_gate, 
            length = msmt.params_lt2['PLU_gate_3_duration']), 
        name = 'plu gate 3', 
        start = msmt.params_lt2['PLU_3_delay'], 
        refpulse = 'plu gate 2')
    
    #12 plugate 4
    e.add(msmt.plu_gate, name = 'plu gate 4', start = msmt.params_lt2['PLU_4_delay'],
            refpulse = 'plu gate 3')

    ############

    if e.length() != msmt.params['LDE_element_length']:
        raise Exception('LDE element length'+e.name+' is not as specified - granylarity issue?')
    return e

    return e


def _lt2_adwin_lt2_trigger_elt(msmt): #only used in calibration
    sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
    sync_elt.append(msmt.adwin_lt2_trigger_pulse)

    return sync_elt

def _lt2_first_pi2(msmt, **kw):
    init_ms1 = kw.pop('init_ms1', False)
    # around each pulse I make an element with length 1600e-9; 
    # the centre of the pulse is in the centre of the element.
    # this helps me to introduce the right waiting times, counting from centre of the pulses
    CORPSE_pi2_wait_length = msmt.params_lt2['CORPSE_pi2_wait_length'] #- (msmt.CORPSE_pi2.length - 2*msmt.params_lt2['MW_pulse_mod_risetime'])/2 

    first_pi2_elt = element.Element('first_pi2_elt', pulsar= qt.pulsar, 
        global_time = True, time_offset = 0.)

    first_pi2_elt.append(pulse.cp(msmt.T, length = 100e-9))
    
    if init_ms1:
        first_pi2_elt.append(pulse.cp(msmt.CORPSE_pi))
        first_pi2_elt.append(pulse.cp(msmt.T, length = 100e-9))
    
    first_pi2_elt.append(pulse.cp(msmt.CORPSE_pi2))
    first_pi2_elt.append(pulse.cp(msmt.T, 
        length =  CORPSE_pi2_wait_length))

    return first_pi2_elt

def _lt2_final_pi2(msmt, name, time_offset, **kw):
    extra_t_before_pi2 = kw.pop('extra_t_before_pi2', 0)
    CORPSE_pi2_phase = kw.pop('CORPSE_pi2_phase', 0)

    # around each pulse I make an element with length 1600e-9; 
    # the centre of the pulse is in the centre of the element.
    # this helps me to introduce the right waiting times, counting from centre of the pulses
    CORPSE_pi2_wait_length = msmt.params_lt2['CORPSE_pi2_wait_length'] #- (msmt.CORPSE_pi2.length - 2*msmt.params_lt2['MW_pulse_mod_risetime'])/2 

    second_pi2_elt = element.Element('second_pi2_elt-{}'.format(name), pulsar= qt.pulsar, 
        global_time = True, time_offset = time_offset)
    second_pi2_elt.append(pulse.cp(msmt.T, 
        length = CORPSE_pi2_wait_length + extra_t_before_pi2))
    second_pi2_elt.append(pulse.cp(msmt.CORPSE_pi2, 
        phase = CORPSE_pi2_phase))
    second_pi2_elt.append(pulse.cp(msmt.T, length =  100e-9 ))           

    return second_pi2_elt

def _lt2_final_pi(msmt, name, time_offset, **kw):
    extra_t_before_pi = kw.pop('extra_t_before_pi', 0)
    CORPSE_pi_phase = kw.pop('CORPSE_pi_phase', 0)
    # around each pulse I make an element with length 1600e-9; 
    # the centre of the pulse is in the centre of the element.
    # this helps me to introduce the right waiting times, counting from centre of the pulses
    CORPSE_pi_wait_length = msmt.params_lt2['CORPSE_pi2_wait_length']  #- (msmt.CORPSE_pi2.length - 2*msmt.params_lt2['MW_pulse_mod_risetime'])/2 

    final_pi_elt = element.Element('second_pi_elt-{}'.format(name), pulsar= qt.pulsar, 
        global_time = True, time_offset = time_offset)
    final_pi_elt.append(pulse.cp(msmt.T, 
        length = CORPSE_pi_wait_length + extra_t_before_pi))
    final_pi_elt.append(pulse.cp(msmt.CORPSE_pi, 
        phase = CORPSE_pi_phase))
    final_pi_elt.append(pulse.cp(msmt.T, length =  100e-9 ))           

    return final_pi_elt

def _lt2_final_id(msmt, name, time_offset, **kw):
    wait_length = msmt.params_lt2['CORPSE_pi2_wait_length'] + msmt.CORPSE_pi.length 
    final_id_elt = element.Element('second_id_elt-{}'.format(name), pulsar= qt.pulsar, 
                global_time = True, time_offset = time_offset)
    final_id_elt.append(pulse.cp(msmt.T, length =  wait_length)) 
    final_id_elt.append(pulse.cp(msmt.T, length =  100e-9 )) 

    return final_id_elt


#### dynamical decoupling element for adding to sequences
### SEE Z:\Projects\Teleportation\Data\2013-10-15 SIL 10_LT2_SSRO_DD.ppt for some schematics 
### on the various waiting times used here 
def _lt2_dynamical_decoupling(msmt, seq, time_offset, **kw):
    free_evolution_time = kw.pop('free_evolution_time', msmt.params_lt2['first_C_revival'])
    extra_t_between_pulses = kw.pop('extra_t_between_pulses', msmt.params_lt2['dd_extra_t_between_pi_pulses'])
    begin_offset_time = kw.pop('begin_offset_time', msmt.params_lt2['dd_spin_echo_time'])
    name = kw.pop('name', 'DD')
    use_delay_reps=kw.pop('use_delay_reps', True)
    
    CORPSE_pi2_wait_length = msmt.params_lt2['CORPSE_pi2_wait_length']
    # around each pulse I make an element with length 1600e-9; 
    # the centre of the pulse is in the centre of the element.
    # this helps me to introduce the right waiting times, counting from centre of the pulses
    CORPSE_pi_wait_length = 800e-9 - (msmt.CORPSE_pi.length)/2
    reduced_free_ev_time = free_evolution_time - 800e-9 - 800e-9      

    elts = []  

    if use_delay_reps:
        # calculate how many waits of 1 us fit in the free evolution time (-1 repetition)
        delay_reps = np.floor(reduced_free_ev_time/1e-6) - 2
        #calculate how much wait time should be added to the above to fill the full free evolution time (+1 us to fill full elt)
        rest_time = np.mod(reduced_free_ev_time,1e-6) + 2e-6

        wait_1us = _lt2_wait_1us_element(msmt)
        elts.append(wait_1us)

    else:
        rest_time = reduced_free_ev_time
           
    wait_rest_elt = element.Element('wait_rest_elt-{}'.format(name), pulsar=qt.pulsar,
        global_time = True)
    wait_rest_elt.append(pulse.cp(msmt.T, length = rest_time))
    elts.append(wait_rest_elt)     
    
    total_time=0.

    for j,DD_pi_phase in enumerate(msmt.params_lt2['DD_pi_phases']):
        
        ### WAIT
        cur_name = name if j==0 else 'wait1-{}-{}'.format(name,j)
        if use_delay_reps:
            seq.append(name = cur_name, 
                wfname = wait_1us.name, 
                repetitions = delay_reps)
            total_time += wait_1us.length()*delay_reps
            cur_name = 'wait_rest1-{}-{}'.format(name,j)
        seq.append(name= cur_name,
            wfname = wait_rest_elt.name)
        total_time += wait_rest_elt.length()

        time_offset_CORPSE = time_offset + total_time
        CORPSE_elt = element.Element('CORPSE_elt-{}-{}'.format(name,j), pulsar= qt.pulsar, 
            global_time = True, time_offset = time_offset_CORPSE)
        ###

        ### PI
        # append a longer waiting time for the not first CORPSE pulse, to get the right evolution time
        if j == 0:
            CORPSE_elt.append(pulse.cp(msmt.T, 
                length = CORPSE_pi_wait_length + begin_offset_time))
        else:
            # add an extra 2*CORPSE_pi2_wait_length, that would otherwise be in the free_ev_time
            # also add the possibility to make the time between pi pulses different,
            # this could correct for where the centre of the pi/2 pulse is.
            CORPSE_elt.append(pulse.cp(msmt.T, 
                length = CORPSE_pi_wait_length + 2.*CORPSE_pi2_wait_length + extra_t_between_pulses ))
        CORPSE_elt.append(pulse.cp(msmt.CORPSE_pi, 
            phase = DD_pi_phase))
        CORPSE_elt.append(pulse.cp(msmt.T, 
            length = CORPSE_pi_wait_length ))
        elts.append(CORPSE_elt)
        ### 

        ### WAIT
        seq.append(name = CORPSE_elt.name+'-{}-{}'.format(name,j), 
            wfname = CORPSE_elt.name)
        total_time += CORPSE_elt.length()
        if use_delay_reps:
            seq.append(name = 'wait2-{}-{}'.format(name,j), 
                wfname = wait_1us.name, 
                repetitions = delay_reps)
            total_time += wait_1us.length()*delay_reps
        seq.append(name= 'wait_rest2-{}-{}'.format(name,j),
            wfname = wait_rest_elt.name)
        total_time += wait_rest_elt.length()
        ###

    return seq, total_time, elts

