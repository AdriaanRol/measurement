# default 2d scanner. uses the linescan to obtain data.
#
# author: wolfgang pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
from numpy import *
import numpy
import qt

class scan(CyclopeanInstrument):
    def __init__(self, name, linescan=''):
        CyclopeanInstrument.__init__(self, name, tags=['measure'])

        self._mos = qt.instruments['master_of_space']
        self._linescan = qt.instruments[linescan]


        # add the relevant parameters for a scanner based on line scans
        self.add_parameter('linescan_dimensions',
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('linescan_px_time', 
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='ms')

        self.add_parameter('linescan_steps',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('linescan_starts',
                type=types.ListType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('linescan_stops',
                type=types.ListType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('current_line',
                type=types.TupleType,
                flags=Instrument.FLAG_GET)

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': True,
            }

        # initialize vars
        self._current_line = ()

    # get and set functions
    def do_get_linescan_dimensions(self):
        return self._linescan_dimensions

    def do_set_linescan_dimensions(self, val):
        self._linescan_dimensions = val

    def do_get_linescan_starts(self):
        return self._linescan_starts.tolist()

    def do_set_linescan_starts(self, val):
        self._linescan_starts = array(val)

    def do_get_linescan_stops(self):
        return self._linescan_stops.tolist()

    def do_set_linescan_stops(self, val):
        self._linescan_stops = array(val)

    def do_get_linescan_steps(self):
        return self._linescan_steps

    def do_set_linescan_steps(self, val):
        self._linescan_steps = val

    def do_set_linescan_px_time(self, val):
        self._linescan_px_time = val

    def do_get_linescan_px_time(self):
        return self._linescan_px_time

    def do_get_current_line(self):
        return self._current_line

        
    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)

        # initalize data field and set current status (i.e, empty)
        # general feature for scan: data for points
        #
        # create a field of correct shape; each line, in whatever form
        # specified via starts and stops gets their own points
        pts_shape = list(self._linescan_starts.shape)
        pts_shape.append(self._linescan_steps)
        pts = zeros(tuple(pts_shape))

        dim_lines = zeros(self._linescan_starts.shape)
        dim_lines_flat = dim_lines.flat
        
        # index gets incremented after the item is being read out, so we
        # start populating before the first readout and stop before the
        # last one
        ndx = dim_lines_flat.coords
        pts[ndx] = linspace(self._linescan_starts[ndx],
               self._linescan_stops[ndx], self._linescan_steps)

        # line index of course without the dimensions in which we scan
        self._current_line = ndx[:-1]

        # print self._current_line
        
        for i in dim_lines_flat:
            i = linspace(self._linescan_starts[ndx],
                self._linescan_stops[ndx], self._linescan_steps)
             
            if dim_lines_flat.index < dim_lines.size:
                ndx = dim_lines_flat.coords
                pts[ndx] = linspace(self._linescan_starts[ndx],
                       self._linescan_stops[ndx], self._linescan_steps)
        
        self._data['points'] = pts

        # set up correct data field, to be implemented by user
        self._setup_data()

        # hook up linescanner changes
        self._linescan.connect('changed', self._linescan_update)

        # now start the actual scanning
        self._next_line()

    def _sampling_event(self):
        if not self._is_running:
            return False
        
        if self._linescan.get_is_running():
            return True
        else:
            # user code
            self._line_finished()
            
            # update the current line 
            lines = zeros(self._linescan_starts.shape[:-1])
            lines_flat = lines.flat
            while lines_flat.coords != self._current_line:
                lines_flat.next()
            lines_flat.next()
            
            if lines_flat.index >= lines.size:
                self._scan_finished()
                return False
            else:
                self._current_line = lines_flat.coords
                self.get_current_line()
                self._next_line()
                return True


    def _setup_data(self):
        pass

    def _linescan_update(self, unused, changes, *arg, **kw):
        pass

    def _line_finished(self):
        pass

    def _next_line(self):
        self._linescan.set_dimensions(self._linescan_dimensions)
        self._linescan.set_starts(tuple(self._linescan_starts\
                [self._current_line]))
        self._linescan.set_stops(tuple(self._linescan_stops\
                [self._current_line]))
        self._linescan.set_px_time(self._linescan_px_time)
        self._linescan.set_steps(self._linescan_steps)
        self._linescan.set_is_running(True)
        return True

    def _scan_finished(self):
        pass

    
