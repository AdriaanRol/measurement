from instrument import Instrument
import serial
import types
import logging
import re
import math

class ParallaxServoController(Instrument):

    def __init__(self, name, address, reset=False):
        Instrument.__init__(self, name)

        self._address = address
        self._ser = serial.Serial(address,2400,timeout = 1)

    def set_position(self,channel,speed,position):
        highbyte = position/256
        lowbyte  = position-highbyte*256
        self._ser.write('!SC'+chr(channel)+chr(speed)+chr(lowbyte)+chr(highbyte)+'\r')

    def get_position(self,channel):
        self._ser.write('!SCRSP'+chr(channel)+'\r')
        answer = self._ser.read(3)
        return ord(answer[2])+ord(answer[1])*256

    def disable(self,channel):
        self._ser.write('!SCPSD'+chr(channel)+'\r')

    def enable(self,channel):
        self._ser.write('!SCPSE'+chr(channel)+'\r')

    def set_startup_mode(self,mode):
        self._ser.write('!SCEDD'+chr(mode)+'\r')
        return self._ser.read(3)

    def set_default_position(self,channel,position):
        highbyte = position/256
        lowbyte  = position-highbyte*256
        self._ser.write('!SCD'+chr(channel)+chr(lowbyte)+chr(highbyte)+'\r')

    def get_version(self):
        self._ser.write('!SCVER?\r')
        return float(self._ser.read(3))

    def clear_EEPROM(self):
        self._ser.write('!SCLEAR'+'\r')
        return self._ser.read(3)

        
