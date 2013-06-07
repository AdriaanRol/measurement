import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt


class ElectronRabi(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRabi'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-%d' % i, pulsar=qt.pulsar)
            e.append(T)
            
            for j in range(self.params['MW_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(X,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_amps'][i],
                        length = self.params['MW_pulse_durations'][i]))
                e.append(
                    pulse.cp(T, length=self.params['MW_pulse_delays'][i]))

            e.append(adwin_sync)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name, 
                trigger_wait = True, goto_target = 'MBI-%d' % i, 
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name, 
                trigger_wait = True)

        # program AWG
        if upload:
            qt.pulsar.upload(mbi_elt, *elts)
        qt.pulsar.program_sequence(seq)

class ElectronRabiSplitMultElements(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRabi'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)

        # electron manipulation elements
        pulse_elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-%d' % i, pulsar=qt.pulsar)
            e.append(T)
            e.append(
                pulse.cp(X,
                    frequency = self.params['MW_pulse_mod_frqs'][i],
                    amplitude = self.params['MW_pulse_amps'][i],
                    length = self.params['MW_pulse_durations'][i]))

            # e.append(adwin_sync)
            pulse_elts.append(e)

        wait_elt = element.Element('pulse_delay', pulsar=qt.pulsar)
        wait_elt.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        sync_elt.append(adwin_sync)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(pulse_elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name, 
                trigger_wait = True, goto_target = 'MBI-%d' % i, 
                jump_target = e.name+'-0')
            
            if self.params['MW_pulse_multiplicities'][i] == 0:
                seq.append(name = e.name+'-0', wfname = wait_elt.name,
                    trigger_wait = True)
            else:            
                for j in range(self.params['MW_pulse_multiplicities'][i]):
                    seq.append(name = e.name+'-%d' % j, wfname = e.name, 
                        trigger_wait = (j==0) )
                    seq.append(name = 'wait-%d-%d' % (i,j), wfname=wait_elt.name,
                        repetitions = int(self.params['MW_pulse_delays'][i]/1e-6))

            seq.append(name = 'sync-%d' % i, wfname=sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(mbi_elt, wait_elt, sync_elt, *pulse_elts)
        qt.pulsar.program_sequence(seq)
