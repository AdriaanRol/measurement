import os, time
from numpy import *
from matplotlib import pyplot as plt
from analysis import fit, rabi, common, esr, ramsey

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def find_nearest(array,value):
    idx=(abs(array-value)).argmin()
    return idx

def plot_rabi(datapath, fit_data = True, with_detuning = False, save = True):

    plt.close('all')
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

    e = load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    mw_min_len = e['min_mw_length']
    mw_max_len = e['max_mw_length']
    noof_datapoints = e['noof_datapoints']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = load(datapath+'\\'+spin_ro_file)
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
    
    if fit_data:
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

    figure2 = plt.figure(2)
        
    if fit_data and with_detuning:
        tau_guess = 200
        fit.fit1d(mw_len, counts_during_readout, 
                rabi.fit_rabi_multiple_detunings, 
                amp_guess, offset_guess, freq_guess, tau_guess,
                (0,0),(2.2E-3,0),(2*2.2E-3,0),
                do_plot = True, do_print = True, newfig = False)
    elif fit_data:
        fit.fit1d(mw_len, counts_during_readout, rabi.fit_rabi_simple, 
                freq_guess, amp_guess, offset_guess, phase_guess,
                do_plot = True, do_print = True, newfig = False)
    
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
    ######## SPIN PUMPING #####################
    ###########################################
    v = load(datapath+'\\'+sp_file)
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

