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
        self.dataset_idx = 0
    
    def measure(self):
        pass
    
    
    def analyze(self):
        pass

    
    def save(self):
        pass


    def save_dataset(self, name='', folder=None, data={}, formats=['npz'], do_plot=True, 
            files=[], txt={}, idx_increment=True):
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
        
        if self.save_folder == '':
            _bp = dh.dummy_qtlab_measurement(self.mclass+'_'+self.name)
            self.save_folder, _tmp = os.path.split(_bp)

        
        # this is the basepath for the files we're about to save
        self.basepath = os.path.join(self.save_folder, 
                self.save_filebase+'-%d' % self.dataset_idx)

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
        supplfolder = os.path.join(self.save_folder, SUPPL_DIRNAME)
        if not os.path.isdir(supplfolder) and len(files) > 0:
            try:
                os.makedirs(supplfolder)
            except:
                print 'could not create separate folder for supplementals!'
                supplfolder = self.save_folder

        # copy the given files to the folder
        for f in files:
            shutil.copy(f, supplfolder)

        # save params in a table ; we take all variables that start with
        # 'par_' as parameters
        params = [p for p in self.__dict__ if p[:4] == 'par_']
        f = open(self.basepath+'_%s.dat' % PARAMS_FNAME, 'w')
        for i,p in enumerate(params):
            f.write('# column %d: %s\n\n' % (i,p))
        for i,p in enumerate(params):
            f.write('%s\t' % str(getattr(self, p)))
        f.write('\n')        
        f.close()
        
        if idx_increment:
            self.dataset_idx += 1
        return


def main():
    m = Measurement('test')
    params = [p for p in m.__dict__ if p[:4] == 'par_']
    for p in params:
        print getattr(m, p)


if __name__ == "__main__":
    main()
