"""
LT1/2 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.cfgman['protocols']['current']

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])

    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])    

    # parameters
    m.params['SSRO_repetitions'] = 5000
    cfg.set(branch+'CR_duration' , 2000)


    m.params['A_CR_amplitude'] = 70e-9 #5e-9
    m.params['Ex_CR_amplitude'] = 20e-9 #5e-9

    m.params['SSRO_duration'] = 120

    # ms = 0 calibration
    m.params['SP_duration'] = 200
    m.params['A_SP_amplitude'] = 70e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 80e-9 #10e-9
    
    m.autoconfig()
    m.setup()

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 700
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9


    m.run()
    m.save('ms1')
    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)