def plot_dark_esr(datapath, fit_data = True, save = True, f_dip = 2.878E9):
    plt.close('all')
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

    e = load(datapath+'\\'+stats_params_file)
    f_center = e['mw_center_freq']
    mwpower = e['mw_power']
    mw_min_freq = e['min_mw_freq']
    mw_max_freq = e['max_mw_freq']
    noof_datapoints = e['noof_datapoints']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    repetitions = f['sweep_axis']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    mw_freq = linspace(mw_min_freq,mw_max_freq,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)

    #########################################
    ############ FITTING ####################
    #########################################

    offset_guess = counts_during_readout.max()
    dip_depth_guess = offset_guess - counts_during_readout.min()

    print offset_guess
    print dip_depth_guess

    width_guess = 1E6
    f_dip_guess = f_dip
    noof_dips = 3
    dip_separation = 2E6

    if fit_data:
        fit.fit1d(mw_freq, counts_during_readout, esr.fit_ESR_gauss, 
            offset_guess, dip_depth_guess, width_guess,
            f_dip_guess, (noof_dips, dip_separation),
            do_plot = True, do_print = True, newfig = False)


    figure2 = plt.figure(2)  
    plt.plot(mw_freq/1E9,counts_during_readout, '-k')
    plt.xlabel('MW frequency (GHz)')
    plt.ylabel('Integrated counts')
    plt.title('MW frequency sweep, laser parking spot $f$ ='+num2str(f_center/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    #plt.text(0.1*(mw_max_freq+mw_min_freq),max(counts_during_readout),datapath)
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
    ######## SPIN PUMPING #####################
    ###########################################

    v = load(datapath+'\\'+sp_file)
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
        col_names = '#Col0: MW freq (GHz)\tCol1: Integrated counts\n'
        col_vals = str()
        for k in arange(noof_datapoints):
            col_vals += num2str(mw_freq[k]/1E9,10)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return True

def plot_ramsey(datapath, fit_data = True, save = True):

    plt.close('all')
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

    e = load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    detuning = e['detuning']
    mwpower = e['mw_power']
    tau_max = e['min_wait_time']
    tau_min = e['max_wait_time']
    pi_2_duration = e['pi_2_duration']
    noof_datapoints = e['noof_datapoints']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    repetitions = f['sweep_axis']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    tau = linspace(tau_min,tau_max,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)

    #########################################
    ############ FITTING ####################
    #########################################
    
    if fit_data:
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

        offset_guess = counts_during_readout.min()+(counts_during_readout.max()+\
                counts_during_readout.min())/2.0
        tau_guess = 1000
        
        #modulations:
        mod_freq_guess = freq[find_nearest(abs(FFT),abs(FFT).max())]
        mod_amp_guess = (counts_during_readout.max()+counts_during_readout.min())/2.0
        mod_phase_guess = 0

        print 'modulation frequency guess = ',freq_guess 
        print 'modulation amplitude guess = ',mod_amp_guess

    figure2 = plt.figure(2)
        
    if fit_data:
        tau_guess = 200
        fit.fit1d(tau, counts_during_readout, 
                ramsey.fit_ramsey_gaussian_decay, 
                tau_guess, offset_guess, 
                (mod_freq_guess,mod_amp_guess,mod_phase_guess),
                do_plot = True, do_print = True, newfig = False)
    
    plt.plot(tau,counts_during_readout, 'sk')
    plt.xlabel('\Delta t$ (ns)')
    plt.ylabel('Integrated counts')
    plt.title('Ramsey, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm,\n Detuning = '+\
            num2str(detuning/1E6,0)+' MHz, $\pi/2$ length = '+\
            num2str(pi_2_duration,0)+' ns')
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
    ######## SPIN PUMPING #####################
    ###########################################
    v = load(datapath+'\\'+sp_file)
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
        col_names = '#Col0: Interpulse delay (ns)\tCol1: Integrated counts\n'
        col_vals = str()
        for k in arange(noof_datapoints):
            col_vals += num2str(tau[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return True

def plot_esmw(datapath, fit_data = True, save = True):
    plt.close('all')

    suffix = 'esmw'

    ###########################################
    ######## MEASUREMENT SPECS ################
    ###########################################
    files = os.listdir(datapath)
    
    e = load(datapath+'\\'+suffix+'-0_statics_and_parameters.npz')
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    mw_min_freq = e['min_esmw_freq']
    mw_max_freq = e['max_esmw_freq']
    noof_datapoints = e['noof_datapoints']
    e.close()
    
    spin_ro_file = list()
    sp_file = list()
    
    for idx in arange(noof_datapoints):
        for k in files:
            if k == suffix+'-'+num2str(idx,0)+'_Spin_RO.npz':
                spin_ro_file.append(k)
            if k == suffix+'-'+num2str(idx,0)+'_SP_histogram.npz':
                sp_file.append(k)



    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    mw_freq = linspace(mw_min_freq,mw_max_freq,noof_datapoints)
    fit_par=[]
    for idx in arange(noof_datapoints):
        f = load(datapath+'\\'+spin_ro_file[idx])
        raw_counts = f['counts']
        repetitions = f['sweep_axis']
        t = f['time']

        tot_size = len(repetitions)
        reps_per_point = tot_size/float(noof_datapoints)

        counts_during_readout = sum(raw_counts, axis = 0)
        ro_time = arange(0,shape(raw_counts)[1])
        figure1 = plt.figure(1)
        
        offset_guess = counts_during_readout.min()
        init_amp_guess = counts_during_readout.max()
        decay_guess = 10

        if fit_data:
            fit_result,p=fit.fit1d(ro_time[arange(4,len(ro_time)-1)], counts_during_readout[arange(4,len(ro_time)-1)], common.fit_exp_decay_with_offset, 
            offset_guess, init_amp_guess, decay_guess,
            do_plot = True, do_print = True, newfig = False,
            plot_fitparams_xy = (0.5,0.5),
            ret=True)
       
        fit_par.append(fit_result['params'][2])
        plt.plot(ro_time, counts_during_readout, 'or')
        plt.xlabel('Read-out duration ($\mu$s)')
        plt.ylabel('Integrated counts')
        plt.title('Read-out with MW, driving $f$ ='+num2str(f_drive/1E6,1)+\
                ' MHz, power = '+num2str(mwpower,0)+' dBm')
        if save:
            figure1.savefig(datapath+'\\histogram_integrated'+num2str(idx,0)+'.png')

        x = 6.0
        y = 8.0

        figure2 = plt.figure(figsize=(x,y))
        plt.pcolor(raw_counts, cmap = 'hot', antialiased=False)
        plt.xlabel('Readout time (us)')
        plt.ylabel('MW repetition number')
        plt.title('Total histogram, integrated over repetitions')
        plt.colorbar()
        if save:
            figure2.savefig(datapath+'\\histogram_counts_2d'+num2str(idx,0)+'.png')

        f.close()
        
        ###########################################
        ######## SPIN PUMPING #####################
        ###########################################
        v = load(datapath+'\\'+sp_file[idx])
        sp_counts = v['counts']
        sp_time = v['time']

        offset_guess = sp_counts[len(sp_counts)-1]
        init_amp_guess = sp_counts[2]
        decay_guess = 10

        figure3 = plt.figure(3)
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
            figure3.savefig(datapath+'\\spin_pumping'+num2str(idx,0)+'.png')

            #Save a dat file for use in e.g. Origin with the rabi oscillation.
            curr_date = '#'+time.ctime()+'\n'
            col_names = '#Col0: MW length (ns)\tCol1: Integrated counts\n'
            col_vals = str()
            for k in arange(max(ro_time)):
                col_vals += num2str(ro_time[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\n'
            fo = open(datapath+'\\integrated_histogram.dat', "w")
            for item in [curr_date, col_names, col_vals]:
                fo.writelines(item)
            fo.close()

    plt.close('all')
    print len(mw_freq)
    print len(fit_par)
    figure4 = plt.figure(4)
    plt.plot(mw_freq/1E6,fit_par, '-r')
    plt.xlabel('MW frequency (MHz)')
    plt.ylabel('Decay constant')

    figure4.savefig(datapath+'\\decay_constant_vs_mw_freq.png')



    return fit_par

