from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import parameters as tparams
reload(tparams)

def pulse_defs_lt2(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T_pulse = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)

    msmt.TIQ_pulse = pulse.SquarePulse(channel='MW_Imod',
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
    msmt.yellow_pulse = pulse.SquarePulse(channel = 'AOM_Yellow', amplitude = 1.0)
    msmt.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = 1.0, 
                                    length = msmt.params_lt2['PLU_gate_duration'])
    
    msmt.HH_marker = pulse.SquarePulse(channel = 'HH_MA1', length = 50e-9, amplitude = 1.0)

    ### LDE attempt

    return True

def pulse_defs_lt1(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T_pulse = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)

    msmt.TIQ_pulse = pulse.SquarePulse(channel='MW_Imod',
        length = 10e-9, amplitude = 0)

    # mw pulses
    msmt.e_pulse = pulselib.MW_IQmod_pulse('MW pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'])

    msmt.pi_pulse = pulselib.MW_IQmod_pulse('MW pi pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['MW_pi_mod_frq'],
        amplitude = msmt.params_lt1['MW_pi_amplitude'],
        length = msmt.params_lt1['MW_pi_length'])

    msmt.pi2_pulse = pulselib.MW_IQmod_pulse('MW pi2 pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params_lt1['MW_pulse_mod_risetime'],
        frequency = msmt.params_lt1['MW_pi2_mod_frq'],
        amplitude = msmt.params_lt1['MW_pi2_amplitude'],
        length = msmt.params_lt1['MW_pi2_length'])

    ### synchronizing, etc
    msmt.adwin_lt1_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2)

    msmt.AWG_LT2_trigger_pulse = pulse.SquarePulse(channel='AWG_LT2_trigger',
        length = 10e-9, amplitude = 2)

    msmt.HH_sync = pulse.SquarePulse(channel = 'HH_sync', length = 50e-9, amplitude = 1.0)

    # light
    msmt.SP_pulse = pulse.SquarePulse(channel = 'Velocity1AOM', amplitude = 1.0)
