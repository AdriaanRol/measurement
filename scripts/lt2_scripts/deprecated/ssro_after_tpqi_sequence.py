import qt
import data
import numpy as np
import msvcrt
import time
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq
import measurement.PQ_measurement_generator_v2 as pqm
import shutil

adwin_lt2 = qt.instruments['adwin']
adwin_lt1 = qt.instruments['adwin_lt1']
awg = qt.instruments['AWG']
hharp = qt.instruments['HH_400']

awg.set_runmode('CONT')

ins_green_aom_lt1=qt.instruments['GreenAOM_lt1']
ins_green_aom_lt2=qt.instruments['GreenAOM']

ins_matisse_aom_lt1=qt.instruments['MatisseAOM_lt1']
ins_matisse_aom_lt2=qt.instruments['MatisseAOM']

ins_newfocus_aom_lt1=qt.instruments['NewfocusAOM_lt1']
ins_newfocus_aom_lt2=qt.instruments['NewfocusAOM']

ins_optimiz0r_lt1=qt.instruments['optimiz0r_lt1']
ins_optimiz0r_lt2=qt.instruments['optimiz0r']

#make sure all green+red lasers are off:
ins_newfocus_aom_lt1.set_power(0)
ins_matisse_aom_lt1.set_power(0)
ins_green_aom_lt1.set_power(0)

ins_newfocus_aom_lt2.set_power(0)
ins_matisse_aom_lt2.set_power(0)
ins_green_aom_lt2.set_power(0)

qt.msleep(0.1)
# configure conditional repumping
time_limit = 50 #in Adwin_proII processor cycles # in units of 1us

# Measurement time
#
# debug mode removes the extra pre- and post rabi syncs. also it automatically sets the
# measurement time to 0, so no need to change that anywhere else. it also
# makes sure that the hydraharp is not initialized such that the HH software
# can be used independently. 
debug_mode = True
par_meas_time = 3 #measurement time in minutes
par_reps = 2
par_raw_path = r'D:\measuring\data\20120601\raw'

lt1_rempump_duration = 6 # in units of 1us
lt1_probe_duration = 61 # in units of 1us
lt1_cnt_threshold_prepare = 0 #20
lt1_cnt_threshold_probe = 0 #9
lt1_counter = 2
lt1_green_power = 0e-6
lt1_ex_power = 0e-9
lt1_a_power = 0e-9

lt2_rempump_duration = 6 # in units of 1us
lt2_probe_duration = 60 # in units of 1us
lt2_cnt_threshold_prepare = 100
lt2_cnt_threshold_probe = 100
lt2_counter = 1
lt2_green_power = 250e-6
lt2_green_aom_voltage_zero=0.06 #voltage with minimum AOM leakage
lt2_ex_power = 7e-9
lt2_a_power = 10e-9

#configure optimisation
par_opt_lt1_green_power = 100e-6
par_opt_lt2_green_power = 200e-6
par_opt_min_cnts_lt1 = 0 
par_opt_min_cnts_lt2 = 0# 5000
par_opt_counter_lt1 = 1     # 2 for PSB and 1 for ZPL
par_opt_counter_lt2 = 2     # 1 for PSB and 2 for ZPL
par_zpl_cts_break = 250000
par_check_redpower = 0.4 #voltage of eom-aom

# configure pulses and sequence
par_sp_duration = 5000# 5000
par_sp_power_lt1 = 7e-9         
par_sp_power_lt2 = 7e-9
par_pre_rabi_syncs =  10
par_rabi_reps = 300
par_post_rabi_syncs =  10
par_eom_start = 0
par_eom_off_duration = 65
par_eom_pulse_duration = 2
par_eom_pulse_offset = -4
pulse_start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset

par_aom_start = pulse_start - 35 -45 #subtract aom rise time
par_aom_duration = 2*23+par_eom_pulse_duration #30

par_eom_off_amplitude = -.25
par_eom_pulse_amplitude = 1.2
par_eom_overshoot_duration1 = 10
par_eom_overshoot1 = -0.05
par_eom_overshoot_duration2 = 10
par_eom_overshoot2 = -0.02

par_eom_aom_amplitude = 1.0

par_rabi_cycle_duration = 2*par_eom_off_duration

# Parameters pulse gating unit #
use_pulse_gating_module = False #flag if the unit should be used
par_gate_start_offset = 0   #shifts your counting window over the pulse
par_gate_duration = 40      #determines the length of the counting window


