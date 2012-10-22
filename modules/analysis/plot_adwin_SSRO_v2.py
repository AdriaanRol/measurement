import os, time

#cur_dir = os.getcwd()
#module_dir = r'Y:\user\modules'

#os.chdir(module_dir)

from modules.analysis import fit, rabi, common

#os.chdir(cur_dir)
#plt.close('all')

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def find_nearest(array,value):
    idx=(abs(array-value)).argmin()
    return idx

def plot(datapath, save = True):
    ###########################################
    ######## MEASUREMENT SPECS ################
    ###########################################
    e = load(datapath+'\\spin_control-0_statics_and_parameters.npz')
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    mw_min_len = e['min_mw_length']
    mw_max_len = e['max_mw_length']
    noof_datapoints = e['noof_datapoints']

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = load(datapath+'\\spin_control-0_Spin_RO.npz')
    raw_counts = f['counts']
    repetitions = f['sweep_axis']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    mw_len = linspace(mw_min_len,mw_max_len,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)

    #########################################
    ############ FITTING ####################
    #########################################

    FFT = fft.fft(counts_during_readout)
    N = int(noof_datapoints)
    timestep = (mw_max_len-mw_min_len)/float(noof_datapoints-1)
    freq = fft.fftfreq(N,d = timestep)

    #Remove offset:
    FFT[freq == 0] = 0

    figure1 = plt.figure(1)
    plt.bar(freq*1E3,abs(FFT), width = 0.4*1E3*(freq[1]-freq[0]), align = 'center')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Amplitude')
    plt.title('FFT (offset removed)')
    
    if save:
        figure1.savefig(datapath+'\\fft_signal_rabi.png')

  
    freq_guess = freq[find_nearest(abs(FFT),abs(FFT).max())]
    amp_guess = (counts_during_readout.max()+counts_during_readout.min())/2.0
    offset_guess = counts_during_readout.min()+(counts_during_readout.max()+\
            counts_during_readout.min())/2.0
    phase_guess = 0

    print 'freq_guess = ',freq_guess
    
    fit.fit1d(mw_len, counts_during_readout, rabi.fit_rabi_simple, 
            freq_guess, amp_guess, offset_guess, phase_guess,
            do_plot = True, do_print = True)
    
    figure2 = plt.gcf()

    plt.plot(mw_len,counts_during_readout, 'sk')
    plt.xlabel('MW length (ns)')
    plt.ylabel('Integrated counts')
    plt.title('MW length sweep, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
    if save:
        figure2.savefig(datapath+'\\histogram_integrated.png')

    x = 6.0
    y = 8.0

    figure3 = plt.figure(figsize=(x,y))
    plt.pcolor(raw_counts, cmap = 'hot', antialiased=False)
    plt.xlabel('Readout time (us)')
    plt.ylabel('MW repetition number')
    plt.title('Total histogram, integrated over repetitions')
    plt.colorbar()
    if save:
        figure3.savefig(datapath+'\\histogram_counts_2d.png')

    f.close()
    
    ###########################################
    ######## CHARGE RO ########################
    ###########################################

    #g = load(datapath+'\\spin_control-0_ChargeRO_before.npz')
    #h = load(datapath+'\\spin_control-0_ChargeRO_after.npz')

    #g.close()
    #h.close()


    ###########################################
    ######## SPIN PUMPING #####################
    ###########################################
    v = load(datapath+'\\spin_control-0_SP_histogram.npz')
    sp_counts = v['counts']
    sp_time = v['time']

    offset_guess = sp_counts[len(sp_counts)-1]
    init_amp_guess = sp_counts[2]
    decay_guess = 10

    figure4 = plt.figure(4)
    fit.fit1d(sp_time/1E3, sp_counts, common.fit_exp_decay_with_offset, 
            offset_guess, init_amp_guess, decay_guess,
            do_plot = True, do_print = True, newfig = False,
            plot_fitparams_xy = (0.5,0.5))
    
    plt.plot(sp_time/1E3,sp_counts,'sg')
    plt.xlabel('Time ($\mu$s)')
    plt.ylabel('Integrated counts')
    plt.title('Spin pumping')
    v.close()
    if save:
        figure4.savefig(datapath+'\\spin_pumping.png')

        #Save a dat file for use in e.g. Origin with the rabi oscillation.
        curr_date = '#'+time.ctime()+'\n'
        col_names = '#Col0: MW length (ns)\tCol1: Integrated counts\n'
        col_vals = str()
        for k in arange(noof_datapoints):
            col_vals += num2str(mw_len[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return True
        
#plot(r'C:\Documents and Settings\localadmin.TUD10238\Desktop\162245_spin_control_SIL9_lt2', save = True)
    


