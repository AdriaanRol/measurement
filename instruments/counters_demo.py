# DEMO VERSION: generates some counts
# gives back count rates as determined by the adwin

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import gobject
from numpy import sqrt
from numpy.random import normal


class counters_demo(CyclopeanInstrument):
    def __init__(self, name, channel='1'):
        CyclopeanInstrument.__init__(self, name, tags=['measure'])
        
        # relevant parameters
        self.add_parameter('countrate',
                           flags=Instrument.FLAG_GET,
                           units='Hz',
                           tags=['measure'],
                           channels=('cntr1', 'cntr2'),
                           channel_prefix='%s_',
                           doc="""
                           Returns the count rates for all counters.
                           """)

        # public functions
        self.add_function("monitor_countrates")

        # init parameters
        self._countrate = {'cntr1': 0.0, 'cntr2': 0.0, }
        
        # instruments we need to access
        # import qt
        # self._ins_adwin = qt.instruments['adwin']

        # cyclopean features
        self._supported = {
            'get_running': True,
            'get_recording': True,
            'set_running': True,
            'set_recording': False,
            'save': False,
            }

        self._busy = False

    def do_get_countrate(self, channel):
        return self._countrate[channel]

    def monitor_countrates(self):
        # self._ins_adwin.set_is_counting(True)
        gobject.timeout_add(int(self._integration_time), self._monitor_event)

    def _monitor_event(self):
        self._get_data()
        for i in self._countrate.keys():
            print i + ': ' + str(self._countrate[i]) + '\t',
        print '\n'
        return True

    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        # self._ins_adwin.set_is_counting(True)

    def _stop_running(self):
        # self._ins_adwin.set_is_counting(False)
        self._countrate = {'cntr1': 0.0, 'cntr2': 0.0, }

    # if this function returns False, the sampling timer gets stopped.
    # it gets re-started once set_is_running(True) gets called again.
    def _sampling_event(self): 
        if not self._is_running:
            return False
        if self._busy:
            return True

        self._busy = True
        self._get_data()
        self._busy = False
        return True
        
    def _get_data(self):
        # cr = self._ins_adwin.get_countrate()
        mean1 = 1e5
        mean2 = 1e5
        cr = [0., int(normal(mean1, sqrt(mean1))), int(normal(mean2, sqrt(mean2))) ]
        self._countrate['cntr1'] = cr[1]
        self._countrate['cntr2'] = cr[2]
        self.get_cntr1_countrate()
        self.get_cntr2_countrate()
            
        
