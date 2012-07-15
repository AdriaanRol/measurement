import os, time, sys
import numpy as np
import plot
from analysis import fit, rabi, common, esr, ramsey

"""
Please note that this module is written for qtlab. It is intended for 
calibration and returns valuable information.
"""

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def find_nearest(array,value):
    """ 
    Returns the index of an array for which the value corresponding to that index
    is closest to the specified value.
    """
    idx=(abs(array-value)).argmin()
    return idx

def find_newest_data(datapath, string = '_spin_control'):
    """ 
    This function returns the datafolder with the latest timestamp.
    Datapath should be a folder containing folders of type 'hhmmss_spin_control'
    """
    all_dirs = os.listdir(datapath)
    right_dirs = list()

    for k in all_dirs:
        if string in k:
            right_dirs.append(k)

    newest_datapath = os.path.join(datapath, right_dirs[len(right_dirs)-1])

    return newest_datapath


def rabi_calibration(datapath, fit_data = True, save = True):
    """ 
    Fits results from a spin_control data using a FFT. 
    Datapath should be a folder that contains the actual measurement results,
    so for example: datapath = 'D:\data\yyyymmdd\hhmmss_spin_control_suffix'
    Flag fit_data if data should be fit.
    Flag save if data should be saved (in the data directory)
    """

    print 'Analyzing spin control data...'

    # Create directories for saving figures and saving processed data:
    if not os.path.exists(os.path.join(datapath,'figures')):
        os.makedirs(os.path.join(datapath,'figures'))
    if not os.path.exists(os.path.join(datapath,'processed_data')): 
        os.makedirs(os.path.join(datapath,'processed_data'))

    ###########################################
    ######## MEASUREMENT SPECS ################
    ###########################################
    files = os.listdir(datapath)
    
    for k in files:
        if 'statics_and_parameters.npz' in k:
            stats_params_file = k
        if 'Spin_RO.npz' in k:
            spin_ro_file = k
        if 'SP_histogram.npz' in k:
            sp_file = k

    e = np.load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    mw_min_len = e['min_mw_length']
    mw_max_len = e['max_mw_length']
    noof_datapoints = e['noof_datapoints']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    g = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = g['counts']
    repetitions = g['sweep_axis']
    t = g['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = np.zeros(noof_datapoints)
    mw_len = np.linspace(mw_min_len,mw_max_len,noof_datapoints)
    counts_during_readout = np.sum(raw_counts, axis = 1)

    #########################################
    ############ FITTING ####################
    #########################################
    
    if fit_data:
        FFT = np.fft.fft(counts_during_readout)
        N = int(noof_datapoints)
        timestep = (mw_max_len-mw_min_len)/float(noof_datapoints-1)
        freq = np.fft.fftfreq(N,d = timestep)

        #Remove offset:
        FFT[freq == 0] = 0

        plot1 = plot.Plot2D(freq*1E3, abs(FFT), 'sb')
        plot1.set_xlabel('Frequency (MHz)')
        plot1.set_ylabel('Amplitude')
        plot1.set_plottitle('FFT (offset removed)')
        plot1.set_title('FFT')

        if save:
            plot1.save_png(os.path.join(datapath, 'figures', 'fft_signal_rabi.png'))

        freq_guess = freq[find_nearest(abs(FFT),abs(FFT).max())]
        amp_guess = (counts_during_readout.max()+counts_during_readout.min())/2.0
        offset_guess = counts_during_readout.min()+(counts_during_readout.max()+\
                counts_during_readout.min())/2.0
        phase_guess = 0

        #print 'frequency guess = ',freq_guess


    if fit_data:
        fit_result = fit.fit1d(mw_len, counts_during_readout, rabi.fit_rabi_simple, 
                freq_guess, amp_guess, offset_guess, phase_guess,
                do_plot = False, ret = True)

        f = fit_result['params_dict']['f']
        a = fit_result['params_dict']['a']
        A = fit_result['params_dict']['A']
        phi = fit_result['params_dict']['phi']
        x = np.linspace(mw_min_len, mw_max_len, 501)

        fit_curve = a + A*np.cos(2*np.pi*(f*x + phi/360))

        pi_pulse_len = 0.5*1/f
        pi_2_pulse_len = 0.5*pi_pulse_len

    plot2 = plot.Plot2D(mw_len, counts_during_readout, 'sk', x,fit_curve, '-r')
    plot2.set_xlabel('MW length (ns)')
    plot2.set_ylabel('Integrated counts')
    plot2.set_plottitle('MW length sweep, driving f ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    #plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
    if save:
        plot2.save_png(os.path.join(datapath,'figures', 'histogram_integrated'))
    g.close()
    plot1.quit()
    plot2.quit()

    if save:
        #Save a dat file for use in e.g. Origin with the rabi oscillation.
        curr_date = '#'+time.ctime()+'\n'
        col_names = '#Col0: MW length (ns)\tCol1: Integrated counts\n'
        col_vals = str()
        for k in np.arange(noof_datapoints):
            col_vals += num2str(mw_len[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(os.path.join(datapath, 'processed_data', 'mw_pi_calibration_integrated_histogram.dat'), "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return pi_pulse_len


def esr_calibration(datapath, fit_data = True, save = True, f_dip = 2.858E9):

    ###########################################
    ######## MEASUREMENT SPECS ################
    ###########################################
    files = os.listdir(datapath)
    
    for k in files:
        if 'statics_and_parameters.npz' in k:
            stats_params_file = k
        if 'Spin_RO.npz' in k:
            spin_ro_file = k
        if 'SP_histogram.npz' in k:
            sp_file = k

    e = np.load(datapath+'\\'+stats_params_file)
    f_center = e['mw_center_freq']
    mwpower = e['mw_power']
    mw_min_freq = e['min_mw_freq']
    mw_max_freq = e['max_mw_freq']
    noof_datapoints = e['noof_datapoints']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    g = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = g['counts']
    repetitions = g['sweep_axis']
    t = g['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = np.zeros(noof_datapoints)
    mw_freq = np.linspace(mw_min_freq,mw_max_freq,noof_datapoints)
    counts_during_readout = np.sum(raw_counts, axis = 1)

    #########################################
    ############ FITTING ####################
    #########################################

    offset_guess = counts_during_readout.max()
    dip_depth_guess = offset_guess - counts_during_readout.min()

    print 'offset guess = ',offset_guess
    print 'dip depth guess = ',dip_depth_guess

    width_guess = 1E6
    f_dip_guess = f_dip
    noof_dips = 3
    dip_separation = 2E6

    if fit_data:
        fit_result = fit.fit1d(mw_freq, counts_during_readout, esr.fit_ESR_gauss, 
            offset_guess, dip_depth_guess, width_guess,
            f_dip_guess, (noof_dips, dip_separation),
            do_plot = False, do_print = False, 
            newfig = False, ret = True)

        x0 = fit_result['params_dict']['x0']
        a = fit_result['params_dict']['a']
        A = fit_result['params_dict']['A']
        sigma = fit_result['params_dict']['sigma']
        s0 = fit_result['params_dict']['s0']

        x = np.linspace(mw_min_freq, mw_max_freq, 501)
        fit_curve = np.zeros(len(x))

        x0 = [x0-s0, x0, x0+s0]
        for k in range(noof_dips):
            fit_curve += np.exp(-((x-x0[k])/sigma)**2)
        fit_curve = a*np.ones(len(x)) - A*fit_curve


    plot1 = plot.Plot2D(mw_freq/1E9, counts_during_readout, '-ok', x/1E9, fit_curve, '-r')  
    plot1.set_xlabel('MW frequency (GHz)')
    plot1.set_ylabel('Integrated counts')
    plot1.set_plottitle('MW frequency sweep, laser parking spot f ='+num2str(f_center/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    if save:
        plot1.save_png(datapath+'\\histogram_integrated.png')

    g.close()
    #plot1.quit()

    if save:
        #Save a dat file for use in e.g. Origin with the dark esr data.
        curr_date = '#'+time.ctime()+'\n'
        col_names = '#Col0: MW freq (GHz)\tCol1: Integrated counts\n'
        col_vals = str()
        for k in range(noof_datapoints):
            col_vals += num2str(mw_freq[k]/1E9,10)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\mw_f_calibration_integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return x0

def ssro_calibration(datapath, fit_data = True, save = True):
    """
    Returns the optimal read-out length for SSRO.
    """
    print 'Analyzing SSRO data...' 

    PREFIX = 'ADwin_SSRO'
    CR_SUFFIX = 'ChargeRO_after'
    SP_SUFFIX = 'SP_histogram'
    RO_SUFFIX = 'Spin_RO'
    PARAMS_SUFFIX = 'parameters'

    PARAM_REPS = 15
    PARAM_CYCLE_DURATION = 18

    def run_single(folder='', ms=0, index=0):
        if folder == "":
            folder = os.getcwd()

        if index < 10:
            SUFFIX = '-00'+str(index)
        elif index < 100:
            SUFFIX = '-0'+str(index)
        else:
            SUFFIX = str(index)

        basepath = os.path.join(folder,PREFIX+SUFFIX)
        params = np.load(basepath+'_'+PARAMS_SUFFIX+'.npz')

        reps    = params['par_long'][PARAM_REPS]
        binsize = params['par_long'][PARAM_CYCLE_DURATION]*.003333

        rodata = np.load(basepath+'_'+RO_SUFFIX+'.npz')
        spdata = np.load(basepath+'_'+SP_SUFFIX+'.npz')
        crdata = np.load(basepath+'_'+CR_SUFFIX+'.npz')

        autoanalyze_single_ssro(rodata, spdata, crdata, folder, ms=ms, 
                binsize=binsize, reps=reps, suffix_for_data = PREFIX+SUFFIX)

    def run_all(folder='', altern=True):
        if folder == "":
            folder = os.getcwd()
        
        #make figures folder and processed data folder
        if not os.path.exists(os.path.join(folder,'figures')):
            os.makedirs(os.path.join(folder,'figures'))
        if not os.path.exists(os.path.join(folder,'processed_data')): 
            os.makedirs(os.path.join(folder,'processed_data'))
        
        allfiles = os.listdir(folder)
        rofiles = [ f for f in allfiles if RO_SUFFIX in f ]
        for i in range(len(rofiles)):
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

                f1 = os.path.join(folder,'processed_data',
                        PREFIX+SUFFIX_i+'_fid_vs_ROtime.npz') 
                f0 = os.path.join(folder,'processed_data',
                        PREFIX+SUFFIX_j+'_fid_vs_ROtime.npz')
                t,f,ferr,t_max,F_max,plot1 = fidelities(f0,f1)
                if save:
                    plot1.save_png(os.path.join(folder,'figures','fidelity_vs_rotime.png'))
                    np.savetxt(os.path.join(folder, 'processed_data',
                    'totalfid-%d_+_%d.dat' % (i-1, i)),(t,f,ferr))

                plot1.quit()

        return t_max, F_max
                
    def autoanalyze_single_ssro(rodata, spdata, crdata, save_basepath, 
            binsize=0.131072, reps=1e4, ms=0, closefigs=True, stop=0, 
            firstbin=0, suffix_for_data = ''):
        """
        Analyzes a single SSRO measurement (can do both ms=0/+-1).
        creates an overview plot over the measurement results, and a plot
        of the measurement fidelity vs the measurement time.
        saves the fidelities and errors vs ro time.

        """

        savepath = os.path.join(save_basepath,'processed_data', suffix_for_data)

        if stop == 0:
            stop = rodata['time'][-1]/1e3
        lastbin = int(stop/binsize)
        
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

        cpsh = np.sum(rocounts[:,firstbin:lastbin], axis=1) # sum over all columns

        mean_cpsh = np.sum(cpsh)/float(reps)
        annotation += "\nmean c.p.sh. = %.2f" % (mean_cpsh)
        info += "\nmean c.p.sh. = %.2f" % (mean_cpsh)

        pzero = len(np.where(cpsh==0)[0])/float(reps)
        annotation += "\np(0 counts) = %.2f" % (pzero)
        info += "\np(0 counts) = %.2f" % (pzero)

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

        #fid_dat[:,0] contains read-out time,
        #fid_dat[:,1] contains read-out fidelity for specific ms

        ### saving
        infofile = open(savepath+'_autoanalysis.txt', 'w')
        infofile.write(info)
        infofile.close()

        # fidelities
        np.savez(os.path.join(savepath+'_fid_vs_ROtime'), time=fid_dat[:,0],
                fid=fid_dat[:,1], fid_error=fid_dat[:,2])
        np.savetxt(os.path.join(savepath+'_fid_vs_ROtime.dat'), fid_dat)

        # counts per shot
        f = open(savepath+'_cpsh_vs_ROtime.dat', 'w')
        f.write(cpsh_vs_ROtime)
        f.close()


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
        F_err = np.sqrt(fid0_err**2 + fid1_err**2)
        F_max = max(F)
        t_max = times[F.argmax()]

        plot1 = plot.Plot2D(times, F, 'or', times, fid1, 'og', times, fid0, 'og')
        plot1.set_plottitle("max. F=%.2f at t=%.2f us" % (F_max, t_max))
        plot1.set_xlabel('Read-out time (us)')
        plot1.set_ylabel('Fidelity')
        
        print "max. F=%.2f at t=%.2f us" % (F_max, t_max)

        return  times, F, F_err, t_max, F_max, plot1

    t_max, F_max = run_all(folder = datapath, altern = True)

    return t_max, F_max

