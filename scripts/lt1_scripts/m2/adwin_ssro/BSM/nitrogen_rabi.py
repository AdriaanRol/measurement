import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)

def run_nmr_frq_scan(name):
    m = BSM.NRabiMsmt('NMR_frq_scan_'+name) # BSM.ElectronRabiMsmt(name)
    BSM.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['RF_pulse_multiplicities'] = np.ones(pts).astype(int) * 1
    m.params['RF_pulse_delays'] = np.ones(pts) * 1e-6

    # MW pulses
    m.params['RF_pulse_durations'] = np.ones(pts) * 70e-6
    m.params['RF_pulse_amps'] = np.ones(pts) * 1
    m.params['RF_pulse_frqs'] = np.linspace(7.12e6, 7.15e6, pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'RF frequency (MHz)'
    m.params['sweep_pts'] = m.params['RF_pulse_frqs'] * 1e-6
    
    funcs.finish(m, debug=False)

def run_nmr_rabi(name):
    m = BSM.NRabiMsmt('Nuclear_rabi_'+name) # BSM.ElectronRabiMsmt(name)
    BSM.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['RF_pulse_multiplicities'] = np.ones(pts).astype(int) * 1
    m.params['RF_pulse_delays'] = np.ones(pts) * 1e-6

    # MW pulses
    m.params['RF_pulse_durations'] = np.linspace(1e-6, 361e-6, pts)
    m.params['RF_pulse_amps'] = np.ones(pts) * 1
    m.params['RF_pulse_frqs'] = np.ones(pts) * m.params['N_0-1_splitting_ms-1']

    # for the autoanalysis
    m.params['sweep_name'] = 'RF duration (us)'
    m.params['sweep_pts'] = m.params['RF_pulse_durations'] * 1e6
    
    BSM.finish(m, debug=False)

if __name__ == '__main__':
    #run_nmr_frq_scan('sil2')
    run_nmr_rabi('sil2')