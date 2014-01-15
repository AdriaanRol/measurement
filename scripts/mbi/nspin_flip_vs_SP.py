import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import mbi_funcs as funcs
reload(funcs)

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

### msmt class
class NSpinflips(pulsar_msmt.MBI):
    mprefix = 'NSpinflips'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 2e-6, amplitude = 0)

        CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('msm1 CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['msm1_CORPSE_pi_mod_frq'],
            amplitude = self.params['msm1_CORPSE_pi_amp'],
            length_60 = self.params['msm1_CORPSE_pi_60_duration'],
            length_m300 = self.params['msm1_CORPSE_pi_m300_duration'],
            length_420 = self.params['msm1_CORPSE_pi_420_duration'])

        SP = pulse.SquarePulse(channel = 'Velocity1AOM',
            length = self.params['AWG_SP_duration'],
            amplitude = self.params['AWG_SP_amplitude'])

        pi2pi_m1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pi2pi_mIm1_mod_frq'],
            amplitude = self.params['pi2pi_mIm1_amp'],
            length = self.params['pi2pi_mIm1_duration'])

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        SP_elt = element.Element('SP_element', pulsar=qt.pulsar)
        SP_elt.append(T, CORPSE_pi, T, SP, T)

        RO_elt = element.Element('RO_element', pulsar=qt.pulsar)
        RO_elt.append(T, CORPSE_pi, T, pi2pi_m1)

        seq = pulsar.Sequence('N spin flips')
        for i,r in enumerate(self.params['AWG_sequence_repetitions']):

            seq.append(name = 'MBI-%d' % i, 
                wfname = mbi_elt.name, 
                trigger_wait = True, 
                goto_target = 'MBI-%d' % i, 
                jump_target = 'SP-{}'.format(i))

            if r > 0:
                seq.append(name = 'SP-{}'.format(i),
                    wfname = SP_elt.name,
                    trigger_wait = True,
                    repetitions = r)
            else:
                seq.append(name = 'SP-{}'.format(i),
                    wfname = wait_1us.name,
                    trigger_wait = True)

            seq.append(name = 'RO-{}'.format(i),
                wfname = RO_elt.name)
            seq.append(name = 'sync-{}'.format(i),
                wfname = sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(mbi_elt, sync_elt, wait_1us, SP_elt, RO_elt)
        qt.pulsar.program_sequence(seq)


def nspinflips(name):
    m = NSpinflips(name)
    funcs.prepare(m)
    
    SP_power = 20e-9
    m.params['AWG_SP_amplitude'] = qt.instruments['NewfocusAOM_lt1'].power_to_voltage(
        SP_power, controller='sec')
    m.params['AWG_SP_duration'] = 10e-6

    pts = 15
    rep_factor = 200
    m.params['pts'] = pts
    m.params['AWG_sequence_repetitions'] = np.arange(pts) * rep_factor
    m.params['reps_per_ROsequence'] = 1000

    # for testing
    m.params['msm1_CORPSE_pi_amp'] = 0.796974
    m.params['pi2pi_mIm1_mod_frq'] = 2.828067e9 - 2.8e9 - 2.19290e6
    m.params['pi2pi_mIm1_amp'] = 0.108
    m.params['pi2pi_mIm1_duration'] = 396e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'SP cycles'
    m.params['sweep_pts'] = m.params['AWG_sequence_repetitions']
    
    funcs.finish(m, upload=True, debug=False)

if __name__ == '__main__':
    nspinflips('hans1_E12')