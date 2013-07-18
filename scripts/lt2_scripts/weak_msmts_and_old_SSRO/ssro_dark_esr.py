import qt
import numpy as np
import ctypes
import inspect
import time
import msvcrt
from measurement.lib import measurement as meas

from measurement.lib.AWG_HW_sequencer_v2 import Sequence
import measurement.lib.PQ_measurement_generator_v2 as pqm

from measurement.lib.config import awgchannels_lt2 as awgcfg
from measurement.lib.sequence import common as commonseq
from measurement.lib.config import experiment_lt2 as exp

f_mw    = exp.sil9['MW_source_freq']
f_start = 2.8245E9           #start frequency in Hz
f_stop = 2.8335E9            #stop frequency in Hz
pi_pulse_length = exp.MBIprotocol['MBI_pulse_len']      #length of MW pi pulse
#pi_pulse_length = 2200
mwpower_lt1 = -10        #in dBm
mwpower_lt2 = 20            #in dBm
nr_of_datapoints = 101       #max nr_of_datapoints*repetitions_per_datapoint should be < 20000
repetitions_per_datapoint = 500 
amplitude_ssbmod = exp.MBIprotocol['MBI_pulse_amp']
#amplitude_ssbmod = 0.015
mwfreq = np.linspace(f_start,f_stop,nr_of_datapoints)
lt1 = False

awg = qt.instruments['AWG']

if lt1:
    ins_green_aom=qt.instruments['GreenAOM_lt1']
    ins_E_aom=qt.instruments['MatisseAOM_lt1']
    ins_A_aom=qt.instruments['NewfocusAOM_lt1']
    adwin=qt.instruments['adwin_lt1']
    counterz=qt.instruments['counters_lt1']
    physical_adwin=qt.instruments['physical_adwin_lt1']
    microwaves = qt.instruments['SMB100_lt1']
    ctr_channel=2
    mwpower = mwpower_lt1
else:
    ins_green_aom=qt.instruments['GreenAOM']
    ins_E_aom=qt.instruments['MatisseAOM']
    ins_A_aom=qt.instruments['NewfocusAOM']
    adwin=qt.instruments['adwin']
    counterz=qt.instruments['counters']
    physical_adwin=qt.instruments['physical_adwin']
    microwaves = qt.instruments['SMB100']
    ctr_channel=1
    mwpower = mwpower_lt2

microwaves.set_iq('on')
microwaves.set_frequency(f_mw)
microwaves.set_pulm('on')
microwaves.set_power(mwpower)
##############Gate Stuff########
set_phase_locking_on=0
set_gate_good_phase=-1


ssrodic=exp.ssroprotocol

par = {}
par['counter_channel'] =              ctr_channel
par['green_laser_DAC_channel'] =      adwin.get_dac_channels()['green_aom']
par['Ex_laser_DAC_channel'] =         adwin.get_dac_channels()['matisse_aom']
par['A_laser_DAC_channel'] =          adwin.get_dac_channels()['newfocus_aom']
par['AWG_start_DO_channel'] =         1
par['AWG_done_DI_channel'] =          8
par['send_AWG_start'] =               1
par['wait_for_AWG_done'] =            0
par['green_repump_duration'] =        ssrodic['green_repump_duration']
par['CR_duration'] =                  ssrodic['CR_duration'] #NOTE 60 for readout A1
par['SP_duration'] =                  ssrodic['SP_A_duration']
par['SP_filter_duration'] =           0
par['sequence_wait_time'] =           int(ceil(pi_pulse_length/1e3)+1)
par['wait_after_pulse_duration'] =    1
par['CR_preselect'] =                 1000
par['RO_repetitions'] =               int(nr_of_datapoints*repetitions_per_datapoint)
par['RO_duration'] =                  ssrodic['RO_duration']
par['sweep_length'] =                 int(nr_of_datapoints)
par['cycle_duration'] =               300
par['CR_probe'] =                     100

par['green_repump_amplitude'] =       160e-6
par['green_off_amplitude'] =          0e-6
par['Ex_CR_amplitude'] =              ssrodic['Ex_CR_amplitude'] #OK
par['A_CR_amplitude'] =               ssrodic['A_CR_amplitude'] #NOTE 15 for readout A1
par['Ex_SP_amplitude'] =              0
par['A_SP_amplitude'] =               ssrodic['A_SP_amplitude'] #OK: PREPARE IN MS = 0
par['Ex_RO_amplitude'] =              ssrodic['Ex_RO_amplitude'] #OK: READOUT MS = 0
par['A_RO_amplitude'] =               0



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

max_SP_bins =    500
max_RO_dim = 1000000

##
###########################################################

