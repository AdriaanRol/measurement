# demo 2d scanner. 
#
# author: wolfgang pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import time
import numpy

import qt

class scan2d_demo(CyclopeanInstrument):
    def __init__(self, name):
        CyclopeanInstrument.__init__(self, name, tags=['measure'])

        # also get the counter, need to disable when linescanning
        self._counters = qt.instruments['counters_demo']
        self._counter_was_running = False

        # add the relevant parameters for a 2D PL scanner
        self.add_parameter('pixel_time', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='ms',
                           minval=1.0, maxval=99.0,
                           doc="""
                           Integration time per image pixel.
                           """)

        self.add_parameter('xstart',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um')
        
        self.add_parameter('xstop',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um')
        
        self.add_parameter('ystart',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um')
        
        self.add_parameter('ystop',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um')
        
        self.add_parameter('xsteps',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='')
        
        self.add_parameter('ysteps',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='')
        
        self.add_parameter('last_line_index',
                           type=types.ObjectType,
                           flags=Instrument.FLAG_GET,
                           units='',
                           doc="""
                           Returns the index of the last line of which data 
                           is available.
                           """)
        
        self.add_parameter('last_line',
                           type=types.ObjectType,
                           flags=Instrument.FLAG_GET,
                           units='cps',
                           doc="""
                           Returns the last line of the measured data.
                           """)
        
        self.add_parameter('counter',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET)


        # relevant functions to be visible outside
        self.add_function('get_line')
        self.add_function('get_lines')
        self.add_function('get_x')
        self.add_function('get_y')
        self.add_function('get_data')
        self.add_function('setup_data')
        # self.add_function('move_abs_xy')

        # default params
        self.set_pixel_time(1.0)
        self.set_xstart(-2.0)
        self.set_xstop(2.0)
        self.set_ystart(-2.0)
        self.set_ystop(2.0)
        self.set_xsteps(11)
        self.set_ysteps(11)
        self.set_counter(1)  
          
        # more set up
        self.setup_data()        
        self._current_line = 0
        self._last_line = 0
        self._busy = False

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': True,
            }

    # get and set functions
    def do_set_pixel_time(self, val):
        self._pixel_time = val

    def do_get_pixel_time(self):
        return self._pixel_time

    def do_set_measuring(self, val):
        self._measuring = val

    def do_get_measuring(self):
        return self._measuring

    def do_set_xstart(self, val):
        self._xstart = val

    def do_get_xstart(self):
        return self._xstart

    def do_set_xstop(self, val):
        self._xstop = val

    def do_get_xstop(self):
        return self._xstop

    def do_set_ystart(self, val):
        self._ystart = val

    def do_get_ystart(self):
        return self._ystart

    def do_set_ystop(self, val):
        self._ystop = val

    def do_get_ystop(self):
        return self._ystop

    def do_set_xsteps(self, val):
        self._xsteps = val

    def do_get_xsteps(self):
        return self._xsteps

    def do_set_ysteps(self, val):
        self._ysteps = val

    def do_get_ysteps(self):
        return self._ysteps

    def do_get_last_line(self):
        return self._data[self._last_line,:].tolist()

    def do_get_last_line_index(self):
        return self._last_line

    def do_set_counter(self, val):
        self._counter = val

    def do_get_counter(self):
        return self._counter
    

    # the publicly visible functions declared above
    def get_line(self, line):            
        return self._data[line,:].tolist()

    def get_lines(self, lines):
        return self._data[lines,:].tolist()

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y
    
    def get_data(self):
        return self._data.tolist()
    
    def setup_data(self):
        self.reset_data('scan', (self._ysteps, self._xsteps))
        
        self._x = numpy.r_[self._xstart:self._xstop:self._xsteps*1j]
        self._y = numpy.r_[self._ystart:self._ystop:self._ysteps*1j]
        self.set_data('x', self._x)
        self.set_data('y', self._y)
        
        # setup demo data
        xx, yy = numpy.meshgrid(self._x, self._y)
        self._demo_data = numpy.exp(-xx**2-yy**2)

    # overloading save function
    def save(self, meta=""):
        CyclopeanInstrument.save(self, meta)

        
    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)

        # make sure the counter is off.
        if self._counters.get_is_running():
            self._counter_was_running = True
            self._counters.set_is_running(False)
        
        self.setup_data()
        self._current_line = 0
        self._last_line = 0
        self._next_line()

    def _stop_running(self):
        if self._counter_was_running:
            self._counters.set_is_running(True)
            self._counter_was_running = False
        return
    
    def _sampling_event(self):
        if not self._is_running:
            return False
        
        if self._busy: 
            if time.time() < self._line_start_time + self._x.size * self._pixel_time / 1000.:
                return True
            else:
                self._busy = False
        
        self.set_data('scan', self._demo_data[self._current_line,:],
                [slice(self._current_line, self._current_line+1)])
        self._last_line = self._current_line
        self._current_line += 1
        
        if self._current_line <= self._y.size - 1:
            self._next_line()
            return True
        else:
            self.save()        
            self.set_is_running(False)
            if self._counter_was_running:
                self._counters.set_is_running(True)
                self._counter_was_running = False
            return False

    def _next_line(self):
        self._busy = True
        self._line_start_time = time.time()
        return True

    
