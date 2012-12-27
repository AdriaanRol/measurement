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

import sys,os,time,shutil,inspect
import logging

import numpy as np

import qt
import hdf5_data as h5

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
        return self._value

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
        return self.parameters[key]

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

    def from_dict(self, param_dict):
        """
        Set many parameters at once from a dictionary. Assumes that the
        dictionary has the form {name : value, }.
        This method leaves parameters that are not contained in 
        param_dict unaffected. If a parameter is already existing, its
        value will be overwritten, if not, it will be created without any
        options (type, max/min, etc).
        """
        for k in param_dict:
            if k in self.parameters:
                self.parameters[key].set(param_dict[k])
            else:
                self.new(k, param_dict[k])
        
        return True

    def to_dict(self):
        param_dict = {}
        for k in self.parameters:
            param_dict[k] = self.parameters[k]()

        return param_dict
            

# TODO see how that goes with all the hdf5 elements as members
# maybe better to use them only locally in functions; also this might result
# in data loss; try to close/re-open all the time.
class Measurement:
    """
    Implements some common tasks such as data creation, so they need not be 
    implemented explicitly by all measurements
    """
    
    mprefix = 'Measurement'
    
    STACK_DIR = 'stack'
    FILES_DIR = 'files'

    def __init__(self, name):
        self.name = name
        self.dataset_idx = 0
        self.params = MeasurementParameters()
        self.h5data = h5.HDF5Data(name=self.mprefix+'_'+self.name)
        self.h5datapath = self.h5data.filepath()
        self.h5base = '/'+self.name
        self.h5basegroup = self.h5data.create_group(self.name)
        self.datafolder = self.h5data.folder()

    def save_stack(self, depth=2):
        sdir = os.path.join(self.h5datapath, self.STACK_DIR)
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
        
        for i in range(depth):
            shutil.copy(inspect.stack()[i][1], sdir)

    def add_file(self, filepath):
        fdir = os.path.join(self.h5datapath, self.STACK_DIR)
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        
        shutil.copy(filepath, fdir+'/')       

    def save_params(self):
        params = self.params.to_dict()
        for k in params:
            self.h5basegroup.attrs[k] = params[k]
    
    def finish(self):
        self.h5data.close()


class AdwinControlledMeasurement(Measurement):
    
    mprefix = 'AdwinMeasurement'

    def __init__(self, name, adwin):
        Measurement.__init__(self, name)

        self.adwin = adwin
        self.adwin_process = ''
        self.adwin_process_params = MeasurementParameters('AdwinParameters')
        self.adwin_process_data = []

    def start_adwin_process(self):
        proc = getattr(self.adwin, 'start_'+self.adwin_process)
        proc(**self.adwin_process_params.to_dict())

    def save_adwin_data(self):
        grp = h5.DataGroup('AdwinProcessData', self.h5data, 
                base=self.h5base)
        getfunc = getattr(self.adwin, 'get_'+self.adwin_process+'_var')
        for d in self.adwin_process_data:
            grp.add(d, data=getfunc(d))

        params = self.adwin_process_params.to_dict()
        for k in params:
            grp.attrs[k] = params[k]

