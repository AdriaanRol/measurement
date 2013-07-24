"""
LT1 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

def ssrocalibration(name, yellow=False):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])    
    
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
        
    # parameters
    m.params['SSRO_repetitions'] = 5000

    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 10e-9#100e-9#
    m.params['A_CR_amplitude'] = 10e-9#70e-9#
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
    ssrocalibration('SIL2_yellow_no_gate', yellow=True)
 
    


