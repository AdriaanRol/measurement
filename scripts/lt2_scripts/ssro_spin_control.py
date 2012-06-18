#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
import ctypes
import inspect
import time
import msvcrt
import measurement.measurement as meas
from measurement.AWG_HW_sequencer_v2 import Sequence
import measurement.PQ_measurement_generator_v2 as pqm

from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq

nr_of_datapoints = 40       #max nr_of_datapoints should be < 10000
repetitions_per_datapoint = 2000
min_mwpulse_length = 0    #in ns
max_mwpulse_length = 6000    #in ns
f_drive = 2.8565E9         #in Hz
mwpower_lt1 = -20                #in dBm
mwpower_lt2 = 10                #in dBm
f_mw = f_drive - 5E6


length = np.linspace(min_mwpulse_length,max_mwpulse_length,nr_of_datapoints)
lt1 = False

awg = qt.instruments['AWG']


if lt1:
    ins_green_aom=qt.instruments['GreenAOM_lt1']
    ins_E_aom=qt.instruments['MatisseAOM_lt1']
    ins_A_aom=qt.instruments['NewfocusAOM_lt1']
    adwin=qt.instruments['adwin_lt1']
    counters=qt.instruments['counters_lt1']
    physical_adwin=qt.instruments['physical_adwin_lt1']
    microwaves = qt.instruments['SMB100_lt1']
    ctr_channel=2
    mwpower = mwpower_lt1
else:
    ins_green_aom=qt.instruments['GreenAOM']
    ins_E_aom=qt.instruments['MatisseAOM']
    ins_A_aom=qt.instruments['NewfocusAOM']
    adwin=qt.instruments['adwin']
    counters=qt.instruments['counters']
    physical_adwin=qt.instruments['physical_adwin']
    microwaves = qt.instruments['SMB100']
    ctr_channel=1
    mwpower = mwpower_lt2

microwaves.set_iq('on')
microwaves.set_frequency(f_mw)
microwaves.set_pulm('on')
microwaves.set_power(mwpower)
microwaves.on()

par = {}
par['counter_channel'] =              ctr_channel
par['green_laser_DAC_channel'] =      adwin.get_dac_channels()['green_aom']
par['Ex_laser_DAC_channel'] =         adwin.get_dac_channels()['matisse_aom']
par['A_laser_DAC_channel'] =          adwin.get_dac_channels()['newfocus_aom']
par['AWG_start_DO_channel'] =         1
par['AWG_done_DI_channel'] =          8
par['send_AWG_start'] =               1
par['wait_for_AWG_done'] =            0
par['green_repump_duration'] =        6
par['CR_duration'] =                  60
par['SP_duration'] =                  25
par['SP_filter_duration'] =           0
par['sequence_wait_time'] =           ceil(max_mwpulse_length/1E3)+1
par['wait_after_pulse_duration'] =    1
par['CR_preselect'] =                 100
par['RO_repetitions'] =               nr_of_datapoints*repetitions_per_datapoint
par['RO_duration'] =                  20
par['sweep_length'] =                 nr_of_datapoints
par['cycle_duration'] =               300
par['CR_probe'] =                     100

par['green_repump_amplitude'] =       200e-6
par['green_off_amplitude'] =          0e-6
par['Ex_CR_amplitude'] =              7e-9 #OK
par['A_CR_amplitude'] =               7e-9 #OK
par['Ex_SP_amplitude'] =              0e-9
par['A_SP_amplitude'] =               7e-9 #OK: PREPARE IN MS = 0
par['Ex_RO_amplitude'] =              7e-9 #OK: READOUT MS = 0
par['A_RO_amplitude'] =               0e-9


ins_green_aom.set_power(0.)
ins_E_aom.set_power(0.)
ins_A_aom.set_power(0.)
ins_green_aom.set_cur_controller('ADWIN')
ins_E_aom.set_cur_controller('ADWIN')
ins_A_aom.set_cur_controller('ADWIN')
ins_green_aom.set_power(0.)
ins_E_aom.set_power(0.)
ins_A_aom.set_power(0.)

par['green_repump_voltage'] = ins_green_aom.power_to_voltage(par['green_repump_amplitude'])
par['green_off_voltage'] = ins_green_aom.power_to_voltage(par['green_off_amplitude'])
par['Ex_CR_voltage'] = ins_E_aom.power_to_voltage(par['Ex_CR_amplitude'])
par['A_CR_voltage'] = ins_A_aom.power_to_voltage(par['A_CR_amplitude'])
par['Ex_SP_voltage'] = ins_E_aom.power_to_voltage(par['Ex_SP_amplitude'])
par['A_SP_voltage'] = ins_A_aom.power_to_voltage(par['A_SP_amplitude'])
par['Ex_RO_voltage'] = ins_E_aom.power_to_voltage(par['Ex_RO_amplitude'])
par['A_RO_voltage'] = ins_A_aom.power_to_voltage(par['A_RO_amplitude'])

