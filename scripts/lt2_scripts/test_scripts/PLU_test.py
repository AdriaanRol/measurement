import qt
import data
import numpy as np
import msvcrt
import time
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels_lt2 as awgcfg
from measurement.sequence import common as commonseq
import measurement.PQ_measurement_generator_v2 as pqm
import shutil

os.chdir('D:/measuring/qtlab/')
reload(awgcfg)
os.chdir('D:/measuring/user/scripts/lt2_scripts/test_scripts/')

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

#ins_newfocus_aom_lt2.set_power(0)
ins_matisse_aom_lt2.set_power(0)
ins_green_aom_lt2.set_power(0)

qt.msleep(0.1)
# configure conditional repumping
#
debug_mode=True
# Measurement time
#
time_limit = 130

par_meas_time = 3 #measurement time in minutes
par_reps=1
par_raw_path=''

lt1_rempump_duration = 6 # in units of 1us
lt1_probe_duration = 61 # in units of 1us
lt1_cnt_threshold_prepare =0 #20
lt1_cnt_threshold_probe =0 #9
lt1_counter = 2
lt1_green_power = 250e-6
lt1_ex_power = 7e-9
lt1_a_power = 7e-9

lt2_rempump_duration = 6 # in units of 1us
lt2_probe_duration = 60 # in units of 1us
lt2_cnt_threshold_prepare = 17
lt2_cnt_threshold_probe = 9
lt2_counter = 1
lt2_green_power = 220e-6
lt2_green_aom_voltage_zero=0.06 #voltage with minimum AOM leakage
lt2_ex_power = 7e-9
lt2_a_power = 7e-9


# configure pulses and sequence
par_rabi_reps = 300
par_post_rabi_syncs =  10
par_eom_start = 40
par_eom_off_duration = 70
par_eom_pulse_duration = 1
par_eom_pulse_offset = 0
pulse_start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset

par_aom_start = pulse_start - 35 -45 #subtract aom rise time
par_aom_duration = 2*23+par_eom_pulse_duration #30

par_eom_off_amplitude = -.25
par_eom_pulse_amplitude = 1.2
par_eom_overshoot_duration1 = 10
par_eom_overshoot1 = -0.03
par_eom_overshoot_duration2 = 10
par_eom_overshoot2 = -0.0

par_eom_aom_amplitude = 1.0

par_rabi_cycle_duration = 2*par_eom_off_duration

# Configure hydraharp
par_binsize_T3 = 8     # resolution of recorded data in HH 1ps*2**binsize_T3
par_range_g2 = 4000 # bins
par_sync_period = 1000  # ns
### end config

# region of interest settings

par_plu_gate_duration=100
par_el_repetitions=90


lt1_ex_aom_voltage = qt.instruments['MatisseAOM_lt1'].power_to_voltage(
        lt1_ex_power)
ins_newfocus_aom_lt1.set_cur_controller('ADWIN')
lt1_a_aom_voltage = qt.instruments['NewfocusAOM_lt1'].power_to_voltage(
        lt1_a_power)
lt1_green_aom_voltage = qt.instruments['GreenAOM_lt1'].power_to_voltage(
        lt1_green_power)
ins_newfocus_aom_lt1.set_cur_controller('AWG')

ins_newfocus_aom_lt1.set_cur_controller('ADWIN')

lt2_ex_aom_voltage = qt.instruments['MatisseAOM'].power_to_voltage(
        lt2_ex_power)
ins_newfocus_aom_lt2.set_cur_controller('ADWIN')
lt2_a_aom_voltage = qt.instruments['NewfocusAOM'].power_to_voltage(
        lt2_a_power)
lt2_green_aom_voltage = qt.instruments['GreenAOM'].power_to_voltage(
        lt2_green_power)
ins_newfocus_aom_lt2.set_cur_controller('AWG')

