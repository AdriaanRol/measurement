import os, sys, time
import shutil

import numpy as np

# # DONT USE WITH CORRUPTED DATA FILES
# def get_data_from_folder(path, file_contains='alldata',
#         file_ending='.npz', verbose=1, 
#         save=False, save_filename='alldata.npz', 
#         file_range=None, *arg, **kw):
#    
#     try:
#         i = len(file_ending)
#         filelist = [f for f in os.listdir(path) if \
#                 file_contains in f and f[-i:] == file_ending and f[:1] != '.' ]
# 
#         if file_range != None:
#             filelist = filelist[file_range[0]:file_range[1]]
#         
#     except:
#         print 'Could not get any files from the specified path, abort.'
#         return
#     
#     if verbose >= 1:
#         print 'Read data from folder. Total files:', len(filelist)
# 
#     
#     fulldat = []
#     lengths = []
# 
#     for i,fn in enumerate(filelist):
#         fp = os.path.join(path, fn)
#         
#         if verbose:
#             print 'Load data. process file %d of %d... (%s)' % (i+1, len(filelist), fn)
# 
#         try:
#             d = np.load(fp)
#             fulldat.append(d['data'].astype(np.uint64))
#             lengths.append(len(d['data'].astype(np.uint64)))
#         except:
#             print 'could not load data from %s.' % fp
#             raise
#         try:
#             d.close()
#         except:
#             pass
# 
#     if save:
#         np.savez(os.path.join(path,save_filename), data=fulldat)
#         print 'data saved to %s.npz' % save_filename
#         return True
# 
#     _fulldat = np.hstack(tuple(fulldat)) if len(fulldat) > 0 else array([])
#     return _fulldat

def data_from_file(filepath, do_filter_ofls=True, do_filter_crap=True, 
        ch0_lastbin=700, ch1_lastbin=700, **kw):
    
    d = np.load(filepath)
    raw = d['data'].astype(np.uint)
    d.close()

    data = decode(raw)

    if do_filter_ofls:
        data,ofls = filter_overflows(data)

    if ch0_lastbin != None:
        data = filter_timewindow(data, 0, 0, ch0_lastbin)

    if ch1_lastbin != None:
        data = filter_timewindow(data, 1, 0, ch1_lastbin)

    if do_filter_crap:
        data = filter_decreasing_syncs(data)
        
    return data

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
    return np.vstack((nsync, event_time, channel, special)).transpose()

def filter_overflows(data, ofl_offset=0, print_status = False):
    t0 = time.time()
    
    if print_status:
        print '* filter overflows'
    
    idx_ofl = np.where(data[:,2]==63)[0]
    if len(idx_ofl) == 0:
        data[:,0] += ofl_offset*1024
        
        return data, ofl_offset

    for i,idx in np.ndenumerate(idx_ofl):
        if i[0] == 0:
            data[:idx,0] += ofl_offset*1024
        
        if idx == idx_ofl[-1]:
            data[idx:,0] += (i[0]+ofl_offset)*1024
        else:
            data[idx:idx_ofl[i[0]+1], 0] += (i[0]+ofl_offset)*1024
    
    if print_status:
        print '  found %d ofl events.' % len(idx_ofl)
        print '  processing took %.2f secs.' % (time.time()-t0)
    
    return np.delete(data, idx_ofl, axis=0), i[0]+ofl_offset

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

    # print clickbad.shape, click.shape
    # print data.shape20120731010524-alldata-20.npz

    if print_status:
        print '  found %d of %d clicks out of time window' % \
            (len(data[clickbad]), len(data[click]))
        print '  processing took %.2f secs.' % (time.time()-t0)

    return data[np.logical_not(clickbad)]

def filter_counts_on_marker(data, mchan, delta_syncs=[1,2], print_status=False):
    '''
    filter on counts that have a marker on mchan and whose sync
    is in the allowed deltas, where delta = sync_count - sync_mrkr.
    filters on both channels.
    '''
    t0 = time.time()
    if print_status:
        print '* filter counts on mrkr %d' % mchan
   
    special = data[:,3] == 1
    mrkr = np.logical_and(special, data[:,2] == mchan)
    mrkr_idx = np.where(mrkr)[0]
    clicks = np.logical_not(special)
    
    # good = data[clicks,0] < 0 # gives an array with right size, all false
    noof_mrkrs = len(data[mrkr,0])
    noof_deltas = len(delta_syncs)

    goodsyncs = np.zeros(noof_mrkrs*noof_deltas, dtype=int) - 1
    for i,d in enumerate(delta_syncs):
        goodsyncs[i*noof_mrkrs:(i+1)*noof_mrkrs] = data[mrkr,0]+d
    
    good = np.in1d(data[clicks,0], goodsyncs)
  
    # should be small, can iterate
    for i,idx in np.ndenumerate(np.where(clicks)[0]):
        if not good[i]:
            clicks[idx] = False
    
    if print_status:
        print '  %d of %d clicks are valid.' % (len(data[clicks]), 
             len(data[np.logical_not(special)]))
        print '  processing took %.2f secs.' % (time.time()-t0)

    return data[np.logical_or(special, clicks)]

def filter_decreasing_syncs(data):
    
    print '* filter on decreasing sync numbers at the beginning'
    i = 0
    minsync = np.argmin(data[:,0])
    data = data[minsync:,]

    while not all([x<=y for x,y in zip(data[:,0],data[1:,0])]):
        data = data[1:,:]
        i += 1
        if len(data) == 0:
            break

    print '  first %d events were invalid, %d remain' % (i, len(data))
    return data

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

    return data[np.logical_or(np.logical_or(other_mrkr, mrkr), clicks)]

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
    return data[np.logical_not(mrkr)]


def get_events(d, min_times=(0,0), max_times=(1000,1000), 
        marker_filter=True, filter_marker_channel=1,
        syncs_after_marker=300, verbose=2, *arg, **kw):

    data = decode(d)
    print '* %d events in total.' % len(data)

    data, ofls = filter_overflows(data)
    data = filter_timewindow(data, 0, min_times[0], max_times[0])
    data = filter_timewindow(data, 1, min_times[1], max_times[1])

    data = filter_counts_on_marker(data, 1, [1,2])

    # print len(data), data.shape

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

def get_all_double_clicks(data):
    clicks=get_allclicks(data)
    clicks=np.vstack((clicks,np.zeros(4,dtype=np.uint32)))
    clicks=np.vstack((np.zeros(4,dtype=np.uint32),clicks))
    delta_marker=clicks[1:,0]-clicks[:-1,0]
    double_click_idx=np.ravel(np.where(delta_marker==1))
    triple_click_idx=np.ravel(np.where(delta_marker==0))

    bad_idx=np.append(triple_click_idx,\
            [triple_click_idx-np.ones(len(triple_click_idx),dtype=np.uint),\
            triple_click_idx+np.ones(len(triple_click_idx),dtype=np.uint)])

    valid_double_click_idx=np.setdiff1d(double_click_idx,bad_idx)
    valid_double_click_idx=np.sort(np.append(valid_double_click_idx,valid_double_click_idx+np.ones(len(valid_double_click_idx),dtype=np.uint)))
    return clicks[valid_double_click_idx]


    

    
