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


plt=qt.Plot2D(name='tpqi_plot',clear=True)
plt2=qt.Plot2D(name='tpqi_plot2',clear=True)

# Measurement time
#
# debug mode removes the extra pre- and post rabi syncs. also it automatically sets the
# measurement time to 0, so no need to change that anywhere else. it also
# makes sure that the hydraharp is not initialized such that the HH software
# can be used independently. 
debug_mode = True
external_hh_debug = False    #Use the hydraharp Gui?
ch0_only = False             #Flag if PSB is connected to ch1 on the HH
lt2_only = 0            #Useful if LT2 is used indepently, LT1 adwin code is not used
long_pulse_settings = False #Flag if a 10 ns pulse should be used for calibrating Rabi f.


#make sure all green+red lasers are off:
ins_newfocus_aom_lt2.set_power(0)
ins_matisse_aom_lt2.set_power(0)
ins_green_aom_lt2.set_power(0)

if not(lt2_only):
    ins_newfocus_aom_lt1.set_power(0)
    ins_matisse_aom_lt1.set_power(0)
    ins_green_aom_lt1.set_power(0)

PMServo_lt1.move_in()
PMServo.move_in()
qt.msleep(5)
print 'Powermeters in!'

awg.set_ch4_marker1_low(1.0)
power_lt1 = powermeter_lt1.get_power()*1E9
power_lt2 = powermeter.get_power()*1E9
print '     Pulse power at LT1 is ', power_lt1, ' nW'
print '     Pulse power at LT2 is ', power_lt2, ' nW'

PMServo_lt1.move_out()
PMServo.move_out()
qt.msleep(1)
print 'Powermeters out!'

qt.msleep(0.1)
# configure conditional repumping
#time_limit = 50 #in Adwin_proII processor cycles # in units of 1us

par_meas_time = 1#measurement time in minutes
par_reps = 1
raw = True              # if the raw events are to be saved
polarizations = ['perpendicular']#, 'parallel']
lt2_phase_locking_on = 0
lt2_good_phase_gate = 1


lt1_rempump_duration = 10 # in units of 1us
lt1_probe_duration = 60 # in units of 1us
lt1_cnt_threshold_prepare = 13 #NOTE
lt1_cnt_threshold_probe = 10#NOTE
lt1_counter = 2
lt1_green_power = 300e-6
lt1_ex_cr_power = 20e-9
lt1_a_cr_power = 15e-9

lt2_rempump_duration = 10 # in units of 1us
lt2_probe_duration = 60 # in units of 1us
lt2_cnt_threshold_prepare = 12 #NOTE
lt2_cnt_threshold_probe = 9 #NOTE
lt2_counter = 1
lt2_green_power = 300e-6
lt2_green_aom_voltage_zero = 0.00 #voltage with minimum AOM leakage
lt2_ex_cr_power = 20e-9
lt2_a_cr_power = 15e-9
lt2_good_phase_gate = -1
lt2_phase_locking_on=1

#configure optimisation
par_opt_lt1_green_power = 200e-6
par_opt_lt2_green_power = 50e-6
par_opt_min_cnts_lt1 = 3400 #NOTE
par_opt_min_cnts_lt2 = 160000 #NOTE
par_opt_counter_lt1 = 1     # 2 for PSB and 1 for ZPL
par_opt_counter_lt2 = 1     # 1 for PSB and 2 for ZPL
par_zpl_cts_break = 250000
par_check_redpower = 0.4 #voltage of eom-aom

# configure pulses and sequence
par_sp_duration = 10000          
par_sp_power = 15e-9         
par_pre_rabi_syncs =  10
par_rabi_reps = 300          #noof pulses in the sequence
par_post_rabi_syncs =  10       
par_elt_reps = 1              #noof spin pump & sequence reps before CR check


if long_pulse_settings:
    par_eom_pulse_duration = 10
    par_eom_pulse_offset = -18
    
    par_eom_off_amplitude = -.25
    par_eom_pulse_amplitude = 1.2
    par_eom_overshoot_duration1 = 10
    par_eom_overshoot1 = -0.03
    par_eom_overshoot_duration2 = 4
    par_eom_overshoot2 = -0.03

    par_eom_aom_amplitude = 1.0
else:
    par_eom_pulse_duration = 2 #NOTE
    par_eom_pulse_offset = 0
    
    par_eom_off_amplitude = -.25
    par_eom_pulse_amplitude = 1.2
    par_eom_overshoot_duration1 = 10
    par_eom_overshoot1 = -0.03
    par_eom_overshoot_duration2 = 4
    par_eom_overshoot2 = -0.03

    par_eom_aom_amplitude = 1.0
    
