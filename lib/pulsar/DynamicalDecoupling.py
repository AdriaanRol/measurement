'''
This is modified version of the ElectronT1 class from PULSAR.PY
Work in progress
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

        2*tau = tau_cut +tau_shortened+ fast_pi_duration + tau_pulse
        '''
        #Generate the basic pulses
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future.
        X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_modulation_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'],
            phase = self.params['X_phase'])


        Y = pulselib.MW_IQmod_pulse('electron Y-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_modulation_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'],
            phase = self.params['Y_phase'])

        minimum_AWG_elementsize = 1e-6 #AWG elements/waveforms have to be 1 mu s
        # would be cleaner to also have AWG quantization =4e-9 as a variable but not done for readability
        fast_pi_duration = self.params['fast_pi_duration']
        pulse_tau = tau - fast_pi_duration/2.0 #To correct for pulse duration

        # initial checks to see if sequence is possible
        if N%2!=0:
            print 'Error: odd number of pulses, impossible to do decoupling control sequence'
        if pulse_tau<0:
            print 'Error: tau is smaller than pi-pulse duration. Cannot generate decoupling element'
            return
        elif tau <0.5e-6:
            print '''Error: total element duration smaller than 1 mu s.
            Requires more coding to implement
            '''
            return
        #Next part of the if statements checks what type of
        elif N%8 == 0:
            #Generate XY8 Decoupling sequence

            #Calculate time to be cut
            #DOUBLE CHECK, NOW JUST MODIFIED OLD CODE TEST THIS!!!!
            element_duration_without_edge = 3*tau + fast_pi_duration/2.0
            if element_duration_without_edge  > (minimum_AWG_elementsize+36e-9): #+20 ns is to make sure that elements always have a minimal size
                tau_shortened = np.ceil((element_duration_without_edge+ 36e-9)/4e-9)*4e-9 -element_duration_without_edge
            else:
                tau_shortened = minimum_AWG_elementsize - element_duration_without_edge
                tau_shortened = np.ceil(tau_shortened/(4e-9))*(4e-9)
            tau_cut = tau - tau_shortened - fast_pi_duration/2.0

            # print 'tau =' +str(tau)
            # print 'tau_pulse = ' +str(pulse_tau)
            # print 'tau shortened= ' + str(tau_shortened)
            # print 'fast_pi_duration = '+ str(fast_pi_duration)
            # print ' tau_cut='+ str(tau_cut)
            # Make the delay pulses
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = pulse_tau, amplitude = 0.)
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)

            #Combine pulses to elements/waveforms and add to list of elements
            list_of_elements = []
            e_XY_start = element.Element('XY Initial %s XY8-Decoupling Element, tau = %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)# Not sure if thgenerate_decoupling_sequence_elementse name here is correct.
            e_XY_start.append(T_before_p)
            e_XY_start.append(pulse.cp(X))
            e_XY_start.append(T)
            e_XY_start.append(T)
            e_XY_start.append(pulse.cp(Y))
            e_XY_start.append(T)
            list_of_elements.append(e_XY_start)

            #Currently middle is XY2 with an if statement based on the value of N this can be optimised
            e_XY = element.Element('XY Rep %s XY8-Decoupling Element, tau= %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_XY.append(T)
            e_XY.append(pulse.cp(X))
            e_XY.append(T)
            e_XY.append(T)
            e_XY.append(pulse.cp(Y))
            e_XY.append(T)
            list_of_elements.append(e_XY)

            #Currently middle is XY2 with an if statement based on the value of N this can be optimised
            e_YX = element.Element('YX Rep %s XY8-Decoupling Element, tau= %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_YX.append(T)
            e_YX.append(pulse.cp(Y))
            e_YX.append(T)
            e_YX.append(T)
            e_YX.append(pulse.cp(X))
            e_YX.append(T)
            list_of_elements.append(e_YX)

            e_YX_end = element.Element('YX Final %s XY-8 Decoupling Element, tau = %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_YX_end.append(T)
            e_YX_end.append(pulse.cp(Y))
            e_YX_end.append(T)
            e_YX_end.append(T)
            e_YX_end.append(pulse.cp(X))
            e_YX_end.append(T_after_p)
            list_of_elements.append(e_YX_end)

        else:
            #Generate an XY4 (+XY) decoupling sequence

            # Calculate the time to be cut
            element_duration_without_edge = tau + fast_pi_duration/2.0
            if element_duration_without_edge  > (minimum_AWG_elementsize+36e-9): #+20 ns is to make sure that elements always have a minimal size
                tau_shortened = np.ceil((element_duration_without_edge+ 36e-9)/4e-9)*4e-9 -element_duration_without_edge
            else:
                tau_shortened = minimum_AWG_elementsize - element_duration_without_edge
                tau_shortened = np.ceil(tau_shortened/(4e-9))*(4e-9)
            tau_cut = tau - tau_shortened - fast_pi_duration/2.0

            # print 'tau =' +str(tau)
            # print 'tau_pulse = ' +str(pulse_tau)
            # print 'tau shortened= ' + str(tau_shortened)
            # print 'fast_pi_duration = '+ str(fast_pi_duration)
            # Make the delay pulses
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = pulse_tau, amplitude = 0.)
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.) #the unit waittime is 10e-6 s
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.

            #Combine pulses to elements/waveforms and add to list of elements
            list_of_elements = []
            e_start = element.Element('X Initial %s Decoupling Element, tau = %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_start.append(T_before_p)
            e_start.append(pulse.cp(X))
            e_start.append(T)
            list_of_elements.append(e_start)
            #Currently middle is XY2 with an if statement based on the value of N this can be optimised
            e_middle = element.Element('YX Rep %s Decoupling Element, tau = %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_middle.append(T)
            e_middle.append(pulse.cp(Y))
            e_middle.append(T)
            e_middle.append(T)
            e_middle.append(pulse.cp(X))
            e_middle.append(T)
            list_of_elements.append(e_middle)
            e_end = element.Element('Y Final %s Decoupling Element, tau = %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)# Not sure if the name here is correct.
            e_end.append(T)
            e_end.append(pulse.cp(Y))
            e_end.append(T_after_p)
            list_of_elements.append(e_end)

        total_sequence_time=2*tau*N - 2* tau_cut
        Number_of_pulses  = N

        return [list_of_elements, Number_of_pulses, tau_cut, total_sequence_time]

    def Determine_length_and_type_of_Connection_elements(self,GateSequence,TotalsequenceTimes,tau_cut) :
        '''
        Empty function, needs to be able to determine the length and type of glue gates in the future
        '''
        pass

    def generate_connection_element(self,time_before_pulse,time_after_pulse, Gate_type,prefix,tau):
        '''
        Generates an element that connects to decoupling elements
        It can be at the start, the end or between sequence elements

        '''

        if Gate_type == 'pi/2': # NB!!!!! Pi-pulse duration/2.0  needs to be replaced by pi2pulse duration which does not yet exist in msmt_params (loads of different ones)

            time_before_pulse = time_before_pulse  -self.params['fast_pi2_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi2_duration']/2.0

            X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['MW_modulation_frequency'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['fast_pi2_duration'], 
                amplitude = self.params['fast_pi2_amp'])
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)


                        #Pi-pulse element/waveform
            e = element.Element('%s Pi_2_pulse, tau = %s' %(prefix,tau),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)
            return [e]

        else:
            print 'this is not programmed yet '
            return

    def combine_to_sequence(self,Lst_lst_els,list_of_repetitions):
        '''
        Combines all the generated elements to a sequence for the AWG
        Needs to be changed to handle the dynamical decoupling elements

        '''
        seq = pulsar.Sequence('Decoupling Sequence')
        list_of_elements=[]
        #Lst_lst_els means list of list of elements 
        for ind, rep in enumerate(list_of_repetitions):
        
            list_of_elements.extend(Lst_lst_els[ind]) #this converts the list_of_list to an 

            ######################
            ### single elements (trigger, connecting elements or single pulses) 
            ######################
            if np.size(Lst_lst_els[ind]) ==1:
                # print "Lst_lst_els == 1"
                e =Lst_lst_els[ind][0]
                if ind == 0:
                    seq.append(name=e.name, wfname=e.name,
                        trigger_wait=True,repetitions = rep)
                elif e.name == 'ADwin_trigger':
                    seq.append(name=str(e.name+Lst_lst_els[ind-1][0].name), wfname=e.name,
                        trigger_wait=False,repetitions = rep)
                else:
                    seq.append(name=e.name, wfname=e.name,
                        trigger_wait=False,repetitions = rep)
            
            ######################
            ### XY4 elements 
            ######################
            elif np.size(Lst_lst_els[ind]) == 3: #XY4 decoupling elements
                # print "lengt of list of list  == 3"
                seq.append(name=Lst_lst_els[ind][0].name, wfname=Lst_lst_els[ind][0].name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=Lst_lst_els[ind][1].name, wfname=Lst_lst_els[ind][1].name,
                    trigger_wait=False,repetitions = rep/2-1)
                seq.append(name=Lst_lst_els[ind][2].name, wfname=Lst_lst_els[ind][2].name,
                    trigger_wait=False,repetitions = 1)
            
            ######################
            ### XY8 elements 
            ######################
            elif np.size(Lst_lst_els[ind]) == 4: #XY8 Decoupling -a-b-(c^2-b^2)^(N/8-1)-c-d-
                # print "Lst_lst_els == 4"
                a = Lst_lst_els[ind][0]
                b= Lst_lst_els[ind][1]
                c = Lst_lst_els[ind][2]
                d = Lst_lst_els[ind][3]
                seq.append(name=a.name, wfname=a.name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=b.name, wfname=b.name,
                    trigger_wait=False,repetitions = 1)
                for i in range(rep/8-1):
                    seq.append(name=(c.name+str(i)), wfname=c.name,
                        trigger_wait=False,repetitions = 2)
                    seq.append(name=(b.name+str(i)), wfname=b.name,
                        trigger_wait=False,repetitions = 2)
                seq.append(name=c.name, wfname=c.name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=d.name, wfname=d.name,
                    trigger_wait=False,repetitions = 1)
            else:
                print 'Size of element not understood Error!'
                return
        return list_of_elements, seq

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
        # print list_of_repetitions
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
        tau_list = self.params['tau_list']
        N = self.params['Number_of_pulses']

        #Generation of initial trigger pulse element 
        Trig = pulse.SquarePulse(channel = 'adwin_sync',
            length = 5e-6, amplitude = 2)
        Trig_element = element.Element('ADwin_trigger', pulsar=qt.pulsar,
            global_time = True)
        Trig_element.append(Trig)

        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Simple Decoupling Sequence')
        i = 0 
        for tau in tau_list:
            prefix = 'electron'
            ## Generate the decoupling elements 
            list_of_decoupling_elements, list_of_decoupling_reps, tau_cut, total_decoupling_time = DynamicalDecoupling.generate_decoupling_sequence_elements(self,tau,N,prefix)
            #Generate the start and end pulse 
            Gate_type = self.params['Initial_Pulse']
            time_before_initial_pulse = max(1e-6 - tau_cut + 36e-9,44e-9)  #statement makes sure that time before initial pulse is not negative 
            time_after_initial_pulse = tau_cut

            prefix = 'initial'
            initial_pi_2 = DynamicalDecoupling.generate_connection_element(self,time_before_initial_pulse,time_after_initial_pulse, Gate_type,prefix,tau)

            Gate_type = self.params['Final_Pulse']
            time_before_final_pulse = tau_cut 
            time_after_final_pulse = time_before_initial_pulse

            prefix = 'final'
            final_pi_2 = DynamicalDecoupling.generate_connection_element(self,time_before_final_pulse,time_after_final_pulse, Gate_type,prefix,tau)

            ########################################
            #Combine all the elements to a sequence 
            #very sequence specific
            ########################################
            list_of_list_of_elements = []
            list_of_list_of_elements.append(initial_pi_2)
            list_of_list_of_elements.append(list_of_decoupling_elements)
            list_of_list_of_elements.append(final_pi_2)
            list_of_list_of_elements.append([Trig_element])
            list_of_repetitions = [1]+ [list_of_decoupling_reps]+[1,1]

            #######
            #The combine to sequence takes a list_of_list_of_elements as input and returns it as a normal list and a sequence (example [[pi/2],[a,b,c,d],[pi/2],[trig]] and [1,16,1,1] as inputs returns the normal list of elements and the sequence)
            #######
            list_of_elements, seq = DynamicalDecoupling.combine_to_sequence(self,list_of_list_of_elements,list_of_repetitions)


            if i ==0: 
                i=1
                combined_list_of_elements.extend(list_of_elements)
            else:
                combined_list_of_elements.extend(list_of_elements[:-1]) 
            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print 'uploading list of elements'
            qt.pulsar.upload(*combined_list_of_elements)
            # program the AWG
            print ' uploading sequence'
            qt.pulsar.program_sequence(combined_seq)
        else:
            print 'upload = false, no sequence uploaded to AWG'


