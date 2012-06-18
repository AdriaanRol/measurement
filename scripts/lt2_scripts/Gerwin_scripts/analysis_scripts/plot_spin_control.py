def plot_spin_control_figures(folder):
    plt.close('all')
    f = load(folder+'\\'+folder+'.npz')

    mw_pulse_length = f['mw_pulse_length']
    counts_during_readout = f['counts_during_readout']

    plt.figure(1)
    plt.plot(mw_pulse_length,counts_during_readout,'-or')
    plt.xlabel('MW pulse length (ns)')
    plt.ylabel('Green counts during readout')
    plt.show()



