import os
import numpy as np
import matplotlib.pyplot as plt
from analysis import fit, common
from analysis.lde import hht3

setup = 'lt1'

DATFILEBASE = 'LDE'
DATIDX = 0
DATIDXDIGITS = 3
ADWINLT1FOLDER = 'adwin_lt1'
ADWINLT2FOLDER = 'adwin_lt2'
ADWINPARAMSFN = 'lde_params.npz'
ADWINDATAFN = 'lde_data.npz'

def set_setup(s):
    global setup
    global ADWINFOLDER
    
    setup = s
    ADWINFOLDER = ADWINLT2FOLDER if setup == 'lt2' else ADWINLT1FOLDER

    return

def correct_ssro_mismatch(SSROs_adwin_LT1, SSROs_adwin_LT2, noof_PLU_markers,
        noof_SSROs_adwin_LT1, noof_SSROs_adwin_LT2, CR_adwin_LT1=None):
    added_idxs = 0
    bad_idx = list() #index where 
    for i in range(noof_PLU_markers):
        if (SSROs_adwin_LT2[i]==-1):
            added_idxs += 1
            bad_idx.append(i)
            SSROs_adwin_LT1 = np.insert(SSROs_adwin_LT1,i,-1)
            if CR_adwin_LT1 != None:
                CR_adwin_LT1 = np.insert(CR_adwin_LT1,i,-1)
    
    print 'Detected missed PLU markers at SSRO LT2 array for indexes: ',bad_idx
    print 'Compensating SSRO mismatch:'
    print '\tADwin LT2 received PLU markers: ',noof_PLU_markers
    print '\tADwin LT2 performed SSROs: ',noof_SSROs_adwin_LT2
    print '\tADwin LT1 performed SSROs: ',noof_SSROs_adwin_LT1
    print 'Finished adding -1 to SSRO LT1 data. Added %s element.'%(added_idxs)
    
    if CR_adwin_LT1 == None:
        return SSROs_adwin_LT1, added_idxs
    return SSROs_adwin_LT1, CR_adwin_LT1, added_idxs

def prepare(datfolder, rawfolder, *arg, **kw):
    global setup

    #############################
    #### LOAD ADWIN LT1 DATA ####
    #############################

    # load adwin autodata 
    fn = os.path.join(datfolder, 
            ADWINLT1FOLDER+('-%.'+str(DATIDXDIGITS)+'d') % DATIDX, 
            ADWINDATAFN)
    d = np.load(fn)
    
    noof_SSROs_adwin_LT1 = d['get_noof_SSROs']
    noof_SSRO_triggers_LT1 = d['get_noof_SSRO_triggers']
    d.close()


    #############################
    #### LOAD ADWIN LT2 DATA ####
    #############################
    
    sn = os.path.join(datfolder, 
        ADWINLT2FOLDER+('-%.'+str(DATIDXDIGITS)+'d') % DATIDX, 
        ADWINDATAFN)
    s = np.load(sn)

    noof_PLU_markers = s['get_noof_PLU_markers']
    noof_SSROs_adwin_LT2 = s['get_noof_SSROs']
    s.close()

    ############################################
    ### LOADING SSRO DATA###
    ############################################ 

    fn = os.path.join(datfolder,
         DATFILEBASE+('-%.'+str(DATIDXDIGITS)+'d.npz') % DATIDX)
    d = np.load(fn)
    
    SSROs_adwin_LT1 = d['adwin_lt1_SSRO']
    SSROs_adwin_LT2 = d['adwin_lt2_SSRO']

    ############################################
    ### COMPENSATING A MISMATCH IN SSRO DATA ###
    ############################################ 
    #filling up SSROs_adwin_lt1 with -1 where LT2 missed a PLU

    SSROs_adwin_LT1, added_idxs = correct_ssro_mismatch(SSROs_adwin_LT1, 
            SSROs_adwin_LT2, noof_PLU_markers,noof_SSROs_adwin_LT1, 
            noof_SSROs_adwin_LT2)
    
    ######################################
    ######################################
    ######################################    
    
    if setup == 'lt2':
        CRs_adwin = d['adwin_lt2_CR']
    else:
        CRs_adwin = d['adwin_lt1_CR']
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
    SSROs_adwin_LT1 = SSROs_adwin_LT1[:noof_SSRO_triggers_LT1+added_idxs]
    SSROs_adwin_LT2 = SSROs_adwin_LT2[:noof_PLU_markers]
    if setup == 'lt1':
        CRs_adwin = CRs_adwin[:noof_SSRO_triggers_LT1]
    
    ######################################
    ######################################
    ######################################    
    
    print 'PLU markers on adwin lt2:', noof_PLU_markers
    
    print '\nLength of ADwin LT1 SSRO array after addition: '\
            , len(SSROs_adwin_LT1)
    print 'Length of ADwin LT2 SSRO array: ', len(SSROs_adwin_LT2)

    ######################################
    ######################################
    ######################################    

    ### first some sanity checks
    invalid_SSROs_adwin = np.where(SSROs_adwin_LT1==-1)[0] \
            if setup =='lt1' else np.where(SSROs_adwin_LT2==-1)[0]
    
    print ''
    print 'adwin detected SSROs: %d' % \
        (noof_SSRO_triggers_LT1 if setup=='lt1' else noof_PLU_markers)
    
    print '  thereof invalid: %d' % len(invalid_SSROs_adwin)
    
    print 'HH SSROs: %d' % len(hhpludat[
        np.logical_and(hhpludat[:,3]==1, hhpludat[:,2]==2)])
    print ''

    ### plot counts
    if(kw.get('do_plot',False)):
        plot_counts_vs_time(window1, datfolder, window=1)
        plot_counts_vs_time(window2, datfolder, window=2)

    ret = SSROs_adwin_LT1 if setup=='lt1' else SSROs_adwin_LT2
    return ret

