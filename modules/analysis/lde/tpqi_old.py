"""
Module for analyzing data from TPQI measurements.

Typical workflow:
    - place the raw data files from the tpqi measurement
      (timestamp-alldata-index.npz) into a subfolder of a working path for this
      measurement (default: rawdata).
    - if the indices in the file name don't contain leading zeros and indices
      with more than one digits occur, rename them with the rename_files
      method.
    - if there's more than one measurment run (more than one timestamp)
      group the files by using the group_files method.
    - use either get_clicks_from_grouped_data or get_clicks_from_folder
      method to extract the photon data.
    - use get_coincidences_from_file(s) to extract coincidences from the 
      photon data.
"""

import os, sys, time
import shutil

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


def rename_files(workingpath, inpath='rawdata'):
    """
    Pad filenames with zeros such that alphabetical ordering of the file
    names corresponds to the order in which the data was recorded.
    i.e., if we have something-1.npz, ..., something-10.npz, then
    the single-digit numbers at the end gets padded: something-01.npz.
    
    Assumes that the number is prepended by the last hyphen ('-') in
    the file name and that otherwise all filenames have the same length.

    input is the folder workingpath/inpath.
    """

    allfiles = os.listdir(os.path.join(workingpath, inpath))
    lengths = [ len(s) for s in allfiles ]
    maxlen = max(lengths)
    minlen = min(lengths)

    for fn in allfiles:
        if len(fn) == maxlen:
            continue
        
        pads = maxlen-len(fn)
        cut = fn.rfind('-') + 1
        fn_new = fn[:cut] + pads * '0' + fn[cut:]

        
        print 'renaming %s to %s...' % (fn, fn_new)
        shutil.move(os.path.join(workingpath, inpath, fn), 
                os.path.join(workingpath, inpath, fn_new))

    return True

def group_files(workingpath, inpath='rawdata', outpath='data',
        prefix_length=14):
    """
    Groups files by common prefix (corresponding to independent measurement
    runs). Gets the files in workingpath/inpath and copies them to subfolders
    of outpath, where each distinct prefix gets one subfolder. 
    """
    
    allfiles = os.listdir(os.path.join(workingpath, inpath))
    lastprefix = ''
    makedirfailed = False
    for fn in allfiles:
        if fn[:prefix_length] != lastprefix:
            try:
                os.makedirs(os.path.join(workingpath,outpath,fn[:prefix_length]))
            except:
                makedirfailed = True
            lastprefix = fn[:prefix_length]
        try:
            shutil.copyfile(os.path.join(workingpath,inpath,fn),
                    os.path.join(workingpath,outpath,lastprefix,fn))
        except:
            if makedirfailed:
                print 'something wrong with the directories?'
                return
            else:
                print 'could not copy file'
                return
    return True

def combine_files(workingpath, inpath='rawdata', outpath='combineddata',
        prefix_length=14):
    """
    Combine files by common prefix (corresponding to independent measurement
    runs). Gets the files in workingpath/inpath and saves combined files
    to outpath. 
    """
    
    allfiles = os.listdir(os.path.join(workingpath, inpath))
       
    while len(allfiles) > 0:
        currentprefix = allfiles[0][:prefix_length]
        grp = [ f for f in allfiles if f[:prefix_length] == currentprefix ]
        allfiles = allfiles[len(grp):]

        print 'current prefix:', currentprefix
        
        data = np.array([])
        for g in grp:
            
            print g

            try:
                d = np.load(os.path.join(workingpath, inpath, g))
                _data = d['data']
            except:
                print 'could not load data'
                raise
                return

            try:
                d.close()
            except:
                pass

            data = np.append(data, _data)

        if not os.path.isdir(os.path.join(workingpath, outpath)):
            os.makedirs(os.path.join(workingpath, outpath))
        
        np.savez(os.path.join(workingpath, outpath, currentprefix+'-alldata'),
            data=data, length=len(data))

    return True

### event and coincidence detection by wolfgang.
### 

