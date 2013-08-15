"""
Cython-based fast data analysis for raw data obtained with the HH in T2 mode.

authors:
Gerwin Koolstra
Wolfgang Pfaff
"""

import cython
import time
import numpy as np
from cython.view cimport array as cvarray
cimport numpy as cnp


###
### Old-style methods
###

# down until LDE_live_filter we used to analyse after measurement with the methods below.
# they work fine, but the data format for input ((N,3) array with uint64 format) is not
# used anymore, so they are rather deprecated; I'll leave them in as instructions.

@cython.boundscheck(False)
@cython.wraparound(False)
def convert_to_real_time_ps(cnp.ndarray[cnp.uint64_t, ndim=2, mode='c'] data not None,
    cnp.uint64_t wraparound = 33552000):
    """
    This function converts event time of all T2 records into the real time.
    Algorithm is taken from h2demo.c that comes with the HH.
    """

    cdef cnp.uint64_t k
    cdef cnp.uint64_t ofl = 0
    cdef cnp.uint64_t length = data.shape[0]

    for k in range(length):
        if data[k,1] == 63:
            ofl += wraparound
        else:
            data[k,0] += ofl
            data[k,0] = data[k,0] / 2

    return data


@cython.boundscheck(False)
@cython.wraparound(False)
def delete_solitary_syncs(cnp.ndarray[cnp.uint64_t, ndim=2, mode='c'] data not None):
    """
    This function deletes all syncs that are followed by another sync.
    """

    cdef cnp.uint64_t k
    cdef cnp.uint64_t length = data.shape[0]

    solitary_syncs = list()

    for k in range(length-1):
        if data[k,1] == 0 and data[k,2] == 1:
            if data[k+1,1] == 0 and data[k+1,2] == 1:
                solitary_syncs.append(k)

    if data[-1,1] == 0 and data[-1,2] == 1:
        solitary_syncs.append(length-1)

    return np.array(solitary_syncs)

@cython.boundscheck(False)
@cython.wraparound(False)
def get_sync_time_ps(cnp.ndarray[cnp.uint64_t, ndim=2, mode='c'] data not None):
    """
    this function returns the relative times for all events in a record,
    where relative time is the time (in ps) since the last sync event.
    """
    cdef cnp.uint64_t k
    cdef cnp.uint64_t length = data.shape[0]
    cdef cnp.ndarray[cnp.uint64_t, ndim=1, mode='c'] rt = np.zeros(length, dtype='u8')
    cdef cnp.uint64_t last_sync_time = 0

    for k in range(length):
        if data[k,2] == 1 and data[k,1] == 0:
            last_sync_time = data[k,0]

        rt[k] = data[k,0] - last_sync_time

    return rt

@cython.boundscheck(False)
@cython.wraparound(False)
def get_outofwindow_event_idxs(cnp.ndarray[cnp.uint64_t, ndim=2, mode='c'] data not None,
    cnp.ndarray[cnp.uint64_t, ndim=1, mode='c'] sync_times not None, 
    mintime=None, maxtime=None, channel=0, marker=False):
    
    """
    This function returns an array of indices that violate sync time boundaries (given by
        mintime, maxtime, in ps) on a given channel.

    TODO: I don't check here whether data and sync_times have the same length,
    that should probably be done.
    """
    cdef cnp.uint64_t k
    cdef cnp.uint64_t length = data.shape[0]

    outofwindow_idxs = list()
    special = 1 if marker else 0

    for k in range(length):
        too_early = False
        too_late = False

        if data[k,1] == channel and data[k,2] == special:
            if mintime != None:
                too_early = (sync_times[k] < mintime)
            if maxtime != None:
                too_late = (sync_times[k] > maxtime)

        if too_early or too_late:
            outofwindow_idxs.append(k)

    return np.array(outofwindow_idxs)

