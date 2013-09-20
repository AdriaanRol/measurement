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
params_lt2 = m2.MeasurementParameters('LT2Parameters')

### Hardware stuff
params['HH_binsize_T3'] = 8

params_lt1['counter_channel'] = 1
params_lt1['ADwin_lt2_trigger_do_channel'] = 8 # OK
params_lt1['ADWin_lt2_di_channel'] = 17 # OK
params_lt1['AWG_lt1_trigger_do_channel'] = 10 # OK
params_lt1['AWG_lt1_di_channel'] = 16 # OK
params_lt1['PLU_arm_do_channel'] = 11
params_lt1['PLU_di_channel'] = 18
params_lt1['AWG_lt1_event_do_channel'] = 14
params_lt1['AWG_lt2_address0_do_channel'] = 0
params_lt1['AWG_lt2_address1_do_channel'] = 1
params_lt1['AWG_lt2_address2_do_channel'] = 2
params_lt1['AWG_lt2_address3_do_channel'] = 3
params_lt1['AWG_lt2_address_LDE'] = 1
params_lt1['AWG_lt2_address_U1'] = 2                    
params_lt1['AWG_lt2_address_U2'] = 3
params_lt1['AWG_lt2_address_U3'] = 4
params_lt1['AWG_lt2_address_U4'] = 5       
params_lt1['repump_off_voltage'] = 0.0         
params_lt1['Ey_off_voltage'] = 0.0
params_lt1['FT_off_voltage'] = 0.0

params_lt2['counter_channel'] = 1
params_lt2['Adwin_lt1_do_channel'] = 2
params_lt2['Adwin_lt1_di_channel'] = 17
params_lt2['AWG_lt2_di_channel'] = 16
params_lt2['repump_off_voltage'] = 0.0
params_lt2['Ey_off_voltage'] = 0.0
params_lt2['A_off_voltage'] = -0.15
params_lt2['freq_AOM_DAC_channel'] = 4


### RO settings
params_lt1['wait_before_SSRO1'] = 3
params_lt1['wait_before_SP_after_RO'] = 3
params_lt1['SP_after_RO_duration'] = 50
params_lt1['wait_before_SSRO2'] = 3
params_lt1['SSRO2_duration'] = 15
params_lt1['SSRO1_duration'] = 15

params_lt2['SSRO_lt2_duration'] = 50

### CR and asynchronous preparation settings
params_lt1['CR_duration'] = 50
params_lt1['CR_threshold_preselect'] = 22
params_lt1['CR_threshold_probe'] = 2
params_lt1['CR_repump'] = 1000
params_lt1['CR_probe_max_time'] = 10000 #us
params_lt1['repump_duration'] = 10#50
params_lt1['time_before_forced_CR'] = 1 #1#20000 # FIXME
params_lt1['N_pol_element_repetitions'] = 5 # FIXME

params_lt2['repump_duration'] = 500
params_lt2['repump_freq_offset'] = 5.
params_lt2['repump_freq_amplitude'] = 4.

params_lt2['CR_duration'] = 50
params_lt2['CR_preselect'] = 25
params_lt2['CR_probe'] = 2
params_lt2['CR_repump'] = 1
params_lt2['CR_probe_max_time'] = 500000 # us = 0.5 s 
 
### SSRO, CR, SP Laser powers
params_lt1['Ey_CR_amplitude'] = 5e-9
params_lt1['FT_CR_amplitude'] = 13e-9               
params_lt1['Ey_SP_amplitude'] = 10e-9               
params_lt1['FT_SP_amplitude'] = 10e-9 
params_lt1['Ey_RO_amplitude'] = 7e-9  
params_lt1['FT_RO_amplitude'] = 0
params_lt1['repump_amplitude'] = 200e-6 #300e-6#

params_lt2['Ey_CR_amplitude'] = 6e-9             
params_lt2['A_CR_amplitude'] = 16e-9              
params_lt2['Ey_SP_amplitude'] = 10e-9              
params_lt2['A_SP_amplitude'] = 20e-9             
params_lt2['Ey_RO_amplitude'] = 10e-9
params_lt2['A_RO_amplitude'] = 0
params_lt2['repump_amplitude'] = 50e-9 #yellow

### pulses and MW stuff
params_lt1['ms-1_cntr_frq'] = 2.827e9 
params_lt1['mw_frq'] = 2.8e9
params_lt1['mw_power'] = 20
params_lt1['MW_pulse_mod_risetime'] = 10e-9
params_lt1['mi-1_mod_frq'] = params_lt1['ms-1_cntr_frq'] - params_lt1['mw_frq']

