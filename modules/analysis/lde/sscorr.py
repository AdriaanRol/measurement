import os
import numpy as np
import matplotlib.pyplot as plt

from analysis.lde import hht3
from analysis.lde import spcorr

DATFILEBASE = 'LDE'
DATIDX = 0
DATIDXDIGITS = 3
ADWINLT1FOLDER = 'adwin_lt1'
ADWINLT2FOLDER = 'adwin_lt2'
ADWINPARAMSFN = 'lde_params.npz'
ADWINDATAFN = 'lde_data.npz'


# load a fill folder of data and stitch together
# markers 1 will be gone after that!
def load_hhdata(rawfolder, file_contains='LDE', *arg, **kw):
    return spcorr.load_hhdata(rawfolder, file_contains, *arg, **kw)

# use this to get the actually useful hhdata out
# assume that the hhpludat is loaded via _load_hhdata:
# - already filtered on time and markers, markers 1 deleted
def get_hhpludata(hhdata):

    hhpludata = hht3.filter_counts_on_marker(hhdata, 2, [-1,0])
    hhpludata1 = hht3.filter_counts_on_marker(hhdata, 2, [-1])
    hhpludata2 = hht3.filter_counts_on_marker(hhdata, 2, [0])

    # some sanity checks
    if (len(hhpludata)==0):
        print 'no valid hhpludata'
    else:
        print ''
        print 'HH SSROs: %d' % len(hhpludata[
            np.logical_and(hhpludata[:,3]==1, hhpludata[:,2]==2)])
        print ''
        print 'counts + PLU: %d' % len(hhpludata[hhpludata[:,3]==0])
        print 'counts in window 1 + PLU: %d' % len(hhpludata1[hhpludata1[:,3]==0])
        print 'counts in window 2 + PLU: %d' % len(hhpludata2[hhpludata2[:,3]==0])

    return hhpludata, hhpludata1, hhpludata2


# function to check for double clicks in the hhdata, independent of the plu marker

def get_double_clicks(hhdata, ch0_start=0, ch0_stop=700,
        ch1_start=0, ch1_stop=700):
    noof_double = 0
    double_clicks = np.zeros(4,dtype=np.uint32)
    hhdata=hht3.get_allclicks(hhdata)
    #hhdata=hht3.filter_timewindow(hhdata,0,ch0_start,ch0_stop)
    #hhdata=hht3.filter_timewindow(hhdata,1,ch1_start,ch1_stop)
    for i in np.arange(len(hhdata)):
        try:
            if (hhdata[i,0]+1==(hhdata[i+1,0])):
                if (len(hhdata[np.where(hhdata[:,0]==hhdata[i,0])])==1 and\
                        len(hhdata[np.where(hhdata[:,0]==hhdata[i+1,0])])==1):
                    double_clicks=np.vstack((double_clicks,hhdata[i]))
                    double_clicks=np.vstack((double_clicks,hhdata[i+1]))
        except IndexError:
            pass
    if (len(np.shape(double_clicks))>1):    
        double_clicks=double_clicks[1:]
    return double_clicks
 

