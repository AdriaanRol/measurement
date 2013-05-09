"""
LT2 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

# set the static variables for LT2
ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt2_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM']
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']

def calibration(name):
    m = AdwinSSRO(name, qt.instruments['adwin'])
	
	m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
	m.setup()
	
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration'] = 50
    m.params['CR_preselect'] = 50 #20
    m.params['CR_probe'] = 50 #20
    m.params['counter_channel'] = 1
    m.params['Ex_CR_amplitude'] = 5e-9 #20e-9 #30e-9
    m.params['A_CR_amplitude'] = 10e-9 #200e-9  #500e-9

    # ms = 0 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_RO_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 2e-9 #10e-9   

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 5e-9 #10e-9
    m.params['A_RO_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 2e-9 #10e-9

    m.run()
    m.save('ms1')

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    m.save_instrument_settings_file()
    
    m.finish()


