import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import mbi_funcs as funcs
reload(funcs)

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

class RR(pulsar_msmt.MBI):
    mprefix = 'NRepetitiveReadout'

    def __init__(self, name):
        pulsar_msmt.MBI.__init__(self, name)

    def generate_sequence(self, upload=True):
        mbi_elt = self._MBI_element()

        T_MW = pulse.SquarePulse(channel='MW_pulsemod',
            length = 50e-9, amplitude = 0)
        T_SP = pulse.SquarePulse(channel='Velocity1AOM',
            length = 200e-9, amplitude = 0)

        CNOT = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pi2pi_mIm1_mod_frq'],
            amplitude = self.params['pi2pi_mIm1_amp'],
            length = self.params['pi2pi_mIm1_duration'])

        CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime =  msmt.params_lt1['MW_pulse_mod_risetime'],
            frequency = msmt.params_lt1['CORPSE_pi_mod_frq'],
            amplitude = msmt.params_lt1['CORPSE_pi_amp'],
            length_60 = msmt.params_lt1['CORPSE_pi_60_duration'],
            length_m300 = msmt.params_lt1['CORPSE_pi_m300_duration'],
            length_420 = msmt.params_lt1['CORPSE_pi_420_duration'])

        SP_pulse = pulse.SquarePulse(channel = 'Velocity1AOM', amplitude = 1.0)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'], 
            amplitude = 2)


        N_ro_elt = element.Element('N_RO', pulsar=qt.pulsar,
            global_time = True)
        N_ro_elt.append(T_SP)
        N_ro_elt.append()




