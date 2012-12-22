"""
AWG Hardware sequencer. Original author Lucio Robledo.
Overhauled version by Wolfgang Pfaff, 2011.

This version does not support sweeps anymore, we'll implement this simply
by for-loops when defining sequences, boils down to the same thing and
removes a massive code-overhead.

"""
# FIXME: still needs cleaning up, and removal of sweeps support

import time
from numpy import *
import numpy as np
from pulse import Pulse

# TODO: use time_to_clock
#       fix sequence_repetitions
#       dynamic jumps
#       sub-sequencing?
#       channel default voltage

class Sequence: 
    def __init__(self, name):
        self.name = name
        self.channels = []
        self.elements = []
        self.sweep_count = 1
        self.sweep_start = 0
        self.sweep_increment = 1
        self.sweep_parameters = []	# e.g. ['SpinEcho_Wait1', 'duration'], ['SpinEcho_Wait2', 'duration']
        self.sweep_elements = []
        self.endofsweep_goto_element = ''
        self.sequence_repetitions = 0
        self.clock = 1e9
        self.time_basis = 1e9
        self.send_waveforms = True
        self.program_sequence = True
        self.program_channels = True
        self.start_sequence = True
        self.use_HW_sequencing = True
        self.update_element = 'all'
        self.opt_09 = False
        self.element_lengths = {}

    def set_instrument(self,instrument):
        self.AWG = instrument

    def set_opt_09(self,flag):
        self.opt_09 = flag

    def set_update_element(self,update_element):
        self.update_element = update_element

    def force_HW_sequencing(self,flag):
        self.use_HW_sequencing = flag

    def set_program_channels(self,flag):
        self.program_channels = flag

    def set_start_sequence(self,flag):
        self.start_sequence = flag

    def set_send_waveforms(self,flag):
        self.send_waveforms = flag

    def set_send_sequence(self,flag):
        self.program_sequence = flag

    def time_to_clock(self,time):
        return int(time/self.time_basis*self.clock+0.5)

    def set_clock(self,clock):
        self.clock = clock
        return True

    def set_sequence_repetitions(self,repetitions):
        if (repetitions < 1) or (repetitions > 65536):
            print ('Error: sweep repetitions must be between 1 and 65536.')
            return False
        self.sequence_repetitions = repetitions
        return True

    def set_sequence_repetitions_infinite(self):
        self.sequence_repetitions = 0
        return True

    def set_sweep(self, start, count, increment):
        if count < 1:
            print ('Error: sweep count must be > 0.')
            return False
        if increment < 0:
            print ('Error: sweep increment must be >= 0.')
            return False
        self.sweep_start = start
        self.sweep_count = count
        self.sweep_increment = increment
        return True

    def set_endofsweep_goto_element(self, element = 'default'):
        index = -1
        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == element:
                index = a
        if index < 0:
            print('Error in set_goto_element: element \'%s\' not found.'%(element))
            return False

        self.endofsweep_goto_element = element
        return True

    def add_sweep_parameter(self, element = 'default', pulse = 'default', parameter = 'start'):
        element_index = -1
        for a in arange(0,len(self.sweep_elements)):
            if self.sweep_elements[a]['name'] == element:
                element_index = a
        if element_index < 0:
            print('Error in add_sweep_parameter: sweep element \'%s\' not defined.'%(element))
            return False

        pulse_index = -1
        for a in arange(0,len(self.sweep_elements[element_index]['pulses'])):
            if self.sweep_elements[element_index]['pulses'][a]['name'] == pulse:
                pulse_index = a
        if pulse_index < 0:
            print('Error in add_sweep_parameter: pulse \'%s\' not defined.'%(pulse))
            return False

        self.sweep_parameters.append([element,pulse,parameter])
        return True
	
    def add_channel(self, name = 'default', AWG_channel = 'ch1', high = 1.0, 
            low = 0.0, cable_delay = 0, default_voltage = 0.0):
        
        channel = {'name': name, 
                'AWG_channel': AWG_channel,
                'high': high,
                'low': low,
                'cable_delay': cable_delay,
                'default_voltage': default_voltage }

        index = -1
        # print self.channels
        for a in arange(0,len(self.channels)):
            if self.channels[a]['AWG_channel'] == AWG_channel:
                index = a
        if index >= 0:
            print('Error: AWG channel \'%s\' already defined, ignoring channel %s.'%(AWG_channel, name))
            return False
    	
        if AWG_channel not in ['ch1', 'ch1m1', 'ch1m2', 'ch2', 'ch2m1', 'ch2m2', 'ch3', 'ch3m1', 'ch3m2', 'ch4', 'ch4m1', 'ch4m2']:
            print('Error: unknown AWG channel \'%s\', ignoring channel %s.'%(AWG_channel, name))
            return False

        self.channels.append(channel)
        return True

    def add_sweep_element(self, name = 'default', min_duration = 1, repetitions = 1, trigger_wait = False, 
            only_full_periods = False, period_length = 1, event_jump_target = 'none', goto_target = 'none'):
        element = {'name': name,
                'min_duration': min_duration,
                'repetitions': repetitions,
                'trigger_wait': trigger_wait,
                'only_full_periods': only_full_periods,
                'period_length': period_length,
                'pulses':[],
                'event_jump_target': event_jump_target,
                'event_jump_index': -1,
                'goto_target': goto_target,
                'goto_index': -1}

        index = -1
        for a in arange(0,len(self.sweep_elements)):
            if self.sweep_elements[a]['name'] == name:
                index = a
        if index >= 0:
            print('Error: sweep element \'%s\' already defined.'%(name))
            return False

        index = -1
        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == name:
                index = a
        if index >= 0:
            print('Error: element \'%s\' already defined.'%(name))
            return False

        self.sweep_elements.append(element)

        return True

    def add_element(self, name = 'default', min_duration = 1, repetitions = 1, 
            trigger_wait = False, only_full_periods = False, period_length = 1, 
            event_jump_target = 'none', goto_target = 'none', 
            dynamic_jump_event = -1, global_phase=True, increment_global_t=True, 
            enforce_duration = -1):
        
        element = {'name': name,
                'min_duration': min_duration,
                'repetitions': repetitions,
                'trigger_wait': trigger_wait,
                'only_full_periods': only_full_periods,
                'period_length': period_length,
                'pulses':[],
                'event_jump_target': event_jump_target,
                'event_jump_index': -1,
                'goto_target': goto_target,
                'goto_index':-1,
                'dynamic_jump_event': dynamic_jump_event,
                'global_phase' : global_phase, 
                'increment_global_t' : increment_global_t,
                'enforce_duration' : enforce_duration}

        index = -1
        for a in arange(0,len(self.sweep_elements)):
            if self.sweep_elements[a]['name'] == name:
                index = a
        if index >= 0:
            print('Error: sweep element \'%s\' already defined.'%(name))
            return False

        index = -1
        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == name:
                index = a
        if index >= 0:
            print('Error: element \'%s\' already defined.'%(name))
            return False

        self.elements.append(element)
        return True

    def clone_channel(self, channel_target = 'default', channel_source = 'default', element = 'default', start = 0, duration = 0, 
            amplitude = 1.0, shape = 'rectangular', link_start_to = '', link_duration_to = '', phase = 0, frequency = 1e6):
        element_index = self.find_element(element)
        if element_index >= 0:
            for a in arange(0,len(self.elements[element_index]['pulses'])):
                pulse = self.elements[element_index]['pulses'][a]

                if pulse['channel'] == channel_source:

                    # debug
                    # print pulse

                    if link_start_to != '':
                        start_ref = pulse['name']
                    else:
                        start_ref = ''
                    if link_duration_to != '':
                        duration_ref = pulse['name']
                    else:
                        duration_ref = ''
                    self.add_pulse(pulse['name']+'_clone_'+channel_target, channel_target, element, start, duration,
                        amplitude, shape, start_ref, duration_ref, link_start_to, link_duration_to, phase, frequency)
        else:
            element_index = self.find_sweep_element(element)
            if element_index >= 0:
                for a in arange(0,len(self.sweep_elements[element_index]['pulses'])):
                    pulse = self.sweep_elements[element_index]['pulses'][a]
                    if pulse['channel'] == channel_source:
                        if link_start_to != '':
                            start_ref = pulse['name']
                        else:
                            start_ref = ''
                        if link_duration_to != '':
                            duration_ref = pulse['name']
                        else:
                            duration_ref = ''
                        self.add_pulse(pulse['name']+'_clone_'+channel_target, channel_target, element, start, duration,
                            amplitude, shape, start_ref, duration_ref, link_start_to, link_duration_to)
            else:
                print('Error cloning channel %s: no element %s found.'%(channel_source,element))


    def add_pulse(self, name = 'default', channel = 'default', 
            element = 'default', start = 0, duration = 0, amplitude = 1.0, 
            shape = 'rectangular', start_reference = '', 
            duration_reference = '', link_start_to = '', link_duration_to = '',
            phase = 0, frequency = 1e6, start_index = 'none',
            element_phase = True, end_index = 'none', **kw):
        
        pulse = {'name': name,
                'channel': channel,
                'element': element,
                'start': start,
                'duration': duration,
                'amplitude': amplitude,
                'shape': shape,
                'start_reference': start_reference,
                'duration_reference': duration_reference,
                'link_start_to': link_start_to,
                'link_duration_to': link_duration_to,
                'phase': phase,
                'frequency': frequency,
                'recursion': False,
                'start_index': start_index,
                'end_index': end_index,
                'element_phase' : element_phase,
                }

        for k in kw:
            pulse[k] = kw[k]

        chan_idx = self._chan_index(channel)
        if chan_idx < 0: 
            print "Error: Invalid channel '%s' in pulse '%s' " % (channel, name)
            return False
              
        element_index = -1
        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == element:
                element_index = a
        
        if element_index >= 0:
            self.elements[element_index]['pulses'].append(pulse)
            return True

        print('Error: element \'%s\' not found: pulse \'%s\' not created'%(element,name))
        return False

    # TODO can maybe extend to a more generic multichannel pulse
    # Possibility to add IQ modulation pulses. This effectively creates two
    # pulses by using the single add_pulse function
    def add_IQmod_pulse(self, name='default', 
            channel=('default','default'), *arg, **kw):
        """
        Add an IQ modulation pulse. Requires two channels, and generates
        two pulses on those, with shape 'IQmod'. '-I' and '-Q' respectively
        will be appended to be pulse name and this shape.

        FIXME: the name is actually misleading -- this pulse is only
        intended for SSB modulation via the iq modulation of the vector source;
        should be upgraded for more flexible use;
        """
        
        for i,c in enumerate(channel):
            iq = '-I' if i == 0 else '-Q'
            if not self.add_pulse(name=name+iq, channel=c, 
                    shape='IQmod'+iq, *arg, **kw):
                return False

    # generic method to generate multichannel pulses
    def add_multichannel_pulse(self, name='default', channels=(), *arg, **kw):
        """
        Create generic multichannel pulses.
        Any argument or keyword argument can be either given globally for all
        channels, or individually for each channel.
        To set something globally, just use the arguments as required by a
        single pulse, the options will be used in the same fashion for all
        channels.
        In case you want individual options for all channels, give the
        corresponding option as a tuple of length of the no of channels; the
        options will then be passed to the single channel pulses in the same
        order as the channels are given.

        Names can be given as tuples as well. If not, then '_chan-<i>' will
        be appended to each single channel pulse, where i denotes the index
        of the channel in the channels-tuple.
        """
        
        for i,c in enumerate(channels):
            
            chanarg = []
            for a in arg:
                if type(a) is tuple:
                    chanarg.append(a[i])
                else:
                    chanarg.append(a)

            chankw = {}
            for k in kw:
                if type(kw[k]) is tuple:
                    chankw[k] = kw[k][i]
                else:
                    chankw[k] = kw[k]

            channame = ''
            if type(name) is tuple:
                channame = name[i]
            else:
                channame = name

            if not self.add_pulse(name=channame, channel=c, 
                    *chanarg, **chankw):
                return False

    
    def find_pulse_in_element(self, pulse = 'default', element = 'default', 
            element_index = -1):
        
        if element_index == -1:
            element_index = self.find_element(element)
            if element_index < 0:
                return -1,-1
        pulse_index = -1
        for a in arange(0,len(self.elements[element_index]['pulses'])):
            if self.elements[element_index]['pulses'][a]['name'] == pulse:
                return a, element_index
        return pulse_index, element_index

    def find_pulse_in_sweep_element(self, pulse = 'default', element = 'default', element_index = -1):
        if element_index == -1:
            element_index = self.find_sweep_element(element)
            if element_index < 0:
                return -1, -1
        pulse_index = -1
        for a in arange(0,len(self.sweep_elements[element_index]['pulses'])):
            if self.sweep_elements[element_index]['pulses'][a]['name'] == pulse:
                return a, element_index
        return pulse_index, element_index

    def find_channel(self, channel = 'default'):
        index = -1
        for a in arange(0,len(self.channels)):
            if self.channels[a]['name'] == channel:
                return a
        return index

    def find_element(self, element = 'default'):
        index = -1
        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == element:
                return a
        return index

    def find_sweep_element(self, element = 'default'):
        index = -1
        for a in arange(0,len(self.sweep_elements)):
            if self.sweep_elements[a]['name'] == element:
                return a
        return index


    def show_channels(self):
        for a in arange(0,len(self.channels)):
            print self.channels[a]['name']

    def show_elements(self):
        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == 'sweep':
                for b in arange(0,self.sweep_count):
                    for c in arange(0,len(self.sweep_elements)):
                        min = 0
                        max = 0
                        print self.sweep_elements[c]['name']+'_%s'%(self.sweep_start+b*self.sweep_increment)
                        for d in arange(0,len(self.sweep_elements[c]['pulses'])):
                            if self.start_index(self.sweep_elements[c]['pulses'][d]['name'], 
                                    self.sweep_elements[c]['name'], sweep_index = b) < min:
                                min = self.start_index(self.sweep_elements[c]['pulses'][d]['name'], self.sweep_elements[c]['name'], sweep_index = b)
                            if self.end_index(self.sweep_elements[c]['pulses'][d]['name'], 
                                    self.sweep_elements[c]['name'], sweep_index = b) > max:
                                max = self.end_index(self.sweep_elements[c]['pulses'][d]['name'], self.sweep_elements[c]['name'], sweep_index = b)
                        print min,max,max-min
            else:    
                print self.elements[a]['name']
                min = 0
                max = 0
                for d in arange(0,len(self.elements[a]['pulses'])):
                    if self.start_index(self.elements[a]['pulses'][d]['name'], self.elements[a]['name']) < min:
                        min = self.start_index(self.elements[a]['pulses'][d]['name'], self.elements[a]['name'])
                    if self.end_index(self.elements[a]['pulses'][d]['name'], self.elements[a]['name']) > max:
                        max = self.end_index(self.elements[a]['pulses'][d]['name'], self.elements[a]['name'])
                print min,max,max-min

    def start_index(self, pulse = 'default', element = 'default', sweep_index = 0):
        pulse_index, element_index = self.find_pulse_in_element(pulse,element)
        if pulse_index >= 0:
            if self.elements[element_index]['pulses'][pulse_index]['start_index'] != 'none': 
                return self.elements[element_index]['pulses'][pulse_index]['start_index']
            if self.elements[element_index]['pulses'][pulse_index]['recursion'] == True:
                print ('Error: circular pulse definition in %s, %s'%(pulse, element))
                return 'Error'
            self.elements[element_index]['pulses'][pulse_index]['recursion'] = True
            
            if self.elements[element_index]['pulses'][pulse_index]['start_reference'] == '':
                self.elements[element_index]['pulses'][pulse_index]['recursion'] = False
                start = self.elements[element_index]['pulses'][pulse_index]['start']
                self.elements[element_index]['pulses'][pulse_index]['start_index'] = start
                return start
            else:
                if self.elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'start':
                    self.elements[element_index]['pulses'][pulse_index]['recursion'] = False
                    start = self.elements[element_index]['pulses'][pulse_index]['start'] + \
                            self.start_index(self.elements[element_index]['pulses'][pulse_index]['start_reference'],element) 
                    self.elements[element_index]['pulses'][pulse_index]['start_index'] = start
                    return start
                elif self.elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'end':
                    self.elements[element_index]['pulses'][pulse_index]['recursion'] = False
                    start = self.elements[element_index]['pulses'][pulse_index]['start'] + \
                            self.end_index(self.elements[element_index]['pulses'][pulse_index]['start_reference'],element)
                    self.elements[element_index]['pulses'][pulse_index]['start_index'] = start
                    return start
                else:
                    print('Error: unexpected link_start_to condition: %s'%self.elements[element_index]\
                            ['pulses'][pulse_index]['link_start_to'])
                    return False
        elif element_index >= 0:
            print('Error: no pulse %s found in element %s.'%(pulse,element))
            return False

        pulse_index, element_index = self.find_pulse_in_sweep_element(pulse,element)
        if element_index < 0:
            print('Error: element %s not found.'%(element))
            return False
        if pulse_index < 0:
            print('Error: no pulse %s found in sweep_element %s.'%(pulse,element))
            return False

        if self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] == True:
            print ('Error: circular pulse definition in %s, %s'%(pulse, element))
            return 'Error'
        self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = True

        sweep = False
        for a in arange(0,len(self.sweep_parameters)):
            if self.sweep_parameters[a][0] == element:
                if self.sweep_parameters[a][1] == pulse:
                    sweep_parameter_index = a
                    sweep = True
                    sweep_value = sweep_index*self.sweep_increment+self.sweep_start
        

        if self.sweep_elements[element_index]['pulses'][pulse_index]['start_reference'] == '':
            if (sweep == True) and (self.sweep_parameters[sweep_parameter_index][2] == 'start'):
                self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = False
                return sweep_value
            else:
                self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = False
                return self.sweep_elements[element_index]['pulses'][pulse_index]['start']
        else:
            if self.sweep_elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'start':
                if (sweep == True) and (self.sweep_parameters[sweep_parameter_index][2] == 'start'):
                    self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = False
                    return sweep_value + self.start_index(self.sweep_elements[element_index]\
                            ['pulses'][pulse_index]['start_reference'],element, sweep_index)
                else:
                    self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = False
                    return self.sweep_elements[element_index]['pulses'][pulse_index]['start'] + \
                            self.start_index(self.sweep_elements[element_index]['pulses']\
                            [pulse_index]['start_reference'],element, sweep_index)
            elif self.sweep_elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'end':
                if (sweep == True) and (self.sweep_parameters[sweep_parameter_index][2] == 'start'):
                    self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = False
                    return sweep_value + self.end_index(self.sweep_elements[element_index]['pulses']\
							[pulse_index]['start_reference'],element, sweep_index)
                else:
                    self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = False
                    return self.sweep_elements[element_index]['pulses'][pulse_index]['start'] + \
                            self.end_index(self.sweep_elements[element_index]['pulses']\
                            [pulse_index]['start_reference'],element, sweep_index)
            else:
                print('Error: unexpected link_start_to condition: %s'%self.sweep_elements[element_index]\
                        ['pulses'][pulse_index]['link_start_to'])
                return False

    def end_index(self, pulse = 'default', element = 'default', sweep_index = 0):
        pulse_index, element_index = self.find_pulse_in_element(pulse,element)
        if pulse_index >= 0:
            if self.elements[element_index]['pulses'][pulse_index]['end_index'] != 'none': 
                return self.elements[element_index]['pulses'][pulse_index]['end_index']
            if self.elements[element_index]['pulses'][pulse_index]['recursion'] == True:
                print ('Error: circular pulse definition in %s, %s'%(pulse, element))
                return 'Error'
            self.elements[element_index]['pulses'][pulse_index]['recursion'] = True

            if (self.elements[element_index]['pulses'][pulse_index]['start_reference'] == ''):
                start = self.elements[element_index]['pulses'][pulse_index]['start']
            else:
                
                
                if self.elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'start':
                    start = self.elements[element_index]['pulses'][pulse_index]['start'] + \
                            self.start_index(self.elements[element_index]['pulses']\
                            [pulse_index]['start_reference'],element)
                elif self.elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'end':
                    start = self.elements[element_index]['pulses'][pulse_index]['start'] + \
                            self.end_index(self.elements[element_index]['pulses']\
                            [pulse_index]['start_reference'],element)
                else:
                    print('Error: unexpected link_start_to condition: %s'%self.elements[element_index]\
                            ['pulses'][pulse_index]['link_start_to'])
                    return False
            if (self.elements[element_index]['pulses'][pulse_index]['duration_reference'] == ''):
                duration = self.elements[element_index]['pulses'][pulse_index]['duration']
            elif self.elements[element_index]['pulses'][pulse_index]['link_duration_to'] == 'duration':
                duration = self.elements[element_index]['pulses'][pulse_index]['duration'] + \
                        self.end_index(self.elements[element_index]['pulses']\
                        [pulse_index]['duration_reference'],element) - \
                        self.start_index(self.elements[element_index]['pulses']\
                        [pulse_index]['duration_reference'],element)
            else:
                print('Error: unexpected link_duration_to condition: %s'%self.elements[element_index]\
                        ['pulses'][pulse_index]['link_duration_to'])
                return False
            self.elements[element_index]['pulses'][pulse_index]['recursion'] = False
            self.elements[element_index]['pulses'][pulse_index]['end_index'] = start + duration
            return start + duration

        elif element_index >= 0:
            print('Error: no pulse %s found in element %s.'%(pulse,element))
            return False

        pulse_index, element_index = self.find_pulse_in_sweep_element(pulse,element)
        if element_index < 0:
            print('Error: element %s not found.'%(element))
            return False
        if pulse_index < 0:
            print('Error: no pulse %s found in sweep_element %s.'%(pulse,element))
            return False

        if self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] == True:
            print ('Error: circular pulse definition in %s, %s'%(pulse, element))
            return 'Error'
        self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = True

        sweep = False
        for a in arange(0,len(self.sweep_parameters)):
            if self.sweep_parameters[a][0] == element:
                if self.sweep_parameters[a][1] == pulse:
                    sweep_parameter_index = a
                    sweep = True
                    sweep_value = sweep_index*self.sweep_increment+self.sweep_start

		
        if (sweep == True) and (self.sweep_parameters[sweep_parameter_index][2] == 'start'):
            pulse_start = sweep_value
        else:
            pulse_start = self.sweep_elements[element_index]['pulses'][pulse_index]['start']
        if (sweep == True) and (self.sweep_parameters[sweep_parameter_index][2] == 'duration'):
            pulse_duration = sweep_value
        else:
            pulse_duration = self.sweep_elements[element_index]['pulses'][pulse_index]['duration']

        if (self.sweep_elements[element_index]['pulses'][pulse_index]['start_reference'] == ''):
            start = pulse_start
        else:
            if self.sweep_elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'start':
                start = pulse_start + self.start_index(self.sweep_elements[element_index]['pulses']\
                        [pulse_index]['start_reference'],element, sweep_index)
            elif self.sweep_elements[element_index]['pulses'][pulse_index]['link_start_to'] == 'end':
                start = pulse_start + self.end_index(self.sweep_elements[element_index]['pulses']\
                        [pulse_index]['start_reference'],element, sweep_index)
            else:
                print('Error: unexpected link_start_to condition: %s'%self.sweep_elements[element_index]\
                        ['pulses'][pulse_index]['link_start_to'])
                return False
        if (self.sweep_elements[element_index]['pulses'][pulse_index]['duration_reference'] == ''):
            duration = pulse_duration
        elif self.sweep_elements[element_index]['pulses'][pulse_index]['link_duration_to'] == 'duration':
            duration = pulse_duration + \
                   self.end_index(self.sweep_elements[element_index]['pulses'][pulse_index]\
                   ['duration_reference'],element, sweep_index) - \
                   self.start_index(self.sweep_elements[element_index]['pulses'][pulse_index]\
                   ['duration_reference'],element, sweep_index)
        else:
            print('Error: unexpected link_duration_to condition: %s'%self.sweep_elements[element_index]['pulses'][pulse_index]['link_duration_to'])
            return False
        self.sweep_elements[element_index]['pulses'][pulse_index]['recursion'] = False
        return start + duration

    def element_length_and_offset(self, element_index):
        min = 0
        max = 0
        for pulse_index in arange(0,len(self.elements[element_index]['pulses'])):
            cable_delay = self.channels[self.find_channel(self.elements[element_index]['pulses'][pulse_index]['channel'])]['cable_delay']
            start = self.start_index(self.elements[element_index]['pulses'][pulse_index]['name'], self.elements[element_index]['name'])
            end   = self.end_index(self.elements[element_index]['pulses'][pulse_index]['name'], self.elements[element_index]['name'])
            if pulse_index == 0:
                min = start - cable_delay
                max = end   - cable_delay
            else:
                if min > start - cable_delay:
                    min = start - cable_delay
                if max < end - cable_delay:
                    max = end   - cable_delay
        offset = -min
        length = max - min
        if length < self.elements[element_index]['min_duration']:
            length = self.elements[element_index]['min_duration']
        if self.elements[element_index]['only_full_periods']:
            period = self.elements[element_index]['period_length']
            periods = length / period
            if periods * period < length:
                length = (periods+1 ) * period
            else:
                length = periods * period
        if self.elements[element_index]['enforce_duration'] >= length:
            length = self.elements[element_index]['enforce_duration']
        else:
            if self.elements[element_index]['enforce_duration'] >= 0:
                print('warning: cannot set element shorter than %i samples'%length)

        if self.use_HW_sequencing:
            if length < 960:
                length = 960
            period = 4      # HW sequence granularity AWG 5014     
