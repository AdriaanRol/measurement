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

    m.params['mw_frq'] = 2.0e9-43e6 #MW source frequency 
    m.params['mw_power'] = 20  
    m.params['repetitions'] = 3000

    m.params['ssbmod_frq_start'] = 43e6 - 6.5e6
    m.params['ssbmod_frq_stop'] = 43e6 + 6.5e6
    m.params['pts'] = 41
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.03
   
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

    def darkesrp1(name):
    
    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])   

    m.params['mw_frq'] = 3.754e9-43e6 #MW source frequency 
    m.params['mw_power'] = 20  
    m.params['repetitions'] = 3000

    m.params['ssbmod_frq_start'] = 43e6 - 6.5e6
    m.params['ssbmod_frq_stop'] = 43e6 + 6.5e6
    m.params['pts'] = 41
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.05
   
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    darkesr(SAMPLE_CFG)
    raw_input ('Do the fitting...')
    darkesrp1(SAMPLE_CFG)
