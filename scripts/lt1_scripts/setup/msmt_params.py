import types
import qt
cfg = qt.cfgman

 
### sample settings
cfg.set('samples/sil2/ms-1_cntr_frq',  2.827049e9)
cfg.set('samples/sil2/N_0-1_splitting_ms-1', 7.1345e6)
cfg.set('samples/sil2/N_HF_frq',  2.19290e6)

mw0 = 2.8e9
f0 = cfg.get('samples/sil2/ms-1_cntr_frq') - mw0
Nsplit = cfg.get('samples/sil2/N_HF_frq')
finit = f0 - Nsplit

### protocol settings ###

### General settings for AdwinSSRO
cfg.set('protocols/AdwinSSRO/AWG_done_DI_channel',  16)
cfg.set('protocols/AdwinSSRO/AWG_event_jump_DO_channel',  7)
cfg.set('protocols/AdwinSSRO/AWG_start_DO_channel',  1)
cfg.set('protocols/AdwinSSRO/A_laser_DAC_channel',  6)
cfg.set('protocols/AdwinSSRO/Ex_laser_DAC_channel',  7)
cfg.set('protocols/AdwinSSRO/counter_channel',  1)
cfg.set('protocols/AdwinSSRO/cycle_duration',  300)
cfg.set('protocols/AdwinSSRO/green_laser_DAC_channel',  4)
cfg.set('protocols/AdwinSSRO/green_off_amplitude',  0.0)
cfg.set('protocols/AdwinSSRO/green_repump_amplitude',  100e-6)
cfg.set('protocols/AdwinSSRO/green_repump_duration',  10)
cfg.set('protocols/AdwinSSRO/send_AWG_start',  0)
cfg.set('protocols/AdwinSSRO/sequence_wait_time',  1)
cfg.set('protocols/AdwinSSRO/wait_after_RO_pulse_duration',  3)
cfg.set('protocols/AdwinSSRO/wait_after_pulse_duration',  3)
cfg.set('protocols/AdwinSSRO/wait_for_AWG_done',  0)
cfg.set('protocols/AdwinSSRO/green_off_voltage',  0)
cfg.set('protocols/AdwinSSRO/Ex_off_voltage',  0)
cfg.set('protocols/AdwinSSRO/A_off_voltage',  0)
cfg.set('protocols/AdwinSSRO/repump_off_voltage',  0)
cfg.set('protocols/AdwinSSRO/repump_after_repetitions',  1)
cfg.set('protocols/AdwinSSRO/yellow_repump_amplitude',  0)

### General settings for AdwinSSRO+espin
cfg.set('protocols/AdwinSSRO+espin/send_AWG_start',  1)

### General settings for AdwinSSRO+MBI
cfg.set('protocols/AdwinSSRO+MBI/AWG_wait_duration_before_MBI_MW_pulse',  1e-6)
cfg.set('protocols/AdwinSSRO+MBI/AWG_wait_for_adwin_MBI_duration',  
    np.array([15e-6]).tolist())
cfg.set('protocols/AdwinSSRO+MBI/AWG_MBI_MW_pulse_duration',  2e-6)
cfg.set('protocols/AdwinSSRO+MBI/AWG_wait_duration_before_shelving_pulse', 100e-9)
cfg.set('protocols/AdwinSSRO+MBI/nr_of_ROsequences',  1)
cfg.set('protocols/AdwinSSRO+MBI/MW_pulse_mod_risetime',  2)
cfg.set('protocols/AdwinSSRO+MBI/AWG_to_adwin_ttl_trigger_duration',  2e-6)
cfg.set('protocols/AdwinSSRO+MBI/repump_after_MBI_duration', 100)
cfg.set('protocols/AdwinSSRO+MBI/repump_after_MBI_amp', 15e-9)

### more specfic settings
   
### sil2, Pulses ###   
tof = 11e-9
cfg.set('protocols/sil2-default/pulses/t_offset', tof)

cfg.set('protocols/sil2-default/pulses/4MHz_pi_duration', tof + 125e-9)
cfg.set('protocols/sil2-default/pulses/4MHz_pi_amp',  0.683)
cfg.set('protocols/sil2-default/pulses/4MHz_pi_mod_frq',  finit)

cfg.set('protocols/sil2-default/pulses/4MHz_pi2_duration',  tof + 62e-9)
cfg.set('protocols/sil2-default/pulses/4MHz_pi2_amp',  0.683)
cfg.set('protocols/sil2-default/pulses/4MHz_pi2_mod_frq',  finit)

cfg.set('protocols/sil2-default/pulses/selective_pi_duration',  2200e-9)
cfg.set('protocols/sil2-default/pulses/selective_pi_amp',  0.02)
cfg.set('protocols/sil2-default/pulses/selective_pi_mod_frq',  finit)

