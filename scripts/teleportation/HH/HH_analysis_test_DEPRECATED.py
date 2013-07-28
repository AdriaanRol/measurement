import numpy as np
import h5py
import logging
import time

import T2_tools

FN = r'D:\measuring\data\20130726\125632_HH_test\125632_HH_test.hdf5'

### important tools

def decode(data):
    """
    Decode the binary data into event time (absolute, highest precision),
    channel number and special bit. See HH documentation about the details.
    """

    if len(data) == 0:
        return np.zeros((0, 3), dtype='u8')

    t0 = time.time()
    length = data.shape[0]
    print '* decode {} events... '.format(length),

    event_time = np.bitwise_and(data, 2**25-1)
    channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
    special = np.bitwise_and(np.right_shift(data, 31), 1)

    # we want to convert time that is supplemented by overflows into absolute
    # time in ps -- this requires 64 bit precision! ('u8')
    ret = np.zeros((length, 3), dtype='u8')
    ret[:,0] = event_time
    ret[:,1] = channel
    ret[:,2] = special

    t1 = time.time() - t0
    print 'done ({:.2f} s).'.format(t1)
    return ret

def convert_to_real_time(data, delete_ofls=True):
    """
    Change the event time of each record into the actual time (since starting)
    the measurment, given in ps.
    """
    if len(data) == 0:
        return np.zeros((0, 3), dtype='u8')

    t0 = time.time()
    print '* convert event time to real time... ',
    data = T2_tools.convert_to_real_time_ps(data)
    t1 = time.time() - t0 
    print 'done ({:.2f} s).'.format(t1)
    
    if delete_ofls:
        t0 = time.time()
        print '* delete overflows... ',
        data = np.delete(data, np.where(data[:,1]==63)[0], axis=0)
        t1 = time.time() - t0 
        print 'done ({:.2f} s).'.format(t1)

    return data

def delete_solitary_syncs(data):
    """
    Delete all sync events that are followed directly by the next sync event,
    i.e., are useless.
    """
    if len(data) == 0:
        return np.zeros((0, 3), dtype='u8')

    t0 = time.time()
    print '* delete solitary syncs... ',
    idxs = T2_tools.delete_solitary_syncs(data)
    data = np.delete(data, idxs, axis=0)
    t1 = time.time() - t0 
    print 'done ({:.2f} s).'.format(t1)

    return data

def get_sync_time(data):
    """
    Get for each record the time (in ps) since the last sync.
    """
    if len(data) == 0:
        return np.zeros((0, 3), dtype='u8')

    t0 = time.time()
    print '* get times relative to previous syncs... ',
    st = T2_tools.get_sync_time_ps(data)
    t1 = time.time() - t0 
    print 'done ({:.2f} s).'.format(t1)

    return st

def filter_events_on_sync_time(data, st=None, mintime=0, maxtime=int(500e3),
    channel=0, marker = False):
    """
    delete all events (photons only) whose arrival times (= times after sync) are out of limits.
    note that the time unit is ps!
    """
    if len(data) == 0:
        return np.zeros((0, 3), dtype='u8'), np.array([], dtype='u8')

    mintime = int(mintime)
    maxtime = int(maxtime)

    t0 = time.time()
    print '* filtering time of channel-{:d} events ({:d}--{:d} ps)...'.format(channel, mintime, maxtime),
    
    delete_idxs = T2_tools.get_outofwindow_event_idxs(data, st, mintime, maxtime, channel, marker)
    print 'delete {} records...'.format(len(delete_idxs)),
    data = np.delete(data, delete_idxs, axis=0)
    
    if st != None:
        st = np.delete(st, delete_idxs)

    t1 = time.time() - t0 
    print 'done ({:.2f} s).'.format(t1)

    if st != None:
        return data, st
    else:
        return data

def delete_all_syncs(data, st=None):
    """
    Delete all sync events. We can do this after all sufficient pre-filtering has been done,
    after that all relevant timing information is in absolute time and sync time.
    """
    if len(data) == 0:
        return np.zeros((0, 3), dtype='u8'), np.array([], dtype='u8')

    t0 = time.time()
    print '* delete all syncs... ',
    
    delete_idxs = T2_tools.get_sync_idxs(data)
    data = np.delete(data, delete_idxs, axis=0)

    if st != None:
        st = np.delete(st, delete_idxs)

    t1 = time.time() - t0 
    print 'done ({:.2f} s).'.format(t1)

    if st != None:
        return data, st
    else:
        return data

### Testing

def sync_time_hist(st):
    h,e = np.histogram(st * 1e-3)

    print 
    print 'Time arrival histogram'
    print 'bin edges (ns): '
    print e
    print 'events:         '
    print h
    print 

def coincidences(data, max_tau=(5*11.6e6 + 1e6)):
    taus = T2_tools.get_coincidence_intervals(data, max_tau)

    # make a histogram with one bin per 10us (interval between fake photons)
    # such that expected coincidence intervals are centered in the bin
    h,e = np.histogram(taus * 1e-3, bins=np.arange(6)*11.6e3 - 11.6e3/2)

    print 
    print 'Coincidence intervals'
    print 'bin edges (ns): '
    print e
    print 'events:         '
    print h
    print 


f = h5py.File(FN, 'a')
rawdata = f['/HH_rawdata'].value
f.close()

# convert the data from binary
data = decode(rawdata)

# convert the time information to absolute times, in ps
data = convert_to_real_time(data)

# delete all syncs that don't have any events following them -- those are useless
# and will make up most of the data in the real experiments
data = delete_solitary_syncs(data)

# get additionally the information when events came with respect to the previous sync
st = get_sync_time(data)

# now, we can filter events on that sync time (markers as well, see function above)
data, st = filter_events_on_sync_time(data, st, mintime=0, maxtime=500e3, channel=0)
data, st = filter_events_on_sync_time(data, st, mintime=0, maxtime=500e3, channel=1)

# at this point we don't need the syncs anymore.
data, st = delete_all_syncs(data, st)

# test: make a histogram of the arrival times.
# ideally in the test sequence this would be a delta function at 100 ns
# (rising edge of fake photon is 100 ns after rising edge of sync)
# all events besides theses photons have been deleted
sync_time_hist(st)

# getting the coincidence intervals -- this should be perfect antibunching 
# (we only have one event per sync). Note: this method is simplified,
# and does not discriminate between channels; therefore all tau values
# are positive (see the pyx file for algorithm)
coincidences(data)


