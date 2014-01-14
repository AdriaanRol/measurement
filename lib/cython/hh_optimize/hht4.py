import os, sys, time
import shutil
#from measurement.lib.cython.hh_optimize import hhopt
import numpy as np
import hhopt

def data_from_file(filepath, do_filter_ofls=True, do_filter_crap=True, 
        ch0_lastbin=700, ch1_lastbin=700, **kw):
    
    t0 = time.clock()
    d = np.load(filepath)
    raw = d['data'].astype(np.uint)
    d.close()
    print "Loading the data took %.2f seconds"%(time.clock()-t0)

    data = decode(raw)

    if do_filter_ofls:
        data = hhopt.filter_overflows(data.copy())

    if ch0_lastbin != None:
        data = filter_timewindow(data, 0, 0, ch0_lastbin)

    if ch1_lastbin != None:
        data = filter_timewindow(data, 1, 0, ch1_lastbin)

    if do_filter_crap:
        data = hhopt.filter_decreasing_syncs(data)
        
    return data


def filter_raw_data(rawdata, do_filter_ofls = True, do_filter_crap = True, 
        do_filter_counts_on_mrkr = True, ch0_lastbin = 700, ch1_lastbin = 700,
        marker_chan = 1, dsyncs = np.array([1,2], dtype = np.uintc)):
    
    if len(rawdata) != 0:
        data = decode(rawdata.astype(np.uintc))

        if do_filter_ofls:
            data = hhopt.filter_overflows(data.copy())

        if ch0_lastbin != None:
            data = filter_timewindow(data, 0, 0, ch0_lastbin)

        if ch1_lastbin != None:
            data = filter_timewindow(data, 1, 0, ch1_lastbin)

        if do_filter_crap:
            data = hhopt.filter_decreasing_syncs(data)

        if do_filter_counts_on_mrkr:
            data = hhopt.filter_counts_on_marker(data, mchan = np.int(marker_chan),
                    delta_syncs = dsyncs.astype(np.uintc))
    else:
        data = np.empty((0,4), dtype = np.uintc)
        print "No data to be filtered!"

    return data
    
    
def filter_raw_antibunch_data(rawdata, ch0_lastbin, ch1_lastbin, filter_on_double_clicks = True): 
  
    if len(rawdata) != 0:
        data = decode(rawdata) 
        
        if len(data) != 0:
            data = hhopt.filter_overflows(data.copy()) 
        #if len(data) != 0:
        #    data = filter_timewindow(data, 0, 0, ch0_lastbin) 
        #if len(data) != 0:
        #    data = filter_timewindow(data, 1, 0, ch1_lastbin) 
        if len(data) != 0:
            data = hhopt.filter_decreasing_syncs(data) 
      
        if filter_on_double_clicks and len(data) != 0: 
            data = hhopt.filter_double_clicks_per_sync(data) 
    else:
        data = np.zeros((0,4), dtype = np.uintc)
  
    return data 
  
  
def get_dts(data, start_ch = 0, stop_ch = 1): 
    
    if len(data) != 0:
        valid_dt = stop_ch - start_ch 
        sorted_data = data[np.lexsort((data[:,1], data[:,0]))] 
        dts = hhopt.get_dts(sorted_data, int(valid_dt)) 
    else:
        dts = np.zeros([])
  
    return dts                 
    

def _stitch_data(d1,d2):
    l1 = len(d1[:,0])
    l2 = len(d2[:,0])

    return np.vstack((d1,d2))


def data_from_folder(path, sync_of=300, filecontains='alldata', *arg, **kw):
    files = [ f for f in os.listdir(path) if f[:1] != '.' and filecontains in f and f[-4:] == '.npz' ]

    fulldata = np.zeros((0,4), dtype=np.uint)
    ofl_of = 0
    for f in files:
        data = data_from_file(os.path.join(path, f), *arg, **kw)
        data[:,0] += ofl_of + sync_of
        ofl_of = data[-1,0] + 1
        fulldata = _stitch_data(fulldata, data)

    return fulldata


def decode(data):
    nsync = np.bitwise_and(data, 2**10-1)
    event_time = np.bitwise_and(np.right_shift(data, 10), 2**15-1)
    channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
    special = np.bitwise_and(np.right_shift(data, 31), 1)
    return hhopt.stack(nsync, event_time, channel, special)


def filter_overflows(data, ofl_offset=0, print_status = False):

    print "Use the external function in the hhopt module."    


