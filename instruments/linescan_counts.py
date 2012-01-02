# line scanner that controls position and obtains counts via the adwin
#
# Author: Wolfgang Pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from linescan import linescan
import qt
from numpy import *

class linescan_counts(linescan):
    def __init__(self, name):
        linescan.__init__(self, name)
        
        self._data['counts'] = array([])
        self._data['countrates'] = array([])
        
        self._counters = qt.instruments['counters']
        self._counter_was_running = False
       
    def _start_running(self):
	linescan._start_running(self)
        # make sure the counter is off.
        if self._counters.get_is_running():
            self._counter_was_running = True
            self._counters.set_is_running(False)

    def _stop_running(self):
        linescan._stop_running(self)

        if self._counter_was_running:
            self._counters.set_is_running(True)
            self._counter_was_running = False
    

    def _linescan_finished(self):
        linescan._linescan_finished(self)
        self._data['counts'] = \
                array(self._adwin.get_linescan_counts(self._steps))
        self._data_update = ('counts', [slice(self._steps)])

	self.get_data_update()



        self._data['countrates'] = \
                self._data['counts'] / (1e-3*self._px_time)

        self._data_update = ('countrates', [slice(self._steps)])
        self.get_data_update()

        if self._counter_was_running:
            self._counters.set_is_running(True)
            self._counter_was_running = False

        
