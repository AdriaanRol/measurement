from instrument import Instrument
import types
import qt
import gobject
import pprint

class broadcast0r(Instrument):
    
    def __init__(self, name):
        Instrument.__init__(self, name)
        self.name = name
        
        self._broadcasts = {}
        
        self.add_parameter('is_running',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)
                
        self.add_parameter('broadcast_interval',
                type=types.FloatType,
                unit='s',
                flags=Instrument.FLAG_GETSET)
                
        self.add_function('start')
        self.add_function('stop')
        self.add_function('add_broadcast')
        self.add_function('remove_broadcast')
        self.add_function('show_broadcasts')
                
        self.set_is_running(False)
        self.set_broadcast_interval(0.2)
    
    def do_get_is_running(self):
        return self._is_running

    def do_set_is_running(self, val):
        self._is_running = val
        
    def do_get_broadcast_interval(self):
        return self._broadcast_interval

    def do_set_broadcast_interval(self, val):
        self._broadcast_interval = val
        
    def start(self):
        if not self._is_running:
            self._is_running = True
            gobject.timeout_add(int(self._broadcast_interval*1e3), self._broadcast)
        
    def stop(self):
        self._is_running = False
        
    
    # broadcast management
    def show_broadcasts(self):
        pprint.pprint(self._broadcasts)
    
    def add_broadcast(self, name, getfunc, setfunc, conditionfunc = None):
        self._broadcasts[name] = {}
        self._broadcasts[name]['getfunc'] = getfunc
        self._broadcasts[name]['setfunc'] = setfunc
        self._broadcasts[name]['conditionfunc'] = conditionfunc
        
    def remove_broadcast(self, name):
        del self._broadcasts[name]
        
    def _broadcast(self):
        if not self._is_running:
            return False
            
        for b in self._broadcasts:
            try:
                value = self._broadcasts[b]['getfunc']()
                if self._broadcasts[b]['conditionfunc'] == None or self._broadcasts[b]['conditionfunc'](value):
                    self._broadcasts[b]['setfunc'](value)
            except:
                print 'Cannot execute broadcast', b, ', will stop now.'
                return False
            
        return True
            
    
        
        
    