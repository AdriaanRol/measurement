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
params_lt1['repump_off_voltage'] = 0         
params_lt1['Ey_off_voltage'] = 0 
params_lt1['FT_off_voltage'] = 0

params_lt2['counter_channel'] = 1
params_lt2['Adwin_lt1_do_channel'] = 2
params_lt2['Adwin_lt1_di_channel'] = 17
params_lt2['AWG_lt2_di_channel'] = 16
params_lt2['repump_off_voltage'] = 0
params_lt2['Ey_off_voltage'] = 0 
params_lt2['A_off_voltage'] = 0

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
params_lt1['CR_threshold_preselect'] = 0
params_lt1['CR_threshold_probe'] = 0
params_lt1['CR_repump'] = 1000
params_lt1['repump_duration'] = 1000
params_lt1['repump_after_repetitions'] = 1
params_lt1['time_before_forced_CR'] = 20000 # FIXME
params_lt1['N_pol_element_repetitions'] = 5 # FIXME

params_lt2['repump_duration'] = 50
params_lt2['CR_duration'] = 50
params_lt2['CR_preselect'] = 0
params_lt2['CR_probe'] = 0
params_lt2['repump_after_repetitions'] = 1
params_lt2['CR_repump'] = 1000

### SSRO, CR, SP Laser powers
params_lt1['Ey_CR_amplitude'] = 0
params_lt1['FT_CR_amplitude'] = 0              
params_lt1['Ey_SP_amplitude'] = 0              
params_lt1['FT_SP_amplitude'] = 0             
params_lt1['Ey_RO_amplitude'] = 0            
params_lt1['FT_RO_amplitude'] = 0
params_lt1['repump_amplitude'] = 0

params_lt2['Ey_CR_amplitude'] = 0             
params_lt2['A_CR_amplitude'] = 0              
params_lt2['Ey_SP_amplitude'] = 0              
params_lt2['A_SP_amplitude'] = 0             
params_lt2['Ey_RO_amplitude'] = 0
params_lt2['A_RO_amplitude'] = 0
params_lt2['repump_amplitude'] = 0

### pulses and MW stuff
params_lt1['mw_frq'] = 2.8e9
params_lt1['mw_power'] = 20
params_lt1['MW_pulse_mod_risetime'] = 10e-9

params_lt2['mw_frq'] = 2.8e9
params_lt2['mw_power'] = 20
params_lt2['MW_pulse_mod_risetime'] = 10e-9


### LDE sequence settings
params['HH_sync_period'] = 400e-9 # in seconds -- important for checking (see measurement_loop())
									#Question from hannes: is this the separation of the optical pi pulses?

### default process settings
params['LDE_attempts_before_CR'] = 100 # FIXME

params_lt1['max_CR_starts'] = -1
params_lt1['teleportation_repetitions'] = -1
params_lt1['do_remote'] = 1
params_lt1['do_N_polarization'] = 1

params_lt2['teleportation_repetitions'] = -1