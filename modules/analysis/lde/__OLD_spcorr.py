import os
import numpy as np
import matplotlib.pyplot as plt

from analysis.lde import hht3

DATFILEBASE = 'LDESpinPhotonCorr'
DATIDX = 0
DATIDXDIGITS = 3
ADWINFOLDER = 'adwin_lt2'
ADWINPARAMSFN = 'lde_params.npz'
ADWINDATAFN = 'lde_data.npz'


def prepare(datfolder, rawfolder, *arg, **kw):
    
    # load adwin autodata
    fn = os.path.join(datfolder, 
            ADWINFOLDER+('-%.'+str(DATIDXDIGITS)+'d') % DATIDX, 
            ADWINDATAFN)
    d = np.load(fn)
    noof_SSROs_adwin = d['get_noof_SSROs']
    noof_PLU_markers = d['get_noof_PLU_markers']
    d.close()

    # load data
    fn = os.path.join(datfolder,
         DATFILEBASE+('-%.'+str(DATIDXDIGITS)+'d.npz') % DATIDX)
    d = np.load(fn)
    SSROs_adwin = d['adwin_lt2_SSRO']
    CRs_adwin = d['adwin_lt2_CR']
    d.close()

    # load HH data
    hh_prefiltered, window1, window2 = split(rawfolder, *arg, **kw)
    hhpludat = hht3.filter_counts_on_marker(
            hh_prefiltered, 2, [-1,0])
    np.savez(os.path.join(datfolder, 'hh_prefiltered_events'),
            data=hh_prefiltered)
    np.savez(os.path.join(datfolder, 'window1_events'),
            data=window1)
    np.savez(os.path.join(datfolder, 'window2_events'),
            data=window2)
    
    # more preparations
    SSROs_adwin = SSROs_adwin[:noof_PLU_markers]
    CRs_adwin = CRs_adwin[:noof_PLU_markers]

    ### first some sanity checks
    invalid_SSROs_adwin = np.where(SSROs_adwin==-1)[0]
    
    print ''
    print 'adwin detected SSROs: %d' % noof_PLU_markers
    print '  thereof invalid: %d' % len(invalid_SSROs_adwin)
    print 'HH SSROs: %d' % len(hhpludat[
        np.logical_and(hhpludat[:,3]==1, hhpludat[:,2]==2)])
    print ''

    ### plot counts
    plot_counts_vs_time(window1, datfolder, window=1)
    plot_counts_vs_time(window2, datfolder, window=2)

    return True

def prepare_correlations(datfolder, datfile='hh_prefiltered_events.npz'):
    
    # load adwin autodata
    fn = os.path.join(datfolder, 
            ADWINFOLDER+('-%.'+str(DATIDXDIGITS)+'d') % DATIDX, 
            ADWINDATAFN)
    d = np.load(fn)
    noof_SSROs_adwin = d['get_noof_SSROs']
    noof_PLU_markers = d['get_noof_PLU_markers']
    d.close()

    # load data
    fn = os.path.join(datfolder,
         DATFILEBASE+('-%.'+str(DATIDXDIGITS)+'d.npz') % DATIDX)
    d = np.load(fn)
    SSROs_adwin = d['adwin_lt2_SSRO']
    CRs_adwin = d['adwin_lt2_CR']
    d.close()

    # HH data
    d = np.load(os.path.join(datfolder, datfile))
    hhdata = d['data']
    d.close()

    # more preparations
    SSROs_adwin = SSROs_adwin[:noof_PLU_markers]
    CRs_adwin = CRs_adwin[:noof_PLU_markers]
    hhpludat = hht3.filter_counts_on_marker(hhdata, 2, [-1,0])
    hhpludat1 = hht3.filter_counts_on_marker(hhdata, 2, [-1])
    hhpludat2 = hht3.filter_counts_on_marker(hhdata, 2, [0])

    ### some sanity checks
    invalid_SSROs_adwin = np.where(SSROs_adwin==-1)[0]

    print ''
    print 'adwin detected SSROs: %d' % noof_PLU_markers
    print '  thereof invalid: %d' % len(invalid_SSROs_adwin)
    print 'HH SSROs: %d' % len(hhpludat[
        np.logical_and(hhpludat[:,3]==1, hhpludat[:,2]==2)])
    print ''
    print 'counts + PLU: %d' % len(hhpludat[hhpludat[:,3]==0])
    print 'counts in window 1 + PLU: %d' % len(hhpludat1[hhpludat1[:,3]==0])
    print 'counts in window 2 + PLU: %d' % len(hhpludat2[hhpludat2[:,3]==0])
    
    return hhpludat, SSROs_adwin


