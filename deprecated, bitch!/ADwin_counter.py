# a dummy counter instrument
#
# has a default count rate of 1e5/s. depending on the set integration time,
# can provide counts and countrate, including some noise.
# New data is generated at every sampling event. This means the instrument can
# be run (from the console, or elsewhere) without being blocking. This principle
# can be used generally to achieve 'fake multithreading', i.e. many instruments
# can be operated simultaneously.

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import time
import math
from numpy import random

class ADwin_counter(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=['measure', 'generate', 'virtual'])

        # relevant parameters
        self.add_parameter('integration_time',
                           type=types.IntType,
                           flags=Instrument.FLAG_SET | Instrument.FLAG_SOFTGET,
                           units='ms',
                           minval=1, maxval=10000,
                           doc="""
                           How long to count to determine the rate.
                           """)

        self.add_parameter('channel',
                           type=types.IntType,
                           flags=Instrument.FLAG_SET | Instrument.FLAG_SOFTGET,
                           units='',
                           minval=1, maxval=5,
                           doc="""
                           ADwin counter channel (1 - 4) or ADwiun counter 1 + counter 2 (channel 5)
                           """)

        self.add_parameter('counts',
                           type=types.IntType,
                           flags=Instrument.FLAG_GET,
                           units='counts',
                           tags=['measure'],
                           doc="""
                           Returns the counts acquired during the last counting period.
                           """)

        self.add_parameter('countrate',
                           type=types.IntType,
                           flags=Instrument.FLAG_GET,
                           units='Hz',
                           tags=['measure'],
                           doc="""
                           Returns the count rate based on the current count value.
                           """)

        # init parameters
        self.set_channel(5)
        self._counts = 0
        self._countrate = 0

        # instruments we need to access
        import qt
#        self._ins_pos = qt.instruments['dummy_pos']
        self._ins_ADwin = qt.instruments['ADwin']

        self.set_integration_time(20.0)

        self._supported = {
            'get_running': True,
            'get_recording': True,
            'set_running': True,
            'set_recording': False,
            'save': False,
            }
            

    def do_set_integration_time(self, val):
        self._integration_time = val
        if self._is_running:
            self._start_running()
        else:
            self._ins_ADwin.Set_Par(24,self._integration_time)

    def do_set_channel(self, val):
        self._channel = val

    def do_get_integration_time(self):
        return self._integration_time

    def do_get_channel(self):
        return self._channel

    def do_get_counts(self):
        return self._counts

    def do_get_countrate(self):
        return self._countrate

    def _stop_running(self):
        CyclopeanInstrument._stop_running(self)
        self._counts = 0
        self._countrate = 0
        self._ins_ADwin.Stop_Process(4)

    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        self._ins_ADwin.Stop_Process(4)
        self._ins_ADwin.Load('D:\\measuring\\user\\ADwin Codes\\simple_counting.tb4')
        self._ins_ADwin.Set_Par(24,self._integration_time)
        time.sleep(0.001)
        self._ins_ADwin.Start_Process(4)
        
    # if this function returns False, the sampling timer gets stopped.
    # it gets re-started once set_is_running(True) gets called again.
    def _sampling_event(self):
        if not self._is_running:
            return False
        
        self._read_counts()
        return True
        
    def _read_counts(self):
        
        if self._channel < 5:
            self._counts = self._ins_ADwin.Get_Par(40+self._channel)
        elif self._channel == 5:
            self._counts = self._ins_ADwin.Get_Par(41) + self._ins_ADwin.Get_Par(42)
        else:
            self._counts = -1

        self._countrate = self._counts
      
