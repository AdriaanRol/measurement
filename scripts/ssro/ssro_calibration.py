"""
LT1/2 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

# import the measurement parameters
execfile("setup/msmt_params.py")
SAMPLE_CFG = qt.cfgman['protocols']['current']

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    # parameters
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration']       = 100
    m.params['SSRO_stop_after_first_photon']= 0

    m.params['A_CR_amplitude']  = 10e-9
    m.params['A_RO_amplitude']  = 0
    m.params['A_SP_amplitude']  = 10e-9

    m.params['CR_duration']     = 25
    m.params['CR_preselect']    = 1000
    m.params['CR_repump']       = 1000
    m.params['CR_probe']        = 1000

    m.params['Ex_CR_amplitude'] =  5e-9
    m.params['Ex_RO_amplitude'] =  8e-9
    m.params['Ex_SP_amplitude'] =  0e-9

    m.params['SP_duration']     =  100
    m.params['SP_filter_duration']  = 0

    # ms = 0 calibration
    m.autoconfig()
    m.setup()

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 300
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9

    m.run()
    m.save('ms1')
    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)

