import types
import qt
cfg = qt.cfgman

 
### sample settings
# branch='samples/sil2/'

# f_msm1_cntr = 2.826961e9
# N_frq = 7.13429e6
# N_HF_frq = 2.19290e6
# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)
# mw0 = 2.8e9
# f0 = f_msm1_cntr - mw0
# Nsplit = N_HF_frq
# finit = f0 - Nsplit
# fmIp1 = f_msm1_cntr - mw0 + N_HF_frq
# cfg.set(branch+'mIm1_mod_frq',  f_msm1_cntr - mw0 - N_HF_frq)
# cfg.set(branch+'mI0_mod_frq',  f_msm1_cntr - mw0)
# cfg.set(branch+'mIp1_mod_frq',  f_msm1_cntr - mw0 + N_HF_frq)


###
branch='samples/hans-sil1/'

f_msm1_cntr = 2.826694e9
N_frq = 7.13429e6
N_HF_frq = 2.19290e6
cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
cfg.set(branch+'N_HF_frq', N_HF_frq)
mw0 = 2.8e9
f0 = f_msm1_cntr - mw0
Nsplit = N_HF_frq
finit = f0 - Nsplit
fmIp1 = f_msm1_cntr - mw0 + N_HF_frq
cfg.set(branch+'mIm1_mod_frq',  f_msm1_cntr - mw0 - N_HF_frq)
cfg.set(branch+'mI0_mod_frq',  f_msm1_cntr - mw0)
cfg.set(branch+'mIp1_mod_frq',  f_msm1_cntr - mw0 + N_HF_frq)


### protocol settings ###

### General settings for AdwinSSRO
branch='protocols/AdwinSSRO/'
cfg.set(branch+        'AWG_done_DI_channel',          16)
cfg.set(branch+        'AWG_event_jump_DO_channel',    7)
cfg.set(branch+        'AWG_start_DO_channel',         10)
cfg.set(branch+        'A_laser_DAC_channel',          6)
cfg.set(branch+        'Ex_laser_DAC_channel',         7)
cfg.set(branch+        'counter_channel',              1)
cfg.set(branch+        'cycle_duration',               300)
cfg.set(branch+        'green_laser_DAC_channel',      4)
cfg.set(branch+        'green_off_amplitude',          0.0)
cfg.set(branch+        'green_repump_amplitude',       100e-6)
cfg.set(branch+        'green_repump_duration',        10)
cfg.set(branch+        'send_AWG_start',               0)
cfg.set(branch+        'sequence_wait_time',           1)
cfg.set(branch+        'wait_after_RO_pulse_duration', 3)
cfg.set(branch+        'wait_after_pulse_duration',    3)
cfg.set(branch+        'wait_for_AWG_done',            0)
cfg.set(branch+        'green_off_voltage',            0)
cfg.set(branch+        'Ex_off_voltage',               0.)
cfg.set(branch+        'A_off_voltage',                0.06)
cfg.set(branch+        'repump_off_voltage',           0)
cfg.set(branch+        'repump_after_repetitions',     1)
cfg.set(branch+        'yellow_repump_amplitude',      50e-9)
cfg.set(branch+        'yellow_repump_duration',       500)
cfg.set(branch+        'yellow_repump_after_repetitions',100)
cfg.set(branch+        'yellow_CR_repump',              1)
cfg.set(branch+        'green_repump_after_repetitions',1)
cfg.set(branch+        'green_CR_repump',              1000)

cfg.set(branch+        'A_CR_amplitude',            10e-9)
cfg.set(branch+        'A_RO_amplitude',            0.)
cfg.set(branch+        'A_SP_amplitude',            10e-9)
cfg.set(branch+        'CR_duration',               100)
cfg.set(branch+        'CR_preselect',              10)
cfg.set(branch+        'CR_probe',                  10)
cfg.set(branch+        'CR_repump',                 1000)
cfg.set(branch+        'Ex_CR_amplitude',           5e-9)
cfg.set(branch+        'Ex_RO_amplitude',           5e-9)
cfg.set(branch+        'Ex_SP_amplitude',           0.)
cfg.set(branch+        'SP_duration',               250)
cfg.set(branch+        'SP_filter_duration',        0)
cfg.set(branch+        'SSRO_duration',             50)
cfg.set(branch+        'SSRO_repetitions',          1000)
cfg.set(branch+        'SSRO_stop_after_first_photon',  0)



### General settings for AdwinSSRO+espin
branch='protocols/AdwinSSRO+espin/'
cfg.set(branch+        'send_AWG_start',                 1)

### General settings for AdwinSSRO+MBI
branch='protocols/AdwinSSRO+MBI/'
cfg.set(branch+        'AWG_wait_duration_before_MBI_MW_pulse',    1e-6)
cfg.set(branch+        'AWG_wait_for_adwin_MBI_duration',  
    np.array([15e-6]).tolist())