# get the adwin data and apply corrections
def load_adwin_data(datfolder, DATIDX=0, *arg, **kw):

    ### load adwin lt1 autodata 
    fn = os.path.join(datfolder, 
            ADWINLT1FOLDER+('-%.'+str(DATIDXDIGITS)+'d') % DATIDX, 
            ADWINDATAFN)
    d = np.load(fn)
    print 'loading :', fn
    
    noof_SSROs_adwin_LT1 = d['get_noof_SSROs']
    noof_SSRO_triggers_LT1 = d['get_noof_SSRO_triggers']
    d.close()

    ### load adwin lt2 autodata
    sn = os.path.join(datfolder, 
        ADWINLT2FOLDER+('-%.'+str(DATIDXDIGITS)+'d') % DATIDX, 
        ADWINDATAFN)
    s = np.load(sn)

    noof_PLU_markers = s['get_noof_PLU_markers']
    noof_SSROs_adwin_LT2 = s['get_noof_SSROs']
    s.close()

    ### get the SSRO data
    fn = os.path.join(datfolder,
         DATFILEBASE+('-%.'+str(DATIDXDIGITS)+'d.npz') % DATIDX)
    d = np.load(fn)
    
    SSROs_adwin_LT1 = d['adwin_lt1_SSRO']
    SSROs_adwin_LT2 = d['adwin_lt2_SSRO']
    CRs_adwin_LT1 = d['adwin_lt1_CR']
    CRs_adwin_LT2 = d['adwin_lt2_CR']
    
    ### fix missed SSROs in lt1
    SSROs_adwin_LT1, CRs_adwin_LT1, added_idxs = spcorr.correct_ssro_mismatch(
            SSROs_adwin_LT1, SSROs_adwin_LT2, noof_PLU_markers, 
            noof_SSROs_adwin_LT1, noof_SSROs_adwin_LT2, CRs_adwin_LT1)

    ### get the part of the array that contains actual data
    SSROs_adwin_LT1 = SSROs_adwin_LT1[:noof_SSRO_triggers_LT1+added_idxs]
    SSROs_adwin_LT2 = SSROs_adwin_LT2[:noof_PLU_markers]
    CRs_adwin_LT1 = CRs_adwin_LT1[:noof_SSRO_triggers_LT1+added_idxs]
    CRs_adwin_LT2 = CRs_adwin_LT2[:noof_PLU_markers]

    ### first some sanity checks
    invalid_SSROs_adwin_LT1 = np.where(SSROs_adwin_LT1==-1)[0]
    invalid_SSROs_adwin_LT2 = np.where(SSROs_adwin_LT2==-1)[0]
    
    print ''
    print 'adwin LT1 detected SSROs: %d' % (noof_SSRO_triggers_LT1)   
    print '  thereof invalid: %d' % len(invalid_SSROs_adwin_LT1)

    print ''
    print 'adwin LT2 detected SSROs: %d' % noof_PLU_markers
    print '  thereof invalid: %d' % len(invalid_SSROs_adwin_LT2)

    return SSROs_adwin_LT1, SSROs_adwin_LT2, CRs_adwin_LT1, CRs_adwin_LT2


# get the valid hhpludata;
# filter for time, time difference between the two clicks
# assume: only plu markers left in the data
# returns an array with the length of plu markers
# that contains a 0 for each invalid event, and a 1 for each invalid event
def windowdata(hhpludat, w1_start=(0,0), w1_stop=(700,700),
        w2_start=(0,0), w2_stop=(700,700), dt_max=-1,dt_min=-1, ch1_offset=0):
    """
    dt_max (=-1):
        if =/= -1, filter on dt: if the time difference between the window 1 
        and window 2 event is larger than dt_max, then we do not accept this
        event as valid.

    ch1_offset (=0):
        add this value to times registered on ch1, to balance.
    """


    photons = hhpludat[:,3] == 0
    mrkrs = np.logical_not(photons)       
    windows = np.zeros(len(hhpludat[hhpludat[:,3]==1]), dtype=int)
    debug=np.array([-1,-1,-1])

    for _i, nsync in np.ndenumerate(hhpludat[hhpludat[:,3]==1,0]):        
        i = _i[0]
        w1 = hhpludat[np.logical_and(photons, hhpludat[:,0] == nsync-1)]
        w2 = hhpludat[np.logical_and(photons, hhpludat[:,0] == nsync)]
        
 
        try:
            w1ch0 = w1[w1[:,2] == 0]
            w1ch0 = w1ch0[w1ch0[:,1] > w1_start[0]]
            w1ch0 = w1ch0[w1ch0[:,1] < w1_stop[0]]
            w1ch0len = len(w1ch0)
            t1 = w1ch0[0,1]
        except IndexError:
            w1ch0len = 0

        try:
            w1ch1 = w1[w1[:,2] == 1]
            w1ch1 = w1ch1[w1ch1[:,1] > w1_start[1]]
            w1ch1 = w1ch1[w1ch1[:,1] < w1_stop[1]]
            w1ch1len = len(w1ch1)
            t1 = w1ch1[0,1] + ch1_offset
        except IndexError:
            w1ch1len = 0

        try:
            w2ch0 = w2[w2[:,2] == 0]
            w2ch0 = w2ch0[w2ch0[:,1] > w2_start[0]]
            w2ch0 = w2ch0[w2ch0[:,1] < w2_stop[0]]
            w2ch0len = len(w2ch0)
            t2 = w2ch0[0,1]
        except IndexError:
            w2ch0len = 0

        try:
            w2ch1 = w2[w2[:,2] == 1]
            w2ch1 = w2ch1[w2ch1[:,1] > w2_start[1]]
            w2ch1 = w2ch1[w2ch1[:,1] < w2_stop[1]]
            w2ch1len = len(w2ch1)
            t2 = w2ch1[0,1] + ch1_offset
        except IndexError:
            w2ch1len = 0

        w1len = w1ch0len + w1ch1len
        w2len = w2ch0len + w2ch1len
        debug=np.vstack((debug,[w1len+w2len, w1len, w2len]))
        
        
        if w1len == 1 and w2len == 1:
            if dt_max == -1 or (dt_min < abs(t2 - t1) < dt_max):
                if (w1ch0len+w2ch0len==2) or (w1ch1len+w2ch1len==2):
                    windows[i] = 1
                else:
                    windows[i] =2
        else:
            pass

    return windows


