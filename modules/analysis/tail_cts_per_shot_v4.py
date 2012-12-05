import os, sys, time
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from analysis import fit, common, rabi
import numpy as np

try:
    import speech
except:
    pass

def find_newest_data(datapath, string, exception = 'exclude_files_string'):
    
    if datapath == '':
        datapath = os.getcwd()

    files = os.listdir(datapath)
    goodfiles = []

    for k in files:
        if (string in k) and (not(exception in k)):
            goodfiles.append(k)
    
    if len(goodfiles) != 0:
        newest_data_folder = os.path.join(datapath,
                goodfiles[len(goodfiles)-1])
    else: 
        newest_data_folder = ''

    return newest_data_folder

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def rebin(a, new_binsize):
    """"Rebin a 1D numpy array"""
    noof_bins = len(a)
    if new_binsize > noof_bins:
        print 'Error: binsize exceeds array length'

    b = np.zeros(np.ceil(len(a)/np.float(new_binsize)))
    for k in np.arange(np.ceil(len(a)/np.float(new_binsize))):
        cts_in_bin = 0
        for l in np.arange(new_binsize):
            if np.int(k*new_binsize+l) > noof_bins-1:
                break
            else:
                add_terms = a[np.int(k*new_binsize+l)]
                cts_in_bin += add_terms
        b[k] = cts_in_bin 

    return b

def find_nearest(array,value):
    idx=(abs(array-value)).argmin()
    return idx
            
def rebin_centered(a, dt, start_bin, new_binsize):
    """Rebin a 1D numpy array. Chose the center bin yourself by setting
    start_bin. New binsize is in bins."""
    noof_bins = len(a)

    if new_binsize > noof_bins:
        print 'Error: binsize exceeds array length'

    #determine value of middle bin
    if start_bin-np.int(np.floor(new_binsize/2.0)) < 0:
        print 'Error: Start bin too far to the left'
    elif start_bin+np.int(np.floor(new_binsize/2.0)) > noof_bins:
        print 'Error: Start bin too far to the right'
    
    middle_bin = 0
    for x in np.arange(new_binsize):
        middle_bin += a[start_bin-np.int(np.floor(new_binsize/2.0))+x]
    
    dt_middle_bin = mean(dt[start_bin-np.int(np.floor(new_binsize/2.0)):\
            start_bin-np.int(np.floor(new_binsize/2.0))+new_binsize])
     
    #determine how many elements are left in array
    noof_bins_to_the_left = start_bin-np.int(np.floor(new_binsize/2.0))
    noof_bins_to_the_right = noof_bins - (start_bin+np.int(np.ceil(new_binsize/2.0)))
    bins_left_newarray = np.ceil(noof_bins_to_the_left/np.float(new_binsize))
    bins_right_newarray = np.ceil(noof_bins_to_the_right/np.float(new_binsize))
    predicted_output_size = bins_left_newarray + bins_right_newarray + 1
    b = np.zeros(predicted_output_size)
    dt_new = np.zeros(predicted_output_size)
    b[bins_left_newarray] = middle_bin
    dt_new[bins_left_newarray] = dt_middle_bin

    #first consider left part
    start_index_left = start_bin-np.int(np.floor(new_binsize/2.0))-1
    
    idx = 0
    temp_val = 0
    step_left = 1
    for y in np.arange(noof_bins_to_the_left):
        b[bins_left_newarray-step_left] += a[start_index_left-y]
        temp_val += dt[start_index_left-y]
        idx += 1

        if idx%new_binsize == 0:
            dt_new[bins_left_newarray-step_left] = temp_val/np.float(new_binsize)
            step_left += 1
            temp_val = 0
            idx = 0

        if (y == noof_bins_to_the_left - 1) and not idx%new_binsize == 0:
            dt_new[0] = temp_val/np.float(idx) 


        if bins_left_newarray-step_left < 0:
            break

    #then consider right part
    start_index_right = start_bin-np.int(np.floor(new_binsize/2.0))+new_binsize
    
    idx = 0
    temp_val = 0
    step_right = 0
    for y in np.arange(noof_bins_to_the_right):
        b[bins_left_newarray+1+step_right] += a[start_index_right+y]
        temp_val += dt[start_index_right+y]
        idx += 1
        if idx%new_binsize == 0:
            dt_new[bins_left_newarray+1+step_right] = temp_val/np.float(new_binsize)
            step_right += 1
            temp_val = 0
            idx = 0

        if (y == noof_bins_to_the_right - 1) and not idx%new_binsize == 0:
            dt_new[predicted_output_size-1] = temp_val/np.float(idx) 

    return b, dt_new

def optical_rabi_resonant_fit(datafile, pulse_start, pulse_end, 
        use_channel = 1, save = True, max_rabi_amp = 0.9):
    """
    can process npz files and txt files.
    use channel specifies the HH channel, can be either 0 or 1.
    """

    binsize = 256./1000.
    
    if '.npz' in datafile:
        df = np.load(datafile)
        if use_channel == 1:
            counts = df['hist_ch1']
        elif use_channel == 0:
            counts = df['hist_ch0']
    else:
        df = os.path.join(datafile)
        data = np.loadtxt(df, skiprows=10)
        counts = data[:,use_channel]
    
    x = np.arange(0,len(counts))
    time = x*binsize
    
    ###########################
    ###########################
    ## FITTING ROUTINE ########
    ###########################
    ###########################

    data_to_fit = counts

    omegaR_init_guess = 2*np.pi*100e6
    xi_init_guess = 0.2

    min_fit_bnd = pulse_start
    max_fit_bnd = pulse_end
    
    fit_range = range(find_nearest(time,min_fit_bnd),
        find_nearest(time,max_fit_bnd))
    time_fit = time[fit_range]*1E-9
    counts_fit = max_rabi_amp*counts[fit_range]/max(counts[fit_range])

    figure = plt.figure(figsize=(8., 6.))
    plt.hold(True)

    fit_result = fit.fit1d(time_fit, counts_fit, rabi.optical_rabi_damped, 
            omegaR_init_guess, xi_init_guess, time_fit[0],
            do_plot = True, newfig = False, ret = True, plot_fitonly = True,
            color = 'r', linewidth = 2.0)
    
    fitparams = fit_result[0]['params_dict']
    omegaR = fitparams['omegaR']

    plt.plot(time*1E-9, max_rabi_amp*counts/max(counts), '.', color = 'k')
    plt.title('Rabi frequency = $2\pi \cdot$'+num2str(omegaR/(2*np.pi*1E6),1)+'MHz')
    plt.xlabel('Time (s)')
    plt.ylabel('Normalized intensity (a.u.)')
    plt.ylim(0,1)
    plt.grid()
    plt.xlim(min_fit_bnd*1e-9-10e-9,max_fit_bnd*1e-9+60e-9)

    print 'Omega_R = 2*pi*'+num2str(omegaR/(2*np.pi*1e6),5)+' MHz' 
    print 'period = '+num2str(2*np.pi/omegaR*1e9,1)+' ns'

    if save:
        figure.savefig(os.path.join(os.path.split(datafile)[0],\
                'optical_rabi_fit.png'))

    return omegaR

