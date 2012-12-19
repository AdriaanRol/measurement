# cyclopean_counts_v2.py
#
# auto-created by ../../../cyclops/tools/ui2cyclops.py v20110215, Thu Nov 17 18:47:34 2011

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import qt

class cyclopean_counts_v2(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=[])

        self._supported = {
            'get_running': False,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self.add_parameter('t_range',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0,
                           maxval=99,
                           doc='')
        self._t_range = 0

        self.add_parameter('integration_time',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0,
                           maxval=99,
                           doc='')
        self._integration_time = 0

        self.add_parameter('countrate',
                           type=types.IntType,
                           flags=Instrument.FLAG_GET,
                           units='',
                           doc='')
        self._countrate = 0

        self.set_is_running(True)

    def do_get_t_range(self):
        return self._t_range

    def do_set_t_range(self, val):
        self._t_range = val

    def do_get_integration_time(self):
        return self._integration_time

    def do_set_integration_time(self, val):
        self._integration_time = val

    def do_get_countrate(self):
        return self._countrate

    def save(self, meta=""): # inherited doesn't do any saving. Implement.
        CyclopeanInstrument.save(self, meta)

        return

    def _start_running(self):
        CyclopeanInstrument._start_running(self)

        return

    def _stop_running(self):
        CyclopeanInstrument._start_running(self)

        return

    def _sampling_event(self):
        self._countrate = qt.instruments['counters_demo'].get_cntr1_countrate()
        self.get_countrate()
        
        return True # sampling timer runs until return value of this is False
