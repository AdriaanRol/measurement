from instrument import Instrument
import qt
import types
import os
from lib import config

class ServoMotor(Instrument):

    def __init__(self, name, servo_controller='Servo'):
        Instrument.__init__(self, name)
        self._ins_servo=qt.instruments[servo_controller]
        #print 'servo:', self._ins_servo
        self.add_parameter('channel', 
                           type=types.IntType,
                           flags = Instrument.FLAG_GETSET,
                           minval=0,maxval=15)
        
        self.add_parameter('position', 
                           type = types.IntType, 
                           flags = Instrument.FLAG_GETSET,
                           minval=500, maxval=2500)
        
        self.add_parameter('speed',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0,maxval=63)
        
        self.add_parameter('in_position', 
                           type = types.IntType, 
                           flags = Instrument.FLAG_GETSET,
                           minval=500, maxval=2500)
        
        self.add_parameter('out_position', 
                           type = types.IntType, 
                           flags = Instrument.FLAG_GETSET,
                           minval=500, maxval=2500)
        #defaults
        self.set_channel(0)
        self.set_speed(20)
        self.set_position(700)
        self.set_in_position(810)
        self.set_out_position(700)
        
        # override from config       
        cfg_fn = os.path.abspath(
                os.path.join(qt.config['ins_cfg_path'], name+'.cfg'))
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()

    def get_all(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self.get_parameter_names():
            value = self.get(param)
            self.ins_cfg[param] = value
       
    def do_set_speed(self,val):
        self._speed = val

    def do_get_speed(self):
        return self._speed

    def do_set_in_position(self,val):
        self._in_position = val

    def do_get_in_position(self):
        return self._in_position
        
    def do_set_out_position(self,val):
        self._out_position = val

    def do_get_out_position(self):
        return self._out_position             

    def do_set_channel(self,val):
        self._channel = val

    def do_get_channel(self):
        return self._channel

    def do_set_position(self, val):
        self._position = val
        succes = self._ins_servo.Set_Position(self._channel,self._speed,self._position)
        succes = succes and self._ins_servo.Set_Default_Position(self._channel,self._position)
        return succes
        
    def do_get_position(self):
        return self._position

    def move_in(self):
        return self.set_position(self._in_position)

    def move_out(self):
        return self.set_position(self._out_position)
        
        
