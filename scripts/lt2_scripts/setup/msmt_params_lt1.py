import types
import qt
cfg = qt.cfgman

cfg['samples']['current'] = 'sil4'
cfg['protocols']['current'] = 'sil4-default'


### sil 7 ###
branch='samples/sil4/'

f_msm1_cntr = 2.829e9 #not calibrated
f_msp1_cntr = 2.925871e9
N_frq = 7.13429e6#not calibrated
N_HF_frq = 2.193e6#not calibrated

cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
cfg.set(branch+'N_HF_frq', N_HF_frq)




### protocol settings ###
### General settings for AdwinSSRO
if type(cfg['protocols']['AdwinSSRO']) == types.NoneType:
	cfg['protocols']['AdwinSSRO'] = {}

cfg['protocols']['AdwinSSRO']['AWG_done_DI_channel'] = 16
cfg['protocols']['AdwinSSRO']['AWG_event_jump_DO_channel'] = 6
cfg['protocols']['AdwinSSRO']['AWG_start_DO_channel'] = 1
# cfg['protocols']['AdwinSSRO']['A_laser_DAC_channel'] = 6
cfg['protocols']['AdwinSSRO']['A_RO_amplitude'] = 0.
# cfg['protocols']['AdwinSSRO']['Ex_laser_DAC_channel'] = 8
cfg['protocols']['AdwinSSRO']['counter_channel'] = 1
cfg['protocols']['AdwinSSRO']['cycle_duration'] = 300
#cfg['protocols']['AdwinSSRO']['green_laser_DAC_channel'] = 7
cfg['protocols']['AdwinSSRO']['green_repump_amplitude'] = 150e-6
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
cfg['protocols']['AdwinSSRO+espin']['wait_for_AWG_done'] = 0

# ### General settings for AdwinSSRO+MBI
# if type(cfg['protocols']['AdwinSSRO+MBI']) == types.NoneType:
# 	cfg['protocols']['AdwinSSRO+MBI'] = {}
    
# cfg['protocols']['AdwinSSRO+MBI']['AWG_wait_duration_before_MBI_MW_pulse'] = 1000

# cfg['protocols']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_duration'] = 2000e-9
# cfg['protocols']['AdwinSSRO+MBI']['AWG_wait_duration_before_shelving_pulse'] = 10
# cfg['protocols']['AdwinSSRO+MBI']['AWG_shelving_pulse_amp'] = 0.9
# cfg['protocols']['AdwinSSRO+MBI']['nr_of_ROsequences'] = 1
# cfg['protocols']['AdwinSSRO+MBI']['MW_pulse_mod_risetime'] = 10e-9
# cfg['protocols']['AdwinSSRO+MBI']['AWG_to_adwin_ttl_trigger_duration'] = 2000e-9


### sil4 ###
### sil4, AdwinSSRO ###
branch='protocols/sil4-default/AdwinSSRO/'
cfg.set(branch+'A_CR_amplitude', 15e-9)
cfg.set(branch+'A_RO_amplitude' , 0)
cfg.set(branch+'A_SP_amplitude', 20e-9)
cfg.set(branch+'CR_duration' , 150)
cfg.set(branch+'CR_preselect', 8)
cfg.set(branch+'CR_probe', 2)
cfg.set(branch+'CR_repump', 1000)
cfg.set(branch+'Ex_CR_amplitude', 15e-9)
cfg.set(branch+'Ex_RO_amplitude', 20e-9)
cfg.set(branch+'Ex_SP_amplitude', 0e-9)
cfg.set(branch+'SP_duration', 250)
cfg.set(branch+'SP_filter_duration', 0)
cfg.set(branch+'SSRO_duration', 50)
cfg.set(branch+'SSRO_repetitions', 5000)
cfg.set(branch+'SSRO_stop_after_first_photon', 0)
cfg.set(branch+'repump_after_repetitions',1)
cfg.set(branch+'mw_frq',2.9e9)
cfg.set(branch+'mw_power',20)
cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

### sil4, AdwinSSRO integrated ###
branch='protocols/sil4-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 50)




### save everything
cfg.save_all()
