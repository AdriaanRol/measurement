import qt
import data
import numpy as np
import msvcrt
import time
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq
import measurement.PQ_measurement_generator_v2 as pqm

adwin_lt2 = qt.instruments['adwin']
adwin_lt1 = qt.instruments['adwin_lt1']
awg = qt.instruments['AWG']
hharp = qt.instruments['HH_400']

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
# configure conditional repumping
time_limit = 30 #in Adwin_proII processor cycles # in units of 1us

lt1_rempump_duration = 10 # in units of 1us
lt1_probe_duration = 100 # in units of 1us
lt1_cnt_threshold = 0
lt1_counter = 2
lt1_green_power = 200e-6
lt1_ex_power = 5e-9
lt1_a_power = 5e-9

lt2_rempump_duration = 10 # in units of 1us
lt2_probe_duration = 100 # in units of 1us
lt2_cnt_threshold = 0
lt2_counter = 1
lt2_green_power = 400e-6
lt2_green_aom_voltage_zero=0.06 #voltage with minimum AOM leakage
lt2_ex_power = 5e-9
lt2_a_power = 5e-9

#configure optimisation
par_opt_lt1_green_power = 50e-6
par_opt_lt2_green_power = 50e-6
par_opt_min_cnts_lt1 = 90000
par_opt_min_cnts_lt2 = 60000
par_zpl_cts_break = 100000

# configure pulses and sequence
par_sp_duration = 5000
par_sp_voltage_lt1 = .22
par_sp_voltage_lt2 = .15
par_rabi_reps = 100
par_eom_start = 20
par_eom_off_duration = 100
par_eom_pulse_duration = 3
par_eom_pulse_offset = -15
pulse_start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset

par_aom_start = pulse_start - 35 -45 #subtract aom rise time
par_aom_duration = 2*35+par_eom_pulse_duration

par_eom_off_amplitude = -.27
par_eom_pulse_amplitude = 1.2
par_eom_overshoot_duration1 = 10
par_eom_overshoot1 = -0.07
par_eom_overshoot_duration2 = 10
par_eom_overshoot2 = -0.02

par_eom_aom_amplitude = 1

par_rabi_cycle_duration = 2*par_eom_off_duration

# Configure hydraharp
par_binsize_T3 = 8     # resolution of recorded data in HH 1ps*2**binsize_T3
par_binsize_sync=0     # bintime = 1ps * 2**(binsize_T3 + binsize_sync)
par_range_sync=4*50    # bins
par_binsize_g2=0       # bintime = 1ps * 2**(binsize_g2 + binsize_T3)
par_range_g2=4*1000    # bins
par_sync_period = 200  # ns
### end config


lt1_ex_aom_voltage = qt.instruments['MatisseAOM_lt1'].power_to_voltage(
        lt1_ex_power)
lt1_a_aom_voltage = qt.instruments['NewfocusAOM_lt1'].power_to_voltage(
        lt1_a_power)
lt1_green_aom_voltage = qt.instruments['GreenAOM_lt1'].power_to_voltage(
        lt1_green_power)

lt2_ex_aom_voltage = qt.instruments['MatisseAOM'].power_to_voltage(
        lt2_ex_power)
lt2_a_aom_voltage = qt.instruments['NewfocusAOM'].power_to_voltage(
        lt2_a_power)
