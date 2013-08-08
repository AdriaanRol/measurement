import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar

from measurement.scripts.lt2_scripts.adwin_ssro import espin_funcs as funcs
reload(funcs)

name = 'sil15'

def electronramsey(name):
    m = pulsar.ElectronRamsey(name)
    funcs.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    m.params['evolution_times'] = np.ones(pts) * 5e-9

    # MW pulses
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = np.linspace(0,360,pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'phase second pi/2 pulse'
    m.params['sweep_pts'] = m.params['CORPSE_pi2_phases2'] 

    funcs.finish(m)

if __name__ == '__main__':
    electronramsey(name)