def _get_data_from_folder(path, file_contains='alldata',
        file_ending='.npz', verbose=1, 
        save=False, save_filename='alldata.npz', 
        file_range=None, *arg, **kw):
   
    try:
        i = len(file_ending)
        filelist = [f for f in os.listdir(path) if \
                file_contains in f and f[-i:] == file_ending]

        if file_range != None:
            filelist = filelist[file_range[0]:file_range[1]]
        
    except:
        print 'Could not get any files from the specified path, abort.'
        return
    
    if verbose >= 1:
        print 'Read data from folder. Total files:', len(filelist)

    
    fulldat = np.array([], dtype=np.uint64)
    lengths = np.array([], dtype=np.uint64)

    for i,fn in enumerate(filelist):
        fp = os.path.join(path, fn)
        
        if verbose:
            print 'Load data. process file %d of %d...' % (i+1, len(filelist))

        try:
            d = np.load(fp)
            fulldat = np.append(fulldat, d['data'].astype(np.uint32))
            lengths = np.append(lengths, len(d['data'].astype(np.uint32)))
        except:
            print 'could not load data from %s.' % fp
            # raise
        try:
            d.close()
        except:
            pass

    if save:
        np.savez(os.path.join(path,save_filename), data=fulldat)
        print 'data saved to %s.npz' % save_filename
        return True

    return fulldat

# A HH event is a single integer
# decode into the four pieces of information that are contained
def _decode_event(event):
    nsync   = event & (2**10 - 1)
    event_time = (event >> 10) & (2**15 - 1)
    channel = (event >> 25) & (2**6 - 1)
    special = (event >> 31) & 1
    return nsync, event_time, channel, special

def _get_events(d, sync_of=0, min_times=(0,0), 
        max_times=(1000,1000), marker_filter=True, 
        syncs_after_marker=300, verbose=2, *arg, **kw):

    length = len(d)
    data = d
    last_marker = -syncs_after_marker
    
    sync_numbers = np.zeros((0,1), dtype=np.uint64)
    clicks = np.zeros((0,2), dtype=int)
    filtered_clicks = np.zeros((0,2), dtype=int)
    times = [ np.zeros((0,2), dtype=np.uint64), 
            np.zeros((0,2), dtype=np.uint64) ]
    filtered_times = np.zeros((0,2), dtype=int)

    if verbose >= 2:
        print
        print 'get clicks from HH events. total length:', length
        pct = 0
   
    for i in range(length):

        if verbose >= 2:
            pct1 = int(100.*float(i)/float(length))
            if pct1 > pct:
                print 'HH events > clicks.', pct, '%', \
                        time.strftime('%H:%M:%S'), ':', i
            pct = pct1

        nsync, event_time, channel, special = _decode_event(int(data[i]))
        
        if special == 1 and channel == 63:
            sync_of += 1024
            continue

        if special == 1:
            marker = channel & 15
            if marker == 1 and marker_filter:
                last_marker = sync_of + nsync
                continue
        
        if marker_filter:
            delta_syncs = sync_of + nsync - last_marker
            if delta_syncs >= syncs_after_marker:
                continue

        if event_time < min_times[channel]:
            continue

        if max_times[channel] > 0 and event_time > max_times[channel]:
            continue

        _time = np.zeros((1,2))
        _time[0,0] = sync_of+nsync
        _time[0,1] = event_time
        times[channel] = np.vstack((times[channel], _time))

    return times[0], times[1]

def _get_coincidence_clicks(t0, t1, delta=0, *arg, **kw):
    
    intersect0 = np.in1d(t0[:,0]+delta, t1[:,0])  
    if len(np.where(intersect0)[0]) == 0:
        return np.zeros((0,2)), np.zeros((0,2))

    ch0 = t0[:,:][intersect0]
    ch0[:,0] += delta
    intersect1 = np.in1d(t1[:,0], t0[:,0]+delta)
    ch1 = t1[:,:][intersect1]

    return ch0, ch1

