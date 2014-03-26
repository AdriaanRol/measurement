"""
Script for e-spin T1 using the pulsar sequencer.
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def T1(name):

    m = pulsar_msmt.ElectronT1(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    '''set experimental parameters'''
        #T1 experiment
    m.params['T1_initial_state'] = 'ms=0' #currently 'ms=0' or 'ms=-1'
    m.params['T1_readout_state'] = 'ms=0' #currently 'ms=0' or 'ms=-1'
    m.params['wait_times'] =  np.linspace(0,1e3,6) #in us, values must be divisible by the repeat element
    m.params['wait_time_repeat_element'] = 100      #in us, this element is repeated to create the wait times
    m.params['repetitions'] = 100

        #Spin pumping and readout
    #m.params['SP_duration'] = 250
    #m.params['Ex_RO_amplitude'] = 8e-9 #10e-9
    #m.params['A_SP_amplitude'] = 40e-9
    #m.params['Ex_SP_amplitude'] = 0.

        #Plot parameters
    m.params['sweep_name'] = 'Times (ms)'
    m.params['sweep_pts'] = m.params['wait_times']/1e3
    m.params['pts'] = len(m.params['sweep_pts']) #Check if we need this line, Tim

        #Set sequence wait time for AWG triggering
    m.params['sequence_wait_time'] = 0

    m.autoconfig()

    print 'initial_state: ' + m.params['T1_initial_state']
    print 'readout_state: ' + m.params['T1_readout_state']

    '''generate sequence'''
    m.generate_sequence(upload=True)
    m.run()
    m.save('ms0')
    m.finish()

if __name__ == '__main__':
    T1(SAMPLE+'_'+'')
