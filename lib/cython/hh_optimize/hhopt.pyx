"""
HydraHarp optimization module, extension in C for Python
Written by Gerwin Koolstra, June - July 2013

Most of the functions in this module are optimized for the data output from the 
HydraHarp. They replace slower equivalents in Numpy. 
"""

import cython
import time
import numpy as np
from cython.view cimport array as cvarray
cimport numpy as cnp


@cython.boundscheck(False)
@cython.wraparound(False)
def stack(cnp.ndarray[cnp.uint_t, mode="c"] nsync not None, 
        cnp.ndarray[cnp.uint_t, mode="c"] event_time not None,
        cnp.ndarray[cnp.uint_t, mode="c"] channel not None,
        cnp.ndarray[cnp.uint_t, mode="c"] special not None):

    cdef int k
    cdef int len_array = nsync.shape[0]
    cdef cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] out_array = \
            np.empty([len_array,4], dtype = np.uintc)

    for k in range(len_array):
        out_array[k,0] = nsync[k]
        out_array[k,1] = event_time[k]
        out_array[k,2] = channel[k]
        out_array[k,3] = special[k]

    return out_array


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
def filter_overflows(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None, 
        int ofl_offset = 0):
    """
    Filters the data on overflows and adjusts the sync number of the data.
    A possible sync offset is also taken into account.

    You should be careful. Running this function changes the input argument data. 
    To avoid frustrations, call this function from python as 
    filter_overflows(data.copy(), ofl_offset = 0). Then only the copy to the 
    data is changed, but we don't care about that. 

    Bottleneck: np.delete (takes ~300 ms)
    Without delete: timed at 17 ms.
    """

    cdef cnp.ndarray[cnp.uint_t, mode="c"] idx_ofl = C_get_oflw_idxs(data)
    cdef int len_oflw = idx_ofl.shape[0]
    cdef int len_arr = data.shape[0]
    cdef unsigned int[::1] sync_offsets = np.empty(len_arr, dtype = np.uintc)
    cdef int k
    cdef unsigned int idx, next_idx

    if len_arr == 0:
        sync_offsets[:] = ofl_offset*1024

    for k in range(len_oflw):
        idx = idx_ofl[k]

        if k == 0:
            sync_offsets[:idx] = ofl_offset*1024
        else:
            if k == len_oflw-1:
                sync_offsets[idx:] = (k+ofl_offset)*1024
            else:
                next_idx = idx_ofl[k+1]
                sync_offsets[idx:next_idx] = (k+ofl_offset)*1024

    data[:,0] += sync_offsets
    
    cdef cnp.ndarray[cnp.uint_t, mode="c"] mask = create_filter_from_array(idx_ofl, len_arr)
    return apply_filter_to_2darray(data, mask)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
def get_oflw_idxs(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None):
    """
    Gets the overflow indexes. 

    Timed at 4.5 ms.
    """

    cdef int k
    cdef int len_data = data.shape[0] #len(data[:,2])
    
    where = list()

    for k in range(len_data):
        if data[k,2] == 63:
            where.append(k)

    return np.asarray(where, dtype = np.uint)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
cdef cnp.ndarray[cnp.uint_t, mode="c"] C_get_oflw_idxs(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data):
    """
    Let's try the C-variant of this function
    """

    cdef int k
    cdef int len_data = data.shape[0]
    
    where = list()

    for k in range(len_data):
        if data[k,2] == 63:
            where.append(k)

    return np.asarray(where, dtype = np.uint)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
def filter_decreasing_syncs(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None):
    """
    Filters poo, shit, stool and crap. 

    Note: no liquid waste!
    """

    print '* filter on decreasing sync numbers at the beginning'
    
    cdef unsigned int k = 0
    cdef int count = 0
    cdef unsigned int [:,::1] Data = data
    cdef int minsync = np.argmin(data[:,0])
    cdef unsigned int el1, el2    

    Data = Data[minsync:,:]
    
    cdef int len_data = Data.shape[0]    

    for k in range(len_data-1):
        el1 = Data[k,0]
        el2 = Data[k+1,0]
        
        if el1 > el2:
            count = k+1

    Data = Data[count:,:]

    print '  first %d events were invalid, %d remain' % (count, Data.shape[0])

    return np.asarray(Data)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
