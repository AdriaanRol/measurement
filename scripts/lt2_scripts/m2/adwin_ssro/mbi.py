"""
LT2 script for MBI
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import measurement.lib.config.awgchannels_lt2 as awgcfg

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import sequence
from measurement.lib.measurement2.adwin_ssro import mbi

current_sample = qt.cfgman['samples']['current']
current_setting = qt.cfgman['protocols']['current']

def postinitdarkesr(name):
    m = mbi.PostInitDarkESR(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO+MBI'])
    
    # only green at the moment
    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']
    
    # ESR pulses
    m.params['RO_MW_pulse_duration'] = 2000
    m.params['RO_MW_pulse_amp'] = 0.03
    
    # MBI
    m.params['MBI_steps'] = 1
    m.params['AWG_wait_for_adwin_MBI_duration'] = np.array([15000], dtype=int)

    # measurement settings
    pts = 41
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = pts
    m.params['RO_MW_pulse_ssbmod_frqs'] = np.linspace(-4e6,4e6,pts) + \
            m.params['AWG_MBI_MW_pulse_ssbmod_frq'] + 2.189e6
    
    m.autoconfig()
    m.generate_sequence(send=True)
    m.setup()
    m.run()
    m.save()
    m.finish()