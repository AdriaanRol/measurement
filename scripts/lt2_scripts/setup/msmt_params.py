import types
import qt
cfg = qt.cfgman

cfg['samples']['current'] = 'sil7'
cfg['protocols']['current'] = 'sil7-default'



# ### sil 15 ###
# branch='samples/sil15/'

# f_msm1_cntr = 2.828992e9
# f_msp1_cntr = 2.925693e9
# N_frq = 7.13429e6
# N_HF_frq = 2.193e6

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


# ### sil 1 ###
# branch='samples/sil1/'

# f_msm1_cntr = 2.829e9
# f_msp1_cntr = 2.925693e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)

### sil 7 ###
branch='samples/sil7/'

f_msm1_cntr = 2.829e9 #not calibrated
f_msp1_cntr = 2.925871e9
N_frq = 7.13429e6#not calibrated
N_HF_frq = 2.193e6#not calibrated

cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
cfg.set(branch+'N_HF_frq', N_HF_frq)


### sil 9 ###
branch='samples/sil9/'

f_msm1_cntr = 2.828980e9 
f_msp1_cntr = 2.925884e9 #not calibrated
N_frq = 7.13429e6 #not calibrated
N_HF_frq = 2.189e6 

cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
cfg.set(branch+'N_HF_frq', N_HF_frq)



### sil 11 ###
# branch='samples/sil11/'

# f_msm1_cntr = 2.829e9
# f_msp1_cntr = 2.926e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


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
cfg['protocols']['AdwinSSRO']['green_repump_amplitude'] = 300e-6
cfg['protocols']['AdwinSSRO']['green_repump_duration'] = 50
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

### Specific protocol settings ###

### sil15 ###
### sil15, AdwinSSRO ###
branch='protocols/sil15-default/AdwinSSRO/'
cfg.set(branch+'A_CR_amplitude', 20e-9)
cfg.set(branch+'A_RO_amplitude' , 0)
cfg.set(branch+'A_SP_amplitude', 20e-9)
cfg.set(branch+'CR_duration' , 100)
cfg.set(branch+'CR_preselect', 12)
cfg.set(branch+'CR_probe', 12)
cfg.set(branch+'CR_repump', 100)
cfg.set(branch+'Ex_CR_amplitude', 20e-9)
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

### sil15, AdwinSSRO integrated ###
branch='protocols/sil15-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 50)

### sil 15 pulses
f0 = cfg['samples']['sil15']['ms+1_cntr_frq'] - cfg['protocols']['sil15-default']['AdwinSSRO']['mw_frq']

branch='protocols/sil15-default/pulses/'
cfg.set(branch+'f0', f0)
cfg.set(branch+'8MHz_pi_duration', 63e-9)
cfg.set(branch+'8MHz_pi_amp',  0.677)
cfg.set(branch+'8MHz_pi_mod_frq',  f0)

# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

# cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
# cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
# cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)

CORPSE_frq = 8.035e6
cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_mod_frq', f0)
cfg.set(branch+'CORPSE_pi_amp',  0.605)

cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
cfg.set(branch+'CORPSE_pi2_amp',  0.639)

#for dynamical decoupling pulses:
cfg.set(branch+'first_C_revival', 53.75e-6)



### sil1 ###
### sil1, AdwinSSRO ###
branch='protocols/sil1-default/AdwinSSRO/'
cfg.set(branch+'A_CR_amplitude', 20e-9)
cfg.set(branch+'A_RO_amplitude' , 0)
cfg.set(branch+'A_SP_amplitude', 20e-9)
cfg.set(branch+'CR_duration' , 100)
cfg.set(branch+'CR_preselect', 12)
cfg.set(branch+'CR_probe', 12)
cfg.set(branch+'CR_repump', 100)
cfg.set(branch+'Ex_CR_amplitude', 20e-9)
cfg.set(branch+'Ex_RO_amplitude', 10e-9)
cfg.set(branch+'Ex_SP_amplitude', 0e-9)
cfg.set(branch+'SP_duration', 250)
cfg.set(branch+'SP_filter_duration', 0)
cfg.set(branch+'SSRO_duration', 50)
cfg.set(branch+'SSRO_repetitions', 5000)
cfg.set(branch+'SSRO_stop_after_first_photon', 0)
cfg.set(branch+'repump_after_repetitions',1)
cfg.set(branch+'mw_frq',2.8e9)
cfg.set(branch+'mw_power',20)
cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

### sil1, AdwinSSRO integrated ###
branch='protocols/sil1-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 50)




### sil7 ###
### sil7, AdwinSSRO ###
branch='protocols/sil7-default/AdwinSSRO/'
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

### sil7, AdwinSSRO integrated ###
branch='protocols/sil7-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 50)

### sil 7 pulses
f0 = cfg['samples']['sil7']['ms+1_cntr_frq'] - cfg['protocols']['sil7-default']['AdwinSSRO']['mw_frq']

branch='protocols/sil7-default/pulses/'
cfg.set(branch+'f0', f0)
cfg.set(branch+'8MHz_pi_duration', 63e-9)
cfg.set(branch+'8MHz_pi_amp',  0.677)
cfg.set(branch+'8MHz_pi_mod_frq',  f0)

# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

# cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
# cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
# cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)

CORPSE_frq = 8.102e6
cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_mod_frq', f0)
cfg.set(branch+'CORPSE_pi_amp',  0.640)

cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
cfg.set(branch+'CORPSE_pi2_amp',  0.698)

#for dynamical decoupling pulses:
cfg.set(branch+'first_C_revival', 53.61e-6) 





### sil11 ###
### sil11, AdwinSSRO ###
branch='protocols/sil11-default/AdwinSSRO/'
cfg.set(branch+'A_CR_amplitude', 15e-9)
cfg.set(branch+'A_RO_amplitude' , 0)
cfg.set(branch+'A_SP_amplitude', 20e-9)
cfg.set(branch+'CR_duration' , 100)
cfg.set(branch+'CR_preselect', 6)
cfg.set(branch+'CR_probe', 2)
cfg.set(branch+'CR_repump', 100)
cfg.set(branch+'Ex_CR_amplitude', 10e-9)
cfg.set(branch+'Ex_RO_amplitude', 10e-9)
cfg.set(branch+'Ex_SP_amplitude', 0e-9)
cfg.set(branch+'SP_duration', 250)
cfg.set(branch+'SP_filter_duration', 0)
cfg.set(branch+'SSRO_duration', 50)
cfg.set(branch+'SSRO_repetitions', 5000)
cfg.set(branch+'SSRO_stop_after_first_photon', 0)
cfg.set(branch+'repump_after_repetitions',1)
cfg.set(branch+'mw_frq',2.8e9)
cfg.set(branch+'mw_power',20)
cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

### sil11, AdwinSSRO integrated ###
branch='protocols/sil11-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 50)




### sil9 ###
### sil9, AdwinSSRO ###
branch='protocols/sil9-default/AdwinSSRO/'
cfg.set(branch+'A_CR_amplitude', 20e-9)
cfg.set(branch+'A_RO_amplitude' , 0)
cfg.set(branch+'A_SP_amplitude', 20e-9)
cfg.set(branch+'CR_duration' , 200)
cfg.set(branch+'CR_preselect', 15)
cfg.set(branch+'CR_probe', 2)
cfg.set(branch+'CR_repump', 1000)
cfg.set(branch+'Ex_CR_amplitude', 20e-9)
cfg.set(branch+'Ex_RO_amplitude', 20e-9)
cfg.set(branch+'Ex_SP_amplitude', 0e-9)
cfg.set(branch+'SP_duration', 250)
cfg.set(branch+'SP_filter_duration', 0)
cfg.set(branch+'SSRO_duration', 50)
cfg.set(branch+'SSRO_repetitions', 5000)
cfg.set(branch+'SSRO_stop_after_first_photon', 0)
cfg.set(branch+'repump_after_repetitions',1)
cfg.set(branch+'mw_frq',2.8e9)
cfg.set(branch+'mw_power',20)
cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

### sil9, AdwinSSRO integrated ###
branch='protocols/sil9-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 50)

# ### sil9, AdwinSSRO+MBI ###
# try:
# 	if type(cfg['protocols']['sil9-default']['AdwinSSRO+MBI']) == types.NoneType:
# 		cfg['protocols']['sil9-default']['AdwinSSRO+MBI'] = {}
# except KeyError:
# 	cfg['protocols']['sil9-default']['AdwinSSRO+MBI'] = {}
   
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['mw_frq'] = 2.80e9
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['mw_power'] = 20    
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['Ex_MBI_amplitude'] = 10e-9
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['Ex_SP_amplitude'] = 20e-9
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['MBI_duration'] = 8
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['MBI_steps'] = 1
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['MBI_threshold'] = 1
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['SP_E_duration'] = 100
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['A_SP_durations'] = np.array([100], dtype=int)
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['E_RO_durations'] = np.array([40], dtype=int)
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['A_SP_amplitudes'] = np.array([20e-9])
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['E_RO_amplitudes'] = np.array([10e-9])
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['send_AWG_start'] = np.array([1])
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['sequence_wait_time'] = np.array([0], dtype=int)
    
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_duration'] = 1728e-9
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['AWG_MBI_MW_pulse_amp'] = 0.03
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['repump_after_MBI_duration'] = 100
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['repump_after_MBI_amplitude'] = 20e-9
# cfg['protocols']['sil9-default']['AdwinSSRO+MBI']['AWG_shelving_pulse_duration'] = 64

# # MBI pulse
# cfg.set('protocols/sil9-default/AdwinSSRO+MBI/AWG_wait_duration_before_MBI_MW_pulse',  50e-9)
# cfg.set('protocols/sil9-default/AdwinSSRO+MBI/AWG_wait_for_adwin_MBI_duration', 18e-6)

### sil 9 pulses
f0 = cfg['samples']['sil9']['ms-1_cntr_frq'] - cfg['protocols']['sil9-default']['AdwinSSRO']['mw_frq']

branch='protocols/sil9-default/pulses/'
cfg.set(branch+'f0', f0)
cfg.set(branch+'8MHz_pi_duration', 63e-9)
cfg.set(branch+'8MHz_pi_amp',  0.677)
cfg.set(branch+'8MHz_pi_mod_frq',  f0)

# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

# cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
# cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
# cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)

CORPSE_frq = 8.065e6
cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_mod_frq', f0)
cfg.set(branch+'CORPSE_pi_amp',  0.468)

cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
cfg.set(branch+'CORPSE_pi2_amp',  0.467)

#for dynamical decoupling pulses:
cfg.set(branch+'first_C_revival', 53.9e-6) 



### save everything
cfg.save_all()
