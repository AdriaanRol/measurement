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
cfg['protocols']['AdwinSSRO']['A_RO_amplitude'] = 0.
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
cfg['protocols']['AdwinSSRO']['repump_after_repetitions'] = 1
cfg['protocols']['AdwinSSRO']['yellow_repump_amplitude'] = 0
cfg['protocols']['AdwinSSRO']['green_off_voltage'] = 0.07
cfg['protocols']['AdwinSSRO']['A_off_voltage'] = -0.08
cfg['protocols']['AdwinSSRO']['Ex_off_voltage'] = 0

### Specific protocol settings ###

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
cfg['protocols']['sil9-default']['AdwinSSRO']['CR_duration'] = 100
cfg['protocols']['sil9-default']['AdwinSSRO']['CR_preselect'] = 10
cfg['protocols']['sil9-default']['AdwinSSRO']['CR_probe'] = 10
cfg['protocols']['sil9-default']['AdwinSSRO']['Ex_CR_amplitude'] = 20e-9
cfg['protocols']['sil9-default']['AdwinSSRO']['Ex_RO_amplitude'] = 10e-9
cfg['protocols']['sil9-default']['AdwinSSRO']['Ex_SP_amplitude'] = 0.
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


### save everything
cfg.save_all()