def prepare_correlations(datfolder, datfile='hh_prefiltered_events.npz'):
    
    # HH data
    d = np.load(os.path.join(datfolder, datfile))
    hhdata = d['data']
    d.close()
    hhpludat = hht3.filter_counts_on_marker(hhdata, 2, [-1,0])
    hhpludat1 = hht3.filter_counts_on_marker(hhdata, 2, [-1])
    hhpludat2 = hht3.filter_counts_on_marker(hhdata, 2, [0])

    ### some sanity checks
    print ''
    print 'HH SSROs: %d' % len(hhpludat[
        np.logical_and(hhpludat[:,3]==1, hhpludat[:,2]==2)])
    print ''
    print 'counts + PLU: %d' % len(hhpludat[hhpludat[:,3]==0])
    print 'counts in window 1 + PLU: %d' % len(hhpludat1[hhpludat1[:,3]==0])
    print 'counts in window 2 + PLU: %d' % len(hhpludat2[hhpludat2[:,3]==0])
    
    return hhpludat

def correlations(hhpludat, SSROs_adwin, w1_start=(0,0), w1_stop=(700,700),
        w2_start=(0,0), w2_stop=(700,700), do_plot = True, savefile='correlations.png'):

    # do timefilter first
    photons = hhpludat[:,3] == 0
    mrkrs = np.logical_not(photons)

    # compute actual correlations             
    windows = np.zeros(len(hhpludat[hhpludat[:,3]==1]), dtype=int)
    idx = list()

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

        idx.append(i)

    if do_plot:
        print 'Plotting valid SSROs...'
        valid_ssro = SSROs_adwin[idx]
        print '\tMean counts per RO: %s'%(np.mean(valid_ssro))
        fig2 = plt.figure()
        plt.hist(valid_ssro, bins = max(valid_ssro))
        plt.xlabel('Number of counts')
        plt.ylabel('Occurrences')
        plt.title('Histogram of time-filtered SSRO events')
        fig2.savefig('valid_ssros.png')

    corr = np.zeros(4)
    total = len(windows[windows>0])
    #print len(windows)
    #print 'Total = ',total
    print 'SSROs in data:',len(SSROs_adwin)
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
        
        y = plt.ylim()[1]*0.9
        plt.text(0, y, corr[0], ha='center', va='top')
        plt.text(1, y, corr[1], ha='center', va='top')
        plt.text(2, y, corr[2], ha='center', va='top')
        plt.text(3, y, corr[3], ha='center', va='top')

        fig.savefig(savefile)

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

def plot_counts_vs_time(windowdata, savepath, window=1, bins=800):
    
    gated = hht3.filter_counts_on_marker(windowdata, 2, [window-2])
    
    print 'length of window data = ',len(windowdata)

    fig = plt.figure()
    
    t0, t1 = hht3.get_click_times(windowdata)
    h0y, h0x = np.histogram(t0, bins=bins, range=(0,bins-1))
    h1y, h1x = np.histogram(t1, bins=bins, range=(0,bins-1))
    
    g_t0, g_t1 = hht3.get_click_times(gated)
    g_h0y, g_h0x = np.histogram(g_t0, bins=bins, range=(0,bins-1))
    g_h1y, g_h1x = np.histogram(g_t1, bins=bins, range=(0,bins-1))
    
    ax = plt.subplot(121)
    if (sum(g_h0y) != 0): 
        ax.semilogy(g_h0x[:-1], g_h0y, color = 'g', label='ch0 gated')
    else:
        print 'No gated clicks in the first window!' 

    if (sum(h0y) != 0):
        ax.semilogy(h0x[:-1], h0y, label='ch0', color = 'b')
        ax.set_xlabel('Bins')
        ax.legend()
    
    ax = plt.subplot(122)
    if (sum(g_h1y) != 0):
        ax.semilogy(g_h1x[:-1], g_h1y, label='ch1 gated')
    else:
        print 'No gated clicks in the second window!' 

    if (sum(h1y) != 0):
        ax.semilogy(h1x[:-1], h1y, label='ch1')
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

    return h1y#True