par_eom_start = 40
par_eom_off_duration = 70
pulse_start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset

par_aom_start = pulse_start - 35 - 186 #+ 20#subtract aom rise time
par_aom_duration = 2*23+par_eom_pulse_duration-2 #30#2

par_rabi_cycle_duration = 2*par_eom_off_duration

# Configure hydraharp
par_binsize_T3 = 8     # resolution of recorded data in HH 1ps*2**binsize_T3
par_binsize_sync=0     # bintime = 1ps * 2**(binsize_T3 + binsize_sync)
par_range_sync=4*par_eom_off_duration*2    # bins
par_binsize_g2=0       # bintime = 1ps * 2**(binsize_g2 + binsize_T3)
par_range_g2=4*1000    # bins
par_sync_period = par_eom_off_duration*2  # ns
par_max_pulses = par_rabi_reps

# region of interest settings
par_laser_end_ch0 = 171#224#190 #NOTE     # last bin of laser pulse ch0
par_laser_end_ch1 = 166#196#218 #NOTE
par_tail_roi = 200          # how many bins the tail is long
par_debug_laser_roi=8

ins_newfocus_aom_lt1.set_cur_controller('ADWIN')
ins_newfocus_aom_lt2.set_cur_controller('ADWIN')
lt1_a_aom_voltage = qt.instruments['NewfocusAOM_lt1'].power_to_voltage(
        lt1_a_cr_power)
lt2_a_aom_voltage = qt.instruments['NewfocusAOM'].power_to_voltage(
        lt2_a_cr_power)
lt1_ex_aom_voltage = qt.instruments['MatisseAOM_lt1'].power_to_voltage(
        lt1_ex_cr_power)
lt2_ex_aom_voltage = qt.instruments['MatisseAOM'].power_to_voltage(
        lt2_ex_cr_power)

lt1_green_aom_voltage = qt.instruments['GreenAOM_lt1'].power_to_voltage(
        lt1_green_power)
lt2_green_aom_voltage = qt.instruments['GreenAOM'].power_to_voltage(
        lt2_green_power)

#determine spin pumping _v=_v(_valid_elmnts) power for the shared awg channel
ins_newfocus_aom_lt1.set_cur_controller('AWG')
par_sp_voltage = qt.instruments['NewfocusAOM_lt1'].power_to_voltage(
        par_sp_power)
ins_newfocus_aom_lt1.set_cur_controller('ADWIN')
ins_newfocus_aom_lt2.set_cur_controller('ADWIN')


def generate_sequence(do_program=True):
    seq = Sequence('tpqi_remote')
    
    # vars for the channel names
    chan_hhsync = 'HH_sync'         # historically PH_start
    chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
    chan_alasers = 'AOM_Newfocus'   # ok
    chan_eom = 'EOM_Matisse'
    chan_eom_aom = 'EOM_AOM_Matisse'

    awgcfg.configure_sequence(seq, 'hydraharp', 
            LDE = {chan_eom_aom: {'high': par_eom_aom_amplitude}, 
                chan_alasers: {'high': par_sp_voltage}})

    seq.add_element('optical_rabi', goto_target = 'idle', 
            repetitions = par_elt_reps)#'optical_rabi',event_jump_target='idle')

    seq.add_pulse('spinpumping',chan_alasers, 'optical_rabi', 
            start = 0, duration = par_sp_duration)
    
    #Define a start point for the sequence, set amplitude to 0. actual sync pulse comes later  
    if debug_mode:
        seq.add_pulse('hh_debug_sync', chan_hhsync, 'optical_rabi', start = 0,
                start_reference = 'spinpumping', link_start_to = 'start', 
                duration = 50, amplitude = 0.0)
    
    
    seq.add_pulse('start', chan_hhsync, 'optical_rabi', start = 0,
            start_reference='spinpumping', link_start_to='end',
            duration = 50, amplitude = 0.0)

    last_start = 'start'
    seq.add_pulse('start_marker', chan_hh_ma1, 'optical_rabi', 
            start = par_rabi_cycle_duration/2,
            start_reference='start', link_start_to='end',
            duration = 50)

    for i in arange(par_rabi_reps):

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
    seq.add_pulse('empty', chan_alasers, 'idle', start=0, duration = 1000, 
            amplitude = 0)
    
    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()

    return seq


