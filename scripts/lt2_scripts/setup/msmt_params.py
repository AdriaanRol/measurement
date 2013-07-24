import types
import qt
cfg = qt.cfgman

cfg['samples']['current'] = 'sil9'
cfg['protocols']['current'] = 'sil9-default'

### sample settings ###
### sil 9 ###
if type(cfg['samples']['sil9']) == types.NoneType:
	cfg['samples']['sil9'] = {}
    
cfg['samples']['sil9']['N_HF_frq'] = 2.189e6
cfg['samples']['sil9']['ms-1_cntr_frq'] =  2.829141e9
cfg['samples']['sil9']['N_0-1_splitting_ms-1']= 7.13433e6 ###copied from sil2 lt1

### sil 15 ###




### protocol settings ###
### General settings for AdwinSSRO
if type(cfg['protocols']['AdwinSSRO']) == types.NoneType:
	cfg['protocols']['AdwinSSRO'] = {}

cfg['protocols']['AdwinSSRO']['AWG_done_DI_channel'] = 8
cfg['protocols']['AdwinSSRO']['AWG_event_jump_DO_channel'] = 6
cfg['protocols']['AdwinSSRO']['AWG_start_DO_channel'] = 1
# cfg['protocols']['AdwinSSRO']['A_laser_DAC_channel'] = 6
cfg['protocols']['AdwinSSRO']['A_RO_amplitude'] = 0.
# cfg['protocols']['AdwinSSRO']['Ex_laser_DAC_channel'] = 8
cfg['protocols']['AdwinSSRO']['counter_channel'] = 1
cfg['protocols']['AdwinSSRO']['cycle_duration'] = 300
#cfg['protocols']['AdwinSSRO']['green_laser_DAC_channel'] = 7
cfg['protocols']['AdwinSSRO']['green_repump_amplitude'] = 100e-6
cfg['protocols']['AdwinSSRO']['green_repump_duration'] = 10
cfg['protocols']['AdwinSSRO']['send_AWG_start'] = 0
cfg['protocols']['AdwinSSRO']['sequence_wait_time'] = 1
cfg['protocols']['AdwinSSRO']['wait_after_RO_pulse_duration'] = 3
cfg['protocols']['AdwinSSRO']['wait_after_pulse_duration'] = 3
cfg['protocols']['AdwinSSRO']['wait_for_AWG_done'] = 0
cfg['protocols']['AdwinSSRO']['repump_after_repetitions'] = 1
cfg['protocols']['AdwinSSRO']['yellow_repump_amplitude'] = 50e-9
cfg['protocols']['AdwinSSRO']['yellow_repump_duration'] = 500
cfg['protocols']['AdwinSSRO']['repump_off_voltage'] = 0.03
cfg['protocols']['AdwinSSRO']['A_off_voltage'] = 0
cfg['protocols']['AdwinSSRO']['Ex_off_voltage'] = 0

### General settings for AdwinSSRO+espin
if type(cfg['protocols']['AdwinSSRO+espin']) == types.NoneType:
	cfg['protocols']['AdwinSSRO+espin'] = {}
cfg['protocols']['AdwinSSRO+espin']['send_AWG_start'] = 1

### General settings for AdwinSSRO+MBI
if type(cfg['protocols']['AdwinSSRO+MBI']) == types.NoneType:
	cfg['protocols']['AdwinSSRO+MBI'] = {}
    
cfg['protocols']['AdwinSSRO+MBI']['AWG_wait_duration_before_MBI_MW_pulse'] = 1000

cfg['protocols']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_duration'] = 2000
cfg['protocols']['AdwinSSRO+MBI']['AWG_wait_duration_before_shelving_pulse'] = 10
cfg['protocols']['AdwinSSRO+MBI']['AWG_shelving_pulse_amp'] = 0.9
cfg['protocols']['AdwinSSRO+MBI']['nr_of_ROsequences'] = 1
cfg['protocols']['AdwinSSRO+MBI']['MW_pulse_mod_risetime'] = 10e-9
cfg['protocols']['AdwinSSRO+MBI']['AWG_to_adwin_ttl_trigger_duration'] = 2000e-9

### Specific protocol settings ###

### sil15 ###
### sil15, AdwinSSRO ###