cfg.set(branch+        'AWG_MBI_MW_pulse_duration',                2e-6)
cfg.set(branch+        'AWG_wait_duration_before_shelving_pulse',  100e-9)
cfg.set(branch+        'nr_of_ROsequences',                        1)
cfg.set(branch+        'MW_pulse_mod_risetime',                    10e-9)
cfg.set(branch+        'AWG_to_adwin_ttl_trigger_duration',        2e-6)
cfg.set(branch+        'repump_after_MBI_duration',                100)
cfg.set(branch+        'repump_after_MBI_amp',                     15e-9)


### more specfic settings
   
### sil2, Pulses ###   
branch='protocols/sil2-default/pulses/'

tof = 0#11e-9
cfg.set(branch+        't_offset',                 tof)

cfg.set(branch+        '4MHz_pi_duration',         tof + 125e-9)
cfg.set(branch+        '4MHz_pi_amp',              0.599)
cfg.set(branch+        '4MHz_pi_mod_frq',          finit)

cfg.set(branch+        '4MHz_pi2_duration',          tof + 62e-9)
cfg.set(branch+        '4MHz_pi2_amp',              0.599)
cfg.set(branch+        '4MHz_pi2_mod_frq',          finit)

cfg.set(branch+        'selective_pi_duration',      2600e-9)
cfg.set(branch+        'selective_pi_amp',          0.02)
cfg.set(branch+        'selective_pi_mod_frq',      finit)

CORPSE_frq = 3.991e6
cfg.set(branch+        'CORPSE_pi_60_duration',     tof/2. + 1./CORPSE_frq/6.)
cfg.set(branch+        'CORPSE_pi_m300_duration',     5./CORPSE_frq/6.)
cfg.set(branch+        'CORPSE_pi_420_duration',     tof/2. + 7./CORPSE_frq/6.)
cfg.set(branch+        'CORPSE_pi_mod_frq',         finit + Nsplit/2.)
cfg.set(branch+        'CORPSE_pi_amp',              0.703)
cfg.set(branch+        'CORPSE_pi_phase_shift',     74.0)
cfg.set(branch+        'CORPSE_pi_center_shift',     13e-9)

cfg.set(branch+        'pi2pi_mIm1_duration',         tof + 395e-9)
cfg.set(branch+        'pi2pi_mIm1_amp',             0.164)
cfg.set(branch+        'pi2pi_mIm1_mod_frq',         finit)

cfg.set(branch+        'pi2pi_mI0_duration',         tof + 395e-9)
cfg.set(branch+        'pi2pi_mI0_amp',             0.170)
cfg.set(branch+        'pi2pi_mI0_mod_frq',         f0)

cfg.set(branch+        'pi2pi_mIp1_duration',         tof + 395e-9)
cfg.set(branch+        'pi2pi_mIp1_amp',             0.185)
cfg.set(branch+        'pi2pi_mIp1_mod_frq',         fmIp1)


### set some other pulses that determinine their values from the ones above
cfg.set(branch+        'AWG_N_CNOT_pulse_duration', 
    cfg.get(branch+         'pi2pi_mIm1_duration'))
cfg.set(branch+        'AWG_N_CNOT_pulse_amp',      
    cfg.get(branch+         'pi2pi_mIm1_amp'))
cfg.set(branch+        'AWG_N_CNOT_pulse_mod_frq',  
    cfg.get(branch+        'pi2pi_mIm1_mod_frq'))

cfg.set(branch+        'AWG_MBI_MW_pulse_mod_frq',  
    finit)
cfg.set(branch+        'AWG_MBI_MW_pulse_amp',      
    cfg.get(branch+        'selective_pi_amp'))
cfg.set(branch+        'AWG_MBI_MW_pulse_duration', 
    cfg.get(branch+        'selective_pi_duration'))

cfg.set(branch+        'AWG_shelving_pulse_duration',
    cfg.get(branch+        '4MHz_pi_duration'))
cfg.set(branch+        'AWG_shelving_pulse_amp',    
    cfg.get(branch+        '4MHz_pi_amp'))

### Nitrogen pulses
cfg.set(branch+        'N_pi_duration', 91.1e-6)
cfg.set(branch+        'N_pi_amp', 1)

cfg.set(branch+        'N_pi2_duration', 91.1e-6/2.)
cfg.set(branch+        'N_pi2_amp', 1)

### sil2, AdwinSSRO ###
branch='protocols/sil2-default/AdwinSSRO/'  
cfg.set(branch+        'A_CR_amplitude',            10e-9)
cfg.set(branch+        'A_RO_amplitude',            0.)
cfg.set(branch+        'A_SP_amplitude',            10e-9)
cfg.set(branch+        'CR_duration',               100)
cfg.set(branch+        'CR_preselect',              40)
cfg.set(branch+        'CR_probe',                  40)
cfg.set(branch+        'CR_repump',                 1000)
cfg.set(branch+        'Ex_CR_amplitude',           5e-9)
cfg.set(branch+        'Ex_RO_amplitude',           5e-9)
cfg.set(branch+        'Ex_SP_amplitude',           0.)
cfg.set(branch+        'SP_duration',               250)
cfg.set(branch+        'SP_filter_duration',        0)
cfg.set(branch+        'SSRO_duration',             50)
cfg.set(branch+        'SSRO_repetitions',          1000)
cfg.set(branch+        'SSRO_stop_after_first_photon',  0)

