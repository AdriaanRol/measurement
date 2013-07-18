"""
LT2 script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

def erabi(name):
    m = pulsar_msmt.ElectronRabi(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    
    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration']=m.params['green_repump_duration']
    m.params['repump_amplitude']=m.params['green_repump_amplitude']
    
    
    m.params['mw_frq'] = 2.80e9
    m.params['MW_length_start'] = 50
    m.params['MW_length_stop'] = 500
    m.params['pts'] = 30
    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.7
    m.params['ssbmod_frequency'] = cfg['samples']['sil9']['ms-1_cntr_frq'] - \
                                        cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['mw_frq']
    m.params['MW_pulse_mod_risetime'] = 2e-9
    
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    erabi('ElectronRabi')
    print 'your mother is a rabi.'
