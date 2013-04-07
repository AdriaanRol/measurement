import qt
import numpy as np

import mbi
reload(mbi)


m = mbi.ElectronRabi('pi2_calib_hard', 
        qt.instruments['adwin'], qt.instruments['AWG'])
mbi._prepare(m)

pts = 16
m.params['pts'] = pts
m.params['AWG_RO_MW_pulse_durations'] = np.linspace(40,80,pts)
m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
m.params['reps_per_ROsequence'] = 1000
m.params['MW_pulse_multiplicity'] = 2
m.params['MW_pulse_delay'] = 100


m.params['sweep_name'] = 'MW pulse duration (ns)'
m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']

mbi._run(m)