# compute the spin-spin correlations from pre-filtered SSRO data
# correlations come out as follows:
# LT1 == 0 AND LT2 == 0 || == 0 AND > 0 || > 0 AND == 0 || > 0 AND > 0
def correlations(SSROs_adwin_LT1, SSROs_adwin_LT2, windows, 
        gate_phase=np.ones(10000), savepath = ''):
    uncond_corr = np.zeros(4)  # these are the unconditional correlations 
    corr_psi1 = np.zeros(4) #correlations for one of the two different psi states
    corr_psi2 = np.zeros(4) #correlations for the other of the two different psi states
    total = len(windows[windows>0])

    valid_idxs = list()

    for _i,w in np.ndenumerate(windows):
        i = _i[0]
        if w == 0 or SSROs_adwin_LT1[i] < 0 or SSROs_adwin_LT2[i] < 0 or gate_phase[i]<=0:
            if w==1:
                print 'kicked out (because of gate_phase) event', i
            continue
        uncond_corr[int(SSROs_adwin_LT1[i]>0)*2**1 + int(SSROs_adwin_LT2[i]>0)*2**0] += 1
        if w == 1:
            corr_psi1[int(SSROs_adwin_LT1[i]>0)*2**1 + int(SSROs_adwin_LT2[i]>0)*2**0] += 1
        if w == 2:
            corr_psi2[int(SSROs_adwin_LT1[i]>0)*2**1 + int(SSROs_adwin_LT2[i]>0)*2**0] += 1
        
        valid_idxs.append(i)

    print '\nPlotting valid SSROs...'
    valid_ssro_lt1 = SSROs_adwin_LT1[valid_idxs]
    valid_ssro_lt2 = SSROs_adwin_LT2[valid_idxs]
    print '\tMean counts per RO for LT1, LT2: %s, %s'%(np.mean(valid_ssro_lt1),
            np.mean(valid_ssro_lt2))

    try:
        fig2 = plt.figure(figsize = (12.,6.))
        plt.subplot(121)
        if not(valid_ssro_lt1 == np.array([])): #make sure valid_ssro_lt1 is not an empty list
            t = plt.hist(valid_ssro_lt1,
                    bins = max(valid_ssro_lt1) if max(valid_ssro_lt1) > 0 else 1,
                    color = '#4682B4')
            plt.text(0.5*0.7*max(valid_ssro_lt1),0.5*max(t[0]), 
                    'mean cps = '+str(np.mean(valid_ssro_lt1)))
            plt.text(0.5*0.7*max(valid_ssro_lt1),0.45*max(t[0]), 
                    'fraction in 0 = '+str(t[0][0]/float(np.sum(t[0]))))
        
        plt.xlabel('Number of counts')
        plt.ylabel('Occurrences')
        plt.title('LT1')
        
        plt.subplot(122)
        if not(valid_ssro_lt2 == np.array([])):
            u = plt.hist(valid_ssro_lt2, 
                    bins = max(valid_ssro_lt2) if max(valid_ssro_lt2) > 0 else 1, 
                    color = '#4B0082')
            plt.text(0.5*0.7*max(valid_ssro_lt2),0.5*max(u[0]), 
                    'mean cps = '+str(np.mean(valid_ssro_lt2)))
            plt.text(0.5*0.7*max(valid_ssro_lt2),0.45*max(u[0]), 
                    'fraction in 0 = '+str(u[0][0]/float(np.sum(u[0]))))

        
        plt.xlabel('Number of counts')
        plt.ylabel('Occurrences')
        plt.title('LT2')
        
        if savepath == '':
            savepath = os.getcwd()

        plt.suptitle('Histogram of time-filtered SSRO events')
        fig2.savefig(os.path.join(savepath, 'valid_ssros_lt1_lt2.png'))

        print '\tFraction in 0-bar for LT1, LT2: %s, %s\n'\
                %(t[0][0]/float(np.sum(t[0])), u[0][0]/float(np.sum(u[0])))
    except:
        pass

    return uncond_corr, corr_psi1, corr_psi2

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def ssro_correct_twoqubit_state_general(correlations, F0a, F0b, F1a, F1b):
    
    if sum(correlations) != 1:
        print 'Correlations not normalized!'

    U = np.matrix([[F0a*F0b, F0a*(1-F1b), F0b*(1-F1a), (1-F1a)*(1-F1b)],
            [F0a*(1-F0b), F0a*F1b, (1-F1a)*(1-F0b), (1-F1a)*F1b],
            [(1-F0a)*F0b, (1-F0a)*(1-F1b), F1a*F0b, F1a*(1-F1b)],
            [(1-F0a)*(1-F0b), (1-F0a)*F1b, F1a*(1-F0b), F1a*F1b]])

    if np.linalg.det(U) != 0:
        Uinv = U.I

    correlations_corrected = np.matrix.dot(Uinv,correlations.T)

    return correlations_corrected