def optimize():
    awg.set_runmode('CONT')

    awg.set_ch4_marker1_low(0)
    adwin_lt1.set_simple_counting()
    adwin_lt2.set_simple_counting()
    print 'Simple counting'

    ins_green_aom_lt1.set_power(0)
    ins_green_aom_lt2.set_power(0)
    ins_newfocus_aom_lt1.set_power(0)
    ins_newfocus_aom_lt2.set_power(0)
    ins_matisse_aom_lt1.set_power(0)
    ins_matisse_aom_lt2.set_power(0)  
        
    ins_green_aom_lt1.set_power(par_opt_lt1_green_power)
    qt.msleep(1)
    if (adwin_lt1.get_countrates()[par_opt_counter_lt1-1] < par_opt_min_cnts_lt1):
        print 'optimizing lt1: zpl countrate', adwin_lt1.get_countrates()[0]
        print 'optimizing lt1: psb countrate', adwin_lt1.get_countrates()[1]
        ins_optimiz0r_lt1.optimize(cnt=par_opt_counter_lt1, cycles = 3, int_time=100)
    ins_green_aom_lt1.set_power(0)

    ins_green_aom_lt2.set_power(par_opt_lt2_green_power)
    qt.msleep(1)
    if (adwin_lt2.get_countrates()[par_opt_counter_lt2-1] < par_opt_min_cnts_lt2):
        print 'optimizing lt2: psb countrate', adwin_lt2.get_countrates()[0]
        print 'optimizing lt2: zpl countrate', adwin_lt2.get_countrates()[1]
        ins_optimiz0r_lt2.optimize(cnt=par_opt_counter_lt2, cycles = 5, int_time=50)
    ins_green_aom_lt2.set_power(0)

    #check for bad suppression
    awg.set_ch4_marker1_low(par_check_redpower)
    counts_with_red = adwin_lt1.get_countrates()[0]+adwin_lt2.get_countrates()[1]
    print 'Countrate in ZPL with red on: ', counts_with_red
    awg.set_ch4_marker1_low(0)
    
    if counts_with_red > par_zpl_cts_break:
        print 'Bad suppression detected, breaking'
        return False
    
    ins_green_aom_lt1.set_power(0)
    ins_green_aom_lt2.set_power(0)
    
    return True

def flip_waveplate_lt1():
    print 'flipping the waveplate in lt1 ZPL'
    adwin_lt1.start_set_dio(dio_no = 3, dio_val = 1)
    qt.msleep(0.5)
    adwin_lt1.start_set_dio(dio_no = 3, dio_val = 0)    
    qt.msleep(0.3)
    adwin_lt1.start_set_dio(dio_no = 3, dio_val = 1)
    qt.msleep(3)



