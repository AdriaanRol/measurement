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

def ssrocalibration(name, yellow=False):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])    
#    m.params.from_dict(qt.cfgman['protocols']['hans-sil4-default']['AdwinSSRO'])    
          
    # parameters
    m.params['SSRO_repetitions'] = 5000
    m.params['A_CR_amplitude'] = 5e-9 
    m.params['E_CR_amplitude'] = 5e-9
    
    m.params['green_repump_amplitude'] = 100e-6
    m.params['green_repump_duration'] = 50
    m.params['yellow_repump_amplitude'] = 50e-9
    m.params['yellow_repump_duration'] = 1000

    m.params['SSRO_duration'] = 50
    m.params['CR_preselect'] = 1000
    m.params['CR_probe'] = 10


    if yellow:
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=1
        m.params['repump_after_repetitions']=10
    else:
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']

        


    # ms = 0 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 10e-9 #10e-9
    
    # m.autoconfig()
    # m.setup()
    
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9
    m.params['Ex_RO_amplitude'] = 10e-9 #10e-9

    m.run()
    m.save('ms1')
    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG, yellow=False)


 
    


