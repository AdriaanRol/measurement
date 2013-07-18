from measurement.lib.pulsar import pulse, pulselib, element, pulsar

def pulse_defs(msmt):

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
        PM_risetime = msmt.params['MW_pulse_mod_risetime'] )

    # slow pi-pulse for MBI
    msmt.slow_pi = pulselib.MW_IQmod_pulse('slow pi',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        frequency = msmt.params['selective_pi_mod_frq'],
        amplitude = msmt.params['selective_pi_amp'],
        length = msmt.params['selective_pi_duration'])

    # reasonably fast pi and pi/2 pulses
    msmt.pi_4MHz = pulselib.MW_IQmod_pulse('4MHz pi',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        frequency = msmt.params['4MHz_pi_mod_frq'],
        amplitude = msmt.params['4MHz_pi_amp'],
        length = msmt.params['4MHz_pi_duration'])

    msmt.pi2_4MHz = pulselib.MW_IQmod_pulse('4MHz pi2',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        frequency = msmt.params['4MHz_pi2_mod_frq'],
        amplitude = msmt.params['4MHz_pi2_amp'],
        length = msmt.params['4MHz_pi2_duration'])

    # shelving pi-pulse to bring electron to ms=-1 after mbi
    msmt.shelving_pulse = pulselib.MW_IQmod_pulse('MBI shelving pulse',
        I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
        amplitude = msmt.params['AWG_shelving_pulse_amp'],
        length = msmt.params['AWG_shelving_pulse_duration'],
        PM_risetime = msmt.params['MW_pulse_mod_risetime'])

    # CORPSE pi pulse
    msmt.CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        frequency = msmt.params['CORPSE_pi_mod_frq'],
        amplitude = msmt.params['CORPSE_pi_amp'],
        length_60 = msmt.params['CORPSE_pi_60_duration'],
        length_m300 = msmt.params['CORPSE_pi_m300_duration'],
        length_420 = msmt.params['CORPSE_pi_420_duration'])

    # CNOT operations on the electron
    msmt.pi2pi_m1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        frequency = msmt.params['pi2pi_mIm1_mod_frq'],
        amplitude = msmt.params['pi2pi_mIm1_amp'],
        length = msmt.params['pi2pi_mIm1_duration'])

    msmt.pi2pi_0 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=0',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        frequency = msmt.params['pi2pi_mI0_mod_frq'],
        amplitude = msmt.params['pi2pi_mI0_amp'],
        length = msmt.params['pi2pi_mI0_duration'])
        
    msmt.pi2pi_p1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=0',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        frequency = msmt.params['pi2pi_mIp1_mod_frq'],
        amplitude = msmt.params['pi2pi_mIp1_amp'],
        length = msmt.params['pi2pi_mIp1_duration'])

    ### nuclear spin manipulation pulses
    msmt.TN = pulse.SquarePulse(channel='RF',
        length = 100e-9, amplitude = 0)

    msmt.N_pulse = pulselib.RF_erf_envelope(
        channel = 'RF',
        frequency = msmt.params['N_0-1_splitting_ms-1'])

    msmt.N_pi = pulselib.RF_erf_envelope(
        channel = 'RF',
        frequency = msmt.params['N_0-1_splitting_ms-1'],
        length = msmt.params['N_pi_duration'],
        amplitude = msmt.params['N_pi_amp'])

    msmt.N_pi2 = pulselib.RF_erf_envelope(
        channel = 'RF',
        frequency = msmt.params['N_0-1_splitting_ms-1'],
        length = msmt.params['N_pi2_duration'],
        amplitude = msmt.params['N_pi2_amp'])

    ### synchronizing, etc
    msmt.adwin_sync = pulse.SquarePulse(channel='adwin_sync',
        length = 10e-6, amplitude = 2)

    return True

