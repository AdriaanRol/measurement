import qt
import data
import numpy as np
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq
import measurement.PQ_measurement_generator_v2 as pqm

adwin_lt2 = qt.instruments['adwin']
adwin_lt1 = qt.instruments['adwin_lt1']
awg = qt.instruments['AWG']
hharp = qt.instruments['HH_400']



# configure conditional repumping
time_limit = 30 #in Adwin_proII processor cycles # in units of 1us

lt1_rempump_duration = 10 # in units of 1us
lt1_probe_duration = 100 # in units of 1us
lt1_cnt_threshold = 8
lt1_counter = 2
lt1_green_power = 200e-6
lt1_ex_power = 7e-9
lt1_a_power = 5e-9

lt2_rempump_duration = 10 # in units of 1us
lt2_probe_duration = 100 # in units of 1us
lt2_cnt_threshold = 3
lt2_counter = 1
lt2_green_power = 700e-6
lt2_ex_power = 12e-9
lt2_a_power = 5e-9

# configure pulses and sequence
par_sp_duration = 5000
par_sp_voltage_lt1 = .1
par_sp_voltage_lt2 = .12
par_rabi_reps = 100
par_eom_start = 20
par_eom_off_duration = 100
par_eom_pulse_duration = 10
par_eom_pulse_offset = -15
pulse_start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset

par_aom_start = pulse_start - 35 -45 #subtract aom rise time
par_aom_duration = 2*35+par_eom_pulse_duration

par_eom_off_amplitude = -.27
par_eom_pulse_amplitude = 1.2
par_eom_overshoot_duration1 = 10
par_eom_overshoot1 = -0.07
par_eom_overshoot_duration2 = 10
par_eom_overshoot2 = 0.05

par_eom_aom_amplitude = 1

par_rabi_cycle_duration = 2*par_eom_off_duration

# Configure hydraharp
par_binsize_sync=8     # bintime = 1ps * 2**binsize
par_range_sync=4*50    # bins
par_binsize_g2=8       # bintime = 1ps * 2**binsize
par_range_g2=4*500     # bins
par_sync_period = 100  # ns
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
print lt2_green_aom_voltage 



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
    return

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
            a_aom_voltage=lt1_a_aom_voltage, )
    
    adwin_lt2.start_remote_tpqi_control(
            repump_duration=lt2_rempump_duration,
            probe_duration=lt2_probe_duration,
            cr_time_limit=time_limit,
            cr_count_threshold=lt2_cnt_threshold,
            counter=lt2_counter,
            green_aom_voltage=lt2_green_aom_voltage,
            ex_aom_voltage=lt2_ex_aom_voltage,
            a_aom_voltage=lt2_a_aom_voltage, )
    
    histogram=[]
    if hh_measurement_time > 0:

        hharp.StartMeas(hh_measurement_time)
        histogram = hharp.get_T3_pulsed_g2_2DHistogram(
                binsize_sync=par_binsize_sync,
                range_sync=par_range_sync,
                binsize_g2=par_binsize_g2,
                range_g2=par_range_g2,
                sync_period = par_sync_period,
                )

    print_double_cr_check_info(300)#hh_measurement_time*1e-3)
    
    adwin_lt2.stop_remote_tpqi_control()
    adwin_lt1.stop_remote_tpqi_control()
    
    awg.stop()
    awg.set_runmode('CONT')

    return histogram

def save_and_plot_data(data,histogram):
    #Data processing
    
    sync = 2**par_binsize_sync * arange(par_range_sync) * 1e3    #sync axis in ns
    dt = 2**par_binsize_g2 * linspace(-par_range_g2/2,par_range_g2/2,par_range_g2)*1e3 #dt axis in ns
    X,Y = meshgrid(dt, sync)
    data.create_file()
    
    #plt = qt.Plot3D(data, name='Interference',clear = True, coorddims=(0,1), valdim=1, style='image')
    
    data.add_data_point(ravel(X),ravel(Y),ravel(histogram))
    filename=data.get_filepath()[:-4]
    pqm.savez(filename,dt=dt,sync=sync, counts=histogram)

    #Plot Data
    plt = plot3(ravel(X),ravel(Y),ravel(histogram),
           style='image',palette='hot',
           title='interference')
    
    #data.new_block()
    plt.set_xlabel('dt [ns]')
    plt.set_ylabel('delay wrt sync pulse [ns]')
    plt.save_png(filename)

    
    data.close_file()
    

    print 'interference'
    print '(entanglement expected in 3 weeks)'
    


def initialize_hh():
    hharp.start_T3_mode()
    hharp.calibrate()
    hharp.set_Binning(0)
    
def print_double_cr_check_info(time=10):
    
    for t in linspace(0,time,time+1):
        qt.msleep(1)
        print 't=%d :' % (t+1)
        print 'lt1 :  noof triggers:', adwin_lt1.remote_tpqi_control_get_noof_trigger() 
        print 'lt1 : CR counts: ', adwin_lt1.remote_tpqi_control_get_cr_check_counts()
        print 'lt1 : below th.: ' , adwin_lt1.remote_tpqi_control_get_cr_below_threshold_events()
        print 'lt1 : CR checks: ', adwin_lt1.remote_tpqi_control_get_noof_cr_checks()
        print 'lt1 : repump cts.: ', adwin_lt1.remote_tpqi_control_get_repump_counts()
        print 'lt2 : CR counts: ', adwin_lt2.remote_tpqi_control_get_cr_check_counts()
        print 'lt2 : below th.: ', adwin_lt2.remote_tpqi_control_get_cr_below_threshold_events()
        print 'lt2 : CR checks: ', adwin_lt2.remote_tpqi_control_get_noof_cr_checks()
        print 'tpqi starts: ', adwin_lt2.remote_tpqi_control_get_noof_tpqi_starts()
        print 'tpqi stops: ', adwin_lt2.remote_tpqi_control_get_noof_tpqi_stops()
        print 'lt2 : repump cts.: ', adwin_lt2.remote_tpqi_control_get_repump_counts()
        print 'lt1 : OKs: ', adwin_lt2.remote_tpqi_control_get_noof_lt1_oks()
        print ''

def main():

    #initialize_hh()
    generate_sequence()

    # configure measurement
    repetitions = 1 
    hh_measurement_time =0# int(1e3 * 10)

    qt.mstart()

    for idx in arange(repetitions):

        histogram = measurement_cycle(hh_measurement_time)
       # data = qt.Data(name='interference'+str(idx))
       # data.add_coordinate('dt')
       # data.add_coordinate('sync')
       # data.add_value('counts')
       # save_and_plot_data(data,histogram)
        qt.msleep(1)
    
    qt.mend()


if __name__ == '__main__':
    main()


# 



# adwin_lt2.stop_remote_tpqi_control()
# adwin_lt1.stop_remote_tpqi_control()

