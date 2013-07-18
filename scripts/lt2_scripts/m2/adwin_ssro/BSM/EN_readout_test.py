import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)

class NRabi(BSM.ENReadoutMsmt):
    mprefix = 'BSM_ENRO_NRabi'

    def get_sweep_elements(self):        
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('NRabi_pt-{}'.format(i), pulsar=qt.pulsar)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(self.T)
            for j in range(self.params['RF_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(self.N_pulse,
                        frequency = self.params['RF_pulse_frqs'][i],
                        amplitude = self.params['RF_pulse_amps'][i],
                        length = self.params['RF_pulse_durations'][i]))
                e.append(
                    pulse.cp(self.TN, length=self.params['RF_pulse_delays'][i]))
            elts.append(e)

        return elts


def N_rabi(name):
    m = NRabi(name) # BSM.ElectronRabiMsmt(name)
    BSM.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500
    m.params['RF_pulse_multiplicities'] = np.ones(pts).astype(int) * 1
    m.params['RF_pulse_delays'] = np.ones(pts) * 1e-6

    # MW pulses
    m.params['RF_pulse_durations'] = np.linspace(1e-6, 181e-6, pts)
    m.params['RF_pulse_amps'] = np.ones(pts) * 1
    m.params['RF_pulse_frqs'] = np.ones(pts) * m.params['N_0-1_splitting_ms-1']

    # for the autoanalysis
    m.params['sweep_name'] = 'RF duration (us)'
    m.params['sweep_pts'] = m.params['RF_pulse_durations'] * 1e6
    
    BSM.finish(m, debug=False)

if __name__ == '__main__':
    N_rabi('sil9_test')