def tail_cts_per_shot_txt_file(datapath, filename, lower, 
        tail_duration, TPQI_starts, 
        pulses_in_sequence, save_suffix = '', bin_size = 0.256, fit_tail = True, 
        save = True, tail_mode = 2):
    """Loads the Hydraharp data from the txt file and calculates the tail counts
    per shot. Lower is begin point of tail in ns, is also used for the fit. 
    datafilelocation should be including .txt, for example: r'mypath//tail_ltx.txt
    tail_mode = 0: only take data from channel 0, 
    tail_mode = 1: only take data from channel 1,
    tail_mode = 2: combine the data from both channels'"""

    min_fit_bnd = lower
    max_fit_bnd = min_fit_bnd+tail_duration

    if '.npz' in filename:
        df = np.load(os.path.join(datapath,filename))
        counts_ch0 = df['ch0_events']
        counts_ch1 = df['ch1_events']
        if tail_mode == 1:
            counts_res = counts_ch1
        elif tail_mode == 0:
            counts_res = counts_ch0
        elif tail_mode == 2:
            counts_res = counts_ch0+counts_ch1
    else:
        data_res = np.loadtxt(os.path.join(datapath,filename))
        counts_ch0 = data_res[:,0]
        counts_ch1 = data_res[:,1]
        if tail_mode == 1:
            counts_res = counts_ch1
        else:
            counts_res = counts_ch0


    x_res = np.arange(0,len(counts_res))
    time_res = x_res*bin_size

    figure3 = plt.figure(figsize=(8.0, 6.0))
    #plt.subplot(111)
    #plt.hold(True)
    #plt.plot(time_res, counts_res, '-', color = 'k')
    #plt.plot(array([lower+tail_duration,lower+tail_duration]),\
    #        array([0, max(counts_res)]), 'r', lw = 2.0)
    #plt.plot(array([lower,lower]),\
    #    array([0, max(counts_res)]), 'r', lw = 2.0)
    #plt.title('Linear scale')
    #plt.legend(('ZPL detection','Exponential decay fit'))
    #plt.xlabel('Time (ns)')
    #plt.ylabel('Normalized intensity (a.u.)')
    #plt.xlim([max(0,lower-20.0),max_fit_bnd+20.])
    #plt.grid()

    plt.subplot(111)
    plt.hold(True)
    plt.semilogy(time_res, counts_res, '-', color = 'k')
    plt.plot(np.array([lower,lower]),np.array([0, max(counts_res)]), 'r', lw = 2.0)
    plt.plot(np.array([lower+tail_duration,lower+tail_duration]),\
            np.array([0, max(counts_res)]), 'r', lw = 2.0)
    plt.title('Logarithmic scale')
    plt.xlabel('Time (ns)')
    plt.ylabel('Normalized intensity (a.u.)')
    plt.xlim([max(0,lower-20.0),max_fit_bnd+20.])
    plt.grid()


    if fit_tail:
        
        data_to_fit = counts_res

        time_pl = time_res[time_res>min_fit_bnd]
        time_fit = time_pl[time_pl<max_fit_bnd]
        counts_pl = data_to_fit[time_res>min_fit_bnd]
        counts_fit = counts_pl[time_pl<max_fit_bnd]

        fit_exp_tail = fit.fit1d(time_fit-time_fit[0],counts_fit, 
                common.fit_exp_decay_with_offset, 
                min(counts_fit), counts_fit[0], 12.0, 
                do_plot = False, ret = True)
        offset = fit_exp_tail['params_dict']['a']
        tau = fit_exp_tail['params_dict']['tau']
        amp= fit_exp_tail['params_dict']['A']
        tau_err = fit_exp_tail['error_dict']['tau']
        amp_err = fit_exp_tail['error_dict']['A']

        fit_result = offset+amp*np.exp(-(time_fit-time_fit[0])/tau)

        #plt.subplot(121)
        #plt.plot(time_fit, fit_result, '-' ,color = 'r', lw = 2.0)
        
        plt.subplot(111)
        plt.semilogy(time_fit, fit_result, '-' ,color = 'r', lw = 2.0)
        
        print 'a = '+num2str(offset,2)
        print 'A = '+num2str(amp,2)+' pm '+num2str(amp_err,2)+' ns'
        print 'tau = '+num2str(tau,2)+' pm '+num2str(tau_err,2)+' ns'

    tail_area_time = time_res[np.int(min_fit_bnd/bin_size):\
            np.int(max_fit_bnd/bin_size)]
    tail_area_ch0 = counts_ch0[np.int(min_fit_bnd/bin_size):\
            np.int(max_fit_bnd/bin_size)]
    tail_area_ch1 = counts_ch1[np.int(min_fit_bnd/bin_size):\
            np.int(max_fit_bnd/bin_size)]

    laser_pulses = pulses_in_sequence*TPQI_starts
    
    if tail_mode == 1:
        tail_counts_per_shot = tail_area_ch1.sum()/np.float(laser_pulses)
    elif tail_mode == 0:
        tail_counts_per_shot = tail_area_ch0.sum()/np.float(laser_pulses)
    else:
        tail_counts_per_shot = (tail_area_ch0.sum()+tail_area_ch1.sum())\
                /np.float(laser_pulses)

    print 'Tail counts per shot = ',num2str(tail_counts_per_shot*1E4,2),'E-4'
    plt.title('Tail counts per shot:'+num2str(tail_counts_per_shot*1E4,2)+'E-4')
    
    try:
        speech.say(num2str(tail_counts_per_shot*1E4,2)+\
                'times ten to the minus four tail counts per shot')
    except:
        pass

    if save:
        figure3.savefig(os.path.join(datapath,\
                'tail_from_txt_'+save_suffix+'.png'))



