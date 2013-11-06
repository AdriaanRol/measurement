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

def erabi(name):
    m = pulsar_msmt.ElectronRabi(name)
    
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])

    m.params['pts'] = 21
    pts = m.params['pts']
    
    m.params['MW_pulse_durations'] = np.ones(pts) * 61e-9 #np.linspace(5, 105, pts) * 1e-9 # 
    m.params['repetitions'] = 1000
    
    m.params['MW_pulse_amplitudes'] = np.linspace(0., 0.7,pts)
    m.params['mw_frq'] = 2.8e9 # m.params['ms-1_cntr_frq']
    m.params['MW_pulse_frequency'] = m.params['ms-1_cntr_frq'] - m.params['mw_frq']  
    
    # for autoanalysis
    m.params['sweep_name'] = 'Pulse amps (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    # m.params['sweep_name'] = 'Pulse amplitudes (V)'
    # m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10)

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    # erabi(SAMPLE+'_'+'find_high_rabi_sil1')
    erabi(SAMPLE+'_'+'find_pi')
