"""
LT2 script for calibration
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

#this is a CORPSE calibration based on electron Rabi.
import measurement.scripts.espin.calibrate_CORPSE as CORPSE_calibration
reload(CORPSE_calibration)
from measurement.scripts.espin.calibrate_CORPSE import CORPSEPiCalibration
from measurement.scripts.espin.calibrate_CORPSE import CORPSEPi2Calibration

from measurement.scripts.teleportation.DD import dd_measurements as dd_msmt
reload(dd_msmt)

from measurement.scripts.lt2_scripts.adwin_ssro import espin_funcs as funcs
reload(funcs)

name = 'sil9'


### Calibration stage 1
def cal_8mhz_rabi(name):
    m = pulsar_msmt.ElectronRabi('cal_8mhz_rabi'+name)
    funcs.prepare(m)

    m.params['pts'] = 21
    pts = m.params['pts'] 
    m.params['repetitions'] = 1000
    #m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    #m.params['MW_pulse_delays'] = np.ones(pts) * 20e-9

    # MW pulses
    m.params['MW_pulse_durations'] = np.linspace(0,250e-9,pts) + 5e-9
    m.params['MW_pulse_amplitudes'] = np.ones(pts) * 0.545
    m.params['MW_pulse_frequency'] = m.params['f0']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations'] * 1e9

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10)
    
    funcs.finish(m)

# Calibration stage 1
def cal_CORPSE_pi(name):
    m = CORPSEPiCalibration(name+'M=11')
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.39, 0.49, pts)
    m.params['multiplicity'] = 11
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']  

    funcs.finish(m)

def cal_CORPSE_pi2(name):
    m = CORPSEPi2Calibration(name+'M=1')
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['CORPSE_pi2_sweep_amps'] = np.linspace(0.42, 0.50, pts)#
    m.params['multiplicity'] = 1
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_element_length'] = 1e-6

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE pi/2 amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi2_sweep_amps']  

    funcs.finish(m)

def dd_calibrate_C13_revival(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_first_revival')
    dd_msmt.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1

    # sweep params
    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = 53.4e-6 + np.linspace(-2.5e-6, 2.5e-6, pts) #m.params_lt2['first_C_revival'] #

    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_free_ev_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = 2*m.params_lt2['free_evolution_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_bare_XY4(name):
    m = dd_msmt.DynamicalDecoupling('bare_xy4_noLDE')
    dd_msmt.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 5000
    m.params_lt2['wait_for_AWG_done'] = 1

    # sweep params
    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = m.params_lt2['first_C_revival'] + np.linspace(-1e-6, 1e-6, pts) # #

    m.params_lt2['DD_pi_phases'] = [0, -90, 0, -90]
    m.dd_sweep_free_ev_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_extra_t_between_pi_pulses'] * (len(m.params_lt2['DD_pi_phases']) -1) + \
        2 * len(m.params_lt2['DD_pi_phases']) * m.params_lt2['free_evolution_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_spin_echo_time(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_LDE_spin_echo_time')
    dd_msmt.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.ones(pts) * m.params_lt2['first_C_revival']
    m.params_lt2['extra_ts_between_pulses'] = np.ones(pts) * 0 
   # m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    m.params_lt2['dd_spin_echo_times'] = np.linspace(450e-9, 610e-9, pts)
    
    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'extra dd spin echo time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_spin_echo_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_free_ev_time_with_LDE(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_first_revival_w_LDE')
    dd_msmt.prepare(m)

    pts = 16
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params_lt2['wait_for_AWG_done'] = 1

    m.params_lt2['revival_nr'] = 1
    m.params_lt2['dd_spin_echo_times'] = np.ones(pts) * m.params_lt2['dd_spin_echo_time']

    # sweep params
    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.linspace(-3000e-9, 3000e-9, pts) + \
        m.params_lt2['first_C_revival'] * m.params_lt2['revival_nr']#

    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = 2*m.params_lt2['free_evolution_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_XY4_t_between_pulse(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xy4_t_between_pulses')
    dd_msmt.prepare(m)

    pts = 12
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.ones(pts) * m.params_lt2['first_C_revival']
    m.params_lt2['dd_spin_echo_times'] = np.ones(pts) * m.params_lt2['dd_spin_echo_time']
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    m.params_lt2['extra_ts_between_pulses'] = np.linspace(-30e-9,80e-9,pts)
    
    m.params_lt2['DD_pi_phases'] = [0,-90,0,-90]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'extra t between pi pulses (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['extra_ts_between_pulses'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_XY4_t_before_pi2(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xy4_t_before_pi2')
    dd_msmt.prepare(m)

    pts = 15
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params  
    m.params_lt2['extra_ts_before_pi2'] = np.linspace(-3e-6, 3e-6,pts)
    
    m.params_lt2['DD_pi_phases'] = [0,-90,0,-90]
    m.dd_sweep_LDE_DD_second_pi2()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'extra t before pi2 pulse (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['extra_ts_before_pi2'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_XY4_pi2_pulse_amp(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xy4_t_before_pi2')
    dd_msmt.prepare(m)

    pts = 16
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    m.params_lt2['extra_ts_before_pi2'] = np.ones(pts) * 0
    
    # sweep params  
    m.params_lt2['pi2_pulse_amps'] = np.linspace(-0.15, 0.15, pts) + m.params_lt2['CORPSE_pi2_amp']
    
    m.params_lt2['DD_pi_phases'] = [0,-90,0,-90]
    m.dd_sweep_LDE_DD_second_pi2()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'pi2 pulse amplitude (V)'
    m.params_lt2['sweep_pts'] = m.params_lt2['pi2_pulse_amps'] 

    dd_msmt.finish(m,upload=True,debug=False)



def dd_sweep_LDE_DD_XY4_spin_echo(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xy4_t_between_pulses')
    dd_msmt.prepare(m)

    pts = 15
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.ones(pts) * m.params_lt2['first_C_revival']
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    m.params_lt2['extra_ts_between_pulses'] = np.ones(pts) * m.params_lt2['dd_extra_t_between_pi_pulses']
    # sweep params
    
    m.params_lt2['dd_spin_echo_times'] = np.linspace(-40e-9,40e-9,pts) + m.params_lt2['dd_spin_echo_time']

    m.params_lt2['DD_pi_phases'] = [0,-90,0,-90]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'dd spin echo times (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_spin_echo_times'] / 1e-6  

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_XY4_free_evolution_time(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xy4_fet')
    dd_msmt.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['extra_ts_between_pulses'] = np.ones(pts) * m.params_lt2['dd_extra_t_between_pi_pulses']
    m.params_lt2['dd_spin_echo_times'] = np.ones(pts) * m.params_lt2['dd_spin_echo_time']
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    
    m.params_lt2['free_evolution_times'] = np.linspace(-1e-6,1e-6,pts) + m.params_lt2['first_C_revival']

    m.params_lt2['DD_pi_phases'] = [0,-90,0,-90]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'free evolution time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_extra_t_between_pi_pulses'] * (len(m.params_lt2['DD_pi_phases']) -1) + \
        2 * len(m.params_lt2['DD_pi_phases']) * m.params_lt2['free_evolution_times'] / 1e-6 
         

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_YXY_free_evolution_time(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_yxy_fet_pi2phase_min90')
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

    m.params_lt2['DD_pi_phases'] = [-90,0,-90]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'free evolution time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_extra_t_between_pi_pulses'] * (len(m.params_lt2['DD_pi_phases']) -1) + \
        2 * len(m.params_lt2['DD_pi_phases']) * m.params_lt2['free_evolution_times'] / 1e-6 
         
    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_XX_free_evolution_time(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xx_fet')
    dd_msmt.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['repetitions'] = 5000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['extra_ts_between_pulses'] = np.ones(pts) * m.params_lt2['dd_extra_t_between_pi_pulses']
    m.params_lt2['dd_spin_echo_times'] = np.ones(pts) * m.params_lt2['dd_spin_echo_time']
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    m.params_lt2['free_evolution_times'] = np.linspace(-1e-6,1e-6,pts) + m.params_lt2['first_C_revival']

    m.params_lt2['DD_pi_phases'] = [0,0]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'free evolution time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_extra_t_between_pi_pulses'] * (len(m.params_lt2['DD_pi_phases']) -1) + \
        2 * len(m.params_lt2['DD_pi_phases']) * m.params_lt2['free_evolution_times'] / 1e-6 

    dd_msmt.finish(m,upload=True,debug=False)

def dd_sweep_LDE_DD_XY4_free_evolution_time_t_coh(name):
    m = dd_msmt.DynamicalDecoupling('calibrate_xy4_fet')
    dd_msmt.prepare(m)

    pts = 51
    ppts = pts*4 + 5
    m.params['pts'] = pts
    m.params['repetitions'] = 1500
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['extra_ts_between_pulses'] = np.ones(ppts) * m.params_lt2['dd_extra_t_between_pi_pulses']
    m.params_lt2['dd_spin_echo_times'] = np.ones(ppts) * m.params_lt2['dd_spin_echo_time']
    #m.params_lt2['A_SP_amplitude'] = 0. #use LDE element SP. 
    
    # sweep params
    
    m.params_lt2['free_evolution_times1'] = np.linspace(-1e-6,1e-6,pts) + m.params_lt2['first_C_revival']
    m.params_lt2['free_evolution_times2'] = np.linspace(-1e-6,1e-6,pts) + 2 * m.params_lt2['first_C_revival']
    m.params_lt2['free_evolution_times3'] = np.linspace(-1e-6,1e-6,10) + 3 * m.params_lt2['first_C_revival']
    m.params_lt2['free_evolution_times4'] = np.linspace(-1e-6,1e-6,pts) + 4 * m.params_lt2['first_C_revival']

    m.params_lt2['free_evolution_times'] = np.linspace(-5e-6,5e-6,pts) + 3 * m.params_lt2['first_C_revival']

    #np.array( [ m.params_lt2['free_evolution_times1'] , m.params_lt2['free_evolution_times2'] ,
    #m.params_lt2['free_evolution_times3'], m.params_lt2['free_evolution_times4'] ]).flatten()

    print m.params_lt2['free_evolution_times']

    m.params_lt2['DD_pi_phases'] = [0,-90,0,-90]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'free evolution time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_extra_t_between_pi_pulses'] * (len(m.params_lt2['DD_pi_phases']) -1) + \
        2 * len(m.params_lt2['DD_pi_phases']) * m.params_lt2['free_evolution_times'] / 1e-6 
         

    dd_msmt.finish(m,upload=True,debug=False)


### master function
def run_calibrations(stage):  
    if stage == 1:
        #cal_8mhz_rabi(name)
        print 'Cal CORPSE pi'
        cal_CORPSE_pi(name)
        print 'Cal CORPSE pi/2'
        cal_CORPSE_pi2(name)
    if stage == 2:
        dd_calibrate_C13_revival(name)
    if stage == 3:
        dd_sweep_LDE_spin_echo_time(name)
    if stage == 4:
        #dd_sweep_free_ev_time_with_LDE(name)
        #dd_sweep_LDE_DD_XY4_t_between_pulse(name)
        #dd_sweep_LDE_DD_XY4_spin_echo(name)
        #dd_sweep_LDE_DD_XY4_t_before_pi2(name)
        #dd_sweep_LDE_DD_XY4_free_evolution_time(name)
        #dd_sweep_LDE_DD_XY4_free_evolution_time_t_coh(name)
        dd_sweep_LDE_DD_YXY_free_evolution_time(name)
        #dd_sweep_LDE_DD_XX_free_evolution_time(name)
        #dd_sweep_LDE_DD_XY4_pi2_pulse_amp(name)
        #dd_bare_XY4(name)



if __name__ == '__main__':
    execfile('d:/measuring/measurement/scripts/lt2_scripts/setup/msmt_params.py')
    #run_calibrations(1)
    #run_calibrations(2)
    #run_calibrations(3) 
    run_calibrations(4) 
    #find_CORPSE_fidelity(name)
    #find_CORPSE_pi2_fidelity(name)

    # stage 0.0: SSRO calibration
    # stage 0.5: dark ESR
    # stage 1: calibrate CORPSE pi and pi2 pulses