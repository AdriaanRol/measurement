from instrument import Instrument
import types
import qt
import gobject
import pprint
import time

class adwin_monit0r(Instrument):

    def __init__(self, name, physical_adwin=''):
        Instrument.__init__(self, name)
        self.name = name
        self._adwin = qt.instruments[physical_adwin]
        
        self._monitor_pars = {}
        self._monitor_fpars = {}
        self._t0 = 0

        self.add_parameter('is_running',
            type=types.BooleanType,
            flags=Instrument.FLAG_GETSET)

        self.add_parameter('update_interval',
            type=types.FloatType,
            unit='s',
            flags=Instrument.FLAG_GETSET)

        self.add_function('start')
        self.add_function('stop')
        self.add_function('add_par')
        self.add_function('add_fpar')
        self.add_function('remove_par')
        self.add_function('remove_fpar')
        self.add_function('show_monitors')

        self.set_is_running(False)
        self.set_update_interval(0.5)

    def do_get_is_running(self):
        return self._is_running

    def do_set_is_running(self, val):
        self._is_running = val

    def do_get_update_interval(self):
        return self._update_interval

    def do_set_update_interval(self, val):
        self._update_interval = val

    def start(self):
        if not self._is_running:
            self._t0 = time.time()
            
            for p in self._monitor_pars:
                n = self._monitor_pars[p]['name']

                self._monitor_pars[p]['data'] = qt.Data(
                    name='{}_Par{}_{}'.format(self.name, p, n))
                self._monitor_pars[p]['data'].add_coordinate('time')
                self._monitor_pars[p]['data'].add_value('value')

                self._monitor_pars[p]['plot'] = qt.Plot2D(
                    self._monitor_pars[p]['data'], 
                    name='Par{}_{}'.format(p, n), coorddim=0, 
                    valdim=1, maxpoints=100, clear=True)

            for fp in self._monitor_fpars:
                n = self._monitor_fpars[fp]['name']

                self._monitor_fpars[fp]['data'] = qt.Data(
                    name='{}_FPar{}_{}'.format(self.name, fp, n))
                self._monitor_fpars[fp]['data'].add_coordinate('time')
                self._monitor_fpars[fp]['data'].add_value('value')

                self._monitor_fpars[fp]['plot'] = qt.Plot2D(
                    self._monitor_fpars[fp]['data'], 
                    name='FPar{}_{}'.format(fp, n), coorddim=0, 
                    valdim=1, maxpoints=100, clear=True)

            self._is_running = True
            gobject.timeout_add(int(self._update_interval*1e3), self._update)

    def stop(self):
        self._is_running = False

    def show_monitors(self):
        print 'Par:'
        print '----'
        pprint.pprint(self._monitor_pars)
        print
        print 'FPar:'
        print '-----'
        pprint.pprint(self._monitor_fpars)

    def add_par(self, number, name = ''):
        self._monitor_pars[number] = {}
        self._monitor_pars[number]['name'] = name        

    def add_fpar(self, number, name = ''):
        self._monitor_fpars[number] = {}
        self._monitor_fpars[number]['name'] = name

    def remove_par(self, number):
        del self._monitor_pars[number]

    def remove_fpar(self, number):
        del self._monitor_fpars[number]

    def _update(self):
        if not self._is_running:
            return False

        t = time.time() - self._t0

        for p in self._monitor_pars:
            try:
                self._monitor_pars[p]['data'].add_data_point(t, 
                    self._adwin.Get_Par(p))
            except:
                print "Could not get Par {}, will stop now.".format(p)
                return False

        for fp in self._monitor_fpars:
            try:
                self._monitor_fpars[fp]['data'].add_data_point(t, 
                    self._adwin.Get_FPar(fp))
            except:
                print "Could not get FPar {}, will stop now.".format(fp)
                return False

        return True







