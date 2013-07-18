"""
This module contains the abstract class Measurement.
The goal is that other measurements are classes based on
this one. This can provide benefits, because measurements
usually have common features, like saving and plotting data,
which then do not have to be written explicitly if implemented
in a common parent class.

Furthermore, measurements can be based on other measurements,
e.g. by just introducing another outer parameter sweep, which can
also be facilitated by an OO approach like this one.
"""

### imports
import sys,os,time,shutil,inspect
import logging
import msvcrt
import gobject
import pprint

import numpy as np

import qt
import hdf5_data as h5
from lib.misc import dict_to_ordered_tuples

from .. import AWG_HW_sequencer_v2
Sequence = AWG_HW_sequencer_v2.Sequence

# FIXME type checking of max/min vals?
# FIXME how to check after updating type,max/minval?
#       idea: split up verification and then after setting one of
#       those vars, only repeat that verification
class MeasurementParameter(object):
    """
    This class implements a measurement parameter, i.e., some value that
    determines or characterizes the behavior of a measurement.
    This is somewhat inspired by the QTlab instrument parameters.

    Features (all optional, early stage of development!):
    - check for type
    - check for bounds
    """

    def __init__(self, key, value, description='', type=None, 
            maxval=None, minval=None):
        
        self.key = key
        self.description = description
        self.type = type
        self.maxval = maxval
        self.minval = minval
        self.value = self.verify(value)
        
    def __call__(self):
        return self.value

    def __repr__(self):
        ret = 'MeasurementParameter %s' % self.key
        if self.description != '':
            ret += r" ('" + self.description + r"')"
        ret += ": " + str(self.value)

        return ret

    def set(self, value):
        self.value = self.verify(value)

    def verify(self, value):
        '''
        Check whether the value of the parameter is allowed.
        Type is cast automatically, if possible.
        '''
        if value == None:
            return True
        
        if self.type == None:
            pass
        else:
            try:
                value = self.type(value)
                
            except ValueError:
                logging.error('Wrong type for parameter %s: %s required, not %s' \
                        % (self.key, str(self.type), str(type(value))))
                return None

        if self.maxval == None:
            pass
        else:
            try:
                if value > self.maxval:
                    logging.error('Value of parameter %s exceeds maximum: %s > %s' \
                            % (self.key, str(value), str(self.maxval)))
                    return None
            
            except ValueError:
                logging.warning('Type of parameter %s cannot be compared' \
                        % (self.key))
                return value
                
        if self.minval == None:
            pass

        else:
            try:
                if value < self.minval:
                    logging.error('Value of parameter %s smaller than minimum: %s < %s' \
                            % (self.key, str(value), str(self.minval)))
                    return None
            
            except ValueError:
                logging.warning('Type of parameter %s cannot be compared' \
                        % (self.key))
                return value

        return value

class MeasurementParameters(object):
    '''
    A container for measurement parameters. Usage is similar as if it where
    just a dictionary, but with some benefits.
    '''

    def __init__(self, name='Params'):
        self.name = name
        self.parameters = {}

    def __getitem__(self, key):
        return self.parameters[key]()

    def __setitem__(self, key, value):
        if self.parameters.has_key(key):
            self.parameters[key].set(value)
        else:
            self.parameters[key] = MeasurementParameter(key, value)

    def __repr__(self):
        fmt = "{:<25}"*3

        ret = fmt.format('Key', 'Description', 'Value') + '\n'
        ret += ('='*78 + '\n')
        for pk in self.parameters:
            p = self.parameters[pk]
            ret += fmt.format(p.key, p.description, p.value) + '\n'
        
        return ret

    def new(self, key, value, *arg, **kw):
        self.parameters[key] = MeasurementParameter(key, value, *arg, **kw)
        
    def add(self, param):
        self.parameters[param.key] = param

    def from_dict(self, param_dict, add_new=True):
        """
        Set many parameters at once from a dictionary. Assumes that the
        dictionary has the form {name : value, }.
        This method leaves parameters that are not contained in 
        param_dict unaffected. If a parameter is already existing, its
        value will be overwritten. If not, it will be created without any
        options (type, max/min, etc) if add_new is True, or ignored if add_new
        is False.
        """
        for k in param_dict:
            if k in self.parameters:
                self.parameters[k].set(param_dict[k])
            else:
                if add_new:
                    self.new(k, param_dict[k])
        
        return True

    def to_dict(self):
        param_dict = {}
        for k in self.parameters:
            param_dict[k] = self.parameters[k]()

        return param_dict
            

