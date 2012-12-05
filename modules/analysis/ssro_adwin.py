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
#from numpy import *
import numpy as np
from matplotlib import pyplot as plt
from analysis import fit, rabi, common, esr, ramsey

PREFIX = 'ADwin_SSRO'
CR_SUFFIX = 'ChargeRO_after'
SP_SUFFIX = 'SP_histogram'
RO_SUFFIX = 'Spin_RO'
PARAMS_SUFFIX = 'parameters'

#PARAM_BINSIZE_COL = 12
#PARAM_REPS_COL = 10

PARAM_REPS = 15
PARAM_CYCLE_DURATION = 18

def get_latest_data(string = 'ADwin_SSRO', datapath = ''):
    meas_folder = r'D:\measuring\data'
    currdate = time.strftime('%Y%m%d')
    
    if datapath == '':
        df = os.path.join(meas_folder, currdate)
    else:
        df = datapath
    
    right_dirs = list()

    if os.path.isdir(df):
        for k in os.listdir(df):
            if string in k:
                right_dirs.append(k)
        
        if len(right_dirs) > 0:
            latest_dir = os.path.join(df,right_dirs[len(right_dirs)-1])
        else:
            print 'No measurements containing %s in %s'%(string, df)
        
        print '\nAnalyzing data in %s'%latest_dir

    else:
        print 'Folder %s does not exist'%df
        latest_dir = False

    return latest_dir


def run_single(folder='', ms=0, index=0):
    if folder == "":
        folder = os.getcwd()

    if index < 10:
        SUFFIX = '-00'+str(index)
    elif index < 100:
        SUFFIX = '-0'+str(index)
    else:
        SUFFIX = str(index)

    basepath = os.path.join(folder, PREFIX+SUFFIX)
    params = np.load(basepath+'_'+PARAMS_SUFFIX+'.npz')

    reps    = params['par_long'][PARAM_REPS]
    binsize = params['par_long'][PARAM_CYCLE_DURATION]*.003333

    rodata = np.load(basepath+'_'+RO_SUFFIX+'.npz')
    spdata = np.load(basepath+'_'+SP_SUFFIX+'.npz')
    crdata = np.load(basepath+'_'+CR_SUFFIX+'.npz')

    autoanalyze_single_ssro(rodata, spdata, crdata, basepath, ms=ms, 
            binsize=binsize, reps=reps)
    rodata.close()
    spdata.close()
    crdata.close()
    params.close()

def run_all(folder='', altern=True):
    if folder == "":
        folder = os.getcwd()

    allfiles = os.listdir(folder)
    rofiles = [ f for f in allfiles if RO_SUFFIX in f ]
    for i in range(len(rofiles)):
        print i
  
        ms = 1 if (i%2 and altern) else 0
        run_single(folder,ms,i)

        if altern and i%2:
 
            if i < 10:
                SUFFIX_i = '-00'+str(i)
                SUFFIX_j = '-00'+str(i-1)
            elif i == 10:
                SUFFIX_i = '-0'+str(i)
                SUFFIX_j = '-00'+str(i-1)
            elif i < 100:
                SUFFIX_i = '-0'+str(i)
                SUFFIX_j = '-0'+str(i-1)

            f1 = PREFIX+SUFFIX_i+'_fid_vs_ROtime.npz' 
            f0 = PREFIX+SUFFIX_j+'_fid_vs_ROtime.npz'
            t,f,ferr,fig = fidelities(folder,f0,f1)

            np.savetxt(folder+'\\'+'totalfid-%d_+_%d.dat' % (i-1, i),(t,f,ferr))
            fig.savefig(folder+'\\'+'totalfid-%d_+_%d.png' % (i-1, i))
    
