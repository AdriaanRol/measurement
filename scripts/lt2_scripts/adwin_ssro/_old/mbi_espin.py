"""
LT2 script for MBI with electron manipulation
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import measurement.lib.config.awgchannels as awgcfg

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import sequence
from measurement.lib.measurement2.adwin_ssro import mbi
from measurement.lib.measurement2.adwin_ssro import mbi_espin

current_sample = qt.cfgman['samples']['current']
current_setting = qt.cfgman['protocols']['current']

def electronrabi(name):
    m = mbi_espin.ElectronRabi(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO+MBI'])
    
    # measurement settings 
    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 2000
    
    # only green at the moment
    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']
    
    # MBI
    m.params['AWG_MBI_MW_pulse_duration'] = 1920
    m.params['AWG_MBI_MW_pulse_amp'] = 0.03
    
    # MW pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(0,2000,pts) + 20
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.17
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()