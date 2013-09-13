"""
LT2 script for calibration
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
reload(pulsar_mbi_espin)

import CORPSE_calibration
reload(CORPSE_calibration)
from CORPSE_calibration import CORPSEPiCalibration

import mbi_espin_funcs as funcs
reload(funcs)



name = 'sil9'

### Calibration stage 1
def cal_slow_pi(name):
    m = pulsar_mbi_espin.ElectronRabi('cal_slow_pi_'+name)
    funcs.prepare(m)
    
    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 500
    m.params['pts'] = pts
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 1e-9
  
    # slow pi pulses
    m.params['MW_pulse_durations'] = np.linspace(0,5e-6,pts) + 5e-9
    m.params['MW_pulse_amps'] = np.ones(pts) * 0.03
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations'] * 1e9
    
    funcs.finish(m)

### Calibration stage 2
def cal_4mhz_rabi(name):
    m = pulsar_mbi_espin.ElectronRabi('cal_4mhz_rabi'+name)
    funcs.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 20e-9

    # MW pulses
    m.params['MW_pulse_durations'] = np.linspace(0,500e-9,pts) + 5e-9
    m.params['MW_pulse_amps'] = np.ones(pts) * 0.7
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations'] * 1e9
    
    funcs.finish(m)


### Calibration stage 3
def cal_4mhz_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_4MHz_pi_'+name+'_M=%d' % mult)
    funcs.prepare(m)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = 1e-9* (np.ones(pts) + 90)
    m.params['MW_pulse_amps'] = np.linspace(0.6,0.75,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

def cal_4mhz_pi2(name,  mult=1):
    m = pulsar_mbi_espin.ElectronRabi(
        'cal_4MHz_pi_over_2_'+name+'_M=%d' % mult)
    funcs.prepare(m)    
    
    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 2000
    m.params['pts'] = pts
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9
    
    # pulses
    m.params['MW_pulse_durations'] = 1e-9 * (np.ones(pts) * 45)
    m.params['MW_pulse_amps'] = np.linspace(0.65, 0.75, pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']
    
    funcs.finish(m)

def cal_CORPSE_pi(name):
    m = CORPSEPiCalibration(name)
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.6, 0.8, pts)
    m.params['multiplicity'] = 11
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    
    funcs.finish(m)

def cal_pi2pi_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_pi2pi_pi_'+name+'_M=%d' % mult)
    funcs.prepare(m)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = 1e-9 * (np.ones(pts) + 395)
    m.params['MW_pulse_amps'] = np.linspace(0.12,0.16,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

def cal_pi2pi_pi_len(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_pi2pi_pi_len_'+name+'_M=%d' % mult)
    funcs.prepare(m)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = 1e-9 * (np.linspace(-50,50,pts).astype(int) + 395)
    m.params['MW_pulse_amps'] = np.ones(pts)*0.137
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['f0']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse length (s)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations']

    funcs.finish(m)
    
def cal_hard_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_hard_pi_'+name+'_M=%d' % mult)
    funcs.prepare(m)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = 1e-9 * (np.ones(pts)*80)
    m.params['MW_pulse_amps'] = np.linspace(0.78,0.92,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)


### master function
def run_calibrations(stage):
    if stage == 1:        
        cal_slow_pi(name)

    if stage == 2:
        cal_pi2pi_pi(name, mult=1)
    
    if stage == 3:    
        cal_4mhz_rabi(name)
        #cal_4mhz_pi(name, mult=11)
    
    if stage == 4:
        cal_4mhz_pi2(name)
        #cal_CORPSE_pi(name)
        #cal_pi2pi_pi(name, mult=11)
        #cal_hard_pi(name, mult=15)


if __name__ == '__main__':
    run_calibrations(1)
    #run_calibrations(2)
    #run_calibrations(3)

