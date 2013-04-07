# some convenience tools
#

import os
import time
import logging
import numpy as np

try:
    import qt
    datadir = qt.config['datadir']
except:
    datadir = r'd:\measuring\data'

def nearest_idx(array, value):
    '''
    find the index of the value closest to the specified value.
    '''
    return np.abs(array-value).argmin()

def nearest_value(array, value):
    '''
    find the value in the array that is closest to the specified value.
    '''
    return array[nearest_idx(array,value)]

def latest_data(contains='',):
    '''
    finds the latest taken data with <contains> in its name.
    returns the full path of the data directory.
    '''

    daydirs = os.listdir(datadir)
    if len(daydirs) == 0:
        logging.warning('No data found in datadir')
        return None

    daydirs.sort()
    
    measdirs = []
    i = len(daydirs)-1
    while len(measdirs) == 0 and i >= 0:       
        daydir = daydirs[i]
        measdirs = [ d for d in os.listdir(os.path.join(datadir, daydir)) \
                if contains in d ]
        i -= 1
        
    if len(measdirs) == 0:
        logging.warning("Cannot find any data folder containing '%s'" \
                % contains)
        return None

    measdirs.sort()
    measdir = measdirs[-1]

    return os.path.join(datadir,daydir,measdir)


def data_from_time(timestamp):
    '''
    returns the full path of the data specified by its timestamp in the
    form YYYYmmddHHMMSS.
    '''
    daydirs = os.listdir(datadir)

    if len(daydirs) == 0:
        logging.warning('No data found in datadir')
        return None
    daydirs.sort()
    
    if len(timestamp) == 6:
        daystamp = time.strftime('%Y%m%d')
        tstamp = timestamp
    elif len(timestamp) == 14:
        daystamp = timestamp[:8]
        tstamp = timestamp[8:]
    else:
        logging.warning("Cannot interpret timestamp '%s'" % timestamp)
        return None

    if not os.path.isdir(os.path.join(datadir,daystamp)):
        logging.warning("Requested day '%s' not found" % daystamp)
        return None

    measdirs = [ d for d in os.listdir(os.path.join(datadir,daystamp)) \
            if d[:6] == tstamp ]
    
    if len(measdirs) == 0:
        logging.warning("Requested data '%s'/'%s' not found" \
                % (daystamp, tstamp))
        return None
    elif len(measdirs) == 1:
        return os.path.join(datadir,daystamp,measdirs[0])
    else:
        logging.warning('Timestamp is not unique: ', str(measdirs))
        return None

def measurement_filename(directory=os.getcwd(), ext='hdf5'):
    dirname = os.path.split(directory)[1]
    fn = dirname+'.'+ext

    if os.path.exists(os.path.join(directory,fn)):
        return os.path.join(directory,fn)
    else:
        logging.warning("Data path '%s' does not exist" % \
                os.path.join(directory,fn))
        return None

    

