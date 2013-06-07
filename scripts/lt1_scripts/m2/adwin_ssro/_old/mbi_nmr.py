"""
LT1 script for nitrogen manipulation
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
from measurement.lib.measurement2.adwin_ssro import mbi_nmr

def _prepare(m):
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['pulses'])
    
    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']

def _finish(m):
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()

def nitrogenrabi(name):
    m = mbi_nmr.NMRSweep(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
   
    # measurement settings
    m.params['pts'] = 16
    pts = m.params['pts']    
    m.params['reps_per_ROsequence'] = 1000
    
    # RF pulses
    m.params['RF_pulse_len'] = np.linspace(1e3, 401e3, pts).astype(int)
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

def Npulse_vs_frq(name):
    m = mbi_nmr.NMRSweep('Npulse_vs_frq_'+name)
    _prepare(m)
    
    # measurement settings
    m.params['pts'] = 31
    pts = m.params['pts']    
    m.params['reps_per_ROsequence'] = 500
    
    # Uncomment for electron in ms=0
    m.params['AWG_shelving_pulse_duration'] = m.params['4MHz_pi_duration']
    m.params['AWG_shelving_pulse_amp'] = 0 # m.params['4MHz_pi_amp']
        
    # RF pulses
    m.params['RF_pulse_len'] = np.ones(pts) * 80e3
    m.params['RF_pulse_amp'] = np.ones(pts) * 0.5
    
    #This is the hyperfine splitting (Q for ms=0, Q+A for ms=-1) between mI=-1 and mI=0
    m.params['RF_frq'] = np.linspace(-0.030e6 , 0.030e6, pts) + 4.942e6 # + 2.193e6
   
    m.params['wait_before_readout_reps'] = np.ones(pts)
    m.params['wait_before_readout_element'] = int(1e3)
    
    # for the autoanalysis
    m.params['sweep_name'] = 'RF pulse frequency (MHz)'
    m.params['sweep_pts'] = m.params['RF_frq']/1e6
    
    _finish(m)
    

def tomo(name):
    m = mbi_nmr.NMRTomoPi2(name)
 
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI']) 

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 3 

    m.params['AWG_uncond_CORPSE_amp'] = 0
    m.params['AWG_uncond_CORPSE60_duration'] = 0 
    m.params['AWG_uncond_CORPSE300_duration'] = 0
    m.params['AWG_uncond_CORPSE420_duration'] = 0
    m.params['AWG_uncond_CORPSE_total_duration'] = 0
    ### For not doing tomo twice, set amplitudes to zero of part 2 in the mbi_nmr module.

    # for the autoanalysis
    m.params['sweep_name'] = 'bases'
    m.params['sweep_pts'] = np.arange(3)

    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish() 
    
def uncondtomo(name):
    m = mbi_nmr.NMRTomoPi2(name)
 
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI']) 

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 3 
    
    # Total CORPSE duration
    m.params['AWG_uncond_CORPSE_total_duration']= m.params['AWG_uncond_CORPSE60_duration'] \
            + m.params['AWG_uncond_CORPSE300_duration'] \
            + m.params['AWG_uncond_CORPSE420_duration'] \
            + int(20) #start delays
    
    # to not do tomography
    #m.params['AWG_RF_p2pulse_duration'] = 0
    #m.params['AWG_RF_p2pulse_amp'] = 0
    
    
    # for the autoanalysis
    m.params['sweep_name'] = 'bases'
    m.params['sweep_pts'] = np.arange(3)

    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()     

def doublereadout(name):
    m = mbi_nmr.NMRDoubleRO(name)
 
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI']) 

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 8 
    pts=m.params['pts']

    ### Here are the parameters for the double readout script.     
    m.params['nr_of_ROsequences'] = 2
    m.params['A_SP_durations'] = np.array([100,100], dtype=int)
    m.params['E_RO_durations'] = np.array([15,15], dtype=int)
    m.params['A_SP_amplitudes'] = np.array([10e-9,10e-9])
    m.params['E_RO_amplitudes'] = np.array([5e-9,5e-9])
    m.params['send_AWG_start'] = np.array([1,1])
    m.params['sequence_wait_time'] = np.array([0,0], dtype=int)
    
    
    # for the autoanalysis
    m.params['sweep_name'] = 'nothing'
    m.params['sweep_pts'] = np.arange(pts)

    m.autoconfig()
    print 0
    m.generate_sequence()
    print 1
    m.setup()
    print 2
    m.run()
    print 3
    m.save()
    print 4
    m.finish()      
    