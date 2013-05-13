import qt
import numpy as np

import sequence_ssro
reload(sequence_ssro)

import mbi
reload(mbi)

## These are the calibrations for SIL2.
# The first step is the darkesr, of which the centre frequency should be
# added in the parameters of mbi.py
# The pulse calibration uses a multiplicity of 5 to determine the
# duration or amplitude.
# To determine the fidelity of the pulses, use multiplicity 1
# Parameters should be stored in mbi.py


def darkesr(name):
    m = sequence_ssro.DarkESR(name, qt.instruments['adwin'], qt.instruments['AWG'])
    sequence_ssro._prepare(m)

    m.params['mw_power'] = 20
    m.params['mw_frq'] = 2.8e9
    m.params['ssbmod_frq_start'] = 40e6
    m.params['ssbmod_frq_stop'] = 48e6
    m.params['pts'] = 61
    m.params['pulse_length'] = 1500
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.01
    m.params['MW_pulse_mod_risetime'] = 2
    m.params['RO_duration'] = 25

    m.params['Ex_RO_amplitude'] = 2e-9
    m.params['CR_preselect'] = 40
    m.params['CR_probe'] = 40
 
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.

    m.params['sweep_name'] = 'MW frq (GHz)'
    m.params['sweep_pts'] = (np.linspace(m.params['ssbmod_frq_start'],
                    m.params['ssbmod_frq_stop'], m.params['pts']) + m.params['mw_frq'])*1e-9


    sequence_ssro._run(m)

def calslowpipulse(name):
    m = mbi.ElectronRabi('pi_calib_slow_'+name,#'pi_calib_slow', 
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 2500
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.009, 0.012, pts)
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 5
    m.params['MW_pulse_delay'] = 20000


    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']

    m.program_AWG = True

    mbi._run(m)

def calpi397ns(name):
    m = mbi.ElectronRabi('pi_calib_397ns_'+name, 
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 396
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.06, 0.1, pts)
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq'] 
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 5
    m.params['MW_pulse_delay'] = 20000

    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']

    mbi._run(m)

def calhardpipulse(name):
    m = mbi.ElectronRabi('pi_calib_hardpulse_'+name,#'pi_calib_hardpulse',
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(55,75,pts)
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 5
    m.params['MW_pulse_delay'] = 20000

    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']
    
    mbi._run(m)

def calpi2pulse198ns(name):
    m = mbi.ElectronRabi('pi2_calib_198ns_'+name,#'pi2_calib_198p5ns', 
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 198
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.06, 0.1, pts)
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 6
    m.params['MW_pulse_delay'] = 100

    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']

    mbi._run(m)

def calhardpi2pulse(name):
    m = mbi.ElectronRabi('pi2_calib_hard_'+name, 
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(30,45,pts)
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 2
    m.params['MW_pulse_delay'] = 100


    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']

    mbi._run(m)

def calNpipulse(name):
    m = mbi.NMRSweep('CalNPipulse_'+name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    # Sweep
    m.params['pts'] = 8
    pts = m.params['pts']

    m.params['RF_pulse_len'] = np.linspace(75e3, 105e3, pts).astype(int)
    m.params['RF_pulse_amp'] = np.ones(pts) * 1.
    m.params['RF_frq'] = np.ones(pts) * 7.135e6

    m.params['wait_before_readout_reps'] = np.ones(pts)
    m.params['wait_before_readout_element'] = int(1e3)

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'RF pulse length (us)'
    m.params['sweep_pts'] = m.params['RF_pulse_len']/1e3

    m.program_AWG = True
    mbi._run(m)

def calCORPSE60(name):
    m = mbi.ElectronRabi('calib_CORPSE60_'+name, 
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(26,36,pts)
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 100

    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']

    mbi._run(m)

def calCORPSE300(name):
    m = mbi.ElectronRabi('calib_CORPSE300_'+name, 
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(92,102,pts)
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 100

    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']

    mbi._run(m)

def calCORPSE420(name):
    m = mbi.ElectronRabi('calib_CORPSE420_'+name, 
        qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(132,142,pts)
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 100

    m.params['sweep_name'] = 'MW pulse duration (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']

    mbi._run(m)

def corpse60sweepcal(name):
    m = mbi.CORPSETest(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    # Rabi    
    m.params['pts'] = 6#11
    pts = m.params['pts']
    
    #Durations CORPSE pulse.
    m.params['AWG_uncond_CORPSE420_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE420_duration'] #np.linspace(-5,+5,pts) + 
    m.params['AWG_uncond_CORPSE300_durations'] =np.ones(pts) * m.params['AWG_uncond_CORPSE300_duration']#  
    m.params['AWG_uncond_CORPSE60_durations'] = np.linspace(-5,+5,pts) + m.params['AWG_uncond_CORPSE60_duration']# + 25##np.ones(pts) * 28#  #  #
 
    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'duration CORPSE 60'
    m.params['sweep_pts'] =  m.params['AWG_uncond_CORPSE60_durations']

    m.program_AWG = True
    mbi._run(m)
### def corpsetest

def corpse300sweepcal(name):
    m = mbi.CORPSETest(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    # Rabi    
    m.params['pts'] = 11#11
    pts = m.params['pts']
    
    #m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = 40.793e6  # + 2.189e6

    m.params['AWG_uncond_CORPSE420_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE420_duration'] #np.linspace(-5,+5,pts) + 
    m.params['AWG_uncond_CORPSE300_durations'] = np.linspace(-5,+5,pts)+ m.params['AWG_uncond_CORPSE300_duration']#  #np.ones(pts) *q
    m.params['AWG_uncond_CORPSE60_durations'] = np.ones(pts) *m.params['AWG_uncond_CORPSE60_duration']#np.linspace(-5,+5,pts) + 25##np.ones(pts) * 28#  #  #

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'duration CORPSE 300'
    m.params['sweep_pts'] =  m.params['AWG_uncond_CORPSE300_durations']

    m.program_AWG = True
    mbi._run(m)
### def corpsetest