def tail_cts_per_shot(datapath, lower, tail_duration, TPQI_starts, pulses_in_sequence, 
        bin_size = 0.256, normalize = False, correct_for_bg = False, save = True, 
        delay = 1.3, file_string = 'interference'):
    """Calculates the tail counts per shot, using data generated by the interference setup (npz files). 
    Lower specifies the tail begin, TPQI_starts specifies the number of TPQI starts during the data. 
    bin_size in ns, normalize to peak height and option to correct for background"""
    
    min_bg_bnd = 0.70
    max_bg_bnd = 0.85

    print 'Analyzing tail counts per shot...' 
    current_dir = os.getcwd()
    plt.close('all')
    os.chdir(datapath)
    files = os.listdir(datapath)

    for k in np.arange(len(files)):
        right_file = (file_string in files[k]) and ('.npz' in files[k])
        
        if right_file:
            data = np.load(os.path.join(datapath,files[k]))

    ch1_counts = data['hist_ch1']
    ch0_counts = data['hist_ch0']

    if TPQI_starts == '':
        TPQI_starts = np.int(data['adwin_lt2_pars'][20][1])
        print '\tAssuming TPQI starts from npz file...'

    time = bin_size*np.arange(len(ch1_counts))
    
    bg_level_ch1 = ch1_counts[np.int(min_bg_bnd*len(ch1_counts)):\
            np.int(max_bg_bnd*len(ch1_counts))].mean()
    bg_level_ch0 = ch0_counts[np.int(min_bg_bnd*len(ch0_counts)):\
            np.int(max_bg_bnd*len(ch0_counts))].mean()
    bg_rate_ch0 = bg_level_ch0/np.float(pulses_in_sequence*TPQI_starts*bin_size*1E-9)
    bg_rate_ch1 = bg_level_ch1/np.float(pulses_in_sequence*TPQI_starts*bin_size*1E-9)
    print '\tBG level for [ch0,ch1] = ['+num2str(bg_level_ch0,1)\
            +','+num2str(bg_level_ch1,1)+'], corresponds to ['\
            +num2str(bg_rate_ch0,0)+','+num2str(bg_rate_ch1,0)+'] Hz'


    if correct_for_bg:
        ch0_counts = ch0_counts - bg_level_ch0*ones(len(ch0_counts))
        ch1_counts = ch1_counts - bg_level_ch1*ones(len(ch1_counts))
        
    if normalize:
        ch1_counts_normalized = ch1_counts/ch1_counts.max()
        ch0_counts_normalized = ch0_counts/ch0_counts.max()
    
    upper = lower + tail_duration

    tail_area_time = time[np.int(lower/bin_size):np.int(upper/bin_size)]
    tail_area_ch1 = ch1_counts[np.int((lower+delay)/bin_size):np.int((upper+delay)/bin_size)]
    tail_area_ch0 = ch0_counts[np.int((lower)/bin_size):np.int(upper/bin_size)]
    
    tail_counts_per_shot = (tail_area_ch1.sum()+tail_area_ch0.sum())\
            /np.float(TPQI_starts*pulses_in_sequence)

    figure1 = plt.figure(figsize=(16.0, 12.0))
    plt.subplot(211)
    if not normalize:
        if sum(ch0_counts) != 0:
            plt.semilogy(time, ch0_counts, '-k')
        plt.plot(np.array([lower,lower]), 
                np.array([1E-1,ch0_counts.max()]), 'r', lw = 2.0)
        plt.plot(np.array([upper,upper]), 
                np.array([1E-1,ch0_counts.max()]), 'r', lw = 2.0)
        plt.plot(np.array([time[np.int(min_bg_bnd*len(ch0_counts))],\
                time[np.int(min_bg_bnd*len(ch0_counts))]]), 
                np.array([1E-1,ch0_counts.max()]), 'g', lw = 2.0)
        plt.plot(np.array([time[np.int(max_bg_bnd*len(ch0_counts))],\
                time[np.int(max_bg_bnd*len(ch0_counts))]]), 
                np.array([1E-1,ch0_counts.max()]), 'g', lw = 2.0)        
    else:
        if sum(ch0_counts_normalized) != 0:
            plt.semilogy(time, ch0_counts_normalized, '-r')
        plt.plot(np.array([lower,lower]), 
                np.array([1E-1,ch0_counts_normalized.max()]), 'r', lw = 2.0)
        plt.plot(np.array([upper,upper]), 
                np.array([1E-1,ch0_counts_normalized.max()]), 'r', lw = 2.0)
        plt.plot(np.array([time[np.int(min_bg_bnd*len(ch0_counts))],\
                time[np.int(min_bg_bnd*len(ch0_counts))]]), 
                np.array([1E-1,ch0_counts_normalized.max()]), 'g', lw = 2.0)
        plt.plot(np.array([time[np.int(max_bg_bnd*len(ch0_counts))],\
                time[np.int(max_bg_bnd*len(ch0_counts))]]), 
                np.array([1E-1,ch0_counts_normalized.max()]), 'g', lw = 2.0)  
    
    plt.xlabel('Time after sync (ns)')
    plt.ylabel('Counts ch0')
    plt.title('Tail counts per shot = '+num2str(tail_counts_per_shot*1e4,1)+'E-4')
    plt.xlim([0,200])

    plt.subplot(212)
    if not normalize:
        if sum(ch1_counts) != 0:
            plt.semilogy(time, ch1_counts, '-k')
        plt.plot(np.array([lower+delay,lower+delay]), np.array([1E-1,ch1_counts.max()]), 
                'r', lw = 2.0)
        plt.plot(np.array([upper,upper]), np.array([1E-1,ch1_counts.max()]), 'r', lw = 2.0)
        plt.plot(np.array([time[np.int(min_bg_bnd*len(ch1_counts))],\
                time[np.int(min_bg_bnd*len(ch1_counts))]]), 
                np.array([1E-1,ch1_counts.max()]), 'g', lw = 2.0)
        plt.plot(np.array([time[np.int(max_bg_bnd*len(ch1_counts))],\
                time[np.int(max_bg_bnd*len(ch1_counts))]]), 
                np.array([1E-1,ch1_counts.max()]), 'g', lw = 2.0)     
    else:
        if sum(ch1_counts_normalized) != 0:
            plt.semilogy(time, ch1_counts_normalized, '-k')
        plt.plot(np.array([lower+delay,lower+delay]),
                np.array([1E-1,ch1_counts_normalized.max()]), 'r', lw = 2.0)
        plt.plot(np.array([upper+delay,upper+delay]), 
                np.array([1E-1,ch1_counts_normalized.max()]), 'r', lw = 2.0)
        plt.plot(np.array([time[np.int(min_bg_bnd*len(ch1_counts))],\
                time[np.int(min_bg_bnd*len(ch1_counts))]]), 
                np.array([1E-1,ch1_counts_normalized.max()]), 'g', lw = 2.0)
        plt.plot(np.array([time[np.int(max_bg_bnd*len(ch1_counts))],\
                time[np.int(max_bg_bnd*len(ch1_counts))]]), 
                np.array([1E-1,ch1_counts_normalized.max()]), 'g', lw = 2.0)  
    
    plt.xlabel('Time after sync (ns)')
    plt.ylabel('Counts ch1')
    plt.xlim([0,200])
    if save:
        figure1.savefig('tail_cts_per_shot.pdf')

    try:
        data.close()
    except:
        pass

    print '\tTail counts per shot = '+num2str(tail_counts_per_shot*1e4,1)+'E-4'

    return tail_counts_per_shot, bg_rate_ch0, bg_rate_ch1, TPQI_starts