###########################################################
##
##  hardcoded in ADwin program (adjust there if necessary!)
##

max_SP_bins = 500
max_RO_dim = 1000000

##
###########################################################

def generate_sequence(do_program=True):
    seq = Sequence('spin_control')
    # vars for the channel names
    chan_mw_pm = 'MW_pulsemod'
    chan_mwI = 'MW_Imod'
    chan_mwQ = 'MW_Qmod'
    
    amplitude_ssbmod = 0.8 #do not exceed 0.8, weird stuff happens: ask Wolfgang 
    MW_pulse_mod_risetime = 20

    awgcfg.configure_sequence(seq,'mw')

    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        seq.add_IQmod_pulse(name = 'mwburst', channel = (chan_mwI,chan_mwQ), 
            element = 'spin_control_'+str(i+1), start = 0, duration = length[i],  
            frequency = f_drive-f_mw, 
            amplitude = amplitude_ssbmod)

        seq.clone_channel(chan_mw_pm, chan_mwI, 'spin_control_'+str(i+1),
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            link_start_to = 'start', link_duration_to = 'duration', 
            amplitude = 2.0)


    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()


def spin_control(name, data, par):
    par['green_repump_voltage'] = ins_green_aom.power_to_voltage(par['green_repump_amplitude'])
    par['green_off_voltage'] = ins_green_aom.power_to_voltage(par['green_off_amplitude'])
    par['Ex_CR_voltage'] = ins_E_aom.power_to_voltage(par['Ex_CR_amplitude'])
    par['A_CR_voltage'] = ins_A_aom.power_to_voltage(par['A_CR_amplitude'])
    par['Ex_SP_voltage'] = ins_E_aom.power_to_voltage(par['Ex_SP_amplitude'])
    par['A_SP_voltage'] = ins_A_aom.power_to_voltage(par['A_SP_amplitude'])
    par['Ex_RO_voltage'] = ins_E_aom.power_to_voltage(par['Ex_RO_amplitude'])
    par['A_RO_voltage'] = ins_A_aom.power_to_voltage(par['A_RO_amplitude'])

    if  (par['SP_duration'] > max_SP_bins) or \
        (par['RO_repetitions'] > max_RO_dim):
            print ('Error: maximum dimensions exceeded')
            return(-1)

    print 'SP E amplitude: %s'%par['Ex_SP_voltage']
    print 'SP A amplitude: %s'%par['A_SP_voltage']

    adwin.start_adwin_spincontrol(
        counter_channel = par['counter_channel'],
        green_laser_DAC_channel = par['green_laser_DAC_channel'],
        Ex_laser_DAC_channel = par['Ex_laser_DAC_channel'],
        A_laser_DAC_channel = par['A_laser_DAC_channel'],
        AWG_start_DO_channel = par['AWG_start_DO_channel'],
        AWG_done_DI_channel = par['AWG_done_DI_channel'],
        send_AWG_start = par['send_AWG_start'],
        wait_for_AWG_done = par['wait_for_AWG_done'],
        green_repump_duration = par['green_repump_duration'],
        CR_duration = par['CR_duration'],
        SP_duration = par['SP_duration'],
        SP_filter_duration = par['SP_filter_duration'],
        sequence_wait_time = par['sequence_wait_time'],
        wait_after_pulse_duration = par['wait_after_pulse_duration'],
        CR_preselect = par['CR_preselect'],
        RO_repetitions = par['RO_repetitions'],
        RO_duration = par['RO_duration'],
        sweep_length = par['sweep_length'],
        cycle_duration = par['cycle_duration'],
        green_repump_voltage = par['green_repump_voltage'],
        green_off_voltage = par['green_off_voltage'],
        Ex_CR_voltage = par['Ex_CR_voltage'],
        A_CR_voltage = par['A_CR_voltage'],
        Ex_SP_voltage = par['Ex_SP_voltage'],
        A_SP_voltage = par['A_SP_voltage'],
        Ex_RO_voltage = par['Ex_RO_voltage'],
        A_RO_voltage = par['A_RO_voltage'])

    CR_counts = 0
    while (physical_adwin.Process_Status(9) == 1):
        reps_completed = physical_adwin.Get_Par(73)
        CR_counts = physical_adwin.Get_Par(70) - CR_counts
        cts = physical_adwin.Get_Par(26)
        trh = physical_adwin.Get_Par(25)
        print('completed %s / %s readout repetitions, %s CR counts/s'%(reps_completed,par['RO_repetitions'], CR_counts))
        print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        qt.msleep(1)
    physical_adwin.Stop_Process(9)
    
    reps_completed      = physical_adwin.Get_Par(73)
    print('completed %s / %s readout repetitions'%(reps_completed,par['RO_repetitions']))

    sweep_length = par['sweep_length']
    par_long   = physical_adwin.Get_Data_Long(20,1,25)
    par_float  = physical_adwin.Get_Data_Float(20,1,10)
    CR_before = physical_adwin.Get_Data_Long(22,1,1)
    CR_after  = physical_adwin.Get_Data_Long(23,1,1)
    SP_hist   = physical_adwin.Get_Data_Long(24,1,par['SP_duration'])
    RO_data   = physical_adwin.Get_Data_Long(25,1,
                    sweep_length * par['RO_duration'])
    RO_data = reshape(RO_data,(sweep_length,par['RO_duration']))
    statistics = physical_adwin.Get_Data_Long(26,1,10)

    sweep_index = arange(sweep_length)
    sp_time = arange(par['SP_duration'])*par['cycle_duration']*3.333
    ro_time = arange(par['RO_duration'])*par['cycle_duration']*3.333

    #stat_str = ''
    #stat_str += '# successful repetitions: %s\n'%(reps_completed/sweep_length)
    #stat_str += '# total repumps: %s\n'%(statistics[0])
    #stat_str += '# total repump counts: %s\n'%(statistics[1])
    #stat_str += '# failed CR: %s\n'%(statistics[2])
    #stat_str += '# MW center frequency: %s\n'%(f_mw)
    #stat_str += '# MW drive frequency: %s\n'%(f_drive)
    #stat_str += '# MW power: %s dBm\n'%(mwpower)
    #stat_str += '# min MW length: %s ns\n'%(min_mwpulse_length )
    #stat_str += '# max MW length: %s ns\n'%(max_mwpulse_length )
    #stat_str += '# nr of datapoints: %s \n'%(nr_of_datapoints)

    data.save()
    #savdat={}
    #savdat['counts']=CR_before
    #data.save_dataset(name='ChargeRO_before', do_plot=False, 
    #    txt = {'statistics': stat_str}, data = savdat, idx_increment = False)
    savdat={}
    savdat['counts']=CR_after
    data.save_dataset(name='ChargeRO_after', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=sp_time
    savdat['counts']=SP_hist
    data.save_dataset(name='SP_histogram', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=ro_time
    savdat['sweep_axis']=sweep_index
    savdat['counts']=RO_data
    data.save_dataset(name='Spin_RO', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['par_long']=par_long
    savdat['par_float']=par_float
    data.save_dataset(name='parameters', do_plot=False, 
        data = savdat, idx_increment = False)
    
    ######################
    ###statistics file####
    ######################
    savdat={}
    savdat['completed_repetitions']=(reps_completed/sweep_length)
    savdat['total_repumps']=statistics[0]
    savdat['total_repump_counts']=statistics[1]
    savdat['noof_failed_CR_checks']=statistics[2]
    savdat['mw_center_freq']=f_mw
    savdat['mw_drive_freq']=f_drive
    savdat['mw_power']=mwpower
    savdat['min_mw_length']=min_mwpulse_length
    savdat['max_mw_length']=max_mwpulse_length
    savdat['noof_datapoints']=nr_of_datapoints
    
    data.save_dataset(name='statics_and_parameters', do_plot=False, 
        data = savdat, idx_increment = True)
   
    return 

def end_measurement():
    awg.stop()
    awg.set_runmode('CONT')
    adwin.set_simple_counting()
    counters.set_is_running(1)
    ins_green_aom.set_power(200e-6)   
    microwaves.off()
    microwaves.set_iq('off')
    microwaves.set_pulm('off')

def ssro_init(name, data, par, do_ms0 = True, do_ms1 = True, 
        A_SP_init_amplitude     = 5e-9,
        Ex_SP_init_amplitude    = 5e-9):

    if do_ms0:
        par['A_SP_amplitude']  = A_SP_init_amplitude
        par['Ex_SP_amplitude'] = 0.
        ssro(name,data,par)

    if do_ms1:
        par['A_SP_amplitude']  = 0.
        par['Ex_SP_amplitude'] = Ex_SP_init_amplitude
        ssro(name,data,par)

def main():
    generate_sequence()
    awg.set_runmode('SEQ')
    awg.start()  
    while awg.get_state() != 'Waiting for trigger':
        qt.msleep(1)

    name = 'SIL9'
    data = meas.Measurement(name,'spin_control')
    spin_control(name,data,par)
    end_measurement()




if __name__ == '__main__':
    main()


