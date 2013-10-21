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

def darkesr(name, yellow = False):
    m = pulsar_msmt.DarkESR(name)
    
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    
    if yellow:
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=m.params['yellow_CR_repump']
        m.params['repump_after_repetitions']=m.params['yellow_repump_after_repetitions']
    else: ##!!!! CHANGE THIS BACK IF MEASURING ON LT2
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']
        m.params['CR_repump']=m.params['green_CR_repump']
        m.params['repump_after_repetitions']=m.params['green_repump_after_repetitions']

    m.params['mw_frq'] = 2.8e9
    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000

    m.params['ssbmod_frq_start'] = 28.288e6 - 5e6
    m.params['ssbmod_frq_stop'] = 28.288e6 + 5e6
    m.params['pts'] = 161
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.02

    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.01
    m.params['MW_pulse_mod_risetime'] = 10e-9
    m.params['SSRO_duration'] = 40
    
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    darkesr(SAMPLE_CFG, yellow = False)