def analyze_thresholds(datapath, threshold_lt1_before_seq, 
        threshold_lt1_after_seq, threshold_lt2_before_seq, 
        threshold_lt2_after_seq, normalize = True, save = True, say_it = True, 
        file_string = 'interference', fit_it = True, LDE_style = False):
    """Analyzes the thresholds and plots the CR counts during the run in four subplots.     
    Takes threshold values of LT1 and LT2 as input values and has an option to 
    normalize to see the fractional occurence of counts."""
    
    print 'Analyzing thresholds...' 
    current_dir = os.getcwd()
    os.chdir(datapath)
    files = os.listdir(datapath)

    for k in np.arange(len(files)):
        right_file = (file_string in files[k]) and ('.npz' in files[k])
        
        if right_file:
            data = np.load(os.path.join(datapath,files[k]))
    
    if not(LDE_style):
        CR_cts_after_seq_lt1 = data['cr_hist_LT1_first']
        CR_cts_after_seq_lt2 = data['cr_hist_LT2_first']
        CR_cts_total_lt1 = data['cr_hist_LT1_total']
        CR_cts_total_lt2 = data['cr_hist_LT2_total']
    else:
        CR_cts_after_seq_lt1 = data['adwin_lt1_CRhist_first']
        CR_cts_after_seq_lt2 = data['adwin_lt2_CRhist_first']
        CR_cts_total_lt1 = data['adwin_lt1_CRhist']
        CR_cts_total_lt2 = data['adwin_lt2_CRhist']

    nr_of_counts = np.arange(len(CR_cts_after_seq_lt1))
    CR_cts_before_seq_lt1 = CR_cts_total_lt1 - CR_cts_after_seq_lt1
    CR_cts_before_seq_lt2 = CR_cts_total_lt2 - CR_cts_after_seq_lt2

    if normalize:
        CR_cts_after_seq_lt2 = CR_cts_after_seq_lt2/\
                np.float(sum(CR_cts_after_seq_lt2))
        
        if sum(CR_cts_before_seq_lt2) == 0:
            CR_cts_before_seq_lt2 = np.zeros(len(CR_cts_before_seq_lt2))
        else:
            CR_cts_before_seq_lt2 = CR_cts_before_seq_lt2/\
                    np.float(sum(CR_cts_before_seq_lt2))

        
        times_passed_after_seq_lt2 = CR_cts_after_seq_lt2[nr_of_counts>=\
                threshold_lt2_after_seq].sum()*100
        times_passed_before_seq_lt2 =  CR_cts_before_seq_lt2[nr_of_counts>=\
                threshold_lt2_before_seq].sum()*100
        
        CR_cts_after_seq_lt1 = CR_cts_after_seq_lt1/\
                np.float(sum(CR_cts_after_seq_lt1))
        
        if sum(CR_cts_before_seq_lt1) == 0:
            CR_cts_before_seq_lt1 = np.zeros(len(CR_cts_before_seq_lt1))
        else:
            CR_cts_before_seq_lt1 = CR_cts_before_seq_lt1/\
                    np.float(sum(CR_cts_before_seq_lt1))
        times_passed_after_seq_lt1 = CR_cts_after_seq_lt1[nr_of_counts>=\
                threshold_lt1_after_seq].sum()*100
        times_passed_before_seq_lt1 =  CR_cts_before_seq_lt1[nr_of_counts>=\
                threshold_lt1_before_seq].sum()*100
    else:
        times_passed_after_seq_lt2 = CR_cts_after_seq_lt2[nr_of_counts>=\
                threshold_lt2_after_seq].sum()/\
                np.float(CR_cts_after_seq_lt2.sum())*100
        times_passed_before_seq_lt2 =  CR_cts_before_seq_lt2[nr_of_counts>=\
                threshold_lt2_before_seq].sum()/\
                np.float(CR_cts_before_seq_lt2.sum())*100
        times_passed_after_seq_lt1 = CR_cts_after_seq_lt1[nr_of_counts>=\
                threshold_lt1_after_seq].sum()*100/\
                np.float(CR_cts_after_seq_lt1.sum())
        times_passed_before_seq_lt1 =  CR_cts_before_seq_lt1[nr_of_counts>=\
                threshold_lt1_before_seq].sum()*100/\
                np.float(CR_cts_before_seq_lt1.sum())


    figure6 = plt.figure(figsize=(16.0, 12.0))
    plt.subplot(223)
    plt.hold(True)
    if fit_it and sum(CR_cts_after_seq_lt2) != 0:
        fit_result,p = fit.fit1d(nr_of_counts, 
                CR_cts_after_seq_lt2, 
                common.fit_gauss, 0, max(CR_cts_after_seq_lt2), 
                find_nearest(CR_cts_after_seq_lt1,max(CR_cts_after_seq_lt2)), 
                10, newfig = False, do_plot=True, plot_fitresult = True, 
                plot_fitonly = True, do_print = False, ret = True, 
                plot_fitparams_xy = (0.15, 0.38), 
                color = 'r', linewidth = 1.5)

        if fit_result != False:
            x0_lt2 = fit_result['params_dict']['x0']            

        if say_it and fit_result != False:
            try:
                speech.say('LT2: '+num2str(x0_lt2,0)+'counts')
            except:
                pass 

    plt.bar(nr_of_counts,CR_cts_after_seq_lt2,
            color = '#4B0082', align = 'center')
    plt.xlabel('Number of counts')
    plt.ylabel('Fraction of occurrences')
    if normalize:
        plt.title('LT2: CR counts after sequence, passed threshold: '\
                +num2str(times_passed_after_seq_lt2,1)+'%')
    else:
        plt.title('CR counts after sequence')
    plt.xlim(-0.6,35)
    plt.ylim(0,1.1*max(CR_cts_after_seq_lt2))
    
    plt.subplot(224)
    plt.bar(nr_of_counts,CR_cts_before_seq_lt2,
            color = '#4B0082', align = 'center')
    plt.xlabel('Number of counts')
    plt.ylabel('Fraction of occurrences')
    if normalize:
        plt.title('LT2: CR counts before sequence')
    else:
        plt.title('CR counts before sequence')
    plt.xlim(-0.6,35)
    plt.ylim(0,1.1*max(CR_cts_before_seq_lt2))

    plt.subplot(221)
    plt.hold(True)

    if fit_it and sum(CR_cts_after_seq_lt1) != 0:
        fit.fit1d(nr_of_counts, 
                CR_cts_after_seq_lt1, 
                common.fit_gauss, 0, max(CR_cts_after_seq_lt1), 
                find_nearest(CR_cts_after_seq_lt1,max(CR_cts_after_seq_lt1)), 
                10, newfig = False, do_plot=True, plot_fitresult = True, 
                plot_fitonly = True, do_print = False, ret = False, 
                plot_fitparams_xy = (0.15, 0.8), 
                color = 'r', linewidth = 1.5)

        #if fit_result != None:
        #    x0_lt1 = fit_result['params_dict']['x0']

        #if say_it and fit_result != None:
        #    speech.say('LT 1: '+num2str(x0_lt1,0)+' counts')
    
    plt.bar(nr_of_counts,CR_cts_after_seq_lt1,
            color = '#4682B4', align = 'center')
    plt.xlabel('Number of counts')
    plt.ylabel('Fraction of occurrences')
    if normalize:
        plt.title('LT1: CR counts after sequence, passed threshold: '\
                +num2str(times_passed_after_seq_lt1,1)+'%')
    else:
        plt.title('CR counts after sequence')
    plt.xlim(-0.6,80)
    plt.ylim(0,1.1*max(CR_cts_after_seq_lt1))
    
    plt.subplot(222)
    plt.bar(nr_of_counts,CR_cts_before_seq_lt1,
            color = '#4682B4', align = 'center')
    plt.xlabel('Number of counts')
    plt.ylabel('Fraction of occurrences')
    if normalize:
        plt.title('LT1: CR counts before sequence')
    else:
        plt.title('CR counts before sequence')
    plt.xlim(-0.6,80)
    plt.ylim(0,1.1*max(CR_cts_before_seq_lt1))
    
    if save:
        if normalize:
            figure6.savefig('CR_information_LT1_and_LT2_normalized.pdf')
            figure6.savefig('CR_information_LT1_and_LT2_normalized.png')
        else:
            figure6.savefig('CR_information_LT1_and_LT2.pdf')
            figure6.savefig('CR_information_LT1_and_LT2.png')


    return times_passed_before_seq_lt1, times_passed_after_seq_lt1, \
            times_passed_before_seq_lt2, times_passed_after_seq_lt2

    



