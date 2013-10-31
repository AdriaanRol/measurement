"""
Calibration functions for the dynamical decoupling used in teleportation
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

#this is a CORPSE calibration based on electron Rabi.
import measurement.scripts.espin.calibrate_CORPSE as CORPSE_calibration
reload(CORPSE_calibration)
from measurement.scripts.espin.calibrate_CORPSE import CORPSEPiCalibration
from measurement.scripts.espin.calibrate_CORPSE import CORPSECalibration

from measurement.scripts.teleportation.DD import dd_measurements as dd_msmt
reload(dd_msmt)

import DD_funcs as funcs
reload(funcs)

name = 'sil10'

###############
##### Pulse calibration
##### Calibration stage 1
def cal_CORPSE_pi(name):
    m = CORPSEPiCalibration(name+'M=11')
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.37, 0.44, pts)
    m.params['multiplicity'] = 5
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']  

    funcs.finish(m, upload = True, debug = False)

# def cal_CORPSE_pi2(name):
#     m = CORPSECalibration(name+'M=1')
#     funcs.prepare(m)

#     pts = 11
#     m.params['pts'] = pts
#     m.params['repetitions'] = 1000
#     m.params['wait_for_AWG_done'] = 1

#     m.params['CORPSE_mod_frq'] = m.params['CORPSE_pi2_mod_frq']


#     # sweep params
#     m.params['CORPSE_sweep_amps'] = np.linspace(0.42, 0.50, pts)#
#     m.params['effective_rotation_angles'] = np.ones(pts) * 90
#     m.params['multiplicity'] = 1
#     name = name + 'M={}'.format(m.params['multiplicity'])
#     m.params['delay_element_length'] = 1e-6

#     # for the autoanalysis
#     m.params['sweep_name'] = 'CORPSE pi/2 amplitude (V)'
#     m.params['sweep_pts'] = m.params['CORPSE_sweep_amps']  

#     funcs.finish(m, upload = True, debug = False)

def cal_CORPSE_rotation_angle(name):
    m = CORPSECalibration(name+'M=1')
    funcs.prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # fixed params
    m.params['CORPSE_mod_frq'] = m.params['CORPSE_pi_mod_frq']
    m.params['CORPSE_sweep_amps'] = np.ones(pts) * m.params['CORPSE_amp']#
    
    # sweep params
    m.params['CORPSE_effective_rotation_angles'] = np.linspace(0,3*360,pts)
    m.params['multiplicity'] = 1
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_element_length'] = 1e-6

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE effective rotation angle'
    m.params['sweep_pts'] = m.params['CORPSE_effective_rotation_angles']  

    funcs.finish(m, upload = True, debug = False)


def dd_calibrate_C13_revival(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_first_revival')
    dd_msmt.prepare(m)
    m.params['dd_use_delay_reps'] = False

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1

    # sweep params
    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = 52.4e-6 + np.linspace(-2.5e-6, 2.5e-6, pts) #m.params_lt2['first_C_revival'] #

    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_free_ev_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = 2*m.params_lt2['free_evolution_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)


def dd_calibrate_T2(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_T2')
    dd_msmt.prepare(m)
    m.params['dd_use_delay_reps'] = True

    pts_per_revival = 11
    revivals=12
    pts=pts_per_revival*(revivals-1)
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1

    # sweep params
    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
  
    sweep_array=  m.params_lt2['first_C_revival'] + np.linspace(-1e-6, 1e-6, pts_per_revival)
    for r in range(2,revivals):
        sweep_array=np.append(sweep_array, \
            r * (m.params_lt2['first_C_revival'] \
            + m.params_lt2['CORPSE_pi2_wait_length'] \
            + m.params_lt2['dd_extra_t_between_pi_pulses'])
            + np.linspace(-1e-6, 1e-6, pts_per_revival))
    print sweep_array
    m.params_lt2['free_evolution_times'] = sweep_array

    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_free_ev_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = 2*m.params_lt2['free_evolution_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_spin_echo_time(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_LDE_spin_echo_time')
    dd_msmt.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1
    m.params['dd_use_delay_reps'] = False

    #suppress optical pulses here
    m.params_lt2['eom_aom_on'] = False
    m.params_lt2['eom_pulse_amplitude'] = -0.26

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.ones(pts) * m.params_lt2['first_C_revival']
    m.params_lt2['extra_ts_between_pulses'] = np.ones(pts) * 0 
   # m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    m.params_lt2['dd_spin_echo_times'] = np.linspace(-30e-9, 70e-9, pts)
    
    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'extra dd spin echo time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_spin_echo_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)


def dd_sweep_LDE_DD_XYX_t_between_pulse(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xyx_t_between_pulses')
    dd_msmt.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1
    m.params['dd_use_delay_reps'] = False

    #suppress optical pulses here
    m.params_lt2['eom_aom_on'] = False
    m.params_lt2['eom_pulse_amplitude'] = -0.26

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.ones(pts) * m.params_lt2['first_C_revival']
    m.params_lt2['dd_spin_echo_times'] = np.ones(pts) * m.params_lt2['dd_spin_echo_time']
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    m.params_lt2['extra_ts_between_pulses'] = 400e-9 + np.linspace(-2e-6,2e-6,pts)
    
    m.params_lt2['DD_pi_phases'] = [-90,0,-90]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'extra t between pi pulses (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['extra_ts_between_pulses'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_XYX_free_evolution_time(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xyx_fet_pi2phase_min90')
    dd_msmt.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['repetitions'] = 3000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['extra_ts_between_pulses'] = np.ones(pts) * m.params_lt2['dd_extra_t_between_pi_pulses']
    m.params_lt2['dd_spin_echo_times'] = np.ones(pts) * m.params_lt2['dd_spin_echo_time']
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    m.params_lt2['pi2_pulse_phase'] = -90
    m.params_lt2['free_evolution_times'] = np.linspace(-1e-6,1e-6,pts) + m.params_lt2['first_C_revival']

    m.params_lt2['DD_pi_phases'] = [90,0,90]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'free evolution time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_extra_t_between_pi_pulses'] * (len(m.params_lt2['DD_pi_phases']) -1) + \
        2 * len(m.params_lt2['DD_pi_phases']) * m.params_lt2['free_evolution_times'] / 1e-6 
         
    dd_msmt.finish(m,upload=True,debug=False)



### master function
def run_calibrations(stage):  
    if stage == 1:
        print 'Cal CORPSE pi'
        cal_CORPSE_pi(name)
    if stage == 1.5:
        print 'CORPSE vs effective angle'
    if stage == 2:
        dd_calibrate_C13_revival(name)
    if stage == 3:
        dd_sweep_LDE_spin_echo_time(name)
    if stage == 4:
        dd_sweep_LDE_DD_XYX_t_between_pulse(name)


if __name__ == '__main__':
    #execfile('d:/measuring/measurement/scripts/lt2_scripts/setup/msmt_params.py')
    #run_calibrations(1)
    #run_calibrations(1.5)
    #run_calibrations(2)
    #run_calibrations(3) 
    #run_calibrations(4) 
    #dd_calibrate_T2(name)
    

    """
    stage 0.0: SSRO calibration
    stage 0.5: dark ESR
            --> f_msm1_cntr_lt2 in parameters.py AND msmt_params.py
    stage 1: pulses: CORPSE pi 
            --> CORPSE_amp in parameters.py]
    stage 1.5: pulses: CORPSE vs angle. If (f-f0)/f0 < 0.005 -> happy. (f0 = 1/360) 
            --> CORPSE_amp in parameters.py
    stage 2: C13 revival time
            --> first_C_revival in parameters.py
    stage 3: LDE - DD spin echo time
            --> dd_spin_echo_time in parameters.py
    stage 4: time between pi pulses
            --> dd_extra_t_between_pi_pulses in paramters.py
    # note: analyze all stages with LT2_calibrations.py (imported as lt2cal)
    """
    
    
    
    
    
    
    
    
    