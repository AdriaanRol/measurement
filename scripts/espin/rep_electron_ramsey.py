# one CR check followed by N ramseys
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar

#reload all parameters and modules
execfile(qt.reload_current_setup)

from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)

name = 'rep_ramseys_SIL4_zero_amp_MW_after_pos_optimize_lower_laserpower_2'
SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
def repelectronramsey(name):
    m = pulsar.RepElectronRamseys(name)
    funcs.prepare(m)
    m.params['wait_after_pulse_duration']=2
    m.params['wait_after_RO_pulse_duration']=2

    pts = 1
    m.params['pts'] = pts
    m.params['repetitions'] = 50000

    m.params['evolution_times'] = np.ones(pts)*(0.25/m.params['N_HF_frq'])

    # MW pulses
    m.params['detuning']  = 0.0e6
    m.params['CORPSE_pi2_mod_frq'] = m.params['CORPSE_pi2_mod_frq']
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']*0
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = np.ones(pts) * 90 #360 * m.params['evolution_times'] * 2e6

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    funcs.finish(m)
    print m.adwin_var('completed_reps')

if __name__ == '__main__':
    repelectronramsey(name)

