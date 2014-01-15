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



    m.params['repump_mod_DAC_channel'] = 4
    m.params['cr_mod_DAC_channel']     = ssro.AdwinSSRO.adwin.get_dac_channels()['gate']
    m.params['cr_mod_control_offset']  =  0.0
    m.params['cr_mod_control_amp']     =  0.1 #V
    m.params['repump_mod_control_offset']  =  4.0
    m.params['repump_mod_control_amp']     =  1.0 #V
    m.params['atto_positions'] = [m.adwin.get_dac_voltage('atto_x'), m.adwin.get_dac_voltage('atto_y'), m.adwin.get_dac_voltage('atto_z')]
    m.set_adwin_process_variable_from_params('atto_positions')
    m.params['pos_mod_control_amp'] =  0.1 #0.03
    m.params['pos_mod_fb'] = 0.0
    m.params['pos_mod_min_counts'] = 300.

    m.params['pos_mod_activate'] = 0
    m.params['repump_mod_activate'] = 0 
    m.params['cr_mod_activate'] = 0

    # parameters
    m.params['SSRO_repetitions'] = 5000

    m.params['A_CR_amplitude'] = 5e-9 #5e-9
    m.params['E_CR_amplitude'] = 5e-9 #5e-9

    m.params['SSRO_duration'] = 50

    # ms = 0 calibration
    m.params['SP_duration'] = 50
    m.params['A_SP_amplitude'] = 5e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 5e-9 #10e-9

    # m.autoconfig()
    # m.setup()
    

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9

    m.params['atto_positions_after'] = m.adwin_var(('atto_positions',3))
    m.adwin.set_dac_voltage(('atto_x',m.params['atto_positions_after'][0]))
    m.adwin.set_dac_voltage(('atto_y',m.params['atto_positions_after'][1]))
    m.adwin.set_dac_voltage(('atto_z',m.params['atto_positions_after'][2]))

    #m.run()
    #m.save('ms1')

    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)