ins_newfocus_aom_lt2.set_cur_controller('ADWIN')



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
    chan_plu = 'PLU_gate'
    #chan_pulse_gating_module = 'Pulse_gating_module'

    awgcfg.configure_sequence(seq, 'hydraharp', 'mw',
                LDE = { 
                    chan_eom_aom: { 'high' : par_eom_aom_amplitude },
                    },
                )
        
    #int(par_adwin_aom_duration*1e4)

    seq.add_element('optical_rabi', repetitions=par_el_repetitions, goto_target = 'idle')#'optical_rabi',event_jump_target='idle')

    seq.add_pulse('sync_start',  chan_hhsync, 'optical_rabi',         
            start = 0, duration = 50, 
            amplitude = 2.0) 

    seq.add_pulse('delay',  chan_hhsync, 'optical_rabi', 
            start = 0, duration = 50, amplitude = 0,
            start_reference = 'sync_start',  link_start_to = 'end') 

    last = 'delay'



    #XXXXXXXX



    seq.add_pulse('AOM',  chan_eom_aom, 'optical_rabi', 
            start = par_aom_start, duration = par_aom_duration, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_off',  chan_eom, 'optical_rabi', 
            amplitude = par_eom_off_amplitude,
            start = par_eom_start, duration = par_eom_off_duration, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_pulse',  chan_eom, 'optical_rabi', 
            amplitude = par_eom_pulse_amplitude - par_eom_off_amplitude,
            start = par_eom_start + par_eom_off_duration/2 + \
                    par_eom_pulse_offset, duration = par_eom_pulse_duration, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_overshoot1',  chan_eom, 'optical_rabi', 
            amplitude = par_eom_overshoot1,
            start = par_eom_start + par_eom_off_duration/2 + \
                    par_eom_pulse_offset + par_eom_pulse_duration, 
            duration = par_eom_overshoot_duration1, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_overshoot2',  chan_eom, 'optical_rabi', 
            amplitude = par_eom_overshoot2,
            start = par_eom_start + par_eom_off_duration/2 + \
                    par_eom_pulse_offset + par_eom_pulse_duration + \
                    par_eom_overshoot_duration1, 
            duration = par_eom_overshoot_duration2, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_off_comp',  chan_eom, 'optical_rabi', 
            amplitude = -par_eom_off_amplitude,
            start = par_eom_start+par_eom_off_duration, 
            duration = par_eom_off_duration, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_pulse_comp',  chan_eom, 'optical_rabi', 
            amplitude = -par_eom_pulse_amplitude + par_eom_off_amplitude,
            start = par_eom_start+par_eom_off_duration + \
                    int(par_eom_off_duration/2) + par_eom_pulse_offset, 
            duration = par_eom_pulse_duration, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_overshoot1_comp',  chan_eom, 'optical_rabi', 
            amplitude = -par_eom_overshoot1, 
            start = par_eom_start+par_eom_off_duration + \
                    int(par_eom_off_duration/2) + par_eom_pulse_offset + \
                    par_eom_pulse_duration, 
            duration = par_eom_overshoot_duration1, 
            start_reference = last, link_start_to = 'start')

    seq.add_pulse('EOM_overshoot2_comp',  chan_eom, 'optical_rabi', 
            amplitude = -par_eom_overshoot2, 
            start = par_eom_start+par_eom_off_duration + \
                    int(par_eom_off_duration/2) + par_eom_pulse_offset + \
                    par_eom_pulse_duration + par_eom_overshoot_duration1, 
            duration = par_eom_overshoot_duration2, 
            start_reference = last, link_start_to = 'start')
    #XXXXXXXXXXXX
    seq.add_pulse('Gate_PLU_2',  chan_plu, 'optical_rabi', 
            start = 0, duration = par_plu_gate_duration,
            start_reference = 'EOM_pulse', link_start_to = 'end')

    seq.add_pulse('Gate_PLU_1',  chan_plu, 'optical_rabi', 
            start = -100, duration = 50, 
            start_reference = 'Gate_PLU_2', link_start_to = 'start')


    seq.add_pulse('Gate_PLU_3',  chan_plu, 'optical_rabi', 
            start = 300, duration = 150,
            start_reference = 'Gate_PLU_2', link_start_to = 'end')
    seq.add_pulse('Gate_PLU_4',  chan_plu, 'optical_rabi', 
            start = 50, duration = 50,
            start_reference = 'Gate_PLU_3', link_start_to = 'end')

    seq.add_pulse('empty', chan_hh_ma1, 'optical_rabi', start=0, 
            start_reference = 'sync_start', link_start_to = 'start',
            duration = par_sync_period , amplitude = 0)

    seq.add_element('idle', goto_target='idle', 
        event_jump_target = 'optical_rabi')
     
    seq.add_pulse('empty', chan_hh_ma1, 'idle', start=0, duration = 1000, 
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
            set_repump_duration=lt1_rempump_duration,
            set_probe_duration=lt1_probe_duration,
            set_cr_count_threshold_probe=lt1_cnt_threshold_probe,
            set_cr_count_threshold_prepare=lt1_cnt_threshold_prepare,          
            set_counter=lt1_counter,
            set_green_aom_voltage=lt1_green_aom_voltage,
            set_ex_aom_voltage=lt1_ex_aom_voltage,
            set_a_aom_voltage=lt1_a_aom_voltage,
            )
    adwin_lt2.start_remote_tpqi_control(
            set_repump_duration=lt2_rempump_duration,
            set_probe_duration=lt2_probe_duration,
            set_cr_time_limit=time_limit,
            set_cr_count_threshold_probe=lt2_cnt_threshold_probe,
            set_cr_count_threshold_prepare=lt2_cnt_threshold_prepare,
            set_counter=lt2_counter,
            set_green_aom_voltage=lt2_green_aom_voltage,
            set_green_aom_voltage_zero=lt2_green_aom_voltage_zero,
            set_ex_aom_voltage=lt2_ex_aom_voltage,
            set_a_aom_voltage=lt2_a_aom_voltage, 
            )

    gated_ch1=[]
    gated_ch0=[]
    hist_ch0=[]
    hist_ch1=[]

    if hh_measurement_time > 0:
        if not(debug_mode):
            hharp.StartMeas(hh_measurement_time)
    
            [hist_ch0, hist_ch1, gated_ch0, gated_ch1] = hharp.get_T3_pulsed_g2_PLU_gated_histogram(
                    range_g2=par_range_g2,
                    sync_period = par_sync_period,
                    save_raw=par_raw_path
                    )
        else:
            qt.msleep(hh_measurement_time / 1e3)
    
    #print ' out of the measurment, total counts ch0:', hist_ch0.sum(),'ch1:', hist_ch1.sum() 
    adwin_lt2.stop_remote_tpqi_control()
    adwin_lt1.stop_remote_tpqi_control()

    awg.stop()
    qt.msleep(0.1)
    awg.set_runmode('CONT')

    return hist_ch0, hist_ch1, gated_ch0, gated_ch1

