"""
LT1 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['hans-sil4-default']['AdwinSSRO'])    
    
    ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM_lt1']
    m.params['repump_duration'] = m.params['yellow_repump_duration']
    m.params['repump_amplitude'] = m.params['yellow_repump_amplitude']

    # parameters
    m.params['CR_preselect'] = 1000
    m.params['CR_probe'] = 2
    m.params['SSRO_repetitions'] = 5000
    m.params['A_CR_amplitude'] = 5e-9
    m.params['Ex_CR_amplitude'] = 1e-9
    m.params['CR_duration'] = 100
    m.params['SP_duration'] = 250

    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 10e-9 #10e-9

    #m.autoconfig()
    #m.setup()
    
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9
    m.params['Ex_RO_amplitude'] = 10e-9 #10e-9

    m.run()
    m.save('ms1')
    m.finish()

if __name__ == '__main__':
    ssrocalibration('lt1_sil4')
 
    


