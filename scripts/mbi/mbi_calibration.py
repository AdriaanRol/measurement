import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
import inspect

import mbi_funcs as funcs
reload(funcs)

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

# TODO should go into calibration file if this works
MIM1_AMP = 0.005687
MI0_AMP = 0.005608
MIP1_AMP = 0.005659

# In principle the msmt is just a Rabi msmt - but I want a different prefix :)
class MBICalibration(pulsar_mbi_espin.ElectronRabi):
    mprefix = 'MBICalibration'

    def __init__(self, name):
        pulsar_mbi_espin.ElectronRabi.__init__(self, name)

def run(name):
    m = pulsar_mbi_espin.ElectronRabi(name)
    funcs.prepare(m)

    pts = 4
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 20000
    
    # MBI
    m.params['SP_E_duration'] = 50
    m.params['Ex_SP_amplitude'] = 15e-9
    # m.params['AWG_MBI_MW_pulse_amp'] = 0 # set to zero for testing (then the populations of all N-states should be the same )
    # m.params['MBI_threshold'] = 1
    m.params['max_MBI_attempts'] = 1

    # MW pulses
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 2000e-9

    m.params['MW_pulse_durations'] = np.ones(pts) * 6e-6 # the four readout pulse durations
    m.params['MW_pulse_amps'] = np.array([MIM1_AMP, MI0_AMP, MIP1_AMP, 0.]) # calibrated powers for equal-length pi-pulses

    # Assume for now that we're initializing into m_I = -1 (no other nuclear spins)
    f_m1 = m.params['AWG_MBI_MW_pulse_mod_frq']
    f_HF = m.params['N_HF_frq']

    m.params['MW_pulse_mod_frqs'] = f_m1 + np.array([0,1,2,5]) * f_HF

    # for the autoanalysis
    m.params['sweep_name'] = 'Readout transitions'
    m.params['sweep_pts'] = m.params['MW_pulse_mod_frqs']
    m.params['sweep_pt_names'] = ['$m_I = -1$', '$m_I = 0$', '$m_I = +1$', 'None']

    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run(SAMPLE + '_' + 'MBI_timing_N=1-TH-37prep-16')