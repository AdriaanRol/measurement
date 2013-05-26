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
from measurement.lib.measurement2.adwin_ssro import mbi_nmr


def calslowpipulse(name):
    m = mbi_espin.ElectronRabi('cal_slow_pi_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 12
    pts=m.params['pts']
    m.params['MW_pulse_multiplicity'] =1
    m.params['MW_pulse_delay'] = 20000
  
    # slow pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 2500
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(-0.005, 0.005, pts)+m.params['AWG_MBI_MW_pulse_amp']
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_RO_MW_pulse_ssbmod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['AWG_RcO_MW_pulse_amps']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()   
    
    
def calpi397ns(name):
    m = mbi_espin.ElectronRabi('cal_397ns_pi_'+name)

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
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
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 2000
    
    # hard pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * m.params['AWG_shelving_pulse_duration'] #np.linspace(-10,10,pts) + m.params['AWG_shelving_pulse_duration']# 
    m.params['AWG_RO_MW_pulse_amps'] =np.ones(pts) * m.params['AWG_shelving_pulse_amp']# np.linspace(0.85,0.9,pts)#
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
   
        
    # for the autoanalysis    
    m.params['sweep_name'] ='nothing' #'MW pulse amplitude'# 'MW pulse length (ns)'#
    m.params['sweep_pts'] =np.arange(pts)#m.params['AWG_RO_MW_pulse_amps']# 
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish() 

def calhardpi2pulse(name):
    m = mbi_espin.ElectronRabi('cal_hard_pi_'+name)

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 2
    m.params['MW_pulse_delay'] = 100
    
    # hard pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(-15,15,pts) + m.params['AWG_MW_hard_pi2_pulse_duration']
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
    
def calpipulsesweepCORPSEamp(name):
    m = mbi_espin.ElectronRabi('cal_CORPSE_pi_'+name)

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])

    # measurement settings
    pts = 12
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_delay'] = 20000
    m.params['MW_pulse_multiplicity'] = 9
    
    # hard pi pulses
    m.params['AWG_RO_MW_pulse_durations'] =np.ones(pts)* m.params['AWG_uncond_CORPSE_amp_pi_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.6,0.9,pts) #+ m.params['AWG_uncond_CORPSE_amp']
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq'] 

    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']

        
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()   
    m.finish() 
    
   
def calsweepCORPSEamplitude(name):
    m = mbi_espin.CORPSETest('sweep_CORPSE_amp_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings    
    m.params['pts'] = 9
    pts = m.params['pts']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 15
    m.params['MW_pulse_delay'] = 100
    
    #CORPSE pulse settings.
    m.params['AWG_uncond_CORPSE420_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE420_duration']
    m.params['AWG_uncond_CORPSE300_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE300_duration'] 
    m.params['AWG_uncond_CORPSE60_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE60_duration']
    m.params['AWG_uncond_CORPSE_amps'] = np.linspace(0.72,0.85,pts)#+ m.params['AWG_uncond_CORPSE_amp']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude'
    m.params['sweep_pts'] =  m.params['AWG_uncond_CORPSE_amps']
   
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish() 


def calNpipulse(name):
    
    m = mbi_nmr.NMRSweep('cal_N_Pipulse_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings
    m.params['pts'] = 8
    pts = m.params['pts']    
    m.params['reps_per_ROsequence'] = 1000
    
    # RF pulses
    m.params['RF_pulse_len'] = np.linspace(-15e3, 15e3, pts).astype(int) + m.params['AWG_RF_pipulse_duration']
    m.params['RF_pulse_amp'] = np.ones(pts) * 1.
    m.params['RF_frq'] = np.ones(pts) * 7.135e6 #This is the hyperfine splitting (Q+A) between mI=-1 and mI=0
   
    m.params['wait_before_readout_reps'] = np.ones(pts)
    m.params['wait_before_readout_element'] = int(1e3)
    
    # for the autoanalysis
    m.params['sweep_name'] = 'RF pulse length (us)'
    m.params['sweep_pts'] = m.params['RF_pulse_len']/1e3
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish() 
    
    
def calCORPSE60(name):
    m = mbi_espin.ElectronRabi('cal_CORPSE60_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
 
    # measurement settings 
    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 18
    m.params['MW_pulse_delay'] = 100
    
    # CORPSE 60 pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE60_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.7,0.9,pts)# m.params['AWG_uncond_CORPSE_amp']
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']   
    
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish() 
    
def calCORPSE300(name):
    m = mbi_espin.ElectronRabi('cal_CORPSE300_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
 
    # measurement settings 
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 3
    m.params['MW_pulse_delay'] = 100
    
    # CORPSE 60 pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) *  m.params['AWG_uncond_CORPSE300_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.7,0.9,pts)
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']   
    
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()  

def calCORPSE420(name):
    m = mbi_espin.ElectronRabi('cal_CORPSE420_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
 
    # measurement settings 
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1 
    m.params['MW_pulse_delay'] = 100
    
    # CORPSE 60 pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(-10,10,pts) + m.params['AWG_uncond_CORPSE420_duration']
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * m.params['AWG_uncond_CORPSE_amp']
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

def calsweepCORPSE60(name):
    m = mbi_espin.CORPSETest('sweep_CORPSE60_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings    
    m.params['pts'] = 15
    pts = m.params['pts']
    m.params['reps_per_ROsequence'] = 1000
    
    #Durations CORPSE pulse.
    m.params['AWG_uncond_CORPSE420_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE420_duration']
    m.params['AWG_uncond_CORPSE300_durations'] =np.ones(pts) * m.params['AWG_uncond_CORPSE300_duration'] 
    m.params['AWG_uncond_CORPSE60_durations'] = np.linspace(-30,+30,pts) + m.params['AWG_uncond_CORPSE60_duration']
    m.params['AWG_uncond_CORPSE_amps'] = np.ones(pts) * m.params['AWG_uncond_CORPSE_amp']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'duration CORPSE 60 (ns)'
    m.params['sweep_pts'] =  m.params['AWG_uncond_CORPSE60_durations']
   
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()
       
def calsweepCORPSE300(name):
    m = mbi_espin.CORPSETest('sweep_CORPSE300_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings    
    m.params['pts'] = 12
    pts = m.params['pts']
    m.params['reps_per_ROsequence'] = 1000
    
    #Durations CORPSE pulse.
    m.params['AWG_uncond_CORPSE420_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE420_duration']
    m.params['AWG_uncond_CORPSE300_durations'] = np.linspace(-30,+30,pts) + m.params['AWG_uncond_CORPSE300_duration'] 
    m.params['AWG_uncond_CORPSE60_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE60_duration']
    m.params['AWG_uncond_CORPSE_amps'] = np.ones(pts) * m.params['AWG_uncond_CORPSE_amp']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'duration CORPSE 300 (ns)'
    m.params['sweep_pts'] =  m.params['AWG_uncond_CORPSE300_durations']
   
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()
       
def calsweepCORPSE420(name):
    m = mbi_espin.CORPSETest('sweep_CORPSE420_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # measurement settings    
    m.params['pts'] = 15
    pts = m.params['pts']
    m.params['reps_per_ROsequence'] = 1000
    
    #Durations CORPSE pulse.
    m.params['AWG_uncond_CORPSE420_durations'] = np.linspace(-30,+30,pts) + m.params['AWG_uncond_CORPSE420_duration']
    m.params['AWG_uncond_CORPSE300_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE300_duration'] 
    m.params['AWG_uncond_CORPSE60_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE60_duration']
    m.params['AWG_uncond_CORPSE_amps'] = np.ones(pts) * m.params['AWG_uncond_CORPSE_amp']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'duration CORPSE 420 (ns)'
    m.params['sweep_pts'] =  m.params['AWG_uncond_CORPSE420_durations']
   
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()     
    
    