def ssro_correct_twoqubit_state_photon_numbers(correlations, F0a, F0b, F1a, F1b,
        verbose = True):

    """
    The input of this function should be an array with photon numbers.
    photon_numbers = [ #LT1 = 0 and LT2 = 0; #LT1 = 0 and LT2 > 0; 
    #LT1 > 0 and LT2 = 0; #LT1 > 0, LT2 > 0]. In ms terms this means
    [11;10;01;00], so the matrix is defined differently now. 

    Photon numbers need not to be normalized.

    a = LT1, b = LT2
    """

    if verbose:
        print 'Correcting for read-out...'
        print 'Before correction: \n\tLT1=0,LT2=0\tLT1=0,LT2>0\tLT1>0,LT2=0\tLT1>0,LT2>0'
        string = str()
        for k in correlations/np.float(correlations.sum()):
            string += '\t'+num2str(k,3)+'\t'
        print string

    #Normalize the stats.
    correlations = np.asmatrix(correlations/np.float(correlations.sum()))
    
    if correlations.sum() != 1:
        print 'Correlations not normalized!'

    U = np.matrix([[F1a*F1b, F1a*(1-F0b), F1b*(1-F0a), (1-F0a)*(1-F0b)],
            [F1a*(1-F1b), F1a*F0b, (1-F0a)*(1-F1b), F0b*(1-F0a)],
            [F1b*(1-F1a), (1-F1a)*(1-F0b), F0a*F1b, F0a*(1-F0b)],
            [(1-F1a)*(1-F1b), F0b*(1-F1a), F0a*(1-F1b), F0a*F0b]])

    if np.linalg.det(U) != 0:
        Uinv = U.I
        correlations_corrected = np.matrix.dot(Uinv,correlations.T)
    else:
        print 'This is a non-invertible matrix!'
        correlations_corrected = False
    
    if verbose:
        print 'After correction:\n\tLT1=0,LT2=0\tLT1=0,LT2>0\tLT1>0,LT2=0\tLT1>0,LT2>0'
        string = str()
        for k in correlations_corrected:
            string += '\t'+num2str(k,3)+'\t'
        print string+'\n'

    return np.asarray(correlations_corrected)


