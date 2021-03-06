"""
Script for BSM calibration
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

from measurement.scripts.mbi import mbi_calibration_funcs as mbi_cal
from measurement.scripts.mbi import pi2_calibration
reload(pi2_calibration)

from measurement.lib.measurement2.adwin_ssro import ssro

from measurement.scripts.mbi import CORPSE_calibration
reload(CORPSE_calibration)

from measurement.scripts.mbi import mbi_fidelity
reload(mbi_fidelity)
from measurement.scripts.mbi.mbi_fidelity import MBIFidelity

from measurement.scripts.teleportation.BSM import BSM_sequences as BSM_sequences
reload(BSM_sequences)

from measurement.scripts.teleportation.BSM import BSM_funcs as funcs
reload(funcs)


#############SSRO

def cal_ssro_teleportation(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name) 
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])  
    funcs.prepare(m)
    m.params['SSRO_repetitions'] = 5000
    m.params['SP_duration'] = 250 # we want to calibrate the RO, not the SP
    m.params['SSRO_duration'] = 50

     # ms = 1 calibration

    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')

    # ms = 1 calibration
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
    funcs.prepare(m)
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
### Calibration of the MBI fidelity readout pulses
### Calibration stage 1.5
def calibrate_MBI_fidelity_RO_pulses(name):
    m = pulsar_msmt.ElectronRabi('MBI_fidelity_RO_pulses_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    funcs.prepare(m)

    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 5000

    m.params['MBI_calibration_RO_pulse_duration'] = 8.3e-6
    m.params['MBI_calibration_RO_pulse_amplitude_sweep_vals'] = np.linspace(0.002,0.007,pts)
    m.params['MBI_calibration_RO_pulse_mod_frqs'] = \
        m.params['ms-1_cntr_frq'] - m.params['mw_frq'] + \
        np.array([-1,0,+1]) * m.params['N_HF_frq']

    m.params['MW_pulse_durations'] =  np.ones(pts) * m.params['MBI_calibration_RO_pulse_duration']  
    m.params['MW_pulse_amplitudes'] = m.params['MBI_calibration_RO_pulse_amplitude_sweep_vals']

    m.params['sweep_name'] = 'Pulse amplitudes (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10)

    for i,f in enumerate(m.params['MBI_calibration_RO_pulse_mod_frqs']):
        m.params['MW_pulse_frequency'] = f
        m.autoconfig()
        m.generate_sequence(upload=True)
        m.run()
        m.save('line-{}'.format(i))
        m.stop_sequence()
        qt.msleep(1)

    m.finish()

###########
### Calibration of the MBI fidelity
### Calibration stage 1.75
def calibrate_MBI_fidelity(name):
    m = MBIFidelity(name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    funcs.prepare(m)

    pts = 4
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 10000    

    # MW pulses
    m.params['max_MBI_attempts'] = 100
    m.params['N_randomize_duration'] = 50 # This could still be optimized, 50 is a guess
    m.params['Ex_N_randomize_amplitude'] = 15e-9 # 10 nW is a guess, not optimized
    m.params['A_N_randomize_amplitude'] = 20e-9 # 10 nW is a guess, not optimized
    m.params['repump_N_randomize_amplitude'] = 0
    
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 2000e-9

    MIM1_AMP = 0.005182
    MI0_AMP = 0.005015
    MIP1_AMP = 0.005009
    m.params['MW_pulse_durations'] = np.ones(pts) * 8.3e-6 # the four readout pulse durations
    m.params['MW_pulse_amps'] = np.array([MIM1_AMP, MI0_AMP, MIP1_AMP, 0.]) # calibrated powers for equal-length pi-pulses

    # Assume for now that we're initializing into m_I = -1 (no other nuclear spins)
    f_m1 = m.params['AWG_MBI_MW_pulse_mod_frq']
    f_HF = m.params['N_HF_frq']

    m.params['MW_pulse_mod_frqs'] = f_m1 + np.array([0,1,2,5]) * f_HF

    # for the autoanalysis
    m.params['sweep_name'] = 'Readout transitions'
    m.params['sweep_pts'] = m.params['MW_pulse_mod_frqs']
    m.params['sweep_pt_names'] = ['$m_I = -1$', '$m_I = 0$', '$m_I = +1$', 'None']

    funcs.finish(m, debug=False, upload=UPLOAD)

###########
### Pulse calibrations
### Calibration stage 2
def cal_fast_rabi(name):
    m = pulsar_mbi_espin.ElectronRabi('cal_fast_rabi'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m)

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
    funcs.prepare(m)
    
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

def cal_fast_pi2(name):
    m = pi2_calibration.Pi2Calibration(
        'cal_fast_pi_over_2_'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m)    
    
    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 3000
    m.params['pts_awg'] = pts
    m.params['pts'] = 2*pts


    sweep_axis = np.linspace(0.65, 0.9, pts)
    # pulses
    m.params['pi2_sweep_amps'] = sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))
    
    funcs.finish(m, debug=False, upload=UPLOAD)

def cal_CORPSE_pi(name , mult=1):
    m = CORPSE_calibration.CORPSEPiCalibration(name+'_M=%d' % mult)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m)

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
    funcs.prepare(m)
    
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

def cal_pi2pi_pi_mI0(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_pi2pi_pi_mI0_'+name+'_M=%d' % mult)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI']) 
    funcs.prepare(m)
    
    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6
    
    # MBI is in mI = 0 here
    # some msmts use mod, others ssbmod (haven't found the mistake yet.) set both.
    m.params['AWG_MBI_MW_pulse_mod_frq'] = m.params['pi2pi_mI0_mod_frq']
    m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = m.params['pi2pi_mI0_mod_frq']

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
    m.params_lt1['RF_pulse_amps'] = np.ones(pts) * .55
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
                                               #but do not need a very a`ccurate number for this calibration
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
    m.calibrate_CORPSE_pi_phase_shift_or_e_time()

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

    m.params_lt1['evolution_times'] = 52.5e-6 + np.linspace(-400e-9,400e-9,pts)
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

    m.params['evolution_times'] = 52.5e-6 + np.linspace(-50e-9,50e-9,pts)
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

    m.test_BSM_with_LDE_element_calibrate_echo_time(basis='-Z')
    
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
    m.params['reps_per_ROsequence'] = 2000

    m.params_lt1['repump_after_MBI_amplitude'] = 0. #SP is in LDE element!! :)
    #H evolution time should be more than N pi/2 pulse duration = 28e-6
    m.params_lt1['H_evolution_times'] = 35.1e-6 + np.linspace(-200e-9,300e-9,pts) 
    m.params_lt1['H_phases'] = np.ones(pts) * m.params_lt1['H_phase']


    m.params_lt1['sweep_name'] = 'H evolution times'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_evolution_times'] * 1e6

    m.test_BSM_with_LDE_element_superposition_in()
    
    BSM_sequences.finish(m, debug=False, upload=UPLOAD)

### Calibration stage 9
def bsm_test_psi_contrast(name):
    m = BSM_sequences.TheRealBSM('TestBSM_PsiContrast_'+name)   
    BSM_sequences.prepare(m)

    m.repetitive_readout = True
    m.params_lt1['N_RO_repetitions'] = 2

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['H_phases'] = np.linspace(0,360,pts)

    m.params_lt1['sweep_name'] = 'H phase'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_phases']

    m.test_BSM_contrast(bs='psi')

    BSM_sequences.finish(m, debug=False, upload=UPLOAD)

def bsm_test_phi_contrast(name):
    m = BSM_sequences.TheRealBSM('TestBSM_PhiContrast_'+name)
    BSM_sequences.prepare(m)

    m.repetitive_readout = True
    m.params_lt1['N_RO_repetitions'] = 2

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['H_phases'] = np.linspace(0,360,pts)

    m.params_lt1['sweep_name'] = 'H phase'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_phases']

    m.test_BSM_contrast(bs='phi')

    BSM_sequences.finish(m, debug=False, upload=UPLOAD)


### master function
def run_calibrations(stage):

    if stage == 0:
        cal_ssro_teleportation(name)

    if stage == 1:        
        cal_slow_pi(name)

    if stage == 1.5:        
        calibrate_MBI_fidelity_RO_pulses(name)

    if stage == 1.75:        
        calibrate_MBI_fidelity(name)
    
    if stage == 2:
        #cal_fast_rabi(name)
        cal_fast_pi(name, mult=11)
        cal_CORPSE_pi(name, mult=11)
        cal_pi2pi_pi(name, mult=5)
        cal_pi2pi_pi_mI0(name, mult=5)

    if stage == 2.5:
        cal_fast_pi2(name)
    
    if stage == 3:
        #run_nmr_frq_scan(name) #for eg first time sil use
        run_nmr_rabi(name)

    if stage == 4:
        #bsm_calibrate_interpulsedelay(name) #for eg first time sil use
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

    if stage == 9:
        bsm_test_psi_contrast(name)
        bsm_test_phi_contrast(name)

SIL_NAME = 'hans-sil1'
SETUP = 'lt1'
name = SIL_NAME
UPLOAD=True

if __name__ == '__main__':
    #execfile('d:/measuring/measurement/scripts/'+SETUP+'_scripts/setup/msmt_params.py')
    #run_calibrations(0)
    #run_calibrations(1)
    #run_calibrations(1.5)
    #run_calibrations(1.75)
    #run_calibrations(2)
    #run_calibrations(2.5)
    # run_calibrations(3)
    #run_calibrations(4)
    #run_calibrations(5)
    #run_calibrations(6)
    #run_calibrations(7)
    run_calibrations(8)
    #run_calibrations(9)

    """

    #note on yellow: Yellow setting is in msmnt_params, params, BSM_funcs and BSM_sequences
    stage 0.0: ssro calibration (first execfile ssro/ssro_calibration.py for coarse)
    ### RO settings
                --> RO settings A_SP_duration, SSRO_duration, E_RO_amplitude
                --> MBI on LT1 'E_SP_duration', 'A_SP_amplitude'
    stage 0.5: dark ESR  (execfile espin/darkesr.py) 
            --> f_msm1_cntr_lt1  in parameters.py AND msmt_params.py
    stage 1: MBI: slow pulse 
            --> selective_pi_amp in parameters.py AND msmt_params.py
    stage 1.5: MBI: slow RO pulses for fidelity calibration
            --> three amplitudes in the function for stage 1.75
    stage 1.75: MBI: fidelity
            --> nothing, this is for statistics during the msmts and correction later
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
    stage 7: Hadamard phase, compensating for psi shift
            --> H_phase in parameters.py
    stage 8: Hadamard evolution time, compensating for phi shift
            --> H_evolution_time in parameters.py
    stage 9: test contrast of the BSM, incl N-RepRO;
            --> nothing, that's just a check

    # note: analyze all stages (except 0.x) with BSM_calibrations.py (imported as bsmcal)
    """
