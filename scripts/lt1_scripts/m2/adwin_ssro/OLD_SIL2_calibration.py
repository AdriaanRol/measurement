import qt
import numpy as np
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import measurement.lib.config.awgchannels as awgcfg

import mbi
reload(mbi)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import sequence

# set the static variables for LT1
ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt1_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['Velocity2AOM']
ssro.AdwinSSRO.A_aom = qt.instruments['Velocity1AOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']

sequence.SequenceSSRO.awg = qt.instruments['AWG']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100']
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['mw', 'rf', 'adwin']


## These are the calibrations for SIL2.
# The first step is the darkesr, of which the centre frequency should be
# added in the parameters of mbi.py
# The pulse calibration uses a multiplicity of 5 to determine the
# duration or amplitude.
# To determine the fidelity of the pulses, use multiplicity 1
# Parameters should be stored in mbi.py


def darkesr(name):
    m = sequence.DarkESR(name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
   
    m.params['mw_power'] = 20
    m.params['mw_frq'] = 2.8e9
    m.params['ssbmod_frq_start'] = 40e6
    m.params['ssbmod_frq_stop'] = 48e6
    m.params['pts'] = 61
    m.params['pulse_length'] = 1500
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.01
    m.params['MW_pulse_mod_risetime'] = 2

    m.autoconfig()
    m.generate_sequence()
    m.run()
    m.save()
    m.finish()  
    


def calslowpipulse(name):
    m = mbi.ElectronRabi('pi_calib_slow_'+name,
        qt.instruments['adwin'], qt.instruments['AWG'])
       
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    pts = 8
    m.params['pts'] = pts
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 2500
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(0.009, 0.012, pts)
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicity'] = 5
    
    m.params['sweep_name'] = 'MW pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_amps']
    
    m.setup()
    m.autoconfig()
    m.generate_sequence()
    m.run()
    m.save()
    m.finish()  

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

