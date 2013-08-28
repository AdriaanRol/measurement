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

def erabi(name, msp1=False):
    m = pulsar_msmt.ElectronRabi(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['samples']['sil9'])

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration']=m.params['green_repump_duration']
    m.params['repump_amplitude']=m.params['green_repump_amplitude']
    

    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['MW_pulse_durations'] = np.linspace(0,150e-9,pts)

    if msp1:
        m.params['mw_frq'] = 2.90e9
        m.params['ms_cntr_frq'] =  m.params['ms+1_cntr_frq']
    else:
        m.params['mw_frq'] = 2.80e9
        m.params['ms_cntr_frq'] =  m.params['ms-1_cntr_frq']

    m.params['mw_power'] = 20
    
    m.params['repetitions'] = 1000
    m.params['MW_pulse_amplitudes'] = np.ones(pts) * 0.9
    m.params['MW_pulse_frequency'] = m.params['ms_cntr_frq'] - m.params['mw_frq']
    m.params['MW_pulse_mod_risetime'] = 10e-9

    
    m.params['sweep_name'] = 'Pulse length (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9 

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10)

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    erabi('ElectronRabi_sil9', msp1=False)