# Configure hydraharp
par_binsize_T3 = 8     # resolution of recorded data in HH 1ps*2**binsize_T3
par_binsize_sync=0     # bintime = 1ps * 2**(binsize_T3 + binsize_sync)
par_range_sync=4*130    # bins
par_binsize_g2=0       # bintime = 1ps * 2**(binsize_g2 + binsize_T3)
par_range_g2=4*1000    # bins
par_sync_period = 130  # ns
par_max_pulses = 300
### end config

# region of interest settings
par_laser_end_ch0 = 150#259     # last bin of laser pulse ch0
par_laser_end_ch1 = 153#262
par_tail_roi = 156          # how many bins the tail is long



lt1_ex_aom_voltage = qt.instruments['MatisseAOM_lt1'].power_to_voltage(
        lt1_ex_power)
ins_newfocus_aom_lt1.set_cur_controller('ADWIN')
lt1_a_aom_voltage = qt.instruments['NewfocusAOM_lt1'].power_to_voltage(
        lt1_a_power)
lt1_green_aom_voltage = qt.instruments['GreenAOM_lt1'].power_to_voltage(
        lt1_green_power)
ins_newfocus_aom_lt1.set_cur_controller('AWG')
par_sp_voltage_lt1 = qt.instruments['NewfocusAOM_lt1'].power_to_voltage(
        par_sp_power_lt1)
ins_newfocus_aom_lt1.set_cur_controller('ADWIN')

lt2_ex_aom_voltage = qt.instruments['MatisseAOM'].power_to_voltage(
        lt2_ex_power)
ins_newfocus_aom_lt2.set_cur_controller('ADWIN')
lt2_a_aom_voltage = qt.instruments['NewfocusAOM'].power_to_voltage(
        lt2_a_power)
lt2_green_aom_voltage = qt.instruments['GreenAOM'].power_to_voltage(
        lt2_green_power)
ins_newfocus_aom_lt2.set_cur_controller('AWG')
par_sp_voltage_lt2 = qt.instruments['NewfocusAOM'].power_to_voltage(
        par_sp_power_lt2)
ins_newfocus_aom_lt2.set_cur_controller('ADWIN')

#print lt2_green_aom_voltage 



