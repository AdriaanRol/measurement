import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


def prepare(m):
    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO-integrated'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+MBI'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO+MBI'))

    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/pulses'))

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']

    m.params['MW_pulse_mod_risetime'] = 2e-9

def finish(m, upload=True, debug=False):
    m.autoconfig()
    m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()

### msmt class
class BSMMsmt(pulsar_msmt.MBI):
    mprefix = 'BSM'

    def _pulse_defs(self):
        ### electron manipulation pulses
        
        # a waiting pulse on the MW pulsemod channel
        self.T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        # slow pi-pulse for MBI
        self.slow_pi = pulselib.MW_IQmod_pulse('slow pi',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['selective_pi_mod_frq'],
            amplitude = self.params['selective_pi_amp'],
            length = self.params['selective_pi_duration'])

        # reasonably fast pi and pi/2 pulses
        self.pi_4MHz = pulselib.MW_IQmod_pulse('4MHz pi',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['4MHz_pi_mod_frq'],
            amplitude = self.params['4MHz_pi_amp'],
            length = self.params['4MHz_pi_duration'])

        self.pi2_4MHz = pulselib.MW_IQmod_pulse('4MHz pi2',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['4MHz_pi2_amp_mod_frq'],
            amplitude = self.params['4MHz_pi2_amp'],
            length = self.params['4MHz_pi2_duration'])

        # shelving pi-pulse to bring electron to ms=-1 after mbi
        self.shelving_pulse = pulselib.MW_IQmod_pulse('MBI shelving pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
            amplitude = self.params['AWG_shelving_pulse_amp'],
            length = self.params['AWG_shelving_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        # CORPSE pi pulse
        self.CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_pi_mod_frq'],
            amplitude = self.params['CORPSE_pi_amp'],
            length_60 = self.params['CORPSE_pi_60_duration'],
            length_m300 = self.params['CORPSE_pi_m300_duration'],
            length_420 = self.params['CORPSE_pi_420_duration'])

        # CNOT operation on the electron
        self.pi2pi_m1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pi2pi_mIm1_mod_frq'],
            amplitude = self.params['pi2pi_mIm1_amp'],
            length = self.params['pi2pi_mIm1_duration'])

        ### synchronizing, etc
        self.adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)


    def generate_sequence(self, upload=True):
        pass



class ElectronROMsmt(BSMMsmt):
    mprefix = 'BSM_EReadout'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # adwin sync element
        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        sync_elt.append(adwin_sync)

        # the sequence
        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix, self.name))


