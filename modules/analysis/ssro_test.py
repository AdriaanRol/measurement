"""
module to postprocess and analyze the resulting data
from a SSRO measurement.

(!!! what is the measurement, i.e. with which program is it done?)

Expects the following files per SSRO measurement:
    - charge readout (cr) data: measurement run vs cr counts 1 vs cr counts 2
    - readout (ro) data: counts per timebin per measurement run (1 line per
      run)
    - spin pumping data: time [us] of bin start vs counts per bin

IMPORTANT: first function to invoke per data set is always load_data(folder)!

For more details, see the functions.

"""

### imports
import sys, os, time
from numpy import *
import numpy as np
from matplotlib import pyplot as plt
from analysis import fit, common

sys.path.append('D:\\measuring\\user\\modules')

PREFIX = 'SSRO_preselect'
CR_SUFFIX = 'ChargeRO'
SP_SUFFIX = 'SpinPumpkin'
RO_SUFFIX = 'SpinRO'
PARAMS_SUFFIX = 'parameters'
PARAM_BINSIZE_COL = 'par_binsize_us' #12
PARAM_REPS_COL = 'par_reps' #10

def run_single(folder='', ms=0, index=0):
    if folder == "":
        folder = os.getcwd()

    basepath = os.path.join(folder, PREFIX+'-'+str(index))
    parfile = basepath+'_'+PARAMS_SUFFIX+'.dat'
    params = loadtxt(parfile)

    binsize = params[get_param_column(parfile,PARAM_BINSIZE_COL)]
    reps = params[get_param_column(parfile,PARAM_REPS_COL)]
    print binsize
    print reps
    print 'index'
    print index
    rodata = np.load(basepath+'_'+RO_SUFFIX+'.npz')
    spdata = np.load(basepath+'_'+SP_SUFFIX+'.npz')
    crdata = np.load(basepath+'_'+CR_SUFFIX+'.npz')

    autoanalyze_single_ssro(rodata, spdata, crdata, basepath, ms=ms, 
            binsize=binsize, reps=reps)

def run_all(folder='', altern=True, save_pdfs=True):
    if folder == "":
        folder = os.getcwd()

    print PREFIX
    allfiles = os.listdir(folder)
    rofiles = [ f for f in allfiles if RO_SUFFIX in f ]
    for i in range(len(rofiles)):
        ms = 1 if (i%2 and altern) else 0
        run_single('',ms,i,save_pdf=save_pdfs)

        if altern and i%2:
            f1 = PREFIX+'-%d_fid_vs_ROtime.npz' % (i)
            f0 = PREFIX+'-%d_fid_vs_ROtime.npz' % (i-1)
            t,f,ferr,fig = fidelities(f0,f1)
            np.savetxt('totalfid-%d_+_%d.dat' % (i-1, i),(t,f,ferr))
            fig.savefig('totalfid-%d_+_%d.png' % (i-1, i))