def autoanalyze_single_ssro(rodata, spdata, crdata, save_basepath, 
        binsize=0.131072, reps=1e4, ms=0, closefigs=True, stop=0, firstbin=0):
    """
    Analyzes a single SSRO measurement (can do both ms=0/+-1).
    creates an overview plot over the measurement results, and a plot
    of the measurement fidelity vs the measurement time.
    saves the fidelities and errors vs ro time.

    """

    if stop == 0:
        stop = rodata['time'][-1]/1e3
    #print rodata['time'][-1]/1e3
    print 'stop = ',stop
    lastbin = int(stop/binsize)
    print 'lastbin = ',lastbin
    print 'binsize = ',binsize
    t0 = time.time()
    ts = timestamp()

    rocounts = rodata['counts']  #.transpose()

    info = '' # will be populated with information that is written to a file
    info = """Analyze SSRO measurement:

Measurement settings:
=====================

repetitions: %d
binsize [us]: %f
stop analysis [us]: %f
    -> last bin: %d

Measurement results:
====================

""" % (reps, binsize, stop, lastbin)

    annotation = 'repetitions: %d' % reps

    cpsh_vs_ROtime = """# columns:
# - time
# - counts per shot
"""

    fig1 = plt.figure(figsize=(16,12))

    ### histogram for photon counts per shot (cpsh)
    cpsh = np.sum(rocounts[:,firstbin:lastbin], axis=1) # sum over all columns
    #print cpsh
    #print max(cpsh)
    ax = plt.subplot(221)
    plt.hist(cpsh, max(cpsh)+1, align='mid', label='counts')
    plt.xlabel('counts/shot')
    plt.ylabel('occurrences')
    plt.title('counts per shot, m_s = %d' % ms)

    mean_cpsh = sum(cpsh)/float(reps)
    annotation += "\nmean c.p.sh. = %.2f" % (mean_cpsh)
    info += "\nmean c.p.sh. = %.2f" % (mean_cpsh)

    pzero = len(np.where(cpsh==0)[0])/float(reps)
    annotation += "\np(0 counts) = %.2f" % (pzero)
    info += "\np(0 counts) = %.2f" % (pzero)

    plt.figtext(0.45, 0.85, annotation, horizontalalignment='right',
            verticalalignment='top')
    
    ### spin relaxation during readout
    ro_time = rodata['time'][:lastbin] # create time axis [us]
    ro_countrate = np.sum(rocounts[:,:lastbin], axis=0) / (binsize*1e-6*reps) # [Hz]
    np.savetxt(save_basepath + '_ro_countrate.dat',
         np.array([ro_time, ro_countrate]).transpose())

    ax = plt.subplot(222)
    # ax.set_yscale('log') 
    plt.plot(ro_time, ro_countrate, 'o')
    plt.xlabel('RO time [ns]')
    plt.ylabel('counts [Hz]')
    plt.title('spin relaxation during readout')

    ### spin pumping data

    # convert counts to Hz
    sp = np.array([j/(binsize*1e-6*reps) for j in spdata['counts']]) 
    ax = plt.subplot(223)
    if False and len(spdata['counts'])>2:
        offset_guess = spdata['counts'][len(spdata['counts'])-1]
        init_amp_guess = spdata['counts'][2]
        decay_guess = 10
        

        fit_result=fit.fit1d(spdata['time'][2:len(spdata['counts'])-1]/1E3, 
                spdata['counts'][2:len(spdata['counts'])-1], 
                common.fit_exp_decay_with_offset, 
                offset_guess, init_amp_guess, decay_guess,
                do_plot = True, do_print = True, newfig = False, ret=True,
                plot_fitparams_xy = (0.5,0.5))

    # ax.set_yscale('log')
    # NOTE: spin pumping starts at 1 us, that is the first datapoint
    # that is retrieved from the adwin. Fit might not be displayed properly
    # anymore now...
    plt.plot(spdata['time']+1E3, sp, 'o')
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
    # plt.legend()

    ### fidelity analysis
    fid_dat = np.zeros((0,3))

    for i in range(1,lastbin):
        t = i*binsize
        
        # d: hist of counts, c: counts per shot
        d = np.sum(rocounts[:,:i], axis=1)
        c = np.sum(d)/float(reps)

        cpsh_vs_ROtime += '%f\t%f\n' % (t, c)
        
        # we get the fidelity from the probability to get zero counts in a
        # shot 
        pzero = len(np.where(d==0)[0])/float(reps)
        pzero_err = np.sqrt(pzero*(1-pzero)/reps)
        fid = 1-pzero if ms == 0 else pzero # fidelity calc. depends on ms
        fid_dat = np.vstack((fid_dat, np.array([[t, fid, pzero_err]])))

    fig2 = plt.figure()
    plt.errorbar(fid_dat[:,0], fid_dat[:,1], fmt='o', yerr=fid_dat[:,2])
    plt.xlabel('RO time [us]')
    plt.ylabel('ms = %d RO fidelity' % ms)
    plt.title('SSRO fidelity')

    ### saving
    infofile = open(save_basepath+'_autoanalysis.txt', 'w')
    infofile.write(info)
    infofile.close()

    # fidelities
    np.savez(os.path.join(save_basepath+'_fid_vs_ROtime'), time=fid_dat[:,0],
            fid=fid_dat[:,1], fid_error=fid_dat[:,2])
    np.savetxt(os.path.join(save_basepath+'_fid_vs_ROtime.dat'), fid_dat)

    # counts per shot
    f = open(save_basepath+'_cpsh_vs_ROtime.dat', 'w')
    f.write(cpsh_vs_ROtime)
    f.close()

    fig1.savefig(save_basepath+'_autoanalysis.pdf', format='pdf')
    fig2.savefig(save_basepath+'_fid_vs_ROtime.pdf', format='pdf')

    totaltime = time.time() - t0
    print 'autoanalysis took %.2f seconds' % totaltime

    if closefigs:
        fig1.clf(); fig2.clf()
        plt.close('all')


