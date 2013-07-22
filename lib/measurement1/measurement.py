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
import pickle

import numpy as np
import matplotlib.pyplot as plt

import qt
from tools import data_handling as dh

# TODO 
# - hdf5 data saving
# - ascii data saving

PARAMS_FNAME = 'parameters'
SUPPL_DIRNAME = 'supplements'

class Measurement:
    """
    Implements common tasks such as data saving, so they need not be implemented
    explicitly by all measurements

    Usage notes:

    adding instances of measurement devices to the list measurement_devices
    will result in:
        during saving of datasets, the get_save_data method of each device
        is called, and the resulting data is saved automatically.

    """

    name = ''
    save_folder = ''
    # save_basepath = ''

    def __init__(self, name, mclass='Measurement'):
        
        # TODO: option to load measurements

        self.name = name # name to identify the measurement (meta information)
        
        self.mclass = mclass # short token to identify the kind of 
                             # measurement

        self.save_filebase = self.mclass # the prefix for all saved
                                         # data
        _bp = dh.dummy_qtlab_measurement(self.mclass+'_'+self.name)
        self.save_folder, _tmp = os.path.split(_bp)
        self.dataset_idx = 0

        self.measurement_devices = []
    
    def add_measurement_element(self, element_instance):
        """
        After creating a measurement element object and adapting it to the 
        specific needs, it can be added to the measurement object via this
        method.
        """
        return element_instance.make()

    
    def measure(self):
        pass
    
    
    def analyze(self):
        pass

    
    def save(self):
        pass


    def save_dataset(self, name='', folder=None, data={}, formats=['npz'], do_plot=True,
            files=[], txt={}, idx_increment=True, script_save_stack_depth=2,
            index_pad=3):
        """
        Automatic data saving for measurements. On what is actually plotted,
        and how, see the tools.data_handling module.

        Arguments (all optional):

            folder (None) : path
                where to save the data. if not given, we use the previousely set
                folder; if not has been set yet, a new one with the usal naming
                scheme is created.

            data ( {} ) : dict
                expects data in the form { 'array_name' : narray, }
                will be saved in one npz data

            formats ( [ 'npz', ] ) : list of format identifiers
                only 'npz' supported at the moment
                
            do_plot ( True ) : bool
                whether to autoplot the saved data. see the data_handling
                docs for details, we only pass this on to the format-resp.
                save-method there

            files ( [] ) : list of file paths
                files in this list are copied to the save folder

            txt ( {} ) : dict of text comments
                any entry in the form { 'filename' : 'content', }
                will be saved as txt file in the save folder
        """

        if folder != None:
            if not os.path.isdir(folder):
                try:
                    os.makedirs(folder)
                    self.save_folder = os.path.abspath(folder)
                except:
                    print 'invalid save directory! will autodetermine one.'
            else:
                self.save_folder = os.path.abspath(folder)
        
        if self.save_folder == '':
            _bp = dh.dummy_qtlab_measurement(self.mclass+'_'+self.name)
            self.save_folder, _tmp = os.path.split(_bp)

        
        # this is the basepath for the files we're about to save
        self.basepath = os.path.join( self.save_folder, 
                (self.save_filebase+'-%.'+str(index_pad)+'d') % \
                        self.dataset_idx )

        # we'd like to have the option to save several datasets from one
        # measurement run, where they share the same statistics, parameters,
        # and meta information, and just the data is distributed over several
        # files
        if name != '':
            self.data_basepath = self.basepath + '_%s' % name    
        else:
            self.data_basepath = self.basepath        
        
        if 'npz' in formats:
            dh.save_npz_data(self.data_basepath, filepath=self.save_folder, 
                    do_plot=do_plot, **data)
        else:
            print 'no supported save formats given, data not saved.'

        for txtfile in txt:
            t = open(self.basepath + '_%s.txt' % txtfile, 'w')
            t.write(txt[txtfile])
            t.close()

        # to keep our folders clean, save extra data in a supplementaries
        # folder; we usually assume this is only one set per measurement
        # (and thus folder)
        supplfolder = os.path.join(self.save_folder, (SUPPL_DIRNAME+'-%.'+ \
                str(index_pad)+'d') % (self.dataset_idx))
        if not len(files) > 0 and os.path.isdir(supplfolder):
            try:
                os.makedirs(supplfolder)
            except:
                print 'could not create separate folder for supplementals!'
                supplfolder = self.save_folder

        # auto copy script files to suppl folderdel pc
        #
        for i in range(script_save_stack_depth):
            shutil.copy(inspect.stack()[i][1], self.save_folder)

        # copy the given files to the folder
        for f in files:
            shutil.copy(f, supplfolder+'/')

        # save params in a table ; we take all variables of types
        # int, float, numpy.ndarray, str
        params = [ p for p in self.__dict__ if type(getattr(self, p)) in \
                [ int, float, str, np.ndarray ] ]
       
        params_dict = {}
        for p in params:
            params_dict[p] = getattr(self, p)
        params_pickle = open(self.basepath+'_%s.pkl' % PARAMS_FNAME, 'wb')
        pickle.dump(params_dict, params_pickle)
        params_pickle.close()

        # save parameter dictionaries
        dicts = [ d for d in self.__dict__ if type(getattr(self, d)) == dict ]
        for d in dicts:
            dic=getattr(self,d)
            if dic.has_key('saveme'):
                if dic['saveme']:
                    dictpickle = open(self.basepath+'_%s.pkl' % d, 'wb')
                    pickle.dump(getattr(self,d), dictpickle)
                    dictpickle.close()
  
        
        # save data from measurement devices
        for i,device in enumerate(self.measurement_devices):
            devicefolder = os.path.join(self.save_folder, (device.name+\
                    '-%.'+str(index_pad)+'d') % (self.dataset_idx))
            try:
                os.makedirs(devicefolder)
            except:
                print 'could not create data folder for instrument %s' % \
                        device.name
                devicefolder = self.save_folder

            savdat = device.get_save_data()
            for data_set in savdat:
                np.savez(os.path.join(devicefolder, data_set), 
                        **savdat[data_set])
        
        
        if idx_increment:
            self.dataset_idx += 1
        return


