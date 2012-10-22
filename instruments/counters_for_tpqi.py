# gives back count rates as determined by the adwin

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import gobject
import qt

class counters_for_tpqi(CyclopeanInstrument):
    def __init__(self, name, adwin):
        """
        Parameters:
            adwin : string
                qtlab-name of the adwin instrument to be used
        """
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
        self._ins_adwin = qt.instruments[adwin]

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
        #self._ins_adwin.set_is_counting(True)
        gobject.timeout_add(int(self._integration_time), self._monitor_event)

    def _monitor_event(self):
        self._get_data()
        for i in self._countrate.keys():
            print i + ': ' + str(self._countrate[i]) + '\t',
        print '\n'
        return True

    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        #self._ins_adwin.start_counter()

    def _stop_running(self):
        #self._ins_adwin.stop_counter()
        self._countrate = {'cntr1': 0.0, 'cntr2': 0.0, }

    # if this function returns False, the sampling timer gets stopped.
    # it gets re-started once set_is_running(True) gets called again.
    def _sampling_event(self): 
        if not self._is_running or not self._ins_adwin.is_counter_running():
            return False
        if self._busy:
            return True

        self._busy = True
        self._get_data()
        self._busy = False
        return True
        
    def _get_data(self):
        #debug = self._ins_adwin.get_countrate()
        #cr = self._ins_adwin.get_countrates()
        self._countrate['cntr1'] = self._ins_adwin.remote_tpqi_control_get_noof_tpqi_starts()
        self._countrate['cntr2'] = self._ins_adwin.remote_tpqi_control_get_cr_below_threshold_events()
        self.get_cntr1_countrate()
        self.get_cntr2_countrate()
            
        