# TODO see how that goes with all the hdf5 elements as members
# maybe better to use them only locally in functions; also this might result
# in data loss; try maybe to close/re-open all the time.
class Measurement(object):
    """
    Implements some common tasks such as data creation, so they need not be 
    implemented explicitly by all measurements
    """
    
    mprefix = 'Measurement'
    
    STACK_DIR = 'stack'
    FILES_DIR = 'files'
    CFG_DIR = 'files/cfg'

    keystroke_monitor_interval = 1000 # [ms]

    def __init__(self, name, save=True):
        self.name = name
        self.params = MeasurementParameters()
        
        if save:
            self.dataset_idx = 0
            self.h5data = h5.HDF5Data(name=self.mprefix+'_'+self.name)
            self.h5datapath = self.h5data.filepath()
            self.h5base = '/'+self.name+'/'
            self.h5basegroup = self.h5data.create_group(self.name)
            self.datafolder = self.h5data.folder()
        
        self.keystroke_monitors = {}
        self.params['measurement_type'] = self.mprefix

        # self.h5data.flush()

    def save_stack(self, depth=2):
        '''
        save stack files, i.e. exectuted scripts, classes and so forth,
        into the subfolder specified by STACK_DIR.
        the depth specifies how many files are saved:
        - 1 is only the executing script,
        - 2 adds the module that it imports that contains the measurement
          class,
        - 3 the module that is imported by the module in step 2 (the more
          basic class), and so forth.
        the desired value of depth depends therefore on the way the code is
        organized and how much is supposed to be saved.
        '''
        sdir = os.path.join(self.datafolder, self.STACK_DIR)
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
        
        # pprint.pprint(inspect.stack())
        
        for i in range(depth):
            # print inspect.stack()[i][1]
            shutil.copy(inspect.stack()[i][1], sdir)

    def add_file(self, filepath):
        '''
        save a file along the data. will be put into FILES_DIR
        '''
        fdir = os.path.join(self.datafolder, self.FILES_DIR)
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        
        shutil.copy(filepath, fdir+'/')

    def save_params(self, grp=None):
        '''
        adds all measurement params contained in self.params as attributes
        to the basis data group of the hdf5 data object or any other
        specified object.
        '''
        if grp == None:
            grp = self.h5basegroup

        params = self.params.to_dict()
        for k in params:
            grp.attrs[k] = params[k]
        
        self.h5data.flush()

    def save_cfg_files(self):
        try:
            cfgman = qt.cfgman
        except:
            print logging.warning('Could not find ConfigManager qt.cfgman')
            return
        
        fdir = fdir = os.path.join(self.datafolder, self.CFG_DIR)
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        
        for k in cfgman.keys():
            fp = cfgman[k]._filename
            shutil.copy(fp, fdir)

    def save_instrument_settings_file(self, parent=None):
        if parent == None:
            parent = self.h5basegroup
        
        h5settingsgroup = parent.create_group('instrument_settings')
        inslist = dict_to_ordered_tuples(qt.instruments.get_instruments())
        
        for (iname, ins) in inslist:
            insgroup = h5settingsgroup.create_group(iname)
            parlist = dict_to_ordered_tuples(ins.get_parameters())
            
            for (param, popts) in parlist:
                try:
                    insgroup.attrs[param] = ins.get(param, query=True) \
                            if 'remote' in ins.get_options()['tags'] \
                            else ins.get(param, query=False)
                except (ValueError, TypeError):
                        insgroup.attrs[param] = str(ins.get(param, query=False))
                
    def review_params(self):
        ''' 
        prints a summary of all measurement params and asks for confirmation.
        if confirmed, returns True, otherwise False
        '''
        print 
        print 'Measurement Parameters:'
        print '-'*78
        print self.params

        happy = None
        while happy == None:
            happy = raw_input('Happy with these settings? (y/n) ')
            if happy not in ['y','Y','n','N']:
                happy = None
                print 'Try again...'

        if happy in ['y','Y']:
            return True
        else:
            return False
    
    def finish(self):
        '''
        closes the hd5 data object
        '''
        self.h5data.close()

    # TODO - have monitors react only to certain keys
    def start_keystroke_monitor(self, name, timer=True):
        self.keystroke_monitors[name] = {}
        self.keystroke_monitors[name]['key'] = ''
        self.keystroke_monitors[name]['running'] = True
        if timer:
            self.keystroke_monitors[name]['timer_id'] = \
                    gobject.timeout_add(self.keystroke_monitor_interval,
                            self._keystroke_check, name)

    def _keystroke_check(self, name):
        if not self.keystroke_monitors[name]['running']:
            return False
        
        if msvcrt.kbhit():
            c = msvcrt.getch()
            self.keystroke_monitors[name]['key'] = c

        return True

    def keystroke(self, name):
        return self.keystroke_monitors[name]['key']

    def stop_keystroke_monitor(self, name):
        self.keystroke_monitors[name]['running'] = False
        qt.msleep(2*self.keystroke_monitor_interval/1e3)
        del self.keystroke_monitors[name]


