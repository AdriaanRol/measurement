# one CR check followed by N ramseys
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar

from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)

name = 'test'
SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']
def repelectronramsey(name):
    m = pulsar.RepElectronRamseys(name)
    funcs.prepare(m)
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['pulses'])


    pts = 1
    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    m.params['evolution_times'] = np.linspace(2000e-9,pts)

    # MW pulses
    m.params['detuning']  = 0.0e6
    m.params['CORPSE_pi2_mod_frq'] = m.params['MW_modulation_frequency'] 
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = np.ones(pts) * 0#360 * m.params['evolution_times'] * 2e6

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)' 
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    funcs.finish(m)
    print m.adwin_var('completed_reps')

if __name__ == '__main__':
    repelectronramsey(name)

