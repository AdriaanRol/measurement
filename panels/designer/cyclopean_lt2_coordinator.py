# cyclopean_lt2_coordinator.py
#
# auto-created by ..\..\..\cyclops\tools\ui2cyclops.py v20110215, Fri Jan 13 13:19:35 2012

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types

class cyclopean_lt2_coordinator(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=[])

        self._supported = {
            'get_running': False,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self.add_parameter('keyword',
                           type=types.StringType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           doc='')
        self._keyword = '' 

        self.add_parameter('x',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=-100.000000000000000,
                           maxval=100.000000000000000,
                           doc='')
        self._x = 0.0

        self.add_parameter('y',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=-100.000000000000000,
                           maxval=100.000000000000000,
                           doc='')
        self._y = 0.0

        self.add_parameter('z',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0.0,
                           maxval=100.000000000000000,
                           doc='')
        self._z = 0.0

        self.add_parameter('z_slider',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0,
                           maxval=400,
                           doc='')
        self._z_slider = 500

        self.add_parameter('step',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0.0,
                           maxval=99.0,
                           doc='')
        self._step = 1.000000000000000

        self.add_function('step_up')

        self.add_function('step_left')

        self.add_function('step_right')

        self.add_function('step_down')

    def do_get_keyword(self):
        return self._keyword

    def do_set_keyword(self, val):
        self._keyword = val

    def do_get_x(self):
        return self._x

    def do_set_x(self, val):
        self._x = val

    def do_get_y(self):
        return self._y

    def do_set_y(self, val):
        self._y = val

    def do_get_z(self):
        return self._z

    def do_set_z(self, val):
        self._z = val

    def do_get_z_slider(self):
        return self._z_slider

    def do_set_z_slider(self, val):
        self._z_slider = val

    def do_get_step(self):
        return self._step

    def do_set_step(self, val):
        self._step = val

    def step_up(self, *arg, **kw):
        pass

    def step_left(self, *arg, **kw):
        pass

    def step_right(self, *arg, **kw):
        pass

    def step_down(self, *arg, **kw):
        pass

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
        return True # sampling timer runs until return value of this is False
