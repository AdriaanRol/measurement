from instrument import Instrument
import qt
import visa
import types
import logging
import re
import math

class remote_pm(Instrument):

    def __init__(self, name, use_adwin=qt.instruments['physical_adwin_lt1'],
            address=30):
        Instrument.__init__(self, name)

        self._address = address
        self._ins_adwin = use_adwin

        self.add_parameter('power',
            flags=Instrument.FLAG_GET,
            type=types.FloatType,
            units='W')

        self.add_parameter('wavelength',
            flags=Instrument.FLAG_SET,
            type=types.FloatType,
            units='nm')

    def do_get_power(self):
        ans = self._ins_adwin.Get_FPar(self._address)
        return float(ans)

    def do_set_wavelength(self, wavelength):
        return
        #self._ins_adwin.Set_FPar(self._address+1, wavelength)


