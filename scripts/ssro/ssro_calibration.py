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



    m.params['repump_mod_DAC_channel'] =
    m.params['cr_mod_DAC_channel']     = 
    m.params['cr_mod_control_offset']  =  0.0
    m.params['cr_mod_control_amp']     =  0.1 #V
    m.params['pos_mod_control_offset_x'] = m.adwin.get_dac_voltage('atto_x')
    m.params['pos_mod_control_offset_y'] = m.adwin.get_dac_voltage('atto_y')
    m.params['pos_mod_control_offset_z'] = m.adwin.get_dac_voltage('atto_z')
    m.params['pos_mod_control_amp'] =  0.03
    m.params['pos_mod_fb'] = 0.0
    m.params['pos_mod_min_counts'] = 300.

    m.params['pos_mod_activate'] = 0
    m.params['repump_mod_activate'] = 0 
    m.params['cr_mod_activate'] = 0

    # parameters
    m.params['SSRO_repetitions'] = 5000

    m.params['A_CR_amplitude'] = 40e-9 #5e-9
    m.params['E_CR_amplitude'] = 6e-9 #5e-9

    m.params['SSRO_duration'] = 50

    # ms = 0 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 40e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 8e-9 #10e-9
    
    # m.autoconfig()
    # m.setup()
    
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9


    m.run()
    m.save('ms1')
    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)

