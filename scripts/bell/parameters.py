"""
This file contains all the measurement parameters.
"""

import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

params = m2.MeasurementParameters('JointParameters')
params_lt1 = m2.MeasurementParameters('LT1Parameters')
params_lt3 = m2.MeasurementParameters('LT3Parameters')

### Hardware stuff
# params['HH_binsize_T3'] = 8

params_lt1['counter_channel'] = 1
params_lt1['ADwin_lt3_trigger_do_channel'] = 8 # OK
params_lt1['ADWin_lt3_di_channel'] = 17 # OK
params_lt1['AWG_lt1_trigger_do_channel'] = 10 # OK
params_lt1['AWG_lt1_di_channel'] = 16 # OK
params_lt1['PLU_arm_do_channel'] = 11
params_lt1['PLU_di_channel'] = 18
params_lt1['AWG_lt1_event_do_channel'] = 14
params_lt1['AWG_lt3_RO1_bit_channel'] = 0
params_lt1['AWG_lt3_RO2_bit_channel'] = 1
params_lt1['AWG_lt3_do_DD_bit_channel'] = 2
params_lt1['AWG_lt3_strobe_channel'] = 9      

params_lt3['counter_channel'] = 1
params_lt3['Adwin_lt1_do_channel'] = 2
params_lt3['Adwin_lt1_di_channel'] = 17
params_lt3['AWG_lt3_di_channel'] = 16

params_lt3['freq_AOM_DAC_channel'] = 4


#################################################################################################################
#LT1 RO CR SP
#################################################################################################################
### RO settings
params_lt1['A_SP_duration'] = 10 # 10 used after MBI and after the first RO of the BSM
params_lt1['wait_before_SSRO2'] = 3
params_lt1['SSRO_duration'] = 10 #15 DO NOT PUT LOWER THAN 10 us or adept adwin trigger length
params_lt1['wait_before_send_BSM_done'] = 40  # this makes sure that the BSM result strobe arives during the last decoupling element. 
                                              # if the total duration of the BSM (incl 3 * params_lt1['SSRO_duration'] ) is changed 
                                              # by more than 20 us, this number has to be readjusted.
# params_lt1['time_before_forced_CR'] = 1 # 1 # 20000 # FIXME

### MBI on LT1
params_lt1['E_SP_duration'] = 100
params_lt1['MBI_duration'] = 4 #put back to 4 with gate
params_lt1['MBI_threshold'] = 1 # 
params_lt1['max_MBI_attempts'] = 100
params_lt1['N_randomize_duration'] = 50 # This could still be optimized, 50 is a guess
params_lt1['E_N_randomize_amplitude'] = 15e-9 # 10 nW is a guess, not optimized
params_lt1['A_N_randomize_amplitude'] = 20e-9 # 10 nW is a guess, not optimized
params_lt1['repump_N_randomize_amplitude'] = 0

 
### SSRO, CR, SP Laser powers
params_lt1['E_CR_amplitude'] = 4e-9
params_lt1['A_CR_amplitude'] = 10e-9               
params_lt1['E_SP_amplitude'] = 10e-9 #was 10e-9              
params_lt1['E_RO_amplitude'] = 4e-9  
params_lt1['A_RO_amplitude'] = 0
params_lt1['A_SP_amplitude'] = 20e-9
params_lt1['repump_amplitude'] = 50e-9 # 50e-9 for yellow 200e-6 for green

### CR and asynchronous preparation settings
# ATM (October 21, green on LT2, yellow+gate on LT1)
params_lt1['CR_duration'] = 50
params_lt1['CR_threshold_preselect'] = 4000
params_lt1['CR_threshold_probe'] = 40
params_lt1['CR_repump'] = 1 # 1 for yellow, 1000 for green
params_lt1['CR_probe_max_time'] = 100000 # in us # TODO is this still valid?
params_lt1['repump_duration'] = 500 # 500 for yellow, 10 for green

# for the N-readout of LT1
params_lt1['N_RO_SP_amplitude'] = params_lt1['A_SP_amplitude']
params_lt1['N_RO_SP_duration'] = 15e-6  #Bas asks: is this an adwin par?
params_lt1['N_RO_repetitions'] = 2 # THIS IS COMPILED INTO THE ADWIN CODE!



#################################################################################################################
#LT2 RO CR SP
#################################################################################################################

params_lt3['SSRO_lt3_duration'] = 23

params_lt3['Ey_CR_amplitude'] = 6e-9#6e-9             
params_lt3['A_CR_amplitude'] = 15e-9#16e-9              
params_lt3['Ey_SP_amplitude'] = 0e-9              
params_lt3['A_SP_amplitude'] = 23e-9             
params_lt3['Ey_RO_amplitude'] = 7e-9
params_lt3['A_RO_amplitude'] = 0
params_lt3['repump_amplitude'] = 200e-6 