def _get_coincidences(t0, t1, delta=0, bins=(None, None), *arg, **kw):

    verbose = kw.get('verbose', 1)

    if verbose >= 2:
        print 'Parse data for coincidences.'
    
    hist = np.array([])
    _ch0, _ch1 = _get_coincidence_clicks(t0, t1, delta=delta, *arg, **kw)

    if len(_ch0) == 0 or len(_ch1) == 0:
        return hist
    
    # first, filter for allowed times
    if bins[0] != None:
        ch0 = _ch0[ np.in1d(_ch0[:,1], bins[0]) ]
    else:
        ch0 = _ch0

    if bins[1] != None:
        ch1 = _ch1[ np.in1d(_ch1[:,1], bins[1]) ]
    else:
        ch1 = _ch1
        
    l0 = len(ch0)
    l1 = len(ch1)

    if l0 == 0 or l1 == 0:
        return hist

    # now process coincidences
    pct = 0
    for i,s in np.ndenumerate(ch0[:,0]):
        _i = i[0]
        _cond = (ch1[:,0] == s)
        if len(np.where(_cond)[0]) > 0:
            dt = ch0[i,1] - ch1[_cond,1]
            hist = np.append(hist, dt)
        
        pct1 = int(float(_i)/l0*100)
        if pct1 > pct and verbose >= 2:
            pct = pct1
            print 'delta = %d, find coincidences. %d%%' % (delta, pct)

        if verbose >= 3:
            print s
    
    return hist

def get_clicks_from_folder(path, piece_size=0, save=True,
        save_filepath='allclicks', *arg, **kw):
    """
    Extract the clicks from raw HH data.
    
    Resulting data:
        times_ch0 : 2D array, two columns; sync number in col 1, detection time
            since the sync in bins (for each click)
        times_ch1 : analogous.
            
    Required arguments:
        path : string
            the folder where the *alldata*.npz files are located

    keyword arguments:
        piece_size : int (default: 0)
            if >0, extract events piecewise from arrays of length <piece_size>.
            speeds up the process for many elements (several millions or so)
            since the for loop gets very slow with time.
            10000 seems to be a good setting.
        save : bool (default: True)
            save the resulting data (y/n)
        save_filename : string (default: 'allclicks')
            filepath of the .npz file. 
        verbose : int (default: 1)
            verbosity level. leave 1 for now.
        min_times : (int, int) (default: (0,0))
            if >0, limit events taken into account on (ch0,ch1) to those
            after bin <min_times>.
        max_times : (int, int) (default: (0,0))
            analogous.
        marker_filter : bool (default: True)
            if true, take into account only syncs that occur after a marker;
            see also syncs_after_marker.
        syncs_after_marker : int (default: 100)
            use the first <syncs_after_marker> syncs after a filter marker,
            then ignore the following until the next marker.
        """        

    verbose = kw.get('verbose', 1)   
    dat = _get_data_from_folder(path, *arg, **kw)
    
    if piece_size == 0:
        t0, t1 = _get_events(dat, *arg, **kw)
        
    else:
        i = 0
        s = np.array([])
        pcs = int(len(dat)/piece_size)
        pcs = pcs+1 if len(dat)%piece_size != 0 else pcs
        
        while i*piece_size < len(dat):
            
            if verbose >= 1:
                print 'HH events > clicks. process block %d (%d)...' % (i+1, pcs)
            
            j = i*piece_size
            
            if (i+1)*piece_size < len(dat):
                k = (i+1)*piece_size
            else:
                k = len(dat)
            
            if i == 0 or len(s) == 0:
                t0, t1 = _get_events(dat[j:k], sync_of=0, 
                        *arg, **kw)
            else:
                _t0, _t1 = _get_events(dat[j:k], sync_of=s[-1],
                        *arg, **kw)
                if len(_t0) > 0:                    
                    t0 = np.vstack((t0, _t0))
                if len(_t1) > 0:
                    t1 = np.vstack((t1, _t1))
            
            i += 1
    
    if save:
        np.savez(save_filepath, times_ch0=t0, times_ch1=t1)
    return


