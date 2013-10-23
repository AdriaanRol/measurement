"""
Script for BSM calibration
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

from measurement.scripts.mbi import mbi_calibration_funcs as mbi_cal

from measurement.lib.measurement2.adwin_ssro import ssro

from measurement.scripts.mbi import CORPSE_calibration
reload(CORPSE_calibration)
from measurement.scripts.mbi.CORPSE_calibration import CORPSEPiCalibration

from measurement.scripts.teleportation.BSM import BSM_sequences as BSM_sequences
reload(BSM_sequences)

from measurement.scripts.teleportation.BSM import BSM_funcs as funcs
reload(funcs)







#############SSRO

def cal_ssro_teleportation(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name) 
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])  
    funcs.prepare(m, SIL_NAME)
    m.params['SSRO_repetitions'] = 5000

     # ms = 1 calibration
    m.params['SP_duration'] = 7#m.params['A_SP_duration']
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = m.params['E_SP_duration']
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] =  m.params['E_SP_amplitude']

    m.run()
    m.save('ms1')
    m.finish()



###########
### Calibration for MBI
### Calibration stage 1
def cal_slow_pi(name):
    m = pulsar_mbi_espin.ElectronRabi('cal_slow_pi_'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m, SIL_NAME)
    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 500
    m.params['pts'] = pts
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 1e-9
  
    # slow pi pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * 2500e-9
    m.params['MW_pulse_amps'] = np.linspace(0,0.03,pts) 
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amp (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']
    
    funcs.finish(m, debug=False, upload=UPLOAD)

###########
### Pulse calibrations
### Calibration stage 2
def cal_fast_rabi(name):
    m = pulsar_mbi_espin.ElectronRabi('cal_fast_rabi'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
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
    
    funcs.finish(m, debug=False, upload=UPLOAD)

def cal_fast_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_fast_pi_'+name+'_M=%d' % mult)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m, SIL_NAME)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['fast_pi_duration']
    m.params['MW_pulse_amps'] = np.linspace(0.7,0.9,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m, debug=False, upload=UPLOAD)

def cal_fast_pi2(name,  mult=1):
    m = pulsar_mbi_espin.ElectronRabi(
        'cal_fast_pi_over_2_'+name+'_M=%d' % mult)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m, SIL_NAME)    
    
    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 2000
    m.params['pts'] = pts
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9
    
    # pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['fast_pi2_duration']
    m.params['MW_pulse_amps'] = np.linspace(0.7, 0.9, pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']
    
    funcs.finish(m, debug=False, upload=UPLOAD)

def cal_CORPSE_pi(name , mult=1):
    m = CORPSEPiCalibration(name+'_M=%d' % mult)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m,SIL_NAME)

    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.49, 0.56, pts)
    m.params['multiplicity'] = mult
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    
    funcs.finish(m, debug=False, upload=UPLOAD)

def cal_pi2pi_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_pi2pi_pi_'+name+'_M=%d' % mult)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m,SIL_NAME)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # hard pi pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * 396e-9
    m.params['MW_pulse_amps'] = np.linspace(0.095,0.12,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
        
    # for the autoanalysis    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m, debug=False, upload=UPLOAD)

##########
### BSM sequences based calibrations
###########
### nitrogen Rabi based calibration
def run_nmr_frq_scan(name):
    m = BSM_sequences.NRabiMsmt('NMR_frq_scan_'+name) # BSM.ElectronRabiMsmt(name)
    BSM_sequences.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params_lt1['RF_pulse_multiplicities'] = np.ones(pts).astype(int) * 1
    m.params_lt1['RF_pulse_delays'] = np.ones(pts) * 1e-6

    # MW pulses
    m.params_lt1['RF_pulse_durations'] = np.ones(pts) * 70e-6
    m.params_lt1['RF_pulse_amps'] = np.ones(pts) * 1
    m.params_lt1['RF_pulse_frqs'] = np.linspace(7.12e6, 7.15e6, pts)

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'RF frequency (MHz)'
    m.params_lt1['sweep_pts'] = m.params_lt1['RF_pulse_frqs'] * 1e-6
    
    BSM_sequences.finish(m, debug=False, upload=UPLOAD)

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
    
    BSM_sequences.finish(m, debug=False, upload=UPLOAD)

### Calibration stage 4
def bsm_calibrate_CORPSE_pi_phase_shift(name):
    m = BSM_sequences.TheRealBSM('CalibrateCORPSEPiPhase'+name)
    BSM_sequences.prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['CORPSE_pi_phase_shifts'] = np.linspace(0,180,pts)
    m.params_lt1['interpulse_delays'] = np.ones(pts) * 52.5e-6 #this is the C13 revival, 
                                               #but do not need a very accurate number for this calibration
    m.calibrate_CORPSE_pi_phase_shift_or_e_time()

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params_lt1['sweep_pts'] = m.params_lt1['CORPSE_pi_phase_shifts']

    BSM_sequences.finish(m, debug=False, upload=True)

def bsm_calibrate_interpulsedelay(name):
    m = BSM_sequences.TheRealBSM('CalibrateCORPSEInterpulsedelay'+name)
    BSM_sequences.prepare(m)

    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['CORPSE_pi_phase_shifts'] = np.ones(pts) * m.params_lt1['CORPSE_pi_phase_shift']
    m.params_lt1['interpulse_delays'] = 52.5e-6 + np.linspace(-10e-6, 10e-6, pts) #this is the C13 revival, 
    m.calibrate_CORPSE_pi_phase_shift_or_e_time()

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'CORPSE interpulse delay (us)'
    m.params_lt1['sweep_pts'] = m.params_lt1['interpulse_delays'] * 1e6

    BSM_sequences.finish(m, debug=False, upload=UPLOAD)



def bsm_calibrate_CORPSE_pi_phase_shift_small_range(name):
    m = BSM_sequences.TheRealBSM('CalibrateCORPSEPiPhase_small_range'+name)
    BSM_sequences.prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['CORPSE_pi_phase_shifts'] = 107 + np.linspace(-40,40,pts)
    m.params_lt1['interpulse_delays'] = np.ones(pts) * 52.5e-6 #this is the C13 revival, 
                                               #but do not need an accurate number for this calibration 
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

    BSM_sequences.finish(m, debug=False, upload=UPLOAD)

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
    
    BSM_sequences.finish(m, debug=False, upload=UPLOAD)    

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
    #H evolution time should be more than N pi/2 pulse duration = 28e-6
    m.params_lt1['H_evolution_times'] = np.ones(pts) * 35e-6 #np.ones(pts) * m.params_lt1['pi2_evolution_time']
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
    #H evolution time should be more than N pi/2 pulse duration = 28e-6
    m.params_lt1['H_evolution_times'] = 35e-6 + np.linspace(-200e-9,300e-9,pts) 
    m.params_lt1['H_phases'] = np.ones(pts) * m.params_lt1['H_phase']


    m.params_lt1['sweep_name'] = 'H evolution times'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_evolution_times'] * 1e6

    m.test_BSM_with_LDE_element_superposition_in()
    
    BSM_sequences.finish(m, debug=False, upload=UPLOAD)    


### master function
def run_calibrations(stage):

    if stage == 0:
        cal_ssro_teleportation(name)

    if stage == 1:        
        cal_slow_pi(name)
    
    if stage == 2:
        #cal_fast_rabi(name)
        cal_fast_pi(name, mult=11)
        cal_fast_pi2(name)
        cal_CORPSE_pi(name, mult=11)
        cal_pi2pi_pi(name, mult=5)
        #cal_pi2pi_pi_mI0(name, mult=5)
    
    if stage == 3:
        #run_nmr_frq_scan(name) #for eg first time sil use
        run_nmr_rabi(name)

    if stage == 4:
        #bsm_calibrate_interpulsedelay(name) #for eg first time sil use
        bsm_calibrate_CORPSE_pi_phase_shift(name)
        #bsm_calibrate_CORPSE_pi_phase_shift_small_range(name)

    if stage == 5:
        bsm_calibrate_UNROT_X_timing(name)
        #bsm_calibrate_UNROT_X_timing_small_range(name)

    if stage == 6:
        bsm_test_BSM_with_LDE_superposition_in_calibrate_echo_time(name)

    if stage == 7:
        bsm_test_BSM_with_LDE_superposition_in_sweep_H_phase(name)

    if stage == 8:
        bsm_test_BSM_with_LDE_superposition_in_sweep_H_ev_time(name)

SIL_NAME = 'hans-sil1'
SETUP = 'lt1'
name = SIL_NAME
UPLOAD=True

if __name__ == '__main__':
    #execfile('d:/measuring/measurement/scripts/'+SETUP+'_scripts/setup/msmt_params.py')
    GreenAOM.set_power(0)
    #run_calibrations(0)
    #run_calibrations(1)
    #run_calibrations(2)
    #run_calibrations(3)
    #run_calibrations(4)
    #run_calibrations(5)
    #run_calibrations(6)
    #run_calibrations(7)
    run_calibrations(8)
    #cal_pi2pi_pi(name,
    """

    #note on yellow: Yellow setting is in msmnt_params, params, BSM_funcs and BSM_sequences
    stage 0.0: ssro calibration (first execfile ssro/ssro_calibration.py for coarse)
    ### RO settings
                --> RO settings A_SP_duration, SSRO1_duration, SSRO2_duration', E_RO_amplitude
                --> MBI on LT1 'E_SP_duration', 'A_SP_amplitude'
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
    # note: analyze all stages (except 0.x) with BSM_calibrations.py (imported as bsmcal)
    """
