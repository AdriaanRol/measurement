import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import mbi_funcs as funcs
reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

class RR(pulsar_msmt.MBI):
    mprefix = 'NRepetitiveReadout'

    def __init__(self, name):
        pulsar_msmt.MBI.__init__(self, name)

    # def autoconfig(self):
    #     pulsar_msmt.MBI.autoconfig(self)

    #     self.params['AWG_RO_SP_voltage'] = self.A_aom.power_to_voltage(
    #         self.params['AWG_RO_SP_amplitude'],
    #         controller='sec')

    # def setup(self):
    #     pulsar_msmt.MBI.setup(self)

    #     qt.pulsar.set_channel_opt('Velocity1AOM', 'high',
    #         self.params['AWG_RO_SP_voltage'])


    def generate_sequence(self, upload=True):
        mbi_elt = self._MBI_element()

        T_MW = pulse.SquarePulse(channel='MW_pulsemod',
            length = 50e-9, amplitude = 0)
        T_SP = pulse.SquarePulse(channel='Velocity1AOM',
            length = 200e-9, amplitude = 0)

        CNOT_pi2pi = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
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
            PM_risetime =  self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_pi_mod_frq'],
            amplitude = self.params['CORPSE_pi_amp'],
            length_60 = self.params['CORPSE_pi_60_duration'],
            length_m300 = self.params['CORPSE_pi_m300_duration'],
            length_420 = self.params['CORPSE_pi_420_duration'])

        SP_pulse = pulse.SquarePulse(channel = 'Velocity1AOM',
            amplitude = 1.0)

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)
        sync_elt.append(adwin_sync)

        N_ro_elt = element.Element('N_RO', pulsar=qt.pulsar,
            global_time = True)

        # N_ro_elt.append(T_SP)
        # N_ro_elt.append(pulse.cp(SP_pulse,
        #                          length = self.params['RO_SP_duration']),
        #                 )

        N_ro_elt.append(T_MW)
        N_ro_elt.append(CORPSE_pi)
        N_ro_elt.append(T_MW)
        N_ro_elt.append(CNOT_pi2pi)
        N_ro_elt.append(pulse.cp(T_MW, length=1e-6))
        # N_ro_elt.append(adwin_sync)

        seq = pulsar.Sequence('N-RR')
        seq.append(name = 'MBI',
            wfname = mbi_elt.name,
            trigger_wait = True,
            goto_target = 'MBI',
            jump_target = 'RO-1')

        for i in range(self.params['nr_of_ROsequences']):
            seq.append(name = 'RO-{}'.format(i+1),
                wfname = N_ro_elt.name,
                trigger_wait = True)

            seq.append(name = 'sync-{}'.format(i+1),
                wfname = sync_elt.name)

        if upload:
            qt.pulsar.upload(mbi_elt, sync_elt, N_ro_elt)
        qt.pulsar.program_sequence(seq)

def finish_RR(m, reps=1, upload=True, debug=False):
    m.autoconfig()

    m.params['A_SP_durations'] = np.ones(reps).astype(int) * 15
    m.params['A_SP_amplitudes'] = np.ones(reps) * 15e-9
    m.params['E_RO_durations'] = np.ones(reps) * m.params['SSRO_duration']
    m.params['E_RO_amplitudes'] = np.ones(reps) * m.params['Ex_RO_amplitude']
    m.params['send_AWG_start'] = np.ones(reps).astype(int)
    m.params['sequence_wait_time'] = np.zeros(reps).astype(int)

    m.generate_sequence(upload=upload)

    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()

def rr(name):
    m = RR(name)
    funcs.prepare(m)

    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # RR settings
    # m.params['CORPSE_pi_amp'] = 0 # 0 for RO from ms=0!
    m.params['nr_of_ROsequences'] = 10
    m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = m.params['mI0_mod_frq'] # m.params['mIm1_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'n/a'
    m.params['sweep_pts'] = m.params['pts']

    finish_RR(m, m.params['nr_of_ROsequences'], upload=True, debug=False)


if __name__ == '__main__':
    rr(SAMPLE + '_' + 'from_ms=-1_MBI_mI=0')






