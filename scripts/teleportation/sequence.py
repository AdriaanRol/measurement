from measurement.lib.pulsar import pulse, pulselib, element, pulsar

# import parameters as tparams
# reload(tparams)

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

    ### synchronizing, etc
    # msmt.adwin_sync = pulse.SquarePulse(channel='adwin_sync',
    #     length = 10e-6, amplitude = 2)

    return True

def pulse_defs_lt1(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T_pulse = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)
