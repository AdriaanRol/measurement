# default 2d scanner. uses the linescan to obtain data.
#


# author: wolfgang pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
from scan import scan
import types
from numpy import *
import qt

class scan2d_counts(scan):
    def __init__(self, name, xdim='stage_x', ydim='stage_y'):
        scan.__init__(self, name, linescan='linescan_counts')

        self._linescan_dimensions = (xdim, ydim)

        # also get the counter, need to disable when linescanning
        self._counters = qt.instruments['counters']
        self._counter_was_running = False


        # add the relevant parameters for a 2D PL scanner
        self.add_parameter('pixel_time', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='ms',
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

        self.add_parameter('counter',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           )

        # parameters to access the member instruments
        self.add_parameter('position', 
                type = types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='um',
                channels = ('x', 'y'),
                channel_prefix='%s_')

        # functions
        self.add_function('get_x')
        self.add_function('get_y')
        self.add_function('set_xy')

        # default params
        self.set_pixel_time(500.0)
        self.set_xstart(1.0)
	self.set_xstop(5.0)
        self.set_ystart(1.0)
        self.set_ystop(5.0)
        self.set_xsteps(5)
        self.set_ysteps(5)
        self.set_counter(1)
        self._position = { 
                'x': getattr(self._mos, 'get_'+xdim)(),
                'y': getattr(self._mos, 'get_'+ydim)(), 
                }

        self._x = linspace(-10,10,11)
        self._y = linspace(-10,10,11)

        # connect instruments
        def _mos_changed(unused, changes, *arg, **kw):
            if xdim in changes:
                self.set_x_position(changes[xdim])
            if ydim in changes:
                self.set_y_position(changes[ydim])
        self._mos.connect('changed', _mos_changed)
  
    # get and set functions
    def do_set_pixel_time(self, val):
        self.set_linescan_px_time(val)

    def do_get_pixel_time(self):
        return self.get_linescan_px_time()

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

    def do_set_counter(self, val):
        self._counter = val

    def do_get_counter(self):
        return self._counter

    # get and set for instruments
    def do_get_position(self, channel):
        return self._position[channel]

    def do_set_position(self, val, channel):
        self._position[channel] = val
        fname = 'set_'+self._linescan_dimensions[0] if channel == 'x' \
                else 'set_'+self._linescan_dimensions[1]
        getattr(self._mos, fname)(val)

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def set_xy(self, x, y):
        self.set_x_position(x)
        self.set_y_position(y)
       
    # overloading save function
    def save(self, meta=""):
        CyclopeanInstrument.save(self, meta)
	

        from wp_toolbox.qtlab_data import save
        save(self.get_name(), meta, x__x__um=self._x, y__y__um=self._y, 
        z__counts__Hz=self._data['countrates'])


	# internal functions
    def _start_running(self):

        # make sure the counter is off.
        if self._counters.get_is_running():
            self._counter_was_running = True
            self._counters.set_is_running(False)

        # first prepare params such that the underlying scan instruments
        # can understand
        self._y = linspace(self._ystart, self._ystop, self._ysteps)
        self._x = linspace(self._xstart, self._xstop, self._xsteps)
        self._linescan_starts = []
        self._linescan_stops = []
        for i, yval in enumerate(self._y):
            self._linescan_starts.append([self._xstart, yval])
            self._linescan_stops.append([self._xstop, yval])
        self._linescan_starts = array(self._linescan_starts)
        self._linescan_stops = array(self._linescan_stops)
        self._linescan_steps = self._xsteps

        # now start inherited stuff
        scan._start_running(self)

    def _stop_running(self):
        if self._counter_was_running:
            self._counters.set_is_running(True)
            self._counter_was_running = False
        self.save()

    def _setup_data(self):
        self.reset_data('countrates', (self._ysteps, self._xsteps))

    def _line_finished(self):

        # get the data from the linescanner
        self.set_data('countrates', 
                self._linescan.get_data('countrates')[self._counter-1],
                [ slice(self._current_line[0], self._current_line[0]+1),
                    slice(self._xsteps) ] )


    def _scan_finished(self):
        if self._counter_was_running:
            self._counters.set_is_running(True)
            self._counter_was_running = False

	self.save()