def analyze_all(datadir, dataruns, pulses_in_sequence, threshold_lt1_before_seq, 
        threshold_lt1_after_seq, threshold_lt2_before_seq, 
        threshold_lt2_after_seq, delay = -7.0, lower = 38.4, tail_duration = 60, 
        save = True, path_string = '_interference_', correct_for_bg = False):
    """Analyzes all the 15 min. measurements in the folder datadir. 
    Automatically loads all the 15 minute measurements in the folder datadir. 
    In the array dataruns, specify the measurements that should be taken into 
    account, for example: arange(1,4) for loading measurements 1 to 3. Output 
    is an npz file in datadir that can be used to recombine several runs of 
    measurements. 
    This is done to avoid having measurements with the same suffix in the 
    same folder (such as twice interference_0). 
    Very important: path_string should contain all of the folder name, but not time,
    For example, if the folders are named, xxyyzz_antibunching_0 etc. then the 
    path string should be path_string = '_antibunching_'."""

    dirs = os.listdir(datadir)
    idx = 0
    right_dirs = list()
    
    #find statistics file containing TPQI starts
    for k in np.arange(len(dirs)):
        mark_stats = '_Statistics_cr_checks' in dirs[k]
        if mark_stats:
            print 'Found statistics file...'
            statistics = np.loadtxt(os.path.join(datadir,dirs[k],dirs[k]+'.dat'))
            if (len(dataruns) == 1) and (dataruns == np.arange(0,1)):
                tpqi_run = statistics[0,None]
                #tpqi_starts = statistics[5,None]
                break
            else:
                tpqi_run = statistics[:,0]
                #tpqi_starts = statistics[:,5]
                break
    
    #load the actual data
    for l in dataruns:
        for k in np.arange(len(dirs)):
            if l<10:
                SUFFIX = '00'
            elif l>=10:
                SUFFIX = '0'

            mark_right = path_string+SUFFIX+num2str(l,0) in dirs[k]

            #print path_string+SUFFIX+num2str(l,0)
            #print dirs[k]
            
            #if mark_right and (len(dirs[k]) > len(path_string+num2str(l,0))+6):
            #    mark_right = False

            if mark_right:
                right_dirs.append(dirs[k])
                idx += 1
                continue
    
    if len(right_dirs) == 0:
        print 'Did not find any files'
    elif len(dataruns) == len(right_dirs):
        print 'Found all files...'
    else:
        print 'Beware, not all directories in the folder are being analyzed.'
    
    tail_over_time = np.zeros(len(right_dirs))
    bg_rate_ch0 = np.zeros(len(right_dirs))
    bg_rate_ch1 = np.zeros(len(right_dirs))
    #tpqi_starts = tpqi_starts[dataruns]
    tpqi_starts = np.zeros(len(right_dirs))
    statistics_info = np.zeros([len(right_dirs),4])

    #print os.path.join(datadir,right_dirs[0])
    
    for k in np.arange(len(right_dirs)):
        tail_over_time[k], bg_rate_ch0[k], bg_rate_ch1[k], tpqi_starts[k] = \
                tail_cts_per_shot(
                datapath = os.path.join(datadir,right_dirs[k]), 
                lower = lower, pulses_in_sequence = pulses_in_sequence, 
                tail_duration = tail_duration, TPQI_starts = '', 
                save = save, correct_for_bg = correct_for_bg, delay = delay)
        
        statistics_info[k,:] = analyze_thresholds(
                os.path.join(datadir,right_dirs[k]), 
                threshold_lt1_before_seq = threshold_lt1_before_seq, 
                threshold_lt1_after_seq = threshold_lt1_after_seq, 
                threshold_lt2_before_seq = threshold_lt2_before_seq,
                threshold_lt2_after_seq = threshold_lt2_after_seq, 
                normalize = True, save = save, fit_it = False)


        os.chdir(datadir)
        percentage_finished = np.float(k+1)/len(right_dirs)*100
        print str(k)+'. Finished: '+num2str(percentage_finished,0)+'%'


    if save:
        times_passed_before_seq_lt1 = statistics_info[:,0]
        times_passed_after_seq_lt1 = statistics_info[:,1]
        times_passed_before_seq_lt2 = statistics_info[:,2]
        times_passed_after_seq_lt2 = statistics_info[:,3]
        filename = 'statistics_run_'+num2str(dataruns.min(),0)+'_to_'+\
                num2str(dataruns.max(),0)+'.npz'

        savez(filename, tpqi_starts = tpqi_starts,
                tail_over_time = tail_over_time,
                bg_rate_ch0 = bg_rate_ch0, bg_rate_ch1 = bg_rate_ch1,                             
                times_passed_before_seq_lt1 = times_passed_before_seq_lt1, 
                times_passed_after_seq_lt1 = times_passed_after_seq_lt1, 
                times_passed_before_seq_lt2 = times_passed_before_seq_lt2,
                times_passed_after_seq_lt2 = times_passed_after_seq_lt2,
                pulses_in_sequence = pulses_in_sequence)


    figure3 = plt.figure(figsize=(12.0, 16.0))
    plt.subplot(211)
    plt.plot(dataruns,tail_over_time*1E4, '-or')
    plt.xlabel('TPQI run number')
    plt.ylabel('Tail counts per shot (x 1E-4)')
    plt.grid()
    plt.ylim([0,1.1*max(tail_over_time*1E4)])

    plt.subplot(212)
    plt.plot(dataruns,tpqi_starts[0:len(right_dirs)], '-or')
    plt.xlabel('TPQI run number')
    plt.ylabel('TPQI starts per run')
    plt.grid()
    plt.ylim([0, 1.1*tpqi_starts[0:len(right_dirs)].max()])
    if save:
        figure3.savefig('tpqi_starts_and_tail_over_time'+path_string+'.png')

