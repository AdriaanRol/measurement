#from analysis import rabi

plt.close('all')

def num2str(num, precision): 
    return "%0.*f" % (precision, num)


def plot_SSRO_data(datapath, SSRO_duration = 20):
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
    time = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    
    idx = 0
    counts_during_readout = zeros(noof_datapoints)
    mw_len = linspace(mw_min_len,mw_max_len,noof_datapoints)
    for k in arange(noof_datapoints):
        counts_during_readout[k] = raw_counts[k,:].sum()
        idx += 1
        #print (idx)/float(noof_datapoints)

    #########################################
    ############ FITTING ####################
    #########################################

    x = mw_len
    y = counts_during_readout
    fit.fit1d(mw_len, counts_during_readout, rabi.fit_rabi_simple, 1/70.0, 
            3000,
            counts_during_readout.min()+(counts_during_readout.max()+counts_during_readout.min())/2.0, 
            -10.0, do_plot = True, do_print = True)


    figure1 = plt.figure(1)
    plt.plot(mw_len,counts_during_readout, 'sk')
    plt.xlabel('MW length (ns)')
    plt.ylabel('Integrated counts')
    plt.title('MW length sweep, driving $f$ ='+num2str(f_drive/1E6,1)+' MHz, power = '+num2str(mwpower,0)+' dBm')
    plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
    figure1.savefig(datapath+'\\histogram_integrated.png')



    x = 6.0
    y = 8.0

    figure2 = plt.figure(figsize=(x,y))
    plt.pcolor(raw_counts, cmap = 'hot', antialiased=False)
    plt.xlabel('Readout time (us)')
    plt.ylabel('MW repetition number')
    plt.title('Total histogram, integrated over repetitions')
    plt.colorbar()
    figure2.savefig(datapath+'\\histogram_counts_2d.png')


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
    figure6 = plt.figure(6)
    plt.plot(sp_time,sp_counts,'sg')
    plt.xlabel('Time (ns)')
    plt.ylabel('Integrated counts')
    plt.title('Spin pumping')
    v.close()
    figure6.savefig(datapath+'\\spin_pumping.png')

        
plot_SSRO_data(r'D:\measuring\data\20120618\162245_spin_control_SIL9_lt2', SSRO_duration = 25)
    


