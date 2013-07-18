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
    m = mbi_espin.ElectronRabi('cal_slow_pi_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 11
    pts=m.params['pts']
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 20000
  
    # slow pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 2500
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(-0.003, 0.003, pts)+m.params['AWG_MBI_MW_pulse_amp']
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_RO_MW_pulse_ssbmod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()   
    
    
def calpi397ns(name):
    m = mbi_espin.ElectronRabi('cal_397ns_pi_'+name)

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 5
    m.params['MW_pulse_delay'] = 20000
    
    # pi 2 pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 396
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(-0.02, 0.02, pts)+m.params['AWG_RO_MW_pulse_amp']
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_RO_MW_pulse_ssbmod_frq'] 

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']

    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()   
    
def calhardpipulse(name):
    m = mbi_espin.ElectronRabi('cal_hard_pi_'+name)

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 5
    m.params['MW_pulse_delay'] = 20000
    
    # hard pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(-10,10,pts) + m.params['AWG_shelving_pulse_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish() 
  
def calCORPSE60(name):
    m = mbi_espin.ElectronRabi('cal_CORPSE60_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO+MBI'])
 
    # measurement settings 
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1 
    m.params['MW_pulse_delay'] = 100
    
    # CORPSE 60 pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(-5,5,pts) + m.params['AWG_uncond_CORPSE60_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']   
    
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish() 
    
def calCORPSE300(name):
    m = mbi_espin.ElectronRabi('cal_CORPSE300_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO+MBI'])
 
    # measurement settings 
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1 
    m.params['MW_pulse_delay'] = 100
    
    # CORPSE 60 pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(-5,5,pts) + m.params['AWG_uncond_CORPSE300_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']   
    
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()  

def calCORPSE420(name):
    m = mbi_espin.ElectronRabi('cal_CORPSE420_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO+MBI'])
 
    # measurement settings 
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1 
    m.params['MW_pulse_delay'] = 100
    
    # CORPSE 60 pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(-10,10,pts) + m.params['AWG_uncond_CORPSE420_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']   
    
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()        
    