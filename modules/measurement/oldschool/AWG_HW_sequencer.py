from numpy import *

# todo: use time_to_clock
#       fix sequence_repetitions
#       dynamic jumps
#       sub-sequencing?
#       channel default voltage

class sequence: 
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
	
    def add_channel(self, name = 'default', AWG_channel = 'ch1', high = 1.0, low = 0.0, cable_delay = 0, default_voltage = 0.0):
        channel = {'name': name, 
                'AWG_channel': AWG_channel,
                'high': high,
                'low': low,
                'cable_delay': cable_delay,
                'default_voltage': default_voltage}

        index = -1
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

    def add_element(self, name = 'default', min_duration = 1, repetitions = 1, trigger_wait = False, 
            only_full_periods = False, period_length = 1, event_jump_target = 'none', goto_target = 'none', dynamic_jump_event = -1):
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
                'dynamic_jump_event': dynamic_jump_event}

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

    def add_pulse(self, name = 'default', channel = 'default', element = 'default', start = 0, duration = 0, 
            amplitude = 1.0, shape = 'rectangular', start_reference = '', duration_reference = '', 
            link_start_to = '', link_duration_to = '', phase = 0, frequency = 1e6, start_index = 'none', end_index = 'none'):
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
                'end_index': end_index}

        channel_index = -1
        for a in arange(0,len(self.channels)):
            if self.channels[a]['name'] == channel:
                channel_index = a
        if channel_index < 0:
            print('Error: channel \'%s\' not found: pulse \'%s\' not created'%(channel,name))
            return False

        element_index = -1
        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == element:
                element_index = a
        if element_index >= 0:
            self.elements[element_index]['pulses'].append(pulse)
            return True
        for a in arange(0,len(self.sweep_elements)):
            if self.sweep_elements[a]['name'] == element:
                element_index = a
        if element_index >= 0:
            self.sweep_elements[element_index]['pulses'].append(pulse)
            return True
        print('Error: element \'%s\' not found: pulse \'%s\' not created'%(element,name))
        return False
    
    def find_pulse_in_element(self, pulse = 'default', element = 'default', element_index = -1):
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

                    




    def send_sequence(self):
        AWG_channels = [False,False,False,False]
        for a in arange(0,len(self.channels)):
            for b in arange(0,4):
                if self.channels[a]['AWG_channel'].find(str(b+1)) > -1:
                    AWG_channels[b] = True

        self.initialize_AWG()
        sequence_element_counter = 0
        goto_index = -1

        for a in arange(0,len(self.elements)):
            if self.elements[a]['name'] == self.endofsweep_goto_element:
                goto_index = sequence_element_counter + 1

#################### only Opt09 AWG ######################
            if self.opt_09:
                if (self.elements[a]['dynamic_jump_event'] != -1) and self.program_sequence:
                    self.AWG.set_event_jump_mode('DJUM')            ### dynamic jump overrides event jump
                    self.AWG.set_djump_def(self.elements[a]['dynamic_jump_event'], sequence_element_counter + 1)