### sil2, integrated SSRO
cfg.set('protocols/sil2-default/AdwinSSRO-integrated/SSRO_duration', 15)

### sil2, Adwin MBI ###
branch='protocols/sil2-default/AdwinSSRO+MBI/'
cfg.set(branch+        'mw_frq',                        mw0)
cfg.set(branch+        'mw_power',                      20)
cfg.set(branch+        'Ex_MBI_amplitude',              5e-9)
cfg.set(branch+        'Ex_SP_amplitude',               10e-9)
cfg.set(branch+        'MBI_duration',                  4)
cfg.set(branch+        'MBI_steps',                     1)
cfg.set(branch+        'MBI_threshold',                 1)
cfg.set(branch+        'SP_E_duration',                 100)
cfg.set(branch+        'repump_after_MBI_duration',     100)
cfg.set(branch+        'repump_after_MBI_amplitude',    25e-9)
cfg.set(branch+        'repump_after_E_RO_duration',    100)
cfg.set(branch+        'repump_after_E_RO_amplitude',   25e-9)

# MBI pulse
cfg.set(branch+        'AWG_wait_duration_before_MBI_MW_pulse',     50e-9)
cfg.set(branch+        'AWG_wait_for_adwin_MBI_duration',           15e-6)

### sil2, Teleportation ###
# branch='protocols/sil2-default/Teleportation/'
# cfg.set(branch+        'A_CR_amplitude',                10e-9)
# cfg.set(branch+        'A_RO_amplitude',                0.)
# cfg.set(branch+        'A_SP_amplitude',                15e-9)
# cfg.set(branch+        'Ex_CR_amplitude',               10e-9)
# cfg.set(branch+        'Ex_RO_amplitude',               5e-9)
# cfg.set(branch+        'Ex_SP_amplitude',               0.)
# cfg.set(branch+        'yellow_repump_amplitude',       0)
# cfg.set(branch+        'yellow_repump_duration',        3) 
# cfg.set(branch+        'CR_duration',                   100)
# cfg.set(branch+        'CR_threshold_preselect',        40)
# cfg.set(branch+        'CR_threshold_probe',            40)
# cfg.set(branch+        'time_before_forced_CR',         500000)
# cfg.set(branch+        'teleportation_repetitions',     1000)

### sil2, BSM
cfg.set('protocols/sil2-default/BSM/N_ref_frq', N_frq)
cfg.set('protocols/sil2-default/BSM/e_ref_frq', finit)

### General settings for ADWIN Teleportation
# branch='protocols/Teleportation/'
# cfg.set(branch+        'AWG_done_DI_channel',                      16)
# cfg.set(branch+        'AWG_event_jump_DO_channel',                7)
# cfg.set(branch+        'AWG_start_DO_channel',                     1)
# cfg.set(branch+        'A_laser_DAC_channel',                      6)
# cfg.set(branch+        'Ex_laser_DAC_channel',                     7)
# cfg.set(branch+        'counter_channel',                          1)
# cfg.set(branch+        'yellow_laser_DAC_channel',                 3)
# cfg.set(branch+        'green_laser_DAC_channel',                  4)
# cfg.set(branch+        'green_off_amplitude',                      0.0)
# cfg.set(branch+        'green_repump_amplitude',                   100e-6)
# cfg.set(branch+        'green_repump_duration',                    10)
# cfg.set(branch+        'yellow_repump_duration',                   500)
# cfg.set(branch+        'yellow_off_voltage',                       0)
# cfg.set(branch+        'green_off_voltage',                        0)

branch='protocols/hans-sil1-default/AdwinSSRO/'  
cfg.set(branch+        'A_CR_amplitude',            10e-9)
cfg.set(branch+        'A_RO_amplitude',            0.)
cfg.set(branch+        'A_SP_amplitude',            10e-9)
cfg.set(branch+        'CR_duration',               100)
cfg.set(branch+        'CR_preselect',              30)
cfg.set(branch+        'CR_probe',                  30)
cfg.set(branch+        'CR_repump',                 1000)
cfg.set(branch+        'Ex_CR_amplitude',           5e-9)
cfg.set(branch+        'Ex_RO_amplitude',           5e-9)
cfg.set(branch+        'Ex_SP_amplitude',           0.)
cfg.set(branch+        'SP_duration',               250)
cfg.set(branch+        'SP_filter_duration',        0)
cfg.set(branch+        'SSRO_duration',             50)
cfg.set(branch+        'SSRO_repetitions',          5000)
cfg.set(branch+        'SSRO_stop_after_first_photon',  0)

cfg.set('protocols/hans-sil1-default/AdwinSSRO-integrated/SSRO_duration', 15)

cfg.save_all()
