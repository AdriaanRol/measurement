### needed if used as instrument
from instrument import Instrument
import instruments
import types

import numpy
import scipy.special 


###############################################################################
### This is the original instrument class I got from Gijs in Ocy 2011
###############################################################################

class AWG_shaped_pulse(Instrument):
    '''
    this is a dummy pulse source
    supported pulseshapes
    gauss, 
    rect, 
    AdInv (pi pulse using adiabatic inversion)
    
    '''

    def __init__(self, name, channel='ch1', shape='rect', clock=1e9, reset=False, filepath=None, amplitude = 1, bandwidth = 200e6, inversion_time = 500e-9, inversion_rise_time = 50e-9,w_power = 10, mwsource = 'Agilent_8267C'):

        Instrument.__init__(self, name, tags=['mw_pulse_sequence_member'])
        
        self.add_parameter('start',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=0, maxval=100,
                units='sec')
        self.add_parameter('length',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=0, maxval=100,
                units='sec')
        self.add_parameter('clock',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=0, maxval=1.2e9,
                units='Hz')
        self.add_parameter('amplitude',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=-1., maxval=1.,
                units='Volts')

        self.add_parameter('frequencies',
                type=types.ListType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                units='rel freq (Hz)')

        self.add_parameter('phases',
                type=types.ListType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                units='deg.')

        self.add_parameter('lines',
                type=types.ListType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                units='rel ampl')

        self.add_parameter('shape',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('profile',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('profile_shape',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('mod_pulse_length',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('mod_pulse_length2',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('modperiod',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('modperiod2',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('risetime',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('reduce_slope',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET)

        self.add_parameter('inversion_time',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=0, maxval=1,
                units='s')
        self.add_parameter('inversion_bandwidth',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=0, maxval=1e9,
                units='Hz')

        self.add_parameter('channel',
                type=types.ListType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=1, maxval=4)
        self.add_parameter('is_marker',
                type=types.BooleanType,
                flags=Instrument.FLAG_GET)
        self.add_parameter('marker_no', 
                type=types.ListType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=1, maxval=2)

        self.add_parameter('frequency',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=0, maxval=1e9,
                units='Hz')
        self.add_parameter('phase',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET | \
                Instrument.FLAG_GET_AFTER_SET,
                minval=-90, maxval=90,
                units='deg')
        
        self._profile=True
        self._profile_shape = 'Wurst'
        self._square_wave_mod_type = '1'
        self.mw_source = mwsource
        self.add_function('reset')
        self.add_function('get_all')
        self._0dbm_rabi_f = 20e6 #hz
        true = True
        false=False
        # these are dummy values for an instrument that
        # is already running
        self._instruments = instruments.get_instruments()
        self.mw_source = self._instruments.get(mwsource)
        self._reduce_slope = False
        self._clock = clock
        self._clock = self._do_get_clock()
        self._do_set_clock(self._clock)
        self._start = 1e-9
        self._stop = 1e-6 #debugging                                    
        self._length = 10e-9
        self._amplitude = amplitude
        self.inversion_sweep_type = 'linear' 
        self._generate_fraction = 1
        self.mw_driving_strength = 20e6 
        self._shape = shape
        self._channel = [int(channel[channel.find('ch')+2])] #'ch1m1' for markers and ch1 for waveform out
        mfind = channel.find('m')
        self._type = 'pulse'
        self.name = name
        #print self._type
        if self._shape == 'P1pulse':
            self._frequencies = [-114,-81,0,81,114]
            self._lines=[1,1,1,1,1]
            self._phases=[0,0,0,0,0]
            self._risetime  = 3
            self._power = w_power
        if self._shape == 'AWG_RF_pulse':
            self._frequencies = [2.93609]
            self._lines=[1]
            self._phases=[0]
            self._risetime  = 0.3 #us
            self._power = 10
            self._modperiod = 10e-6 #us
            self._mod_pulse_length_on = 10e-6



        if self._shape == 'AdInv':
            print 'this is the adiabatic inversion pulse'
            self._sweep_direction = 'pos'
            self._inversion_bandwidth = bandwidth
            self._inversion_time = inversion_time
            self._inversion_rise_time = inversion_rise_time
            self._power = w_power
        if self._shape == 'gauss':
            self._sigma_t = 3e-9
            self._cutoff = 3
            self.get_length()
        elif self._shape == 'file':
            waveform = self._load_waveform_from_file(filepath)
            length=len(waveform)
            self._length=1000 #!!!!!!!!!!!!!!!!! need to figure out how to put in waveforms from outside!!!!!!!!!!!!!!!!!  
        if self._shape == 'sin':
            self._frequency = 1e6
            self._phase = 0
        if mfind == -1:
            self._is_marker = False
            self._marker_no = [[0]]
        else:
            self._is_marker = True
            self._marker_no = [[int(channel[mfind+1])]]
            self._amplitude = 1
        self.get_channel()
        self.get_marker_no()
        self.get_is_marker()




        if reset:
            self.reset()
        else:
            self.get_all()

#### initialization related

    def reset(self):
        print __name__, ': resetting instrument'

        #this resets the values of the 'dummy' instrument:
        self.set_start(2e-9)
        self.set_length(2e-9)
        self.set_amplitude(2)


        #this updates all the variables in memory to the instrument values
        self.get_all()
    
    def set_pulse_property(self, property, value):
        eval_string = '%s.set_%s(%s)'%(self,property,value)
        eval(eval_string)
    def _do_get_shape(self):
        return self._shape
    def _do_set_shape(self,shape):
        self._shape=shape
    def set_generate_fraction(self, fraction):
        self._generate_fraction = fraction
    def get_generate_fraction(self):
        return self._generate_fraction
    def _do_set_lines(self, lines):
        self._lines = lines
    def _do_get_lines(self):
        return self._lines
    def _do_get_frequencies(self):
        return self._frequencies
    def _do_set_frequencies(self, frequencies):
        self._frequencies = frequencies
    def _do_set_risetime(self, risetime):
        self._risetime = risetime
    def _do_get_risetime(self):
        return self._risetime
    def _do_set_reduce_slope(self, state = True):
        self._reduce_slope = state
    def _do_get_reduce_slope(self):
        return self._reduce_slope


    def _do_get_channel(self):
        return self._channel

    def _do_set_channel(self, channel):
        self._channel = channel

    def _do_get_is_marker(self):
        return self._is_marker

    def _do_get_marker_no(self):
        return self._marker_no

    def _do_set_marker_no(self, markerno):
        self._marker_no  = markerno
        print 'this can not be done yet'

    def get_all(self):
        print __name__, ': reading all settings from %s'%self._name

        self.get_start()
        self.get_length()
        self.get_amplitude()
    
    def get_pulse_src(self):
        return self._instruments.get(self.name)



#### communication with machine
    def _do_get_shape(self):
        return self._shape

    def _do_get_start(self):
        return self._start
    
    def get_stop(self):  #debugging
        return self._stop

    def _do_set_start(self, start):
        self._start = start

    def _do_set_clock(self,clock):
        self._clock=clock
        
    def _do_get_clock(self):
        if self._instruments['AWG'] is not None:
            self._clock = self._instruments['AWG'].get_clock()
        else:
            self._clock = 1e9
        return self._clock
        
    def set_stop(self, stop): #debugging
        self._stop = stop


    def _do_get_length(self,fixed='stop'):
        if self._shape == 'rect':
            pass            
        elif self._shape == 'gauss':
            length_p=self._get_number_of_points_in_gauss(self._sigma_t, self._cutoff)
            self._length = length_p/self._clock
        elif self._shape == 'AdInv':
            self._length = int((self.get_inversion_time()*self._generate_fraction*self._clock))/self._clock
        elif self._shape == 'sequence':
            length = self._length
        elif self._shape == 'sin':
            pass
        else:
            pass
            #print 'pulseshape unknown, asumed rectangular pulse_shape or equivalent'
        return self._length
    def set_reduce_slope(self, state):
        self._reduce_slope = state
#adiabatic inversion routines            
    def get_number_of_points_in_AdInv(self):
        number_of_points = self._clock*self.get_inversion_time()
        return number_of_points
    def set_inversion_sweep_type(self, type = ''):
        self.inversion_sweep_type = type
    def get_inversion_sweep_type(self):
        return self.inversion_sweep_type
    def _do_set_inversion_time(self, time):
        self._inversion_time = time
    def _do_get_inversion_time(self):
        return self._inversion_time
    def _do_set_inversion_bandwidth(self, bandwidth):
        self._inversion_bandwidth = bandwidth
    def _do_get_inversion_bandwidth(self):
        return self._inversion_bandwidth
    def get_sweep_direction(self):
        return self._sweep_direction
    def set_sweep_direction(self, direction = 'pos'):
        return self._sweep_direction
    def set_mw_driving_strength(self, driving_strength = 20e6):
        self.mw_driving_strength = driving_strength

    def set_odbm_rabi_f(self, rabi_f):
        self._0dbm_rabi_f = rabi_f
    def get_0dbm_rabi_f(self):
        self.get_mw_power()
        return self.mw_driving_strength


    def set_mw_source(self, source_inst):
        self.mw_source = source_inst
    def get_mw_power(self):
        self._mw_power = self.mw_source.get_power()
        f_driv = self.get_amplitude()*self._0dbm_rabi_f*10**(self._mw_power/20)
        self.set_mw_driving_strength(f_driv)
        return self._mw_power
    def get_inversion_rise_time(self): #23/08
        return self._inversion_rise_time
    def get_power(self):  #wurst power
        return self._power
    def set_inversion_rise_time(self, no):  #23/08
        self._inversion_rise_time = no
    def set_power(self,no):
        self._power = no
    def set_square_wave_mod_type(self, type ='1'):
        self._square_wave_mod_type = type
    def get_square_wave_mod_type(self):
        return self._square_wave_mod_type
    def _do_set_profile(self, state = True):
        self._profile=state
    def _do_set_profile_shape(self, shape = 'Wurst'):
        self._profile_shape = shape
    def _do_set_modperiod(self, period):
        self._modperiod = period
    def _do_set_mod_pulse_length(self, pulse_length):
        self._mod_pulse_length_on = pulse_length
    def _do_set_modperiod2(self, period):
        self._modperiod2 = period
    def _do_set_mod_pulse_length2(self, pulse_length):
        self._mod_pulse_length_on2 = pulse_length


    def _do_get_profile(self):
        return self._profile
    def _do_get_profile_shape(self):
        return self._profile_shape
    def _do_get_modperiod(self):
        return self._modperiod
    def _do_get_mod_pulse_length(self):
        return self._mod_pulse_length_on
    def _do_get_modperiod2(self):
        return self._modperiod2
    def _do_get_mod_pulse_length2(self):
        return self._mod_pulse_length_on2

    def _do_set_phases(self,phases):
        self._phases=phases
    def _do_get_phases(self):
        return self._phases
    def _generate_P1bath_pulse(self, p1_phase=0):
        pi= numpy.pi
        length=self._length
        clock = self._clock
        phases = self._phases
        time = numpy.linspace(0,length-1e-9,clock*length)
        hf1 = 114e6
        hf2 = 81e6
        a=self._amplitude
        lines=self._lines
        sin=numpy.sin
        cos = numpy.cos
        wf1=0.2*a*sin(2*pi*hf1*time)
        risetime = self._risetime
        power = self._power
        #print power
        #print wf1
        #wf2=0.2*a*sin(2*pi*hf2*time)
        #wf1r = 0.2*a*cos(2*pi*hf1*time)
        #wf2r = 0.2*a*cos(2*pi*hf2*time)
        I=numpy.array(len(time)*[0])
        Q=numpy.array(len(time)*[0])
        f=self._frequencies
        for k in range(len(f)):

            I=I+lines[k]*1*cos(2*pi*(f[k]*1e6*time+phases[k]/360.))
            Q=Q+lines[k]*1*sin(2*pi*(f[k]*1e6*time+phases[k]/360.))
            #print Q
        #print self.wurst(arange(clock*length),arange(clock*length),power)
        if length>1e-9:
            if self._profile:
                if self._profile_shape == 'Wurst':
                    I = self.wurst(time,length-1e-9,power)*I
                    Q = self.wurst(time,length-1e-9,power)*Q
                elif self._profile_shape == 'Erf':
                    I = self.error_function_shape(time*1e9, self._power * 1000)*I
                    Q = self.error_function_shape(time*1e9, self._power * 1000)*Q
            else:
                pass
        #print 'yyy%s' %time
        #print self.wurst(time,risetime,power)

        return [I.tolist(), Q.tolist()] 
    
    def _generate_AWG_RF_pulse(self):
        '''
        This generates a pulse shaped by the AWG on one channel, the other channel is filled with zeros
        '''
        pi= numpy.pi
        length=self._length
        clock = self._clock
        phases = self._phases
        time = numpy.linspace(0,length-1e-9,clock*length)
        a=self._amplitude
        lines=self._lines
        sin = numpy.sin
        cos = numpy.cos
        risetime = self._risetime
        power = self._power
        I=numpy.array(len(time)*[0])
        Q=numpy.array(len(time)*[0])
        f=self._frequencies
        for k in range(len(f)):
            I=I+lines[k]*1*cos(2*pi*(f[k]*1e6*time+phases[k]/360.))
        if length>1e-9:
            if self._profile:
                if self._profile_shape == 'Wurst':
                    I = self.wurst(time,length-1e-9,power)*I
                elif self._profile_shape == 'Erf':
                    I = self.error_function_shape(time*1e6, risetime*1e6)*I
                elif self._profile_shape == 'Erf_mod':
                    period = self._modperiod
                    pulse_length = self._mod_pulse_length_on
                    I = self.modulate_periodically(time*1e6, risetime*1e6, period*1e6, pulse_length*1e6)*I
                elif self._profile_shape == 'Erf_mod_mod':
                    period = self._modperiod
                    pulse_length = self._mod_pulse_length_on
                    period2 = self._modperiod2
                    pulse_length2 = self._mod_pulse_length_on2
                    I = self.modulate_periodically(time*1e6, risetime*1e6, period*1e6, pulse_length*1e6)*I
                    #I = self.modulate_periodically(time*1e6, risetime*1e6, period2*1e6, pulse_length2*1e6)*I
                    I = self.modulate_with_square_wave(time*1e6, period2*1e6, pulse_length2*1e6, type = self._square_wave_mod_type)*I
            else:
                pass
        return [I.tolist(), Q.tolist()] 

    def error_function_shape(self, time_array, risetime_us):
        #This creates an error function-like rise of the pulse
        envelope_start = 0.5 + 0.5 * scipy.special.erf(-2 + (time_array-time_array[0])/risetime_us)
        envelope_end   = 0.5 + 0.5 * scipy.special.erf(-(2 + (time_array - time_array[-1])/risetime_us))
        envelope = envelope_start * envelope_end
        nr_of_points = len(time_array)
        for i in arange(0, nr_of_points):
            if envelope[i] > 0.999:
                envelope[i]=1
        return envelope  

    def modulate_periodically(self, time_array, risetime, period_us, length_on_us):
        '''
        This periodically turns the input pulse on and off with an error function profile
        Starting with the pulse off for length = (period - length_on_us)/2, then on for length_on_us and then off for (period - length_on_us)/2, repeating
        '''
        nr_of_periods = int(round(time_array[-1]/period_us))
        print 'nr_of_periods =%s' % nr_of_periods
        length_off_us = period_us - length_on_us
        
        #print 'length_off_us = %s' % length_off_us
        #print 'nr_of_periods = %s' % nr_of_periods
        envelope = numpy.zeros(len(time_array))

        index_period_start = 0
        index_period_stop = 0
        #Find index corresponding to end of ith period
        for i in arange(0, int(nr_of_periods)):
            while time_array[index_period_stop] < (i+1)*period_us and index_period_stop < len(time_array)-1:
                index_period_stop += 1
            #print 'index_period_stop=%s' % index_period_stop

            #Find index corresponding to end of first period of off time
            index_off = index_period_start
            while time_array[index_off] < i*period_us + length_off_us/2.:
                index_off += 1
            #print 'index_off=%s' %index_off
            #Find index corresponding to end of first period of on time
            index_on = index_off
            while time_array[index_on] <  i*period_us + length_on_us + length_off_us/2.:
                index_on += 1
            #print 'index_on=%s' %index_on
            envelope[index_off:index_on] = self.error_function_shape(time_array[index_off:index_on], risetime)
            index_period_start = index_period_stop
        
        #print 'length time_array = %s' % (len(time_array))
        #print 'length envelope   = %s' % (len(envelope))
        return envelope

    def modulate_with_square_wave(self, time_array, period_us, length_on_us, type = '1'):
        '''
        type: set to '1' to create off - on - on - off, or or to '2' to create on - off - off - on
        '''
        nr_of_periods = int(round(time_array[-1]/period_us))
        print 'nr_of_periods =%s' % nr_of_periods
        length_off_us = period_us - length_on_us
        
        #print 'length_off_us = %s' % length_off_us
        #print 'nr_of_periods = %s' % nr_of_periods
        if type == '1':
            envelope = numpy.zeros(len(time_array))
        elif type=='2':
            envelope = numpy.ones(len(time_array))
        else:
            print 'UKNOWN TYPE!!!!!!'

        index_period_start = 0
        index_period_stop = 0
        #Find index corresponding to end of ith period
        for i in arange(0, int(nr_of_periods)):
            while time_array[index_period_stop] < (i+1)*period_us and index_period_stop < len(time_array)-1:
                index_period_stop += 1
            #print 'index_period_stop=%s' % index_period_stop

            #Find index corresponding to end of first part (first part is either ON or OFF depending on type)
            index_off = index_period_start
            while time_array[index_off] < i*period_us + length_off_us/2.:
                index_off += 1
            #print 'index_off=%s' %index_off

            #Find index corresponding to end of second part (second part is either OFF-OFF or ON-ON depending on type)
            index_on = index_off
            while time_array[index_on] <  i*period_us + length_on_us + length_off_us/2.:
                index_on += 1
            #print 'index_on=%s' %index_on
            if type == '1':
                envelope[index_off:index_on] = 1.0
            if type == '2':
                envelope[index_off:index_on] = 0

            index_period_start = index_period_stop
        
        #print 'length time_array = %s' % (len(time_array))
        #print 'length envelope   = %s' % (len(envelope))
        return envelope


    def wurst(self,x,rise_time,power):
        y = (1-(numpy.sin((x-rise_time/2)*numpy.pi/rise_time)**self.get_power()))* (1-(numpy.sin((x-(x[-1]-rise_time/2))*numpy.pi/rise_time)**self.get_power()))
        #print 'x%s' %x
         #print 'y%s' %y
        return y

    def _generate_inversion_pulse_wurst(self): #23/08
        pi = numpy.pi
        inversion_sweep_type = self.inversion_sweep_type
        sweep_dir = self.get_sweep_direction()
        dir = (-1)**sweep_dir.find('pos')
        bandwidth = self.get_inversion_bandwidth()
        clock = self._clock
        time = self.get_inversion_time()
        omega = (2*numpy.pi*numpy.linspace(0,bandwidth,clock*time/2+1)).tolist()
        time_base = numpy.linspace(0, time, 2*len(omega)-1)
        #print 'time_base %s'%len(time_base)

                    
        if self.inversion_sweep_type == 'truly_linear':
            mwpower = self.get_mw_power()
            mw_driving_strength = self.mw_driving_strength
            epsilon = 0.5 - 1/pi*numpy.arctan(bandwidth/mw_driving_strength)
            tan_arg = (pi*((2*epsilon-1)/time*time_base+ 0.5-epsilon))
            omega_sweep = mw_driving_strength*numpy.tan(abs(tan_arg))
            print 'True linear sweep'
        elif self.inversion_sweep_type == 'linear':
                        #print omega
            omega_sweep = numpy.array(omega[::-1] + omega[1::])
            #print 'omega_sweep %s'%len(omega_sweep)
        elif self.inversion_sweep_type == 'quadratic':
            omega_sweep = numpy.array(((arange(int(time*clock/2+1))[::-1]/time/clock*2)**2).tolist() + (((arange(int(time*clock/2))+1)/time/clock*2)**2).tolist())*bandwidth*2*pi   #modulation see notebook (mathematica) file


        phasey = numpy.array(len(omega[::-1])*[-dir*pi/2] + len(omega[1::])*[dir*pi/2])
        argx = omega_sweep*(0.5*(time_base-0.5*time))
        #print 'argx %s'%len(argx)

        argy = omega_sweep*(0.5*(time_base-0.5*time))+phasey
        ww = self.wurst(arange(len(argx))*1e-9,self.get_inversion_rise_time(),self.get_power())
        #print ww
        x_channel = (2**-0.5*self._amplitude*numpy.cos(argx)*ww).tolist()  
        y_channel = (2**-0.5*self._amplitude*numpy.cos(argy)*ww).tolist()
        if self._inversion_time == 0:
            x_channel = []
            y_channel = []

        return [x_channel[0:int(self._generate_fraction*len(x_channel))-1], y_channel[0:int(self._generate_fraction*len(x_channel))-1]]



    def _generate_inversion_pulse(self):
        pi = numpy.pi
        inversion_sweep_type = self.inversion_sweep_type
        sweep_dir = self.get_sweep_direction()
        dir = (-1)**sweep_dir.find('pos')
        bandwidth = self.get_inversion_bandwidth()
        clock = self._clock
        time = self.get_inversion_time()
        omega = (2*numpy.pi*numpy.linspace(0,bandwidth,clock*time/2+1)).tolist()
        time_base = numpy.linspace(0, time, 2*len(omega)-1)
        #print 'time_base %s'%len(time_base)

                    
        if self.inversion_sweep_type == 'truly_linear':
            mwpower = self.get_mw_power()
            mw_driving_strength = self.mw_driving_strength
            epsilon = 0.5 - 1/pi*numpy.arctan(bandwidth/mw_driving_strength)
            tan_arg = (pi*((2*epsilon-1)/time*time_base+ 0.5-epsilon))
            omega_sweep = mw_driving_strength*numpy.tan(abs(tan_arg))
            print 'True linear sweep'
        elif self.inversion_sweep_type == 'linear':
                        #print omega
            omega_sweep = numpy.array(omega[::-1] + omega[1::])
            #print 'omega_sweep %s'%len(omega_sweep)
        elif self.inversion_sweep_type == 'quadratic':
            omega_sweep = numpy.array(((arange(int(time*clock/2+1))[::-1]/time/clock*2)**2).tolist() + (((arange(int(time*clock/2))+1)/time/clock*2)**2).tolist())*bandwidth*2*pi


        phasey = numpy.array(len(omega[::-1])*[-dir*pi/2] + len(omega[1::])*[dir*pi/2])
        argx = omega_sweep*(0.5*(time_base-0.5*time))
        #print 'argx %s'%len(argx)

        argy = omega_sweep*(0.5*(time_base-0.5*time))+phasey
        x_channel = (2**-0.5*self._amplitude*numpy.cos(argx)).tolist()
        y_channel = (2**-0.5*self._amplitude*numpy.cos(argy)).tolist()
        if self._inversion_time == 0:
            x_channel = []
            y_channel = []

        return [x_channel[0:int(self._generate_fraction*len(x_channel))-1], y_channel[0:int(self._generate_fraction*len(x_channel))-1]]



    def _do_set_length(self, length,fixed='stop'):
        if self._shape is 'gauss':
            self._length = length
            self._sigma_t = length/2/self._cutoff + 1/self._clock
        else:
            self._length = length
    def set_sigma(self, sigma):
        self._sigma_t = sigma
        self.get_length()
    
    def get_sigma(self):
        return self._sigma_t

    def set_cutoff(self, cutoff):
        self._cutoff = cutoff
        self.get_length()

    def get_cutoff(self):
        return self._cutoff

    def _do_get_amplitude(self):
        return self._amplitude

    def _do_set_amplitude(self, amplitude):
        self._amplitude = amplitude
    
    def _do_set_frequency(self,frequency):
        self._frequency = frequency

    def _do_set_phase(self,sin_phase):
        self._phase = sin_phase

    def _do_get_frequency(self):
        return self._frequency

    def _do_get_phase(self):
        return self._phase

    
    def get_el_type(self):
        return self._type

    def _do_get_number_of_points(self):
        clock=self._clock
        length=self.get_length()

        if self._shape == 'gauss':
            self._no_of_points = self._get_number_of_points_in_gauss(self._sigma_t, self._cutoff)
        elif self._shape == 'rect':
            self._no_of_points = clock*(length)
        elif self._shape == 'AdInv':
            self._no_of_points = self.get_number_of_points_in_AdInv()
        elif self._shape == 'sin':
            self._no_of_points = clock*(length)
        elif self._shape== 'P1pulse':
            self._no_of_points = clock*(length)
        elif self._shape== 'AWG_RF_pulse':
            self._no_of_points = clock*(length)


        else:
            print 'pulse shape specifier unknown, assumed rectangle'
            self._no_of_points = clock*(length)
        return self._no_of_points

    def __get_number_of_points_in_gauss(self, sigma_t, cutoff=3):
        sigma_p = self._clock*sigma_t
        return int(2*cutoff*sigma_p+1)
           
    def _gaussian(self, sigma_t, cutoff=3):
        clock=self._clock
        if sigma_t == 0:
            pulse_wform = numpy.array([0])

        else:
            sigma_p = int(sigma_t*clock)
            h_width_t = cutoff*sigma_t
        
            h_width_p = sigma_p*cutoff
            #print h_width_p,int(2*h_width_p+1)
            x=numpy.linspace(-h_width_p, h_width_p, int(2*h_width_p+1))
            pulse_wform = numpy.exp(-(((x/sigma_p)**2)/2))
            #print pulse_wform
        return pulse_wform
    
    def _gaussian2(self, x, sigma_t, cutoff=3):
        clock=self._clock
       
               
        #print h_width_p,int(2*h_width_p+1)
        xm = (x[0]+x[-1])/2.
        pulse_wform = numpy.exp(-(((abs(x-xm)/(sigma_t/clock))**2)/2))
        #print 'sigma_t%s' %sigma_t
        #print pulse_wform
        return pulse_wform


    def _rect(self):         
        clock=self._clock
        length = self._length
        pulse_wform =  int(length*clock)*[self._amplitude]
        if self._reduce_slope and (len(pulse_wform) > 2):
            pulse_wform[0] = 0.5*self._amplitude
            pulse_wform[-1]= 0.5*self._amplitude
        return pulse_wform
    

    def _sin(self):
        clock=self._clock
        length=self._length
        frequency=self._frequency
        sin_phase = self._phase
        x = arange(0,int(length*clock))*1./clock
        #print 'sin_phase = %s'%sin_phase
        pulse_wform =self._amplitude*numpy.cos(2*numpy.pi*frequency*(x-1.75e-6) + numpy.pi/180.0*sin_phase)
        #if length < 250:
        #    gauss_rise=length
        #else:
        gauss_rise = 250
        for ind_x in range(gauss_rise):
            pulse_wform[ind_x] = pulse_wform[ind_x]*numpy.exp(-((250.0-ind_x)/100.0)**2)
            pulse_wform[-ind_x] = pulse_wform[-ind_x]*numpy.exp(-((250.0-ind_x)/100.0)**2)

        #print 'wf=%s'%(self._amplitude*numpy.sin(2*numpy.pi*frequency*x + sin_phase),)

        return pulse_wform.tolist()

    def _load_waveform_from_file(self, filepath):
        '''
        need to look into how to do this
        '''
        return numpy.array(1000*[0])

    def generate_wform(self, phase_P=0):
        clock=self._clock
        shape=self._shape
        
        if shape == 'gauss':
            sigma_t = self._sigma_t
            cutoff = self._cutoff
            pulse_wform_array = (self._amplitude*self._gaussian(sigma_t, cutoff))
            pulse_wform = [[pulse_wform_array.tolist()]]
            self._length = max(pulse_wform_array.shape)
        elif shape == 'P1pulse':
            lines = self._lines
            pulse_wform1, pulse_wform2 = self._generate_P1bath_pulse(p1_phase=phase_P)
            pulse_wform = [pulse_wform1, pulse_wform2] 
        elif shape == 'AWG_RF_pulse':
            lines = self._lines
            pulse_wform1, pulse_wform2 = self._generate_AWG_RF_pulse()
            pulse_wform = [pulse_wform1, pulse_wform2] 
        elif shape == 'rect':
            pulse_wform = [[self._rect()]]
        elif shape == 'AdInv':
            pulse_wform1, pulse_wform2 = self._generate_inversion_pulse_wurst()
            pulse_wform = [pulse_wform1, pulse_wform2]
        elif shape == 'sin':
            pulse_wform = [[self._sin()]]
        elif shape == 'file':
            pulse_wform = self.load_waveform_from_file(self._filename)
            
        else:
            print 'unknown pulse_shape, assumed rectangular shaped pulse'
            pulse_wform = [[self._rect()]]
        return pulse_wform #the list in list is to make it compatible with virtual sequence instrument that generates the actual AWG waveforms with gates?

    def generate_wform_single_channel(self, phase_P=0):
        clock=self._clock
        shape=self._shape
        
        if shape == 'P1pulse':
            lines = self._lines
            pulse_wform1, pulse_wform2 = self._generate_P1bath_pulse(p1_phase=phase_P)
            pulse_wform = [pulse_wform1] 
        elif shape == 'AWG_RF_pulse':
            lines = self._lines
            pulse_wform = self._generate_AWG_RF_pulse()[0]
            pulse_wform = [[pulse_wform]]
            print 'length=', (len(pulse_wform))
        elif shape == 'rect':
            pulse_wform = [[self._rect()]]
            print 'length=', (len(pulse_wform))
        elif shape == 'sin':
            pulse_wform = [[self._sin()]]
        else:
            print 'unknown pulse_shape, assumed rectangular shaped pulse'
            pulse_wform = [[self._rect()]]
        return pulse_wform 

        

    