params_lt3['repump_duration'] = 10 # 10 for green, 500 for yellow
params_lt3['repump_freq_offset'] = 0 # 5.
params_lt3['repump_freq_amplitude'] = 0 # 4.

params_lt3['CR_duration'] = 50
params_lt3['CR_preselect'] = 2500
params_lt3['CR_probe'] = 2
params_lt3['CR_repump'] = 1000 # 1 for yellow, 1000 for green
params_lt3['CR_probe_max_time'] = 500000 # in us # TODO is that still valid?

####################
### pulses and MW stuff LT1
#####################
## general
f_msm1_cntr_lt1 = 2.828048e9
N_frq_lt1 = 7.13456e6
N_HF_frq_lt1 = 2.19290e6
mw0_lt1= 2.8e9
f0_lt1 = f_msm1_cntr_lt1 - mw0_lt1
finit_lt1 = f0_lt1

params_lt1['N_HF_frq'] = N_HF_frq_lt1
params_lt1['mw_frq'] = mw0_lt1
params_lt1['mw_power'] = 20
params_lt1['mI-1_mod_frq'] = finit_lt1
params_lt1['MW_pulse_mod_risetime'] = 10e-9
params_lt1['AWG_MBI_MW_pulse_mod_frq'] = finit_lt1

## pulses
params_lt1['fast_pi_mod_frq'] = finit_lt1
params_lt1['fast_pi_amp'] = 0.794
params_lt1['fast_pi_duration'] = 80e-9

# fast pi/2 pulse
params_lt1['fast_pi2_mod_frq'] = finit_lt1
params_lt1['fast_pi2_amp'] = 0.77867#0.805
params_lt1['fast_pi2_duration'] = 42e-9

CORPSE_frq_lt1 = 5e6
params_lt1['CORPSE_pi_mod_frq'] = finit_lt1 + N_HF_frq_lt1/2.
params_lt1['CORPSE_pi_60_duration'] = 1./CORPSE_frq_lt1/6.
params_lt1['CORPSE_pi_m300_duration'] = 5./CORPSE_frq_lt1/6.
params_lt1['CORPSE_pi_420_duration'] = 7./CORPSE_frq_lt1/6.
params_lt1['CORPSE_pi_amp'] = 0.503
params_lt1['CORPSE_pi_phase_shift'] = 86.9
params_lt1['CORPSE_pi_center_shift'] = 0.e-9

####################
### pulses and MW stuff LT2
#####################
## general
f_msm1_cntr_lt3 = 2.828827e9 
mw0_lt3 = 2.8e9
f0_lt3 = f_msm1_cntr_lt3 - mw0_lt3
params_lt3['ms-1_cntr_frq'] = f_msm1_cntr_lt3
params_lt3['mw_frq'] = mw0_lt3
params_lt3['mw_power'] = 20
params_lt3['MW_pulse_mod_risetime'] = 10e-9

params_lt3['CORPSE_rabi_frequency'] = 8.15e6
params_lt3['CORPSE_amp'] = 0.382
params_lt3['CORPSE_pi2_amp'] = 0.419864

params_lt3['CORPSE_pi_mod_frq'] = f0_lt3
params_lt3['CORPSE_pi2_mod_frq'] = f0_lt3


### LDE sequence settings
params['HH_sync_period'] = 400e-9 # in seconds -- important for checking (see measurement_loop())
									#Question from hannes: is this the separation of the optical pi pulses?

# LDE Sequence in the AWGs
params_lt3['eom_pulse_duration']        = 2e-9
params_lt3['eom_off_duration']          = 100e-9
params_lt3['eom_off_amplitude']         = -.26  # calibration from 23-08-2013
params_lt3['eom_pulse_amplitude']       = 1.2
params_lt3['eom_overshoot_duration1']   = 10e-9
params_lt3['eom_overshoot1']            = -0.03
params_lt3['eom_overshoot_duration2']   = 4e-9
params_lt3['eom_overshoot2']            = -0.03
params_lt3['aom_risetime']              = 42e-9
params_lt3['eom_aom_on']                = True

