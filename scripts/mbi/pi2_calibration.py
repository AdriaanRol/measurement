import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

class Pi2Calibration(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIPi2Calibration'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        fast_pi = pulselib.MW_IQmod_pulse('MW pi pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        frequency = self.params['fast_pi_mod_frq'],
        amplitude = self.params['fast_pi_amp'],
        length = self.params['fast_pi_duration'])

        fast_pi2 = pulselib.MW_IQmod_pulse('MW pi2 pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        frequency = self.params['fast_pi2_mod_frq'],
        amplitude = self.params['fast_pi2_amp'],
        length = self.params['fast_pi2_duration'])

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        # electron manipulation elements
        elts = []
        seq = pulsar.Sequence('Pi2 Calibration')

        for i in range(self.params['pts_awg']):
            e = element.Element('Pi2_Pi-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(fast_pi2, amplitude = self.params['pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=200e-9))
            e.append(pulse.cp(fast_pi))
            e.append(T)
            elts.append(e)

            seq.append(name = 'MBIa-%d' % i, wfname = mbi_elt.name, 
                trigger_wait = True, goto_target = 'MBIa-%d' % i, 
                jump_target = e.name)
            seq.append(name='Pi2_Pi-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='synca-{}'.format(i),
                wfname = sync_elt.name)
            
            e = element.Element('Pi2-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(fast_pi2, amplitude = self.params['pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=200e-9))
            e.append(T)
            elts.append(e)
            seq.append(name = 'MBIb-%d' % i, wfname = mbi_elt.name, 
                trigger_wait = True, goto_target = 'MBIb-%d' % i, 
                jump_target = e.name)
            seq.append(name='Pi2-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)

        if upload:
            qt.pulsar.upload(mbi_elt, sync_elt, *elts)
        qt.pulsar.program_sequence(seq)
    