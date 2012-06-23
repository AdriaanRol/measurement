import os, time
from numpy import *
from matplotlib import pyplot as plt
from modules.analysis import fit, rabi, common

def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def find_nearest(array,value):
    idx=(abs(array-value)).argmin()
    return idx

def plot(datapath, with_detuning = False, save = True):

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
    f_drive = e['mw_center_freq']
    mwpower = e['mw_power']
    mw_min_freq = e['min_mw_freq']
    mw_max_freq = e['max_mw_freq']
    noof_datapoints = e['noof_datapoints']

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

    figure2 = plt.figure(2)  
    plt.plot(mw_freq/1E9,counts_during_readout, 'sk')
    plt.xlabel('MW frequency (GHz)')
    plt.ylabel('Integrated counts')
    plt.title('MW frequency sweep, driving $f$ ='+num2str(f_drive/1E6,1)+\
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
    ######## CHARGE RO ########################
    ###########################################

    #g = load(datapath+'\\spin_control-0_ChargeRO_before.npz')
    #h = load(datapath+'\\spin_control-0_ChargeRO_after.npz')

    #g.close()
    #h.close()


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
        
#plot(r'C:\Documents and Settings\localadmin.TUD10238\Desktop\162245_spin_control_SIL9_lt2', save = True)
    