def generate_sequence(do_program=True):
    seq = Sequence('tpqi_remote')
    
    # vars for the channel names
    chan_hhsync = 'HH_sync'         # historically PH_start
    chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
    chan_exlaser = 'AOM_Matisse'    # ok
    chan_alaser_lt2 = 'AOM_Newfocus'    # ok
    chan_alaser_lt1 = 'AOM_Newfocus_lt1'
    chan_adwinsync = 'ADwin_sync'   # ok
    chan_eom = 'EOM_Matisse'
    chan_eom_aom = 'EOM_AOM_Matisse'

    awgcfg.configure_sequence(seq, 'hydraharp',
            optical_rabi = {chan_eom_aom: {'high': par_eom_aom_amplitude}, 
                chan_alaser_lt1: {'high': par_sp_voltage_lt1}},
            ssro = {chan_alaser_lt2: {'high': par_sp_voltage_lt2}})
        

    seq.add_element('optical_rabi', goto_target = 'idle')#'optical_rabi',event_jump_target='idle')

    seq.add_pulse('spinpumping_LT1',chan_alaser_lt1, 'optical_rabi', 
            start = 0, duration = par_sp_duration)

    seq.add_pulse('spinpumping_LT2',chan_alaser_lt2, 'optical_rabi', 
            start = 0, duration = par_sp_duration)

    
    #Define a start point for the sequence, set amplitude to 0. actual sync pulse comes later  
    if debug_mode:
        seq.add_pulse('hh_debug_sync', chan_hhsync, 'optical_rabi', start = 0,
                duration = 50, amplitude = 0.0)
    
    
    seq.add_pulse('start', chan_hhsync, 'optical_rabi', start = 0,
            start_reference='spinpumping_LT1', link_start_to='end',
            duration = 50, amplitude = 0.0)

    last_start = 'start'
    seq.add_pulse('start_marker', chan_hh_ma1, 'optical_rabi', 
            start = par_rabi_cycle_duration/2,
            start_reference='start', link_start_to='end',
            duration = 50)

    for i in arange(par_rabi_reps):
        #FIXME position for the initialization pulse
        
        seq.add_pulse('start'+str(i),  chan_hhsync, 'optical_rabi',         
                start = par_rabi_cycle_duration, duration = 50, 
                amplitude = 2.0, start_reference = last_start,  
                link_start_to = 'start') 
        last_start = 'start'+str(i)

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'optical_rabi', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last_start,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'optical_rabi', 
                start = par_aom_start, duration = par_aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_off_amplitude,
                start = par_eom_start, duration = par_eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_pulse_amplitude - par_eom_off_amplitude,
                start = par_eom_start + par_eom_off_duration/2 + \
                        par_eom_pulse_offset, duration = par_eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_overshoot1,
                start = par_eom_start + par_eom_off_duration/2 + \
                        par_eom_pulse_offset + par_eom_pulse_duration, 
                duration = par_eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_overshoot2,
                start = par_eom_start + par_eom_off_duration/2 + \
                        par_eom_pulse_offset + par_eom_pulse_duration + \
                        par_eom_overshoot_duration1, 
                duration = par_eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_off_amplitude,
                start = par_eom_start+par_eom_off_duration, 
                duration = par_eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_pulse_amplitude + par_eom_off_amplitude,
                start = par_eom_start+par_eom_off_duration + \
                        int(par_eom_off_duration/2) + par_eom_pulse_offset, 
                duration = par_eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_overshoot1, 
                start = par_eom_start+par_eom_off_duration + \
                        int(par_eom_off_duration/2) + par_eom_pulse_offset + \
                        par_eom_pulse_duration, 
                duration = par_eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_overshoot2, 
                start = par_eom_start+par_eom_off_duration + \
                        int(par_eom_off_duration/2) + par_eom_pulse_offset + \
                        par_eom_pulse_duration + par_eom_overshoot_duration1, 
                duration = par_eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        if use_pulse_gating_module:
            seq.add_pulse('gate'+str(i),  chan_pulse_gating_module, 'optical_rabi', 
                amplitude = 2., 
                start = par_eom_start + par_eom_off_duration/2 + \
                        par_eom_pulse_offset + par_gate_start_offset, 
                duration = par_gate_duration, 
                start_reference = last, link_start_to = 'start')

    first_sync = 'start0'
    last_sync = 'start'+str(par_rabi_reps-1)

    if not debug_mode:
        last = first_sync
        for i in arange(par_pre_rabi_syncs):
            seq.add_pulse('pre_start'+str(i),  chan_hhsync, 'optical_rabi', 
                    start = -par_rabi_cycle_duration, duration = 50, 
                    start_reference = last,  link_start_to = 'start') 
            last = 'pre_start'+str(i)

        last = last_sync
        for i in arange(par_post_rabi_syncs):
            seq.add_pulse('post_start'+str(i),  chan_hhsync, 'optical_rabi', 
                    start = par_rabi_cycle_duration, duration = 50, 
                    start_reference = last,  link_start_to = 'start') 
            last = 'post_start'+str(i)

    seq.add_element('idle', goto_target='idle', 
            event_jump_target = 'optical_rabi')
    seq.add_pulse('empty', chan_exlaser, 'idle', start=0, duration = 1000, 
            amplitude = 0)
    

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()



def measurement_cycle(hh_measurement_time):
    awg.set_runmode('SEQ')
    awg.start()    
    
    adwin_lt1.start_remote_tpqi_control(
            repump_duration=lt1_rempump_duration,
            probe_duration=lt1_probe_duration,
            cr_count_threshold_probe=lt1_cnt_threshold_probe,
            cr_count_threshold_prepare=lt1_cnt_threshold_prepare,          
            counter=lt1_counter,
            green_aom_voltage=lt1_green_aom_voltage,
            ex_aom_voltage=lt1_ex_aom_voltage,
            a_aom_voltage=lt1_a_aom_voltage,
            )
    adwin_lt2.start_remote_tpqi_control(
            repump_duration=lt2_rempump_duration,
            probe_duration=lt2_probe_duration,
            cr_time_limit=time_limit,
            cr_count_threshold_probe=lt2_cnt_threshold_probe,
            cr_count_threshold_prepare=lt2_cnt_threshold_prepare,
            counter=lt2_counter,
            green_aom_voltage=lt2_green_aom_voltage,
            green_aom_voltage_zero=lt2_green_aom_voltage_zero,
            ex_aom_voltage=lt2_ex_aom_voltage,
            a_aom_voltage=lt2_a_aom_voltage, 
            )

    
    histogram=[]
    hist_ch0=[]
    hist_ch1=[]
    hist_ch1_long=[]
    hist_roi=[]

    if not debug_mode:
        if hh_measurement_time > 0:
            hharp.StartMeas(hh_measurement_time)
        
            [histogram,hist_ch0,hist_ch1,hist_ch1_long,hist_roi] = hharp.get_T3_pulsed_g2_2DHistogram_v5(
                    binsize_sync=par_binsize_sync,
                    range_sync=par_range_sync,
                    binsize_g2=par_binsize_g2,
                    range_g2=par_range_g2,
                    max_pulses = par_max_pulses,
                    sync_period = par_sync_period,
                    laser_end_ch0 = par_laser_end_ch0,
                    laser_end_ch1 = par_laser_end_ch1,
                    tail_roi = par_tail_roi,
                    save_raw=par_raw_path
                    )
    
    if debug_mode:
        qt.msleep(par_meas_time*60)

    adwin_lt2.stop_remote_tpqi_control()
    adwin_lt1.stop_remote_tpqi_control()
    
    awg.stop()
    qt.msleep(0.1)
    awg.set_runmode('CONT')

    return histogram, hist_ch0,hist_ch1,hist_ch1_long, hist_roi

