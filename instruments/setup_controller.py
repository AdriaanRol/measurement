# controller for all coordinates of the setup
# includes positioning and path options (beam splitters, ...)
# basically everything controlled via use of other instruments

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import logging

from measurement.wp_setup import state,control

class setup_controller(CyclopeanInstrument):
    def __init__(self, name, use={}):
        CyclopeanInstrument.__init__(self, name, tags=[], use=use)
        
        self._supported = {
            'get_running': False,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self.add_parameter('keyword',
                           type = types.StringType,
                           flags=Instrument.FLAG_GETSET,
                           units='' )

        self.add_function('set_control_variable')
        self.add_function('get_control_variable')

    def do_get_keyword(self):
        return state.info['keyword']


    def do_set_keyword(self, val):
        state.info['keyword'] = val


    def set_control_variable(self, var_name, val):
        l = logging.getLogger('experiment')
        try:
            setattr(control, var_name, val)
            l.info('set control variable %s to %s' % (var_name, val))
        except:
            l.error('could not get control variable %s' % var_name)
            return

    def get_control_variable(self, var_name):
        try:
            return getattr(control, var_name)
        except:
            l = logging.getLogger('experiment')
            l.error('could not get control variable %s' % var_name)
            return
