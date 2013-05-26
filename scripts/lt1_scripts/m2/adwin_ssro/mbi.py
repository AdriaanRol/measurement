"""
LT1 script for MBI
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


def postinitdarkesr(name):
    m = mbi.PostInitDarkESR(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # ESR pulses
    m.params['RO_MW_pulse_duration'] = 2100
    m.params['RO_MW_pulse_amp'] = 0.02
    
    # MBI
    m.params['AWG_MBI_MW_pulse_amp'] = 0.1898
    m.params['AWG_MBI_MW_pulse_duration'] = 398
    m.params['MBI_steps'] = 1

    # measurement settings
    pts = 81
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = pts
    m.params['RO_MW_pulse_ssbmod_frqs'] = np.linspace(-4e6,4e6,pts) + \
            m.params['AWG_MBI_MW_pulse_ssbmod_frq'] + 2.175e6
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()   