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
    m.params.from_dict(qt.cfgman['protocols']['sil15-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil15-default']['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['samples']['sil15'])
       
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration']=m.params['green_repump_duration']
    m.params['repump_amplitude']=m.params['green_repump_amplitude']
    
    
    m.params['mw_frq'] = 2.80e9
    m.params['MW_length_start'] = 0
    m.params['MW_length_stop'] = 2000e-9
    m.params['pts'] = 51
    m.params['mw_power'] = 20
    m.params['repetitions'] = 500
    m.params['ssbmod_amplitude'] = 0.9
    m.params['ssbmod_frequency'] = m.params['ms-1_cntr_frq'] - m.params['mw_frq']
    m.params['MW_pulse_mod_risetime'] = 10e-9
      
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    erabi('ElectronRabi')