def correlations(hhpludat, SSROs_adwin, w1_start=(0,0), w1_stop=(500,500),
        w2_start=(0,0), w2_stop=(500,500), do_plot = True, savefile='correlations.pdf'):

    # do timefilter first
    photons = hhpludat[:,3] == 0
    mrkrs = np.logical_not(photons)

    # compute actual correlations             
    windows = np.zeros(len(hhpludat[hhpludat[:,3]==1]), dtype=int)
    
    for _i, nsync in np.ndenumerate(hhpludat[hhpludat[:,3]==1,0]):        
        i = _i[0]
        w1 = hhpludat[np.logical_and(photons, hhpludat[:,0] == nsync-1)]
        w2 = hhpludat[np.logical_and(photons, hhpludat[:,0] == nsync)]

        # print w1, w2
        
        try:
            w1ch0 = w1[w1[:,2] == 0]
            w1ch0 = w1ch0[w1ch0[:,1] > w1_start[0]]
            w1ch0 = w1ch0[w1ch0[:,1] < w1_stop[0]]
            w1ch0len = len(w1ch0)
        except IndexError:
            w1ch0len = 0

        try:
            w1ch1 = w1[w1[:,2] == 1]
            w1ch1 = w1ch1[w1ch1[:,1] > w1_start[1]]
            w1ch1 = w1ch1[w1ch1[:,1] < w1_stop[1]]
            w1ch1len = len(w1ch1)
        except IndexError:
            w1ch1len = 0

        try:
            w2ch0 = w2[w2[:,2] == 0]
            w2ch0 = w2ch0[w2ch0[:,1] > w2_start[0]]
            w2ch0 = w2ch0[w2ch0[:,1] < w2_stop[0]]
            w2ch0len = len(w2ch0)
        except IndexError:
            w2ch0len = 0

        try:
            w2ch1 = w2[w2[:,2] == 1]
            w2ch1 = w2ch1[w2ch1[:,1] > w2_start[1]]
            w2ch1 = w2ch1[w2ch1[:,1] < w2_stop[1]]
            w2ch1len = len(w2ch1)
        except IndexError:
            w2ch1len = 0

        w1len = w1ch0len + w1ch1len
        w2len = w2ch0len + w2ch1len

        # print w1len, w2len
        
        if w1len == 1 and w2len == 0:
            windows[i] = 1
        elif w2len == 1 and w1len == 0:
            windows[i] = 2
        else:
            pass

    corr = np.zeros(4)
    total = len(windows[windows>0])
    for _i, w in np.ndenumerate(windows):
        i = _i[0]
        if w == 0 or SSROs_adwin[i]<0:
            continue
        corr[(w-1)*2**1 + int(SSROs_adwin[i]>0)*2**0] += 1

    # corr = corr/float(total)
    if do_plot:
        fig = plt.figure()
        plt.bar(np.arange(4)-0.4, corr)
        plt.xticks([])
        plt.ylabel('fraction of events')
        plt.text(0, 1, "Window 1\n0 cts", ha='center', va='bottom')
        plt.text(1, 1, "Window 1\n>0 cts", ha='center', va='bottom')
        plt.text(2, 1, "Window 2\n0 cts", ha='center', va='bottom')
        plt.text(3, 1, "Window 2\n>0 cts", ha='center', va='bottom')
        fig.savefig(savefile, format='pdf')

    return corr

def SSRO_correct(corr, F0, F1, F0err = 0.01, F1err = 0.01):
    w1 = corr[:2].copy()
    w2 = corr[2:].copy()
    w1 = w1[::-1]
    w2 = w2[::-1]
    
    w1total = np.sum(w1)
    w2total = np.sum(w2)
    w1 /= float(w1total)
    w2 /= float(w2total)

    norm = 1./(F0+F1-1.)
    w1staterr = np.sqrt(w1*(1.-w1)/float(w1total))
    w2staterr = np.sqrt(w2*(1.-w2)/float(w2total))
   
    w1p0 = w1[1]
    w1p1 = w1[0]
    w2p0 = w2[1]
    w2p1 = w2[0]

    w1ms0err = np.sqrt( 
            (norm**2 * (-w1p1 + F0*(w1p0+w1p1)) * F1err)**2 +\
            (norm**2 * (w1p0 - F1*(w1p0+w1p1)) * F0err)**2 +\
            (norm * (F1 - 1) * w1staterr[1])**2 +\
            (norm * F1 * w1staterr[0])**2
            )
    w1ms1err = w1ms0err
    w1err = np.array([w1ms0err, w1ms1err])

    w2ms0err = np.sqrt( 
            (norm**2 * (-w2p1 + F0*(w2p0+w2p1)) * F1err)**2 +\
            (norm**2 * (w2p0 - F1*(w2p0+w2p1)) * F0err)**2 +\
            (norm * (F1 - 1) * w2staterr[1])**2 +\
            (norm * F1 * w2staterr[0])**2
            )
    w2ms1err = w2ms0err
    w2err = np.array([w2ms0err, w2ms1err])

    corrmat = 1./(F0*F1 - (1.-F1)*(1.-F0)) * np.array([[F1, F1-1.],[F0-1., F0]])
    
    return np.dot(corrmat, w1.reshape(2,1)).reshape(-1), \
            np.dot(corrmat, w2.reshape(2,1)).reshape(-1), \
            w1err, w2err