CORPSE_frq = 4.06e6
cfg.set('protocols/sil2-default/pulses/CORPSE_pi_60_duration', tof + 1./CORPSE_frq/6.)
cfg.set('protocols/sil2-default/pulses/CORPSE_pi_m300_duration', tof + 5./CORPSE_frq/6.)
cfg.set('protocols/sil2-default/pulses/CORPSE_pi_420_duration', tof + 7./CORPSE_frq/6.)
cfg.set('protocols/sil2-default/pulses/CORPSE_pi_mod_frq', finit + Nsplit/2.)
cfg.set('protocols/sil2-default/pulses/CORPSE_pi_amp',  0.7)

cfg.set('protocols/sil2-default/pulses/pi2pi_mIm1_duration', tof + 395e-9)
cfg.set('protocols/sil2-default/pulses/pi2pi_mIm1_amp', 0.167)
cfg.set('protocols/sil2-default/pulses/pi2pi_mIm1_mod_frq', finit)

### set some other pulses that determinine their values from the ones above
cfg.set('protocols/sil2-default/pulses/AWG_N_CNOT_pulse_duration', cfg.get('protocols/sil2-default/pulses/pi2pi_mI1_duration'))
cfg.set('protocols/sil2-default/pulses/AWG_N_CNOT_pulse_amp', cfg.get('protocols/sil2-default/pulses/pi2pi_mI1_amp'))
cfg.set('protocols/sil2-default/pulses/AWG_N_CNOT_pulse_mod_frq', cfg.get('protocols/sil2-default/pulses/pi2pi_mI1_mod_frq'))

cfg.set('protocols/sil2-default/pulses/AWG_MBI_MW_pulse_mod_frq',  finit)
cfg.set('protocols/sil2-default/pulses/AWG_MBI_MW_pulse_amp', cfg.get('protocols/sil2-default/pulses/selective_pi_amp'))
cfg.set('protocols/sil2-default/pulses/AWG_MBI_MW_pulse_duration', cfg.get('protocols/sil2-default/pulses/selective_pi_duration'))

cfg.set('protocols/sil2-default/pulses/AWG_shelving_pulse_duration', cfg.get('protocols/sil2-default/pulses/4MHz_pi_duration'))
cfg.set('protocols/sil2-default/pulses/AWG_shelving_pulse_amp',cfg.get('protocols/sil2-default/pulses/4MHz_pi_amp'))

cfg.set('protocols/sil2-default/pulses/N_pi_duration', 90.1e-6)
cfg.set('protocols/sil2-default/pulses/N_pi2_duration', 90.1e-6)


### sil2, AdwinSSRO ###
cfg.set('protocols/sil2-default/AdwinSSRO/A_CR_amplitude',  10e-9)
cfg.set('protocols/sil2-default/AdwinSSRO/A_RO_amplitude',  0.)
cfg.set('protocols/sil2-default/AdwinSSRO/A_SP_amplitude',  15e-9)
cfg.set('protocols/sil2-default/AdwinSSRO/CR_duration',  100)
cfg.set('protocols/sil2-default/AdwinSSRO/CR_preselect',  40)
cfg.set('protocols/sil2-default/AdwinSSRO/CR_probe',  40)
cfg.set('protocols/sil2-default/AdwinSSRO/Ex_CR_amplitude',  10e-9)
cfg.set('protocols/sil2-default/AdwinSSRO/Ex_RO_amplitude',  7e-9)
cfg.set('protocols/sil2-default/AdwinSSRO/Ex_SP_amplitude',  0.)
cfg.set('protocols/sil2-default/AdwinSSRO/SP_duration',  250)
cfg.set('protocols/sil2-default/AdwinSSRO/SP_filter_duration',  0)
cfg.set('protocols/sil2-default/AdwinSSRO/SSRO_duration',  50)
cfg.set('protocols/sil2-default/AdwinSSRO/SSRO_repetitions',  5000)
cfg.set('protocols/sil2-default/AdwinSSRO/SSRO_stop_after_first_photon',  0)

### sil2, integrated SSRO
cfg.set('protocols/sil2-default/AdwinSSRO-integrated/SSRO_duration',  15)

### sil2, Adwin MBI ###
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/mw_frq',  mw0)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/mw_power',  20)    
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/Ex_MBI_amplitude',  7e-9)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/Ex_SP_amplitude',  10e-9)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/MBI_duration',  4)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/MBI_steps',  1)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/MBI_threshold',  1)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/SP_E_duration',  100)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/repump_after_MBI_duration', 100)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/repump_after_MBI_amplitude', 25e-9)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/repump_after_E_RO_duration', 100)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/repump_after_E_RO_amplitude', 25e-9)


# MBI pulse
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_wait_duration_before_MBI_MW_pulse',  50e-9)
cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_wait_for_adwin_MBI_duration', 15e-6)

# shelving pulse    
#cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_RF_pipulse_duration',  87e3
#cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_RF_pipulse_amp',  1.
#cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_RF_pipulse_frq',  7.135e6
#cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_RF_p2pulse_duration',  \
#    cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_RF_pipulse_duration']/2
#cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_RF_p2pulse_amp',  1.
#cfg.set('protocols/sil2-default/AdwinSSRO+MBI/AWG_RF_p2pulse_frq',  7.135e6

#cfg.save_all()
