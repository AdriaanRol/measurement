"""
Script for BSM calibration
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

from measurement.scripts.mbi import mbi_calibration_funcs as mbi_cal

from measurement.scripts.mbi import CORPSE_calibration
reload(CORPSE_calibration)
from measurement.scripts.mbi.CORPSE_calibration import CORPSEPiCalibration

from measurement.scripts.teleportation.BSM import BSM_sequences_copy as BSM_sequences
reload(BSM_sequences)

from measurement.scripts.mbi import mbi_funcs as funcs
reload(funcs)

###########
### Calibration for MBI
### Calibration stage 1
def cal_slow_pi(name):
    m = pulsar_mbi_espin.ElectronRabi('cal_slow_pi_'+name)
    funcs.prepare(m, SIL_NAME)
    
    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 500
    m.params['pts'] = pts
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 1e-9
  
    # slow pi pulses
    m.params['MW_pulse_durations'] = np.linspace(0,5e-6,pts) + 5e-9
    m.params['MW_pulse_amps'] = np.ones(pts) * 0.011
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations'] * 1e9
    
    funcs.finish(m)

###########
### Pulse calibrations
### Calibration stage 2
def cal_fast_rabi(name):
    m = pulsar_mbi_espin.ElectronRabi('cal_fast_rabi'+name)
    funcs.prepare(m, SIL_NAME)

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 20e-9

    # MW pulses
    m.params['MW_pulse_durations'] = np.linspace(0,500e-9,pts) + 5e-9
    m.params['MW_pulse_amps'] = np.ones(pts) * 0.4
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations'] * 1e9
    
    funcs.finish(m)

def cal_fast_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_fast_pi_'+name+'_M=%d' % mult)
    funcs.prepare(m, SIL_NAME)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = 1e-9* (np.ones(pts) + 61)
    m.params['MW_pulse_amps'] = np.linspace(0.7,0.9,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

def cal_fast_pi2(name,  mult=1):
    m = pulsar_mbi_espin.ElectronRabi(
        'cal_fast_pi_over_2_'+name+'_M=%d' % mult)
    funcs.prepare(m, SIL_NAME)    
    
    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 2000
    m.params['pts'] = pts
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9
    
    # pulses
    m.params['MW_pulse_durations'] = 1e-9 * (np.ones(pts) * 32)
    m.params['MW_pulse_amps'] = np.linspace(0.7, 0.9, pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']
    
    funcs.finish(m)

def cal_CORPSE_pi(name, yellow):
    m = CORPSEPiCalibration(name)
    funcs.prepare(m,SIL_NAME,yellow)

    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.32, 0.4, pts)
    m.params['multiplicity'] = 11
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    
    funcs.finish(m)

def cal_pi2pi_pi(name, yellow, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_pi2pi_pi_'+name+'_M=%d' % mult)
    funcs.prepare(m,SIL_NAME,yellow)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * 396e-9
    m.params['MW_pulse_amps'] = np.linspace(0.07,0.095,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

##########
### BSM sequences based calibrations
###########
### nitrogen Rabi based calibration
### Calibration stage 3
def run_nmr_rabi(name):
    m = BSM_sequences.NRabiMsmt('Nuclear_rabi_'+name) # BSM.ElectronRabiMsmt(name)
    BSM_sequences.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params_lt1['RF_pulse_multiplicities'] = np.ones(pts).astype(int) * 1
    m.params_lt1['RF_pulse_delays'] = np.ones(pts) * 1e-6

    # MW pulses
    m.params_lt1['RF_pulse_durations'] = np.linspace(1e-6, 201e-6, pts)
    m.params_lt1['RF_pulse_amps'] = np.ones(pts) * 1
    m.params_lt1['RF_pulse_frqs'] = np.ones(pts) * m.params_lt1['N_0-1_splitting_ms-1']

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'RF duration (us)'
    m.params_lt1['sweep_pts'] = m.params_lt1['RF_pulse_durations'] * 1e6
    
    BSM_sequences.finish(m, debug=False, upload=True)

### Calibration stage 4
def bsm_calibrate_CORPSE_pi_phase_shift(name):
    m = BSM_sequences.TheRealBSM('CalibrateCORPSEPiPhase_51us'+name)
    BSM_sequences.prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['CORPSE_pi_phase_shifts'] = np.linspace(0,180,pts)
    m.params_lt1['interpulse_delay'] = 50.9e-6
    m.calibrate_CORPSE_pi_phase_shift()

    # for the autoanalysis
    m.param_lt1s['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params_lt1['sweep_pts'] = m.params_lt1['CORPSE_pi_phase_shifts']

    BSM_sequences.finish(m, debug=False, upload=True)


def bsm_calibrate_CORPSE_pi_phase_shift_small_range(name):
    m = BSM_sequences.TheRealBSM('CalibrateCORPSEPiPhase_small_range_50p9us'+name)
    BSM_sequences.prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['CORPSE_pi_phase_shifts'] = 107 + np.linspace(-40,40,pts)
    m.params_lt1['interpulse_delay'] = 50.9e-6
    m.calibrate_CORPSE_pi_phase_shift()

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params_lt1['sweep_pts'] = m.params_lt1['CORPSE_pi_phase_shifts']

    BSM_sequences.finish(m, debug=False, upload=True)

### Calibration stage 5
def bsm_calibrate_UNROT_X_timing(name):
    m = BSM_sequences.TheRealBSM('Calibrate_UNROT_X_timing'+name)
    BSM_sequences.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['evolution_times'] = 50.9e-6 + np.linspace(-400e-9,400e-9,pts)
    m.calibrate_UNROT_X_timing(eigenstate='-1')

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'evolution time (us)'
    m.params_lt1['sweep_pts'] = m.params_lt1['evolution_times'] * 1e6

    BSM_sequences.finish(m, debug=False, upload=True)

def bsm_calibrate_UNROT_X_timing_small_range(name):
    m = BSM_sequences.TheRealBSM('Calibrate_UNROT_X_timing_small_range'+name)
    BSM_sequences.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['evolution_times'] = 51.089e-6 + np.linspace(-50e-9,50e-9,pts)
    m.calibrate_UNROT_X_timing(eigenstate='-1')

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (us)'
    m.params['sweep_pts'] = m.params['evolution_times'] * 1e6

    BSM_sequences.finish(m, debug=False, upload=True)

##########
### LDE element based calibrations
###########
### Calibration stage 6
def bsm_test_BSM_with_LDE_superposition_in_calibrate_echo_time(name):
    m = BSM_sequences.TheRealBSM('TestBSM_LDE_calibrate_echo'+name)
    BSM_sequences.prepare(m)
    
    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['repump_after_MBI_amplitude'] = 0. #SP is in LDE element!! :)

    # sweep pts
    m.params_lt1['echo_times_after_LDE'] = np.linspace(-2e-6,2e-6,pts)

    m.params_lt1['sweep_name'] = 'echo times after LDE'
    m.params_lt1['sweep_pts'] = m.params_lt1['echo_times_after_LDE'] /1e-9

    m.test_BSM_with_LDE_element_calibrate_echo_time()
    
    BSM_sequences.finish(m, debug=False, upload=True)    

### Calibration stage 7
def bsm_test_BSM_with_LDE_superposition_in_sweep_H_phase(name):
    m = BSM_sequences.TheRealBSM('TestBSM_LDE_calibrate_H_phase_'+name)
    BSM_sequences.prepare(m)
    
    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['repump_after_MBI_amplitude'] = 0. #SP is in LDE element!! :)
    # a random value (but more than N pi2 pulse duration) for H ev times
    # does not influence calibrated H phase from psi+-. 
    m.params_lt1['H_evolution_times'] = np.ones(pts) * 26e-6 #np.ones(pts) * m.params_lt1['pi2_evolution_time']
    m.params_lt1['H_phases'] = np.linspace(0,360,pts) 

    m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

    m.test_BSM_with_LDE_element_superposition_in()
    
    BSM_sequences.finish(m, debug=False, upload=True)    

### Calibration stage 8
def bsm_test_BSM_with_LDE_superposition_in_sweep_H_ev_time(name):
    m = BSM_sequences.TheRealBSM('TestBSM_LDE_calibrate_H_ev_time_'+name)
    BSM_sequences.prepare(m)
    
    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['repump_after_MBI_amplitude'] = 0. #SP is in LDE element!! :)
    #H evolution time should be more than N pi/2 pulse duration = 24e-6
    m.params_lt1['H_evolution_times'] = 26e-6 + np.linspace(-200e-9,300e-9,pts) 
    m.params_lt1['H_phases'] = np.ones(pts) * m.params_lt1['H_phase']


    m.params_lt1['sweep_name'] = 'H evolution times'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_evolution_times'] 

    m.test_BSM_with_LDE_element_superposition_in()
    
    BSM_sequences.finish(m, debug=False, upload=True)    


### master function
def run_calibrations(stage, yellow):
    if stage == 1:        
        cal_slow_pi(name)
    
    if stage == 2:
        #cal_fast_rabi(name)
        cal_fast_pi(name, mult=11)
        cal_fast_pi2(name)
        cal_CORPSE_pi(name, yellow)
        cal_pi2pi_pi(name, yellow, mult=5)
        #cal_pi2pi_pi_mI0(name, yellow, mult=5)
    
    if stage == 3:
        #run_nmr_frq_scan(name) #not every time!
        run_nmr_rabi(name)

    if stage == 4:
        #bsm_calibrate_CORPSE_pi_phase_shift(name)
        bsm_calibrate_CORPSE_pi_phase_shift_small_range(name)

    if stage == 5:
        bsm_calibrate_UNROT_X_timing(name)
        #bsm_calibrate_UNROT_X_timing_small_range(name)

    if stage == 6:
        bsm_test_BSM_with_LDE_superposition_in_calibrate_echo_time(name)

    if stage == 7:
        bsm_test_BSM_with_LDE_superposition_in_sweep_H_phase(name)

    if stage == 8:
        bsm_test_BSM_with_LDE_superposition_in_sweep_H_ev_time(name)

SIL_NAME = 'hans-sil4'
SETUP = 'lt1'
name = SIL_NAME

if __name__ == '__main__':
    execfile('d:/measuring/measurement/scripts/'+SETUP+'_scripts/setup/msmt_params.py')
    #run_calibrations(1, yellow=False)
    #run_calibrations(2, yellow=False)
    #run_calibrations(3, yellow=False)
    #run_calibrations(4, yellow=False)
    #run_calibrations(5, yellow=False)
    run_calibrations(6, yellow=False)
    #run_calibrations(7, yellow=False)
    #run_calibrations(8, yellow=False)

    """
    stage 0.0: ssro calibration (execfile ssro/ssro_calibration.py)
    stage 0.5: dark ESR  (execfile espin/darkesr.py) 
            --> f_msm1_cntr_lt1  in parameters.py AND msmt_params.py
    stage 1: MBI: slow pulse 
            --> selective_pi_amp in parameters.py AND msmt_params.py
    stage 2: pulses: fast pi pulse, fast pi/2 pulse, CORPSE, pi-2pi pulse on mI=-1 
            --> fast_pi_amp, fast_pi2_amp, CORPSE_pi_amp, pi2pi_mIm1_amp in parameters.py
    stage 3: N RF pulse durations
            --> N_pi_duration in parameters.py
    stage 4: CORPSE phase shift
            --> CORPSE_pi_phase_shift in parameters.py
    stage 5: UNROT evolution time
            --> pi2_evolution_time in parameters.py
    stage 6: LDE - BSM echo time
            --> echo_time_after_LDE in parameters.py
    stage 7: Hadamard phase, compensating for psi shift (10)
            --> H_phase in parameters.py
    stage 8: Hadamard evolution time, compensating for phi shift (11)
            --> H_evolution_time in parameters.py
    # note: analyze all stages with BSM_calibrations.py (imported as bsmcal)
    """
