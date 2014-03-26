"""
Script for mbi calibrations
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
reload(pulsar_mbi_espin)

import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

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
    m.params['MW_pulse_durations'] = np.ones(pts) * 2500e-9
    m.params['MW_pulse_amps'] = np.linspace(0,0.05,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amp (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

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

### Calibration stage 3
def cal_fast_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_fast_pi_'+name+'_M=%d' % mult)
    #funcs.prepare(m, SIL_NAME)
    funcs.prepare(m)

    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6

    # hard pi pulses
    m.params['MW_pulse_durations'] = m.params['fast_pi_duration']*(np.ones(pts))
    m.params['MW_pulse_amps'] = np.linspace(0.8,0.9,pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

def cal_fast_pi2(name,  mult=1):
    m = pulsar_mbi_espin.ElectronRabi(
        'cal_fast_pi_over_2_'+name+'_M=%d' % mult)
    #funcs.prepare(m, SIL_NAME)
    funcs.prepare(m)

    # measurement settings
    pts = 11
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = pts
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9

    # pulses
    m.params['MW_pulse_durations'] = m.params['fast_pi2_duration']*(np.ones(pts))
    m.params['MW_pulse_amps'] = np.linspace(0.74, 0.82, pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

def cal_pi2pi_pi(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_pi2pi_pi_'+name+'_M=%d' % mult)
    funcs.prepare(m, SIL_NAME)

    # measurement settings
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int) * mult
    m.params['MW_pulse_delays'] = np.ones(pts) * 15e-6

    # hard pi pulses
    m.params['MW_pulse_durations'] = np.ones(pts) * 395e-9
    m.params['MW_pulse_amps'] = np.linspace(0.06, 0.12, pts)
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amps']

    funcs.finish(m)

def cal_pi2pi_pi_len(name, mult=1):
    m = pulsar_mbi_espin.ElectronRabiSplitMultElements(
        'cal_pi2pi_pi_len_'+name+'_M=%d' % mult)
    funcs.prepare(m, SIL_NAME)

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

### master function
def run_calibrations(stage):
    if stage == 1:
        cal_slow_pi(name)

    if stage == 2:
        #cal_fast_rabi(name)
        cal_fast_pi(name, mult=11)


    if stage == 3:
        cal_fast_pi2(name)
        #cal_pi2pi_pi(name, mult=11)
        #cal_pi2pi_pi_len(name, mult=11)


if __name__ == '__main__':

    cal_fast_pi2(SAMPLE_CFG,mult=10)
    #cal_pi2pi_pi(SAMPLE_CFG, 5)
