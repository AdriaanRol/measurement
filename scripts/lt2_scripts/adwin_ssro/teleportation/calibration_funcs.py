"""
LT2 script for calibration
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

#this is a CORPSE calibration based on electron Rabi.
import measurement.scripts.lt2_scripts.adwin_ssro.teleportation.CORPSE_calibration as CORPSE_calibration
reload(CORPSE_calibration)
from measurement.scripts.lt2_scripts.adwin_ssro.teleportation.CORPSE_calibration import CORPSEPiCalibration
from measurement.scripts.lt2_scripts.adwin_ssro.teleportation.CORPSE_calibration import CORPSEPi2Calibration

from measurement.scripts.lt2_scripts.adwin_ssro import espin_funcs as funcs
reload(funcs)

name = 'hans-sil4'


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

# Calibration stage 2
def cal_CORPSE_pi(name):
    m = CORPSEPiCalibration(name+'M=11')
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.5, 0.6, pts)#
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
    m.params['CORPSE_pi2_sweep_amps'] = np.linspace(0.5, 0.6, pts)#
    m.params['multiplicity'] = 1
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_element_length'] = 1e-6

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE pi/2 amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi2_sweep_amps']  

    funcs.finish(m)

def cal_CORPSE_pi2_alternative(name, M):
    m = CORPSEPi2Calibration(name+str(M))
    funcs.prepare(m)
    ### Currently does not work, because element length fill-up causes dephasing. 
    #Calibration method abandoned for now

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['CORPSE_pi2_sweep_amps'] = np.linspace(0.5, 0.6, pts)#
    m.params['multiplicity'] = M
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_element_length'] = 10e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE pi/2 amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi2_sweep_amps']  

    funcs.finish(m)


# Fidelities
def find_CORPSE_fidelity(name):
    m = CORPSEPiCalibration(name+'fidelity_M=1')
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.ones(pts)*m.params['CORPSE_pi_amp']#np.linspace(0.54, 0.66, pts)#
    m.params['multiplicity'] = 1
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_element_length'] = 1e-6
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = ''
    m.params['sweep_pts'] = np.arange(pts) # m.params['CORPSE_pi_sweep_amps']  

    funcs.finish(m)
   
def find_CORPSE_pi2_fidelity(name):
    m = CORPSEPi2Calibration(name+'fidelity_M=1')
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['CORPSE_pi2_sweep_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']#np.linspace(0.54, 0.66, pts)#
    m.params['multiplicity'] = 1
    name = name + 'M={}'.format(m.params['multiplicity'])
    m.params['delay_element_length'] = 1e-6
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = ''
    m.params['sweep_pts'] = np.arange(pts) # m.params['CORPSE_pi_sweep_amps']  

    funcs.finish(m)
   

### master function
def run_calibrations(stage):  
    if stage == 1:
        cal_8mhz_rabi(name)
    
    if stage == 2:
        print 'Cal CORPSE pi'
        cal_CORPSE_pi(name)
        print 'Cal CORPSE pi/2'
        cal_CORPSE_pi2(name)
        #cal_CORPSE_pi2_alternative(name, M=2)
        #cal_CORPSE_pi2_alternative(name, M=4)



if __name__ == '__main__':
    # stage 0: dark esr

    # stage 1: find CORPSE Rabi frequency
    #run_calibrations(1)

    # stage 2: calibrate CORPSE pi and pi2 pulses
    run_calibrations(2)

    #find_CORPSE_fidelity(name)
    #find_CORPSE_pi2_fidelity(name)
