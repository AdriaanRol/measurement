'''
module for TPQI analysis, August 1st 2012;
author: wolfgang
'''

import os, sys, time
import shutil

import numpy as np
import matplotlib.pyplot as plt

import hht3

workingpath = ''

# prepare the folder: all indices with same amount of digits!
# NOT NEEDED ATM!
def rename(path):
    
    allfiles = os.listdir(os.path.join(workingpath, path))
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
        shutil.move(os.path.join(workingpath, path, fn), 
                os.path.join(workingpath, path, fn_new))

    return True


# coincidence detection for a single folder
# will get the coincidences for all rawdata .npz files in that folder
def coincidences_from_folder(path, ch0window=(0,500), ch1window=(0,500), *arg, **kw):
    
    npzfiles = [ f for f in os.listdir(os.path.join(workingpath, path)) \
            if ( os.path.splitext(f)[1] == '.npz' and 'alldata' in f and f[:1] != '.') ]
   
    sync_range = kw.pop('sync_range', range(1, 301))
    ret = kw.pop('ret', True)
   
    totalhist = np.array([], dtype=int)
    for i,f in enumerate(npzfiles):
        print ''
        print 'file', f

        # brute force for now: ignore the first file of each measurement.
        # if os.path.splitext(f)[0][-3:] == '-0':
        #     print 'IGNORED; FIND BETTER WAY...'
        #     continue

        base = path
        d = np.load(os.path.join(workingpath, path, f))
        raw = d['data'].astype(np.uint)
        d.close()

        data = hht3.decode(raw)
        data, ofls = hht3.filter_overflows(data)
        
        # print 'filter on timewindow'
        data = hht3.filter_timewindow(data, 0, mintime=ch0window[0], maxtime=ch0window[1])
        data = hht3.filter_timewindow(data, 1, mintime=ch1window[0], maxtime=ch1window[1])
        if len(data) == 0:
            continue

        data = hht3.filter_decreasing_syncs(data)
        if len(data) == 0:
            continue

        # print 'filter counts on markers'
        data = filter_markers(data, sync_range=sync_range)
        if len(data) == 0:
            continue

        # print 'extract coincidences'
        deltas, c = coincidences(data, *arg, **kw)
        print '* Coincidences for %s:' % f, [ len(_c) for _c in c ]
        print ''


        totalhist = add_coincidences(totalhist, c)
    
    p = os.path.join(workingpath, '%s_coincidences_syncs_%d-%d_ch0_%d-%d_ch1_%d-%d' % \
                (base, sync_range[0], sync_range[-1], ch0window[0], ch0window[1], ch1window[0], ch1window[1]))

    np.savez(p, deltas=deltas, coincidences=totalhist)
    plot_g2(deltas, totalhist, savepath=p+'.png', 
        title='%s; windows: %d-%d, %d-%d; syncs: %d-%d' % (path, 
            ch0window[0], ch0window[1], ch1window[0], ch1window[1], sync_range[0], sync_range[-1]))

    if ret:
        return deltas, totalhist


def add_coincidences(c1, c2):
    if len(c1) == 0:
        return c2
    elif len(c2) == 0:
        return c1

    for i,c in enumerate(c1):
        c1[i] = np.append(c1[i], c2[i])

    return c1

def coincidences(data, deltas=range(-3,4), *arg, **kw):
    t0, t1 = hht3.get_clicks(data)
    
    if t0.shape == (4,0) or t1.shape == (4,0):
        return deltas, [np.array([], dtype=int) for d in deltas]

    c = []
    for delta in deltas:
        c.append(_coincidences(t0.astype(int),t1.astype(int),delta))

    return deltas, c

def _coincidences(t0, t1, delta=0, *arg, **kw):
    
    hist = np.array([], dtype=int)
    ch0, ch1 = _coincidence_clicks(t0, t1, delta=delta, *arg, **kw)
    
    # now process coincidences
    pct = 0
    for i,s in np.ndenumerate(ch0[:,0]):
        _i = i[0]
        _cond = (ch1[:,0] == s)
        if len(np.where(_cond)[0]) > 0:
            dt = ch0[i,1] - ch1[_cond,1]
            hist = np.append(hist, dt)

    return hist

def _coincidence_clicks(t0, t1, delta=0, *arg, **kw):

    intersect0 = np.in1d(t0[:,0]+delta, t1[:,0])  
    if len(np.where(intersect0)[0]) == 0:
        return np.zeros((0,2)), np.zeros((0,2))

    ch0 = t0[:,:][intersect0]
    ch0[:,0] += delta
    intersect1 = np.in1d(t1[:,0], t0[:,0]+delta)
    ch1 = t1[:,:][intersect1]

    return ch0, ch1

# marker filtering
def filter_markers(data, sync_range=range(1,301), delete=True):
    data = hht3.filter_counts_on_marker(data, 1, sync_range)
    
    if len(data) > 0 and delete:
        print 'delete markers'
        data = hht3.delete_markers(data, 1)

    return data

# plotting
def plot_g2(deltas, dts, time_per_bin=0.256, delta_separation_time=200,
        binrange=(-700,700), bins=701, *arg, **kw):
    
    savepath = kw.pop('savepath', None)
    title = kw.pop('title', None)

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

    if title != None:
        plt.title(title)

    for d,dt in zip(deltas,dts):
        plt.text(d*delta_separation_time, ylim_old*1.05, '%d' % len(dt), ha='center')

    if savepath != None:
        fig.savefig(savepath)


def plot_counts_vs_time(data, rng=500.):
    
    fig = plt.figure()
    
    t0, t1 = hht3.get_click_times(data)
    h0y, h0x = np.histogram(t0, bins=rng+1, range=(0.,rng))
    h1y, h1x = np.histogram(t1, bins=rng+1, range=(0.,rng))
       
    ax = plt.subplot(121)
    ax.semilogy(h0x[:-1], h0y, 'o-', c='k', mfc='None', mec='k', label='ch0')
    ax.set_xlabel('Bins')
    ax.legend()

    ax = plt.subplot(122)
    ax.semilogy(h1x[:-1], h1y, 'o-', c='k', mfc='None', mec='k', label='ch1')
    ax.set_xlabel('Bins')
    ax.legend()