def plot_channel_clicks(workingpath, click_files, *arg, **kw):
    """
    plot time histograms for the clicks on both channels, from
    a list of clicks-files.
    returns the figure instance.
    args and kws get passed to the hist plot method.
    """
    ch0_clicks = np.array([], dtype=np.uint64)
    ch1_clicks = np.array([], dtype=np.uint64)

    for f in click_files:
        try:
            d = np.load(os.path.join(workingpath, f))
            t0 = d['times_ch0'].astype(np.uint64)
            t1 = d['times_ch1'].astype(np.uint64)
        except:
            print 'could not load data file %s' % f
            continue

        try:
            d.close()
        except:
            pass
        
        ch0_clicks = np.append(ch0_clicks, t0[:,1])
        ch1_clicks = np.append(ch1_clicks, t1[:,1])

    fig = plt.figure()
    
    ax1 = plt.subplot(121)
    ax1.set_yscale('log')
    plt.hist(ch0_clicks, color='b', *arg, **kw)
    plt.xlabel('bins')
    plt.ylabel('occurrences')
    plt.title('ch0 clicks')

    ax2 = plt.subplot(122)
    ax2.set_yscale('log')
    plt.hist(ch1_clicks, color='r', *arg, **kw)
    plt.xlabel('bins')
    plt.ylabel('occurrences')
    plt.title('ch1 clicks')

    return fig

def plot_click_stats(workingpath, click_files, *arg, **kw):
    """
    plots information on the clicks on both channels from a list of
    clicks-files.
    returns the figure instance.

    kw arguments:
    - tail_bins : (range, range) (default: (range(257,750), range(262,750)))
    - time_per_bin : float (default: 0.256)

    """
    tail_bins = kw.pop('tail_bins', (range(257,500), range(262,500)) )
    time_per_bin = kw.pop('time_per_bin', 0.256)

    
    clicks = np.array([], dtype=np.uint64)
    totals = np.array([], dtype=int)
    tail = np.array([], dtype=np.uint64)
    tail_totals = np.array([], dtype=int)
   
    for f in click_files:
        try:
            d = np.load(os.path.join(workingpath, f))
            t0 = d['times_ch0'].astype(np.uint64)
            t1 = d['times_ch1'].astype(np.uint64)
        except:
            print 'could not load data file %s' % f
            continue

        try:
            d.close()
        except:
            pass
        
        clicks = np.append(clicks, t0[:,1])
        clicks = np.append(clicks, t1[:,1])
        totals = np.append(totals, len(t0)+len(t1))

        tail = np.append(tail, t0[:,1][np.in1d(t0[:,1], tail_bins[0])])
        tail = np.append(tail, t1[:,1][np.in1d(t1[:,1], tail_bins[1])])
        tail_totals = np.append(tail_totals,
                len(t0[:,1][np.in1d(t0[:,1], tail_bins[0])]) + \
                len(t1[:,1][np.in1d(t1[:,1], tail_bins[1])]) )
        
    fig = plt.figure()
    
    ax1 = plt.subplot(221)
    ax1.set_yscale('log')
    _c = clicks*time_per_bin
    plt.hist(_c, color='b', bins=np.arange(int(max(_c)+0.5)+1),
            range=(0,int(max(_c)+0.5)) )
    plt.xlabel('time (ns)')
    plt.ylabel('occurrences')
    plt.title('clicks')

    ax2 = plt.subplot(222)
    plt.plot(np.arange(len(totals))+1, totals, 'bo-')
    plt.xlabel('measurement run')
    plt.ylabel('clicks')
    plt.title('clicks per measurement')

    ax3 = plt.subplot(223)
    ax3.set_yscale('log')
    _c = tail*time_per_bin
    _bins = max(tail_bins[0][-1],tail_bins[1][-1]) - \
            min(tail_bins[0][0],tail_bins[1][0]) + 1
    _bins = int(_bins*time_per_bin+0.5)
    _min = int( min(tail_bins[0][0],tail_bins[1][0])*time_per_bin+0.5 )
    _max = int( max(tail_bins[0][-1],tail_bins[1][-1])*time_per_bin+0.5 )
    plt.hist(_c, color='r', bins=_bins, range=(_min,_max))
    plt.xlabel('time (ns)')
    plt.ylabel('occurrences')
    plt.title('tail clicks')

    ax4 = plt.subplot(224)
    plt.plot(np.arange(len(tail_totals))+1, tail_totals, 'rs-')
    plt.xlabel('measurement run')
    plt.ylabel('clicks')
    plt.title('tail clicks per measurement')

    return fig


