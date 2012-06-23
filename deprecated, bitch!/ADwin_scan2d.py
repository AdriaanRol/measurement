# An example 2D scanner.
#
# has a predefined 'signal' (a sinc-function, centered at r=0), that gets
# scanned line by line with a pixel time per data point (implemented as sleep).
# one can set the area and resolution (see code) and start the scan. when the
# scan is finished, the instrument stops.
# after a line has finished, get_last_line_index, which returns the first index
# of the 2D data array where the new data has been stored, is called, so
# listening clients get notified that data is available and can react (i.e., get
# the new data).

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import gobject
import types
import time
import math
import numpy
import qt

class ADwin_scan2d(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name,
                                     tags=['measure', 'generate', 'virtual'])

        # add the relevant parameters for a 2D PL scanner
        self.add_parameter('pixel_time', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='ms',
                           minval=1, maxval=1000,
                           doc="""
                           Integration time per image pixel.
                           """)

        self.add_parameter('xstart',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0.0, maxval=50.0,
                           units='um')

        self.add_parameter('xstop',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0.0, maxval=50.0,
                           units='um')

        self.add_parameter('ystart',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0.0, maxval=50.0,
                           units='um')

        self.add_parameter('ystop',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0.0, maxval=50.0,
                           units='um')

        self.add_parameter('xsteps',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=2, maxval=1000,
                           units='')

        self.add_parameter('ysteps',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=2, maxval=1000,
                           units='')

        self.add_parameter('data',
                           tags=['measure'],
                           type=types.ObjectType,
                           flags=Instrument.FLAG_GET,
                           units='cps',
                           doc="""
                           Returns the full data array, not a single value.
                           The dimensions are given by the scan settings.
                           """)

        self.add_parameter('x',
                           type=types.ObjectType,
                           flags=Instrument.FLAG_GET,
                           units='um',
                           doc="""
                           Returns the x coordinates of the data pixels.
                           """)
        
        self.add_parameter('y',
                           type=types.ObjectType,
                           flags=Instrument.FLAG_GET,
                           units='um',
                           doc="""
                           Returns the y coordinates of the data pixels.
                           """)

        self.add_parameter('last_line_index',
                           type=types.ObjectType,
                           flags=Instrument.FLAG_GET,
                           units='',
                           doc="""
                           Returns the index of the last line of which data is
                           available.
                           """)

        self.add_parameter('last_line',
                           tags=['measure'],
                           type=types.ObjectType,
                           flags=Instrument.FLAG_GET,
                           units='cps',
                           doc="""
                           Returns the last line of the measured data.
                           """)
        
        # relevant functions to be visible outside
        # a method that gives only a specified range of lines back
        # (minimize data exchange)
        self.add_function('get_line')
        self.add_function('get_lines')

        # method to set up the data field: after setting the scan area, use this
        # to create a data field of appropriate size
        self.add_function('setup_data')

        # default params
        self.set_pixel_time(10)
        self.set_xstart(0.0)
        self.set_xstop(10.0)
        self.set_ystart(0.0)
        self.set_ystop(10.0)
        self.set_xsteps(101)
        self.set_ysteps(101)
        self.set_sampling_interval(500)
  
        # more set up
        self.setup_data()
        self._current_line = 0
        self._last_line = 0

        # instruments and access functions for the panels
        import qt
        self._ins_linescan = qt.instruments['ADwin_linescan']
        self._ins_pos = qt.instruments['ADwin_pos']
        self._ins_count = qt.instruments['ADwin_count']

        self.add_function('move_abs_xy')

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': True,
            }

        self._busy = False
        self._counter = False

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

    def do_get_data(self):
        return self._data

    def do_get_last_line(self):
        return self._data[self.get_last_line_index(),:]

    def do_get_x(self):
        return self._x

    def do_get_y(self):
        return self._y

    def do_get_last_line_index(self):
        return self._last_line

    # the publicly visible functions declared above
    def get_line(self, line):            
        return self._data[line,:]

    def get_lines(self, lines):
        return self._data[lines,:]
    
    def setup_data(self):
        self._data = numpy.zeros((self._ysteps, self._xsteps))
        self._x = numpy.r_[self._xstart:self._xstop:self._xsteps*1j]
        self._y = numpy.r_[self._ystart:self._ystop:self._ysteps*1j]

    # overloading save function
    # FIXME: doesn't use meta yet
    def save(self, meta=""):
        CyclopeanInstrument.save(self, meta)

        import qt
        qt.mstart()
        data = qt.Data(name='dummy 2D scan')
        data.add_coordinate('x [um]')
        data.add_coordinate('y [um]')
        data.add_value('counts [Hz]')
        data.create_file()
        for i in range(self._xsteps):
            for j in range(self._ysteps):
                data.add_data_point(self._x[i], self._y[j], self._data[j,i])
            data.new_block()
        data.close_file()
        qt.mend()
        
    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        self._counter = self._ins_count.get_is_running()
        self._ins_count.set_is_running(False)
        self.setup_data()
        self._current_line = 0
        self._last_line = 0

    def _stop_running(self):
        return

    # ATM, getting data is done at timer intervals (i.e., non-blocking).
    # if blocking is not an issue, this is of course not necessary
    def _sampling_event(self):
        if not self._is_running:
            return False

        if self._current_line < self._y.size:
            if self._busy == False:
                self._busy = True
                self._fetch_line()
            return True
        else:
            self.set_is_running(False)
            self._center_pos()
            if self._counter == True:
                self._ins_count.set_is_running(True)
            return False

    def _center_pos(self):
        self._ins_pos.set_X_position((self._xstart+self._xstop)/2)
        self._ins_pos.set_Y_position((self._ystart+self._ystop)/2)
        return

    # instrument access
    def move_abs_xy(self, x, y):
        self._ins_pos.set_X_position(x)
        self._ins_pos.set_Y_position(y)
        self._ins_pos.move_abs_xy()
        return
    
    # we use the linescanner instrument to get the actual data
    # like this, one can have much flexibility on how scan the area
    # TODO: not very convenient like this, add convenience methods in linescan
    def _fetch_line(self):
        y0 = self._y[self._current_line]
        x0 = self._x[0]
        self.move_abs_xy(x0,y0)
        self._ins_linescan.set_start(self._xstart)
        self._ins_linescan.set_start(self._xstop)
        self._ins_linescan.set_nr_of_points(self._xsteps)
        self._ins_linescan.set_pixel_time(self._pixel_time)
        self._ins_linescan.set_axis(1)
        #self._ins_linescan.set_angle(0)
        #self._ins_linescan.set_length(self._xstop-self._xstart)
        self._ins_linescan.set_is_running(True)
        
        self._data[self._current_line,:] = self._ins_linescan.get_values()
        self._last_line = self._current_line
        self._current_line += 1
        self.get_last_line_index()
        self._busy = False
        return True

    
