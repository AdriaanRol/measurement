import types
import qt
cfg = qt.cfgman

cfg.remove_cfg('protocols')
cfg.remove_cfg('samples')
cfg.remove_cfg('setup')
cfg.add_cfg('protocols')
cfg.add_cfg('samples')
cfg.add_cfg('setup')

cfg['samples']['current'] = 'sil2'
cfg['protocols']['current'] = 'sil2-default'

print 'updating msmt params lt3 for {}'.format(cfg['samples']['current'])

##############################################################################
##############################################################################
### Protocols
##############################################################################
##############################################################################

### General settings for AdwinSSRO
branch='protocols/AdwinSSRO/'
cfg.set(branch+        'AWG_done_DI_channel',          16)
cfg.set(branch+        'AWG_event_jump_DO_channel',    6)
cfg.set(branch+        'AWG_start_DO_channel',         1)
cfg.set(branch+        'counter_channel',              1)
cfg.set(branch+        'cycle_duration',               300)
cfg.set(branch+        'green_off_amplitude',          0.0)
cfg.set(branch+        'green_repump_amplitude',       200e-6)
cfg.set(branch+        'green_repump_duration',        10)
cfg.set(branch+        'send_AWG_start',               0)
cfg.set(branch+        'sequence_wait_time',           1)
cfg.set(branch+        'wait_after_RO_pulse_duration', 3)
cfg.set(branch+        'wait_after_pulse_duration',    3)
cfg.set(branch+        'cr_wait_after_pulse_duration', 2)
cfg.set(branch+        'wait_for_AWG_done',            0)
cfg.set(branch+        'green_off_voltage',            0)
cfg.set(branch+        'Ex_off_voltage',               0.)
cfg.set(branch+        'A_off_voltage',                -0.0)
cfg.set(branch+        'repump_off_voltage',           0)
cfg.set(branch+        'yellow_repump_amplitude',      50e-9)
cfg.set(branch+        'yellow_repump_duration',       500)
cfg.set(branch+        'yellow_CR_repump',             1)
cfg.set(branch+        'green_CR_repump',              1000)
cfg.set(branch+        'CR_probe_max_time',            1000000)

yellow=False
cfg.set(branch + 'yellow', yellow)
if yellow:
    cfg.set(branch + 'repump_duration',             cfg.get(branch+ 'yellow_repump_duration'))
    cfg.set(branch + 'repump_amplitude',            cfg.get(branch+ 'yellow_repump_amplitude')) 
    cfg.set(branch + 'CR_repump',                   cfg.get(branch+ 'yellow_CR_repump'))
else:
    cfg.set(branch + 'repump_duration',             cfg.get(branch+ 'green_repump_duration'))
    cfg.set(branch + 'repump_amplitude',            cfg.get(branch+ 'green_repump_amplitude')) 
    print branch
    print cfg.get(branch + 'repump_amplitude')
    cfg.set(branch + 'CR_repump',                   cfg.get(branch+ 'green_CR_repump'))

### General settings for AdwinSSRO+espin
branch='protocols/AdwinSSRO+espin/'
cfg.set(branch+        'send_AWG_start',                 1)
cfg.set(branch+        'MW_pulse_mod_risetime',          10e-9)

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

##############
### sil 16 ###
##############

branch='samples/sil2/'

f_msm1_cntr = 2.828855e9   #not calibrated
f_msp1_cntr = 2.925884e9    #not calibrated
N_frq = 7.13429e6           #not calibrated
N_HF_frq = 2.16042e6   #not calibrated

cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
cfg.set(branch+'N_HF_frq', N_HF_frq)

branch='protocols/sil2-default/AdwinSSRO/'

cfg.set(branch+'A_CR_amplitude', 40e-9)
cfg.set(branch+'A_RO_amplitude' , 0)
cfg.set(branch+'A_SP_amplitude', 40e-9)
cfg.set(branch+'CR_duration' , 50)
cfg.set(branch+'CR_preselect', 1000)
cfg.set(branch+'CR_probe', 1000)
cfg.set(branch+'CR_repump', 1000)
cfg.set(branch+'Ex_CR_amplitude', 6e-9)
cfg.set(branch+'Ex_RO_amplitude', 8e-9)
cfg.set(branch+'Ex_SP_amplitude', 0e-9)
cfg.set(branch+'SP_duration', 250)
cfg.set(branch+'SP_filter_duration', 0)
cfg.set(branch+'SSRO_duration', 50)
cfg.set(branch+'SSRO_repetitions', 5000)
cfg.set(branch+'SSRO_stop_after_first_photon', 0)
cfg.set(branch+'mw_frq',2.8e9) #-100e6)  #Probably Redundant, better to read out from AWG 
cfg.set(branch+'mw_power',20)
cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

branch='protocols/sil2-default/AdwinSSRO-integrated/'
cfg.set(branch+'SSRO_duration', 40)

### sil 16 pulses ### !!!NOT CALIBRATED

branch='protocols/sil10-default/pulses/'

f0 = cfg['samples']['sil2']['ms-1_cntr_frq'] - cfg['protocols']['sil2-default']['AdwinSSRO']['mw_frq']
cfg.set(branch+'MW_modulation_frequency', f0)
cfg.set(branch+'Pi_pulse_duration', 50e-9)
cfg.set(branch+'Pi_pulse_amp',  0.49)
cfg.set(branch+'CORPSE_pi2_amp',0.4)
CORPSE_frq = 8.15e6
cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
'''
cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
cfg.set('protoMW_pulse_frequencycols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)
'''