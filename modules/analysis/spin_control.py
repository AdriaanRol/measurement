import os, time
import numpy as np
from numpy import *
from matplotlib import pyplot as plt
from analysis import fit, rabi, common, esr, ramsey, SE

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def find_nearest(array,value):
    idx=(abs(array-value)).argmin()
    return idx

def SSRO_correct(SSRO_meas, F0, F1, F0err = 0.01, F1err = 0.01):
    w1 = SSRO_meas[:2].copy()
    w1 = w1[::-1]
    
    w1total = np.sum(w1)
    w1 /= float(w1total)

    norm = 1./(F0+F1-1.)
    w1staterr = np.sqrt(w1*(1.-w1)/float(w1total))
    
    w1p0 = w1[1]
    w1p1 = w1[0]

    w1ms0err = np.sqrt( 
            (norm**2 * (-w1p1 + F0*(w1p0+w1p1)) * F1err)**2 +\
            (norm**2 * (w1p0 - F1*(w1p0+w1p1)) * F0err)**2 +\
            (norm * (F1 - 1) * w1staterr[1])**2 +\
            (norm * F1 * w1staterr[0])**2
            )
    w1ms1err = w1ms0err
    w1err = np.array([w1ms0err, w1ms1err])


    corrmat = 1./(F0*F1 - (1.-F1)*(1.-F0)) * np.array([[F1, F1-1.],[F0-1., F0]])
    return np.dot(corrmat, w1.reshape(2,1)).reshape(-1), \
            w1err

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

    e = np.load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    mw_min_len = e['min_mw_length']
    mw_max_len = e['max_mw_length']
    noof_datapoints = e['noof_datapoints']
    noof_reps = e['completed_repetitions']
    e.close()

    
    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    SSRO_counts = f['SSRO_counts']
    repetitions = f['sweep_axis']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    mw_len = linspace(mw_min_len,mw_max_len,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)
    SSRO_readout = sum(SSRO_counts, axis = 1)/float(noof_reps)
    

    #########################################
    ############ FITTING ####################
    #########################################
    
    if fit_data:
        FFT = fft.fft(SSRO_readout)
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

    figure3 = plt.figure(3)
    plt.clf()
    ax1 = figure3.add_subplot(111)
   
    if fit_data and with_detuning:
        tau_guess = 200
        fit.fit1d(mw_len, counts_during_readout, 
                rabi.fit_rabi_multiple_detunings, 
                amp_guess, offset_guess, freq_guess, tau_guess,
                (0,0),(2.2E-3,0),(2*2.2E-3,0),
                do_plot = True, do_print = True, newfig = False)
    elif fit_data:
        [fit_result, p] = fit.fit1d(mw_len, counts_during_readout, rabi.fit_rabi_simple, 
                freq_guess, amp_guess, offset_guess, phase_guess,
                do_plot = True, do_print = True, newfig = False, ret = True)

        #pi_pulse_len = 0.5*1/fit_result['params_dict']['f']
        #pi_2_pulse_len = 0.5*pi_pulse_len

        #print 'pi pulse length = ', pi_pulse_len
        #print 'pi/2 pulse length = ',pi_2_pulse_len
    

    #ax2 = figure2.add_subplot(111, sharex=ax1, frameon=False)
    #ax2.plot(mw_len,counts_during_readout, 'sk')

    plt.xlabel('MW length (ns)')
    plt.ylabel('Integrated counts')
    plt.title('MW length sweep, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
    if save:
        figure3.savefig(datapath+'\\histogram_integrated.png')


    figure2 = plt.figure(2)
    plt.clf()
    ax1 = figure2.add_subplot(111)
    #plt.plot(mw_len,SSRO_readout, 'sk')

    if fit_data and with_detuning:
        tau_guess = 200
        fit.fit1d(mw_len, SSRO_readout, 
                rabi.fit_rabi_multiple_detunings, 
                amp_guess, offset_guess, freq_guess, tau_guess,
                (0,0),(2.2E-3,0),(2*2.2E-3,0),
                do_plot = True, do_print = True, newfig = False)
    elif fit_data:
        [fit_result, p] = fit.fit1d(mw_len, SSRO_readout, rabi.fit_rabi_simple, 
                freq_guess, amp_guess, offset_guess, phase_guess,
                do_plot = True, do_print = True, newfig = False, ret = True)

        pi_pulse_len = 0.5*1/fit_result['params_dict']['f']
        pi_2_pulse_len = 0.5*pi_pulse_len

        print 'pi pulse length = ', pi_pulse_len
        print 'pi/2 pulse length = ',pi_2_pulse_len
    

    #ax2 = figure2.add_subplot(111, sharex=ax1, frameon=False)
    #ax2.plot(mw_len,counts_during_readout, 'sk')
    plt.ylim([0,1])
    plt.xlabel('MW length (ns)')
    plt.ylabel('P($m_s=0$)')
    plt.title('MW length sweep, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
    if save:
        figure2.savefig(datapath+'\\histogram_integrated_SSRO.png')

    x = 6.0
    y = 8.0

    figure4 = plt.figure(figsize=(x,y))
    plt.pcolor(raw_counts, cmap = 'hot', antialiased=False)
    plt.xlabel('Readout time (us)')
    plt.ylabel('MW repetition number')
    plt.title('Total histogram, integrated over repetitions')
    plt.colorbar()
    if save:
        figure4.savefig(datapath+'\\histogram_counts_2d.png')

    f.close()
    

    ###########################################
    ######## SPIN PUMPING #####################
    ###########################################
    v = np.load(datapath+'\\'+sp_file)
    sp_counts = v['counts']
    sp_time = v['time']

    offset_guess = sp_counts[len(sp_counts)-1]
    init_amp_guess = sp_counts[2]
    decay_guess = 10

    figure5 = plt.figure()
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
        figure5.savefig(datapath+'\\spin_pumping.png')

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
    
    f = np.load(datapath+'\\'+spin_ro_file)
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

    figure2 = plt.figure(2)
    plt.plot(mw_freq/1E9,counts_during_readout, '-ok')

    if fit_data:
        fit_result, p = fit.fit1d(mw_freq/1E9, counts_during_readout, 
                esr.fit_ESR_gauss, offset_guess, dip_depth_guess, width_guess/1E9,
                f_dip_guess/1E9, (noof_dips, dip_separation/1E9),
                do_plot = True, do_print = True, newfig = False, ret = True, 
                plot_fitonly = True)


        center_peak = fit_result['params_dict']['x0']
        splitting = fit_result['params_dict']['s0']

        print '-1: f = ', (center_peak - splitting), ' GHz'
        print '0: f = ', center_peak, ' GHz'
        print '1: f = ', (center_peak + splitting), ' GHz'

    plt.xlabel('MW frequency (GHz)')
    plt.ylabel('Integrated counts')
    plt.title('MW frequency sweep, MW parking spot $f$ ='+num2str(f_center/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
   
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

    v = np.load(datapath+'\\'+sp_file)
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

    e = np.load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    detuning = e['detuning']
    mwpower = e['mw_power']
    tau_max = e['tau_min']
    tau_min = e['tau_max']
    #pi_2_duration = e['pi_2_duration']
    pi_2_duration=25
    noof_datapoints = e['noof_datapoints']
    noof_reps = e['completed_repetitions']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    SSRO_counts = f['SSRO_counts']
    repetitions = f['sweep_axis']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    tau = linspace(tau_min,tau_max,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)
    SSRO_readout = sum(SSRO_counts, axis = 1)/float(noof_reps)
    #########################################
    ############ FITTING ####################
    #########################################
    print fit_data
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
    print SSRO_readout
    plt.plot(tau,SSRO_readout, 'sk')
    plt.xlabel('\Delta t$ (ns)')
    plt.ylabel('Integrated counts')
    plt.title('Ramsey, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm,\n Detuning = '+\
            num2str(detuning/1E6,0)+' MHz, $\pi/2$ length = '+\
            num2str(pi_2_duration,0)+' ns')
    plt.text(0.1*(tau_max+tau_min),max(counts_during_readout),datapath)
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
    v = np.load(datapath+'\\'+sp_file)
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

def plot_SE(datapath, fid=(0.82,0.9),fiderr=(0.01,0.01),fit_data = True, exp_guess=2.8, save = True):

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

    e = np.load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    tau_max = e['tau_max']
    tau_min = e['tau_min']
    #frabi = e['frabi']
    frabi=11.

    noof_datapoints = e['noof_datapoints']
    noof_reps = e['completed_repetitions']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    SSRO_counts = f['SSRO_counts']
    repetitions = f['sweep_axis']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    tau_free_evol = linspace(tau_min,tau_max,noof_datapoints)*2e-3
    counts_during_readout = sum(raw_counts, axis = 1)
    SSRO_readout = sum(SSRO_counts, axis = 1)/float(noof_reps)
    SSRO_readout_corr = zeros(len(SSRO_readout))
    readout_error = zeros(len(SSRO_readout))

    for i in arange(len(SSRO_readout)):
        ms0_events = SSRO_readout[i]*noof_reps
        ms1_events = noof_reps*(1-SSRO_readout[i])
        corr = SSRO_correct(array([ms1_events,ms0_events]),F0=fid[0],F1=fid[1],F0err=fiderr[0],F1err=fiderr[1])
        SSRO_readout_corr[i]=corr[0][0]
        readout_error[i] = corr[1][0] 

    #########################################
    ############ FITTING ####################
    #########################################
    #FIXME: write nice fitting routine for SE
    
    figure2 = plt.figure(2)
        

    plt.plot(tau_free_evol,counts_during_readout, 'sk')
    plt.xlabel('Free evolution time [us]')
    plt.ylabel('Integrated counts')
    plt.title('Spin Echo, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, frabi = '+num2str(frabi,0)+' MHz')
    plt.text(0.1*(max(tau_free_evol)+min(tau_free_evol)),max(counts_during_readout),datapath)
    if save:
        figure2.savefig(datapath+'\\histogram_integrated.png')

    figure4 = plt.figure(4)
  
    plt.plot(tau_free_evol,SSRO_readout, 'sk')
    plt.xlabel('Free evolution time [us]')
    plt.ylabel('Fraction of events >0 counts')
    plt.title('Spin Echo SSRO cor, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, frabi = '+num2str(frabi,0)+' MHz')
    plt.text(0.1*(max(tau_free_evol)+min(tau_free_evol)),max(SSRO_readout),datapath)
    if save:
        figure4.savefig(datapath+'\\SSRO_readout.png')    

    figure6 = plt.figure(6)
        
    if fit_data:
        tau_guess = 530
        offset_guess = SSRO_readout_corr.min()
        amp_guess=SSRO_readout_corr.max()-offset_guess

        print tau_guess
        print offset_guess
        print amp_guess
        print tau_guess
        print exp_guess
        print tau_free_evol

        fitresult=fit.fit1d(tau_free_evol, SSRO_readout_corr, 
                SE.fit_echo, tau_guess, amp_guess,offset_guess, 
                exp_guess, do_plot = True, do_print = True, newfig = False)
        print fitresult
    plt.errorbar(tau_free_evol,SSRO_readout_corr,fmt='sk',yerr=readout_error)
    plt.xlabel('Free evolution time [us]')
    plt.ylabel('P ms=0')
    plt.title('Spin Echo SSRO cor, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, frabi = '+num2str(frabi,0)+' MHz')
    plt.text(0.1*(max(tau_free_evol)+min(tau_free_evol)),max(SSRO_readout_corr),datapath)
    if save:
        figure6.savefig(datapath+'\\SSRO_readout_corr.png')  


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
    v = np.load(datapath+'\\'+sp_file)
    sp_counts = v['counts']
    sp_time = v['time']

    offset_guess = sp_counts[len(sp_counts)-1]
    init_amp_guess = sp_counts[2]
    decay_guess = 10

    figure5 = plt.figure(5)
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
        figure5.savefig(datapath+'\\spin_pumping.png')

        #Save a dat file for use in e.g. Origin with the rabi oscillation.
        curr_date = '#'+time.ctime()+'\n'
        col_names = '#Col0: Interpulse delay (ns)\tCol1: Integrated counts\tCol2: SSRO corr\n'
        col_vals = str()
        for k in arange(noof_datapoints):
            col_vals += num2str(tau_free_evol[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\t'+num2str(SSRO_readout_corr[k],2)+'\n'
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
    
    e = np.load(datapath+'\\'+suffix+'-1_statics_and_parameters.npz')
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
        f = np.load(datapath+'\\'+spin_ro_file[idx])
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
            fit_result,p=fit.fit1d(ro_time[arange(4,len(ro_time)-1)], 
                    counts_during_readout[arange(4,len(ro_time)-1)], 
                    common.fit_exp_decay_with_offset, 
                    offset_guess, init_amp_guess, decay_guess,
                    do_plot = True, do_print = True, newfig = False,
                    plot_fitparams_xy = (0.5,0.5),
                    ret=True)
            if fit_result != False:
                fit_par.append(fit_result['params'][2])
            else:
                fit_par.append(0)
        plt.plot(ro_time, counts_during_readout, 'or')
        plt.xlabel('Read-out duration ($\mu$s)')
        plt.ylabel('Integrated counts')
        plt.title('Read-out with MW, driving $f$ ='+num2str(f_drive/1E6,1)+\
                ' MHz, power = '+num2str(mwpower,0)+' dBm')
        if save:
            figure1.savefig(datapath+'\\histogram_integrated'+num2str(idx,0)+'.png')
        plt.clf()

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
        plt.clf()

        f.close()
        
        ###########################################
        ######## SPIN PUMPING #####################
        ###########################################
        v = np.load(datapath+'\\'+sp_file[idx])
        sp_counts = v['counts']
        sp_time = v['time']

        offset_guess = sp_counts[len(sp_counts)-1]
        init_amp_guess = sp_counts[2]
        decay_guess = 10

        figure3 = plt.figure(3)
        if fit_data:
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
        plt.clf()
    
    if save:
        #Save a dat file for use in e.g. Origin with the rabi oscillation.
        curr_date = '#'+time.ctime()+'\n'
        col_names = '#Col0: MW Freq (ns)\tCol1: Integrated counts\n'
        col_vals = str()
        for k in arange(len(mw_freq)):
            col_vals += num2str(mw_freq[k],4)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()
    
    if fit_data:
        plt.close('all')
        print len(mw_freq)
        print len(fit_par)
        figure4 = plt.figure(4)
        plt.plot(mw_freq/1E6,fit_par, '-r')
        plt.xlabel('MW frequency (MHz)')
        plt.ylabel('Decay constant')
        
        if save:
            figure4.savefig(datapath+'\\decay_constant_vs_mw_freq.png')
        plt.clf()



    return fit_par

def plot_esr(datapath, fit_data = True, save = True, f_dip = 2.828E9,msplusone=False,Zsplitting=35e6):
    plt.close('all')
    ###########################################
    ######## MEASUREMENT SPECS ################
    ###########################################
    files = os.listdir(datapath)
    
    for k in files:
        if '.npz' in k:
            data_file = k


    data = np.load(datapath+'\\'+data_file)

    mw_freq = data['freq']
    counts = data['counts']
    data.close()

    f_dip_guess=f_dip
    offset_guess = counts.max()
    dip_depth_guess = offset_guess - counts.min()
    width_guess = 5e-3
    

    if msplusone:
        noof_dips = 2
        dip_separation = Zsplitting
    else:
        noof_dips = 1
        dip_separation=0

    if fit_data:
        figure2 = plt.figure(2)
        figure2.clf()
        fit_res=fit.fit1d(mw_freq/1E9, counts, common.fit_gauss, 
            offset_guess, dip_depth_guess, f_dip_guess/1E9,width_guess,
            do_plot = True, do_print = True, newfig = False)
    
    
    print fit_res
    plt.plot(mw_freq/1E9,counts, '-k')
    plt.xlabel('MW frequency (GHz)')
    plt.ylabel('Integrated counts')
    plt.title('MW frequency sweep')
#, power = '+num2str(mwpower,0)+' dBm)
    #plt.text(0.1*(mw_max_freq+mw_min_freq),max(counts_during_readout),datapath)
    if save:
        figure2.savefig(datapath+'\\esr_data.png')

def plot_Pulse_cal(datapath, fit_data = True, save = True):

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


    e = np.load(datapath+'\\'+stats_params_file)

    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    min_pulse_nr = e['min_pulse_nr']
    max_pulse_nr = e['max_pulse_nr']
    noof_datapoints = e['noof_datapoints']
    noof_reps = e['completed_repetitions']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    

    f = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    repetitions = f['sweep_axis']
    SSRO_counts = f['SSRO_counts']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    pulse_nr = linspace(min_pulse_nr,max_pulse_nr,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)
    SSRO_readout = sum(SSRO_counts, axis = 1)/float(noof_reps)
    

    #########################################
    ############ FITTING ####################
    #########################################
    
    #FIXME to be implemented
    figure2=plt.figure(2)
    figure2.clf()
    plt.plot(pulse_nr,SSRO_readout, 'sk')
    plt.xlabel('Pulse nr')
    plt.ylabel('P ms=0')
    plt.title('MW length sweep, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    #plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
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

    v = np.load(datapath+'\\'+sp_file)
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
            col_vals += num2str(pulse_nr[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return True

def plot_Pulse_cal_amp(datapath, fit_data = True, save = True):

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

    e = np.load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    min_amp = e['min_pulse_amp']
    max_amp = e['max_pulse_amp']
    noof_datapoints = e['noof_datapoints']
    noof_reps = e['completed_repetitions']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    repetitions = f['sweep_axis']
    SSRO_counts = f['SSRO_counts']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    amp = linspace(min_amp,max_amp,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)
    SSRO_readout = sum(SSRO_counts, axis = 1)/float(noof_reps)

    

    #########################################
    ############ FITTING ####################
    #########################################
    
    #FIXME to be implemented
    figure2=plt.figure(2)
    plt.plot(amp,SSRO_readout, 'sk')
    plt.xlabel('Pulse amp')
    plt.ylabel('P ms=0')
    plt.title('MW length sweep, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    #plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
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

    v = np.load(datapath+'\\'+sp_file)
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
            col_vals += num2str(amp[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return True

def plot_Pulse_cal_time(datapath, fit_data = True, save = True):

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


    e = np.load(datapath+'\\'+stats_params_file)
    f_drive = e['mw_drive_freq']
    mwpower = e['mw_power']
    min_amp = e['min_pulse_amp']
    max_amp = e['max_pulse_amp']
    min_time = e['min_time']
    max_time = e['max_time']
    noof_datapoints = e['noof_datapoints']
    noof_reps = e['completed_repetitions']
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    f = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = f['counts']
    repetitions = f['sweep_axis']
    SSRO_counts = f['SSRO_counts']
    t = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    delay_time = linspace(min_time,max_time,noof_datapoints)
    amp = linspace(min_amp,max_amp,noof_datapoints)
    counts_during_readout = sum(raw_counts, axis = 1)
    SSRO_readout = sum(SSRO_counts, axis = 1)/float(noof_reps)

    

    #########################################
    ############ FITTING ####################
    #########################################
    
    #FIXME to be implemented
    figure2=plt.figure(2)
    plt.plot(delay_time,SSRO_readout, 'sk')
    plt.xlabel('time between CORPSE pulses [ns]')
    plt.ylabel('P ms=0')
    plt.title('MW length sweep, driving $f$ ='+num2str(f_drive/1E6,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    #plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
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
    v = np.load(datapath+'\\'+sp_file)
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
            col_vals += num2str(amp[k],2)+'\t'+num2str(counts_during_readout[k],0)+'\n'
        fo = open(datapath+'\\integrated_histogram.dat', "w")
        for item in [curr_date, col_names, col_vals]:
            fo.writelines(item)
        fo.close()

    return True