def get_clicks_from_grouped_data(workingpath, datapath='data', *arg, **kw):
    alldirs = [d for d in os.listdir(os.path.join(workingpath,datapath)) if \
            os.path.isdir(os.path.join(workingpath,datapath,d))]
    """
    In the given workingpath/datapath, get clicks from all subfolders. 
    The method used for each folder is get_clicks_from_folder, to which all
    args and kws are passed on.

    additonal kws:
    - plot_stats : bool (default: True)
    - plot_file : filename (default: click_stats.pdf)
    """

    
    verbose = kw.get('verbose', 1)
    
    for i,d in enumerate(alldirs):
        if verbose >= 1:
            print 'extract clicks from %s (%d/%d)' % (d,i+1,len(alldirs))
        
        get_clicks_from_folder(os.path.join(workingpath,datapath,d), 
                save_filepath=os.path.join(workingpath,d+'-clicks'), *arg, **kw)

    return True

def get_coincidences_from_file(clicks_file_path, save=True, 
        save_filename='coincidences', piece_size=100000, 
        bins=(None, None), *arg, **kw):
    """
    From a clicks-file, get all coincidences.

    Required arguments:
    - clicks_file_path : string
      filepath

    Keyword arguments:
    - save : bool (default: True)
      whether to save the resulting data
    - save_filename : string (default: 'coincidences')
      filename of the saved data (will be saved in the same folder where
      the clicks file is located)
    - piece_size : int (default: 100000)
      only process so many clicks at a time. speeds up things to not use
      the full data (for loop is used)
    - bins : (int, int) (default: (None, None))
      bin numbers (after sync) to accept for both channels;
      per channel this is typically something like range(start, stop)
    - deltas: [ int, ..., int ] (default: range(2,3))
      determines between which syncs to compute coincidences.
      delta = 0 means clicks on ch0, ch1 that belong to the same sync
      delta = -1 means clicks where the one on ch0 is one sync earlier, etc.
    - ret : bool (default: True)
      whether to return the result.

    Returns:
    (deltas, coincidences)
    deltas is a list of the used deltas
    coincidences is a list with coincidences for each delta (one 1d-array per
      delta), where the coincidences are specified as the time difference 
      between the ch0 and ch1 click, one per coincidence.
    The data is also saved like this.
    """

    verbose = kw.get('verbose', 1)
    deltas = kw.get('deltas', range(-2,3))
    ret = kw.get('ret', True)
    
    try:
        d = np.load(clicks_file_path)
        t0 = d['times_ch0']
        t1 = d['times_ch1']
    except:
        print 'could not load data.'
        return

    try:
        d.close()
    except:
        pass
   
    hists = []
   
    for delta in deltas:
       
        if verbose >= 1:
            print 'delta:', delta
        
        h = _get_coincidences(t0, t1, delta=delta, bins=bins, *arg, **kw)   
        hists.append(h)
        if verbose >= 1:
            print 'found %d coincidences.' % len(h)
    
    if save:
        p,f = os.path.split(clicks_file_path)
        np.savez(os.path.join(p,save_filename), deltas=np.array(deltas), 
                dts=np.array(hists))
        if verbose >= 1:
            print 'coincidences saved as %s.npz.' % save_filename
    
    if ret:
        return deltas, hists

    return True

def get_coincidences_from_files(workingpath, files, save=True, 
        save_filename='coincidences', *arg, **kw):
    """
    From a list of clicks-files in workingpath, get all coincidences.
    Gets the coincidences per file with the get_coincidences_from_file method,
    then combines into one set.
    All args and kws are passed to that function.

    exceptions for keywords:
    - plot_g2 : bool (default: True)
      when True, plot the g2 function. kws and args are passed to the g2 method.
    - bin : (int, int) (default in this function: 
        (range(257,750), range(262,750)) )

    if save is True, saves the data into one set.
    """
    
    verbose = kw.pop('verbose', 1)
    plot_g2 = kw.get('plot_g2', True)
    bins = kw.pop('bins', (range(250,450), range(255,455)))
    
    deltas = []
    hists = []

    for i,f in enumerate(files):
        if verbose >= 1:
            print 'getting coincidences from file %s (%d/%d)' % (f, i+1, len(files))        
        
        deltas, _hists = get_coincidences_from_file(os.path.join(workingpath, f), 
                save=False, ret=True, bins=bins, verbose=0, *arg, **kw)
        
        if i == 0 or len(hists) == 0:
            hists = _hists
            continue

        for i in range(len(hists)):
            hists[i] = np.append(hists[i], _hists[i])

    if save:
        np.savez(os.path.join(workingpath,save_filename), 
                deltas=np.array(deltas), dts=np.array(hists))

    if plot_g2:
        g2(data=(deltas, hists), *arg, **kw)

    return True