params_lt2['mw_frq'] = 2.8e9
params_lt2['mw_power'] = 20
params_lt2['MW_pulse_mod_risetime'] = 10e-9

#the LDE sequence pi and pi/2 pulse on mI=-1
params_lt1['MW_pi_mod_frq'] = params_lt1['mi-1_mod_frq']
params_lt1['MW_pi_amplitude'] = 0.9
params_lt1['MW_pi_length'] = 500e-9

params_lt1['MW_pi2_mod_frq'] = params_lt1['mi-1_mod_frq']
params_lt1['MW_pi2_amplitude'] = 0.9
params_lt1['MW_pi2_length'] = 500e-9

## Hannes: i just copied these corpse parameters from msmt_params in setup
CORPSE_frq = 8.035e6
params_lt2['CORPSE_pi2_mod_frq'] = params_lt2['mw_frq']
params_lt2['CORPSE_pi2_amp'] = 0.639
params_lt2['CORPSE_pi2_24p3_duration'] = 24.3/CORPSE_frq/360.
params_lt2['CORPSE_pi2_m318p6_duration'] = 318.6/CORPSE_frq/360.
params_lt2['CORPSE_pi2_384p3_duration'] = 384.3/CORPSE_frq/360.

params_lt2['CORPSE_pi_mod_frq'] = params_lt2['mw_frq']
params_lt2['CORPSE_pi_amp'] = 0.605
params_lt2['CORPSE_pi_60_duration'] =1./CORPSE_frq/6.
params_lt2['CORPSE_pi_m300_duration'] = 5./CORPSE_frq/6.
params_lt2['CORPSE_pi_420_duration'] = 7./CORPSE_frq/6.


### LDE sequence settings
params['HH_sync_period'] = 400e-9 # in seconds -- important for checking (see measurement_loop())
									#Question from hannes: is this the separation of the optical pi pulses?

#EOM stuff:
params_lt2['eom_pulse_duration']        = 2e-9
params_lt2['eom_off_duration']          = 100e-9
params_lt2['eom_off_amplitude']         = -.26  # calibration from 23-08-2013
params_lt2['eom_pulse_amplitude']       = 1.2
params_lt2['eom_overshoot_duration1']   = 10e-9
params_lt2['eom_overshoot1']            = -0.03
params_lt2['eom_overshoot_duration2']   = 4e-9
params_lt2['eom_overshoot2']            = -0.03
params_lt2['aom_risetime']              = 42e-9

params_lt2['AWG_SP_power']            = 40e-9
params_lt2['AWG_yellow_power']        = 50e-9 #yellow power during SP in LDE on LT1
params_lt2['opt_pulse_separation']    = 600e-9
params_lt2['MW_opt_puls1_separation'] = 50e-9 #distance between the end of the MW and the start of opt puls1
params_lt2['MW_opt_puls2_separation'] = 50e-9

params_lt2['PLU_gate_duration']       = 70e-9
params_lt2['PLU_gate_3_duration']     = 40e-9
params_lt2['PLU_3_delay']             = 50e-9
params_lt2['PLU_4_delay']             = 150e-9

params_lt1['AWG_SP_power']            = 20e-9 # 500e-9 #this should be on the FT
params_lt1['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT1
params_lt1['MW_wait_after_SP']        = 20e-9 #wait time between end of SP_lt1 and start of first MW
params_lt1['MW_separation']           = 600e-9 # separation between the two MW pulses on LT1

params_lt1['initial_delay']           = 10e-9 + 240e-9
params_lt2['initial_delay']           = 10e-9

params['single_sync']                 = 1 #if ==1 then there will only be 1 sync otherwise 1 for each puls
params['long_histogram']              = 0 #if ==1 there will be only one sync at the beginning of LDE
params['MW_during_LDE']               = 0 #NOTE:MW stuff not implemented, yet

params['LDE_SP_duration']             = 5e-6
params['LDE_SP_duration_yellow']      = 3e-6
params['wait_after_sp']               = 500e-9 #this should be large enough, so that the MW puls fits
params['LDE_element_length']          = 9e-6 # 9k for TPQI.


### default process settings
params['LDE_attempts_before_CR'] = 1000 # 1000 for tpqi seems ok

params_lt1['max_CR_starts'] = -1
params_lt1['teleportation_repetitions'] = -1
params_lt1['do_remote'] = 1
params_lt1['do_N_polarization'] = 1

params_lt2['teleportation_repetitions'] = -1