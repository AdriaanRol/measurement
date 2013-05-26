import types
import qt
cfg = qt.cfgman

### protocol settings ###

### General settings for AdwinSSRO
if type(cfg['protocols']['AdwinSSRO']) == types.NoneType:
	cfg['protocols']['AdwinSSRO'] = {}

cfg['protocols']['AdwinSSRO']['AWG_done_DI_channel'] = 16
cfg['protocols']['AdwinSSRO']['AWG_event_jump_DO_channel'] = 7
cfg['protocols']['AdwinSSRO']['AWG_start_DO_channel'] = 1
cfg['protocols']['AdwinSSRO']['A_laser_DAC_channel'] = 6
cfg['protocols']['AdwinSSRO']['Ex_laser_DAC_channel'] = 7
cfg['protocols']['AdwinSSRO']['counter_channel'] = 1
cfg['protocols']['AdwinSSRO']['cycle_duration'] = 300
cfg['protocols']['AdwinSSRO']['green_laser_DAC_channel'] = 4
cfg['protocols']['AdwinSSRO']['green_off_amplitude'] = 0.0
cfg['protocols']['AdwinSSRO']['green_repump_amplitude'] = 100e-6
cfg['protocols']['AdwinSSRO']['green_repump_duration'] = 10
cfg['protocols']['AdwinSSRO']['send_AWG_start'] = 0
cfg['protocols']['AdwinSSRO']['sequence_wait_time'] = 1
cfg['protocols']['AdwinSSRO']['wait_after_RO_pulse_duration'] = 3
cfg['protocols']['AdwinSSRO']['wait_after_pulse_duration'] = 3
cfg['protocols']['AdwinSSRO']['wait_for_AWG_done'] = 0
cfg['protocols']['AdwinSSRO']['green_off_voltage'] = 0
cfg['protocols']['AdwinSSRO']['Ex_off_voltage'] = 0
cfg['protocols']['AdwinSSRO']['A_off_voltage'] = 0
cfg['protocols']['AdwinSSRO']['repump_after_repetitions'] = 1
cfg['protocols']['AdwinSSRO']['yellow_repump_amplitude'] = 0

### General settings for AdwinSSRO+espin
if type(cfg['protocols']['AdwinSSRO+espin']) == types.NoneType:
	cfg['protocols']['AdwinSSRO+espin'] = {}
cfg['protocols']['AdwinSSRO+espin']['send_AWG_start'] = 1

### General settings for AdwinSSRO+MBI
if type(cfg['protocols']['AdwinSSRO+MBI']) == types.NoneType:
	cfg['protocols']['AdwinSSRO+MBI'] = {}

cfg['protocols']['AdwinSSRO+MBI']['AWG_wait_duration_before_MBI_MW_pulse'] = 1000
cfg['protocols']['AdwinSSRO+MBI']['AWG_wait_for_adwin_MBI_duration'] = np.array([15000], dtype=int)
cfg['protocols']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_duration'] = 2000
cfg['protocols']['AdwinSSRO+MBI']['AWG_wait_duration_before_shelving_pulse'] = 100
cfg['protocols']['AdwinSSRO+MBI']['nr_of_ROsequences'] = 1
cfg['protocols']['AdwinSSRO+MBI']['MW_pulse_mod_risetime'] = 2
cfg['protocols']['AdwinSSRO+MBI']['AWG_to_adwin_ttl_trigger_duration'] = 2000

### more specfic settings

### sil2 ###
if type(cfg['protocols']['sil2-default']) == types.NoneType:
	cfg['protocols']['sil2-default'] = {}

### sil2, AdwinSSRO ###
try:
	if type(cfg['protocols']['sil2-default']['AdwinSSRO']) == types.NoneType:
		cfg['protocols']['sil2-default']['AdwinSSRO'] = {}
except KeyError:
	cfg['protocols']['sil2-default']['AdwinSSRO'] = {}