def save_and_plot_data(data,histogram,histogram_summed,hist_ch0,hist_ch1,hist_ch1_long,hist_roi,hist_roi_summed):
    #Data processing
    
    sync = 2**(par_binsize_sync+par_binsize_T3) * arange(par_range_sync) / 1e3    #sync axis in ns
    dt = 2**(par_binsize_g2+par_binsize_T3) * linspace(-par_range_g2/2,par_range_g2/2,par_range_g2)/ 1e3 #dt axis in ns

    data.create_file()
    
    max_cts = 100
    cr_hist_LT1_first = physical_adwin_lt1.Get_Data_Long(7,1,max_cts)
    cr_hist_LT1_total = physical_adwin_lt1.Get_Data_Long(8,1,max_cts)
    cr_hist_LT2_first = physical_adwin.Get_Data_Long(7,1,max_cts)
    cr_hist_LT2_total = physical_adwin.Get_Data_Long(8,1,max_cts)
    physical_adwin_lt1.Set_Data_Long(zeros(max_cts,dtype=int32),7,1,max_cts)
    physical_adwin_lt1.Set_Data_Long(zeros(max_cts,dtype=int32),8,1,max_cts)
    physical_adwin.Set_Data_Long(zeros(max_cts,dtype=int32),7,1,max_cts)
    physical_adwin.Set_Data_Long(zeros(max_cts,dtype=int32),8,1,max_cts)

    filename=data.get_filepath()[:-4]
    pqm.savez(filename,
            dt=dt,
            sync=sync,
            counts=histogram,
            counts_summed = histogram_summed,
            hist_ch0=hist_ch0,
            hist_ch1=hist_ch1,
            hist_ch1_long=hist_ch1_long,
            hist_roi = hist_roi,
            hist_roi_summed = hist_roi_summed,
            cr_hist_LT1_first=cr_hist_LT1_first,
            cr_hist_LT1_total=cr_hist_LT1_total,
            cr_hist_LT2_first=cr_hist_LT2_first,
            cr_hist_LT2_total=cr_hist_LT2_total)

    #Plot Data
    do_plot=not(debug_mode)
    if do_plot:

        plt = plot(dt,hist_roi)
        plt.set_xlabel('dt [ns]')
        plt.set_ylabel('number of coincidences in current cycle')
        plt.save_png(filename+'.png')
        plt.clear()
        plt = plot(dt,hist_roi_summed)
        plt.set_xlabel('dt [ns]')
        plt.set_ylabel('number of coincidences in total')
        plt.save_png(filename+'total.png')
        plt.clear()

    data.close_file()

   
    

def initialize_hh():
    hharp.start_T3_mode()
    hharp.calibrate()
    hharp.set_Binning(par_binsize_T3)