cdef unsigned int len_where(cnp.ndarray[cnp.uint_t, mode="c"] filtered, unsigned int condition = 1):
    """
    This function I use to find out how many "idx" in an array "filtered" follow 
    the condition filtered[idx] == condition. 
    """

    cdef unsigned int len_filtered = filtered.shape[0]
    cdef unsigned int k
    cdef unsigned int out = 0

    for k in range(len_filtered):
        if filtered[k] == condition:
            out += 1

    return out


@cython.boundscheck(False)
@cython.wraparound(False)
def apply_filter_to_2darray(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None, 
        cnp.ndarray[cnp.uint_t, mode="c"] filtered not None):
    """
    Removes rows from an array. The rows to be removed are specified in a
    mask array containing zeros or ones. The indexes with ones are the rows
    that are to be removed from the array data. 

    Timed at ~26 ms. 
    """
    cdef unsigned int len_final_data = len_where(filtered, condition = 1)
    cdef unsigned int len_data = data.shape[0]
    cdef unsigned int width_data = data.shape[1]
    cdef cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] filtered_data = \
            np.empty([len_final_data, 4], dtype = np.uint)
    cdef unsigned int k, j
    cdef unsigned int idx = 0

    for k in range(len_data):
        if filtered[k]:
            for j in range(width_data):
                filtered_data[idx,j] = data[k,j]
            idx += 1
        
    return filtered_data
    
@cython.boundscheck(False)
@cython.wraparound(False)


def apply_filter_to_1darray(cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] data not None, 
        cnp.ndarray[cnp.uint_t, mode="c"] mask not None):
    """
    Removes rows from a 1D array. The rows to be removed are specified in a
    mask array containing zeros or ones. The indexes with zeros are the rows
    that are to be removed from the array data. 

    Timed at ~26 ms. 
    """
    cdef unsigned int len_final_data = len_where(mask, condition = 1)
    cdef unsigned int len_data = data.shape[0]
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] filtered_data = \
            np.empty([len_final_data], dtype = np.uint)
    cdef unsigned int k
    cdef unsigned int idx = 0

    for k in range(len_data):
        if mask[k]:
            filtered_data[idx] = data[k]
            idx += 1
        
    return filtered_data


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
cdef cnp.ndarray[cnp.uint_t, mode="c"] create_filter_from_array(cnp.ndarray[cnp.uint_t, mode="c"] array,
        unsigned int array_length):
    """
    Input: array with indexes. These indexes determine the indexes in the output
    array that will be set 1. The output array will have length "array_length".
    """

    cdef unsigned int k, flag_index
    cdef cnp.ndarray[cnp.uint_t, mode="c"] filter_out = \
            np.ones(array_length, dtype = np.uintc)
    cdef unsigned int len_in = array.shape[0]

    for k in range(len_in):
        flag_index = array[k]
        filter_out[flag_index] = 0

    return filter_out

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

