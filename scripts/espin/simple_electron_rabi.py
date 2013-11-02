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
    
    m.params['MW_pulse_durations'] =  np.ones(pts) * 8.3e-6
    m.params['repetitions'] = 5000
    
    m.params['MW_pulse_amplitudes'] = np.linspace(0.002,0.007,pts)
    m.params['MW_pulse_frequency'] = m.params['ms-1_cntr_frq'] + (+1) * m.params['N_HF_frq']\
        - m.params['mw_frq']    
    
    # for autoanalysis
    # m.params['sweep_name'] = 'Pulse length (ns)'
    # m.params['sweep_pts'] = m.params['MW_pulse_durations'] 

    m.params['sweep_name'] = 'Pulse amplitudes (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10)

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    # erabi(SAMPLE+'_'+'find_high_rabi_sil1')
    erabi(SAMPLE+'_'+'find_slow_pulse_mI=-1')
