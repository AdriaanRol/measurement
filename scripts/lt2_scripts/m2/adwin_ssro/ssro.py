"""
LT2 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import msvcrt

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

# set the static variables for LT2
ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt2_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM']
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']

def calibration(name,yellow=False):
    
        
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])    
        
    # parameters
    m.params['SSRO_repetitions'] = 5000
    
    #repump settings
    _set_repump_settings(m,yellow)
    
    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 70e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 5e-9 #10e-9
    
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 5e-9 #10e-9
    m.params['Ex_RO_amplitude'] = 5e-9 #10e-9

    m.run()
    m.save('ms1')
    m.finish()
    
def RO_saturation_power(name, yellow=False):
    m = ssro.AdwinSSRO('RO_saturation_power_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    
    #repump settings
    _set_repump_settings(m,yellow)
    
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitudes'] = np.arange(20)*2e-9 + 2e-9

    for p in m.params['Ex_RO_amplitudes']:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
        m.params['Ex_RO_amplitude'] = p
        m.run()
        m.save('P_%dnW' % (p*1e9))
        
    m.finish()

def SP_RO_saturation_power(name, yellow=False):
    m = ssro.AdwinSSRO('RO_saturation_power_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    
    #repump settings
    _set_repump_settings(m,yellow)
    
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitudes'] = np.arange(20)*2e-9 + 2e-9

    for p in m.params['Ex_RO_amplitudes']:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
        m.params['Ex_RO_amplitude'] = p
        m.params['A_SP_amplitude'] = 0
        m.run()
        m.save('P_%dnW' % (p*1e9))
        
    m.finish()
    
def _set_repump_settings(m,yellow):
    if yellow:
        qt.instruments['GreenAOM'].set_power(0)
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
    else:
        qt.instruments['YellowAOM'].set_power(0)
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']
