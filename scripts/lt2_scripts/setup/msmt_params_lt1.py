import types
import qt
cfg = qt.cfgman

cfg['samples']['current'] = 'hans-sil4'
cfg['protocols']['current'] = 'hans-sil4-default'


### sil 4 ###
branch='samples/hans-sil4/'

f_msm1_cntr = 2.826694e9
N_frq = 7.13429e6
N_HF_frq = 2.19290e6

cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
cfg.set(branch+'N_HF_frq', N_HF_frq)


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


### sil4 ###
### sil4, AdwinSSRO ###
branch='protocols/hans-sil4-default/AdwinSSRO/'  
cfg.set(branch+        'A_CR_amplitude',            10e-9)
cfg.set(branch+        'A_RO_amplitude',            0.)
cfg.set(branch+        'A_SP_amplitude',            10e-9)
cfg.set(branch+        'CR_duration',               100)
cfg.set(branch+        'CR_preselect',              15)
cfg.set(branch+        'CR_probe',                  5)
cfg.set(branch+        'CR_repump',                 1000)
cfg.set(branch+        'Ex_CR_amplitude',           10e-9)
cfg.set(branch+        'Ex_RO_amplitude',           3e-9)
cfg.set(branch+        'Ex_SP_amplitude',           0.)
cfg.set(branch+        'SP_duration',               250)
cfg.set(branch+        'SP_filter_duration',        0)
cfg.set(branch+        'SSRO_duration',             50)
cfg.set(branch+        'SSRO_repetitions',          5000)
cfg.set(branch+        'SSRO_stop_after_first_photon',  0)
cfg.set(branch+        'repump_after_repetitions',  1)
cfg.set(branch+        'mw_frq',                    2.8e9)
cfg.set(branch+        'mw_power',                  20)
cfg.set(branch+        'MW_pulse_mod_risetime',     10e-9)

### sil4, AdwinSSRO integrated ###
branch='protocols/hans-sil4-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 50)

### save everything
cfg.save_all()