params_lt3['AWG_SP_power']            = params_lt3['A_SP_amplitude']
params_lt3['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT2
params_lt3['opt_pulse_separation']    = 600e-9
params_lt3['MW_opt_puls1_separation'] = 100e-9 #distance between the end of the MW and the start of opt puls1
params_lt3['MW_opt_puls2_separation'] = 150e-9

params_lt3['PLU_gate_duration']       = 70e-9
params_lt3['PLU_gate_3_duration']     = 40e-9
params_lt3['PLU_1_delay']             = 1e-9
params_lt3['PLU_2_delay']             = 1e-9
params_lt3['PLU_3_delay']             = 50e-9
params_lt3['PLU_4_delay']             = 150e-9

params_lt1['AWG_SP_power']            = params_lt1['A_SP_amplitude'] 
params_lt1['AWG_yellow_use']          = False #toggles the actual yellow pulse
params_lt1['AWG_yellow_power']        = 50e-9 #yellow power during SP in LDE on LT1, to turn off, do not set to zero.
params_lt1['MW_wait_after_SP']        = 200e-9 # wait time between end of SP_lt1 and start of first MW
params_lt1['MW_separation']           = 600e-9 # separation between the two MW pulses on LT1

params_lt1['initial_delay']           = 10e-9 + 240e-9
params_lt3['initial_delay']           = 10e-9

params['single_sync']                 = 1 #if ==1 then there will only be 1 sync otherwise 1 for each puls
params_lt1['MW_during_LDE']           = 0 #NOTE:gets set automatically
params_lt3['MW_during_LDE']           = 0 #NOTE:gets set automatically

params['LDE_SP_duration']             = 5e-6
params['LDE_SP_duration_yellow']      = 3e-6
params['wait_after_sp']               = 500e-9 #this should be large enough, so that the MW puls fits
params['LDE_element_length']          = 8e-6 # 9e-6 for TPQI with 5 pulses


### default process settings
params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok

params_lt1['max_CR_starts'] = -1
params_lt1['teleportation_repetitions'] = -1
params_lt1['do_remote'] = 1
params_lt3['teleportation_repetitions'] = -1

########
## parameters (for now) only used in calibration scripts
########
CALIBRATION = False

if CALIBRATION == True:
    print 'calibration settings loaded'

    ############### lt1
    ####################
    params_lt1['AWG_wait_duration_before_MBI_MW_pulse'] = 1e-6
    params_lt1['AWG_wait_for_adwin_MBI_duration'] = 15e-6
    params_lt1['AWG_wait_duration_before_shelving_pulse'] = 100e-9

    
    params_lt1['Ex_CR_amplitude'] = params_lt1['E_CR_amplitude']
    params_lt1['A_CR_amplitude'] = params_lt1['A_CR_amplitude']
    params_lt1['Ex_SP_amplitude'] = params_lt1['E_SP_amplitude'] # to pump to ms+- 1 before MBI slow pulse
    params_lt1['SP_E_duration'] = params_lt1['E_SP_duration']

    params_lt1['cycle_duration'] = 300
    params_lt1['repump_after_repetitions'] = 1 #could remove this altogether from adwin...
    params_lt1['send_AWG_start'] = 1
    params_lt1['AWG_done_DI_channel'] = params_lt1['AWG_lt1_di_channel']
    params_lt1['AWG_event_jump_DO_channel'] = params_lt1['AWG_lt1_event_do_channel']
    params_lt1['AWG_start_DO_channel'] = params_lt1['AWG_lt1_trigger_do_channel'] 

    params_lt1['CR_preselect'] = params_lt1['CR_threshold_preselect']
    params_lt1['CR_probe'] = params_lt1['CR_threshold_probe']

    params_lt1['wait_after_RO_pulse_duration'] = 3
    params_lt1['wait_after_pulse_duration'] = 3


    ############### lt3
    ####################
    params_lt3['SP_duration'] = 250
    params_lt3['SSRO_duration'] = params_lt3['SSRO_lt3_duration'] 
    params_lt3['SSRO_stop_after_first_photon'] = 0
    params_lt3['SP_filter_duration'] = 0

    params_lt3['cycle_duration'] = 300
    params_lt3['sequence_wait_time'] = 1
    params_lt3['wait_after_RO_pulse_duration'] = 3
    params_lt3['wait_after_pulse_duration'] = 3
    params_lt3['send_AWG_start'] = 1
    params_lt3['repump_after_repetitions'] = 1

    params_lt3['AWG_done_DI_channel'] = params_lt3['AWG_lt3_di_channel']
    params_lt3['AWG_event_jump_DO_channel'] = 6
    params_lt3['AWG_start_DO_channel'] = 1

    params_lt3['Ex_CR_amplitude'] = params_lt3['Ey_CR_amplitude']
    params_lt3['Ex_SP_amplitude'] = params_lt3['Ey_SP_amplitude']
    params_lt3['Ex_RO_amplitude'] = params_lt3['Ey_RO_amplitude']

    params_lt1['Ex_RO_amplitude'] = params_lt1['E_RO_amplitude']
else:
    print 'calibration settings not loaded'