#            period = 64     # HW sequence granularity AWG 5014B
            periods = length / period
            if periods * period < length:
                length = (periods+1 ) * period
            else:
                length = periods * period
        return length, offset

    def sweep_element_length_and_offset(self, element_index, sweep_index):
        for pulse_index in arange(0,len(self.sweep_elements[element_index]['pulses'])):
            cable_delay = self.channels[self.find_channel(self.sweep_elements[element_index]['pulses'][pulse_index]['channel'])]['cable_delay']
            start = self.start_index(self.sweep_elements[element_index]['pulses'][pulse_index]['name'], self.sweep_elements[element_index]['name'], sweep_index)
            end   = self.end_index(self.sweep_elements[element_index]['pulses'][pulse_index]['name'], self.sweep_elements[element_index]['name'], sweep_index)
            if pulse_index == 0:
                min = start - cable_delay
                max = end   - cable_delay
            else:
                if min > start - cable_delay:
                    min = start - cable_delay
                if max < end - cable_delay:
                    max = end   - cable_delay
        offset = -min
        length = max - min
        if length < self.sweep_elements[element_index]['min_duration']:
            length = self.sweep_elements[element_index]['min_duration']
        if self.sweep_elements[element_index]['only_full_periods']:
            period = self.sweep_elements[element_index]['period_length']
            periods = length / period
            if periods * period < length:
                length = (periods+1 ) * period
            else:
                length = periods * period
        if self.use_HW_sequencing:
            if length < 960:
                length = 960
            period = 4      # AWG 5014     