##########################################################
            
            for b in arange(0,len(self.elements)):
                if self.elements[b]['goto_target'] == self.elements[a]['name']:
                    self.elements[b]['goto_index'] = sequence_element_counter + 1
                if self.elements[b]['event_jump_target'] == self.elements[a]['name']:
                    self.elements[b]['event_jump_index'] = sequence_element_counter + 1
            for b in arange(0,len(self.sweep_elements)):
                if self.sweep_elements[b]['goto_target'] == self.elements[a]['name']:
                    self.sweep_elements[b]['goto_index'] = sequence_element_counter + 1
                if self.sweep_elements[b]['event_jump_target'] == self.elements[a]['name']:
                    self.sweep_elements[b]['event_jump_index'] = sequence_element_counter + 1

            if self.elements[a]['name'] == 'sweep':
                for c in arange(0,len(self.sweep_elements)):
                    for d in arange(0,len(self.elements)):
                        if self.elements[d]['goto_target'] == self.sweep_elements[c]['name']:
                            self.elements[d]['goto_index'] = sequence_element_counter + 1
                        if self.elements[d]['event_jump_target'] == self.sweep_elements[c]['name']:
                            self.elements[d]['event_jump_index'] = sequence_element_counter + 1
                    for d in arange(0,len(self.sweep_elements)):
                        if self.sweep_elements[d]['goto_target'] == self.sweep_elements[c]['name']:
                            self.sweep_elements[d]['goto_index'] = sequence_element_counter + 1 + d
                        if self.sweep_elements[d]['event_jump_target'] == self.sweep_elements[c]['name']:
                            self.sweep_elements[d]['event_jump_index'] = sequence_element_counter + 1 + d
                for b in arange(0,self.sweep_count):
                    for c in arange(0,len(self.sweep_elements)):
                        length, offset = self.sweep_element_length_and_offset(c, b)
                        waveforms = [[],[],[],[]]
                        for d in arange(0,4):
                            if AWG_channels[d]:
                                waveforms[d] = [zeros(length,dtype = float), zeros(length, dtype = int), zeros(length, dtype = int)]
                                for e in arange(0,len(self.channels)):
                                    AWG_channel = self.channels[e]['AWG_channel']
                                    AWG_channel_index = ['ch1','ch2','ch3','ch4'].index(AWG_channel[0:3])
                                    AWG_subchannel_index = ['','m1','m2'].index(AWG_channel[3:5])
                                    if (d == AWG_channel_index):
                                        if (AWG_subchannel_index == 0):
                                            H = self.channels[e]['high']
                                            L = self.channels[e]['low']
                                            amplitude = (-L-H)/(H-L)
                                            waveforms[d][0] = waveforms[d][0] + amplitude + self.channels[e]['default_voltage']
                                        else:
                                            if self.channels[e]['default_voltage'] == self.channels[e]['high']:
                                                waveforms[d][AWG_subchannel_index] == waveforms[d][AWG_subchannel_index] + 1

                        for d in arange(0,len(self.sweep_elements[c]['pulses'])):
                            pulse = self.sweep_elements[c]['pulses'][d]
                            channel_index = self.find_channel(pulse['channel'])
                            AWG_channel = self.channels[channel_index]['AWG_channel']
                            AWG_channel_index = ['ch1','ch2','ch3','ch4'].index(AWG_channel[0:3])
                            AWG_subchannel_index = ['','m1','m2'].index(AWG_channel[3:5])
                            cable_delay = self.channels[channel_index]['cable_delay']
                            if pulse['shape'] == 'rectangular':
                                if AWG_subchannel_index > 0:
                                    if pulse['amplitude'] > 0:
                                        amplitude = 1
                                    else:
                                        amplitude = 0
                                else:
                                    H = self.channels[channel_index]['high']
                                    L = self.channels[channel_index]['low']
                                    amplitude = (2*pulse['amplitude']-L-H)/(H-L)
                                for e in arange(self.start_index(self.sweep_elements[c]['pulses'][d]['name'], self.sweep_elements[c]['name'], sweep_index = b) + offset - cable_delay, 
                                        self.end_index(self.sweep_elements[c]['pulses'][d]['name'], self.sweep_elements[c]['name'], sweep_index = b) + offset - cable_delay):
                                    waveforms[AWG_channel_index][AWG_subchannel_index][e] = amplitude
                            elif pulse['shape'] == 'sine':
                                if AWG_subchannel_index > 0:
                                    print('Error: sine waveform not compatible with marker channel')
                                else:
                                    H = self.channels[channel_index]['high']
                                    L = self.channels[channel_index]['low']
                                    amplitude = (2*pulse['amplitude']-L-H)/(H-L)
                                    wv_start = self.start_index(self.sweep_elements[c]['pulses'][d]['name'], self.sweep_elements[c]['name'], sweep_index = b) + offset - cable_delay
                                    wv_length = self.end_index(self.sweep_elements[c]['pulses'][d]['name'], self.sweep_elements[c]['name'], sweep_index = b) + offset - cable_delay - wv_start

                                    for e in arange(0, wv_length):
                                        waveforms[AWG_channel_index][AWG_subchannel_index][e+wv_start] += amplitude*sin(e*1e-9*self.sweep_elements[c]['pulses'][d]['frequency']*2*pi+self.sweep_elements[c]['pulses'][d]['phase'])
                            else:
                                print('Error: unknown pulse shape %s. pulse %s ignored.'%(pulse['shape'],pulse['name']))
                        sequence_element_counter += 1
                        print('generating sequence element %s'%sequence_element_counter)
                        if self.send_waveforms:
                            for d in arange(0,4):
                                if AWG_channels[d]:
                                    name = self.sweep_elements[c]['name']+'_'+str(b)+'_ch'+str(d+1)
                                    self.AWG.send_waveform(waveforms[d][0],waveforms[d][1], waveforms[d][2], \
                                            name, self.clock)
                                    self.AWG.import_waveform_file(name,name)
                        if self.program_sequence:
                            self.AWG.set_sq_length(sequence_element_counter)
                            self.AWG.set_sqel_loopcnt_to_inf(sequence_element_counter, False)
                            self.AWG.set_sqel_loopcnt(self.sweep_elements[c]['repetitions'], sequence_element_counter)
                            for d in arange(0,4):
                                if AWG_channels[d]:
                                    name = self.sweep_elements[c]['name']+'_'+str(b)+'_ch'+str(d+1)
                                    self.AWG.set_sqel_waveform(name,d+1,sequence_element_counter)

            else:    
                length, offset = self.element_length_and_offset(a)
                waveforms = [[],[],[],[]]
                for b in arange(0,4):
                    if AWG_channels[b]:
                        waveforms[b] = [zeros(length,dtype = float), zeros(length, dtype = int), zeros(length, dtype = int)]
                        for e in arange(0,len(self.channels)):
                            AWG_channel = self.channels[e]['AWG_channel']
                            AWG_channel_index = ['ch1','ch2','ch3','ch4'].index(AWG_channel[0:3])
                            AWG_subchannel_index = ['','m1','m2'].index(AWG_channel[3:5])
                            if (b == AWG_channel_index):
                                if (AWG_subchannel_index == 0):
                                    H = self.channels[e]['high']
                                    L = self.channels[e]['low']
                                    amplitude = (-L-H)/(H-L)
                                    waveforms[b][0] = waveforms[b][0] + amplitude + self.channels[e]['default_voltage']
                                else:
                                    if self.channels[e]['default_voltage'] == self.channels[e]['high']:
                                        waveforms[b][AWG_subchannel_index] == waveforms[b][AWG_subchannel_index] + 1
                for b in arange(0,len(self.elements[a]['pulses'])):
                    pulse = self.elements[a]['pulses'][b]
                    channel_index = self.find_channel(pulse['channel'])
                    cable_delay = self.channels[channel_index]['cable_delay']
                    AWG_channel = self.channels[channel_index]['AWG_channel']
                    AWG_channel_index = ['ch1','ch2','ch3','ch4'].index(AWG_channel[0:3])
                    AWG_subchannel_index = ['','m1','m2'].index(AWG_channel[3:5])
                    if pulse['shape'] == 'rectangular':
                        if AWG_subchannel_index > 0:
                            if pulse['amplitude'] > 0:
                                amplitude = 1
                            else:
                                amplitude = 0
                        else:
                            H = self.channels[channel_index]['high']
                            L = self.channels[channel_index]['low']
                            amplitude = (2*pulse['amplitude']-L-H)/(H-L)
                        for c in arange(self.start_index(self.elements[a]['pulses'][b]['name'], self.elements[a]['name']) + offset - cable_delay, 
                                self.end_index(self.elements[a]['pulses'][b]['name'], self.elements[a]['name']) + offset - cable_delay):
                            waveforms[AWG_channel_index][AWG_subchannel_index][c] = amplitude
                    elif pulse['shape'] == 'sine':
                        if AWG_subchannel_index > 0:
                            print('Error: sine waveform not compatible with marker channel')
                        else:
                            H = self.channels[channel_index]['high']
                            L = self.channels[channel_index]['low']
                            amplitude = (2*pulse['amplitude']-L-H)/(H-L)
                            wv_start = self.start_index(self.elements[a]['pulses'][b]['name'], self.elements[a]['name']) + offset - cable_delay
                            wv_length = self.end_index(self.elements[a]['pulses'][b]['name'], self.elements[a]['name']) + offset - cable_delay - wv_start
                            for c in arange(0, wv_length):
                                waveforms[AWG_channel_index][AWG_subchannel_index][c+wv_start] += amplitude*sin(c*1e-9*self.elements[a]['pulses'][b]['frequency']*2*pi+self.elements[a]['pulses'][b]['phase'])
                    else:
                        print('Error: unknown pulse shape %s. pulse %s ignored.'%(pulse['shape'],pulse['name']))
                sequence_element_counter += 1
                print('generating sequence element %s'%sequence_element_counter)
                if (self.send_waveforms == True) and ((self.update_element == 'all') or (self.update_element == self.elements[a]['name'])):
                    for b in arange(0,4):
                        if AWG_channels[b]:
                            self.AWG.send_waveform(waveforms[b][0],waveforms[b][1], waveforms[b][2], \
                                    self.elements[a]['name']+'_ch'+str(b+1), self.clock)
                            self.AWG.import_waveform_file(self.elements[a]['name']+'_ch'+str(b+1),self.elements[a]['name']+'_ch'+str(b+1))
                if self.program_sequence:
                    self.AWG.set_sq_length(sequence_element_counter)
                    self.AWG.set_sqel_loopcnt_to_inf(sequence_element_counter, False)
                    self.AWG.set_sqel_loopcnt(self.elements[a]['repetitions'], sequence_element_counter)
                    for b in arange(0,4):
                        if AWG_channels[b]:
                            self.AWG.set_sqel_waveform(self.elements[a]['name']+'_ch'+str(b+1),b+1,sequence_element_counter)
                    if self.elements[a]['trigger_wait']:
                        self.AWG.set_sqel_trigger_wait(sequence_element_counter, 1)

        if (self.sequence_repetitions == 0) and (goto_index > -1):
            self.AWG.set_sqel_goto_state(sequence_element_counter, True)
            self.AWG.set_sqel_goto_target_index(sequence_element_counter, goto_index)

        if self.program_channels:
            for b in arange(0,4):
                if AWG_channels[b]:
                    if b == 0:
                        self.AWG.set_ch1_status('on')
                    elif b == 1:
                        self.AWG.set_ch2_status('on')
                    elif b == 2:
                        self.AWG.set_ch3_status('on')
                    elif b == 3:
                        self.AWG.set_ch4_status('on')
                else:
                    if b == 0:
                        self.AWG.set_ch1_status('off')
                    elif b == 1:
                        self.AWG.set_ch2_status('off')
                    elif b == 2:
                        self.AWG.set_ch3_status('off')
                    elif b == 3:
                        self.AWG.set_ch4_status('off')

        if self.program_sequence:
            if self.AWG.get_sq_mode() != 'HARD':
                print('WARNING: AWG not in hardware sequencer mode!')
            else:
                sequence_element_counter = 0
                for a in arange(0,len(self.elements)):
                    if self.elements[a]['name'] == 'sweep':
                        for b in arange(0,self.sweep_count):
                            for c in arange(0,len(self.sweep_elements)):
                                sequence_element_counter += 1
                                element = self.sweep_elements[c]
                                if element['event_jump_index'] > -1:
                                    self.AWG.set_sqel_event_jump_type(sequence_element_counter, 'IND')
                                    self.AWG.set_sqel_event_jump_target_index(sequence_element_counter, element['event_jump_index'])
                                if element['goto_index'] > -1:
                                    self.AWG.set_sqel_goto_state(sequence_element_counter, '1')
                                    self.AWG.set_sqel_goto_target_index(sequence_element_counter, element['goto_index'])
                    else:
                        sequence_element_counter += 1
                        element = self.elements[a]
                        if element['event_jump_index'] > -1:
                            self.AWG.set_sqel_event_jump_type(sequence_element_counter, 'IND')
                            self.AWG.set_sqel_event_jump_target_index(sequence_element_counter, element['event_jump_index'])
                        if element['goto_index'] > -1:
                            self.AWG.set_sqel_goto_state(sequence_element_counter, '1')
                            self.AWG.set_sqel_goto_target_index(sequence_element_counter, element['goto_index'])
            if goto_index > -1:
                self.AWG.set_sqel_goto_state(sequence_element_counter, '1')
                self.AWG.set_sqel_goto_target_index(sequence_element_counter, goto_index)


        if self.start_sequence:
            self.AWG.start()