def measurement_cycle(hh_measurement_time, save_raw, adwin_wait_time):
    awg.set_runmode('SEQ')
    awg.start()    
    if not(lt2_only):
        adwin_lt1.start_remote_tpqi_control(load = True, 
                stop_processes = ['counter'],
                set_repump_duration=lt1_rempump_duration,
                set_probe_duration=lt1_probe_duration,
                set_cr_count_threshold_probe=lt1_cnt_threshold_probe,
                set_cr_count_threshold_prepare=lt1_cnt_threshold_prepare,          
                set_counter=lt1_counter,
                set_green_aom_voltage=lt1_green_aom_voltage,
                set_ex_aom_voltage=lt1_ex_aom_voltage,
                set_a_aom_voltage=lt1_a_aom_voltage,
                set_green_aom_dac=adwin_lt1.get_dac_channels()['green_aom'],
                set_ex_aom_dac=adwin_lt1.get_dac_channels()['matisse_aom'],
                set_a_aom_dac=adwin_lt1.get_dac_channels()['newfocus_aom'],
                )
    adwin_lt2.start_remote_tpqi_control(load = True, 
            stop_processes = ['counter'],
            set_repump_duration=lt2_rempump_duration,
            set_probe_duration=lt2_probe_duration,
            set_cr_time_limit=adwin_wait_time,
            set_cr_count_threshold_probe=lt2_cnt_threshold_probe,
            set_cr_count_threshold_prepare=lt2_cnt_threshold_prepare,
            set_counter=lt2_counter,
            set_green_aom_voltage=lt2_green_aom_voltage,
            set_green_aom_voltage_zero=lt2_green_aom_voltage_zero,
            set_ex_aom_voltage=lt2_ex_aom_voltage,
            set_a_aom_voltage=lt2_a_aom_voltage, 
            set_green_aom_dac=adwin_lt2.get_dac_channels()['green_aom'],
            set_ex_aom_dac=adwin_lt2.get_dac_channels()['matisse_aom'],
            set_a_aom_dac=adwin_lt2.get_dac_channels()['newfocus_aom'],
            set_gate_good_phase=lt2_good_phase_gate,
            set_phase_locking_on=lt2_phase_locking_on,
            set_lt2_check_only=lt2_only,
            )

    
    histogram=[]
    hist_ch0=[]
    hist_ch1=[]
    hist_ch1_long=[]
    hist_roi=[]

    if not debug_mode:
        if hh_measurement_time > 0:
            hharp.StartMeas(hh_measurement_time)
        
            [histogram,hist_ch0,hist_ch1,hist_ch1_long,hist_roi] = hharp.get_T3_pulsed_g2_2DHistogram(
                    binsize_sync=par_binsize_sync,
                    range_sync=par_range_sync,
                    binsize_g2=par_binsize_g2,
                    range_g2=par_range_g2,
                    max_pulses = par_max_pulses,
                    sync_period = par_sync_period,
                    laser_end_ch0 = par_laser_end_ch0,
                    laser_end_ch1 = par_laser_end_ch1,
                    tail_roi = par_tail_roi,
                    save_raw=save_raw
                    )
    
    else:
        if not external_hh_debug:
            [hist_ch0,hist_ch1]=get_HH_debug_histogram(hh_measurement_time)
        else:
            for i in range(100):
                print i
                qt.msleep(hh_measurement_time/100./1e3)
                if(msvcrt.kbhit() and msvcrt.getch()=='q'):
                    break

    adwin_lt2.stop_remote_tpqi_control()
    adwin_lt1.stop_remote_tpqi_control()
    
    awg.stop()
    qt.msleep(0.1)
    awg.set_runmode('CONT')

    return histogram, hist_ch0,hist_ch1,hist_ch1_long, hist_roi

def save_and_plot_data(data,histogram,histogram_summed,
        hist_ch0,hist_ch1,hist_ch1_long,hist_roi,hist_roi_summed):
    #Data processing

    adpars_lt1 = adwin_lt1.get_remote_tpqi_control_var('par')
    adpars_lt2 = adwin_lt2.get_remote_tpqi_control_var('par')

    gate_fpars = adwin_lt2.get_gate_modulation_var('fpar')
    gate_pars = adwin_lt2.get_gate_modulation_var('par')
    
    sync = 2**(par_binsize_sync+par_binsize_T3) * arange(par_range_sync) / 1e3 #sync axis in ns
    dt = 2**(par_binsize_g2+par_binsize_T3) * \
            linspace(-par_range_g2/2,par_range_g2/2,par_range_g2)/ 1e3 #dt axis in ns

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
            cr_hist_LT2_total=cr_hist_LT2_total,
            adwin_lt1_pars = adpars_lt1,
            adwin_lt2_pars = adpars_lt2,
            gate_fpars = gate_fpars,
            gate_pars = gate_pars)

    #Plot Data
    do_plot=not(debug_mode)
    if do_plot:
        plt.clear()
        plt.set_xlabel('dt [ns]')
        plt.set_ylabel('number of coincidences in current cycle')
        plt.add(dt,hist_roi)
        plt.save_png(filename+'.png')
       
        plt2.clear()
        plt2.set_xlabel('dt [ns]')
        plt2.set_ylabel('number of coincidences in total')
        plt2.add(dt,hist_roi_summed)
        plt2.save_png(filename+'total.png')

    data.close_file()

def initialize_hh():
    hharp.start_T3_mode()
    hharp.calibrate()
    hharp.set_Binning(par_binsize_T3)

