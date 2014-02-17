"""
Script for a simple Decoupling sequence

Right now it is a copy of the electron T1 Measurment script
This will be edited to do a simple decoupling sequence
Made by Adriaan
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

def SimpleDecoupling(name):

    m = pulsar_msmt.DecouplingGateSequence(name)

    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['pulses'])

    '''set experimental parameters'''
        #T1 experiment
    m.params['T1_initial_state'] = 'ms=-1' #currently 'ms=0' or 'ms=-1'
    m.params['T1_readout_state'] = 'ms=-1' #currently 'ms=0' or 'ms=-1'

        #Spin pumping and readout
    m.params['SP_duration'] = 250
    m.params['Ex_RO_amplitude'] = 8e-9 #10e-9
    m.params['A_SP_amplitude'] = 40e-9
    m.params['Ex_SP_amplitude'] = 0.

        #Plot parameters
    m.params['sweep_name'] = 'Times (ms)'
    m.params['sweep_pts'] = m.params['wait_times']/1e3
    m.params['pts'] = len(m.params['sweep_pts']) #Check if we need this line, Tim

        #Set sequence wait time for AWG triggering (After AWG trigger? Tim)
    m.params['sequence_wait_time'] = 0

    m.autoconfig()

    print 'initial_state: ' + m.params['T1_initial_state']
    print 'readout_state: ' + m.params['T1_readout_state']

    '''generate sequence'''
    m.generate_sequence(upload=True)


    #m.run()
    #m.save('ms0')
    #m.finish()

if __name__ == '__main__':
    T1(SAMPLE+'_'+'')
