import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar

from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)

name = 'sil4_no_time'

def electronramsey(name):
    m = pulsar.ElectronRamsey(name)
    funcs.prepare(m)

    pts = 61
    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    m.params['evolution_times'] = np.linspace(0,450e-9,pts)

    # MW pulses
    m.params['detuning']  = 0.0e6
    m.params['CORPSE_pi2_mod_frq'] = m.params['CORPSE_pi2_mod_frq'] + m.params['detuning']
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = np.ones(pts) * 0#360 * m.params['evolution_times'] * 2e6

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)' 
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    funcs.finish(m)

if __name__ == '__main__':
    electronramsey(name)