def save_and_plot_data(data,hist_ch0,hist_ch1,gated_ch0,gated_ch1,gated_ch0_summed,gated_ch1_summed ):
    #Data processing
    
    dt = 2**(par_binsize_T3) * arange(0,par_range_g2)/ 1e3 #dt axis in ns
    #X,Y = meshgrid(dt, sync)
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
            hist_ch0=hist_ch0,
            hist_ch1=hist_ch1,
            gated_ch0=gated_ch0,
            gated_ch1=gated_ch1,
            gated_ch0_summed=gated_ch0_summed,
            gated_ch1_summed=gated_ch1_summed,
            cr_hist_LT1_first=cr_hist_LT1_first,
            cr_hist_LT1_total=cr_hist_LT1_total,
            cr_hist_LT2_first=cr_hist_LT2_first,
            cr_hist_LT2_total=cr_hist_LT2_total)

    #Plot Data
    do_plot=not(debug_mode)
    if do_plot:

        plt = plot(dt,gated_ch0, name='plu_ch0', clear=True)
        plt.add(dt,hist_ch0)
        plt.set_ylog(True)
        plt.set_xrange(25,130)
        plt.set_xlabel('dt [ns]')
        plt.set_ylabel('Gated histogram ch0')
        plt.save_png(filename+'_gated_ch0.png')

        plt = plot(dt,gated_ch1, name='plu_ch1', clear=True)
        plt.add(dt,hist_ch1)
        plt.set_ylog(True)
        plt.set_xrange(25,130)        
        plt.set_xlabel('dt [ns]')
        plt.set_ylabel('Gated histogram ch1')
        plt.save_png(filename+'_gated_ch1.png')

    data.close_file()  