def g2(coincidences_file_path='', time_per_bin=0.256, delta_separation_time=200,
        binrange=(-500,500), bins=1001, data=None, *arg, **kw):
    """
    plots the g2 function from data or file.

    keyword args:
    - coincidences_file_path : filepath (default: '')
      only used if data is None
    - data : (deltas, coincidences) (default: None)
    - time_per_bin : float
      which time per bin in the measurement data
    - delta_separation_time : float
      what time between two sync pulses
    - binrange : (int, int)
      which range of bins to plot in the histogram
    - bins : int
      how many bins to use
    """
    
    if data == None:
        try:
            d = np.load(coincidences_file_path)
            deltas = d['deltas']
            dts = d['dts']
        except:
            print 'could not load data'
            return False
            
        try:
            d.close()
        except:
            pass

    else:
        deltas = data[0]
        dts = data[1]

    totalhist = np.array([])
    for d,dt in zip(deltas, dts):
        totalhist = np.append(totalhist, (dt*time_per_bin)+(d*delta_separation_time))

    fig = plt.figure()
    ax = plt.subplot(111)
    plt.hist(totalhist, bins=bins, range=binrange)
    plt.xlabel('time')
    plt.ylabel('occurences')
    ylim_old = ax.get_ylim()[1]
    ylim_new = ylim_old * 1.1
    ax.set_ylim((0,ylim_new))

    for d,dt in zip(deltas,dts):
        plt.text(d*delta_separation_time, ylim_old*1.05, '%d' % len(dt), ha='center')

###
### end method by wolfgang