### sil9 ###
if type(cfg['protocols']['sil9-default']) == types.NoneType:
	cfg['protocols']['sil9-default'] = {}

### sil9, AdwinSSRO ###
try:
	if type(cfg['protocols']['sil9-default']['AdwinSSRO']) == types.NoneType:
		cfg['protocols']['sil9-default']['AdwinSSRO'] = {}
except KeyError:
	cfg['protocols']['sil9-default']['AdwinSSRO'] = {}	

cfg['protocols']['sil9-default']['AdwinSSRO']['A_CR_amplitude'] = 20e-9
cfg['protocols']['sil9-default']['AdwinSSRO']['A_RO_amplitude'] = 0.
cfg['protocols']['sil9-default']['AdwinSSRO']['A_SP_amplitude'] = 20e-9
cfg['protocols']['sil9-default']['AdwinSSRO']['CR_duration'] = 200
cfg['protocols']['sil9-default']['AdwinSSRO']['CR_preselect'] = 15
cfg['protocols']['sil9-default']['AdwinSSRO']['CR_probe'] = 15
cfg['protocols']['sil9-default']['AdwinSSRO']['CR_repump'] = 0
cfg['protocols']['sil9-default']['AdwinSSRO']['Ex_CR_amplitude'] = 20e-9
cfg['protocols']['sil9-default']['AdwinSSRO']['Ex_RO_amplitude'] = 0e-9
cfg['protocols']['sil9-default']['AdwinSSRO']['Ex_SP_amplitude'] = 20e-9
cfg['protocols']['sil9-default']['AdwinSSRO']['SP_duration'] = 250
cfg['protocols']['sil9-default']['AdwinSSRO']['SP_filter_duration'] = 0
cfg['protocols']['sil9-default']['AdwinSSRO']['SSRO_duration'] = 50
cfg['protocols']['sil9-default']['AdwinSSRO']['SSRO_repetitions'] = 5000
cfg['protocols']['sil9-default']['AdwinSSRO']['SSRO_stop_after_first_photon'] = 0

### sil9, integrated SSRO
try:
	if type(cfg['protocols']['sil9-default']['AdwinSSRO-integrated']) == types.NoneType:
		cfg['protocols']['sil9-default']['AdwinSSRO-integrated'] = {}
except KeyError:
	cfg['protocols']['sil9-default']['AdwinSSRO-integrated'] = {}	
cfg['protocols']['sil9-default']['AdwinSSRO-integrated']['SSRO_duration'] = 40

### sil9, AdwinSSRO+MBI ###
try:
	if type(cfg['protocols']['sil9-default']['AdwinSSRO+MBI']) == types.NoneType:
		cfg['protocols']['sil9-default']['AdwinSSRO+MBI'] = {}
except KeyError:
	cfg['protocols']['sil9-default']['AdwinSSRO+MBI'] = {}
   
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['mw_frq'] = 2.80e9
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['mw_power'] = 20    
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['Ex_MBI_amplitude'] = 10e-9
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['Ex_SP_amplitude'] = 20e-9
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['MBI_duration'] = 8
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['MBI_steps'] = 1
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['MBI_threshold'] = 1
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['SP_E_duration'] = 100
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['A_SP_durations'] = np.array([100], dtype=int)
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['E_RO_durations'] = np.array([40], dtype=int)
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['A_SP_amplitudes'] = np.array([20e-9])
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['E_RO_amplitudes'] = np.array([10e-9])
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['send_AWG_start'] = np.array([1])
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['sequence_wait_time'] = np.array([0], dtype=int)
    
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_duration'] = 1728e-9
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_amp'] = 0.03
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['repump_after_MBI_duration'] = 100
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['repump_after_MBI_amplitude'] = 20e-9
cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['AWG_shelving_pulse_duration'] = 64

# MBI pulse
cfg.set('protocols/sil9-default/AdwinSSRO+MBI/AWG_wait_duration_before_MBI_MW_pulse',  50e-9)
cfg.set('protocols/sil9-default/AdwinSSRO+MBI/AWG_wait_for_adwin_MBI_duration', 18e-6)

#sil 9 pulses
###copied from sil2 lt1
   

