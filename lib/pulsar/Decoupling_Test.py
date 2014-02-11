'''
This is modified version of the ElectronT1 class from pulsar.py
eventually this class should be placed in that file again
File made by Adriaan
'''

import msvcrt
import numpy as np
import qt
import hdf5_data as h5
import logging

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


class DecouplingGateSequence(PulsarMeasurement):

    mprefix = 'DecouplingGate'

    class Gate(object):
            '''
            A class for Carbon Gate and elctron gate objects
            index 0 corresponds to the electron
            '''
            def __init__(self, acts_on, C_index, Gate):
                self.acts_on = acts_on #is either 'Carbon' or 'electron' subclass is prolly neither but don't really need it here
                self.C_index = C_index # index 0 corresponds to the electron
                self.Gate = Gate

    def retrieve_resonant_carbon_conditions(Carbon_gate):
        '''
        This function retrieves the corresponding tau and N values from the cfg_man
        aswell as the order of the resonance k that is required to calculate phase differences
        '''

        if Carbon_gate != 'Carbon' :
            print 'Error: Gate not acting on Carbon'
            return

        # some code to retrieve  tau, N and k

        elif Carbon_gate.Gate =='Pi' :
            N = N_cfgman
        elif Carbon_gate.Gate == 'Pi/2' :
            N = N_cfgman /2
        else:
            print 'Error: Gate type not recognized for Carbon: %d Gate: %s' %(Carbon_gate.C_index, Carbon_gate.Gate)
        return tau, N , k


    def generate_decoupling_sequence(tau,N):
        '''
        This function takes the wait time and the number of pulses blocks as input and returns a sequence with the edges (wait time) cut of
        '''
        # Generate the three different elements start, middle **N, end based on pulses
        #return  three elements and N or sequence depending on merging capabilities

    def combine_to_sequence():
    # create a sequence from the elements
    #This should be rewritten so that it works for an arbitrary nummer of elements
        seq = pulsar.Sequence('ElectronT1_sequence')

        for i in range(len(self.params['wait_times'])):
            seq.append(name='Pi_pulse_with_wait_time_%d'%i,wfname='Pi_pulse_with_wait_time',trigger_wait=True)
            if self.params['wait_times'][i]/100 !=0:
                seq.append(name='ElectronT1_wait_time_%d'%i, wfname='ElectronT1_wait_time', trigger_wait=False,repetitions=self.params['wait_times'][i]/100)
            seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ElectronT1_ADwin_trigger', trigger_wait=False)

    #the actual code executed in this class
    #!!!! Gate sequence has to be defined somewhere it is a list of Gate objects

    #The phase correction gate is a 'glue' element to stick between two carbon gates
    PhaseCorrectionGate = Gate('electron',0,'Phase_Gate')

    gate_seq = [None]*len(Input_Gate_Sequence)

    #First loop rewrites the sequence so that it alternates between carbon elements and 'glue' elements or electron gates
    Modified_Input_Gate_Sequence = Input_Gate_Sequence
    for i, gate in enumerate(Input_Gate_Sequence):
        if gate.acts_on == last_gate.acts_on:
            Modified_Input_Gate_Sequence.insert(i,PhaseCorrectionGate)
        last_gate = gate

    for i, gate in enumerate(Modified_Input_Gate_Sequence)

        if gate.acts_on != 'Carbon' :
            pass
        else:
            tau,N, k = retrieve_resonant_carbon_conditions(Carbon_gate)
            gate_seq[i] = generate_decoupling_sequence(tau,N)




    # upload the waveforms to the AWG
    if upload:
        qt.pulsar.upload(*elements)

    # program the AWG
    qt.pulsar.program_sequence(seq)







class ThreeQubitMB_QEC(DecouplingGateSequence)
    '''
    The thre qubit MB QEC is a child class of the more general decoupling gate sequence class
    It contains a specific gate sequence with feedback loops and other stuff
    '''