@cython.boundscheck(False)
@cython.wraparound(False)
def filter_counts_on_marker(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None, 
        int mchan = 1, cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] delta_syncs = np.array([1,2], dtype = np.uintc)):
    """
    Filter on counts that have a marker on mchan and whose sync
    is in the allowed deltas, where delta = sync_count - sync_mrkr.
    filters on both channels.
    """
    #these are the markers
    special = data[:,3] == 1
    
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] mrkr = \
            np.logical_and(special, data[:,2] == mchan).astype(np.uintc)
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] mrkr_idx = \
            np.where(mrkr)[0].astype(np.uintc)
    
    cdef int noof_mrkrs = mrkr_idx.shape[0]
    cdef int noof_deltas = delta_syncs.shape[0]
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] clicks = \
            np.logical_not(special).astype(np.uintc)
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] goodsyncs = \
            np.empty(noof_mrkrs*noof_deltas, dtype = np.uintc)
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] marker_sync_nrs = \
            apply_filter_to_1darray(data[:,0].astype(np.uintc), mrkr)
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] click_sync_nrs = \
            apply_filter_to_1darray(data[:,0].astype(np.uintc), clicks)
    cdef unsigned int len_goodsyncs = goodsyncs.shape[0]
    cdef unsigned int len_delta_syncs = delta_syncs.shape[0]
    cdef unsigned int len_clicks = click_sync_nrs.shape[0]
    cdef unsigned int l, k, c, d, j, click
    cdef unsigned int i = 0, lstart = 0, lend = noof_mrkrs, idx = 0
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] add
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] good = \
            np.zeros(len_clicks, dtype = np.uintc)

    for k in range(len_delta_syncs):
        d = delta_syncs[k]
        add = initialize_array(noof_mrkrs, d)
        goodsyncs[i*noof_mrkrs:(i+1)*noof_mrkrs] = marker_sync_nrs + add
        i += 1
    
    #Note this is a fast substitution for the NumPy function np.in1d, which is 
    #only valid for the case that delta_syncs = [1,2]. Any other cases are 
    #handled below.
    if len_delta_syncs == 2:        
        for c in range(len_clicks):
            click = click_sync_nrs[c]
            
            for l from lstart <= l < lend:
                
                if click == goodsyncs[l] or click == goodsyncs[l+noof_mrkrs]:
                    good[c] = 1
                    lstart = l
                    break
                
                elif click < goodsyncs[l]:
                    break

                idx += 1
    
    #You can write your own adaptation for different values of delta_syncs,
    #or simply leave the numpy function here. 
    else:
        good = np.in1d(click_sync_nrs, goodsyncs)

    #At this point we have an array "good", which contains flags (0 or 1) for 
    # - the sync number is one more than the marker number AND
    # - the sync number is associated with a click on one of the two channels
    
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] good_idxs = \
            np.where(clicks)[0].astype(np.uintc)
    cdef unsigned int N = good_idxs.shape[0]
    
    #Below we make a selection of all the clicks. Only the ones that are 
    #marked as good will stay: we do this by no longer marking it as a click
    #i.e. by setting the appropriate indices of clicks to 0
    for i in range(N):
        if not good[i]:
            clicks[good_idxs[i]] = 0
    
    #This is the final mask. Only special events (markers) or 
    #clicks that are marked as "good" are now left in the data. 
    filtered = np.logical_or(special, clicks)
    if len(np.where(filtered)[0]) == 0:
        return np.zeros((0,4), dtype=np.uintc)

    return apply_filter_to_2darray(data, filtered.astype(np.uintc))
  

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] initialize_array(unsigned int N, unsigned int value):

    cdef unsigned int k
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] array = \
            np.empty(N, dtype = np.uintc)

    for k in range(N):
        array[k] = value

    return array


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
def filter_double_clicks_per_sync(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None):
    """
    This is a function typically used for an anti-bunching experiment. 
    It filters events where two clicks were recorded for the same 
    sync number. All other events are discarded, including events 
    with only one click per sync.
    """
    cdef unsigned int k
    cdef unsigned int len_data = data.shape[0]
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] mask = \
            np.zeros(len_data, dtype = np.uintc)

    for k from 1 <= k < len_data:

        if data[k,0] == data[k-1,0]:
            mask[k] = 1
            mask[k-1] = 1

    return apply_filter_to_2darray(data, mask)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

