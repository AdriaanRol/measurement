"""
LT1 script for MBI with electron manipulation
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

def electronrabi(name):
    m = mbi_espin.ElectronRabi(name)
    _prepare(m)
    
    m.params['mw_frq'] = 2.8e9
    m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    
    # measurement settings 
    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 2000
    
    # MW pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(0,1500,pts) + 5
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.15
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse duration(ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']
    
    _finish(m)

def electronramsey(name):
    m = mbi_espin.ElectronRamsey(name)
    _prepare(m)
       
    # measurement settings 
    pts = 51
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_delay'] = 2000

    m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq']    
    m.params['Ramsey_pi2_pulse_detuning'] = 0.7e6
    m.params['Phase_induced_frq_shift'] = 4e6
    times = np.linspace(0,1000,pts)
    
    # MW pulses
    m.params['AWG_1st_pi2_duration'] = m.params['4MHz_pi2_duration']
    m.params['AWG_1st_pi2_amp'] = m.params['4MHz_pi2_amp']
    m.params['AWG_1st_pi2_ssbmod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq'] + m.params['Ramsey_pi2_pulse_detuning'] 
    
    m.params['AWG_2nd_pi2_duration'] = m.params['4MHz_pi2_duration']
    m.params['AWG_2nd_pi2_amp'] = m.params['4MHz_pi2_amp']
    m.params['AWG_2nd_pi2_ssbmod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq'] + m.params['Ramsey_pi2_pulse_detuning'] 
    # Phases of 2nd pi2 pulse. -180 rotates back to ms=0, an extra 
    m.params['AWG_2nd_pi2_phases'] = - 180 + 360 * m.params['Phase_induced_frq_shift'] * times/1e9 

    # Waiting time 
    m.params['Waiting_times'] = times
    
    # for the autoanalysis
    m.params['sweep_name'] = 'tau (ns)'
    m.params['sweep_pts'] = times
    
    _finish(m)

    
def pi_vs_detuning(name):
    m = mbi_espin.ElectronRabi('DetuningSweep_'+name)
    _prepare(m)
    
    # measurement settings 
    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 2000
    
    # MW pulses
    detunings = np.linspace(-4e6, 4e6, pts)
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * (126 + 11) # np.linspace(0,500,pts) + 10
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.68
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq'] + detunings
    
    # for the autoanalysis
    m.params['sweep_name'] = 'Detuning (Hz)'
    m.params['sweep_pts'] = detunings
    
    _finish(m)
    
def CORPSE_vs_detuning(name):
    m = mbi_espin.CORPSETest('CORPSE_vs_detuning_'+name)
    _prepare(m)
    
    # measurement settings    
    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delay'] = 100
    
    #CORPSE pulse settings.
    m.params['AWG_uncond_CORPSE420_durations'] = np.ones(pts) * (253 + 42 + 11) # m.params['AWG_uncond_CORPSE420_duration']
    m.params['AWG_uncond_CORPSE300_durations'] = np.ones(pts) * (253 - 42 + 11) # m.params['AWG_uncond_CORPSE300_duration'] 
    m.params['AWG_uncond_CORPSE60_durations'] = np.ones(pts) * (57 + 11) # m.params['AWG_uncond_CORPSE60_duration']
    
    m.params['AWG_uncond_CORPSE420_amps'] = np.ones(pts) * 0.68 # amps # m.params['AWG_uncond_CORPSE60_amp'] 
    m.params['AWG_uncond_CORPSE300_amps'] = np.ones(pts) * 0.68 #amps
    m.params['AWG_uncond_CORPSE60_amps'] = np.ones(pts) * 0.68 # amps
    
    detunings = np.linspace(-4e6, 4e6, pts)
    m.params['AWG_uncond_CORPSE_mod_frqs'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq'] + detunings
 
    # for the autoanalysis
    m.params['sweep_name'] = 'Detuning (Hz)'
    m.params['sweep_pts'] = detunings
    
    _finish(m)
    