tof = 0e-9#11e-9
f0 = cfg['samples']['sil9']['ms-1_cntr_frq'] - cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['mw_frq']
Nsplit = cfg['samples']['sil9']['N_HF_frq']
finit = f0 - Nsplit

cfg.set('protocols/sil9-default/pulses/t_offset', tof)
cfg.set('protocols/sil9-default/pulses/f0', f0)

cfg.set('protocols/sil9-default/pulses/4MHz_pi_duration', tof + 90e-9)
cfg.set('protocols/sil9-default/pulses/4MHz_pi_amp',  0.677)
cfg.set('protocols/sil9-default/pulses/4MHz_pi_mod_frq',  finit)

cfg.set('protocols/sil9-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
cfg.set('protocols/sil9-default/pulses/4MHz_pi2_amp',  0.698)
cfg.set('protocols/sil9-default/pulses/4MHz_pi2_mod_frq',  finit)

cfg.set('protocols/sil9-default/pulses/selective_pi_duration',  1728e-9)
cfg.set('protocols/sil9-default/pulses/selective_pi_amp',  0.03)
cfg.set('protocols/sil9-default/pulses/selective_pi_mod_frq',  finit)

cfg.set('protocols/sil9-default/pulses/hard_pi_duration',  80e-9)
cfg.set('protocols/sil9-default/pulses/hard_pi_amp',  0.809)
cfg.set('protocols/sil9-default/pulses/hard_pi_frq',  f0)

CORPSE_frq = 3.98e6
cfg.set('protocols/sil9-default/pulses/CORPSE_pi_60_duration', tof/2. + 1./CORPSE_frq/6.)
cfg.set('protocols/sil9-default/pulses/CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
cfg.set('protocols/sil9-default/pulses/CORPSE_pi_420_duration', tof/2. + 7./CORPSE_frq/6.)
cfg.set('protocols/sil9-default/pulses/CORPSE_pi_mod_frq', finit + Nsplit/2.)
cfg.set('protocols/sil9-default/pulses/CORPSE_pi_amp',  0.7)
cfg.set('protocols/sil9-default/pulses/CORPSE_pi_phase_shift', 65.2)

cfg.set('protocols/sil9-default/pulses/pi2pi_mIm1_duration', tof + 395e-9)
cfg.set('protocols/sil9-default/pulses/pi2pi_mIm1_amp', 0.143)
cfg.set('protocols/sil9-default/pulses/pi2pi_mIm1_mod_frq', finit)

### set some other pulses that determinine their values from the ones above
cfg.set('protocols/sil9-default/pulses/AWG_N_CNOT_pulse_duration', cfg.get('protocols/sil9-default/pulses/pi2pi_mIm1_duration'))
cfg.set('protocols/sil9-default/pulses/AWG_N_CNOT_pulse_amp', cfg.get('protocols/sil9-default/pulses/pi2pi_mIm1_amp'))
cfg.set('protocols/sil9-default/pulses/AWG_N_CNOT_pulse_mod_frq', cfg.get('protocols/sil9-default/pulses/pi2pi_mIm1_mod_frq'))

cfg.set('protocols/sil9-default/pulses/AWG_MBI_MW_pulse_mod_frq',  finit)
cfg.set('protocols/sil9-default/pulses/AWG_MBI_MW_pulse_amp', cfg.get('protocols/sil9-default/pulses/selective_pi_amp'))
cfg.set('protocols/sil9-default/pulses/AWG_MBI_MW_pulse_duration', cfg.get('protocols/sil9-default/pulses/selective_pi_duration'))

cfg.set('protocols/sil9-default/pulses/AWG_shelving_pulse_duration', cfg.get('protocols/sil9-default/pulses/4MHz_pi_duration'))
cfg.set('protocols/sil9-default/pulses/AWG_shelving_pulse_amp', cfg.get('protocols/sil9-default/pulses/4MHz_pi_amp'))

### Nitrogen pulses
cfg.set('protocols/sil9-default/pulses/N_pi_duration', 90.36e-6 + 1e-6)
cfg.set('protocols/sil9-default/pulses/N_pi_amp', 1)

cfg.set('protocols/sil9-default/pulses/N_pi2_duration', 90.36e-6/2. + 1e-6)
cfg.set('protocols/sil9-default/pulses/N_pi2_amp', 1)


### save everything
cfg.save_all()
