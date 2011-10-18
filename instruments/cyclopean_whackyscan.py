# cyclopean_whackyscan.py
#
# auto-created by ../ui2cyclops.py v20110215, Thu Aug 04 23:36:00 2011

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import time, datetime

import qt
from numpy import *

import threading


class PxMeasurement(threading.Thread):
    
    a = 0

    def run(self):

        ins = qt.instruments['whackyscan']
        ctr = qt.instruments['counters_demo']
        ctr.set_is_running(True)
            
        d = qt.Data(name='test_measurement')
        d.add_coordinate('time')
        d.add_value('a')
        p = qt.plot(d)
        d.create_file()
        qt.mstart()

        t0 = time.time()

        for i in range(10):
            qt.msleep(0.5)
            self.a = ctr.get_cntr1_countrate() * ins.get_pxtime()
            if not ins.get_is_running():
                print 'aborted'
                break

            d.add_data_point(time.time()-t0, self.a)
        
        qt.mend()
        d.close_file()
        
        now = datetime.datetime.now()
        print 'thread done at', now


class cyclopean_whackyscan(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=[])

        self._supported = {
            'get_running': True,
            'get_recording': True,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self.add_parameter('current_z',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           doc='')
        self._current_z = 0

        self.add_parameter('cube_size',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=1.000000000000000,
                           maxval=99.0,
                           doc='')
        self._cube_size = 4.000000000000000

        self.add_parameter('pxperdim',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=3,
                           maxval=99,
                           doc='')
        self._pxperdim = 3

        self.add_parameter('pxtime',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=1,
                           maxval=99,
                           doc='')
        self._pxtime = 1

        self.add_function('go')

        self.add_function('stop')

        
        # user content
        ### internal variables
        self._busy = False

        ### more setup
        self._prepare_data()


    def do_get_current_z(self):
        return self._current_z

    def do_set_current_z(self, val):
        self._current_z = val

    def do_get_cube_size(self):
        return self._cube_size

    def do_set_cube_size(self, val):
        self._cube_size = val

    def do_get_pxperdim(self):
        return self._pxperdim

    def do_set_pxperdim(self, val):
        self._pxperdim = val

    def do_get_pxtime(self):
        return self._pxtime

    def do_set_pxtime(self, val):
        self._pxtime = val

    def go(self, *arg, **kw):
        self.set_is_running(True)

        if hasattr(self, 'm'):
            if self.m.is_alive():
                print 'measurement already running'
                return
        
        self.m = PxMeasurement()
        self.m.start()

        return 42

    def stop(self, *arg, **kw):
        self.set_is_running(False)

    def save(self, meta=""): # inherited doesn't do any saving. Implement.
        CyclopeanInstrument.save(self, meta)

        return

    def _start_running(self):
        self._prepare_data()

        # prepare the sampling which is responsible for doing the work
        # we can only (safely) communicate with the GUI during the sampling
        # event calls; try to handle each pixel, take into account some
        # overhead
        #self.i, self.j, self.k = 0, 0, 0
        #self.set_sampling_interval(self._pxtime/1e3 + 0.005)
        
        CyclopeanInstrument._start_running(self)
        # self._acquire_data()
        return

    def _stop_running(self):
        CyclopeanInstrument._stop_running(self)

        return

    def _sampling_event(self):
        """
        This function only checks the status of the data acquisition.
        """

        # catches stop button pressed
        if not self._is_running: 
            return False

        if hasattr(self, 'm'):
            if not self.m.is_alive():
                print 'sampling detected the measurement is finished'
                self.set_is_running(False)
                return False
        
        return True

    def _prepare_data(self):
        shape = (self._pxperdim, self._pxperdim, self._pxperdim)
        # self.reset_data('cubescan', shape)
        self._data['cubescan'] = zeros(shape)
        
        for dim in 'x', 'y', 'z':
            #self.set_data(dim, linspace(-self._cube_size/2.0, self._cube_size/2.0,
            #    self._pxperdim))
            self._data[dim] = linspace(-self._cube_size/2., self._cube_size/2.,
                    self._pxperdim)

    def _acquire_data(self):

        print 'run data acquisition'
        
        for i, z in enumerate(self._data['z']):
            self._current_z = i
            
            for j, y in enumerate(self._data['y']):
                for k, x in enumerate(self._data['x']):
                    print self._is_running
                    
                    if not self._is_running: 
                        return False
                    
                    v = self._data_point(x, y, z)
                    # self._data['cubescan'][i,j,k] = v
                    self.set_data('cubescan', v, [slice(i,i+1), slice(j,j+1),
                        slice(k,k+1)])

                    print x, y, z, ':', v

                    qt.msleep(self._pxtime/1e3)

                #self.set_data_update( ('cubescan', [slice(i,i+1),slice(j,j+1),
                #    slice(0, self._pxperdim)]) )

        
        self._busy = False
        self.set_is_running(False)

    def _data_point(self, x, y, z):
        return exp(-x**2-y**2-z**2)



