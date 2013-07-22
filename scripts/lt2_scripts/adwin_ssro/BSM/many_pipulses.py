import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

import pulsar_mbi_espin_funcs as funcs
reload(funcs)

def sweep_pies(name):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements("sweep_pipulse_cnt_"+name)
    funcs.prepare(m)
    
    # measurement settings
    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = range(0,5*pts,5)
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['4MHz_pi_duration']
    m.params['MW_pulse_amps'] = np.ones(pts) * m.params['4MHz_pi_amp']
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'Number of pies'
    m.params['sweep_pts'] = m.params['MW_pulse_multiplicities']

    funcs.finish(m, upload=True)

if __name__ == '__main__':
    sweep_pies('sil9')