def generate_sequence(fstart = f_start-f_mw, fstop = f_stop-f_mw, steps = nr_of_datapoints, do_program = True):
    seq = Sequence('dark_esr')

    print 'start frequency = ',(fstart+f_mw)/1E9
    print 'stop frequency = ',(fstop+f_mw)/1E9

    awgcfg.configure_sequence(seq,'mw')
    
    # vars for the channel names
    

    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
        chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1

    # in this version we keep the center frequency and sweep the
    # modulation frequency

    # f_central = (fstart+fstop)/2.0
    
    pipulse = pi_pulse_length

    mode = 'SSB'
    amplitude_i = 0.
    amplitude_q = 0. 

    

    if lt1:
        MW_pulse_mod_risetime = 2
    else:
        MW_pulse_mod_risetime = 6

    # sweep the modulation freq
    for i, f_mod in enumerate(linspace(fstart, fstop, steps)):
    
        ###################################################################
        # the actual rabi sequence and readout
        
        ename = 'desrseq%d' % i
        kw = {} if i < steps-1 else {'goto_target': 'desrseq0'}
        seq.add_element(ename, trigger_wait = True, **kw)

        seq.add_pulse('wait', channel = chan_mw_pm, element = ename,
                start = 0, duration = 100, amplitude = 0)
        
        seq.add_pulse(name = 'mwburst', channel = chan_mwI, 
            element = ename, start = 0, duration = pipulse,
            frequency = f_mod, shape = 'cosine', 
            amplitude = amplitude_ssbmod, link_start_to = 'end',
            start_reference = 'wait')
        seq.add_pulse(name = 'mwburstQ', channel = chan_mwQ, 
            element = ename, start = 0, duration = pipulse,
            frequency = f_mod, shape = 'sine', 
            amplitude = amplitude_ssbmod, link_start_to = 'end',
            start_reference = 'wait')
                             
        seq.add_pulse('pulse_mod', channel = chan_mw_pm, element = ename,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'mwburst', link_start_to = 'start', 
            duration_reference = 'mwburst', link_duration_to = 'duration', 
            amplitude = 2.0)

        ###################################################################

    

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()


def dark_esr(name, data, par):
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

    #print 'SP E amplitude: %s'%par['Ex_SP_voltage']
    #print 'SP A amplitude: %s'%par['A_SP_voltage']

    if not(lt1):
        adwin.set_spincontrol_var(set_phase_locking_on = set_phase_locking_on)
        adwin.set_spincontrol_var(set_gate_good_phase =  set_gate_good_phase)
    print 'start adwin'

    adwin.start_spincontrol(load = True, stop_processes=['counter'],
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
    print 'adwin started'
    if lt1:
        adwin_lt2.start_check_trigger_from_lt1()

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
    
    if lt1:
        adwin_lt2.stop_check_trigger_from_lt1()

    reps_completed      = physical_adwin.Get_Par(73)
    print('completed %s / %s readout repetitions'%(reps_completed,par['RO_repetitions']))

    sweep_length = par['sweep_length']
    
    par_long   = physical_adwin.Get_Data_Long(20,1,25)
    par_float  = physical_adwin.Get_Data_Float(21,1,10)
    CR_before = physical_adwin.Get_Data_Long(22,1,1)
    CR_after  = physical_adwin.Get_Data_Long(23,1,1)
    SP_hist   = physical_adwin.Get_Data_Long(24,1,par['SP_duration'])
    #RO_data   = physical_adwin.Get_Data_Long(25,1,
    #                sweep_length * par['RO_duration'])
    #RO_data = reshape(RO_data,(sweep_length,par['RO_duration']))
    # SSRO_data contains adwin decisions for the spin
    SSRO_data   = physical_adwin.Get_Data_Long(27,1,
                    sweep_length * par['RO_duration'])
    RO_data=SSRO_data
    SSRO_data = reshape(SSRO_data,(sweep_length,par['RO_duration']))
    statistics = physical_adwin.Get_Data_Long(26,1,10)

    sweep_index = arange(sweep_length)
    sp_time = arange(par['SP_duration'])*par['cycle_duration']*3.333
    ro_time = arange(par['RO_duration'])*par['cycle_duration']*3.333


    data.save()
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
    savdat['SSRO_counts']=SSRO_data
    data.save_dataset(name='Spin_RO', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['par_long']=par_long
    savdat['par_float']=par_float
    data.save_dataset(name='parameters', do_plot=False, 
        data = savdat, idx_increment = True)
   
    ######################
    ###statistics file####
    ######################
    savdat={}
    savdat['completed_repetitions']=(reps_completed/sweep_length)
    savdat['total_repumps']=statistics[0]
    savdat['total_repump_counts']=statistics[1]
    savdat['noof_failed_CR_checks']=statistics[2]
    savdat['mw_center_freq']=f_mw
    savdat['mw_power']=mwpower
    savdat['min_mw_freq']=f_start
    savdat['max_mw_freq']=f_stop
    savdat['noof_datapoints']=nr_of_datapoints
    
    data.save_dataset(name='statics_and_parameters', do_plot=False, 
        data = savdat, idx_increment = True)


    return 

def end_measurement():
    awg.stop()
    awg.set_runmode('CONT')
    adwin.set_simple_counting()
    counterz.set_is_running(1)
    ins_green_aom.set_power(150e-6)   
    microwaves.set_status('off')
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
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            end_measurement()
            break

    name = 'SIL9_lt2'
    data = meas.Measurement(name,'dark_esr')
    microwaves.set_status('on')
    dark_esr(name,data,par)
    end_measurement()




if __name__ == '__main__':
    main()