def fidelities(folder,fid_ms0, fid_ms1):
    """
    Performs the analysis for two SSROs with ms=0/1, and
    plots the total measurement fidelity (F) in dependence of the RO time.
    
    The two measurements need to fit (same nr of points, points matching)

    Parameters: The two respective npz files from the analysis of the single
    SSRO measurements. Filepath (string) to show at plot

    returns F, error of F
    """

    d_ms0 = np.load(folder+'\\'+fid_ms0)
    d_ms1 = np.load(folder+'\\'+fid_ms1)

    times = d_ms0['time']
    fid0 = d_ms0['fid']
    fid0_err = d_ms0['fid_error']
    fid1 = d_ms1['fid']
    fid1_err = d_ms1['fid_error']
    F = (fid0 + fid1)/2.
    F_err = np.sqrt(fid0_err**2 + fid1_err**2)
    F_max = max(F)
    t_max = times[F.argmax()]

    fig = plt.figure()
    plt.errorbar(times, fid0, fmt='.', yerr=fid0_err, label='ms=0')
    plt.errorbar(times, fid1, fmt='.', yerr=fid1_err, label='ms=1')
    plt.errorbar(times, F, fmt='.', yerr=F_err, label='total')
    plt.xlabel('RO time [us]')
    plt.ylabel('RO fidelity')
    plt.ylim((0.5,1.08))
    plt.text(0.01*(max(times)+min(times)),1.05*max(fid1),folder+'\\'+fid_ms1,fontsize='x-small')
    plt.title('SSRO fidelity')
    plt.legend(loc=4, fancybox = True, shadow = True)
    plt.figtext(0.8, 0.5, "max. F=%.2f at t=%.2f us" % (F_max, t_max),
            horizontalalignment='right')
    d_ms0.close()
    d_ms1.close()
    return  times, F, F_err, fig

