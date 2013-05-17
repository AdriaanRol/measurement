"""
LT1 script for calibration
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


def calslowpipulse(name):
    m = mbi_espin.ElectronRabi(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # slow pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 2500
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(-0.0015, 0.0015, pts)+m.params['AWG_MBI_MW_pulse_amp']
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 25
    pts=m.params['pts']
    m.params['MW_pulse_multiplicity'] = 5
  
    # for the autoanalysis
    m.params['sweep_name'] = 'MW frq (MHz)'
    m.params['sweep_pts'] = (m.params['RO_MW_pulse_ssbmod_frqs'] +  m.params['mw_frq'])/1e6
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()   