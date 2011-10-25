# A dummy linescanner. Returns function values (in this case of a dummy-function)
# that are lying in the XY plane. The positions for the return values are
# specified via a start point in the plane, an angle (0=positive x,
# 90=positive y, and so on), a length, and the nr of points (start and end point
# included). Also, a pixel time can be specified (implemented as sleep)
#
# Author: Wolfgang Pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import time
import numpy
import qt

class ADwin_linescanner(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=['measure', 'virtual'])

        self.add_parameter('start',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um')

#        self.add_parameter('angle',
#                           type=types.FloatType,
#                           flags=Instrument.FLAG_GETSET,
#                           units='')

        self.add_parameter('stop',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='um')

        self.add_parameter('nr_of_points',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='')

#        self.add_parameter('points',
#                           type=types.ListType,
#                           flags=Instrument.FLAG_GET,
#                           units='um',
#                           channels=('X', 'Y'))

        self.add_parameter('pixel_time',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='ms')

        self.add_parameter('values',
                           type=types.ListType,
                           flags=Instrument.FLAG_GET,
                           units='')

        self.add_parameter('axis',
                           type=types.IntType,
                           flags=Instrument.FLAG_SET | Instrument.FLAG_SOFTGET,
                           units='',
                           minval=1, maxval=2,
                           doc="""
                           Scan axis for linescan (1 is x, 2 is y)
                           """)


#        self._points = ( [0., 0.5, 1.], [0., 0., 0.] )
        self._values = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]
#        self._start = (0., 0.)
        self._axis = 1

#        self.set_angle(0)

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self._ins_ADwin = qt.instruments['ADwin']
        self._ins_ADwin_pos = qt.instruments['ADwin_pos']
        self._ins_ADwin_count = qt.instruments['ADwin_count']
        self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\simple_linescan.tb2')

        self.set_start(0)
        self.set_stop(1)
        self.set_axis(1)
        self.set_nr_of_points(10)
        self.set_pixel_time(10)

    def do_get_start(self):
        return self._start

    def do_set_start(self, val):
        if self._axis == 1:
            V = self._ins_ADwin_pos.pos_to_U_x(val)
        else:
            V = self._ins_ADwin_pos.pos_to_U_y(val)
        self._ins_ADwin.Set_FPar(20, V)
        self._start = val

    def do_get_stop(self):
        return self._stop

    def do_set_stop(self, val):
        if self._axis == 1:
            V = self._ins_ADwin_pos.pos_to_U_x(val)
        else:
            V = self._ins_ADwin_pos.pos_to_U_y(val)
        self._ins_ADwin.Set_FPar(21, V)
        self._stop = val

    def do_get_axis(self):
        return self._axis

    def do_set_axis(self, val):
        self._ins_ADwin.Set_Par(25, val)
        self._axis = val

#    def do_get_angle(self):
#        return self._angle

#    def do_set_angle(self, val):
#        self._angle = val

    def do_get_nr_of_points(self):
        return self._nr_of_points

    def do_set_nr_of_points(self, val):
        self._ins_ADwin.Set_Par(20, val)
        self._nr_of_points = val

    def do_get_pixel_time(self):
        return self._pixel_time

    def do_set_pixel_time(self, val):
        self._ins_ADwin.Set_Par(24, val)
        self._pixel_time = val

    def do_get_points(self):
        return self._points

    def do_get_values(self):
        return self._values


    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        # determine points of the line in x/y space
        self._ins_ADwin.Start_Process(2)
        while self._ins_ADwin.Process_Status(2) > 0:
#            qt.msleep(0.1)
            time.sleep(0.01)

        channel = self._ins_ADwin_count.get_channel()

        if channel < 5:
            self._values = self._ins_ADwin.Get_Data_Long(channel,1,self._nr_of_points)
        elif channel == 5:
            self._values = numpy.add(self._ins_ADwin.Get_Data_Long(1,1,self._nr_of_points), self._ins_ADwin.Get_Data_Long(2,1,self._nr_of_points))

        self.get_values()

        self.do_set_is_running(False)