def filter_PLU(data, mchan=2):
    filtered = hht3.filter_counts_on_marker(data, mchan, delta_syncs=[0])
    
    return filtered

# in case of large data sets, we need to treat data in chunks;
# can combine back after reducing to some reasonable size
def split(rawfolder, file_contains='LDE',print_status=False, *arg, **kw):
    
    allfiles = [ f for f in os.listdir(rawfolder) if file_contains in f and \
            f[:1] != '.' and f[-4:] == '.npz' ]
    lastidx = len(allfiles)

    # we don't have too much data left over, so can use this approach
    finaldata = np.zeros((0,4), dtype=np.uint)
    window1data = np.zeros((0,4), dtype=np.uint)
    window2data = np.zeros((0,4), dtype=np.uint)

    ch0maxtime = kw.pop('ch0maxtime', 700)
    ch1maxtime = kw.pop('ch1maxtime', 700)
    
    sync_of = 0
    for i,f in enumerate(allfiles):
        if print_status:
            print 'file %d (%d) ...' % (i+1, len(allfiles))
        
        fp = os.path.join(rawfolder, f)
        data = hht3.data_from_file(fp, ch0_lastbin=ch0maxtime, 
                ch1_lastbin=ch1maxtime, *arg, **kw)
        
        if len(data) == 0:
            continue

        data[:,0] += sync_of + 100
        sync_of = data[-1,0] + 1

        data = hht3.filter_counts_on_marker(data, 1, [1,2])
        if len(data) == 0:
            continue
        
        w1data = hht3.filter_counts_on_marker(data, 1, [1])
        w2data = hht3.filter_counts_on_marker(data, 1, [2])
        
        data = hht3.delete_markers(data, 1)
        w1data = hht3.delete_markers(w1data, 1)
        w2data = hht3.delete_markers(w2data, 1)

        finaldata = np.vstack((finaldata, data))
        window1data = np.vstack((window1data, w1data))
        window2data = np.vstack((window2data, w2data))

    return finaldata, window1data, window2data
load_hhdata = split

def barplot_correlations(datfolder, correlations, F0, F1, F0err, F1err):

    a = correlations[[0,1]]/float(sum(correlations[[0,1]]))
    b = correlations[[2,3]]/float(sum(correlations[[2,3]]))

    corrected = SSRO_correct(correlations, F0, F1, F0err, F1err)

# corrected: first element: 

    print 'corrected first window:',corrected[0]
    print 'corrected second window:',corrected[1]

    def num2str(num, precision): 
        return "%0.*f" % (precision, num)

    alpha = 0.5
    text_offset = 0.02

    figure2 = plt.figure(figsize = (12,8))
    plt.subplot(121)
    plt.title('Uncorrected')
    plt.bar(np.arange(2), a[::-1], color = 'g', align = 'center', 
            alpha = alpha, label = 'first window')
    plt.bar(np.arange(2,4),b[::-1], color = 'r', align = 'center', 
            alpha = alpha,label = 'second window')
    plt.legend(shadow = True, fancybox = True, loc = 3)
    plt.ylabel('Probability')
    plt.xticks([0,1,2,3],['$m_s = 0$','$m_s = -1$','$m_s = 0$','$m_s = -1$'])
    plt.ylim([0,1])
    for k in range(0,4):
        if k < 2:
            plt.text(k,a[::-1][k]+text_offset, 
                    num2str(a[::-1][k],2), 
                    ha = 'center', va = 'bottom')
        else:
            plt.text(k,b[::-1][k-2]+text_offset, 
                    num2str(b[::-1][k-2],2), 
                    ha = 'center', va = 'bottom')

    plt.subplot(122)
    plt.title('Corrected for read-out')
    plt.bar(np.arange(2), corrected[0], yerr=corrected[2], 
            color = 'g', ecolor='k',
            align = 'center', lw=1,
            label = 'first window')
    plt.bar(np.arange(2,4),corrected[1], yerr=corrected[3], 
            color = 'r', ecolor='k',
            align = 'center', lw=1,
            label = 'second window')
    plt.legend(shadow = True, fancybox = True, loc = 3)
    plt.ylabel('Probability')
    plt.xticks([0,1,2,3],['$m_s = 0$','$m_s = -1$','$m_s = 0$','$m_s = -1$'])
    plt.ylim([0,1])
    for k in range(0,4):
        if k < 2:
            plt.text(k,corrected[0][k]+text_offset, 
                    num2str(corrected[0][k],2), 
                    ha = 'center', va = 'bottom')
        else:
            plt.text(k,corrected[1][k-2]+text_offset, 
                    num2str(corrected[1][k-2],2), 
                    ha = 'center', va = 'bottom')


    if not os.path.exists(os.path.join(datfolder,'figures')):
        os.makedirs(os.path.join(datfolder,'figures'))

    figure2.savefig(os.path.join(datfolder,'figures','correlation_diagram.png'))
    
    raw_pops = dict()
    raw_pops['w1ms0'] = a[::-1][0]
    raw_pops['w1ms1'] = a[::-1][1]
    raw_pops['w2ms0'] = b[::-1][0]
    raw_pops['w2ms1'] = b[::-1][1]

    corr_pops = dict()
    corr_pops['w1ms0'] = corrected[0][0]
    corr_pops['w1ms1'] = corrected[0][1]
    corr_pops['w2ms0'] = corrected[1][0]
    corr_pops['w2ms1'] = corrected[1][1]
    corr_pops['w1ms0_err'] = corrected[2][0]
    corr_pops['w1ms1_err'] = corrected[2][1]
    corr_pops['w2ms0_err'] = corrected[3][0]
    corr_pops['w2ms1_err'] = corrected[3][1]

    F = dict()
    F['F0'] = F0
    F['F1'] = F1
    F['F0_err'] = F0err
    F['F1_err'] = F1err

    np.savez(os.path.join(datfolder, 'correlations.npz'),
            raw = raw_pops, corrected = corrected, 
            corr_pops = corr_pops, F = F)

    return 