@cython.boundscheck(False)
@cython.wraparound(False)
def get_dts(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None, 
        int valid_dt = 1):
    """
    This function returns an array of dts. The dts are time differences
    between two clicks on ch2 - ch1 = valid_dt, or ch1 - ch2 = valid_dt. 
    All other combinations are discarded, e.g.: if valid_dt = 0, then no 
    dts are returned for clicks on different channels. Also, a dt is only 
    valid if the clicks corresponded to the same sync channel. 
    """

    cdef unsigned int k
    cdef unsigned int len_data = data.shape[0]
    cdef int sync_difference, ch_difference

    dts = list()

    for k from 1 <= k < len_data:
        
        sync_difference = data[k,0] - data[k-1,0]
        ch_difference = data[k,2] - data[k-1,2]            
        
        if sync_difference == 0 and ch_difference == valid_dt:
            dts.append(int(data[k,1] - data[k-1,1]))
        elif sync_difference == 0 and ch_difference == -valid_dt:  
            dts.append(int(data[k-1,1]) - int(data[k,1]))

    return np.asarray(dts)        

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
def get_sync_number(cnp.ndarray[cnp.uint8_t, ndim = 1, mode="c"] ch not None,
        unsigned int sync_chan, unsigned int sync_offset = 0):
    """
    Outputs an array with the same length as ch, with sync numbers for each 
    event. 
    """

    cdef unsigned int k, sync_nr = sync_offset
    cdef unsigned int len_ch = ch.shape[0]
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] sync_numbers = \
            np.empty(len_ch ,dtype = np.uintc)
    cdef cnp.ndarray[cnp.uint8_t, ndim = 1, mode="c"] syncs = \
            (ch == sync_chan).astype(np.uint8)

    for k in range(len_ch):
        
        if syncs[k]:
            sync_nr += 1
        
        sync_numbers[k] = sync_nr    

    return sync_numbers

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
@cython.boundscheck(False)
@cython.wraparound(False)
def get_dt_wrt_sync(cnp.ndarray[cnp.uint8_t, ndim = 1, mode="c"] ch not None,
                    cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] ts not None,
                    unsigned int sync_chan):
    """
    Outputs an array with the same length as ts, with indices the time differences
    with respect to the last sync. Note that the first element must be a sync,
    otherwise the first few elements are neglected. This must be implemented 
    separately in the measurement code.
    """

    cdef unsigned int k, kmin, last_sync_idx
    cdef unsigned int len_ts = ts.shape[0]

    cdef cnp.ndarray[cnp.uint8_t, ndim = 1, mode="c"] syncs = \
            (ch == sync_chan).astype(np.uint8)
    cdef cnp.ndarray[cnp.uint_t, ndim = 1, mode="c"] timings_wrt_sync = \
            np.empty(len_ts, dtype = np.uintc)

    #determine the first sync
    if syncs[0] == False:
        for k in range(len_ts):
            if syncs[k]:
                kmin = k
                break
            else:
                timings_wrt_sync[k] = 0

    for k from kmin <= k < len_ts:

        if syncs[k]:
            timings_wrt_sync[k] = 0
            last_sync_idx = k
        else:
            timings_wrt_sync[k] = ts[k] - ts[last_sync_idx]

    return timings_wrt_sync

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

@cython.boundscheck(False)
@cython.wraparound(False)
def get_dts_qutau(cnp.ndarray[cnp.uint_t, ndim = 2, mode="c"] data not None, 
        int channelA, int channelB):
    """
    Put channelA = -1 to get the time difference with respect to the sync.
    """
    cdef unsigned int k
    cdef unsigned int len_data = data.shape[0]
    cdef int sync_difference, ch_difference

    cdef extern from "math.h":
        int abs(int x)

    cdef cnp.ndarray[cnp.uint_t, mode="c"] Bidxs = \
            (np.where(data[:,2] == channelB)[0]).astype(np.uintc)       
    
    if Bidxs.shape[0] == 0:
        print "No clicks on channel B (%d) were found in the data"%channelB
    
    cdef cnp.ndarray[cnp.uint_t, mode="c"] dts = \
            np.empty(Bidxs.shape[0], dtype = np.uintc)
    
    for k in range(Bidxs.shape[0]):
        dts[k] = data[Bidxs[k],1]              
    
    #return if you just want the dts of channel B w.r.t. the sync.
    if channelA < 0:
        return dts
    else:
        print "Not yet implemented"
        return 0
