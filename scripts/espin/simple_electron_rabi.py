"""
LT2 script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

def erabi(name, yellow):
    m = pulsar_msmt.ElectronRabi(name)
    
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])

    if yellow:
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=1
    else:
        ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.green_aom
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']
    

    m.params['pts'] = 21
    pts = m.params['pts']
    
    m.params['MW_pulse_durations'] = np.ones(pts) * 6e-6 # np.linspace(0, 30e-6, pts)
    m.params['mw_frq'] = 2.80e9   
    m.params['mw_power'] = 20
    m.params['repetitions'] = 5000
    
    m.params['MW_pulse_amplitudes'] = np.linspace(0.003, 0.01, pts) # np.ones(pts) * 0.014
    m.params['MW_pulse_frequency'] = m.params['ms-1_cntr_frq'] + (+1) * m.params['N_HF_frq']\
        - m.params['mw_frq']    
    
    # for autoanalysis
    # m.params['sweep_name'] = 'Pulse length (ns)'
    # m.params['sweep_pts'] = m.params['MW_pulse_durations'] * 1e9

    m.params['sweep_name'] = 'Pulse amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10)

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    erabi(SAMPLE+'_'+'find_low_Rabi-frq_ms=-1_mI=+1', yellow=True)
    # erabi(SAMPLE+'_'+'find_MBI_pulse', yellow=True)