def get_HH_debug_histogram(hh_measurement_time):

    par_debug_hist_length=2
    
    true_length=2**par_debug_hist_length*1024
    do_plot=True

    hharp.start_histogram_mode()
    hharp.calibrate()
    hharp.set_Binning(par_binsize_T3)
    hharp.set_HistoLen(par_debug_hist_length)

    hist_ch0=zeros(true_length)
    hist_ch1=zeros(true_length)
    hist_ch0_sum=zeros(true_length)
    hist_ch1_sum=zeros(true_length)
    roi_ch0=zeros(true_length)
    roi_ch1=zeros(true_length)

    avg_tail_cts=0.0
    avg_laser_cts=0.0
    avg=20.
    
    tpqi_starts_old=adwin_lt2.get_remote_tpqi_control_var('get_noof_tpqi_stops')
    
    dt = 2**(par_binsize_T3) * \
            linspace(0,true_length,true_length)/ 1e3
    hharp.StartMeas(hh_measurement_time)
    i=0
    while hharp.get_MeasRunning():
        i+=1
        hist_ch0_raw=hharp.get_Histogram(0, clear=1)
        hist_ch1_raw=hharp.get_Histogram(1, clear=1)
        hist_ch0+=hist_ch0_raw
        hist_ch1+=hist_ch1_raw
        
        if ch0_only:
            laser_counts=hist_ch0_raw[par_laser_end_ch0-par_debug_laser_roi:par_laser_end_ch0].sum()
            tail_counts=hist_ch0_raw[par_laser_end_ch0:par_laser_end_ch0+par_tail_roi].sum()
        else:
            laser_counts=hist_ch0_raw[par_laser_end_ch0-par_debug_laser_roi:par_laser_end_ch0].sum()+\
                        hist_ch1_raw[par_laser_end_ch1-par_debug_laser_roi:par_laser_end_ch1].sum()
            tail_counts=hist_ch0_raw[par_laser_end_ch0:par_laser_end_ch0+par_tail_roi].sum()+\
                        hist_ch1_raw[par_laser_end_ch1:par_laser_end_ch1+par_tail_roi].sum()
        
        tpqi_starts_new=adwin_lt2.get_remote_tpqi_control_var('get_noof_tpqi_stops')
        tpqi_starts=float(tpqi_starts_new-tpqi_starts_old)
        tpqi_starts_old=tpqi_starts_new
        
        if tpqi_starts>0:
            avg_tail_cts=(1-1/avg)*avg_tail_cts + 1/avg*tail_counts/tpqi_starts
            avg_laser_cts=(1-1/avg)*avg_laser_cts + 1/avg*laser_counts/tpqi_starts
            adwin_lt2.set_remote_tpqi_control_var(set_noof_tailcts=avg_tail_cts,
                    set_noof_lasercts=avg_laser_cts)
        adwin_lt2.set_remote_tpqi_control_var(set_zpl_countrate=hharp.get_CountRate0())

        if mod(i,100) == 0 and do_plot:
            hist_ch0_sum+=hist_ch0
            hist_ch1_sum+=hist_ch1

            plt.clear()
            plt.set_xlabel('dt [ns]')
            plt.set_ylabel('number of coincidences in current cycle')
            plt.add(dt,hist_ch0,'r-')
            plt.add(dt,hist_ch1,'b-')
            
            if ch0_only:
                plt.set_plottitle('Counts in CH0')
            else:
                plt.set_plottitle('Summed counts (CH0 + CH1)')

            roi_ch0[par_laser_end_ch0]=max(hist_ch0)/2
            roi_ch1[par_laser_end_ch1]=max(hist_ch1)/2
            #rois[par_laser_end_ch1]=max(hist_ch1)
            plt.add(dt,roi_ch0,'r-')
            plt.add(dt,roi_ch1,'b-')
            plt.set_ylog(True)
            plt.set_xrange(minval = 0, maxval = 2*par_eom_off_duration)
                        
            hist_ch1=zeros(true_length)
            hist_ch0=zeros(true_length)
            hist_ch1=zeros(true_length)
        if(msvcrt.kbhit() and msvcrt.getch()=='q'):
            hharp.StopMeas()
            plt.clear()
            plt.set_xlabel('dt [ns]')
            plt.set_ylabel('number of coincidences overall')
            plt.add(dt,hist_ch0_sum,'r-')
            plt.add(dt,hist_ch1_sum,'b-')
            plt.set_xrange(minval = 0, maxval = 2*par_eom_off_duration)
            plt.set_ylog(True)

        qt.msleep(.3)


    return hist_ch0_sum, hist_ch1_sum
        