def combine_runs(datapath, runs, do_g2 = True, do_draw_curve = True, save = True):
    """ Combines the measurements that are separated in different folders. 
    Different sets of measurements should be grouped in folders called runx, 
    where x is an integer. With runs = arange(x1,x2) you can specify which runs 
    should be taken into account, in this case x1 to x2. Datapath should be the 
    folder that contains the runx folders. Uses the .npz files generated in 
    g2_from_npzfiles and analyze_all. These functions should be run before this one."""
    
    print 'Combining runs...'

    current_dir = os.getcwd()
    
    tpqi_starts_allruns = tail_cts_per_shot_allruns = \
            bg_rate_ch0_allruns = bg_rate_ch1_allruns = \
            times_passed_before_seq_lt1_allruns = \
            times_passed_before_seq_lt2_allruns = \
            times_passed_after_seq_lt1_allruns = \
            times_passed_after_seq_lt2_allruns = np.array([])
    
    counts_in_peaks = g2_rebinned = 0

    for k in runs:
        npz_file = []
        npz_g2_file = []
        dirs = os.listdir(datapath)

        os.chdir(os.path.join(datapath,'run'+num2str(k,0)))
        
        dirs = os.listdir(os.getcwd())
        for j in range(len(dirs)):
            npz_indicator = dirs[j].startswith('statistics_run') \
                    and dirs[j].endswith('.npz')
            npz_g2_indicator = dirs[j].startswith('g2_information') \
                    and dirs[j].endswith('.npz')
            if npz_indicator:
                npz_file = dirs[j]
                print '\t'+num2str(k,0)+'. statistics file found'
            if npz_g2_indicator:
                npz_g2_file = dirs[j]
                print '\t'+num2str(k,0)+'. g2 file found'

        data_from_runs = np.load(npz_file)

        if do_g2:
            g2_info = np.load(npz_g2_file)
            counts_in_peaks += g2_info['counts_in_peaks']
            g2_rebinned += g2_info['g2_rebinned']
            dt_rebinned = g2_info['dt_rebinned']
            rebinsize = g2_info['rebinsize']
            peak_numbers = g2_info['peak_numbers']
            tail_duration = g2_info['tail_duration']
            measurement_rep_time = g2_info['measurement_rep_time']
            dataruns = g2_info['dataruns']
            g2_info.close

        tpqi_starts_thisrun = data_from_runs['tpqi_starts']
        bg_rate_ch0_thisrun = data_from_runs['bg_rate_ch0']
        bg_rate_ch1_thisrun = data_from_runs['bg_rate_ch1']
        tail_cts_per_shot_thisrun = data_from_runs['tail_over_time']
        times_passed_before_seq_lt1_thisrun = \
                data_from_runs['times_passed_before_seq_lt1']
        times_passed_after_seq_lt1_thisrun = \
                data_from_runs['times_passed_after_seq_lt1']
        times_passed_before_seq_lt2_thisrun = \
                data_from_runs['times_passed_before_seq_lt2']
        times_passed_after_seq_lt2_thisrun = \
                data_from_runs['times_passed_after_seq_lt2']
        pulses_in_sequence = data_from_runs['pulses_in_sequence']

        os.chdir(current_dir)
        
        tpqi_starts_allruns = np.concatenate((tpqi_starts_allruns,\
                tpqi_starts_thisrun), axis = 1)
        tail_cts_per_shot_allruns = np.concatenate((tail_cts_per_shot_allruns,\
                tail_cts_per_shot_thisrun), axis = 1)
        bg_rate_ch0_allruns = np.concatenate((bg_rate_ch0_allruns,\
                bg_rate_ch0_thisrun),axis = 1)
        bg_rate_ch1_allruns = np.concatenate((bg_rate_ch1_allruns,\
                bg_rate_ch1_thisrun),axis = 1)
        
        times_passed_before_seq_lt1_allruns = \
                np.concatenate((times_passed_before_seq_lt1_allruns,\
                times_passed_before_seq_lt1_thisrun), axis = 1)
        times_passed_before_seq_lt2_allruns = \
                np.concatenate((times_passed_before_seq_lt2_allruns,\
                times_passed_before_seq_lt2_thisrun), axis = 1)
        times_passed_after_seq_lt1_allruns = \
                np.concatenate((times_passed_after_seq_lt1_allruns,\
                times_passed_after_seq_lt1_thisrun), axis = 1)
        times_passed_after_seq_lt2_allruns = \
                np.concatenate((times_passed_after_seq_lt2_allruns,\
                times_passed_after_seq_lt2_thisrun), axis = 1)

    tpqi_runs = np.arange(len(tpqi_starts_allruns))

    print '\ttotal tpqi starts: ',tpqi_starts_allruns.sum()

    figure5 = plt.figure(figsize=(16.0,16.0))
    plt.subplot(321)
    plt.plot(tpqi_runs, tail_cts_per_shot_allruns*1E4, '-or')
    plt.ylabel('Tail counts per shot (x1E-4)')

    plt.subplot(322)
    plt.plot(tpqi_runs, tpqi_starts_allruns, '-or')
    plt.ylabel('TPQI starts in 15 minutes')

    plt.subplot(323)
    plt.plot(tpqi_runs, times_passed_before_seq_lt1_allruns, '-ob')
    plt.ylabel('Percentage passed before the sequence')

    plt.subplot(324)
    plt.plot(tpqi_runs, times_passed_after_seq_lt1_allruns, '-ob')
    plt.ylabel('Percentage passed after the sequence')
    plt.legend(['LT 1'])

    plt.subplot(325)
    plt.plot(tpqi_runs, times_passed_before_seq_lt2_allruns, '-om')
    plt.xlabel('TPQI run number')
    plt.ylabel('Percentage passed before the sequence')

    plt.subplot(326)
    plt.plot(tpqi_runs, times_passed_after_seq_lt2_allruns, '-om')
    plt.xlabel('TPQI run number')
    plt.ylabel('Percentage passed after the sequence')
    plt.legend(['LT 2'])

    if save:
        figure5.savefig(os.path.join(datapath,'measurement_overview.pdf'))

    if do_g2:
        err_in_peaks = np.sqrt(counts_in_peaks)

        x = counts_in_peaks[peak_numbers == 0]
        y = (counts_in_peaks[peak_numbers == 1]+\
                counts_in_peaks[peak_numbers == -1])/2.0
        sigmax = np.sqrt(x)
        sigmay = np.sqrt(y)
        
        contrast = 100*(1-x/(0.5*y))
        contrast_error = 100*np.sqrt((2*sigmax/y)**2+(2*x*sigmay/y**2)**2)
        
        mean_bg_rate_ch0 = np.mean(bg_rate_ch0_allruns)
        mean_bg_rate_ch1 = np.mean(bg_rate_ch1_allruns)
        single_tail_count_prob = 0.5*np.mean(tail_cts_per_shot_allruns)*\
                (1-np.exp(-tail_duration/12.0))/(1-np.exp(-60/12.0))

        bg_prob = (tail_duration*1E-9)*single_tail_count_prob*\
                (mean_bg_rate_ch0+mean_bg_rate_ch1) + (tail_duration*1E-9)**2\
                *mean_bg_rate_ch0*mean_bg_rate_ch1
        bg_contribution = bg_prob*tpqi_starts_allruns.sum()*pulses_in_sequence

        print '\tcoincidences caused by background: '+num2str(bg_contribution,1)

        figure12 = plt.figure()
        plt.bar(peak_numbers, counts_in_peaks, yerr = err_in_peaks, 
                color = '#4682B4', align = 'center', edgecolor = '#696969',
                ecolor = 'k', capsize = 5, linewidth = 1.5)
        plt.title('$g^{(2)}(\Delta t)$, contrast = '+\
                num2str(contrast,0)+'$\pm$'+num2str(contrast_error,0)+'%')
        plt.ylabel('Coincidences')
        plt.xlabel('Laser pulse number')

        idx = 0
        xtickies = list()
        for peak in peak_numbers:
            xtickies.append(num2str(peak*measurement_rep_time,0))
            idx += 1
        
        font_size = 22

        figure13 = plt.figure(figsize=(16.0, 12.0))
        plt.bar(dt_rebinned, g2_rebinned, width = rebinsize, align = 'center', 
                color = '#3D9140', edgecolor = '#000000')
        plt.title('$g^{(2)}(\Delta t)$, binwidth = '+num2str(rebinsize,0)\
                +' ns', size = font_size)
        plt.ylabel('Coincidences', size = font_size)
        plt.xlabel('$\Delta t$ (ns)', size = font_size)
        plt.xticks(peak_numbers*measurement_rep_time,xtickies)
        plt.tick_params(axis='both', labelsize = font_size)


        counts_in_peaks_corrected = counts_in_peaks - bg_contribution 
        err_in_peaks_corrected = np.sqrt(counts_in_peaks_corrected)


        x_corr = counts_in_peaks_corrected[peak_numbers==0]
        y_corr = (counts_in_peaks_corrected[peak_numbers == 1]\
                +counts_in_peaks_corrected[peak_numbers == -1])/2.0
        sigmax_corr = np.sqrt(x_corr)
        sigmay_corr = np.sqrt(y_corr)

        contrast_corrected = 100*(1-x_corr/(0.5*y_corr))
        contrast_error_corrected = 100*np.sqrt((2*sigmax_corr/y_corr)**2+\
                (2*x_corr*sigmay_corr/y**2)**2)


        figure14 = plt.figure()
        plt.bar(peak_numbers, counts_in_peaks_corrected, 
                yerr = err_in_peaks_corrected, 
                color = '#5D478B', align = 'center', edgecolor = '#696969',
                ecolor = 'k')
        plt.title('corrected $g^{(2)}(\Delta t)$, interference contrast = '+\
                num2str(contrast_corrected,0)+'$\pm$'+\
                num2str(contrast_error_corrected,0)+'%')
        plt.ylabel('Coincidences')
        plt.xlabel('Laser pulse number')

        print '\tcounts in peaks = ',counts_in_peaks

        

        if save:
            figure12.savefig(os.path.join(datapath,\
                    'cumulative_g2_single_bins.pdf'))
            figure13.savefig(os.path.join(datapath,\
                    'cumulative_g2_rebinned.pdf'))
            figure14.savefig(os.path.join(datapath,\
                    'cumulative_g2_single_bins_corrected.pdf'))

            np.savez(os.path.join(datapath, 'g2_combined.npz'), 
                    dt_rebinned = dt_rebinned,
                    g2_rebinned = g2_rebinned,
                    peak_numbers = peak_numbers,
                    counts_in_peaks = counts_in_peaks,
                    err_in_peaks = err_in_peaks,
                    contrast = contrast,
                    contrast_error = contrast_error,
                    counts_in_peaks_corrected = counts_in_peaks_corrected,
                    err_in_peaks_corrected =  err_in_peaks_corrected,
                    contrast_corrected = contrast_corrected,
                    contrast_error_corrected = contrast_error_corrected
                    )



