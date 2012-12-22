#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import os
import numpy as np
import ctypes
import inspect
import time
import msvcrt
#import measurement.measurement as meas
#from measurement.AWG_HW_sequencer_v2 import Sequence
#import measurement.PQ_measurement_generator_v2 as pqm


#from measurement.config import awgchannels_lt2 as awgcfg
#from measurement.sequence import common as commonseq
#from measurement.sequence import mwseq_calibration as cal
from analysis import lde_calibration
import plot
from analysis import fit, rabi, common, esr, ramsey, spin_control

def main():
    datafolder= 'D:/msblok/Analysis/'
    date = time.strftime('%Y') + time.strftime('%m') + time.strftime('%d')
    datapath = datafolder+date + '/'
    nr_of_datapoints = 21
    
    min_pulse_amp =             0.0
    max_pulse_amp =             0.85
    amplitude = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
    
    pulse_dict = {
                "Pi":{"duration": 58.},
                "Pi_2":   {"duration": 29., "amplitude": 0.7},
                "init_state_pulse": {"duration":29. , "amplitude":0.7,  
                                "Do_Pulse": False},
                "time_between_pulses": 10.,
                "nr_of_pulses": 1.,
                "duty_cycle_time": 100.,                             
                }
    
    path = lde_calibration.find_newest_data(datapath,string='ADwin_SSRO_')
    ssro_dict=lde_calibration.ssro_calibration(path)
    #return ssro_dict
    #par['RO_duration'] = int(round(ssro_dict["t_max"]))
    #execfile('esr.py')
    #path = lde_calibration.find_newest_data(datapath,string='ESR')
    #f_fit=lde_calibration.esr_calibration(path)
    #f_drive=f_fit
    #print f_drive
    #start_measurement(cal.Pi_Pulse_amp,amplitude,pulse_dict,name='Cal_Pi_amp')
    #par['sweep_par_name'] = 'Pi Pulse amp'
    path = lde_calibration.find_newest_data(datapath,string='Cal_Pi')
    fit_amp = lde_calibration.rabi_calibration(path,close_fig=False)
    #print fit_amp
    #pulse_dict["nr_of_pulses"] = 5
    #pulse_dict["duty_cycle_time"] = 500
    #min_pulse_amp=fit_amp-0.1
    #max_pulse_amp=fit_amp+0.1
    #amplitude = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
    #print amplitude
    #start_measurement(cal.Pi_Pulse_amp,amplitude,pulse_dict,name='Cal_5_Pi_amp')
    path = lde_calibration.find_newest_data(datapath,string='Cal_5_Pi')
    fit_amp = lde_calibration.rabi_calibration(path,new_fig=False,close_fig=True)
    #print fit_amp


    # evt Rabi oscilatie
    path = lde_calibration.find_newest_data(datapath,string='rabi')
    rabi_calibration(path,ssro_dict=ssro_dict)
    
def rabi_calibration(datapath, ssro_dict={},fit_data = True, save = True,close_fig=False,new_fig=True):
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
    name=['sweep_par_name']
    noof_datapoints = e['noof_datapoints']
    noof_reps = e['completed_repetitions']
    #ro_duration=e['RO_duration']
    ro_duration=26.
    e.close()

    ###########################################
    ######## SPIN RO  #########################
    ###########################################
    
    g = np.load(datapath+'\\'+spin_ro_file)
    raw_counts = g['counts']
    SSRO_counts = g['SSRO_counts']
    repetitions = g['sweep_axis']
    t = g['time']

    tot_size = len(repetitions)
    reps_per_point = tot_size/float(noof_datapoints)

    idx = 0
    counts_during_readout = np.zeros(noof_datapoints)
    mw_len = np.linspace(mw_min_len,mw_max_len,noof_datapoints)
    counts_during_readout = np.sum(raw_counts, axis = 1)
    SSRO_readout = sum(SSRO_counts, axis = 1)/float(noof_reps)


    # Spin RO corrected for SSRO error
    #
    if ssro_dict:
        f=ssro_dict
        idx = find_nearest(f["times"],ro_duration)
        F0 = f["fid0"][idx]
        F1 = f["fid1"][idx]
        F0err = f["fid0_err"][idx]
        F1err = f["fid1_err"][idx]
        SSRO_readout_corr = zeros(len(SSRO_readout))
        readout_error = zeros(len(SSRO_readout))
        for i in arange(len(SSRO_readout)):
            
            ms0_events = SSRO_readout[i]*noof_reps
            ms1_events = noof_reps*(1-SSRO_readout[i])
            corr = spin_control.SSRO_correct(array([ms1_events,ms0_events]),
                   F0=F0,F1=F1,F0err=F0err,F1err=F1err)
            SSRO_readout_corr[i]=corr[0][0]
            readout_error[i] = corr[1][0] 
            counts_during_readout=SSRO_readout_corr
            ylabel = 'P(ms=0)'
    else:
        readout_error=zeros(len(counts_during_readout))
        ylabel = 'Integrated Counts'
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
    print f
    name= spin_ro_file[:len(spin_ro_file)-16]
    if new_fig:
        plot2 = qt.plots['Cal']
        plot2.clear()
       
        plot2 = plot.plot(mw_len, counts_during_readout, 'k',yerr=readout_error,
                title=name,name='Cal')
        plot2.add(x,fit_curve, '-r',title='fit '+name)
    else:
        plot2 = qt.plots['Cal']
        plot2.add(mw_len, counts_during_readout, 'xk',yerr=readout_error,
                title=name)
        plot2.add(x,fit_curve, '-r',title='fit '+name)
    plot2.set_xlabel(name)
    plot2.set_ylabel(ylabel)
    plot2.set_plottitle(str(name) + ' , frabi ='+num2str(f*1E3,1)+\
            ' MHz, power = '+num2str(mwpower,0)+' dBm')
    
    #plt.text(0.1*(mw_max_len+mw_min_len),max(counts_during_readout),datapath)
    if save:
        plot2.save_png(os.path.join(datapath,'figures', 'histogram_integrated'))
    g.close()
    plot1.quit()
    if close_fig:
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
    
    if 'len' in name:
        minimum = pi_pulse_len
        
    else:
        minimum=x[find_nearest(fit_curve,fit_curve.min())]

    return minimum


def num2str(num, precision): 
    return "%0.*f" % (precision, num)

def find_nearest(array,value):
    """ 
    Returns the index of an array for which the value corresponding to that index
    is closest to the specified value.
    """
    idx=(abs(array-value)).argmin()
    return idx

if __name__ == '__main__':
    main()


