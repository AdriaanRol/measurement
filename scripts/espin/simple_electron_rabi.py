"""
Script for e-spin manipulations using the pulsar sequencer
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
    m.params['repetitions'] = 1000

    m.params['wait_after_pulse_duration']=0
    m.params['wait_after_RO_pulse_duration']=0
    
    m.params['mw_frq'] = 2.2e9 
    m.params['MW_pulse_frequency'] = m.params['ms-1_cntr_frq'] - m.params['mw_frq']  
    print m.params['ms-1_cntr_frq']

    #m.params['MW_pulse_durations'] =  np.linspace(0, 200, pts) * 1e-9 
    m.params['MW_pulse_durations'] =  np.ones(pts)*40*1e-9 #np.linspace(0, 200, pts) * 1e-9 

    #m.params['MW_pulse_amplitudes'] = np.ones(pts) *0.55
    m.params['MW_pulse_amplitudes'] = np.linspace(0,0.7,pts)
    
    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    #m.params['sweep_name'] = 'Pulse durations (ns)'
    m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'
    
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10) #Redundant because defined in m.autoconfig? Tim

    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    # erabi(SAMPLE+'_'+'find_high_rabi_sil1')
    erabi(SAMPLE+'_'+'Rabi')
