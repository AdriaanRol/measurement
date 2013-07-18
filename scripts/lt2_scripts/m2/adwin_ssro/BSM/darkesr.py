"""
LT1 script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

def darkesr(name):
    m = pulsar_msmt.DarkESR(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    
    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration']=m.params['green_repump_duration']
    m.params['repump_amplitude']=m.params['green_repump_amplitude']
    
    m.params['mw_frq'] = 2.8e9
    m.params['ssbmod_frq_start'] = 25e6
    m.params['ssbmod_frq_stop'] = 34e6
    m.params['pts'] = 161
    m.params['mw_power'] = 20
    m.params['pulse_length'] = 2.5e-6
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.02
    m.params['MW_pulse_mod_risetime'] = 2e-9
    
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    darkesr('DarkESR')