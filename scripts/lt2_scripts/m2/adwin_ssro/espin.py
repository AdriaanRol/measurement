"""
LT2 script for e-spin manipulations
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import measurement.lib.config.awgchannels_lt2 as awgcfg

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import sequence

def darkesr(name):
    m = sequence.DarkESR(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])    
    
    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']
    
    m.params['mw_frq'] = 2.8e9
    m.params['ssbmod_frq_start'] = 26e6
    m.params['ssbmod_frq_stop'] = 34e6
    m.params['pts'] = 81
    m.params['mw_power'] = 20
    m.params['pulse_length'] = 1000
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.03
    m.params['MW_pulse_mod_risetime'] = 2
    
    m.autoconfig()
    m.generate_sequence()
    m.run()
    m.save()
    m.finish()
