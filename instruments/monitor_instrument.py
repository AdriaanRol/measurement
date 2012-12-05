import os
import types
import gobject
import time
import qt
from instrument import Instrument
from lib import config

class MonitorInstrument(Instrument):
    '''This is a simple monitoring insturment that uses a 
    gobject timeout to trigger an update method. Child classes can
    overide the _update() method to monitor something and process the data.'''
	
    
    def __init__(self, name, **kw):
        Instrument.__init__(self, name)


	
        self.add_parameter('save_data',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('send_email',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)
				
        self.add_parameter('is_running',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)
    
        self.add_parameter('read_interval',
                type=types.FloatType,
                unit='min',
                flags=Instrument.FLAG_GETSET)

        self.add_function('start')
        self.add_function('stop')
        self.add_function('manual_update')
        self.add_function('save_cfg')
        
        self.set_is_running(False)
        self.set_save_data(True)
        self.set_send_email(True)
        self.set_read_interval(10) #min
        
        # override from config       
        cfg_fn = os.path.abspath(
                os.path.join(qt.config['ins_cfg_path'], name+'.cfg'))
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._parlist = ['save_data', 'send_email', 'read_interval']
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()

		#our list of monitor variables in the form (name,get_value_func,formatting_str)
		#_monitor_list = ('demo_monitor',_demo_get_value_func,'.0f')
	
    def get_all(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
            if p in self._parlist:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self._parlist:
            value = self.get(param)
            self.ins_cfg[param] = value
    
    
    ### set & get methods
	
    def do_get_is_running(self):
        return self._is_running

    def do_set_is_running(self, val):
        self._is_running = val
    
    def do_get_save_data(self):
        return self._save_data

    def do_set_save_data(self, val):
        self._save_data = val
		    
    def do_get_send_email(self):
        return self._send_email

    def do_set_send_email(self, val):
        self._send_email = val

    def do_get_read_interval(self):
        return self._read_interval

    def do_set_read_interval(self, val):
        self._read_interval = val
    ### end set/get

    ### public methods
    def start(self):
        self._t0 = time.time()
        self.set_is_running(True)
        self._timer=gobject.timeout_add(int(self._read_interval*60*1e3), self._update) #set update timing in ms
        self._update()

    def stop(self):
        self.set_is_running(False)

    def manual_update(self):
        self._update()

    def _update(self):
		#override this method in child classes.
        if not self._is_running:
            print 'Instrument not running, start first' 
            return False
		
        return True
				
#		#retrieve list of monitor values in the form (value_flt, exceeds_minmax_bool, warning_msg_str) 	
#		data_str=''
#		warning=False
#		warning_msg=''
#		for monitor in _monitor_list:
#			monitor_value = monitor[0]()
#			data_str=data_str + monitor_value[1]
		#etc
#        return True

        


    
    ### end public methods


    ### private methods    
    
    ### end private methods