class MeasurementElement:

    def __init__(self, parent):
        """
        Constructor.
        Requires the parent measurement class instance as first argument.
        All other args depend on the specific implementation.
        Any members of the measurement class that are to be modified in the
        element (sequences, etc.) should be passed as keyword here.
        """
        self.parent = parent

    def make(self):
        """
        This function generates the element, and should be executed by
        the add_measurement_element function of the measurement.
        Does nothing in the prototype implementation.
        """
        pass


class MeasurementDevice:
    """
    Basis class for measurement devices (anything that aquires data).
    Need to implement specifically for each device.
    """

    def __init__(self, name): 
        """
        Constructor.
        """
        self.name = name


    def get_save_data(self):
        """
        needs to be implemented.
        """
        pass


class AdwinMeasurementDevice(MeasurementDevice):
    """
    A logical adwin used in the measurement class.

    Usage:
    after init, specify process parameters in a dictionary as
        {'process_name', **params, },
    and place as AdwinMeasurementDevice.process_params.
    these will be saved automatically by the measurement class.

    if you populate the list AdwinMeasurementDevice.processes with process
    names, you can start all processes at the same time using start_all().

    all data elements (names known to adwin configuration) added to 
    process_data as
        {'process_name', *dataelements, }
    will be saved automatically.

    single processes are started by start_process(name).

    process names are as defined in the adwin configuration.

    """
    
    def __init__(self, adwin_instrument, name='adwin'):
        MeasurementDevice.__init__(self, name)

        self.adwin = adwin_instrument
        self.processes = []
        self.process_params = {}
        self.process_data = {}

    def start_all(self):
        for p in self.processes:
            self.start_process(p)

    def start_process(self, name):
        """
        starts the adwin process via the logical adwin instrument.
        all arguments are passed to the start method of the instrument,
        and should therefore be initialization parameters.
        """
        getattr(self.adwin, 'start_'+name)(**self.process_params[name])

    def get_save_data(self):
        """
        return save data of all specified processes.
        """
        savdat = {}
        
        for p in self.process_params:
            n = p+'_params'
            savdat[n] = self.process_params[p]
            
        for p in self.process_data:
            n = p+'_data'
            savdat[n] = {}
            for d in self.process_data[p]:
                savdat[n][d] = getattr(self.adwin, 'get_'+p+'_var')(d)

        return savdat


def main():
    m = Measurement('test')
    params = [p for p in m.__dict__ if p[:4] == 'par_']
    for p in params:
        print getattr(m, p)


if __name__ == "__main__":
    main()