cfg['protocols']['sil2-default']['AdwinSSRO']['A_CR_amplitude'] = 10e-9
cfg['protocols']['sil2-default']['AdwinSSRO']['A_RO_amplitude'] = 0.
cfg['protocols']['sil2-default']['AdwinSSRO']['A_SP_amplitude'] = 15e-9
cfg['protocols']['sil2-default']['AdwinSSRO']['CR_duration'] = 100
cfg['protocols']['sil2-default']['AdwinSSRO']['CR_preselect'] = 40
cfg['protocols']['sil2-default']['AdwinSSRO']['CR_probe'] = 40
cfg['protocols']['sil2-default']['AdwinSSRO']['Ex_CR_amplitude'] = 10e-9
cfg['protocols']['sil2-default']['AdwinSSRO']['Ex_RO_amplitude'] = 5e-9
cfg['protocols']['sil2-default']['AdwinSSRO']['Ex_SP_amplitude'] = 0.
cfg['protocols']['sil2-default']['AdwinSSRO']['SP_duration'] = 250
cfg['protocols']['sil2-default']['AdwinSSRO']['SP_filter_duration'] = 0
cfg['protocols']['sil2-default']['AdwinSSRO']['SSRO_duration'] = 50
cfg['protocols']['sil2-default']['AdwinSSRO']['SSRO_repetitions'] = 5000
cfg['protocols']['sil2-default']['AdwinSSRO']['SSRO_stop_after_first_photon'] = 0

### sil2, integrated SSRO
try:
	if type(cfg['protocols']['sil2-default']['AdwinSSRO-integrated']) == types.NoneType:
		cfg['protocols']['sil2-default']['AdwinSSRO-integrated'] = {}
except KeyError:
	cfg['protocols']['sil2-default']['AdwinSSRO-integrated'] = {}	
cfg['protocols']['sil2-default']['AdwinSSRO-integrated']['SSRO_duration'] = 15

### sil2, Adwin MBI ###
try:
	if type(cfg['protocols']['sil2-default']['AdwinSSRO+MBI']) == types.NoneType:
		cfg['protocols']['sil2-default']['AdwinSSRO+MBI'] = {}
except KeyError:
	cfg['protocols']['sil2-default']['AdwinSSRO+MBI'] = {}

cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['mw_frq'] = 2.80e9
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['mw_power'] = 20    
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['Ex_MBI_amplitude'] = 2e-9
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['Ex_SP_amplitude'] = 10e-9
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['MBI_duration'] = 5
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['MBI_steps'] = 1
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['MBI_threshold'] = 1
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['SP_E_duration'] = 100
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['A_SP_durations'] = np.array([50], dtype=int)
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['E_RO_durations'] = np.array([15], dtype=int)
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['A_SP_amplitudes'] = np.array([15e-9])
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['E_RO_amplitudes'] = np.array([5e-9])
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['send_AWG_start'] = np.array([1])
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['sequence_wait_time'] = np.array([0], dtype=int)
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_ssbmod_frq'] = 24.80e6
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_amp'] = 0.03
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_duration'] = 1852
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_shelving_pulse_duration'] = 72
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_shelving_pulse_amp'] = 0.884
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_wait_duration_before_MBI_MW_pulse'] = 50
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_wait_for_adwin_MBI_duration'] = np.array([15000], dtype=int)
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RO_MW_pulse_duration'] = 396
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RO_MW_pulse_ssbmod_frq'] = \
    cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_ssbmod_frq'] 
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RO_MW_pulse_amp'] = 0.093
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_MW_hard_pi2_pulse_duration']=40
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_uncond_CORPSE_amp_pi_duration']=66+10
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_uncond_CORPSE60_duration'] = 22+10
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_uncond_CORPSE300_duration'] = 110+10
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_uncond_CORPSE420_duration'] = 154+10
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_uncond_CORPSE_amp'] = 0.797#0.735
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_uncond_CORPSE_mod_frq'] = \
    cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_ssbmod_frq'] +(2.189e6/2)
    
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RF_pipulse_duration'] = 87e3
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RF_pipulse_amp'] = 1.
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RF_pipulse_frq'] = 7.135e6
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RF_p2pulse_duration'] = \
    cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RF_pipulse_duration']/2
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RF_p2pulse_amp'] = 1.
cfg['protocols']['sil2-default']['AdwinSSRO+MBI']['AWG_RF_p2pulse_frq'] = 7.135e6


cfg.save_all()
