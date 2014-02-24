"""
Script for a simple Decoupling sequence

Right now it is a copy of the electron T1 Measurment script
This will be edited to do a simple decoupling sequence
Made by Adriaan Rol
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
import measurement.lib.pulsar.DynamicalDecoupling as DD

reload(DD)

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

def SimpleDecoupling(name):

    m = DD.SimpleDecoupling(name)

    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['pulses'])

    '''set experimental parameters'''
        #Spin pumping and readout
    m.params['SP_duration'] = 250
    m.params['Ex_RO_amplitude'] = 8e-9 #10e-9
    m.params['A_SP_amplitude'] = 40e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['repetitions'] = 200


        #Plot parameters
    m.params['sweep_name'] = 'Times (ms)'
    m.params['sweep_pts'] = [1, 10] # m.params['wait_times']/1e3
    m.params['pts'] = len(m.params['sweep_pts']) #Check if we need this line, Tim

        #Set sequence wait time for AWG triggering (After AWG trigger? Tim)
    m.params['sequence_wait_time'] = 0

    m.autoconfig()

    #Decoupling specific parameters
    m.params['Number_of_pulses'] = 8 #linspace()
    m.params['tau_list'] = np.linspace(.7e-6,1e-6,2)
    m.params['Initial_Pulse'] ='pi/2'
    m.params['Final_Pulse'] ='pi/2'

    '''generate sequence'''
    m.generate_sequence(upload=True)


    #m.run()
    #m.save('ms0')
    #m.finish()

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_'+'')
