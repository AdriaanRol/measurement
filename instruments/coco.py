# python class to access the coincidence counter used for the Bell experiment
# RP by Val Zwiller
#
# Author: Wolfgang Pfaff <w dot pfaff at tudelft dot nl>

import serial
import os, sys, time

import qt
from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import gobject
from numpy import *

## constants for device access
ADDRESS = '/dev/ttyUSB0'
DETECTORS = 8
CHANNELS = 10 # to determine the size of the data within the driver
DEMO = True
GNUPLOT = True

## tools
def bytes_to_int(list_of_bytes):
    """
    converts a list of bytes, hex coded into strings, into a number.
    Important: LSB comes first!

    Example:
        ['\x00', '\x00', '\x01'] = 0*(256**0) + 0*(256**1) + 1*(256**2) = 65536
    """
    number = 0
    for i in range(len(list_of_bytes)):
        number += int(list_of_bytes[i].encode('hex'), 16) * (256**i)
    return number

class coco(CyclopeanInstrument):
    """
    The class describing the counter
    """
    
    verbose = False
    
    def __init__(self, name, addr=ADDRESS, detectors=DETECTORS):
        CyclopeanInstrument.__init__(self, name, tags=[])

        # open the device with some working settings (got that partially from
        # the original c-program and some testing
        self.device = serial.Serial(addr, 115200, timeout=0)
        self.detectors = detectors
        self.maxbytes = 6 * (2**detectors)
        self.t0 = 0. # the time denoting start of a measurement
        self.recording = False # whether to save data to file during measurement
        
        self.single_chans =  {1 : 'Alice V', 
                2 : 'Alice H',
                4 : 'Bob V',
                8 : 'Bob H', }
        self.coincidence_chans = {5 : 'VV', 
                9 : 'VH',
                6 : 'HV',
                10 : 'HH', }

        # create the channels
        chans = []
        for i in range(CHANNELS):
            chans.append('channel_%d' % (i+1))

        self.add_parameter('counts',
                flags=Instrument.FLAG_GET,
                type=types.FloatType,
                units='Hz',
                tags=['measure'],
                channels=tuple(chans),
                channel_prefix='%s_',
                doc="""
                Returns the count rates for all counter channels
                """)

        self.add_parameter('count_interval',
                flags=Instrument.FLAG_GETSET,
                type=types.FloatType,
                units='s',
                minval=0.1,
                maxval=25.5,
                doc="""
                how long the fpga counter measures before writing a result
                to its buffer """)

        self.add_parameter('measurement_time',
                flags=Instrument.FLAG_GETSET,
                type=types.IntType,
                units='s',
                minval=1,
                maxval=999,
                doc="""
                how long to measure if we set it running. 
                999: unlimited """)

        self.add_parameter('measurement_name',
                flags=Instrument.FLAG_GETSET,
                type=types.StringType)
                
        self.add_parameter('buf_len',
                flags=Instrument.FLAG_GETSET,
                type=types.IntType,
                doc="""
                determines the length of the data buffer
                """)

        ### init parameters

        # how often to check the device
        self.set_sampling_interval(250)
        
        self._counts = {}
        for i in range(CHANNELS):
            self._counts['channel_%d' % (i+1)] = 0.
        
        self._buf_len = 150
        self._count_interval = 1
        self._measurement_time = 999
        self._measurement_name = ''

        # cyclopean features
        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': True,
            'set_recording': False,
            'save': False,
            }

    ### get and set functions
    def do_get_counts(self, channel):
        return self._counts[channel]

    def do_get_buf_len(self):
        return self._buf_len

    def do_set_buf_len(self, val):
        self._buf_len = val

    def do_get_count_interval(self):
        return self._count_interval

    def do_set_count_interval(self, val):
        self._count_interval = val

    def do_get_measurement_time(self):
        return self._measurement_time

    def do_set_measurement_time(self, val):
        self._measurement_time = val

    def do_get_measurement_name(self):
        return self._measurement_name

    def do_set_measurement_name(self, val):
        self._measurement_name = val

    ### this function parses the result we get from one read() call
    ### and puts it into a dict of form {counter : events, }
    def parse(self, buf):
        result = {}

        # if the device is running and doesn't get events, there'll be
        # at least the six stop bytes; otherwise, the device is not
        # running, or no new events are written to the hardware buffer yet
        if len(buf) > 0:
            buf = buf[:-6]
            
            # we return an empty dict if there is no result
            if len(buf) > 0:
                for i in range(1, CHANNELS+1):
                    result[i] = 0

                while len(buf) > 0:
                    # first two bytes are the address
                    address = bytes_to_int(buf[:2])
                    buf = buf[2:]

                    # next four bytes contain the value
                    result[address] = bytes_to_int(buf[:4])
                    buf = buf[4:]

        if self.verbose:
            print 'parsing result: %s' % result

        return result

    ### this reads one set of counts from the device
    ### there might be more left, but this function only takes the
    ### first set out of the buffer
    def read(self):
        buf = []
        stopcounts = 0
        bytes_read = 0
        stop = False
        error = False
        
        while(bytes_read < self.maxbytes and not stop and not error):
            b = self.device.read()
            if len(b) > 0:
                bytes_read += len(b)
                buf.append(b)

                # check for the 6 stopbytes that end each readout sequence
                if b == '\xff': 
                    stopcounts += 1
                else:
                    stopcounts = 0

                if stopcounts == 6: 
                    stop = True
            else:
                if self.verbose:
                    print 'device did not return finite data'
                return []
                
        if self.verbose:
            print 'finished reading %d bytes, data = %s' % (len(buf), str(buf))

        if stop:
            return buf
        else:
            return False

   
    ### how to start and stop the hardware
    def stop_device(self):
        # sending a two-byte zero stops the device (setting the measurement
        # time to zero ds)
        self.device.write("\x00\x00")
        qt.msleep(0.1)

        # be polite and empty the buffer
        while len(self.device.read(100)) > 0:
            pass

    def start_device(self):
        # stop first
        self.stop_device()
        # we always operate with 1s integration interval, LSB gets sent first
        lsb = ("\\x%02X" % (int(self._count_interval*10))).decode('string_escape')
        self.device.write(lsb+"\x00")

    ### setup and stop of measurements
    def _start_running(self):
        self.t0 = time.time()
        if self._measurement_time == 999:
            self.t_end = None
        else:
            self.t_end = time.time() + self._measurement_time

        # setup the qtlab data in case we're recording
        if self.record:
            self.d_count = qt.Data(name=self._measurement_name+'_counts')         
            self.d_count.add_coordinate('time [s]')
            self.d_coincidence = qt.Data(name=self._measurement_name+'_coincidences')
            self.d_coincidence.add_coordinate('time [s]')

            for i in range(CHANNELS):
                if (i+1) in self.single_chans:
                    self.d_count.add_value(self.single_chans[(i+1)])
                if (i+1) in self.coincidence_chans:
                    self.d_coincidence.add_value(self.coincidence_chans[(i+1)])

            self.d_count.create_file()
            self.d_coincidence.create_file()

            if GNUPLOT:
                self.plot_count = qt.Plot2D(name='countrates', clear=True,
                        maxpoints=30)
                countdim = 1
                for i in range(CHANNELS):
                    if (i+1) in self.single_chans:
                        self.plot_count.add(self.d_count, coorddim=0, valdim=countdim)
                        countdim+=1

                self.plot_coincidence = qt.Plot2D(name='coincidence rates', clear=True,
                        maxpoints=30)
                coincidencedim = 1
                for i in range(CHANNELS):
                    if (i+1) in self.coincidence_chans:
                        self.plot_coincidence.add(self.d_coincidence, coorddim=0, 
                                valdim=coincidencedim)
                        coincidencedim+=1

    
        self.start_device()
        CyclopeanInstrument._start_running(self)

    def _stop_running(self):
        self.stop_device()
    
    ### we can set a time limit for recording;
    ### if this is negative, then we measure for an unlimited time (well, very long :))
    def _start_recording(self):
        self.record = True
        self.set_is_running(True)

    def _stop_recording(self):
        self.set_is_running(False)
        self.record = False

    ### the actual data acquisition is in here:
    ### we probe the device periodically, and retrieve all available data
    ### !!! make sure this function doesn't take longer to execute
    ### !!! than the frq with which it is invoked!
    def _sampling_event(self):
        
        if not self._is_running:
            return False

        if self.t_end != None and self.t_end < time.time():
            return False

        tval = time.time()-self.t0
        row_count = [tval]
        row_coincidence = [tval]
        
        # read as long as there's data
        result = self.parse(self.read())
    
        while len(result) > 0:
            for i in range(CHANNELS):
                if len(result) == 0:
                    val = 0.
                else:
                    val = result[i+1]

                getattr(self, 'get_channel_%d_counts' % (i+1))()
                if (i+1) in self.single_chans:
                    row_count.append(val)
                if (i+1) in self.coincidence_chans:
                    row_coincidence.append(val)

            if self.record:
                self.d_count.add_data_point(*row_count)
                row_count = [time.time()-self.t0]

                self.d_coincidence.add_data_point(*row_coincidence)
                row_coincidence = [time.time()-self.t0]

            result = self.parse(self.read())

        return True