def print_save_cr_check_info(cr_stats,rep_nr):
 
    qt.msleep(1)

    lt1_cnts_below = adwin_lt1.get_remote_tpqi_control_var('get_cr_below_threshold_events')
    lt1_cr_checks = adwin_lt1.get_remote_tpqi_control_var('get_noof_cr_checks')
    lt2_cnts_below = adwin_lt2.get_remote_tpqi_control_var('get_cr_below_threshold_events')
    lt2_cr_checks = adwin_lt2.get_remote_tpqi_control_var('get_noof_cr_checks')
    TPQI_starts = adwin_lt2.get_remote_tpqi_control_var('get_noof_tpqi_starts')
       
    lt1_repump_cts= adwin_lt1.get_remote_tpqi_control_var('get_repump_counts')
    lt2_repump_cts= adwin_lt2.get_remote_tpqi_control_var('get_repump_counts')
    lt1_triggers_received= adwin_lt1.get_remote_tpqi_control_var('get_noof_trigger')
    lt2_triggers_sent= adwin_lt2.get_remote_tpqi_control_var('get_noof_triggers_sent')
    lt1_oks_sent = adwin_lt1.get_remote_tpqi_control_var('get_noof_oks_sent')
    lt2_oks_received = adwin_lt2.get_remote_tpqi_control_var('_get_noof_lt1_oks')
    
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

def initialize_hh():
    hharp.start_T3_mode()
    #hharp.set_MarkerEnable(1,1,1,1)
    #hharp.set_MarkerEdgesRising(1,1,1,1)
    hharp.calibrate()
    hharp.set_Binning(par_binsize_T3)


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

    counters_lt1.set_is_running(0)
    counters.set_is_running(0)
  
    if not debug_mode:initialize_hh()

    generate_sequence()

    # configure measurement
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

    gated_ch0_summed=zeros(par_range_g2)
    gated_ch1_summed=zeros(par_range_g2)
    
    for idx in arange(repetitions):
        if msvcrt.kbhit():
            kb_char=msvcrt.getch()
            if kb_char == "q" : break
        
        print 'Starting measurement cycle', idx, 'current time:', time.strftime('%H:%M',time.localtime())
        [hist_ch0, hist_ch1, gated_ch0, gated_ch1] = measurement_cycle(hh_measurement_time)

#        gated_ch0_summed += gated_ch0
#        gated_ch1_summed += gated_ch1
        print 'Finished measurement cycle', idx, 'start saving'
        
        print_save_cr_check_info(cr_stats,idx)

        data = qt.Data(name='PLU_calibration'+"_"+str(idx))
        data.add_coordinate('dt')
        data.add_value('counts')
        save_and_plot_data(data,hist_ch0, hist_ch1, gated_ch0, gated_ch1,gated_ch0_summed,gated_ch1_summed)
        print 'Data saving cycle', idx, 'completed'
        qt.msleep(1)

    cr_stats.close_file()    
    qt.mend()
    end_measuring()

if __name__ == '__main__':
    
    #generate_sequence()
    main()