def filter_timewindow(data, chan, mintime, maxtime, print_status = False):    
    t0 = time.time()

    if print_status:
        print '* filter ch %d timewindow' % chan
    
    if len(data) == 0:
        print '  empty data, cannot time-filter'
        return data

    notspecial = data[:,3] == 0
    ch = data[:,2] == chan
    click = np.logical_and(notspecial, ch)
    clickstartbad = np.logical_and(click, data[:,1] < mintime)
    clickstopbad = np.logical_and(click, data[:,1] > maxtime)
    clickbad = np.logical_or(clickstartbad, clickstopbad)

    if print_status:
        print '  found %d of %d clicks out of time window' % \
            (len(data[clickbad]), len(data[click]))
        print '  processing took %.2f secs.' % (time.time()-t0)

    filtered = np.logical_not(clickbad)
    if len(np.where(filtered)[0]) == 0:
        return np.zeros((0,4), dtype=np.uint)
    
    return hhopt.apply_filter_to_2darray(data, filtered.astype(np.uint))


def filter_counts_on_marker(data, mchan, delta_syncs=[1,2], print_status=False):

    print "Use the external function in the hhopt module."   


def filter_decreasing_syncs(data):

    print "Use the external function in the hhopt module."


def filter_marker_on_counts(data, mchan, delta_syncs=[0], print_status = False):
    t0 = time.time()
    if print_status:
        print '* filter mrkr %s on counts' % mchan

    special = data[:,3] == 1
    mrkr = np.logical_and(special, data[:,2] == mchan)
    other_mrkr = np.logical_and(special, np.logical_not(mrkr))
    clicks = np.logical_not(special)

    good = data[mrkr,0] < 0
    for d in delta_syncs:
        good = np.logical_or(good, np.in1d(data[mrkr,0]+d, data[clicks,0]))

    for i,idx in np.ndenumerate(np.where(mrkr)[0]):
        if not good[i]:
            mrkr[idx] = False
    
    if print_status:
        print '  %d markers are valid.' % len(data[mrkr])
        print '  processing took %.2f secs.' % (time.time()-t0)

    filtered = np.logical_or(np.logical_or(other_mrkr, mrkr), clicks)
    if len(np.where(filtered)[0]) == 0:
        return np.zeros((0,4), dtype=np.uint)
    
    return hhopt.apply_filter_to_2darray(data, filtered.astype(np.uint))


def filter_early_high_syncs(data):
    '''
    quickfix no1 (august 3, 2012): start at the smalles sync no, discard
    all data before.
    '''
    minidx = np.argmin(data[:,0])
    return data[minidx:,:]


def delete_markers(data, mchan):
    special = data[:,3] == 1
    mrkr = np.logical_and(special, data[:,2] == mchan)

    filtered = np.logical_not(mrkr)
    if len(np.where(filtered)[0]) == 0:
        return np.zeros((0,4), dtype=np.uint)

    return data[filtered]


def get_events(d, min_times=(0,0), max_times=(1000,1000), 
        marker_filter=True, filter_marker_channel=1,
        syncs_after_marker=300, verbose=2, *arg, **kw):

    data = decode(d)
    print '* %d events in total.' % len(data)

    data, ofls = filter_overflows(data)
    data = filter_timewindow(data, 0, min_times[0], max_times[0])
    data = filter_timewindow(data, 1, min_times[1], max_times[1])

    data = filter_counts_on_marker(data, 1, [1,2])

    return data


def save_data(d, filepath='hhdata'):
    np.savez(filepath, data=d)
    return True


def get_click_times(data):    
    special = data[:,3] == 1
    allclicks = data[np.logical_not(special)]
    t0 = allclicks[allclicks[:,2]==0,1]
    t1 = allclicks[allclicks[:,2]==1,1]

    return t0,t1


def get_clicks(data):
    if len(data) == 0:
        return np.zeros((4,0), dtype=np.uint), np.zeros((4,0), dtype=np.uint)

    special = data[:,3] == 1
    allclicks = data[np.logical_not(special)]
    ch0 = allclicks[:,2]==0
    ch1 = allclicks[:,2]==1
    t0 = allclicks[ch0,:] if len(ch0) > 0 else np.zeros((4,0), dtype=np.uint)
    t1 = allclicks[ch1,:] if len(ch1) > 0 else np.zeros((4,0), dtype=np.uint)

    return t0,t1


def get_allclicks(data):
    c = data[:,3] == 0
    allclicks = data[c] if len(np.where(c)[0]) > 0 else np.zeros((4,0), dtype=np.uint)    
    return allclicks 


def get_markers(data, mchan=1):
    special = data[:,3] == 1
    mrkrs = np.logical_and(special, data[:,2]==mchan)

    if len(np.where(mrkrs)[0]) > 0:
        return data[mrkrs,:]
    else:
        return np.zeros((0,4), dtype=np.uint)


