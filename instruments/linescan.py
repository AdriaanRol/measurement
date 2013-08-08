# line scanner that controls position and obtains counts via the adwin
#
# Author: Wolfgang Pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import qt
from qt import msleep
import types
import time
from numpy import *

class linescan(CyclopeanInstrument):
    def __init__(self, name, adwin, mos, *arg, **kw):
        """
        Parameters:
            adwin : string
                qtlab-name of the adwin instrument to be used
            mos : string
                qtlab-name of the master of space to be used
        """
        CyclopeanInstrument.__init__(self, name, tags=['measure'])

        # adwin and positioner
        self._adwin = qt.instruments[adwin]
        self._mos = qt.instruments[mos]
        self._scan_value = 'counts'

        # connect the mos to monitor methods
        self._mos.connect('changed', self._mos_changed)

        # params that define the linescan
        self.add_parameter('dimensions', 
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET,
                doc="""Sets the names of the dimensions involved, as specified
                in the master of space""")

        self.add_parameter('starts',
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('stops',
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET)
 
        self.add_parameter('steps',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('px_time',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET,
                units='ms')

        self.add_parameter('scan_value',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET)

        self.add_function('get_points')

        self._points = ()
        # self._values = {1: [], 2: []}
        self.set_steps(1)
        self.set_px_time(1)
        self.set_dimensions(())
        self.set_starts(())
        self.set_stops(())
        self.set_scan_value('counts')

        # other vars
        self._px_clock = 0

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

    def do_get_dimensions(self):
        return self._dimensions

    def do_set_dimensions(self, val):
        self._dimensions = val

    def do_get_starts(self):
        return self._starts

    def do_set_starts(self, val):
        self._starts = val

    def do_get_stops(self):
        return self._stops

    def do_set_stops(self, val):
        self._stops = val

    def do_get_steps(self):
        return self._steps

    def do_set_steps(self, val):
        self._steps = val

    def do_get_px_time(self):
        return self._px_time

    def do_set_px_time(self, val):
        self._px_time = val

    def do_get_scan_value(self):
        return self._scan_value

    def do_set_scan_value(self, val):
        self._scan_value = val

    # public functions
    def get_points(self):
        return self._points

    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)

        # determine points of the line
        self._points = zeros((len(self._dimensions), self._steps))

        for i,d in enumerate(self._dimensions):

	    self._points[i,:] = linspace(self._starts[i], self._stops[i],self._steps)


        # start the linescan
        if not self._mos.linescan_start(self._dimensions, self._starts, 
                self._stops, self._steps, self._px_time, 
                value=self._scan_value):
            self.set_is_running(False)
   
    def _sampling_event(self):
        if self.get_is_running():
            return True
        else:
            return False
    
    def _mos_changed(self, unused, changes, *arg, **kw):
        for c in changes:
            if c == 'linescan_px_clock':
                self._px_clock_set(changes[c])

            if c == 'linescan_running':
                self._linescan_running_changed(changes[c])

    def _px_clock_set(self, px_clock):
        if self._px_clock >= px_clock:
            return
        else:
            self._px_clock = px_clock
            self._px_clock_changed(px_clock)

    def _linescan_running_changed(self, running):
        if not running:
            self._linescan_finished()
            self.set_is_running(False)

    # inherit in child classes for real functionality
    def _px_clock_changed(self, px_clock):
        pass

    def _linescan_finished(self):
        pass

        
