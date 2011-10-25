# RS_SMB100.py class, to perform the communication between the Wrapper and the device
# Pieter de Groot <pieterdegroot@gmail.com>, 2008
# Martijn Schaafsma <qtlab@mcschaafsma.nl>, 2008
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
import visa
import types
import logging
import numpy

class RS_SMB100(Instrument):
    '''
    This is the python driver for the Rohde & Schwarz SMB100
    signal generator

    Usage:
    Initialize with
    <name> = instruments.create('name', 'RS_SMB100', address='<GPIB address>',
        reset=<bool>)
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the RS_SMB100, and communicates with the wrapper.

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            reset (bool)     : resets to default values, default=false

        Output:
            None
        '''
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        self._address = address
        self._visainstrument = visa.instrument(self._address)

        self.add_parameter('frequency', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=9e3, maxval=40e9,
            units='Hz', format='%.04e',
            tags=['sweep'])
        self.add_parameter('power', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=-30, maxval=30, units='dBm',
            tags=['sweep'])
        self.add_parameter('status', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('pulm', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('iq', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('sweep_frequency_start', type=types.FloatType,
            flags=Instrument.FLAG_SET,
            minval=9e3, maxval=40e9,
            units='Hz', format='%.04e',
            tags=['sweep'])
        self.add_parameter('sweep_frequency_stop', type=types.FloatType,
            flags=Instrument.FLAG_SET,
            minval=9e3, maxval=40e9,
            units='Hz', format='%.04e',
            tags=['sweep'])
        self.add_parameter('sweep_frequency_step', type=types.FloatType,
            flags=Instrument.FLAG_SET,
            minval=1, maxval=1e9,
            units='Hz', format='%.04e',
            tags=['sweep'])

        self.add_function('reset')
        self.add_function('reset_sweep')
        self.add_function('get_all')

        if reset:
            self.reset()
        else:
            self.get_all()

    # Functions
    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Resetting instrument')
        self._visainstrument.write('*RST')
        self.get_all()

    def get_all(self):
        '''
        Reads all implemented parameters from the instrument,
        and updates the wrapper.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : reading all settings from instrument')
        self.get_frequency()
        self.get_power()
        self.get_status()

    # communication with machine
    
    def _do_set_mode(self, mode):
        '''
        Change mode to list sweep or continious
        '''
        self._visainstrument.write('SOUR:FREQ:MODE %s'%mode)
    def enable_list_mode(self):
        self._visainstrument.write('SOUR:FREQ:MODE LIST')
    def enable_list_step_mode(self):
        self._visainstrument.write('SOUR:LIST:MODE STEP')
    def set_list_ext_trigger_source(self):
        self._visainstrument.write('SOUR:LIST:TRIG:SOUR ext')

    def enable_ext_freq_sweep_mode(self):
        self._visainstrument.write('SOUR:SWE:FREQ:MODE STEP')
        self._visainstrument.write('SOUR:SWE:FREQ:SPAC LIN')
        self._visainstrument.write('TRIG:FSW:SOUR EXT')
        self._visainstrument.write('SOUR:FREQ:MODE SWE')
    def reset_sweep(self):
        self._visainstrument.write('SOUR:SWE:RES:ALL')

    def reset_list_mode(self):
        self._visainstrument.write('SOUR:LIST:RES')
    def learn_list(self):
        self._visainstrument.write('SOUR:LIST:LEAR')


    def _create_list(self, start, stop, unit, number_of_steps):
        flist_l = numpy.linspace(start, stop, number_of_steps)
        flist_s = ''
        k=0
        for f_el in flist_l:
            if k is 0:
                flist_s = flist_s + '%s%s'%(int(flist_l[k]),unit)
            else:
                flist_s = flist_s + ', %s%s'%(int(flist_l[k]),unit)
            k+=1
        return flist_s
    def reset_list(self):
        self._visainstrument.write('ABOR:LIST')

    def load_fplist(self, fstart, fstop, funit , pstart, pstop, punit, number_of_steps):
        self._visainstrument.write('SOUR:LIST:SEL "list_%s_%s_%s"'%(fstart, fstop, number_of_steps))

        flist = self._create_list(fstart, fstop, funit, number_of_steps)
        plist = self._create_list(pstart, pstop, punit, number_of_steps)
        #print flist
        #print plist

        self._visainstrument.write('SOUR:LIST:FREQ '+flist)
        self._visainstrument.write('SOUR:LIST:POW '+plist)
        
        #self._visainstrument.write('')

        
        
        
        
    def _do_get_frequency(self):
        '''
        Get frequency from device

        Input:
            None

        Output:
            frequency (float) : frequency in Hz
        '''
        logging.debug(__name__ + ' : reading frequency from instrument')
        return float(self._visainstrument.ask('SOUR:FREQ?'))

    def _do_set_frequency(self, frequency):
        '''
        Set frequency of device

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting frequency to %s GHz' % frequency)
        self._visainstrument.write('SOUR:FREQ %e' % frequency)

    def _do_set_sweep_frequency_start(self, frequency):
        '''
        Set start frequency of sweep

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting sweep frequency start to %s GHz' % frequency)
        self._visainstrument.write('SOUR:FREQ:STAR %e' % frequency)

    def _do_set_sweep_frequency_stop(self, frequency):
        '''
        Set stop frequency of sweep

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting sweep frequency stop to %s GHz' % frequency)
        self._visainstrument.write('SOUR:FREQ:STOP %e' % frequency)

    def _do_set_sweep_frequency_step(self, frequency):
        '''
        Set step frequency of sweep

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting sweep frequency step to %s GHz' % frequency)
        self._visainstrument.write('SOUR:SWE:FREQ:STEP:LIN %e' % frequency)

    def _do_get_power(self):
        '''
        Get output power from device

        Input:
            None

        Output:
            power (float) : output power in dBm
        '''
        logging.debug(__name__ + ' : reading power from instrument')
        return float(self._visainstrument.ask('SOUR:POW?'))

    def _do_set_power(self,power):
        '''
        Set output power of device

        Input:
            power (float) : output power in dBm

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting power to %s dBm' % power)
        self._visainstrument.write('SOUR:POW %e' % power)

    def _do_get_status(self):
        '''
        Get status from instrument

        Input:
            None

        Output:
            status (string) : 'on or 'off'
        '''
        logging.debug(__name__ + ' : reading status from instrument')
        stat = self._visainstrument.ask(':OUTP:STAT?')

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('Output status not specified : %s' % stat)

    def _do_set_status(self,status):
        '''
        Set status of instrument

        Input:
            status (string) : 'on or 'off'

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting status to "%s"' % status)
        if status.upper() in ('ON', 'OFF'):
            status = status.upper()
        else:
            raise ValueError('set_status(): can only set on or off')
        self._visainstrument.write(':OUTP:STAT %s' % status)

    def _do_get_pulm(self):
        '''
        Get pulse modulation status from instrument

        Input:
            None

        Output:
            pulm (string) : 'on' or 'off'
        '''
        logging.debug(__name__ + ' : reading pulse modulation status from instrument')
	stat = self._visainstrument.ask(':SOUR:PULM:STAT?')

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('Pulse modulation status not specified : %s' % stat)

    def _do_get_iq(self):
        '''
        Get IQ modulation status from instrument

        Input:
            None

        Output:
            iq (string) : 'on' or 'off'
        '''
        logging.debug(__name__ + ' : reading IQ modulation status from instrument')
	stat = self._visainstrument.ask('IQ:STAT?')

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('IQ modulation status not specified : %s' % stat)

    def _do_set_pulm(self,pulm):
        '''
        Switch external pulse modulation

        Input:
            pulm (string) : 'on' or 'off'

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting external pulse modulation to "%s"' % pulm)
        if pulm.upper() in ('ON', 'OFF'):
            pulm = pulm.upper()
        else:
            raise ValueError('set_pulm(): can only set on or off')
        self._visainstrument.write(':PULM:SOUR EXT')
        self._visainstrument.write(':SOUR:PULM:STAT %s' % pulm)

    def _do_set_iq(self,iq):
        '''
        Switch external IQ modulation

        Input:
            iq (string) : 'on' or 'off'

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting external IQ modulation to "%s"' % iq)
        if iq.upper() in ('ON', 'OFF'):
            iq = iq.upper()
        else:
            raise ValueError('set_iq(): can only set on or off')
        self._visainstrument.write('IQ:SOUR ANAL')
        self._visainstrument.write('IQ:STAT %s'%iq)

    # shortcuts
    def off(self):
        '''
        Set status to 'off'

        Input:
            None

        Output:
            None
        '''
        self.set_status('off')

    def on(self):
        '''
        Set status to 'on'

        Input:
            None

        Output:
            None
        '''
        self.set_status('on')