lt2_green_aom_voltage = qt.instruments['GreenAOM'].power_to_voltage(
        lt2_green_power)
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

    awgcfg.configure_sequence(seq, 'hydraharp', 'ssro',
            optical_rabi = {chan_eom_aom: {'high': par_eom_aom_amplitude}} )
        
    #int(par_adwin_aom_duration*1e4)

    seq.add_element('optical_rabi', goto_target = 'idle')#'optical_rabi',event_jump_target='idle')

    seq.add_pulse('spinpumping_LT1',chan_alaser_lt1, 'optical_rabi', 
            start = 0, duration = par_sp_duration, amplitude = par_sp_voltage_lt1)

    seq.add_pulse('spinpumping_LT2',chan_alaser_lt2, 'optical_rabi', 
            start = 0, duration = par_sp_duration, amplitude = par_sp_voltage_lt2 )

    
    #Define a start point for the sequence, set amplitude to 0. actual sync pulse comes later  
    seq.add_pulse('start', chan_hhsync, 'optical_rabi', start = 0,
            start_reference='spinpumping_LT1', link_start_to='end',
            duration = 50, amplitude = 0.0)
    last = 'start'

    for i in arange(par_rabi_reps):
        #FIXME position for the initialization pulse
        
        seq.add_pulse('start'+str(i),  chan_hhsync, 'optical_rabi', 
                start = par_rabi_cycle_duration, duration = 50, 
                start_reference = last,  link_start_to = 'start') 
        last = 'start'+str(i)

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

    seq.add_element('idle', goto_target='idle', 
            event_jump_target = 'optical_rabi')
    seq.add_pulse('empty', chan_exlaser, 'idle', start=0, duration = 1000, 
            amplitude = 0)
    
    #seq.add_pulse('probe2', chan_alaser, 'wait_for_ADwin', start=-125, duration = 1000, 
    #        amplitude = par_cr_A_amplitude)
    #seq.add_pulse('probemw', chan_mw, 'wait_for_ADwin', start=-525, duration = 1000, 
    #       amplitude = 1.0)

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()


def optimize():
    awg.set_ch4_marker1_low(0)
    adwin_lt1.set_simple_counting()
    adwin_lt2.set_simple_counting()
    ins_green_aom_lt1.set_power(par_opt_lt1_green_power)
    ins_green_aom_lt2.set_power(par_opt_lt2_green_power)
    ins_newfocus_aom_lt1.set_power(0)
    ins_newfocus_aom_lt2.set_power(0)
    ins_matisse_aom_lt1.set_power(0)
    ins_matisse_aom_lt2.set_power(0)
    
    print 'Simple counting'
    
    qt.msleep(5)
    
    if (adwin_lt1.get_countrates()[1] < par_opt_min_cnts_lt1):
        print 'optimizing lt1: countrate', adwin_lt1.get_countrates()[1]
        ins_optimiz0r_lt1.optimize(cnt=2)
        ins_optimiz0r_lt1.optimize(cnt=2)
        ins_optimiz0r_lt1.optimize(cnt=2)
    if (adwin_lt2.get_countrates()[0] < par_opt_min_cnts_lt2):
        print 'optimizing lt2: countrate', adwin_lt2.get_countrates()[0]
        ins_optimiz0r_lt2.optimize(cnt=1)  
        ins_optimiz0r_lt2.optimize(cnt=1)
        ins_optimiz0r_lt2.optimize(cnt=1)
    
    #check for bad suppression
    awg.set_ch4_marker1_low(0.3)
    counts_with_red = adwin_lt1.get_countrates()[0]
    print 'Countrate in ZPL with red on: ', counts_with_red
    awg.set_ch4_marker1_low(0)
    
    if counts_with_red > par_zpl_cts_break:
        ins_optimiz0r_lt1.optimize(cnt=2)
        qt.msleep(0.1)
        ins_optimiz0r_lt2.optimize(cnt=1)
        qt.msleep(0.1)
        awg.set_ch4_marker1_low(0.3)
        counts_with_red = adwin_lt1.get_countrates()[0]
        print 'Reoptimizing, countrate in ZPL with red on: ', counts_with_red
    
    if (counts_with_red > par_zpl_cts_break) or (adwin_lt2.get_countrates()[1] > par_zpl_cts_break):
        awg.set_ch4_marker1_low(0)
        print 'Bad suppression detected, breaking'
        return False
    
    awg.set_ch4_marker1_low(0)
    ins_green_aom_lt1.set_power(0)
    ins_green_aom_lt2.set_power(0)
    
    return True



