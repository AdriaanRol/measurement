# controls a single dimension of a position that is set via an
# adwin DAC voltage

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import qt
import time
import types
import gobject
import numpy as np

# constants
LINESCAN_CHECK_INTERVAL = 50 # [ms]

class master_of_space(CyclopeanInstrument):
    def __init__(self, name):
        CyclopeanInstrument.__init__(self, name, tags=['positioner'])

        import qt
        self._adwin = qt.instruments['adwin']
	
        # should not change often, hardcode is fine for now
        self.dimensions = {
                'stage_x' : {
                    'dac' : 1,
                    'micron_per_volt' : 9.324,
                    'max_v' : 4.29,
                    'min_v' : 0.,
                    'default' : 20.,
                    'origin' : 0.,
                    }, 
                'stage_y' : {
                    'dac' : 2,
                    'micron_per_volt' : 5.59,
                    'min_v' : 0.,
                    'max_v' : 4.29,
                    'default' : 12.,
                    'origin' : 0.,
                    },
                'front_z' : {
                    'dac' : 3,
                    'micron_per_volt' : 9.324,
                    'max_v' : 4.29,
                    'min_v' : 0.,
                    'default' : 20.,
                    'origin' : 0.,
                    },
                }

        # auto generate parameters incl set and get for all dimensions
        for d in self.dimensions:
            dim = self.dimensions[d]
            
            # make set and get
            self._make_get(d)
            self._make_set(d)
            
            # make stepping function
            self._make_stepfunc(d)

            # register parameter (set and get need to exist already)
            self.add_parameter(d, 
                    type=types.FloatType,
                    flags=Instrument.FLAG_GETSET, 
                    units='um',
                    minval=dim['min_v']*dim['micron_per_volt'],
                    maxval=dim['max_v']*dim['micron_per_volt'], )

            # register the step function
            self.add_function('step_'+d)

            # set default value
            getattr(self, 'set_'+d,)(dim['default'])


        # scan control
        self._linescan_running = False
        self._linescan_px_clock = 0

        self.add_parameter('linescan_running',
                type=types.BooleanType,
                flags=Instrument.FLAG_GET)
        self.add_parameter('linescan_px_clock',
                type=types.IntType,
                flags=Instrument.FLAG_GET)

        self.add_function('linescan_start')

        # managing the coordinate system
        self.add_function('set_origin')
        self.add_function('get_origin')
        self.add_function('from_relative')
        self.add_function('to_relative')
        self.add_function('set_relative_position')
        self.add_function('get_relative_position')
	self.add_function('move_xyz')

        # markers
        self._markers = {}
        self.add_function('set_marker')
        self.add_function('get_marker')
        self.add_function('get_markers')
        self.add_function('goto_marker')
        self.add_function('push_position')
        self.add_function('pop_position')


    # Line scan control
    def linescan_start(self, dimensions, starts, stops, steps, px_time, 
            relative=False, value='counts'):
        
        # for now, user has to wait until scan is finished
        if self._linescan_running or self._adwin.is_linescan_running():
            return False
        
        self._linescan_running = True

        # if we get relative coordinates, convert to absolutes first
        if relative:
            for i, dimname in enumerate(dimensions):
                starts[i] = from_relative(dimname, starts[i])
                stops[i] = from_relative(dimname, stops[i])
        
        # calculate the stepping in voltages and move to the start position
        dacs = []
        starts_v = []
        stops_v = []
        for i, dimname in enumerate(dimensions):
            dim = self.dimensions[dimname]
            dacs.append(dim['dac'])
            if self.dimensions[dimname]['min_v'] < starts[i] / dim['micron_per_volt'] < self.dimensions[dimname]['max_v']:
                starts_v.append(starts[i] / dim['micron_per_volt'])
            else:
                starts_v.append(self.dimensions[dimname]['min_v'])
                print "Error in master_of_space.linescan_start: Exceeding max/min voltage "
                print starts[i] / dim['micron_per_volt']
            if self.dimensions[dimname]['min_v'] < stops[i] / dim['micron_per_volt'] < self.dimensions[dimname]['max_v']:
                stops_v.append(stops[i] / dim['micron_per_volt'])
            else:
                stops_v.append(self.dimensions[dimname]['max_v'])
                print "Error in master_of_space.linescan_start: Exceeding max.min voltage"
                print stops[i] / dim['micron_per_volt']            
	    #getattr(self, 'set_'+dimname)(starts[i])
        # wait a bit to stabilize, then start the linescan
        time.sleep(0.05)
	print'mos calls adwin start linescan'
        self._adwin.start_linescan(np.array(dacs), np.array(starts_v), np.array(stops_v),
                steps, px_time, value=value)

        # start monitoring the status
        gobject.timeout_add(LINESCAN_CHECK_INTERVAL, self._linescan_check)

        return True

    def do_get_linescan_running(self):
        return self._linescan_running

    def do_get_linescan_px_clock(self):
        return self._linescan_px_clock

    # monitor the status of the linescan
    def _linescan_check(self):

        # first update the px clock, call get to make connects easy
        if self._adwin.get_linescan_px_clock() > self._linescan_px_clock:
            self._linescan_px_clock = self._adwin.get_linescan_px_clock()
            self.get_linescan_px_clock()

        # debug output
        # print 'px clock: ', self._linescan_px_clock

        if self._adwin.is_linescan_running():
            return True
        else:
            self._linescan_running = False
            self.get_linescan_running()
            
            # debug output
            # print 'scan finished'
            
            return False


    ### managing the coordinate system
    def set_origin(self, relative=False, **kw):
        for d in kw:
            if d in self.dimensions:
                origin = kw.pop(d)
                if origin == 'here':
                    self.dimensions[d]['origin'] = getattr(self, 'get_'+d)()
                else:
                    self.dimensions[d]['origin'] = float(origin)

    def get_origin(self, dim):
        if dim in self.dimensions:
            return self.dimensions[dim]['origin']
        else:
            return False

    def to_relative(self, dim, val):
        if dim in self.dimensions:
            return val-self.dimensions[dim]['origin']
        else:
            return False

    def from_relative(self, dim, val):
        if dim in self.dimensions:
            return val+self.dimensions[dim]['origin']
        else:
            return False

    def set_relative_position(self, dim, val):
        if dim in self.dimensions:
            return getattr(self, 'set_'+dim)(self.from_relative(dim, val))
        else:
            return False

    def get_relative_position(self, dim):
        if dim in self.dimensions:
            return self.to_relative(getattr(self, 'get_'+dim)())

    
    ### managing markers
    def set_marker(self, name, **kw):
        self._markers[name] = {} 
        for d in kw:
            if d in self.dimensions:
                pt = kw.pop(d)
                if pt == 'here':
                    self._markers[name][d] = getattr(self, 'get_'+d)()
                else:
                    self._markers[name][d] = float(pt)

    def get_markers(self):
        return self._markers

    def get_marker(self, name):
        return self._markers[name]

    def goto_marker(self, name):
        for d in self._markers[name]:
            print name
            getattr(self, 'set_'+d)(self._markers[name][d])

    def push_position(self, dims=[]):
        self._markers['push'] = {}
        for d in dims:
            if d in self.dimensions:
                self._markers['push'][d] = getattr(self, 'get_'+d)()

    def pop_position(self):
        if 'push' not in self._markers:
            print 'no position pushed, cannot pop'
            return False
        else:
            self.goto_marker('push')


    ### internals
    # creation of get and set functions, stepfunction
    def _make_get(self, dimname):
        def getfunc():
            return getattr(self, '_' + dimname)
        getfunc.__name__ = 'do_get_'+dimname
        setattr(self, 'do_get_'+dimname, getfunc)
        return

    def _make_set(self, dimname):
        def setfunc(val):
            self._set_dim(dimname, val)
            setattr(self, '_'+dimname, val)
            return
        setfunc.__name__ = 'do_set_'+dimname
        setattr(self, 'do_set_'+dimname, setfunc)
        return

    def _make_stepfunc(self, dimname):
        def stepfunc(delta):
            self._step_dim(dimname, delta)
            return
        stepfunc.__name__ = 'step_'+dimname
        setattr(self, 'step_'+dimname, stepfunc)

    # functions that do the actual work :)
    def _set_dim(self, dimname, val):
        dim = self.dimensions[dimname]
        v = val / dim['micron_per_volt']
        self._adwin.set_dac_voltage((dim['dac'], v))

    def _step_dim(self, dimname, delta):
        current = getattr(self, 'get_'+dimname)()
        getattr(self, 'set_'+dimname)(current+delta)
 
    #Convenient extra functions
    # FIXME this already exists; check where this is used and correct
    def move_xyz(self, dimname, val):
	pos=self._adwin.get_xyz_pos()
	xyz_names=['stage_x','stage_y','front_z']
	print dimname
	for i in xyz_names:
		if i in dimname:
			print xyz_names.index(i)
			print dimname.index(i)
			print val
			print pos
			pos[xyz_names.index(i)]=val[dimname.index(i)]
	self._adwin.move_abs_xyz(pos[0],pos[1],pos[2])