def print_save_cr_check_info(cr_stats,rep_nr):
 
    qt.msleep(1)

    lt1_cnts_below = adwin_lt1.remote_tpqi_control_get_cr_below_threshold_events()
    lt1_cr_checks = adwin_lt1.remote_tpqi_control_get_noof_cr_checks()
    lt2_cnts_below = adwin_lt2.remote_tpqi_control_get_cr_below_threshold_events()
    lt2_cr_checks = adwin_lt2.remote_tpqi_control_get_noof_cr_checks()
    TPQI_starts = adwin_lt2.remote_tpqi_control_get_noof_tpqi_starts()
       
    lt1_repump_cts= adwin_lt1.remote_tpqi_control_get_repump_counts()
    lt2_repump_cts= adwin_lt2.remote_tpqi_control_get_repump_counts()
    lt1_triggers_received= adwin_lt1.remote_tpqi_control_get_noof_trigger()
    lt2_triggers_sent= adwin_lt2.remote_tpqi_control_get_noof_triggers_sent()
    lt1_oks_sent = adwin_lt1.remote_tpqi_control_get_noof_oks_sent()
    lt2_oks_received = adwin_lt2.remote_tpqi_control_get_noof_lt1_oks()
    
    print 'lt1 : CR below threshold: ', lt1_cnts_below
    print 'lt1 : CR checks: ', lt1_cr_checks
    print 'lt2 : CR below threshold: ', lt2_cnts_below
    print 'lt2 : CR checks: ', lt2_cr_checks
    print 'tpqi starts: ', TPQI_starts
    print ' adwin check-trigger difference:', lt2_triggers_sent - lt1_triggers_received
    print ' adwin ok-trigger difference: ', lt1_oks_sent - lt2_oks_received
    print ''
    cr_stats.add_data_point(rep_nr,lt1_cnts_below,lt1_cr_checks,
                            lt2_cnts_below,lt2_cr_checks,TPQI_starts,lt1_repump_cts,
                            lt2_repump_cts,lt1_triggers_received,lt2_triggers_sent,
                            lt1_oks_sent,lt2_oks_received)



def end_measuring():
    ins_newfocus_aom_lt1.set_power(0)
    ins_newfocus_aom_lt2.set_power(0)
    ins_matisse_aom_lt1.set_power(0)
    ins_matisse_aom_lt2.set_power(0) 
    counters_lt1.set_is_running(1)
    counters.set_is_running(1)
    adwin_lt1.set_simple_counting()
    adwin_lt2.set_simple_counting()
    GreenAOM.set_power(lt2_green_power)
    GreenAOM_lt1.set_power(lt1_green_power)


def main():

    if not debug_mode:
        initialize_hh()

    generate_sequence()

    repetitions = par_reps
    hh_measurement_time = int(1e3 * 60 *  par_meas_time) #ms

    qt.mstart()

    cr_stats = qt.Data(name = 'Statistics_cr_checks') 
    cr_stats.add_coordinate('repetition nr')
    cr_stats.add_value('lt1_cr_below threshold')
    cr_stats.add_value('lt1_cr_checks')
    cr_stats.add_value('lt2_cr_below_threshold')
    cr_stats.add_value('lt2_cr_checks')
    cr_stats.add_value('tpqi_starts')
    cr_stats.add_value('lt1_repump_cts')
    cr_stats.add_value('lt2_repump_cts')
    cr_stats.add_value('lt1_triggers_received')
    cr_stats.add_value('lt2_triggers_sent')
    cr_stats.add_value('lt1_oks_sent')
    cr_stats.add_value('lt2_oks_received')
    cr_stats.create_file()


    histogram_summed=zeros((par_range_sync,par_range_g2))
    hist_roi_summed = zeros(par_range_g2)
    
    
    for idx in arange(repetitions):

        if msvcrt.kbhit():
            kb_char=msvcrt.getch()
            if kb_char == "q" : break
        
        print 'Starting measurement cycle', idx, 'current time:', time.strftime('%H:%M',time.localtime())
        [histogram,hist_ch0,hist_ch1,hist_ch1_long,hist_roi] = measurement_cycle(hh_measurement_time)

        print_save_cr_check_info(cr_stats,idx)    

        if not debug_mode:
            histogram_summed += histogram
            hist_roi_summed += hist_roi
        print 'Finished measurement cycle', idx, 'start saving'
        
        data = qt.Data(name='interference'+"_"+str(idx))
        data.add_coordinate('dt')
        data.add_coordinate('sync')
        data.add_value('counts')
        save_and_plot_data(data,histogram,histogram_summed,hist_ch0,hist_ch1,hist_ch1_long, hist_roi, hist_roi_summed)
        print 'Data saving cycle', idx, 'completed'
        qt.msleep(1)

        

    cr_stats.close_file()
    qt.mend()
    end_measuring()

if __name__ == '__main__':
    
    main()