def find_nearest(array,value):
    idx=(np.abs(array-value)).argmin()
    return idx

def num2str(num, precision): 
    return "%0.*f" % (precision, num)


def plot_crs(setup, datfolder):

    #################################################
    ####### PLOT THE CR HISTS #######################
    #################################################

    pct_passed_before_lde_lt1 = 100
    pct_passed_after_lde_lt1 = 100
    pct_passed_before_lde_lt2 = 100
    pct_passed_after_lde_lt2 = 100

    print 'Analyzing CR events...'

    files = os.listdir(datfolder)

    for f in files:
        if ('LDE' in f) and ('.npz' in f):
            datafile = f
            break

    df = np.load(os.path.join(datfolder,datafile))

    #list all the different cr instances
    threshold_probe_lt1 = int(df['adwin_lt1_pars'][\
            np.where(df['adwin_lt1_pars']=='set_CR_probe')[0][0]][1])
    threshold_preselect_lt1 = int(df['adwin_lt1_pars'][\
            np.where(df['adwin_lt1_pars']=='set_CR_preselect')[0][0]][1])
    threshold_probe_lt2 = int(df['adwin_lt2_pars'][\
            np.where(df['adwin_lt2_pars']=='set_CR_probe')[0][0]][1])
    threshold_preselect_lt2 = int(df['adwin_lt2_pars'][\
            np.where(df['adwin_lt2_pars']=='set_CR_preselect')[0][0]][1])

    print 'Thresholds were:\n\tLT1 before: %s\t\tLT2 before: %s\n\tLT1 after: %s\t\tLT2 after: %s'%(threshold_preselect_lt1,threshold_preselect_lt2,threshold_probe_lt1,threshold_probe_lt2)

    CR_after_lde_lt1 = df['adwin_lt1_CRhist_first']
    CR_before_lde_lt1 = df['adwin_lt1_CRhist']-CR_after_lde_lt1
    CR_after_SSRO_lt1 = df['adwin_lt1_CR']
    CR_after_SSRO_lt1 = CR_after_SSRO_lt1[CR_after_SSRO_lt1!=-1]

    CR_after_lde_lt2 = df['adwin_lt2_CRhist_first']
    CR_before_lde_lt2 = df['adwin_lt2_CRhist']-CR_after_lde_lt2
    CR_after_SSRO_lt2 = df['adwin_lt2_CR']
    CR_after_SSRO_lt2 = CR_after_SSRO_lt2[CR_after_SSRO_lt2!=-1]

    noof_counts = np.arange(0,100)

    #normalize the CR data
    lt1_empty = False
    lt2_empty = False

    if setup == 'lt1':
        if sum(CR_after_lde_lt1) == 0 or sum(CR_before_lde_lt1) == 0 or \
                sum(CR_after_SSRO_lt1) == 0:
            print 'Warning: empty histogram detected for LT1!!'
            lt1_empty = True
    if setup == 'lt2': 
        if sum(CR_after_lde_lt2) == 0 or sum(CR_before_lde_lt2) == 0 or \
                sum(CR_after_SSRO_lt2) == 0:
            print 'Warning: empty histogram detected for LT2!!'
            lt2_empty = True


    if not(lt1_empty):
        if setup == 'lt1':
            CR_after_lde_lt1 = CR_after_lde_lt1/float(sum(CR_after_lde_lt1))
            CR_before_lde_lt1 = CR_before_lde_lt1/float(sum(CR_before_lde_lt1))
           
            pct_passed_after_lde_lt1 = np.sum(CR_after_lde_lt1[noof_counts>=\
                    threshold_probe_lt1])*100
            pct_passed_before_lde_lt1 = np.sum(CR_before_lde_lt1[noof_counts>=\
                    threshold_preselect_lt1])*100
    if lt1_empty:
        CR_after_lde_lt1 = CR_before_lde_lt1 = np.zeros(len(noof_counts))
        pct_passed_after_lde_lt1 = pct_passed_before_lde_lt1 = 0

    if not(lt2_empty):
        if setup == 'lt2':
            CR_after_lde_lt2 = CR_after_lde_lt2/float(sum(CR_after_lde_lt2))
            CR_before_lde_lt2 = CR_before_lde_lt2/float(sum(CR_before_lde_lt2))
          
            pct_passed_after_lde_lt2 = sum(CR_after_lde_lt2[noof_counts>=\
                    threshold_probe_lt2])*100
            pct_passed_before_lde_lt2 = sum(CR_before_lde_lt2[noof_counts>=\
                    threshold_preselect_lt2])*100
    if lt2_empty:
         CR_after_lde_lt2 = CR_before_lde_lt2 = np.zeros(len(noof_counts))
         pct_passed_after_lde_lt2 = pct_passed_before_lde_lt2 = 0

    ###########################
    ### CR plots of LT1 #######
    ###########################

    alpha = 1

    figure5 = plt.figure(figsize = (16.,12.))

    plt.subplot(321)
    plt.title('Before LDE sequence (passed: '\
            +num2str(pct_passed_before_lde_lt1,0)+'%)')
    plt.bar(noof_counts,
            CR_before_lde_lt1, 
            color = '#4682B4', alpha = alpha, align = 'center', 
            edgecolor = 'None', capsize = 5, linewidth = 0.2)
    plt.ylim(0,1.1*max(CR_before_lde_lt1))
    plt.xlim(-0.6,70)

    plt.subplot(323)
    if setup == 'lt1' and not(lt1_empty):
        fit_result = fit.fit1d(noof_counts[np.arange(1,len(noof_counts)-1)], 
                CR_after_lde_lt1[np.arange(1,len(noof_counts)-1)], 
                common.fit_gauss, 0, max(CR_after_lde_lt1), 
                find_nearest(CR_after_lde_lt1,max(CR_after_lde_lt1)), 
                5, newfig = False, do_plot=True, plot_fitresult = True, 
                plot_fitonly = True, do_print = False, ret = True, 
                plot_fitparams_xy = (0.31, 0.5), 
                color = 'r', linewidth = 1.5)


        if fit_result != None:
            x0_lt1 = fit_result[0]['params_dict']['x0']
        else:
            x0_lt1 = 0

    plt.title('After LDE sequence (passed: '\
            +num2str(pct_passed_after_lde_lt1,0)+'%)')
    
    plt.bar(noof_counts,
            CR_after_lde_lt1, 
            color = '#4682B4', alpha = alpha, align = 'center', 
            edgecolor = 'None', capsize = 5, linewidth = 0.2)

    plt.ylabel('Fraction of occurrences')
    plt.xlim(-0.6,70)
    plt.ylim(0,1.1*max(CR_after_lde_lt1))


    plt.subplot(325)
    plt.title('CR counts after SSRO')
    if setup == 'lt1' and not(lt1_empty):
        t = plt.hist(CR_after_SSRO_lt1, bins = int(max(CR_after_SSRO_lt1)), 
                color = '#4682B4', alpha = alpha, edgecolor = 'k',
                linewidth = 0.2, rwidth = 0.85)
        plt.ylim(0,1.1*max(t[0]))
    
    plt.xlim(-0.6,70)
    plt.xlabel('Number of counts')


    #########################
    #### CR plots of LT2 ####
    #########################

    plt.subplot(322)
    if setup == 'lt2':
        plt.title('Before LDE sequence (passed: '\
              +num2str(pct_passed_before_lde_lt2,0)+'%)')
    plt.bar(noof_counts,
            CR_before_lde_lt2, 
            color = '#4B0082', alpha = alpha, align = 'center', 
            edgecolor = 'None', capsize = 5, linewidth = 0.2)
    plt.ylabel('Fraction of occurrences')
    plt.xlim(-0.6,50)
    plt.ylim(0,1.1*max(CR_before_lde_lt2))

    plt.subplot(324)
    if setup == 'lt2' and not(lt2_empty):
        fit_result = fit.fit1d(noof_counts[np.arange(1,len(noof_counts)-1)], 
            CR_after_lde_lt2[np.arange(1,len(noof_counts)-1)], 
            common.fit_gauss, 0, max(CR_after_lde_lt2), np.mean(CR_after_lde_lt2), 
            5, newfig = False, do_plot=True, plot_fitresult = True, 
            plot_fitonly = True, do_print = False, ret = True, 
            plot_fitparams_xy = (0.7, 0.5), color = 'r', linewidth = 1.5)

        if fit_result != None:
            x0_lt2 = fit_result[0]['params_dict']['x0']
        else:
            x0_lt2 = 0
      
    plt.title('After LDE sequence (passed: '\
            +num2str(pct_passed_after_lde_lt2,0)+'%)')
    plt.bar(noof_counts,
            CR_after_lde_lt2, 
            color = '#4B0082', alpha = alpha, align = 'center', 
            edgecolor = 'None', capsize = 5, linewidth = 0.2)
    plt.ylabel('Fraction of occurrences')
    plt.xlim(-0.6,50)
    plt.ylim(0,1.1*max(CR_after_lde_lt2))

    plt.subplot(326)
    plt.title('CR counts after SSRO')
    if setup == 'lt2' and not(lt2_empty):
        t = plt.hist(CR_after_SSRO_lt2, bins = int(max(CR_after_SSRO_lt2)), 
                color = '#4B0082', alpha = alpha, edgecolor = 'k',
                linewidth = 0.2, rwidth = 0.85)
        plt.ylim(0,1.1*max(t[0]))

    plt.xlabel('Number of counts')
    plt.ylabel('Fraction of occurrences')
    plt.xlim(-0.6,50)
    
    if not os.path.exists(os.path.join(datfolder,'figures')):
        os.makedirs(os.path.join(datfolder,'figures'))

    figure5.savefig(os.path.join(datfolder,'figures', 'cr_checks.png'))
    figure5.savefig(os.path.join(datfolder,'figures', 'cr_checks.pdf'))
    
    df.close()

    print 'Done!'

