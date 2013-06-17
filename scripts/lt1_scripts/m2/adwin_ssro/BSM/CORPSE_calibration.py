import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import mbi_espin_funcs as funcs
reload(funcs)


### msmt class
class CORPSEPiCalibration(pulsar_msmt.MBI):
    mprefix = 'CORPSEPiCalibration'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_pi_mod_frq'],
            amplitude = self.params['CORPSE_pi_amp'],
            length_60 = self.params['CORPSE_pi_60_duration'],
            length_m300 = self.params['CORPSE_pi_m300_duration'],
            length_420 = self.params['CORPSE_pi_420_duration'])

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        elts = []
        for i in range(self.params['pts']):
            e = element.Element('CORPSE-{}'.format(i), pulsar=qt.pulsar)
            e.append(T,
                pulse.cp(CORPSE_pi,
                    amplitude=self.params['CORPSE_pi_sweep_amps'][i]))
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('CORPSE pi calibration')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name, 
                trigger_wait = True, goto_target = 'MBI-%d' % i, 
                jump_target = e.name+'-0')
            
            for j in range(self.params['multiplicity']):
                seq.append(name = e.name+'-{}'.format(j), 
                    wfname = e.name,
                    trigger_wait = (j==0))
                seq.append(name = 'wait-{}-{}'.format(i,j), 
                    wfname = wait_1us.name, 
                    repetitions = self.params['delay_reps'])
            seq.append(name = 'sync-{}'.format(i),
                wfname = sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(mbi_elt, sync_elt, wait_1us, *elts)
        qt.pulsar.program_sequence(seq)

# class CORPSEPiCalibration

def sweep_amplitude(name):
    m = CORPSEPiCalibration(name)
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.6, 0.8, pts)
    m.params['multiplicity'] = 11
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    sweep_amplitude('sil2_test')