class AdwinControlledMeasurement(Measurement):
    
    mprefix = 'AdwinMeasurement'
    adwin_process = ''

    def __init__(self, name, save=True):
        Measurement.__init__(self, name, save=save)

        self.adwin_process_params = MeasurementParameters('AdwinParameters')

    def start_adwin_process(self, load=True, stop_processes=[]):
        proc = getattr(self.adwin, 'start_'+self.adwin_process)
        proc(load=load, stop_processes=stop_processes,
                **self.adwin_process_params.to_dict())

    def stop_adwin_process(self):
        func = getattr(self.adwin, 'stop_'+self.adwin_process)
        return func()

    def save_adwin_data(self, name, variables):
        grp = h5.DataGroup(name, self.h5data, 
                base=self.h5base)
        
        for v in variables:
            name = v if type(v) == str else v[0]
            data = self.adwin_var(v)
            if data != None:
                grp.add(name,data=data)

        # save all parameters in each group (could change per run!)
        self.save_params(grp=grp.group)  

        # then save all specific adwin params, overwriting other params
        # if double
        adwinparams = self.adwin_process_params.to_dict()
        for k in adwinparams:
            grp.group.attrs[k] = adwinparams[k]

        self.h5data.flush()

    def adwin_process_running(self):
        func = getattr(self.adwin, 'is_'+self.adwin_process+'_running')
        return func()

    def adwin_var(self, var):
        v = var
        getfunc = getattr(self.adwin, 'get_'+self.adwin_process+'_var')
        
        if type(v) == str:
                return getfunc(v)
        elif type(v) == tuple:
            if len(v) == 2:
                return getfunc(v[0], length=v[1])
            elif len(v) == 3:
                return getfunc(v[0], start=v[1], length=v[2])
            else:
                logging.warning('Cannot interpret variable tuple, ignore: %s' % \
                        str(v))
        else:
            logging.warning('Cannot interpret variable, ignore: %s' % \
                    str(v))
        return None

    def adwin_process_filepath(self):
        return self.adwin.process_path(self.adwin_process)

    def adwin_process_src_filepath(self):
        binpath = self.adwin_process_filepath()
        srcpath = os.path.splitext(binpath)[0] + '.bas'
        if not os.path.exists(srcpath):
            return None
        else:
            return srcpath

    def save_stack(self, depth=3):
        Measurement.save_stack(self, depth=depth)

        sdir = os.path.join(self.datafolder, self.STACK_DIR)
        adsrc = self.adwin_process_src_filepath()
        if adsrc != None:
            shutil.copy(adsrc, sdir)


class SequencerMeasurement(Measurement):
    
    mprefix = 'SequencerMeasurement'

    def __init__(self, name, awg):
        Measurement.__init__(self, name)

        self.awg = awg
        self.seq = Sequence(name)



    