def print_save_cr_check_info(cr_stats,rep_nr,wp_flips):
 
    qt.msleep(1)

    adpars_lt1 = adwin_lt1.get_remote_tpqi_control_var('par')
    adpars_lt2 = adwin_lt2.get_remote_tpqi_control_var('par')

    lt1_cnts_below = adpars_lt1[1][1]
    lt1_cr_checks = adpars_lt1[0][1]
    lt2_cnts_below = adpars_lt2[3][1]
    lt2_cr_checks = adpars_lt2[2][1]
    TPQI_starts = adpars_lt2[15][1]
       
    lt1_repump_cts = adpars_lt1[8][1]
    lt1_triggers_received= adpars_lt1[11][1]
    lt1_oks_sent = adpars_lt1[7][1]
    lt2_repump_cts= adpars_lt2[0][1]
    lt2_triggers_sent= adpars_lt2[10][1]
    lt2_oks_received = adpars_lt2[17][1]
    
    #print 'lt1 : CR below threshold: ', lt1_cnts_below
    #print 'lt1 : CR checks: ', lt1_cr_checks
    #print 'lt2 : CR below threshold: ', lt2_cnts_below
    #print 'lt2 : CR checks: ', lt2_cr_checks
    print rep_nr, ': TPQI starts during the cycle = ', TPQI_starts
    #print ' adwin check-trigger difference:', lt2_triggers_sent - lt1_triggers_received
    #print ' adwin ok-trigger difference: ', lt1_oks_sent - lt2_oks_received
    #print ''
    
    cr_stats.add_data_point(rep_nr,lt1_cnts_below,lt1_cr_checks,
                            lt2_cnts_below,lt2_cr_checks,TPQI_starts,lt1_repump_cts,
                            lt2_repump_cts,lt1_triggers_received,lt2_triggers_sent,
                            lt1_oks_sent,lt2_oks_received,wp_flips)



def end_measuring():
    ins_newfocus_aom_lt1.set_power(0)
    ins_newfocus_aom_lt2.set_power(0)
    ins_matisse_aom_lt1.set_power(0)
    ins_matisse_aom_lt2.set_power(0) 
    counters_lt1.set_is_running(1)
    counters.set_is_running(1)
    adwin_lt1.set_simple_counting()
    adwin_lt2.set_simple_counting()
    GreenAOM.set_power(par_opt_lt2_green_power)
    GreenAOM_lt1.set_power(par_opt_lt1_green_power)


def main():
   
    if not debug_mode:
        initialize_hh()

    seq = generate_sequence()
    #wait at least three idle sequences extra
    adwin_wait_time = int(seq.element_lengths['optical_rabi']*par_elt_reps*1E6 \
            + 3*seq.element_lengths['idle']*1E6)
    
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
    cr_stats.add_value('wp_flips')
    cr_stats.create_file()

    wp_flips=0

    histogram_summed= {}
    hist_roi_summed = {}
    for pol in polarizations:
        histogram_summed[pol] = zeros((par_range_sync,par_range_g2))
        hist_roi_summed[pol] = zeros(par_range_g2)
      
    
    for idx in arange(repetitions):
        skip_opt=False

        for pol in polarizations:
            print '\n##############################################################'
            print '##### Starting measurement cycle_'+pol+'_', idx, 'current time:',\
                    time.strftime('%H:%M',time.localtime())
            print '##############################################################'

            if raw:
                save_raw = os.path.join(qt.config['datadir'], time.strftime('%Y%m%d'), \
                time.strftime('%H%M%S')+'_interference_'+pol+'_rawdata'+ '%.3d' % idx)
                if not os.path.isdir(save_raw):
                    os.makedirs(save_raw)
            else: 
                save_raw = r''


                    
            [histogram,hist_ch0,hist_ch1,hist_ch1_long,hist_roi] = \
                    measurement_cycle(hh_measurement_time, 
                            save_raw, adwin_wait_time)

            print_save_cr_check_info(cr_stats,idx,wp_flips)    

            if not debug_mode:
                histogram_summed[pol] += histogram
                hist_roi_summed[pol] += hist_roi
            print 'Finished measurement cycle_'+pol+'_', idx, 'start saving'
            
            data = qt.Data(name='interference_'+pol+'_'+'%.3d' % idx)
            data.add_coordinate('dt')
            data.add_coordinate('sync')
            data.add_value('counts')
            save_and_plot_data(data,histogram,histogram_summed[pol],\
                    hist_ch0,hist_ch1,hist_ch1_long, hist_roi, hist_roi_summed[pol])
            print 'Data saving cycle_'+pol+'_', idx, 'completed'
            qt.msleep(1)

            if (len(polarizations)>1):
                flip_waveplate_lt1()
                wp_flips+=1
            if msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q" : break
                elif kb_char == "c" : skip_opt=True

            if not(debug_mode) and not(skip_opt):
                if not optimize(): 
                    print 'Break after polarization '+pol
                    print 'CHECK WAVEPLATE STATUS!!!'
                    break
                else:
                    print 'Optimisation step_'+pol+'_', idx, ' completed'
        if msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q" : break
        

    cr_stats.close_file()
    qt.mend()
    end_measuring()

if __name__ == '__main__':

    main()