def plot_counts_vs_time(windowdata, savepath, window=1, bins=500):
    
    gated = hht3.filter_counts_on_marker(windowdata, 2, [window-2])
    
    print 'length of window data = ',len(windowdata)

    fig = plt.figure()
    
    t0, t1 = hht3.get_click_times(windowdata)
    h0y, h0x = np.histogram(t0, bins=bins)
    h1y, h1x = np.histogram(t1, bins=bins)
    
    g_t0, g_t1 = hht3.get_click_times(gated)
    g_h0y, g_h0x = np.histogram(g_t0, bins=bins)
    g_h1y, g_h1x = np.histogram(g_t1, bins=bins)
    
    ax = plt.subplot(121)
    ax.semilogy(g_h0x[:-1], g_h0y, color = 'g', label='ch0 gated')
    ax.semilogy(h0x[:-1], h0y, label='ch0', color = 'b')
    ax.set_xlabel('Bins')
    ax.legend()

    ax = plt.subplot(122)
    ax.semilogy(h1x[:-1], h1y, label='ch1')
    ax.semilogy(g_h1x[:-1], g_h1y, label='ch1 gated')
    ax.set_xlabel('Bins')
    ax.legend()

    plt.suptitle('Clicks after optical pulse, window %d' % window)
    
    fig.savefig(os.path.join(savepath,'histogram_window%s.pdf'%window))

    np.savez(os.path.join(savepath, 'histogram_window%s.npz'%window), 
        window_number = window, 
        window_data = windowdata, 
        ch0 = h0y, 
        ch0_xaxis = h0x[:-1],
        ch0_gated = g_h0y,
        ch0_gated_xaxis = g_h0x[:-1],
        ch1 = h1y, 
        ch1_xaxis = h1x[:-1],
        ch1_gated = g_h1y,
        ch1_gated_xaxis = g_h1x[:-1])

    return True

def filter_PLU(data, mchan=2):
    filtered = hht3.filter_counts_on_marker(data, mchan, delta_syncs=[0])
    
    return filtered

# in case of large data sets, we need to treat data in chunks;
# can combine back after reducing to some reasonable size
def split(rawfolder, file_contains='LDE', chunk_size=50, *arg, **kw):
    
    allfiles = [ f for f in os.listdir(rawfolder) if file_contains in f ]
    lastidx = len(allfiles)

    # we don't have too much data left over, so can use this approach
    finaldata = np.zeros((0,4))
    window1data = np.zeros((0,4))
    window2data = np.zeros((0,4))

    ch0maxtime = kw.pop('ch0maxtime', 500)
    ch1maxtime = kw.pop('ch1maxtime', 500)
    
    i = 0
    k = 0
    ofls = 0
    while i < lastidx:
        j = i + chunk_size
        if j > lastidx:
            j = lastidx
        
        print ''
        print 'get data from %d to %d' % (i,j)
        print ''

        decoded = decode_files(rawfolder, (i,j), file_contains)
        data, ofls = hht3.filter_overflows(decoded, ofl_offset=ofls)
        data = hht3.filter_timewindow(data, 0, mintime=0, 
                maxtime=ch0maxtime)
        data = hht3.filter_timewindow(data, 1, mintime=0, 
                maxtime=ch1maxtime)        
        
        data = hht3.filter_counts_on_marker(data, 1, [1,2])                
        w1data = hht3.filter_counts_on_marker(data, 1, [1])
        w2data = hht3.filter_counts_on_marker(data, 1, [2])
        
        data = hht3.delete_markers(data, 1)
        w1data = hht3.delete_markers(w1data, 1)
        w2data = hht3.delete_markers(w2data, 1)

        finaldata = np.vstack((finaldata, data))
        window1data = np.vstack((window1data, w1data))
        window2data = np.vstack((window2data, w2data))

        print 'length after basic filtering: %d' % (len(data))

        i=j
        k+=1

    return finaldata, window1data, window2data

def decode_files(rawfolder, file_range, file_contains='LDE'):
    dat = hht3.get_data_from_folder(rawfolder, 
                file_contains=file_contains, file_range=file_range,
                verbose=0)
    return hht3.decode(dat)
