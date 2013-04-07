import qt
import numpy as np

import mbi
reload(mbi)


m = mbi.ElectronRabi('pi_calib_slow', 
        qt.instruments['adwin'], qt.instruments['AWG'])
mbi._prepare(m)

pts = 16
m.params['pts'] = pts
m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 2500
m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.01, 0.04, pts)
m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
m.params['reps_per_ROsequence'] = 1000
m.params['MW_pulse_multiplicity'] = 5
m.params['MW_pulse_delay'] = 20000


m.params['sweep_name'] = 'MW pulse amplitude (V)'
m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']

mbi._run(m)