#            period = 64     # AWG 5014B
            periods = length / period
            if periods * period < length:
                length = (periods+1 ) * period
            else:
                length = periods * period
        return length, offset

    def initialize_AWG(self):
        if self.program_sequence:
            self.AWG.stop()
            self.AWG.set_runmode('SEQ')
            self.AWG.set_sq_length(0)

#################### only Opt09 AWG ######################
            if self.opt_09:
                for a in arange(0,15):              
                    self.AWG.set_djump_def(a,-1)
                self.AWG.set_event_jump_mode('EJUM')
##########################################################
            
        if (self.send_waveforms == True) and (self.update_element == 'all'):
            self.AWG.delete_all_waveforms_from_list()

        if self.program_channels:
            for a in arange(0,len(self.channels)):
                channel = self.channels[a]['AWG_channel']
                if channel.find('m')<0:
                    amplitude = self.channels[a]['high'] - self.channels[a]['low']
                    offset    = (self.channels[a]['high'] + self.channels[a]['low']) / 2.0
                    analog_channel = ['ch1','ch2','ch3','ch4'].index(channel) + 1
                    if analog_channel == 1:
                        self.AWG.set_ch1_amplitude(amplitude)
                        self.AWG.set_ch1_offset(offset)
                    elif analog_channel == 2:
                        self.AWG.set_ch2_amplitude(amplitude)
                        self.AWG.set_ch2_offset(offset)
                    elif analog_channel == 3:
                        self.AWG.set_ch3_amplitude(amplitude)
                        self.AWG.set_ch3_offset(offset)
                    elif analog_channel == 4:
                        self.AWG.set_ch4_amplitude(amplitude)
                        self.AWG.set_ch4_offset(offset)
                else:
                    high = self.channels[a]['high']
                    low  = self.channels[a]['low']
                    marker_channel = ['ch1m1','ch1m2','ch2m1','ch2m2','ch3m1','ch3m2','ch4m1','ch4m2'].index(channel) + 1
                    if marker_channel == 1:
                        self.AWG.set_ch1_marker1_low(low)
                        self.AWG.set_ch1_marker1_high(high)
                    elif marker_channel == 2:
                        self.AWG.set_ch1_marker2_low(low)
                        self.AWG.set_ch1_marker2_high(high)
                    elif marker_channel == 3:
                        self.AWG.set_ch2_marker1_low(low)
                        self.AWG.set_ch2_marker1_high(high)
                    elif marker_channel == 4:
                        self.AWG.set_ch2_marker2_low(low)
                        self.AWG.set_ch2_marker2_high(high)
                    elif marker_channel == 5:
                        self.AWG.set_ch3_marker1_low(low)
                        self.AWG.set_ch3_marker1_high(high)
                    elif marker_channel == 6:
                        self.AWG.set_ch3_marker2_low(low)
                        self.AWG.set_ch3_marker2_high(high)
                    elif marker_channel == 7:
                        self.AWG.set_ch4_marker1_low(low)
                        self.AWG.set_ch4_marker1_high(high)
                    elif marker_channel == 8:
                        self.AWG.set_ch4_marker2_low(low)
                        self.AWG.set_ch4_marker2_high(high)

    
    ### Changed by Wolfgang for v2 -- sweeps not supported anymore
    ### FIXME rest of file still needs cleaning up
    
    def send_sequence(self):
        
        print ''
        print "Start generating sequence '%s'" % self.name
        generation_start = time.time()
        
        # FIXME determine used,unused channels at the beginning, both
        # the AWG channels (1,2,3,4) and our channels (ch1, ch1m1, ... ch4m2)
        # check which channels we actually make use of
        AWG_channels = [ False, False, False, False ]
        used_channels = [ ch['AWG_channel'] for ch in self.channels ]
        for ch in used_channels:
            for b, awg_ch in enumerate(AWG_channels):
                if str(b+1) in ch:
                    AWG_channels[b] = True

        # FIXME maybe put somewhere else later?
        self.initialize_AWG()
        sequence_element_counter = 0
        goto_index = -1
    
        # go through all elements of the sequence, generate waveforms
        # and send to the AWG
        
        element_time_offset = 0.
        max_seq_length = 0          # in steps
        for i, element in enumerate(self.elements):

