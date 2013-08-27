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
### LDE live filtering
###

# use this method during the measurement loop with the HH in T2 mode.
# the other methods above are deprecated for now and should only be seen
# as instructions.

# TODO: channel-dependent sync-time filters?

@cython.boundscheck(False)
@cython.wraparound(False)
def LDE_live_filter(cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] time not None,
    cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] channel not None,
    cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] special not None,
    cnp.uint64_t t_ofl,
    cnp.uint64_t t_lastsync,
    cnp.uint64_t last_sync_number,
    cnp.uint64_t min_sync_time,
    cnp.uint64_t max_sync_time):
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
    cdef cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] sync_number = np.empty((length,), dtype='u4')

    for k in range(length):
        if channel[k] == 63:
            t_ofl += wraparound
            continue

        # syncs are basically pointless -- we only need for each element the time
        # since the last sync; also, save the sync number, this can be handy for
        # filtering
        if special[k] == 1 and channel[k] == 0:
            t_lastsync = (time[k] + t_ofl) / 2 # the factor 2 comes from an extra bit. see HH docs.
            last_sync_number += 1
            continue

        _sync_time = (t_ofl + time[k]) / 2  - t_lastsync
        if _sync_time < min_sync_time or _sync_time > max_sync_time:
            continue

        hhtime[l] = (t_ofl + time[k]) / 2
        hhchannel[l] = channel[k]
        hhspecial[l] = special[k]
        sync_time[l] = _sync_time
        sync_number[l] = last_sync_number
        l += 1

    return hhtime[:l], hhchannel[:l], hhspecial[:l], sync_time[:l], sync_number[:l], l, t_ofl, t_lastsync, last_sync_number

