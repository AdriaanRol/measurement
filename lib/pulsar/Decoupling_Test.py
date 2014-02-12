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

    '''
    This is a general class for decoupling gate sequences used in addressing Carbon -13 atoms
    It is a child of PulsarMeasurment
    '''
    mprefix = 'DecouplingGate'

    def autoconfig(self):
        self.params['wait_for_AWG_done'] = 1
        PulsarMeasurement.autoconfig(self)

    def retrieve_resonant_carbon_conditions(GateName):
        '''
        This function retrieves the corresponding tau and N values from the cfg_man
        aswell as the order of the resonance k that is required to calculate phase differences

        Currently This function just returns some fixed values. Ideally it should get them from the cfg_man where they are set in the experiment
        '''
        if GateName = 'StdDecoupling':
            tua = 1.5e-6
            N = 30
        else:
            print 'Gate not in database'
            return

        return tau, N
    def generate_decoupling_sequence_elements(tau,N):
        '''
        This function takes the wait time and the number of pulse-blocks(repetitions) as input
        It returns the start middle and end elements aswell as the total time and time cut of at the edges
        It creates three elements:
        tau_start - Pi - tau
        tau-pi-tau-tau-pi-tau
        tau-pi-tau_end
        '''
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future.
        X = pulselib.MW_IQmod_pulse('electron Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_modulation_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['Pi_pulse_duration'],
            amplitude = self.params['Pi_pulse_amp'])

        #Also checks if planned wait times lead to impossible sequences
        # Wait-times
        pulse_tau = tau - self.params['Pi_pulse_duration']/2.0 #To correct for pulse duration
        pulse_tau_shortened = tau - self.params['Pi_pulse_duration']/2.0 - #something to make it
        if tau <0.5e-6:
            print 'Error: total element duration smaller than 1 mu Impossible to create edge elements, Requires more coding to implement'
            # This error is not expected immediately as resonances we would like to address are beyond this window. It would requiring a bit different to get a fingerprint for the
            return
        elif pulse_tau<0:
            print 'Error: tau is smaller than pi-pulse duration. Cannot generate decoupling element'
            return



        else:
            #continue executing code
        #Suzanne uses (CORPSE_pi.length - 2*self.params['MW_pulse_mod_risetime'])/2 to correct for

            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = pulse_tau_shortened, amplitude = 0.) #the unit waittime is 10e-6 s
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = pulse_tau_shortened, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.

            #Decoupling element/waveform Start
            e_start = element.Element('Decoupling Element',  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_start.append(T_before_p)
            e_start.append(pulse.cp(X))
            e_start.append(T)
            list_of_elements.append(e_start)

            e_middle = element.Element('Decoupling Element',  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_middle.append(T)
            e_middle.append(pulse.cp(X))
            e_middle.append(T)
            e_middle.append(T)
            e_middle.append(pulse.cp(X))
            e_middle.append(T)
            list_of_elements.append(e_middle)

            e_end = element.Element('Decoupling Element',  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_end.append(T)
            e_end.append(pulse.cp(X))
            e_end.append(T_after_p)
            list_of_elements.append(e_end)
            #Build in checks to prevent impossible sequences from being uploaded

                        ### create the elements/waveforms from the basic pulses ###
            list_of_elements = []
            #Check for multiple of 4 ns : np.ceil(element/4e-9)*4e-9


            return e_start,e_middle, e_end, total_sequence_time, time_removed_from_edges, N
    def Determine_length_and_type_of_Glue_elements(GateSequence,TotalsequenceTimes,TimeRemoved) :
    def generate_glue_elements(length, type):
        '''
        Generates the elements between the decoupling sequences
        '''
        if type == 'pi/2':
            X = pulselib.MW_IQmod_pulse('electron Pi-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['MW_modulation_frequency'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['Pi_pulse_duration'],
                amplitude = self.params['Pi_pulse_amp'])
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = 100e-9, amplitude = 0.) #the unit waittime is 10e-6 s
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = 850e-9, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.


                        #Pi-pulse element/waveform
        e = element.Element('Pi_pulse',  pulsar=qt.pulsar,
                global_time = True)
        e.append(T_before_p)
        e.append(pulse.cp(X))
        e.append(T_after_p)

        else:
            pass
    def combine_to_sequence():
        '''
        Combines all the generated elements to a sequence for the AWG
        '''
        list_of_elements = []
        seq = pulsar.Sequence('Decoupling Sequence')
        for e in elements:


            seq.append(name='Init_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
            seq.append(name='ElectronT1_wait_time_%d'%i, wfname='T1_wait_time', trigger_wait=False,repetitions=self.params['wait_times'][i]/100)
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

    def generate_AWG_sequence(upload=True):
        '''
        This is the function that programs the measurement specific sequence to the AWG
        This is overwritten in childclasses that program different experiments
        Might be better to locate this in a childclass for the specific measurment but not now :)
        '''
        InputGateSequence = ['ePi/2','StdDecoupling','ePi/2']
        for InputGate in InputGateSequence:
            if InputGate[0] == 'ePi/2':   #Very specific, just because we are not doing the general case yet but a simple version







        # upload the waveforms to the AWG
        if upload:
            qt.pulsar.upload(*list_of_elements)
            # program the AWG
            qt.pulsar.program_sequence(seq)


    # class Gate(object):
    #         '''
    #         Class made specifically for the Resonant Carbon decoupling gates
    #         If C_index is 0 no carbon is addressed and the gates apply to the electron
    #         Gate corresponds to the type of gate to be implemented, this is a string
    #         '''
    #         def __init__(Gate,C_index):
    #             self.Gate = Gate
    #             self.C_index = C_index # index 0 corresponds to the electron





class ThreeQubitMB_QEC(DecouplingGateSequence):
    '''
    The thre qubit MB QEC is a child class of the more general decoupling gate sequence class
    It contains a specific gate sequence with feedback loops and other stuff
    !NB: It is currently EMPTY

    '''
class SimpleDecouplingSequence(DecouplingGateSequence):
    '''
    The most simple version of a decoupling sequence
    Only contains a simple decoupling sequence no carbon addressing and stuff
    '''
    def __init__(N,tau):
        self.N = N
        self.tau = tau