def g2_from_npzfiles(datapath, dataruns, measurement_rep_time, laser_end, 
        tail_duration, rebinsize, rebin_around, binsize = 0.256, do_ROI = True, 
        do_plot_boundaries = False, do_rebin = True, save = True, 
        path_string = '_interference_', peak_numbers = np.arange(-2,3), delay = 0,
        save_2D_hist = False):
    """this function loads data from separate measurements (.npz files) and plots
    it as a g2, datapath should be the path consisting the 15 min run folders,
    and dataruns should be an array of numbers that indicate which runs should
    be taken into account. Ex: for run 0 to 7 use dataruns = arange(0,8) 
    pulse_end defines the end of the laser pulse, this value is used for filtering.
    Very important: path_string should contain all of the folder name, but not time,
    For example, if the folders are named, xxyyzz_antibunching_0 etc. then the 
    path string should be path_string = '_antibunching_'. """

    os.chdir(datapath)
    
    # explanation of parameters: 
    # measurement_rep_time = delay between two laser pulses in ns
    # peak_numbers = which peak numbers should show up in the g2 (ex. arange(-2,3))
    
    shift_boundary_right  = delay #ns
    total_peak_counts = np.zeros(len(peak_numbers))

    dirs = os.listdir(datapath)
    idx = 0
    right_dirs = list()
    
    # load the data from separate measurements, create a list with the right
    # directories (right_dirs) and load them. relevant data is kept in a new 
    # dictionary (d)
    
    for l in dataruns:
        for k in np.arange(len(dirs)):
            if l<10:
                SUFFIX = '00'
            elif l>10:
                SUFFIX = '0'

            mark_right = path_string+SUFFIX+num2str(l,0) in dirs[k]
            if mark_right:
                right_dirs.append(dirs[k])
                idx += 1
                continue
                  

    if len(dataruns) == len(right_dirs):
        print 'Found all files...'
    elif len(right_dirs) == 0:
        print 'Did not find any files'
    else:
        print 'Beware, not all directories in the folder are being analyzed.'

    d={}
    print 'Loading data...'

    hist_summed=np.zeros((4*measurement_rep_time,4000))   # full histogram

    for k in np.arange(len(right_dirs)):
        data = np.load(right_dirs[k]+'\\'+right_dirs[k]+'.npz')
        noof_dt_bins = len(data['dt'])
        noof_sync_bins = len(data['sync'])
        int_tail = np.zeros(noof_sync_bins)
        hist_summed+=data['counts']
        summed_counts_single_msmt = data['counts'].sum()
        summed_counts_total= hist_summed.sum()
        if k == 0:
            d['sync'] = data['sync']
            d['dt'] = data['dt']
        data.close()
        print '\t'+num2str((k+1)/float(len(right_dirs))*100,0)+'%'
            
    print '\ttotal coincidences: %s' %summed_counts_total
    d['counts_summed'] = hist_summed

    
    # plot the 2D histogram with coincidences
    figure9 = plt.figure(figsize=(16.0,9.0))

    im = plt.imshow(d['counts_summed'],origin='lower', 
            interpolation=None, cmap=cm.binary, vmin = 0, vmax=2)
    dt_xticks = np.linspace(peak_numbers.min()*measurement_rep_time, \
            peak_numbers.max()*measurement_rep_time, \
            len(peak_numbers))/binsize +len(d['dt'])/2
    sync_yticks = np.linspace(0,measurement_rep_time,6)/binsize
    xtickies = []
    ytickies = []
    
    for l in np.arange(len(peak_numbers)):
        xtickies.append(peak_numbers[l]*measurement_rep_time)
    for l in np.arange(len(sync_yticks)):
        ytickies.append(sync_yticks[l]*binsize)
                
    plt.xticks(dt_xticks, xtickies)
    plt.yticks(sync_yticks, ytickies)
    plt.ylabel('Time of ch0 w.r.t. sync (ns)')
    plt.xlabel('$\Delta t$ (ch1-ch0) (ns)')
    cb = figure9.colorbar(im,shrink=0.25,ticks=[2,1,0])
    cb.set_ticklabels(['>2','1','0'])

    if do_ROI:
        # sync_range contains the range over the sync over which is integrated. 
        # So for every dt, the sync range is different. in the loop, n runs 
        # over the dt axis, summing all coincidences in the parallellogram for 
        # each value of dt. the counts are stored in g2_counts.

        print 'Selecting ROI...'

        g2_counts = np.zeros(noof_dt_bins)

        for peak in peak_numbers:
            print '\tpeak ',peak
            tail_start = np.int((laser_end+measurement_rep_time*peak)/binsize)
            tail_end = tail_start + np.int(tail_duration/binsize)
            dt_range = np.arange(+np.int(shift_boundary_right/binsize)-\
                    np.int(tail_duration/binsize)+np.int(noof_dt_bins/2)+\
                    np.int(measurement_rep_time*peak/binsize),\
                    np.int(noof_dt_bins/2)+np.int(measurement_rep_time*peak/binsize)+\
                    np.int(tail_duration/binsize)+np.int(shift_boundary_right/binsize))
            
            sync_range = list()
            sync_range.append(np.int((laser_end+tail_duration)/binsize)) #initial start of integration
            n = 0            
            for k in dt_range:
                if n < len(dt_range)/2:
                    n += 1
                    g2_counts[k] = d['counts_summed'][sync_range,k].sum()
                    sync_range.append(np.int((laser_end+tail_duration)/binsize-n))
                    if do_plot_boundaries:
                        plt.plot(k,sync_range[len(sync_range)-1],'r.')
                        plt.plot(k,sync_range[0],'r.')
                if (n >= len(dt_range)/2) and (n<len(dt_range)):
                    n += 1
                    g2_counts[k] = d['counts_summed'][sync_range,k].sum()
                    sync_range.remove(sync_range[0])
                    
                    if do_plot_boundaries:
                        plt.plot(k,sync_range[len(sync_range)-1],'r.')
                        plt.plot(k,sync_range[0],'r.')

        if save_2D_hist:
            figure9.savefig('histogram_2D'+path_string+'.pdf',
                    format='pdf',dpi=1200)



        figure10 = plt.figure()
        if do_rebin: #rebin the data using the funcion rebin defined above
            print 'Rebinning...'
            rebin_factor = rebinsize/binsize
            expected_zero_bin = find_nearest(d['dt'],rebin_around)
            g2_rebinned, dt_rebinned = rebin_centered(g2_counts, d['dt'], 
                    start_bin = expected_zero_bin, new_binsize = rebin_factor)
            #time_shift_factor = rebinsize/2.0
            #dt_rebinned = arange(-len(g2_rebinned)/2,len(g2_rebinned)/2)*rebinsize \
            #        +ones(len(g2_rebinned))*time_shift_factor
            
            idx = 0
            xtickies = list()
            for peak in peak_numbers:
                xtickies.append(num2str(peak*measurement_rep_time,0))
                idx += 1
            
            plt.bar(dt_rebinned, g2_rebinned, width = rebinsize, 
                    align = 'center', color = '#FF4500', edgecolor = '#121212',
                    ecolor = 'k')
            plt.xlim([-1.1*len(g2_rebinned)/2*rebinsize,1.1*len(g2_rebinned)/2*rebinsize])
            plt.ylabel('Coincidences')
            plt.xlabel('$\Delta t$ (ch1-ch0) (ns)')
            plt.title('$g^{(2)}(\Delta t)$, binwidth: '+num2str(rebinsize,1)+' ns')
            plt.xticks(peak_numbers*measurement_rep_time,xtickies)

            #full rebin
            iter = 0
            counts_in_peak = np.zeros(len(peak_numbers))
            err_in_peak = np.zeros(len(peak_numbers))
            for peak in peak_numbers:
                peak_start_ns = measurement_rep_time*peak-tail_duration
                peak_end_ns = measurement_rep_time*peak+tail_duration
                single_out_peaks = g2_counts[find_nearest(d['dt'], peak_start_ns)-1\
                        :find_nearest(d['dt'], peak_end_ns)+1]

                #print dt_rebinned[0]
                #print dt_rebinned[len(dt_rebinned)-1]
                #print peak_start_ns
                #print peak_end_ns
                #print dt_rebinned[int(peak_start_ns-dt_rebinned[0]/rebinsize)]
                #print dt_rebinned[int((peak_end_ns-dt_rebinned[0])/rebinsize)]
                #print d['dt'][find_nearest(d['dt'], peak_start_ns)-1]
                #print d['dt'][find_nearest(d['dt'], peak_end_ns)+1]
                
                counts_in_peak[iter] = single_out_peaks.sum()
                #print single_out_peaks.sum()
                #print '---------'
                err_in_peak[iter] = np.sqrt(single_out_peaks.sum())
                iter += 1
            
            ref_peak_nr = 1
            
            x = counts_in_peak[peak_numbers==0]
            y = (counts_in_peak[peak_numbers == 1]+counts_in_peak[peak_numbers == -1])/2.0
            sigmax = np.sqrt(x)
            sigmay = np.sqrt(y)
            
            contrast = 100*(1-x/(0.5*y))
            contrast_error = 100*np.sqrt((2*sigmax/y)**2+(2*x*sigmay/y**2)**2)


            figure11 = plt.figure()
            plt.bar(peak_numbers, counts_in_peak, yerr = err_in_peak, 
                    color = '#6495ED', align = 'center', edgecolor = '#696969',
                    ecolor = 'k')
            plt.title('$g^{(2)}(\Delta t)$')
            plt.ylabel('Coincidences')
            plt.xlabel('Laser pulse number')
            plt.title('$g^{(2)}(\Delta t)$, interference contrast = '+\
            num2str(contrast,0)+'$\pm$'+num2str(contrast_error,0)+'%')

            if save:
                figure11.savefig('g2_single_bins'+path_string+'.png')
                filename = 'g2_information.npz' 
                savez(filename, dt = np.arange(-noof_dt_bins/2,noof_dt_bins/2)*binsize, 
                        g2 = g2_counts, 
                        dt_rebinned = dt_rebinned, g2_rebinned = g2_rebinned,
                        peak_numbers = peak_numbers, counts_in_peaks = counts_in_peak,
                        err_in_peaks = err_in_peak,
                        rebinsize = rebinsize, laser_end = laser_end, 
                        tail_duration = tail_duration, 
                        measurement_rep_time = measurement_rep_time,
                        dataruns = dataruns)


        else: #plot the original, non-rebinned g2
            plt.plot(np.arange(-noof_dt_bins/2,noof_dt_bins/2)*binsize, g2_counts)
            plt.xlim([-1.1*noof_dt_bins/2*binsize,1.1*noof_dt_bins/2*binsize])
            plt.ylabel('Coincidences')
            plt.xlabel('$\Delta t$ (ch1-ch0) (ns)')     
            plt.title('$g^{(2)}(\Delta t)$, binwidth: '+num2str(binsize,1)+' ns')


        if save:
            figure10.savefig('g2'+path_string+'.png')

        print 'Done!\n'



