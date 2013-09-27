from measurement.lib.pulsar import pulse, pulselib, element, pulsar

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

    # CORPSE pulses
    msmt.CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',    
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt2['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt2['CORPSE_pi_mod_frq'],
        amplitude = msmt.params_lt2['CORPSE_pi_amp'],
        length_60 = msmt.params_lt2['CORPSE_pi_60_duration'],
        length_m300 = msmt.params_lt2['CORPSE_pi_m300_duration'],
        length_420 = msmt.params_lt2['CORPSE_pi_420_duration'])    

    msmt.CORPSE_pi2 = pulselib.IQ_CORPSE_pi2_pulse('CORPSE pi2-pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt2['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt2['CORPSE_pi2_mod_frq'],
        amplitude = msmt.params_lt2['CORPSE_pi2_amp'],
        length_24p3 = msmt.params_lt2['CORPSE_pi2_24p3_duration'],
        length_m318p6 = msmt.params_lt2['CORPSE_pi2_m318p6_duration'],
        length_384p3 = msmt.params_lt2['CORPSE_pi2_384p3_duration'])

    ### synchronizing, etc
    msmt.adwin_lt2_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2)


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

    msmt.HH_sync = pulse.SquarePulse(channel = 'HH_sync', length = 50e-9, amplitude = 1.0)
    msmt.SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
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
        length = 5e-6, amplitude = 2)

    msmt.AWG_LT2_trigger_pulse = pulse.SquarePulse(channel='AWG_LT2_trigger',
        length = 10e-9, amplitude = 2)

    msmt.HH_sync = pulse.SquarePulse(channel = 'HH_sync', length = 50e-9, amplitude = 1.0)

    # light
    msmt.SP_pulse = pulse.SquarePulse(channel = 'Velocity1AOM', amplitude = 1.0)
    msmt.yellow_pulse = pulse.SquarePulse(channel = 'YellowAOM', amplitude = 1.0)

#************************ Sequence elements LT1   ******************************

def _lt1_mbi_element(msmt):
    """
    this generates the MBI element, with the (slow) CNOT pulse and adwin trigger
    """
    e = element.Element('MBI CNOT', pulsar=msmt.pulsar_lt1)
    e.append(pulse.cp(msmt.T,
        length = 10e-9))
    e.append(msmt.slow_pi)
    e.append(msmt.adwin_lt1_trigger_pulse)

    return e

def _lt1_N_polarization_decision_element(msmt):
    """
    This is just an empty element that needs to be long enough for the
    adwin to decide whether we need to do CR (then it times out) or
    jump to the LDE sequence.
    """

    e = element.Element('N_pol_decision', pulsar = msmt.pulsar_lt1)
    e.append(pulse.cp(msmnt.T, length=10e-6))

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


    #2 MW pi/2
    if msmt.params['MW_during_LDE'] == 1:
        e.add(msmt.fast_pi2, name = 'mw_pi2_pulse', 
                start = msmt.params_lt1['MW_wait_after_SP'],
                refpulse = 'spinpumping', refpoint = 'end', refpoint_new = 'start')

    #3 MW pi
    if msmt.params['MW_during_LDE'] == 1:
        e.add(msmt.fast_pi, name = 'mw_pi_pulse',
                start = msmt.params_lt1['MW_separation'],
                refpulse = 'mw_pi2_pulse', refpoint = 'end', refpoint_new = 'start')
        
    # e.add(pulse.cp(msmnt.TIQ, duration = msmnt.params_lt1['finaldelay']))
    
    # need some waiting pulse on IQ here to be certain to operate on spin echo after

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
    
    e.append(pulse.cp(msmt.T, length=1e-6))

    return e


def _lt1_N_RO_CNOT_elt(msmt):
    """
    This is an element with the (pi-2pi) CNOT pulse for the nitrogen readout.
    """
    N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=msmt.pulsar_lt1)
    N_RO_CNOT_elt.append(pulse.cp(msmt.T,
        length=100e-9))
    N_RO_CNOT_elt.append(msmt.pi2pi_m1)

    return N_RO_CNOT_elt

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
    # is zero-time on the IQ channels (and not of the N pulse due to delays)
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
    
    delay0_name = elt.append(pulse.cp(msmt.TIQ,
        length = begin_offset_time))
    delay1_name = elt.append(pulse.cp(msmt.TIQ, 
        length = evolution_time))
    
    if N_pulse != None:
        
        # support for lists of pulses -- we need this for the H gate
        if type(N_pulse) != list:
            
            # first N operation, with adapted phase
            # the resulting time of the pulse within the element
            
            # eff_t_op1 = start_buffer - elt.channel_delay('RF') + \
            #    elt.channel_delay('MW_Imod')
            
            # op1_phase = (N_ref_phase + N_pulse.phase + \
            #     phaseref(N_pulse.frequency, eff_t_op1) )        
            
            op1_name = elt.add(N_pulse, start=start_buffer)

            # if verbose:
            #     print 'Phase of the first NROT:', op1_phase

        else:
            for i,op in enumerate(N_pulse):
                if i == 0:
                    # eff_t_op = start_buffer - elt.channel_delay('RF') + \
                    #     elt.channel_delay('MW_Imod')
                    start = start_buffer
                else:
                    # eff_t_op += N_pulse[i-1].length
                    start += N_pulse[i-1].length

                # op_phase = (N_ref_phase + op.phase + \
                #     phaseref(op.frequency, eff_t_op))
                n = elt.add(op, start = start)

                if i == 0:
                    # first_op_phase = op_phase
                    first_op_name = n
    
    if first_N_pulse_only == True:
        elt.add(msmt.TIQ)

    else:

        # the CORPSE pi-pulse
        delta_t_CORPSE = - msmt.CORPSE_pi.effective_length()/2. + \
        msmt.params_lt1['CORPSE_pi_center_shift']
    
        # t_CORPSE = evolution_time + delta_t_CORPSE
        # CORPSE_phase = e_ref_phase + phaseref(
        #     msmt.params_lt1['e_ref_frq'], t_CORPSE) + \
        #     CORPSE_pi_phase_shift

        # want to have the CORPSE phase as a shift with respect to the current
        # rotating frame phase.
        CORPSE_phase = phaseref(msmt.params_lt1['e_ref_frq'],
            elt.pulse_global_end_time(delay1_name, 'MW_Imod') + delta_t_CORPSE) \
            + CORPSE_pi_phase_shift

        # if verbose:
        #     print 'Start time of the CORPSE:', t_CORPSE
        #     print 'Phase of the CORPSE:', CORPSE_phase

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
                # after the start of the first.
        
                if type(N_pulse) != list:
            
                    t_op2 = evolution_time + msmt.CORPSE_pi.effective_length()/2.
            
                    # op2_phase = op1_phase + phaseref(N_pulse.frequency, t_op2)

                    elt.add(N_pulse,
                        start = t_op2,
                        refpulse = op1_name,
                        refpoint = 'start')

                    # if verbose:
                    #     print 'Phase of the second NROT:', op2_phase

                else:
                    for i,op in enumerate(N_pulse):
                        if i == 0:
                            t_op = evolution_time + \
                                msmt.CORPSE_pi.effective_length()/2.
                        else:
                            t_op += N_pulse[i-1].length

                        # op_phase = first_op_phase + \
                        #     phaseref(op.frequency, t_op)
                
                        elt.add(op,
                            start = t_op,
                            refpulse = first_op_name,
                            refpoint = 'start')
    return elt

