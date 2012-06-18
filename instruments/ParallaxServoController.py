from instrument import Instrument
import serial

class ParallaxServoController(Instrument):

    def __init__(self, name, address, reset=False):
        Instrument.__init__(self, name)

        self._address = address
        self._ser = serial.Serial(address,2400,timeout = 1)
        self.add_function('Set_Position')
        self.add_function('Get_Position')
        self.add_function('Disable')
        self.add_function('Enable')
        self.add_function('Set_Startup_Mode')
        self.add_function('Set_Default_Position')
        self.add_function('Get_Version')
        self.add_function('Clear_EEPROM')    
        self.add_function('Reload')

    def Set_Position(self,channel,speed,position):
        highbyte = position/256
        lowbyte  = position-highbyte*256
        self._ser.write('!SC'+chr(channel)+chr(speed)+chr(lowbyte)+chr(highbyte)+'\r')

    def Get_Position(self,channel):
        self._ser.write('!SCRSP'+chr(channel)+'\r')
        answer = self._ser.read(3)
        return ord(answer[2])+ord(answer[1])*256

    def Disable(self,channel):
        self._ser.write('!SCPSD'+chr(channel)+'\r')

    def Enable(self,channel):
        self._ser.write('!SCPSE'+chr(channel)+'\r')

    def Set_Startup_Mode(self,mode):
        self._ser.write('!SCEDD'+chr(mode)+'\r')
        return self._ser.read(3)

    def Set_Default_Position(self,channel,position):
        highbyte = position/256
        lowbyte  = position-highbyte*256
        self._ser.write('!SCD'+chr(channel)+chr(lowbyte)+chr(highbyte)+'\r')

    def Get_Version(self):
        self._ser.write('!SCVER?\r')
        return float(self._ser.read(3))

    def Clear_EEPROM(self):
        self._ser.write('!SCLEAR'+'\r')
        return self._ser.read(3) 

    def Reload(self):
        self._ser.close()
        self._ser = serial.Serial(self._address,2400,timeout = 1)