def plot_uncorrected_corrected(correlations,corr,sav_fig=False,save_path='', state = ''):
    fig1=plt.figure()
    plt.title(state+' Uncorrected')
    plt.bar(np.arange(0,4), np.squeeze(np.asarray(correlations)), align = 'center',
            color = '#173DA6')
    for k in range(4):
        plt.text(k,0.8,num2str(np.squeeze(np.asarray(correlations))[k],2), ha = 'center')
    plt.xlabel('States [LT1,LT2]')
    plt.ylabel('Correlations')
    plt.ylim([0,1])
    plt.xticks([0,1,2,3], ['|-1-1>', '|-10>', '|0-1>', '|00>'])

    if sav_fig:
        fig1.savefig(save_path+'correlation_uncorrected.png')
        #print (save_path+'correlation_uncorrected.png')


    fig2=plt.figure()
    plt.title(state+' Corrected')
    plt.bar(np.arange(0,4), np.squeeze(np.asarray(corr)), align = 'center',
            color = '#436CDE')
    for k in range(4):
        plt.text(k,0.8, num2str(np.squeeze(np.asarray(corr))[k],2), ha = 'center')
    plt.xlabel('States [LT1,LT2]')
    plt.ylabel('Correlations')
    plt.ylim([0,1])
    plt.xticks([0,1,2,3], ['|-1-1>', '|-10>', '|0-1>', '|00>'])
    if sav_fig:
        fig2.savefig(save_path+'correlation_corrected.png')




def get_channel_statistics(raw_double_click_data):
    """returns the division over windows/channels in the form
    [ch0+ch0,ch1+ch0,ch0+ch1,ch1+ch1]"""

    data=raw_double_click_data
    channels=np.zeros(4,dtype=np.uint32)
    for i in np.arange(len(data)-1):
        try:
            if (data[i,0]+1==(data[i+1,0])):
                channels[int(data[i,2]*2**0+data[i+1,2]*2**1)]+=1
        except IndexError:
            pass
    return channels

def get_dt_hist(raw_double_click_data,hist_size=700):

    """returns a histogram of dt's between double clicks]"""

    data=raw_double_click_data
    histogram=np.zeros(hist_size,dtype=np.uint32)
    for i in np.arange(len(data)-1):
        try:
            if (data[i,0]+1==(data[i+1,0])):
                histogram[int(abs(data[i,1]-data[i+1,1]))]+=1
        except IndexError:
            print'dt outside histogram range'

    return histogram

def get_dt_hist_vs_chan_stat(raw_double_click_data,hist_size=700):

    """returns a histogram of dt's between double clicks, 
    seperated to the different channel signatures
     [ch0+ch0,ch1+ch0,ch0+ch1,ch1+ch1]"""

    data=raw_double_click_data.astype(np.int32)
    histogram=np.zeros((4,hist_size),dtype=np.int32)
    for i in np.arange(len(data)-1):
        try:
            if (data[i,0]+1==(data[i+1,0])):
                histogram[int(data[i,2]*2**0+data[i+1,2]*2**1),int(data[i,1]-data[i+1,1])+350]+=1
                if int(data[i,1]-data[i+1,1])<0:
                    print int(data[i,1]-data[i+1,1])
        except IndexError:
            print'dt outside histogram range'

    return histogram


# create some dummy data foanalr testing
def dummy_data():
    
    hhdata = np.zeros((0,4), dtype=np.uint)
    adwin1 = np.array([], dtype=int)
    adwin2 = np.array([], dtype=int)

    for i in range(1000):
        hhdata = np.vstack((hhdata, np.array([5*i,10,0,0], dtype=np.uint)))
        if i%2:
            hhdata = np.vstack((hhdata, np.array([5*i+1,10,1,0], dtype=np.uint)))
        hhdata = np.vstack((hhdata, np.array([5*i+1,0,2,1], dtype=np.uint)))

        #adwin1 = np.append(adwin1, -1**i if i%2 else 0)
        #adwin2 = np.append(adwin2, -1**(i+1) if i%2 else 0)
        adwin1 = np.append(adwin1, 1)
        adwin2 = np.append(adwin2, 0)

    return hhdata, adwin1, adwin2