##################
##### Nitrogen initialization element
##################
def _lt1_N_init_element(msmt, name, basis = 'X', **kw):
    echo_time_after_LDE = kw.pop('echo_time_after_LDE', msmt.params_lt1['echo_time_after_LDE'])
    end_offset_time = kw.pop('end_offset_time', -240e-9)

    if basis == 'Z':
        N_pulse = pulse.cp(msmt.TN) # waiting time only -> change as little as possible
    elif basis == 'X':
        N_pulse = pulse.cp(msmt.N_pi2, 
            phase = 0) #pulse along y onto x
    elif basis == 'Y':
        N_pulse = pulse.cp(msmt.N_pi2, 
            phase = -90) #pulse along -x onto y
    elif basis == '-Z':
        N_pulse = pulse.cp(msmt.N_pi) #pulse onto -z
                            
    UNROT_N_init_elt = _lt1_UNROT_element(msmt, 'N_init_element',
        N_pulse, 
        msmt.params_lt1['pi2_evolution_time'], 
        _lt1_LDE_element.length(), 
        begin_offset_time = echo_time_after_LDE,
        end_offset_time = end_offset_time)
        #end_offset time: to compensate for CNOT time in next element 

    return UNROT_N_init_elt

##################
##### BSM elements (CNOT + UNROT with Hadamard)
##################
def _lt1_BSM_elements(msmt, name, time_offset, 
    start_buffer_time=240e-9, **kw):
    """
    Attention: Make sure that the CNOT element time adds up to a length
    that is a multiple of the granularity!
    """

    evo_offset = kw.pop('evo_offset', 1000e-9)
    CNOT_offset = kw.pop('CNOT_offset', 0)
    CNOT_phase_shift = kw.pop('CNOT_phase_shift', 0)
    evo_time = kw.pop('evolution_time', msmt.params_lt1['H_evolution_time'])
    H_phase = kw.pop('H_phase', 0)
    BSM_CNOT_amp = kw.pop('BSM_CNOT_amp', msmt.params_lt1['pi2pi_mIm1_amp'])
    # N_frq = kw.pop('N_frq', msmt.N_pi2.frequency)
    
    eff_evo_time = evo_time - evo_offset

    # we make the evolution time a bit shorter (default 1000 ns), 
    # then make an extra
    # element of length start_buffer_time plus this offset.
    # in this element we put the CNOT pulse such that it's centered
    # at the start of the effective evolution time (end - 1000 ns).
    CNOT_elt = element.Element('{}_BSM-CNOT'.format(name), 
        pulsar = msmt.pulsar_lt1,
        global_time = True,
        time_offset = time_offset)

    t_CNOT = start_buffer_time - msmt.pi2pi_m1.effective_length()/2. + \
        CNOT_offset
    
    # phi_CNOT = phaseref(msmt.pi2pi_m1.frequency,
    #     t_CNOT) + e_ref_phase + CNOT_phase_shift

    CNOT_elt.append(pulse.cp(msmt.TIQ, 
        length = t_CNOT))
    CNOT_elt.append(pulse.cp(msmt.pi2pi_m1,
        phase = CNOT_phase_shift,
        amplitude = BSM_CNOT_amp))
    CNOT_elt.append(pulse.cp(msmt.TIQ,
        length = evo_offset + start_buffer_time - \
            msmt.pi2pi_m1.effective_length() - t_CNOT))

    # UNROT_e_ref_phase = e_ref_phase + phaseref(msmt.params_lt1['e_ref_frq'], 
    #     CNOT_elt.length())
    # UNROT_N_ref_phase = N_ref_phase + phaseref(msmt.params_lt1['N_ref_frq'],
    #     CNOT_elt.length())
    
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
        time_offset = _lt1_LDE_element.length() + N_init_elt.length())

    return N_init_elt, BSM_elts[0], BSM_elts[1]
