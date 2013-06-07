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
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])    
        
    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration']=m.params['green_repump_duration']
    m.params['repump_amplitude']=m.params['green_repump_amplitude']
        
    # parameters
    m.params['SSRO_repetitions'] = 5000

    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 15e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 5e-9 #10e-9

    #m.autoconfig()
    #m.setup()
    
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9
    m.params['Ex_RO_amplitude'] = 5e-9 #10e-9

    m.run()
    m.save('ms1')
    m.finish()

if __name__ == '__main__':
    ssrocalibration('SIL2')
 
    


