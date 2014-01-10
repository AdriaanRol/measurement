# general Shutter instrument class
# assumes Shutter Driver connected to either ADwin DAC channel
# parameters are stored in the setup configuration file (defined as setup_cfg in qtlab.cfg,
# and will automatically be reloaded with qtlab start.
#
# if a new Shutter instrument is added, initial (not necessary useful) parameters will be used.
# channel configuration, maximum allowed voltages etc. should be immediately set after 
# loading new Shutter instrument for first time.

### NOTE: this class is work in progress Tim&Adriaan, 140108
### In particular this instrument does not generally know 
### what the status of the shutter is.

from instrument import Instrument
import numpy as np
from analysis.lib.fitting import fit, common
import os,sys,time
import qt
import types
from lib import config
import logging


class shutter(Instrument):

    def __init__(self, name, use_adwin='adwin'):

        Instrument.__init__(self, name)
       
        self.add_parameter('channel', 
                           type = types.IntType, 
                           flags = Instrument.FLAG_GETSET)
               
        self.add_parameter('state',
                            type = types.StringType,
                            flags = Instrument.FLAG_GETSET,
                            option_list = ('Open', 'Closed')) #Naar voorbeeld van eerder, Werkt dit? 

        self._ins_adwin=qt.instruments[use_adwin]

        # set defaults
        self._channel = 7 # THis is the channel on the second breakout box, does this corespond? 
        self._state = 'Closed'
        self.get_all()
       
        # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()

    def get_all(self): 
        for n in self.get_parameter_names():
            self.get(n)
        
    
    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            self.set(p, value=val)

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value

    def _do_set_channel(self, val):
        self._channel = val

    def _do_get_channel(self):
        return self._channel


    def _do_set_state(self, state):
        if state == open:
            self.open()
        else: 
            self.close()

    def _do_get_state(self):
        return self._state


    def change_state_label(self):
        '''
        Only use when state indicated does not correspond to actual shutter state
        ''' 
        if self._state == 'Open':
            self._state = 'Closed'
            print 'Shutter closed'
        else: 
            self._state = 'Open'
            print 'Shutter open' 

    def openclose(self):
        # applies a pulse to the shutter driver to close when open or open when closed
        self._ins_adwin.start_set_dio(dio_no=self._channel,dio_val=0)
        qt.msleep(0.001)
        self._ins_adwin.start_set_dio(dio_no=self._channel,dio_val=1)
        qt.msleep(0.001)
        self._ins_adwin.start_set_dio(dio_no=self._channel,dio_val=0)

        if self._state == 'Open':
            self._state = 'Closed'
            print 'Shutter closed'
        else:
            self._state = 'Open'
            print 'Shutter open' 

    def close(self):
        if self._state == 'Closed':
            print 'Shutter is already closed'
        else:
            self.openclose()


    def open(self):
        if self._state == 'Open':
            print 'Shutter is already open'
        else: 
            self.openclose()