def draw_theoretical_curve(g2, measurement_rep_time, delay, 
        peak_numbers, height, polarization):
    
    tau1 = tau2 = 12.5e-9
    delta_omega = 2*pi*40E6
    normalization = height

    P_side = np.zeros(1000)
    td = np.linspace((min(peak_numbers)-1)*measurement_rep_time*1E-9, 
            (max(peak_numbers)+1)*measurement_rep_time*1E-9, 1000)

    for peak in peak_numbers:
        t0 = peak*measurement_rep_time*1E-9
        delay = delay*1E-9
        if peak != 0:
            P_side += (np.exp(-abs(td-t0-delay)/tau1) + \
                    np.exp(-abs(td-t0-delay)/tau2))/(tau1+tau2)
        else:   
            if polarization == 'par':
                P_perp = (np.exp(-np.abs(td-t0-delay)/tau1) + \
                        np.exp(-np.abs(td-t0-delay)/tau2))/(2*(tau1+tau2))
                P_side += -np.cos(delta_omega*(td-t0-delay))*\
                        np.exp(-np.abs(td-t0)*(tau1+tau2)/(2*tau1*tau2))/\
                        (2*(tau1+tau2)) + P_perp/2.0
            elif polarization == 'perp':
                P_side += (np.exp(-np.abs(td-t0-delay)/tau1) + \
                        np.exp(-np.abs(td-t0-delay)/tau2))/(2*(tau1+tau2))
   
    
    
    P_side = P_side/max(P_side)*normalization

    return td*1E9, P_side


def correct_for_ab(counts_in_peaks, tail_counts_1, tail_counts_2):
    
    r = tail_counts_1/float(tail_counts_2)
    tpqi_contribution = 2*r/(1+r)**2
    
    counts_peak_0 = counts_in_peaks[len(counts_in_peaks)/2]
    counts_peak_plus1 = counts_in_peaks[len(counts_in_peaks)/2+1]
    counts_peak_min1 = counts_in_peaks[len(counts_in_peaks)/2+1]
    
    x = counts_peak_0
    y = tpqi_contribution*(counts_peak_plus1 + counts_peak_min1)/2.0
    
    sigmax = np.sqrt(x)
    sigmay = np.sqrt(y)

    contrast_ab_corrected = 100*(1-x/y)
    contrast_err_ab_corrected = 100*np.sqrt((2*sigmax/y)**2+(2*x*sigmay/y**2)**2)

    counts_by_tpqi = np.zeros(len(counts_in_peaks))
    peak_numbers = range(-len(counts_in_peaks)/2+1,len(counts_in_peaks)/2+1)
    
    for k in range(len(counts_in_peaks)):
        if k == (len(counts_in_peaks)-1)/2:
            counts_by_tpqi[k] = counts_peak_0
        else:
            counts_by_tpqi[k] = counts_in_peaks[k]*tpqi_contribution
    
    print peak_numbers
    print counts_by_tpqi

    plt.figure(figsize = (8.,6.))
    plt.bar(peak_numbers, counts_by_tpqi, 
            yerr = np.sqrt(counts_by_tpqi), 
            color = '#5D478B', align = 'center', edgecolor = '#696969',
            ecolor = 'k')
    plt.title('Corrected for AB: contrast = '+num2str(contrast_ab_corrected,0)+\
            '$\pm$'+num2str(contrast_err_ab_corrected,0))
    plt.ylabel('Coincidences')
    plt.xlabel('Laser pulse number')

    return contrast_ab_corrected, contrast_err_ab_corrected
    

def calculate_contrast(counts_in_peaks, peak_numbers):
    """
    Counts in peaks should be an array with the same size as peak_numbers
    """
    x = counts_in_peaks[peak_numbers==0]
    y = (counts_in_peaks[peak_numbers == 1]+counts_in_peaks[peak_numbers == -1])/2.0
    sigmax = np.sqrt(x)
    sigmay = np.sqrt(y)

    contrast = 100*(1-x/(0.5*y))
    contrast_error = 100*np.sqrt((2*sigmax/y)**2+(2*x*sigmay/y**2)**2)

    return contrast, contrast_error