@cython.boundscheck(False)
@cython.wraparound(False)
def get_sync_idxs(cnp.ndarray[cnp.uint64_t, ndim=2, mode='c'] data not None):
    """
    Returns the array indices of all sync events.
    """
    cdef cnp.uint64_t k
    cdef cnp.uint64_t length = data.shape[0]

    sync_idxs = list()

    for k in range(length):
        if data[k,2] == 1 and data[k,1] == 0:
            sync_idxs.append(k)

    return np.array(sync_idxs)

@cython.boundscheck(False)
@cython.wraparound(False)
def get_coincidence_intervals(cnp.ndarray[cnp.uint64_t, ndim=2, mode='c'] data not None,
    max_tau = None):
    """
    Returns an array containing all coincidence intervals (that's basically g2
        with tau > 0, we don't discriminate between detectors here)
    """
    cdef cnp.uint64_t k
    cdef cnp.uint64_t l
    cdef cnp.uint64_t length = data.shape[0]
    cdef cnp.uint64_t t0
    cdef cnp.uint64_t t1    

    if max_tau == None:
        max_tau = data[length-1,0]
    taus = list()

    for k in range(length-1):
        if data[k,2] == 0: # only photons allowed
            t0 = data[k,0]
            
            for l in range(k+1,length):
                if data[l,2] == 0:
                    t1 = data[l,0]

                    if t1 - t0 > max_tau:
                        break

                    taus.append(t1-t0)

    return np.array(taus)



###
### LDE live filtering
###

# use this method during the measurement loop with the HH in T2 mode.
# the other methods above are deprecated for now and should only be seen
# as instructions.

# TODO some methods above, most importantly time window filtering 
# and coincidence intervals would still be cool to have!

@cython.boundscheck(False)
@cython.wraparound(False)
def LDE_live_filter(cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] time not None,
    cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] channel not None,
    cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] special not None,
    cnp.uint64_t t_ofl,
    cnp.uint64_t t_lastsync):
    """
    This function expects as input decoded HH data:
    - an array with time information,
    - an array for the channel,
    - an array containing the special bit,
    and overflow information: 
    - the current overflow time,
    - and the time of the last sync. (both start with zero and get updated by
        calls of this function).
    
    Returns for each event (syncs and overflows are not in the data anymore)
    - the absolute time since msmt start (in ps)
    - channel
    - special bit,
    - relative time to the last previous sync (in ps)
    and overflow information (absolute overflow time and time of the last sync).
    """

    cdef cnp.uint64_t k
    cdef cnp.uint64_t l = 0
    cdef cnp.uint64_t wraparound = 33552000
    cdef cnp.uint64_t length = time.shape[0]
    cdef cnp.ndarray[cnp.uint64_t, ndim=1, mode='c'] sync_time = np.empty((length,), dtype='u8')
    cdef cnp.ndarray[cnp.uint64_t, ndim=1, mode='c'] hhtime = np.empty((length,), dtype='u8')
    cdef cnp.ndarray[cnp.uint8_t, ndim=1, mode='c'] hhchannel = np.empty((length,), dtype='u1')
    cdef cnp.ndarray[cnp.uint8_t, ndim=1, mode='c'] hhspecial = np.empty((length,), dtype='u1')

    for k in range(length):
        if channel[k] == 63:
            t_ofl += wraparound
            continue

        # syncs are basically pointless -- we only need for each element the time
        # since the last sync
        if special[k] == 1 and channel[k] == 0:
            t_lastsync = (time[k] + t_ofl) / 2 # the factor 2 comes from an extra bit. see HH docs.
            continue

        hhtime[l] = (t_ofl + time[k]) / 2
        hhchannel[l] = channel[k]
        hhspecial[l] = special[k]
        sync_time[l] = (t_ofl + time[k]) / 2  - t_lastsync

        l += 1

    return hhtime[:l], hhchannel[:l], hhspecial[:l], sync_time[:l], l, t_ofl, t_lastsync