def fidelity_vs_power(folder='',sweep_param='Ex_RO_amplitude'):
    
    if folder == '':
        folder = os.getcwd()

    allfiles = os.listdir(folder)
    fidfiles = [f for f in allfiles if ('totalfid' in f and '.dat' in f)]

    pow = []
    maxfid = []
    maxfid_t = []

    
    for f in fidfiles:
        fn, ext = os.path.splitext(f)
        idx = int(fn[fn.find('+_')+2:])-1
        print idx
        
        if idx < 10:
            SUFFIX = '-00'+str(idx)
        elif idx == 10:
            SUFFIX = '-0'+str(idx)
        elif idx < 100:
            SUFFIX = '-0'+str(idx)

        basepath = os.path.join(folder, PREFIX+SUFFIX)
        parfile = basepath+'_parameters_dict.npz'  
        param_dict=load(parfile)
        #pow.append(loadtxt(parfile)[get_param_column(parfile,'par_ro_Ex_power')]*1e9)
        #pow.append(int(idx/2)*1.)
        pow.append(param_dict[sweep_param])
        param_dict.close
        fiddat = loadtxt(f)
        maxidx = argmax(fiddat[1,:])
        maxfid.append(fiddat[1,maxidx])
        maxfid_t.append(fiddat[0,maxidx])
        #fiddat.close() 
    
    fig = plt.figure()
    plt.plot(pow, maxfid, 'ro', label='max F')
    plt.xlabel('P [nW]')
    plt.ylabel('max. F', color = 'r')
    plt.ylim(0.9*min(maxfid),1)
    plt.title('Maximum SSRO Fidelity and Optimal readout time vs' + sweep_param)
    plt.text(0.01*(max(pow)+min(pow)),1.15*max(maxfid),folder,fontsize='x-small')
    plt.legend()
    ax = plt.gca()
    ax.tick_params(axis='y', colors='red')
    
    plt.twinx()
    plt.plot(pow, maxfid_t, 'bo')
    plt.ylabel('best ro-time', color = 'b')
    plt.ylim(ymax=1.2*max(maxfid_t))
    ax = plt.gca()
    ax.tick_params(axis='y', colors='blue')
    plt.savefig('fidelity_vs_power.png')
    


def spin_flip_time_vs_MW_freq(folder=''):
    
    if folder == '':
        folder = os.getcwd()
    
    print get_param_column(os.path.join(folder,'SSRO_preselect-0_parameters.dat'),'par_cr_threshold')

    #allfiles = os.listdir(folder)
    #fidfiles = [f for f in allfiles if ('_ro_countrate' in f and '.dat' in f)]
 
    #pow = []
    #maxfid = []
    #maxfid_t = []

    #for f in fidfiles:
     #   fn, ext = os.path.splitext(f)
      #  idx = int(fn[fn.find('+_')+2:])
       # basepath = os.path.join(folder, PREFIX+'-'+str(index))
        #params = loadtxt(basepath+'_'+PARAMS_SUFFIX+'.dat')
        #pow.append(loadtxt('SSRO_preselect-%d_parameters.dat' %idx)[8]*1e9)
     #   
     #   fiddat = loadtxt(f)
     #   maxidx = argmax(fiddat[1,:])
     #   maxfid.append(fiddat[1,maxidx])
     #   maxfid_t.append(fiddat[0,maxidx])
    




    #ro_time = rodata['time'][:lastbin] # create time axis [us]
    #ro_countrate = sum(rocounts[:,:lastbin], axis=0) / (binsize*1e-6*reps) # [Hz]
    #savetxt(save_basepath + '_ro_countrate.dat',
    #     array([ro_time, ro_countrate]).transpose())

