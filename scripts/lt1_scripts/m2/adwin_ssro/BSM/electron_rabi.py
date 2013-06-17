import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)

def run_electron_rabi(name):
    m = BSM.ElectronRabiMsmt(name) # BSM.ElectronRabiMsmt(name)
    BSM.prepare(m)

    leftline = m.params['AWG_MBI_MW_pulse_mod_frq']
    HF = 2.19290e6

    m.params['AWG_MBI_MW_pulse_mod_frq'] = leftline

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * 1
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9

    # MW pulses
    m.params['MW_pulse_durations'] = np.linspace(0, 150e-9, pts) + 10e-9
    m.params['MW_pulse_amps'] = np.ones(pts) * 0.7
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations'] * 1e9
    
    funcs.finish(m, debug=False)


def MBI_fidelity(name):
    m = BSM.ElectronRabiMsmt(name) # BSM.ElectronRabiMsmt(name)
    BSM.prepare(m)

    leftline = m.params['AWG_MBI_MW_pulse_mod_frq']
    HF = 2.19290e6

    m.params['AWG_MBI_MW_pulse_mod_frq'] = leftline

    pts = 4
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * 1
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9

    # MW pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * 2800e-9
    m.params['MW_pulse_amps'] = np.array([0.0213, 0.0218, 0.0218, 0.0218]) * 0
    m.params['MW_pulse_mod_frqs'] = np.array([leftline, leftline + HF, leftline + 2*HF, leftline + 3*HF])

    # for the autoanalysis
    m.params['sweep_name'] = 'MW mod frq (MHz)'
    m.params['sweep_pts'] = m.params['MW_pulse_mod_frqs']
    
    BSM.finish(m, debug=False)

if __name__ == '__main__':
    run_electron_rabi('SIL2_find_pi2')
    # MBI_fidelity('SIL2_test_MBI_fidelity_no_driving')

