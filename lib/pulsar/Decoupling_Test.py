'''
This is modified version of the ElectronT1 class from PULSAR.PY
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
    mprefix = 'DecouplingSequence'

    def autoconfig(self):
        self.params['wait_for_AWG_done'] = 1
        PulsarMeasurement.autoconfig(self)


    # upload the waveforms to the AWG
    def generate_sequence(self,upload=False):
        '''
        The function that is executed when a measurement script is executed
        It calls the different functions in this class
        For now it is simplified and can only do one type of decoupling sequence
        '''
        #load_input_gate_sequence()
        #For now we use a placeholder sequence
        tau, N = retrieve_resonant_carbon_conditions('StdDecoupling')
        list_of_decoupling_elements, list_of_decoupling_reps, decoupling_meta_data = generate_decoupling_sequence_elements(tau,N)
        #duration, Gate_type = Determine_length_and_type_of_Glue_elements(Gate_sequence,total_sequencetimes,times_removed)

        duration = 1.5e-6
        Gate_type = 'pi/2'
        initial_pi_2 = generate_glue_element(duration, Gate_type)
        final_pi_2 = initial_pi_2

        #very sequence specific
        list_of_elements = []
        list_of_elements.extend(initial_pi_2)
        list_of_elements.extend(list_of_decoupling_elements)
        list_of_elements.extend(final_pi_2)

        list_of_repetitions = [1,list_of_decoupling_reps[0],1]
        seq = combine_to_sequence(list_of_elements,list_of_repetitions)

        if upload:
            qt.pulsar.upload(*list_of_elements)
            # program the AWG
            qt.pulsar.program_sequence(seq)
        else:
            print 'upload = false, no sequence uploaded to AWG'





    def retrieve_resonant_carbon_conditions(GateName):
        '''
        This function retrieves the corresponding tau and N values from the cfg_man
        aswell as the order of the resonance k that is required to calculate phase differences

        Currently This function just returns some fixed values. Ideally it should get them from the cfg_man where they are set in the experiment
        '''
        if GateName = 'StdDecoupling':
            tua = 1.5e-6
            N = 32
            print 'Using arbitrary interpulse delay and number of pulses of tau =  1.5e-6 and N = 32'
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
        #Also checks if planned wait times lead to impossible sequences
        # Wait-times
        pulse_tau = tau - self.params['Pi_pulse_duration']/2.0 #To correct for pulse duration
        pulse_tau_shortened = tau - self.params['Pi_pulse_duration']/2.0 - #something to make it

        #Checks to prevent impossible pulse sequences from being created
        if tau <0.5e-6:
            print 'Error: total element duration smaller than 1 mu Impossible to create edge elements, Requires more coding to implement'
            # This error is not expected immediately as resonances we would like to address are beyond this window. It would requiring a bit different to get a fingerprint for the
            return
        elif pulse_tau<0:
            print 'Error: tau is smaller than pi-pulse duration. Cannot generate decoupling element'
            return
        else:

        ## Puplses
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future. Might also need Y pulse
            X = pulselib.MW_IQmod_pulse('electron Pi-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['MW_modulation_frequency'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['Pi_pulse_duration'],
                amplitude = self.params['Pi_pulse_amp'])
            #Y pulse is needed for XY decoupling schemse
            # !NB currently identical to X pulse
            Y = pulselib.MW_IQmod_pulse('electron Pi-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['MW_modulation_frequency'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['Pi_pulse_duration'],
                amplitude = self.params['Pi_pulse_amp'])

            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = pulse_tau, amplitude = 0.)
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = pulse_tau_shortened, amplitude = 0.) #the unit waittime is 10e-6 s
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = pulse_tau_shortened, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.

            # add sequence elements to a list
            list_of_elements = []
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
            #Check for multiple of 4 ns : np.ceil(element/4e-9)*4e-9

            list_of_repetitions = 1, N-2, 1
            return [list_of_elements, list_of_repetitions, [total_sequence_time, time_removed_from_edges]]

    def Determine_length_and_type_of_Glue_elements(GateSequence,TotalsequenceTimes,TimeRemoved) :
    '''
    Empty function, needs to be able to determine the length and type of glue gates in the future
    '''


    def generate_glue_element(length, Gate_type):
        '''
        Generates the elements between the decoupling sequences
        '''
        if type == 'pi/2':
            X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['MW_modulation_frequency'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['Pi_pulse_duration/2.0'], #Divided by 2.0 to get a pi/2 pulse (not RIGHT)
                amplitude = self.params['Pi_pulse_amp'])
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = 100e-9, amplitude = 0.) #the unit waittime is 10e-6 s
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = 850e-9, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.


                        #Pi-pulse element/waveform
            e = element.Element('Pi_2_pulse',  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)
            return [e]

        else:
            print 'this is not programmed yet '
            return


    def combine_to_sequence(list_of_elements,list_of_repetitions):
        '''
        Combines all the generated elements to a sequence for the AWG
        '''
        #Ideally this would work for an arbitrary number of elements lists and repetition lists
        seq = pulsar.Sequence('Decoupling Sequence')
        for ind, e in enumerate list_of_elements:
            if ind = 0:
                seq.append(name=e.name, wfname=e.name,
                    trigger_wait=True,repetitions = list_of_repetitions[ind])
            else:
                seq.append(name=e.name, wfname=e.name,
                    trigger_wait=False,repetitions = list_of_repetitions[ind])
        return seq

class AdvancedDecouplingSequence(DecouplingGateSequence):
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