def analyze_SP_RO(sp_file, params,folder='',plot=True,save=True,do_print=False,ret = False,name='spin_pumping.png'):
    '''
    Function to plot and fit a single SP or RO curve. 
    

    sp_file     string      (part of) the filename that contains data of interest
    folder      string      folder that contains the data
    '''     
    
    if folder == '':
        folder = os.getcwd()

    v = load(folder+'\\'+sp_file)
    Ex_RO_power = params['Ex_RO_amplitude']
    A_RO_power = params['Ex_RO_amplitude']
    Ex_SP_power = params['Ex_SP_amplitude']
    A_SP_power = params['A_SP_amplitude']

    if 'Spin_RO' in sp_file:
        sp_counts = sum(v['counts'],axis=0)
        title = 'RO Powers: Ex = ' + str(Ex_RO_power*1E9) + 'nW, A = ' + str(A_RO_power*1E9) + 'nW'
    else:
        sp_counts = v['counts']
        title = 'SP Powers: Ex = ' + str(Ex_SP_power*1E9) + 'nW, A = ' + str(A_SP_power*1E9) + 'nW'
        
    
    sp_time = v['time']
    v.close()

    offset_guess = sp_counts[len(sp_counts)-1]
    init_amp_guess = max(sp_counts)
    firstpoint=int(find_nearest(sp_counts,init_amp_guess))

    decay_guess = 10

    if plot:
        figure4 = plt.figure(4)
        plt.clf()

    fit_result=fit.fit1d(sp_time[firstpoint:len(sp_counts)-1]/1E3, sp_counts[firstpoint:len(sp_counts)-1], common.fit_exp_decay_with_offset, 
            offset_guess, init_amp_guess, decay_guess,
            do_plot = plot, do_print = do_print, newfig = False, ret=True,
            plot_fitparams_xy = (0.5,0.5))
    
    if plot:
       
        plt.plot(sp_time/1E3,sp_counts,'sg')
        plt.xlabel('Time ($\mu$s)')
        plt.ylabel('Integrated counts')
        plt.title(title)
        plt.ylim(ymax=max(sp_counts)*1.2)
        plt.text(0.01*(max(sp_time/1E3)+min(sp_time/1E3)),1.15*max(sp_counts),folder+sp_file,fontsize='x-small')
    
        if save:
            figure4.savefig(folder+'\\'+name+'.png')

    if ret:
        return fit_result
       

def SP_RO_fitparam_vs_sweepparam(folder='',fitparam_nr=2,sweeppar='Ex_RO_power',
        suffix = PREFIX,fitfile=SP_SUFFIX,
        xlabel = 'sweep',ylabel = 'fitresult',name='fitvssweep'):
    '''
    This function fits all spin-pumping/spin readout data from 1 folder and plots one of 
    the fitparameters (amplitude, decay or offset) versus a parameter that is varied.

    datapath     string     folder where data is located
    fitparam_nr  integer    fit1d returns p, fitparam = p[integer]
    sweeppar     string     fitparam is plotted vs par['string'] from params_dict.npz
    suffix       string     name of measurement
    fitfile      string     (part of) the filename that contains data of interest
                      
    '''
    if folder == '':
        folder = os.getcwd()
    
    sweepparam=[]
    fitparam=[]
    ###########################################
    ######## MEASUREMENT SPECS ################
    ###########################################
    files = os.listdir(folder)
    
    for fn in files:        
        if (fitfile in fn) and ('.npz' in fn):
            idx = fn[len(suffix)+1:len(fn)-len(fitfile)-5]
            params=load(folder + '\\' + suffix + '-'+idx+'_parameters_dict.npz')
            if (params['do_ms0']) and (params['do_ms1']):
                altern = True
            else:
                altern = False
            sweeppar_val = params[sweeppar]                    
            fitresult = analyze_SP_RO(fn,params,folder,save=True,ret=True,name=fitfile+num2str(len(fitparam),0))
            if fitresult:
                fitparam.append(fitresult[0]['params'][fitparam_nr])
                sweepparam.append(float(sweeppar_val*1E9))
            params.close()
    
    if (altern) and ('SP' in sweepparam):
        if 'Ex' in sweepparam:
            sweepparamplot = sweepparam[1::2]
            fitparamplot   = fitparam[1::2]
        if 'A' in sweepparam:
            sweepparamplot = sweepparam[::2]
            fitparamplot   = fitparam[::2]
    else:
        sweepparamplot = sweepparam
        fitparamplot = fitparam
    figure1 = plt.figure(1)    
    plt.clf()
    plt.plot(sweepparamplot,fitparamplot, 'or')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(name)
    plt.ylim(ymax=1.2*max(fitparamplot))
    plt.text(0.01*(max(sweepparamplot)+min(sweepparamplot)),1.15*max(fitparamplot),folder,fontsize='x-small')
    
    if save:
        figure1.savefig(folder+'\\'+name+'.png')
    return {'fitparam' : fitparam,'sweepparam':sweepparam}

