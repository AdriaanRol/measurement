from instrument import Instrument
from numpy import *
import time
import matplotlib.pyplot as plt
import ConfigParser
import qt
import types

class ServoMotor(Instrument):

    def __init__(self, name):
        Instrument.__init__(self, name)

        self.add_parameter('channel', 
                           type=types.IntType,
                           flags = Instrument.FLAG_GETSET,
                           minval=0,maxval=15)
        
        self.add_parameter('position', 
                           type = types.StringType, 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('speed',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0,maxval=63)
        
        config = ConfigParser.SafeConfigParser()
        config.read(qt.config['setup_cfg'])
        try:
            self._channel = config.get('Servo', name+'_channel')
        except ConfigParser.NoSectionError:
            config.add_section('Servo')
            config.set('Servo',name+'_channel','0')
            config.set('Servo',name+'_positions',"{'in': 810, 'out': 700}")
            config.set('Servo',name+'_speed','20')
            config.set('Servo',name+'_position','out')
            with open(qt.config['setup_cfg'], 'wb') as configfile:
                config.write(configfile)
        except ConfigParser.NoOptionError:
            config.set('Servo',name+'_channel','0')
            config.set('Servo',name+'_positions','{\'in\': 810, \'out\': 700}')
            config.set('Servo',name+'_speed','20')
            config.set('Servo',name+'_position','out')
            with open(qt.config['setup_cfg'], 'wb') as configfile:
                config.write(configfile)

        self._channel = config.getint('Servo', name+'_channel')
        self._positions = eval(config.get('Servo', name+'_positions'))
        self._speed = config.getint('Servo', name+'_speed')
        self._position = config.get('Servo', name+'_position')

    def save_cfg(self):
        config = ConfigParser.SafeConfigParser()
        config.read(qt.config['setup_cfg'])
        name = self._name
        config.set('Servo',name+'_channel',str(self._channel))
        config.set('Servo',name+'_positions',str(self._positions))
        config.set('Servo',name+'_speed',str(self._speed))
        with open(qt.config['setup_cfg'], 'wb') as configfile:
            config.write(configfile)

    def do_set_speed(self,val):
        self._speed = val
        self.save_cfg()

    def do_get_speed(self):
        return self._speed

    def do_set_channel(self,val):
        self._channel = val
        self.save_cfg()

    def do_get_channel(self):
        return self._channel

    def do_set_position(self, val):
        self._position = val
        if val not in self._positions:
            print('Error: invalid %s servo position %s'%(self._name,val))
            return

        pos = self._positions[val]
        if (pos >= 500) & (pos <= 2500):
            qt.instruments['Servo'].set_position(self._channel,self._speed,pos)
            qt.instruments['Servo'].set_default_position(self._channel,pos)
            self.save_cfg()
        else:
            print('Error: invalid %s servo position %s'%(self._name,pos))

    def do_get_position(self):
        return self._position

    def move(self, val):
        self.set_position(val)

    def define_position(self, name, position):
        pos = {name: position}
        self._positions.update(pos)
        self.save_cfg()

    def delete_position(self, name):
        if name in self._positions:
            del self._positions[name]
            self.save_cfg()
        else:
            print('Unable to delete position %s: position not defined.'%name)

