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
ssro.AdwinSSRO.E_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.A_aom = qt.instruments['MatisseAOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']

def calibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])    
        
    # parameters
    m.params['SSRO_repetitions'] = 5000

    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 20e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 10e-9 #10e-9

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 20e-9 #10e-9
    m.params['Ex_RO_amplitude'] = 10e-9 #10e-9

    m.run()
    m.save('ms1')
    m.finish()
    
def RO_saturation_power(name):
    m = ssro.AdwinSSRO('RO_saturation_power_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitudes'] = np.arange(20)*2e-9 + 2e-9

    for p in m.params['Ex_RO_amplitudes']:
        m.params['Ex_RO_amplitude'] = p
        m.run()
        m.save('P_%dnW' % (p*1e9))
        
    m.finish()