def spin_pumping_during_readout_vs_RO_power(folder='',transition='A'):
    '''
    This function uses SP_RO_fitparam_vs_sweepparam to fit the Spin_RO curves
    for a measurement where the RO amplitude ('A' or 'Ex') is swept.
    It plots the resulting decay constant and amplitude vs RO power in 1 plot
    and the offset vs RO power in a separate plot.
    '''


    if folder == '':
        folder = os.getcwd()
    fittau = SP_RO_fitparam_vs_sweepparam(folder,2,transition + '_RO_amplitude',fitfile='Spin_RO',
            xlabel=transition+' power [W]',ylabel='Decay constant [us]',
            name='RO Curve Decay const vs '+transition+' RO power')
    fitA   = SP_RO_fitparam_vs_sweepparam(folder,1,transition + '_RO_amplitude',fitfile='Spin_RO',
            xlabel=transition+' power [W]',ylabel='Amplitude  [cts]',
            name='RO Curve Peak counts vs '+transition+' RO power')
    fita   = SP_RO_fitparam_vs_sweepparam(folder,0,transition + '_RO_amplitude',fitfile='Spin_RO',
            xlabel=transition+' power [W]',ylabel='Amplitude  [cts]',
            name='RO Curve Offset vs '+transition+' RO power')
   
    fig1 = plt.figure(1)
    plt.clf()
    ax1 = fig1.add_subplot(111)
    

    tau = ax1.plot(fittau['sweepparam'],fittau['fitparam'], 'ob')
    plt.ylabel("Decay constant [us]",color = 'b')
    plt.ylim(ymax=1.3*max(fittau['fitparam']))
    ax1.tick_params(axis='y',colors='b',right='off')
    ax1.yaxis.set_label_position("left")

    ax2 = fig1.add_subplot(111, sharex=ax1, frameon=False)
    A = ax2.plot(fitA['sweepparam'],fitA['fitparam'], 'xr')
    ax2.tick_params(axis='y',colors='r')
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    plt.ylabel("Amplitude [counts]",color = 'r')
    plt.ylim(ymax = 1.3*max(fitA['fitparam']))
    plt.text(0.01*(max(fitA['sweepparam'])+min(fitA['sweepparam'])),1.25*max(fitA['fitparam']),folder,fontsize='x-small')
    plt.xlabel(transition+" power [nW]")
    plt.title('RO Curve Decay time and Peak counts vs '+transition+' RO power')
    
    plt.legend((tau, A), ("Tau", "Amplitude"),loc='upper right',bbox_to_anchor=(1,1/1.05))
    fig1.savefig(folder+'\\'+'SP_A_and_tau_vs_'+transition+'_power.png')
    
def get_readout_corr(ro_time, dat_path = ''):

    if dat_path == '':
        dat_path = os.getcwd()

    d= np.load(dat_path+'\ADwin_SSRO-000_fid_vs_ROtime.npz')
    time=d['time']
    idx = find_nearest(time,ro_time)
    ms0_fid=d['fid'][idx]
    ms0_error=d['fid_error'][idx]
    d.close()

    f= np.load(dat_path+'\ADwin_SSRO-001_fid_vs_ROtime.npz')
    time=f['time']
    idx = find_nearest(time,ro_time)
    ms1_fid=f['fid'][idx]
    ms1_error=f['fid_error'][idx]
    f.close()

    print 'ms_0 fid', ms0_fid
    print 'ms_0 error', ms0_error

    print 'ms_1 fid', ms1_fid
    print 'ms_1 error', ms1_error
    
    return (ms0_fid,ms1_fid), (ms0_error,ms1_error)

# helper functions
def timestamp():
    return time.strftime('%Y%m%d.%H%M%S')

def get_param_column(parfile,parname):
    with open(parfile) as f:
        for line in f.readlines():
            if line.find(parname) != -1:
                return int(line[line.find('column')+7:line.find(':')]) 
    return -1       

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def find_nearest(array,value):
    idx=(np.abs(array-value)).argmin()
    return idx








