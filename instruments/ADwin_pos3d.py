# A dummy 2D positioner. Stores and returns a position in x/y coordinates,
# units are microns.
# Further features: movement speed can be set, absolute and relative positions
# can be set.
#
# TODO: speed not implemented yet: can be set/get, but isn't used so far
#
# Author: Wolfgang Pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import time

class ADwin_pos3d(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=['positioner', 'virtual'])

        self.add_parameter('X_position',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um',
                           format='%.03f, %.03f')

        self.add_parameter('Y_position',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um',
                           format='%.03f, %.03f')

        self.add_parameter('Z_position',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um',
                           format='%.03f, %.03f')

        self.add_parameter('speed',
                           type=types.FloatType,
                           flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                           format='%.01f, %.01f',
                           units = 'V/s')

        self.add_parameter('LT',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval = 0, maxval = 1)



       
        self._speed = 1.0
        self._LT = 0                       # set to 1 for low temperature operation

        self._max_x_RT = 40.0              # micrometer
        self._max_y_RT = 24    		   # micrometer
        self._max_z_RT = 40.0              # micrometer
        self._cal_x_RT = 107.2             # mV/micrometer
        self._cal_y_RT = 178.9             # mV/micrometer
        self._cal_z_RT = 107.0             # mV/micrometer
        self._max_V_RT = 4.29              # Volt
        self._max_x_LT = 30.0              # micrometer
        self._max_y_LT = self._max_x_LT    # micrometer
        self._max_z_LT = 15.0              # micrometer
        self._cal_x_LT = 357.0             # mV/micrometer
        self._cal_y_LT = self._cal_x_LT    # mV/micrometer
        self._cal_z_LT = 714.3             # mV/micrometer
        self._max_V_LT = 10.0              # Volt

        self._max_speed = 1.0              # V/s

        self._supported = {
            'get_running': False,
            'get_recording': False,
            'set_running': False,            'set_recording': False,
            'save': False,
            }

	import qt
        self._ins_ADwin = qt.instruments['physical_adwin']
        self._ins_ADwin.Load('D:\\measuring\\user\\ADwin_Codes\\cursor_move.tb0')
        if self._speed <= self._max_speed:
            self._ins_ADwin.Set_FPar(29, self._speed*1000.0)
        else:
            self._ins_ADwin.Set_FPar(29, self._max_speed*1000.0)
	    
	self._X_position = self._ins_ADwin.Get_Data_Float(1,1,3)[0]/(self._cal_x_RT*1e-3)
        self._Y_position = self._ins_ADwin.Get_Data_Float(1,1,3)[1]/(self._cal_y_RT*1e-3)
        self._Z_position = self._ins_ADwin.Get_Data_Float(1,1,3)[2]/(self._cal_z_RT*1e-3)
	#self._ins_ADwin.Set_FPar(22,self._X_position)
        #self._ins_ADwin.Set_FPar(23,self._Y_position)
	#self._ins_ADwin.Set_FPar(24,self._Z_position)
	self.set_speed(1.0)

    def pos_to_U_x(self,val):
        if self._LT == 0:
            voltage = val * self._cal_x_RT / 1000.0
        else:
            voltage = val * self._cal_x_LT / 1000.0
        return voltage

    def pos_to_U_y(self,val):
        if self._LT == 0:
            voltage = val * self._cal_y_RT / 1000.0
        else:
            voltage = val * self._cal_y_LT / 1000.0
        return voltage

    def pos_to_U_z(self,val):
        if self._LT == 0:
            voltage = val * self._cal_z_RT / 1000.0
        else:
            voltage = val * self._cal_z_LT / 1000.0
        return voltage

    def U_to_pos_x(self,val):
        if self._LT == 0:
            pos = val / self._cal_x_RT * 1000.0
        else:
            pos = val / self._cal_x_LT * 1000.0
        return pos

    def U_to_pos_y(self,val):
        if self._LT == 0:
            pos = val / self._cal_y_RT * 1000.0
        else:
            pos = val / self._cal_y_LT * 1000.0
        return pos

    def U_to_pos_z(self,val):
        if self._LT == 0:
            pos = val / self._cal_z_RT * 1000.0
        else:
            pos = val / self._cal_z_LT * 1000.0
        return pos

    def do_get_X_position(self):
        V_x = self._ins_ADwin.Get_Data_Float(1,1,3)[0]
        self._X_position = self.U_to_pos_x(V_x)
        return self._X_position

    def do_get_Y_position(self):
        V_y = self._ins_ADwin.Get_Data_Float(1,1,3)[1]
        self._Y_position = self.U_to_pos_y(V_y)
        return self._Y_position

    def do_get_Z_position(self):
        V_z = self._ins_ADwin.Get_Data_Float(1,1,3)[2]
        self._Z_position = self.U_to_pos_z(V_z)
        return self._Z_position

    def do_set_X_position(self, val):
        voltage = self.pos_to_U_x(val)
        if self._LT == 0:
            if voltage <= self._max_V_RT:
                self._ins_ADwin.Set_FPar(22, voltage)
        else:
            if voltage <= self._max_V_LT:
                self._ins_ADwin.Set_FPar(22, voltage)
        self._X_position = val

    def do_set_Y_position(self, val):
        voltage = self.pos_to_U_y(val)
        if self._LT == 0:
            if voltage <= self._max_V_RT:
                self._ins_ADwin.Set_FPar(23, voltage)
        else:
            if voltage <= self._max_V_LT:
                self._ins_ADwin.Set_FPar(23, voltage)
        self._Y_position = val

    def do_set_Z_position(self, val):
        voltage = self.pos_to_U_z(val)
        if self._LT == 0:
            if voltage <= self._max_V_RT:
                self._ins_ADwin.Set_FPar(24, voltage)
        else:
            if voltage <= self._max_V_LT:
                self._ins_ADwin.Set_FPar(24, voltage)
        self._Z_position = val

    def do_get_LT(self):
        return self._LT

    def do_set_LT(self, val):
        self._LT = val

    def do_get_speed(self):
        return self._speed

    def do_set_speed(self, val):
        if val <= self._max_speed:
            self._ins_ADwin.Set_FPar(29, val*1000.0)
            self._speed = val
        else:
            self._ins_ADwin.Set_FPar(29, self._max_speed*1000.0)

    def move_abs_xy(self):
	self._ins_ADwin.Start_Process(10)

    def move_abs_xyz(self):
        self._ins_ADwin.Start_Process(10)

    def move_abs_z(self,z):
        self.set_Z_position(z)
        self._ins_ADwin.Start_Process(10)
        while (self._ins_ADwin.Process_Status(10) > 0):
            time.sleep(.01)

    def move_abs_xy(self,x,y):
        self.set_X_position(x)
        self.set_Y_position(y)
	self.set_Z_position(self._Z_position)
        self._ins_ADwin.Start_Process(10)
        while (self._ins_ADwin.Process_Status(10) > 0):
            time.sleep(.01)

    def move_abs_xyz(self,x,y,z):
        self.set_X_position(x)
        self.set_Y_position(y)
        self.set_Z_position(z)
        self._ins_ADwin.Start_Process(10)
        while (self._ins_ADwin.Process_Status(10) > 0):
            time.sleep(.01)