def autoanalyze_single_ssro(rodata, spdata, crdata, save_basepath, 
        binsize=0.131072, reps=1e4, ms=0, closefigs=True, stop=0, firstbin=0,save_pdf=True):
    """
    Analyzes a single SSRO measurement (can do both ms=0/+-1).
    creates an overview plot over the measurement results, and a plot
    of the measurement fidelity vs the measurement time.
    saves the fidelities and errors vs ro time.

    """

    if stop == 0:
        stop = rodata['time'][-1]/1e3
    print rodata['time'][-1]/1e3
    print stop
    lastbin = int(stop/binsize)
    print lastbin
    t0 = time.time()
    ts = timestamp()

    rocounts = rodata['counts'].transpose()

    info = '' # will be populated with information that is written to a file
    info = """Analyze SSRO measurement:

Measurement settings:
=====================

repetitions: %d
binsize [us]: %f
stop analysis [us]: %f
    -> last bin: %dD:\measuring\data\20120408\131848_SSRO_preselect_SIL10

Measurement results:
====================

""" % (reps, binsize, stop, lastbin)

    annotation = 'repetitions: %d' % reps

    cpsh_vs_ROtime = """# columns:
# - time
# - counts per shot
"""

    fig1 = plt.figure(figsize=(16,12))

    ### histoD:\measuring\data\20120408\131848_SSRO_preselect_SIL10gram for photon counts per shot (cpsh)
    cpsh = sum(rocounts[:,firstbin:lastbin], axis=1) # sum over all columns

    ax = plt.subplot(221)
    plt.hist(cpsh, max(cpsh)+1, align='mid', label='counts')
    plt.xlabel('counts/shot')
    plt.ylabel('occurrences')
    plt.title('counts per shot, m_s = %d' % ms)

    mean_cpsh = sum(cpsh)/float(reps)
    annotation += "\nmean c.p.sh. = %.2f" % (mean_cpsh)
    info += "\nmean c.p.sh. = %.2f" % (mean_cpsh)

    pzero = len(where(cpsh==0)[0])/float(reps)
    annotation += "\np(0 counts) = %.2f" % (pzero)
    info += "\np(0 counts) = %.2f" % (pzero)

    plt.figtext(0.45, 0.85, annotation, horizontalalignment='right',
            verticalalignment='top')
    
    ### spin relaxation during readout
    ro_time = rodata['time'][:lastbin] # create time axis [us]
    ro_countrate = sum(rocounts[:,:lastbin], axis=0) / (binsize*1e-6*reps) # [Hz]
    savetxt(save_basepath + '_ro_countrate.dat',
         array([ro_time, ro_countrate]).transpose())

    ax = plt.subplot(222)
    # ax.set_yscale('log') 
    plt.plot(ro_time, ro_countrate, 'o')
    plt.xlabel('RO time [ns]')
    plt.ylabel('counts [Hz]')
    plt.title('spin relaxation during readout')

    ### spin pumping data

    # convert counts to Hz
    sp = array([j/(binsize*1e-6*reps) for j in spdata['counts']]) 

    ax = plt.subplot(223)
    # ax.set_yscale('log')
    plt.plot(spdata['time'], sp, 'o')
    plt.xlabel('spin pumping time [ns]')
    plt.ylabel('counts [Hz]')
    plt.title('spin relaxation during pumping')

    ### charge readout
    ax = plt.subplot(224)
    cr = crdata['counts']
    plt.hist(cr, abs(max(cr)-min(cr)+1), label='cr')
    #### plt.hist(cr[:,2], abs(max(cr[:,2])-min(cr[:,2]))+1, label='cr2')
    plt.xlabel('counts')
    plt.ylabel('occurences')
    plt.title('charge readout statistics')
    # plt.legend()D:\measuring\data\20120408\131848_SSRO_preselect_SIL10

    ### fidelity analysis
    fid_dat = zeros((0,3))

    for i in range(1,lastbin):
        t = i*binsize
        
        # d: hist of counts, c: counts per shot
        d = sum(rocounts[:,:i], axis=1)
        c = sum(d)/float(reps)

        cpsh_vs_ROtime += '%f\t%f\n' % (t, c)
        
        # we get the fidelity from the probability to get zero counts in a
        # shot 
        pzero = len(where(d==0)[0])/float(reps)
        pzero_err = sqrt(pzero*(1-pzero)/reps)
        fid = 1-pzero if ms == 0 else pzero # fidelity calc. depends on ms
        fid_dat = vstack((fid_dat, array([[t, fid, pzero_err]])))

    fig2 = plt.figure()
    print 'fid_dat[:,0]'
    print fid_dat[:,0]
    print 'fid_dat[:,1]'
    print fid_dat[:,1]
    print 'fid_dat[:,2]'
    print fid_dat[:,2]
    plt.errorbar(fid_dat[:,0], fid_dat[:,1], fmt='o', yerr=fid_dat[:,2])
    plt.xlabel('RO time [us]')
    plt.ylabel('ms = %d RO fidelity' % ms)
    plt.title('SSRO fidelity')

    ### saving
    infofile = open(save_basepath+'_autoanalysis.txt', 'w')
    infofile.write(info)
    infofile.close()

    # fidelities
    savez(os.path.join(save_basepath+'_fid_vs_ROtime'), time=fid_dat[:,0],
            fid=fid_dat[:,1], fid_error=fid_dat[:,2])
    savetxt(os.path.join(save_basepath+'_fid_vs_ROtime.dat'), fid_dat)

    # counts per shot
    f = open(save_basepath+'_cpsh_vs_ROtime.dat', 'w')
    f.write(cpsh_vs_ROtime)
    f.close()
    if save_pdf:
        fig1.savefig(save_basepath+'_autoanalysis.pdf', format='pdf')
        fig2.savefig(save_basepath+'_fid_vs_ROtime.pdf', format='pdf')

    totaltime = time.time() - t0
    print 'autoanalysis took %.2f seconds' % totaltime

    if closefigs:
        fig1.clf(); fig2.clf()
        plt.close('all')


