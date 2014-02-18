'''
This is modified version of the ElectronT1 class from PULSAR.PY
eventually this class should be placed in that file again
File made by Adriaan Rol
'''

import msvcrt
import numpy as np
import qt
import hdf5_data as h5
import logging

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro.pulsar import PulsarMeasurement


class DynamicalDecoupling(PulsarMeasurement):

    '''
    This is a general class for decoupling gate sequences used in addressing Carbon -13 atoms
    It is a child of PulsarMeasurment
    '''
    mprefix = 'DecouplingSequence'

    def autoconfig(self):
        self.params['wait_for_AWG_done'] = 1
        PulsarMeasurement.autoconfig(self)

    def retrieve_resonant_carbon_conditions(self,GateName):
        '''
        This function retrieves the corresponding tau and N values from the cfg_man
        aswell as the order of the resonance k that is required to calculate phase differences

        Currently This function just returns some fixed values. Ideally it should get them from the cfg_man where they are set in the experiment
        '''
        if GateName == 'StdDecoupling':
            tau = self.params['tau']
            N = self.params['Number_of_pulses']
        elif GateName == 'Carbon1' :
            tau = self.params['tau_C1'] #From the measurement script would be better if it comes from config file
            N = self.params['N_C1']

        else:
            print 'Gate not in database'
            print GateName
            return
        return tau, N

    def generate_decoupling_sequence_elements(self,tau,N,prefix):
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
        pulse_tau_shortened = tau - self.params['Pi_pulse_duration']/2.0 # - something to make it

        #Checks to prevent impossible pulse sequences from being created
        if tau <0.5e-6:
            print 'Error: total element duration smaller than 1 mu Impossible to create edge elements, Requires more coding to implement'
            # This error is not expected immediately as resonances we would like to address are beyond this window. It would requiring a bit different to get a fingerprint for the
            return
        elif pulse_tau<0:
            print 'Error: tau is smaller than pi-pulse duration. Cannot generate decoupling element'
            return
        else:

        ## Pulses
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future. Might also need Y pulse
            X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['MW_modulation_frequency'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['Pi_pulse_duration'],
                amplitude = self.params['Pi_pulse_amp'])
            #Y pulse is needed for XY decoupling schemse
            # !NB currently identical to X pulse
            Y = pulselib.MW_IQmod_pulse('electron Y-Pi-pulse',
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
            e_start = element.Element('Initial %s Decoupling Element' %prefix,  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_start.append(T_before_p)
            e_start.append(pulse.cp(X))
            e_start.append(T)
            list_of_elements.append(e_start)

            #Currently middle is XY2 with an if statement based on the value of N this can be optimised
            e_middle = element.Element('Repeating %s Decoupling Element' %prefix,  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_middle.append(T)
            e_middle.append(pulse.cp(X))
            e_middle.append(T)
            e_middle.append(T)
            e_middle.append(pulse.cp(Y))
            e_middle.append(T)
            list_of_elements.append(e_middle)

            e_end = element.Element('Final %s Decoupling Element' %prefix,  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_end.append(T)
            e_end.append(pulse.cp(X))
            e_end.append(T_after_p)
            list_of_elements.append(e_end)

            #Build in checks to prevent impossible sequences from being uploaded
            ### create the elements/waveforms from the basic pulses ###
            #Check for multiple of 4 ns : np.ceil(element/4e-9)*4e-9
            total_sequence_time=0
            time_removed_from_edges=0

            list_of_repetitions = [1, N/2-1, 1]

            return [list_of_elements, list_of_repetitions, [total_sequence_time, time_removed_from_edges]]

    def Determine_length_and_type_of_Connection_elements(self,GateSequence,TotalsequenceTimes,TimeRemoved) :
        '''
        Empty function, needs to be able to determine the length and type of glue gates in the future
        '''
        pass

    def generate_connection_element(self,length, Gate_type,prefix):
        '''
        Generates an element that connects to decoupling elements
        It can be at the start, the end or between sequence elements

        '''
        if Gate_type == 'pi/2':
            X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['MW_modulation_frequency'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['Pi_pulse_duration']/2.0, #Divided by 2.0 to get a pi/2 pulse (not RIGHT)
                amplitude = self.params['Pi_pulse_amp'])
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = 100e-9, amplitude = 0.) #the unit waittime is 10e-6 s
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = 850e-9, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.


                        #Pi-pulse element/waveform
            e = element.Element('%s Pi_2_pulse' %prefix,  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)
            return [e]

        else:
            print 'this is not programmed yet '
            return


    def combine_to_sequence(self,list_of_elements,list_of_repetitions):
        '''
        Combines all the generated elements to a sequence for the AWG
        '''
        #Ideally this would work for an arbitrary number of elements lists and repetition lists
        seq = pulsar.Sequence('Decoupling Sequence')

        for ind, e in enumerate(list_of_elements):
            if ind == 0:
                seq.append(name=e.name, wfname=e.name,
                    trigger_wait=True,repetitions = list_of_repetitions[ind])
            # elif ind == len(list_of_elements):
            #     # adds a trigger element to the final element of the sequence
            #     seq.append(name=e.name, wfname=e.name,
            #        trigger_wait=False,repetitions = list_of_repetitions[ind])

            #     Trig = pulse.SquarePulse(channel = 'adwin_sync',
            #         length = 5e-6, amplitude = 2)
            #     Trig_element = element.Element('ADwin_trigger', pulsar=qt.pulsar,
            #         global_time = True)
            #     Trig_element.append(Trig)
            #     seq.append(Trig_element)
            else:
                seq.append(name=e.name, wfname=e.name,
                    trigger_wait=False,repetitions = list_of_repetitions[ind])
        return seq

class AdvancedDecouplingSequence(DynamicalDecoupling):
    '''
    The advanced decoupling sequence is a child class of the more general decoupling gate sequence class
    It contains a specific gate sequence with feedback loops and other stuff
    !NB: It is currently EMPTY
    '''
    def generate_sequence(self,upload=False):
        '''
        The function that is executed when a measurement script is executed
        It calls the different functions in this class
        For now it is simplified and can only do one type of decoupling sequence
        '''
        #load_input_gate_sequence()
        #For now we use a placeholder sequence
        #tau, N = DynamicalDecoupling.retrieve_resonant_carbon_conditions('StdDecoupling')
        tau = self.params['tau']
        N = self.params['Number_of_pulses']
        list_of_decoupling_elements, list_of_decoupling_reps, decoupling_meta_data = DynamicalDecoupling.generate_decoupling_sequence_elements(self,tau,N)
        #duration, Gate_type = Determine_length_and_type_of_Connection_elements(Gate_sequence,total_sequencetimes,times_removed)

        duration = self.params['Init_Pulse_Duration']
        Gate_type = self.params['Initial_Pulse']
        initial_pi_2 = DynamicalDecoupling.generate_connection_element(self,duration, Gate_type)
        final_pi_2 = initial_pi_2

        #very sequence specific
        initial_pi_2
        list_of_elements = []
        list_of_elements.extend(initial_pi_2)
        list_of_elements.extend(list_of_decoupling_elements)
        list_of_elements.extend(final_pi_2)

        list_of_repetitions = [1]+ list_of_decoupling_reps+[1]
        print list_of_repetitions
        seq = DynamicalDecoupling.combine_to_sequence(self,list_of_elements,list_of_repetitions)

        if upload:
            qt.pulsar.upload(*list_of_elements)
            # program the AWG
            qt.pulsar.program_sequence(seq)
        else:
            print 'upload = false, no sequence uploaded to AWG'

class SimpleDecoupling(DynamicalDecoupling):
    '''
    The most simple version of a decoupling sequence
    Contains initial pulse, decoupling sequence and final pulse.
    '''

    def generate_sequence(self,upload=False):
        '''
        The function that is executed when a measurement script is executed
        It calls the different functions in this class
        For now it is simplified and can only do one type of decoupling sequence
        '''
        tau = self.params['tau']
        N = self.params['Number_of_pulses']
        prefix = 'electron'
        list_of_decoupling_elements, list_of_decoupling_reps, decoupling_meta_data = DynamicalDecoupling.generate_decoupling_sequence_elements(self,tau,N,prefix)


        Gate_type = self.params['Initial_Pulse']
        duration = self.params['Initial_Pulse_Duration']
        prefix = 'initial'
        initial_pi_2 = DynamicalDecoupling.generate_connection_element(self,duration, Gate_type,prefix)

        duration = self.params['Final_Pulse_Duration']
        Gate_type = self.params['Final_Pulse']
        prefix = 'final'
        final_pi_2 = DynamicalDecoupling.generate_connection_element(self,duration, Gate_type,prefix)

        Trig = pulse.SquarePulse(channel = 'adwin_sync',
            length = 5e-6, amplitude = 2)
        Trig_element = element.Element('ADwin_trigger', pulsar=qt.pulsar,
            global_time = True)
        Trig_element.append(Trig)

        #very sequence specific
        list_of_elements = []
        list_of_elements.extend(initial_pi_2)
        list_of_elements.extend(list_of_decoupling_elements)
        list_of_elements.extend(final_pi_2)
        list_of_elements.extend([Trig_element])


        list_of_repetitions = [1]+ list_of_decoupling_reps+[1,1]
        print list_of_repetitions
        seq = DynamicalDecoupling.combine_to_sequence(self,list_of_elements,list_of_repetitions)

        if upload:
            qt.pulsar.upload(*list_of_elements)
            # program the AWG
            qt.pulsar.program_sequence(seq)
        else:
            print 'upload = false, no sequence uploaded to AWG'