def measurement_cycle(hh_measurement_time):
    awg.set_runmode('SEQ')
    awg.start()    
    
    adwin_lt1.start_remote_tpqi_control(
            repump_duration=lt1_rempump_duration,
            probe_duration=lt1_probe_duration,
            cr_count_threshold=lt1_cnt_threshold,
            counter=lt1_counter,
            green_aom_voltage=lt1_green_aom_voltage,
            ex_aom_voltage=lt1_ex_aom_voltage,
            a_aom_voltage=lt1_a_aom_voltage,
            )
    
    adwin_lt2.start_remote_tpqi_control(
            repump_duration=lt2_rempump_duration,
            probe_duration=lt2_probe_duration,
            cr_time_limit=time_limit,
            cr_count_threshold=lt2_cnt_threshold,
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

    if hh_measurement_time > 0:
        hharp.StartMeas(hh_measurement_time)
        #[histogram,hist_ch0,hist_ch1,hist_ch1_long] = hharp.get_T3_pulsed_g2_2DHistogram_v2(
        #        binsize_T3=par_binsize_T3,
        #        binsize_sync=par_binsize_sync,
        #        range_sync=par_range_sync,
        #        binsize_g2=par_binsize_g2,
        #        range_g2=par_range_g2,
        #        sync_period = par_sync_period,
        #        )
        [histogram,hist_ch0,hist_ch1,hist_ch1_long] = hharp.get_T3_pulsed_g2_2DHistogram_v3(
                binsize_sync=par_binsize_sync,
                range_sync=par_range_sync,
                binsize_g2=par_binsize_g2,
                range_g2=par_range_g2,
                sync_period = par_sync_period,
                )
    
        
    adwin_lt2.stop_remote_tpqi_control()
    adwin_lt1.stop_remote_tpqi_control()
    
    awg.stop()
    awg.set_runmode('CONT')

    return histogram, hist_ch0,hist_ch1,hist_ch1_long

def save_and_plot_data(data,histogram,histogram_summed,hist_ch0,hist_ch1,hist_ch1_long):
    #Data processing
    
    sync = 2**(par_binsize_sync+par_binsize_T3) * arange(par_range_sync) / 1e3    #sync axis in ns
    dt = 2**(par_binsize_g2+par_binsize_T3) * linspace(-par_range_g2/2,par_range_g2/2,par_range_g2)/ 1e3 #dt axis in ns
    X,Y = meshgrid(dt, sync)
    data.create_file()
    #plt = qt.Plot3D(data, name='Interference',clear = Truprint 'Optimisation step completed'e, coorddims=(0,1), valdim=1, style='image')
    #data.add_data_point(ravel(X),ravel(Y),ravel(histogram))
    
    max_cts = 100
    cr_hist_LT1_first = physical_adwin_lt1.Get_Data_Long(71,1,max_cts)
    cr_hist_LT1_total = physical_adwin_lt1.Get_Data_Long(72,1,max_cts)
    cr_hist_LT2_first = physical_adwin.Get_Data_Long(71,1,max_cts)
    cr_hist_LT2_total = physical_adwin.Get_Data_Long(72,1,max_cts)

    filename=data.get_filepath()[:-4]
    pqm.savez(filename,
            dt=dt,
            sync=sync,
            counts=histogram,
            counts_summed = histogram_summed,
            hist_ch0=hist_ch0,
            hist_ch1=hist_ch1,
            hist_ch1_long=hist_ch1_long,
            cr_hist_LT1_first,
            cr_hist_LT1_total,
            cr_hist_LT2_first,
            cr_hist_LT2_total)

    #Plot Data
    do_plot=False
    if do_plot:
        plt = plot3(ravel(X),ravel(Y),ravel(histogram),
                style='image',palette='hot',
                title='interference')
    
        data.new_block()
        plt.set_xlabel('dt [ns]')
        plt.set_ylabel('delay wrt sync pulse [ns]')
        plt.save_png(filename)

    data.close_file()

    print 'interference, bitch'
    print '(entanglement expected in 3 weeks)'


    
    

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

    
    lt1_succes =100.*( 1.-(float(lt1_cnts_below)/lt1_cr_checks))
    lt2_succes = 100.*(1.-(float(lt2_cnts_below)/lt2_cr_checks))

    print 'lt1 : CR succes_percentage: ', lt1_succes
    print 'lt1 : CR checks: ', lt1_cr_checks
    print 'lt2 : CR succes_percentage: ', lt2_succes
    print 'lt2 : CR checks: ', lt2_cr_checks
    print 'tpqi starts: ', TPQI_starts
    print ' adwin check-trigger difference:', lt2_triggers_sent - lt1_triggers_received
    print ' adwin ok-trigger difference: ', lt1_oks_sent - lt2_oks_received
    print ''
    cr_stats.add_data_point(rep_nr,lt1_succes,lt1_cr_checks,
                            lt2_succes,lt2_cr_checks,TPQI_starts,lt1_repump_cts,
                            lt2_repump_cts,lt1_triggers_received,lt2_triggers_sent,
                            lt1_oks_sent,lt2_oks_received)


def test_hh():
    
    qt.mstart()
    initialize_hh()
    hharp.StartMeas(int(1e3 * 60 * 2))
#    [histogram,hist_ch0,hist_ch1,hist_ch1_long] = hharp.get_T3_pulsed_g2_2DHistogram_v2(
#                binsize_T3 = par_binsize_T3,
#                binsize_sync=par_binsize_sync,
#                range_sync=par_range_sync,
#                binsize_g2=par_binsize_g2,
#                range_g2=par_range_g2,
#                sync_period = par_sync_period,
#                )
    [histogram,hist_ch0,hist_ch1,hist_ch1_long] = hharp.get_T3_pulsed_g2_2DHistogram_v3(
                binsize_sync=par_binsize_sync,
                range_sync=par_range_sync,
                binsize_g2=par_binsize_g2,
                range_g2=par_range_g2,
                sync_period = par_sync_period,
                )
    data = qt.Data(name='interference test_hh')
    data.add_coordinate('dt')
    data.add_coordinate('sync')
    data.add_value('counts')
    
    cr_stats = qt.Data(name = 'Statistics_cr_checks') 
    cr_stats.add_coordinate('repetition nr')
    cr_stats.add_value('lt1_cr_succes_percentage')
    cr_stats.add_value('lt1_cr_checks')
    cr_stats.add_value('lt2_cr_succes_percentage')
    cr_stats.add_value('lt2_cr_checks')
    cr_stats.add_value('tpqi_starts')
   
    save_and_plot_data(data,histogram,histogram,hist_ch0,hist_ch1,hist_ch1_long)
    qt.mend()
    optimize()

def main():

    initialize_hh()
    generate_sequence()

    # configure measurement
    repetitions = 100
    hh_measurement_time = int(1e3 * 60 * 15) #ms

    qt.mstart()

    cr_stats = qt.Data(name = 'Statistics_cr_checks') 
    cr_stats.add_coordinate('repetition nr')
    cr_stats.add_value('lt1_cr_succes_percentage')
    cr_stats.add_value('lt1_cr_checks')
    cr_stats.add_value('lt2_cr_succes_percentage')
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
    for idx in arange(repetitions):
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        
        print 'Starting measurement cycle', idx, 'current time:', time.strftime('%H:%M',time.localtime())
        [histogram,hist_ch0,hist_ch1,hist_ch1_long] = measurement_cycle(hh_measurement_time)
        print_save_cr_check_info(cr_stats,idx)    

        
        print shape(histogram)
        histogram_summed += histogram
        print 'Finished measurement cycle', idx, 'start saving'
        
        data = qt.Data(name='interference'+str(idx))
        data.add_coordinate('dt')
        data.add_coordinate('sync')
        data.add_value('counts')
        
        save_and_plot_data(data,histogram,histogram_summed,hist_ch0,hist_ch1,hist_ch1_long)
        print 'Data saving cycle', idx, 'completed'
        qt.msleep(1)

        if not optimize(): break
        print 'Optimisation step', idx, ' completed'

    cr_stats.close_file()
    qt.mend()

if __name__ == '__main__':
    #test_hh()
    #optimize()
    main()


# 



# adwin_lt2.stop_remote_tpqi_control()
# adwin_lt1.stop_remote_tpqi_control()

