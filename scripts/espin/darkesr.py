"""
Script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

SAMPLE= qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

def darkesr(name):
    m = pulsar_msmt.DarkESR(name)
   
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])   

    m.params['mw_frq'] = 2.8e9
    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000

    m.params['ssbmod_frq_start'] = 28.28e6 - 4e6
    m.params['ssbmod_frq_stop'] = 28.28e6 + 4e6
    m.params['pts'] = 161
    m.params['pulse_length'] = 3e-6
    m.params['ssbmod_amplitude'] = 0.01
   
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    darkesr(SAMPLE_CFG)