def plot_tail(datfolder, w1_starts, w2_starts, w1_stops, w2_stops):

    #################################################
    ####### PLOT THE TAIL ###########################
    #################################################

    data_w1 = np.load(os.path.join(datfolder,'histogram_window1.npz'))
    data_w2 = np.load(os.path.join(datfolder,'histogram_window2.npz'))
    lde_file = np.load(os.path.join(datfolder,'LDE-000.npz'))

    double_clicks = 0

    noof_starts = int(lde_file['adwin_lt2_pars'][np.where(lde_file['adwin_lt2_pars'] \
            == 'get_noof_seq_starts')[0][0]][1])
    noof_pulses_in_seq = 300.

    #### WINDOW 1
    ch0 = data_w1['ch0']
    ch0_xaxis = data_w1['ch0_xaxis']
    ch0_gated = data_w1['ch0_gated']
    ch0_gated_xaxis = data_w1['ch0_gated_xaxis']

    ch1 = data_w1['ch1']
    ch1_xaxis = data_w1['ch1_xaxis']
    ch1_gated = data_w1['ch1_gated']
    ch1_gated_xaxis = data_w1['ch1_gated_xaxis']

    #TAIL ANALYSIS
    w1ch0_tailph = sum(ch0[np.logical_and(ch0_xaxis > w1_starts[0], 
        ch0_xaxis < w1_starts[0]+int(60./0.256))])
    w1ch1_tailph = sum(ch1[np.logical_and(ch1_xaxis > w1_starts[1], 
        ch1_xaxis < w1_starts[1]+int(60./0.256))])

    print '\n===== WINDOW 1 ====='
    print '*    CH0: single clicks in tail region (60 ns): %s'%(w1ch0_tailph)
    print '*    CH1: single clicks in tail region (60 ns): %s'%(w1ch1_tailph)
    
    figure3 = plt.figure()
    ax = plt.subplot(121)
    ax.semilogy(ch0_xaxis*0.256, ch0, '-', label='ch0', color = 'k')
    ax.semilogy(ch0_gated_xaxis*0.256, ch0_gated, '.', label='ch0 gated', color = 'g')
    ax.semilogy(np.ones(2)*w1_starts[0]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.semilogy(np.ones(2)*w1_stops[0]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.set_xlabel('Time (ns)')
    ax.legend()

    ax = plt.subplot(122)
    ax.semilogy(ch1_xaxis*0.256, ch1, '-', label='ch1', color = 'k')
    ax.semilogy(ch1_gated_xaxis*0.256, ch1_gated, '.', label='ch1 gated', color = 'g')
    ax.semilogy(np.ones(2)*w1_starts[1]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.semilogy(np.ones(2)*w1_stops[1]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.set_xlabel('Time (ns)')
    ax.legend()

    plt.suptitle('Clicks after optical pulse 1')

    #### counts during tail in window 1:
    tail_counts_w1_ch0 = sum(ch0[np.arange(find_nearest(ch0_xaxis, w1_starts[0]), \
            find_nearest(ch0_xaxis, w1_stops[0]))])
    tail_counts_w1_ch1 = sum(ch1[np.arange(find_nearest(ch1_xaxis, w1_starts[1]), \
            find_nearest(ch1_xaxis, w1_stops[1]))])
    tail_counts_w1_ch0_gated = sum(ch0_gated[np.arange(find_nearest(ch0_gated_xaxis,\
            w1_starts[0]), find_nearest(ch0_gated_xaxis, w1_stops[0]))])
    tail_counts_w1_ch1_gated = sum(ch1_gated[np.arange(find_nearest(ch1_gated_xaxis,\
            w1_starts[1]), find_nearest(ch1_gated_xaxis, w1_stops[1]))])

    print '*    CH0: double clicks = ',tail_counts_w1_ch0-tail_counts_w1_ch0_gated
    print '*    CH1: double clicks = ',tail_counts_w1_ch1-tail_counts_w1_ch1_gated

    double_clicks_w1 = tail_counts_w1_ch0-tail_counts_w1_ch0_gated + \
            tail_counts_w1_ch1-tail_counts_w1_ch1_gated
    total_clicks_w1 = tail_counts_w1_ch0 + tail_counts_w1_ch1

    #### WINDOW 2
    ch0 = data_w2['ch0']
    ch0_xaxis = data_w2['ch0_xaxis']
    ch0_gated = data_w2['ch0_gated']
    ch0_gated_xaxis = data_w2['ch0_gated_xaxis']

    ch1 = data_w2['ch1']
    ch1_xaxis = data_w2['ch1_xaxis']
    ch1_gated = data_w2['ch1_gated']
    ch1_gated_xaxis = data_w2['ch1_gated_xaxis']

    w2ch0_tailph = sum(ch0[np.logical_and(ch0_xaxis > w2_starts[0], 
        ch0_xaxis < w2_starts[0]+int(60./0.256))])
    w2ch1_tailph = sum(ch1[np.logical_and(ch1_xaxis > w2_starts[1], 
        ch1_xaxis < w2_starts[1]+int(60./0.256))])

    print '===== WINDOW 2 ====='
    print '*    CH0: single clicks in tail region (60 ns): %s'%(w2ch0_tailph)
    print '*    CH1: single clicks in tail region (60 ns): %s'%(w2ch1_tailph)

    figure4 = plt.figure()
    ax = plt.subplot(121)
    ax.semilogy(ch0_xaxis*0.256, ch0, '-', label='ch0', color = 'k')
    ax.semilogy(ch0_gated_xaxis*0.256, ch0_gated, '.', label='ch0 gated')
    ax.semilogy(np.ones(2)*w2_starts[0]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.semilogy(np.ones(2)*w2_stops[0]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.set_xlabel('Time (ns)')
    ax.legend()

    ax = plt.subplot(122)
    ax.semilogy(ch1_xaxis*0.256, ch1, '-', label='ch1', color = 'k')
    ax.semilogy(ch1_gated_xaxis*0.256, ch1_gated, '.', label='ch1 gated')
    ax.semilogy(np.ones(2)*w2_starts[1]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.semilogy(np.ones(2)*w2_stops[1]*0.256, np.array([1,1E5]), '-r', lw = 2.0)
    ax.set_xlabel('Time (ns)')
    ax.legend()

    plt.suptitle('Clicks after optical pulse 2')

    #### counts during tail in window 2:
    tail_counts_w2_ch0 = sum(ch0[np.arange(find_nearest(ch0_xaxis, w2_starts[0]), \
            find_nearest(ch0_xaxis, w2_stops[0]))])
    tail_counts_w2_ch1 = sum(ch1[np.arange(find_nearest(ch1_xaxis, w2_starts[1]), \
            find_nearest(ch1_xaxis, w2_stops[1]))])
    tail_counts_w2_ch0_gated = sum(ch0_gated[np.arange(find_nearest(ch0_gated_xaxis\
            , w2_starts[0]), find_nearest(ch0_gated_xaxis, w2_stops[0]))])
    tail_counts_w2_ch1_gated = sum(ch1_gated[np.arange(find_nearest(ch1_gated_xaxis\
            , w2_starts[1]),find_nearest(ch1_gated_xaxis, w2_stops[1]))])

    print '*    CH0: double clicks = ',tail_counts_w2_ch0-tail_counts_w2_ch0_gated
    print '*    CH1: double clicks = ',tail_counts_w2_ch1-tail_counts_w2_ch1_gated

    double_clicks_w2 = tail_counts_w2_ch0-tail_counts_w2_ch0_gated+\
            tail_counts_w2_ch1-tail_counts_w2_ch1_gated
    total_clicks_w2 = tail_counts_w2_ch0+tail_counts_w2_ch1

    print 'Total detected double clicks: %s out of %s total clicks (%s percent)'\
            %(double_clicks_w1 + double_clicks_w2,total_clicks_w2, 
                    (double_clicks_w1 + double_clicks_w2)/float(total_clicks_w2)*100.)

    if not os.path.exists(os.path.join(datfolder,'figures')):
        os.makedirs(os.path.join(datfolder,'figures'))

    figure3.savefig(os.path.join(datfolder,'figures','histogram_window1.png'))
    figure4.savefig(os.path.join(datfolder,'figures','histogram_window2.png'))

    data_w1.close()
    data_w2.close()
    lde_file.close()

    tail_cps = (w1ch0_tailph + w1ch0_tailph + w2ch0_tailph + \
            w2ch1_tailph)/float(noof_starts*noof_pulses_in_seq*2)

    print 'Tail counts per shot = %s E-4 \n(NOTE: summed over 2 detectors, per applied laser pulse, not taking into account microwaves)\n'%(tail_cps*1E4)


def correlations_vs_time(hhpludat, ssro, w1_starts, w2_starts, max_window_len, 
        F0, F1, F0err, F1err, datapath, steps = 6, method = 1):
    """
    method = 2: integrate over detection window: 0, ... , length
    method = 1: take parts of the detection window: x, ... , x+dx
    """
    print 'Scanning over detection windows...'

    corr_vs_time = np.zeros([steps,4])
    corrected = np.zeros([steps,4])
    corr_err = np.zeros([steps,4])
    stepsize = max_window_len/float(steps)

    for step in np.arange(steps):
        if method == 2:
            w1_stop = (int(w1_starts[0]+(step+1)*stepsize),
                    int(w1_starts[1]+(step+1)*stepsize))
            w2_stop = (int(w2_starts[0]+(step+1)*stepsize),
                    int(w2_starts[1]+(step+1)*stepsize))
            w1_start = w1_starts
            w2_start = w2_starts
            print 'Window length =',w1_stop[0]-w1_start[0]
        elif method == 1:
            w1_stop = (int(w1_starts[0]+(step+1)*stepsize),
                    int(w1_starts[1]+(step+1)*stepsize))
            w2_stop = (int(w2_starts[0]+(step+1)*stepsize),
                    int(w2_starts[1]+(step+1)*stepsize))
            w1_start = (int(w1_starts[0]+step*stepsize),
                    int(w1_starts[1]+step*stepsize))
            w2_start = (int(w2_starts[0]+step*stepsize),
                    int(w2_starts[1]+step*stepsize))
        print 'Window length =',int(stepsize)


        b = correlations(hhpludat, ssro, 
                w1_start= w1_start, w2_start=w2_start, 
                w1_stop = w1_stop, w2_stop = w2_stop, 
                do_plot = False)

        #correct for readout
        c = SSRO_correct(b, F0, F1, F0err, F1err)

        for k in range(4):
            corr_vs_time[step,k] = b[k]
            corrected[step,k] = c[k/2][k%2]
            corr_err[step,k] = c[k/2+2][k%2]

    fig,(ax,ax2) = plt.subplots(2, 1, sharex=True)

    ax2.errorbar(np.linspace(0, max_window_len, steps), corrected[:,0], 
            yerr = corr_err[:,0], color = 'g', marker = 'd', label = 'w1, $m_s = 0$')
    ax.errorbar(np.linspace(0, max_window_len, steps), corrected[:,1], 
            yerr = corr_err[:,1], color = 'g', marker = 's', label = 'w1, $m_s = -1$')
    ax.errorbar(np.linspace(0, max_window_len, steps), corrected[:,2], 
            yerr = corr_err[:,2], color = 'r', marker = 'd', label = 'w2, $m_s = 0$')
    ax2.errorbar(np.linspace(0, max_window_len, steps), corrected[:,3], 
            yerr = corr_err[:,3], color = 'r', marker = 's', label = 'w2, $m_s = -1$')
    
    ax.set_ylim([0.8, 1.0])
    ax.legend(shadow = True, fancybox = True, loc = 3)
    ax2.legend(shadow = True, fancybox = True, loc = 2)
    ax.tick_params(labeltop='off')
    ax2.set_ylim([0.0, 0.2])

    plt.xlabel('Length of detection window (bins)')
    plt.suptitle('Correlations as function of detection window')
    plt.ylabel('Correlations')
    plt.xlim([0,max_window_len])
    
    # hide the spines between ax and ax2
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.xaxis.tick_bottom()
    ax.xaxis.tick_top()

    # Make the spacing between the two axes a bit smaller
    plt.subplots_adjust(hspace=0.1)

    fig.savefig(os.path.join(datapath, 'figures','correlations_vs_time.png'))
    
    return corr_vs_time

