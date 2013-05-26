"""
LT1 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

def calibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])    
        
    # parameters
    m.params['SSRO_repetitions'] = 5000

    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 15e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 5e-9 #10e-9

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9
    m.params['Ex_RO_amplitude'] = 5e-9 #10e-9

    m.run()
    m.save('ms1')
    m.finish()
    


