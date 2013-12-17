"""
Script for e-spin T1 using the pulsar sequencer
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

def T1(name):
    
    m = pulsar_msmt.ElectronT1(name)
    
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['pulses'])

    #set evolution time    
    m.params['wait_times'] =  np.linspace(0,1e6,11) #np.ones(pts) * 50e-9 #np.linspace(5, 105, pts) * 1e-9 #
    m.params['repetitions'] = 200
    #set plot variables
    m.params['sweep_name'] = 'Times (ms)'
    m.params['sweep_pts'] = m.params['wait_times']/1e3
    m.params['pts'] = len(m.params['sweep_pts']) #see if we need this, tim
    #set sequence wait time for AWG triggering
    m.params['sequence_wait_time'] = 0
    
    #generate sequence
    m.autoconfig() 
    m.generate_sequence(upload=True)
    
     #Set SSRO parameters
    m.params['SP_duration'] = 250
    m.params['Ex_RO_amplitude'] = 8e-9 #10e-9
    
    # ms = 0 start
        
    print 'start ms0'
    
    m.params['A_SP_amplitude'] = 40e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.run()
    m.save('ms0')
    
    # ms = 1 calibration
    
    print 'start ms1'
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9 #10e-9
    m.run()
    m.save('ms1')

    m.finish()
    
if __name__ == '__main__':
    # erabi(SAMPLE+'_'+'find_high_rabi_sil1')
    T1(SAMPLE+'_'+'')