### coincidence detection by lucio
### adapted by wolfgang to be able to run on full saved data set
### (and removed time information; can be done later)
def hhstyle_coincidence_2dhist_from_folder(workingpath, datapath='combineddata', 
        range_sync=750, range_g2=3900, 
        sync_period=781.25, max_pulses=100, *arg, **kw):
    """
    run lucio's original coincidence detection on the raw data.
    requires the timestamp-alldata-idx.npz files to be (renamed! see rename
    method in this module) in the path workingpath/datapath.
    """

    verbose = kw.get('verbose', 1)
    save = kw.get('save', True)
    save_filename = kw.get('save_filename', 'histogramdata')
    ret = kw.get('ret', False)


    histogram = np.zeros((range_sync,range_g2), dtype = int)
    events_t0 = np.array([])
    events_dt = np.array([])
    events_syncno_ch0 = np.array([])
    events_syncno_ch1 = np.array([])
    hist_ch0 = np.zeros(range_sync, dtype = int)
    hist_ch1 = np.zeros(range_sync, dtype = int)
    hist_ch1_long = np.zeros(range_g2, dtype = int)
    mode = 2    # mode = 0, if a click was received on channel 0, 
                #        1, if a click was received on channel 1,
                #        2, if no click was detected
    nsync_overflow=0
    ch0_sync=0
    ch0_bin=0
    ch1_sync=0
    ch1_bin=0
    idx = 0
    good_events=0
    nsync_ma1=-max_pulses
    measuring = False
    
    try:
        data = _get_data_from_folder(
                os.path.join(workingpath,datapath), *arg, **kw)
        
        length = len(data)
    except:
        raise
        return
    
    pct = 0

    for i in range(length):
        nsync, event_time, channel, special = _decode_event(int(data[i]))

        pct1 = int(float(i+1)*100./length)
        if pct1 > pct and verbose >= 1:
            pct = pct1
            print 'parse for coincidences (hh code by lucio). %d%% ...' % pct
        
        if special == 1:
            
            if channel == 63:
                nsync_overflow += 1024
            
            else:
                marker = channel & 15
                if marker == 1:
                    measuring = True
                    nsync_overflow = 0
                    nsync_ma1 = nsync
                    if (nsync_ma1==-max_pulses):
                        print 'first marker'
            
            continue

        if channel == 0:
            good_events += 1
            ch0_bin = event_time

            if nsync+nsync_overflow-nsync_ma1 > max_pulses:
                measuring = False
                mode = 2
                continue

            if measuring:
                ch0_sync = int((nsync+nsync_overflow)*sync_period)
                delta_ch0 = (ch1_sync-ch0_sync-ch0_bin) + range_g2/2
                
                if 0 <= ch0_bin < range_sync:
                    hist_ch0[ch0_bin] += 1

                if 0 <= delta_ch0 < range_g2:
                    hist_ch1_long[delta_ch0] += 1

                if mode != 1:
                    mode = 0
                    continue

                delta = range_g2/2 + (ch1_bin+ch1_sync) - (ch0_bin+ch0_sync)
                if 0 <= delta < range_g2 and ch0_bin < range_sync and \
                        ch1_bin < range_sync:
                    histogram[ch0_bin,delta] += 1
                    mode = 2
                else:
                    mode = 0

        if channel == 1:
            good_events += 1
            ch1_bin = event_time
            
            if nsync+nsync_overflow-nsync_ma1 > max_pulses:
                measuring = False
                mode = 2
                continue

            if measuring:
                ch1_sync = int((nsync+nsync_overflow)*sync_period)
                delta_ch1 = (ch1_sync-ch0_sync+ch1_bin) + range_g2/2
                
                if 0 <= ch1_bin < range_sync:
                    hist_ch1[ch1_bin] += 1
               
                if 0 <= delta_ch1 < range_g2:
                    hist_ch1_long[delta_ch1] += 1

                if mode != 0:
                    mode = 1
                    continue

                delta = range_g2/2 + (ch1_bin+ch1_sync) - (ch0_bin+ch0_sync)
                if 0 <= delta < range_g2 and ch0_bin < range_sync and \
                        ch1_bin < range_sync:
                    histogram[ch0_bin,delta] += 1
                    mode = 2
                else:
                    mode = 1

    if verbose >= 1:
        print 'Total detected coincidences in histogram: %s'%(histogram.sum())
        print 'Good events during measuring: %s'%good_events
        
    plt.figure()
    plt.imshow(histogram, vmin=0, vmax=1, cmap=cm.hot, interpolation='nearest')
    plt.colorbar()

    if save:
        np.savez(os.path.join(workingpath, save_filename), histogram=histogram,
                hist_ch0=hist_ch0, hist_ch1=hist_ch1, 
                hist_ch1_long=hist_ch1_long)

    if ret:
        return histogram, hist_ch0, hist_ch1, hist_ch1_long
    return True

