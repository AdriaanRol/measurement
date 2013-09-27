import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

import mbi_funcs as funcs
reload(funcs)

SIL_NAME = 'hans-sil4'

def run(name):
    m = pulsar_mbi_espin.ElectronRamsey(name)
    funcs.prepare(m, SIL_NAME)

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['MW_pulse_delays'] = np.linspace(0,3000e-9,pts)

    # MW pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['fast_pi2_duration']
    m.params['MW_pulse_amps'] = np.ones(pts) * m.params['fast_pi2_amp']
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
    m.params['MW_pulse_1_phases'] = np.ones(pts) * 0
    m.params['MW_pulse_2_phases'] = np.ones(pts) * 0

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_delays'] /1e-9
    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run(SIL_NAME+'mbi_eramsey')