def fidelities(fid_ms0, fid_ms1):
    """
    Performs the analysis for two SSROs with ms=0/1, and
    plots the total measurement fidelity (F) in dependence of the RO time.
    
    The two measurements need to fit (same nr of points, points matching)

    Parameters: The two respective npz files from the analysis of the single
    SSRO measurements.

    returns F, error of F
    """

    d_ms0 = np.load(fid_ms0)
    d_ms1 = np.load(fid_ms1)

    times = d_ms0['time']
    fid0 = d_ms0['fid']
    fid0_err = d_ms0['fid_error']
    fid1 = d_ms1['fid']
    fid1_err = d_ms1['fid_error']
    F = (fid0 + fid1)/2.
    F_err = sqrt(fid0_err**2 + fid1_err**2)
    F_max = max(F)
    t_max = times[F.argmax()]

    fig = plt.figure()
    plt.errorbar(times, fid0, fmt='.', yerr=fid0_err, label='ms=0')
    plt.errorbar(times, fid1, fmt='.', yerr=fid1_err, label='ms=1')
    plt.errorbar(times, F, fmt='.', yerr=F_err, label='total')
    plt.xlabel('RO time [us]')
    plt.ylabel('RO fidelity')
    plt.ylim((0.5,1))
    plt.title('SSRO fidelity')
    plt.legend(loc=4)
    plt.figtext(0.8, 0.5, "max. F=%.2f at t=%.2f us" % (F_max, t_max),
            horizontalalignment='right')

    return  times, F, F_err, fig

def fidelity_vs_power(folder='', x_axis_par='par_ro_Ex_power'):
    
    if folder == '':
        folder = os.getcwd()

    allfiles = os.listdir(folder)
    fidfiles = [f for f in allfiles if ('totalfid' in f and '.dat' in f)]

    x_axis = [] #in this case powers
    maxfid = []
    maxfid_t = []

    for f in fidfiles:
        fn, ext = os.path.splitext(f)
        idx = int(fn[fn.find('+_')+2:])
        basepath = os.path.join(folder, PREFIX+'-'+str(idx))
        parfile = basepath+'_'+PARAMS_SUFFIX+'.dat'  
        x_axis.append(loadtxt(parfile)[get_param_column(parfile,x_axis_par)]*1e9) #pwr in nW
        
        fiddat = loadtxt(f)
        maxidx = argmax(fiddat[1,:])
        maxfid.append(fiddat[1,maxidx])
        maxfid_t.append(fiddat[0,maxidx])
    
    
    fig = plt.figure()
    plt.plot(x_axis, maxfid, 'ro', label='max F')
    plt.xlabel('P [nW]')
    plt.ylabel('max. F')
    plt.legend()
    
    plt.twinx()
    plt.plot(x_axis, maxfid_t, 'bo')
    plt.ylabel('best ro-time')
    plt.savefig('fidelity_vs_power.png')

def spin_flip_time_vs_MW_freq(folder='', x_axis_par='par_MW_freq'):
    
    if folder == '':
        folder = os.getcwd()
    
    print get_param_column(os.path.join(folder,'SSRO_preselect-0_parameters.dat'),'par_cr_threshold')

    allfiles = os.listdir(folder)
    rofiles = [f for f in allfiles if ('_ro_countrate' in f and '.dat' in f)]
 
    x_axis = []
    spin_flip_time = []
    
    for f in rofiles:
        fn, ext = os.path.splitext(f)
        print fn
        idx = int(fn[fn.find('SSRO_preselect-')+15:fn.find('_ro_countrate')])
        basepath = os.path.join(folder, PREFIX+'-'+str(idx))
        parfile = basepath+'_'+PARAMS_SUFFIX+'.dat'  
        x_axis.append(loadtxt(parfile)[get_param_column(parfile,x_axis_par)]/1.0e9) #MW freq in GHz
        
        ro_data= loadtxt(f)
        
        t = ro_data[:,0]/1000 #time in us
        y = ro_data[:,1] #cnts
        #a : offset ~ 0, A : Amplitude, tau : spin_flip_time ~ 20 us
        a, A, tau = 0, max(y), 20
        
        #debug: CHECKING TODO
        print idx
        print 't', t
        print 'y' , y 
        #break


        
        fitres = fit.fit1d(t,y, common.fit_exp_decay_with_offset, \
                a, A, tau, do_print=True, do_plot=False, ret=True)

        if type(fitres) != type(False):
            p1 = fitres['params_dict']
            spin_flip_time.append(p1['tau'])
        else:    
            print 'could not fit exponential curve for file index ', idx 

    fig = plt.figure()
    plt.plot(x_axis, spin_flip_time, 'ro', label='spin flip time vs MW freq')
    plt.xlabel('MW frequqncy [GHz]')
    plt.ylabel('spin flip time [ns]')
    plt.legend()

# helper functions
def timestamp():
    return time.strftime('%Y%m%d.%H%M%S')

def get_param_column(parfile,parname):
    with open(parfile) as f:
        for line in f.readlines():
            if line.find(parname) != -1:
                return int(line[line.find('column')+7:line.find(':')]) 
    return -1
        













