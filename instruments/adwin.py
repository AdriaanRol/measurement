# Virtual adwin instrument, adapted from rt2 to fit lt2, dec 2011 
import os
import types
import qt
import numpy as np
from instrument import Instrument
import time
from lib import config

class adwin(Instrument):
    def __init__(self, name, adwin, processes={}, **kw):
        Instrument.__init__(self, name, tags=['virtual'])

        self.physical_adwin = adwin
        self.process_dir = qt.config['adwin_programs']
        self.processes = processes
        self.default_processes = kw.get('default_processes', [])
        self.dacs = kw.get('dacs', {})

        self._dac_voltages = {}
        for d in self.dacs:
            self._dac_voltages[d] = 0.
       
        if kw.get('init', False):
            self._load_programs()

        # the accessible functions
        # initialization
        self.add_function('boot')
        self.add_function('load_programs')

        # tools
        self.add_function('get_process_status')

        # automatically generate process functions
        self._make_process_tools(self.processes)

        # convenience functions that belong to processes
        self.add_function('set_dac_voltage')
        self.add_function('get_dac_voltage')
        self.add_function('get_dac_channels')

        self.add_function('get_countrates')
        self.add_function('set_simple_counting')

        # set up config file
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self.ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()

    ### config management
    def load_cfg(self, set_voltages=False):
        params = self.ins_cfg.get_all()
        if 'dac_voltages' in params:
            for d in params['dac_voltages']:
                if set_voltages:
                    self.set_dac_voltage((d, params['dac_voltages'][d]))
                else:
                    self._dac_voltages[d] = params['dac_voltages'][d]

    def save_cfg(self):
        self.ins_cfg['dac_voltages'] = self._dac_voltages

    ### end config management
    def boot(self):
        self.physical_adwin.Boot()
        self.load_programs()  
        
        if 'init_data' in self.processes:
            self.start_init_data(load=True)
    
    # automatic creation of process management/access tools from the 
    # process dictionary
    def _make_process_tools(self, proc):
        for p in proc:
            self._make_load(p, proc[p]['file'], proc[p]['index'])
            self._make_start(p, proc[p]['index'], proc[p])
            self._make_stop(p, proc[p]['index'])
            self._make_is_running(p, proc[p]['index'])
            self._make_get(p, proc[p])
            self._make_set(p, proc[p])

    def _make_load(self, pn, fn, pidx):
        funcname = 'load_' + pn
        while hasattr(self, funcname):
            funcname += '_'
        
        def f():
            """
            this function is generated automatically by the logical
            adwin driver.
            """

            if self.physical_adwin.Process_Status(pidx):
                self.physical_adwin.Stop_Process(pidx)
            self.physical_adwin.Load(os.path.join(self.process_dir, fn))
            return True
        
        f.__name__ = funcname
        setattr(self, funcname, f)
        self.add_function(funcname)

        return True

    def _make_start(self, pn, pidx, proc):
        funcname = 'start_' + pn
        while hasattr(self, funcname):
            funcname += '_'

        def f(timeout=None, stop=True, load=False, 
                stop_processes=[], **kw):

            """
            this function is generated automatically by the logical
            adwin driver.
            

            kw args:
            - load : load the process first (default: False)
            - stop_processes : list of processes (numbers or names) that
              are stopped before starting this one.

            all other kws are interpreted as parameters for the process (as defined
            in the process dictionary).
            PAR and FPAR parmeters (old style) have no default at the moment, 
            DATA param (new style) defaults are specified in the process 
            dictionary.
            """

            for p in stop_processes:
                if type(p) == str:
                    if p in self.processes:
                        try:
                            getattr(self, 'stop_'+p)()
                        except:
                            print 'cannot stop process %s' % p
                    else:
                        'unknown process %s' % p
                elif type(p) == int:
                    try:
                        self.physical_adwin.Stop_Process(p)
                    except:
                        print 'cannot stop process %s' % p
                else:
                    print 'cannot figure out what process %s is' % p


            if self.physical_adwin.Process_Status(pidx):
                self.physical_adwin.Stop_Process(pidx)
            if load:
                getattr(self, 'load_'+pn)()
            
            if timeout != None:
                _t0 = time.time()
                while self.physical_adwin.Process_Status(pidx):
                    if time.time() > _t0+timeout:
                        print 'Timeout while starting ADwin process %d (%s)' \
                                % (pidx, pn)
                        return False
                    time.sleep(.001)

            if 'params_long' in proc:
                pls = np.zeros(len(proc['params_long']), dtype=int)
                for i,pl in enumerate(proc['params_long']):
                    pls[i] = kw.pop(pl[0], pl[1])
                self.physical_adwin.Set_Data_Long(pls, 
                        proc['params_long_index'], 1, 
                       len(proc['params_long']))

            if 'params_float' in proc:
                pfs = np.zeros(len(proc['params_float']), dtype=float)
                for i,pf in enumerate(proc['params_float']):
                    pfs[i] = kw.pop(pf[0], pf[1])
                self.physical_adwin.Set_Data_Float(pfs, 
                        proc['params_float_index'], 1, 
                        len(proc['params_float']))

            setfunc = getattr(self, pn+'_setfunc_name')
            getattr(self, setfunc)(**kw)

            self.physical_adwin.Start_Process(pidx)
            return True

        f.__name__ = funcname
        setattr(self, funcname, f)
        self.add_function(funcname)

        return True

    def _make_stop(self, pn, pidx):
        funcname = 'stop_' + pn
        while hasattr(self, funcname):
            funcname += '_'

        def f():
            """
            this function is generated automatically by the logical
            adwin driver.
            """
            if self.physical_adwin.Process_Status(pidx):
                self.physical_adwin.Stop_Process(pidx)
            else:
                print 'Process not running.'
            return True

        f.__name__ = funcname
        setattr(self, funcname, f)
        self.add_function(funcname)
        
        return True
    
    def _make_is_running(self, pn, pidx):
        funcname = 'is_' + pn + '_running'
        while hasattr(self, funcname):
            funcname += '_'

        def f():
            """
            this function is generated automatically by the logical
            adwin driver.
            """
            return bool(self.physical_adwin.Process_Status(pidx))

        f.__name__ = funcname
        setattr(self, funcname, f)
        self.add_function(funcname)


    def _make_get(self, pn, proc):
        funcname = 'get_' + pn + '_var'
        while hasattr(self, funcname):
            funcname += '_'

        def f(name, *arg, **kw):
            """
            this function is generated automatically by the logical
            adwin driver.

            returns a value belonging to an adwin process, which can be either
            a PAR, FPAR or DATA element. What is returned is specified by
            the name of the variable.

            known keywords:
            - start (integer): if DATA is returned, the start index of the
              array. default is 1.
            - length (integer): if DATA is returned, the length of the array
              needs to be specified. default is 1.
            """
            
            start = kw.get('start', 1)
            length = kw.get('length', 1)
            
            if not 'par' in proc:
                proc['par'] = {}
            if not 'fpar' in proc:
                proc['fpar'] = {}
            if not 'data_long' in proc:
                proc['data_long'] = {}
            if not 'data_float' in proc:
                proc['data_float'] = {}

            if name in proc['par']:
                if type(proc['par'][name]) in [list, tuple]:
                    return [ self.physical_adwin.Get_Par(i) for i in \
                            proc['par'][name] ]
                else:
                    return self.physical_adwin.Get_Par(proc['par'][name])
            elif name in proc['fpar']:
                if type(proc['fpar'][name]) in [list, tuple]:
                    return [ self.physical_adwin.Get_FPar(i) for i in \
                            proc['fpar'][name] ]
                else:
                    return self.physical_adwin.Get_FPar(proc['fpar'][name])
            elif name in proc['data_long']:
                if type(proc['data_long'][name]) in [list, tuple]:
                    return [ self.physical_adwin.Get_Data_Long(
                        i, start, length) for i in proc['data_long'][name] ]
                else:
                    return self.physical_adwin.Get_Data_Long(
                            proc['data_long'][name], start, length)
            elif name in proc['data_float']:
                if type(proc['data_float'][name]) in [list, tuple]:
                    return [ self.physical_adwin.Get_Data_Float(
                        i, start, length) for i in proc['data_float'][name] ]
                else:
                    return self.physical_adwin.Get_Data_Float(
                            proc['data_float'][name], start, length)
            else:
                print 'Unknown variable.'
                return False

        f.__name__ = funcname
        setattr(self, funcname, f)
        self.add_function(funcname)

        return True

    def _make_set(self, pn, proc):
        funcname = 'set_' + pn + '_var'
        while hasattr(self, funcname):
            funcname += '_'
        setattr(self, pn + '_setfunc_name', funcname)
        
        def f(**kw):
            """
            this function is generated automatically by the logical
            adwin driver.

            sets all given PARs and FPARs, specified as kw-args by their names
            as defined in the process dictionary.

            """
            
            if not 'par' in proc:
                proc['par'] = {}
            if not 'fpar' in proc:
                proc['fpar'] = {}

            for var in kw:
                if var in proc['par']:
                    self.physical_adwin.Set_Par(proc['par'][var], kw[var])
                elif var in proc['fpar']:
                    self.physical_adwin.Set_FPar(proc['fpar'][var], kw[var])
                else:
                    print 'Parameter %s is not defined.' % var
        
        f.__name__ = funcname
        setattr(self, funcname, f)
        self.add_function(funcname)

        return True
    
    
    def stop_process(self,process_nr):
        self.physical_adwin.Stop_Process(process_nr)

    def get_process_status(self, name):
        return self.physical_adwin.Process_Status(
                self.processes[name]['index'])

    def wait_for_process(self, name):
        while bool(self.get_process_status(name)):
            time.sleep(0.005)
        return

    def load_programs(self):
        for p in self.processes.keys():
            if p in self.default_processes:
                self.physical_adwin.Load(
                        os.path.join(self.process_dir, 
                            self.processes[p]['file']))

    ###
    ### Additional functions, for convenience, etc.
    ### FIXME ultimately, most of these functions should not be used and go out;
    ### the automatically generated functions should suffice, plus usage of
    ### of scripts
    
    # dacs
    def get_dac_channels(self):
        return self.dacs.copy()

    def set_dac_voltage(self, (name, value), timeout=1, **kw):
        if 'set_dac' in self.processes:
            self.start_set_dac(dac_no=self.dacs[name], 
                    dac_voltage=value, timeout=timeout, **kw)

            self._dac_voltages[name] = value
            self.save_cfg()
            return True
        else:
            print 'Process for setting DAC voltage not configured.'
            return False

    def get_dac_voltage(self, name):
        return self._dac_voltages[name]
    
    def get_dac_voltages(self, names):
        return [ self.get_dac_voltage(n) for n in names ] 
   
   
    # counter
    def set_simple_counting(self, int_time=1, avg_periods=100,
            single_run=0, **kw):
        
        if not 'counter' in self.processes:
            print 'Process for counting not configured.'
            return False

        self.start_counter(load=True, stop=True,
                set_integration_time=int_time, 
                set_avg_periods=avg_periods,
                set_single_run=single_run)

    def get_countrates(self):
        if not 'counter' in self.processes:
            print 'Process for counting not configured.'
            return False

        if self.is_counter_running():
            return self.get_counter_var('get_countrates')
            
    
    def get_last_counts(self):
        if not 'counter' in self.processes:
            print 'Process for counting not configured.'
            return False

        return self.get_counter_var('get_last_counts', start=1, length=4)        