# same method, but from pre-filetered events
def hhstyle_coincidence_2dhist_from_clicks(clicks_file_path, range_sync=750, range_g2=3900, 
        sync_period=781.25, max_pulses=100, *arg, **kw):

    verbose = kw.get('verbose', 1)
    
    try:
        d = load(clicks_file_path)
        t0 = d['times_ch0']
        t1 = d['times_ch1']
    except:
        print 'could not load data'
        return False
        
    try:
        d.close()
    except:
        pass

    # add channel information and combine
    l0 = len(t0)
    t0 = np.hstack((t0, zeros((l0,1), dtype=int)))
    l1 = len(t1)
    t1 = np.hstack((t1, ones((l1,1), dtype=int)))
    data = np.vstack((t0,t1))
    ordered_idxs = np.argsort(data[:,0])
    data = data[ordered_idxs,:]
    
    # start the HH algorithm from lucio
    histogram = np.zeros((range_sync,range_g2), dtype = int)
    events_t0 = np.array([])
    events_dt = np.array([])
    events_syncno_ch0 = np.array([])
    events_syncno_ch1 = np.array([])
    hist_ch0 = np.zeros(range_sync, dtype = int)
    hist_ch1 = np.zeros(range_sync, dtype = int)
    hist_ch1_long = np.zeros(range_g2, dtype = int)
    mode = 2    # mode = 0, if a click was received on channel 0, 
                #        1, if a click was received on channel 1,
                #        2, if no click was detected
    nsync_overflow=0
    ch0_sync=0
    ch0_bin=0
    ch1_sync=0
    ch1_bin=0
    idx = 0
    pct = 0

    for i,d in enumerate(data):
        sync, time, channel = int(d[0]), int(d[1]), int(d[2])

        pct1 = int(float(i+1)*100./len(data))
        if pct1 > pct and verbose >= 1:
            pct = pct1
            print 'parse for coincidences (hh code by lucio). %d%% ...' % pct
        
        if channel == 0:
            ch0_bin = time
            ch0_sync = sync*sync_period
            delta_ch0 = (ch1_sync-ch0_sync-ch0_bin) + range_g2/2
            
            if 0 <= ch0_bin < range_sync:
                hist_ch0[ch0_bin] += 1

            if 0 <= delta_ch0 < range_g2:
                hist_ch1_long[delta_ch0] += 1

            if mode != 1:
                mode = 0
                continue

            delta = range_g2/2 + (ch1_bin+ch1_sync) - (ch0_bin+ch0_sync)
            if 0 <= delta < range_g2 and ch0_bin < range_sync and \
                    ch1_bin < range_sync:
                histogram[ch0_bin,delta] += 1
                mode = 2
            else:
                mode = 0

        if channel == 1:
            ch1_bin = time
            ch1_sync = sync*sync_period
            delta_ch1 = (ch1_sync-ch0_sync+ch1_bin) + range_g2/2
            
            if 0 <= ch1_bin < range_sync:
                hist_ch1[ch1_bin] += 1
           
            if 0 <= delta_ch1 < range_g2:
                hist_ch1_long[delta_ch1] += 1

            if mode != 0:
                mode = 1
                continue

            delta = range_g2/2 + (ch1_bin+ch1_sync) - (ch0_bin+ch0_sync)
            if 0 <= delta < range_g2 and ch0_bin < range_sync and \
                    ch1_bin < range_sync:
                histogram[ch0_bin,delta] += 1
                mode = 2
            else:
                mode = 1

    if verbose >= 1:
        print 'Total detected coincidences in histogram: %s'%(histogram.sum())
        
    plt.figure()
    plt.imshow(histogram, vmin=0, vmax=1, cmap=cm.hot)
    plt.colorbar()
    
    return 
        
### some tools
def hist_2d_from_clicks(clicks_file_path, deltas=range(-2,3), delta_bins=781):
    """
    plot a 2d histogram (t_ch0-t_ch1) vs t_ch0 like in the code from lucio,
    but straight from a clicks-file. no re-binning or so included at the moment.
    """

    try:
        d = np.load(clicks_file_path)
        t0 = d['times_ch0']
        t1 = d['times_ch1']
    except:
        print 'could not load data'

    try:
        d.close()
    except:
        pass

    w = (len(deltas)+1)*delta_bins
    h = delta_bins+1
    histogram = np.zeros((w,h))
    
    for d in deltas:
        ch0,ch1 = _get_coincidence_clicks(t0,t1,delta=d)
        
        for i,s in np.ndenumerate(ch0[:,0]):
            _i = i[0]
            _cond = (ch1[:,0] == s)
            if len(where(_cond)[0]) > 0:
                dt = ch0[i,1] - ch1[_cond,1]
                dt_idx = w/2 + dt + d*delta_bins
                t0_idx = ch0[i,1]
                
                # print dt_idx, type(dt_idx)
                if type(dt_idx) != ndarray:
                    histogram[int(dt_idx), int(t0_idx)] += 1
                    continue

                for _dt_idx in dt_idx:
                    histogram[int(_dt_idx), int(t0_idx)] += 1
        
    print 'found %d coincidences' % histogram.sum()

    plt.figure()
    plt.imshow(histogram.transpose(), vmin=0, vmax=1, cmap=cm.hot)
    plt.colorbar()
    
    return True

