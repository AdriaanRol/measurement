plt.close('all')

def plot_SSRO_data(datapath, noof_datapoints = 20, mw_min_len = 0, mw_max_len = 200, SSRO_duration = 30):
    f = load(datapath+'\\spin_control-0_Spin_RO.npz')
    raw_counts = f['counts']
    repetitions = f['repetitions']
    time = f['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    print reps_per_point
    
    idx = 0
    add_ms0 = 0
    add_ms1 = 0
    ms0_vs_mwlen = zeros(noof_datapoints)
    ms1_vs_mwlen = zeros(noof_datapoints)
    norm_factor = zeros(noof_datapoints)
    counts_during_readout = zeros(noof_datapoints)
    mw_len = linspace(mw_min_len,mw_max_len,noof_datapoints)
    total_hist = zeros([noof_datapoints,SSRO_duration])
    for k in arange(noof_datapoints):
        
        proper_entries = arange(k,tot_size,noof_datapoints)
        for m in proper_entries:
            total_hist[k,:] += raw_counts[m,:]
        
        counts_during_readout[k] = total_hist[k,:].sum()
        
        if counts_during_readout[k] == 0:
            add_ms1 += 1
        else:
            add_ms0 += 1
        
        ms0_vs_mwlen[k] = add_ms0
        ms1_vs_mwlen[k] = add_ms1
        
        norm_factor[k] = add_ms0+add_ms1

        add_ms0 = 0
        add_ms1 = 0
        idx += 1

        print (idx)/float(noof_datapoints)

    

    figure1 = plt.figure(1)
    plt.plot(mw_len, ms0_vs_mwlen/norm_factor, 'or')
    plt.xlabel('MW length (ns)')
    plt.ylabel('$m_s = 0$ probability')
    plt.title('Readout: $m_s = 0$')
    plt.ylim([0,1])

    figure2 = plt.figure(2)
    plt.plot(mw_len, ms1_vs_mwlen/norm_factor, 'or')    
    plt.xlabel('MW length (ns)')
    plt.ylabel('$m_s = \pm 1$ probability')
    plt.title('Readout: $m_s \pm 1$')
    plt.ylim([0,1])

    figure3 = plt.figure(3)
    plt.plot(mw_len,counts_during_readout, 'sr')
    plt.xlabel('Readout time (ns)')
    plt.ylabel('Integrated counts')
    plt.title('Total histogram')
    figure3.savefig(datapath+'\\histogram_integrated.png')

    figure4 = plt.figure(figsize=(14.0,6.0))
    plt.imshow(total_hist, cmap = 'hot')
    plt.xlabel('Readout time (us)')
    plt.ylabel('MW repetition number')
    plt.title('Total histogram, integrated over repetitions')
    plt.colorbar()
    figure4.savefig(datapath+'\\histogram_counts_2d.png')


    f.close()
    ###########################################
    ######## CHARGE RO ########################
    ###########################################

    g = load(datapath+'\\spin_control-0_ChargeRO_before.npz')
    h = load(datapath+'\\spin_control-0_ChargeRO_after.npz')

    g.close()
    h.close()



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
        
plot_SSRO_data(r'D:\measuring\data\20120612\194724_spin_control_SIL9', 
        noof_datapoints = 40,
        mw_min_len = 0,
        mw_max_len = 3000,
        SSRO_duration = 20)
    