### special feature for opt09 AWG #############################################
            if self.opt_09:
                if (element['dynamic_jump_event'] != -1) and \
                        self.program_sequence:

                    # dyn. jump overrides event jump
                    self.AWG.set_event_jump_mode('DJUM') 
                    self.AWG.set_djump_def(element['dynamic_jump_event'], 
                            sequence_element_counter+1)
###############################################################################

            # check if the current element is the goto target of another
            # element
            for j,element2 in enumerate(self.elements):
                if element2['goto_target'] == element['name']:
                    element2['goto_index'] = sequence_element_counter + 1
                if element2['event_jump_target'] == element['name']:
                    element2['event_jump_index'] = sequence_element_counter + 1

            # create the WF for this element, add all pulses
            # FIXME t0 should be more flexible, could maybe link that to other
            # elements, etc.
            length, offset = self.element_length_and_offset(i)
            if length > max_seq_length:
                max_seq_length = length 
            waveforms = self._init_waveforms(AWG_channels, length)
            for j, pulse in enumerate(element['pulses']):
                self._add_pulse(element, offset, pulse, waveforms, 
                        element_time_offset=element_time_offset if \
                                element['global_phase'] else 0)

            # have to scale all waveforms from voltages to the -1..1 range
            for j in [ j for j in range(4) if AWG_channels[j] ]:
                for chan in self.channels:
                    cidx, scidx = self._AWG_chan_indices(chan)
                    if j == cidx:
                        waveforms[j][scidx] = \
                                self._voltage_to_waveform(chan,
                                     waveforms[j][scidx])


            sequence_element_counter += 1
            print "Generating element '%s' (%d/%d) : %.3f us" % (element['name'], 
                    sequence_element_counter, len(self.elements), 
                    length/self.clock*1e6)
            
            self.element_lengths[element['name']] = length/self.clock
                    
           

            # send the waveform to the AWG
            if (self.send_waveforms == True) and \
                    ((self.update_element == 'all') or \
                    (self.update_element == element['name'])):
                
                for j in [ j for j in range(4) if AWG_channels[j] ]:
                    n = element['name']+'_ch%d'%(j+1)
                   
                    self.AWG.send_waveform(waveforms[j][0],
                            waveforms[j][1], waveforms[j][2], n, self.clock)
                    self.AWG.import_waveform_file(n, n)

            # program AWG
            if self.program_sequence:
                self.AWG.set_sq_length(sequence_element_counter)
                self.AWG.set_sqel_loopcnt_to_inf(sequence_element_counter, 
                        False)
                self.AWG.set_sqel_loopcnt(element['repetitions'], 
                        sequence_element_counter)
                for j in [ j for j in range(4) if AWG_channels[j] ]:
                    n = element['name']+'_ch%d'%(j+1)
                    self.AWG.set_sqel_waveform(n, j+1, sequence_element_counter)
                
                if element['trigger_wait']:
                    self.AWG.set_sqel_trigger_wait(sequence_element_counter, 1)

            
            # update the total time the sequence lasts up to now, take
            # repeated elements into account
            #
            # not all waveforms might be used; take the longest analog channel
            # to be the time
            if element['increment_global_t'] :
                element_time_offset += float(length * element['repetitions']) / \
                        self.clock
            #print "length of element '%s': %d, with of %d" % (element['name'], length, offset)
            #print "total sequence time after element '%s': %d " % (element['name'], of)

        # set correct looping behavior
        if (self.sequence_repetitions == 0) and (goto_index > -1):
            self.AWG.set_sqel_goto_state(sequence_element_counter, True)
            self.AWG.set_sqel_goto_target_index(sequence_element_counter, 
                    goto_index)
        
        # set used channels to on, unused to off
        if self.program_channels:
            for j in [ j for j in range(4) if AWG_channels[j] ]:
                getattr(self.AWG, 'set_ch%d_status' % (j+1))('on')
            for j in [ j for j in range(4) if not AWG_channels[j] ]:
                getattr(self.AWG, 'set_ch%d_status' % (j+1))('off')

        if self.program_sequence:
            if self.AWG.get_sq_mode() != 'HARD':
                print('WARNING: AWG not in hardware sequencer mode!')
            else:
                seq_elt_cnt = 0
                for i, elt in enumerate(self.elements):
                    seq_elt_cnt += 1
                    if elt['event_jump_index'] > -1:
                        self.AWG.set_sqel_event_jump_type(seq_elt_cnt, 'IND')
                        self.AWG.set_sqel_event_jump_target_index(seq_elt_cnt, 
                                elt['event_jump_index'])
                    if elt['goto_index'] > -1:
                        self.AWG.set_sqel_goto_state(seq_elt_cnt, '1')
                        self.AWG.set_sqel_goto_target_index(seq_elt_cnt, 
                                elt['goto_index'])
            if goto_index > -1:
                self.AWG.set_sqel_goto_state(sequence_element_counter, '1')
                self.AWG.set_sqel_goto_target_index(sequence_element_counter, 
                        goto_index)
        if self.start_sequence:
            self.AWG.start()
        print 'Sequence generation finished in %.2f seconds.' % (time.time()-\
                generation_start)
        #print 'Max seq length: %d us.' %(max_seq_length/self.clock*1e6)
        print ''
        return max_seq_length/self.clock*1e6        # us

    # we initialize the waveforms for all used channels
    # will all be set to a default voltage, specified for each channel
    def _init_waveforms(self, AWG_channels, length):
        waveforms = [ [], [], [], [] ]
        
        for j in [ j for j in range(4) if AWG_channels[j] ]:    
            waveforms[j] = [ zeros(length, dtype = float), 
                    zeros(length, dtype = float), 
                    zeros(length, dtype = float)]
             
            for chan in self.channels:
                AWG_chan_idx, AWG_subchan_idx = self._AWG_chan_indices(chan)
                if j == AWG_chan_idx:
                    waveforms[j][AWG_subchan_idx] += chan['default_voltage']
            
        return waveforms

    ### move this up to tools for sake of organisation?
    ### Tools
    
    # returns a channel from its name
    def _chan(self, cname):
        idx = self._chan_index(cname)
        if idx < 0:
            return False
        else:
            return self.channels[idx]
    
    # returns the index of a channel within the class channel list
    def _chan_index(self, cname):
        lst = [ i for i,c in enumerate(self.channels) if c['name'] == cname ]
        if len(lst) > 0:
            return lst[0]
        else:
            return -1
    
    # returns AWG channel and subchannel indices of a channel 
    def _AWG_chan_indices(self, chan):
        
        # constants
        AWG_CHANS = ['ch1','ch2','ch3','ch4']
        AWG_SUBCHANS = ['', 'm1', 'm2' ]

        n = chan['AWG_channel']
        chan_idx = AWG_CHANS.index(n[0:3])
        subchan_idx = AWG_SUBCHANS.index(n[3:5])

        return chan_idx, subchan_idx

    def _voltage_to_waveform(self, chan, v):
        c_idx, sc_idx = self._AWG_chan_indices(chan)

        H = chan['high']
        L = chan['low']
        if sc_idx == 0:
            return ((2.0*array(v)-H-L)/(H-L))
        else:
            for i,val in enumerate(v):
                if val > 0.:
                    v[i] = 1.
            return array(v)

    ###
    ### pulse generation;
    ### The actual waveforms are generated in an external class.

    # main pulse creation method
    def _add_pulse(self, element, offset, pulse, waveforms, 
            element_time_offset):
       
        chan_idx = self.find_channel(pulse['channel'])
        chan = self.channels[chan_idx]
        cable_delay = chan['cable_delay']
        AWG_chan_idx, AWG_subchan_idx = self._AWG_chan_indices(chan)
        
        # where we actually put the wfs depends on the cable delay
        # of the involved channels        
        sidx = int(self.start_index(pulse['name'], element['name']) + offset - \
            cable_delay)
        eidx = int(self.end_index(pulse['name'], element['name']) + offset - \
            cable_delay)
        
        stime = (sidx/self.clock + element_time_offset) if \
                pulse['element_phase'] else 0
        samples = eidx-sidx
        duration = samples/self.clock
        if pulse['duration'] < 0 :
            print 'ERROR: pulse ', pulse['name'], 'in element',pulse['element'],'has duration', pulse['duration'] 
        # print "pulse '%s' has offset %d (=%.3f us)" % (pulse['name'], sidx+of, stime*1e6)
        p = Pulse(pulse, samples, stime, self.clock)
        waveforms[AWG_chan_idx][AWG_subchan_idx][sidx:eidx] += p.wform()
        return waveforms

