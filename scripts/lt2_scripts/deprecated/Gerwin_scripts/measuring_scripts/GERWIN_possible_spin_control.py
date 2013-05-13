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

nr_of_datapoints = 50 #max nr_of_datapoints should be < 10000
repetitions_per_datapoint = 1000
min_mwpulse_length = 100
max_mwpulse_length = 1000

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
    ctr_channel=3
else:
    ins_green_aom=qt.instruments['GreenAOM']
    ins_E_aom=qt.instruments['MatisseAOM']
    ins_A_aom=qt.instruments['NewfocusAOM']
    adwin=qt.instruments['adwin']
    counters=qt.instruments['counters']
    physical_adwin=qt.instruments['physical_adwin']
    ctr_channel=4

par = {}
par['counter_channel'] =              ctr_channel
par['green_laser_DAC_channel'] =      adwin.get_dac_channels()['green_aom']
par['Ex_laser_DAC_channel'] =         adwin.get_dac_channels()['matisse_aom']
par['A_laser_DAC_channel'] =          adwin.get_dac_channels()['newfocus_aom']
par['AWG_start_DO_channel'] =         1
par['AWG_done_DI_channel'] =          8
par['send_AWG_start'] =               1
par['wait_for_AWG_done'] =            0
par['green_repump_duration'] =        20
par['CR_duration'] =                  100
par['SP_duration'] =                  250
par['SP_filter_duration'] =           0
par['sequence_wait_time'] =           10
par['wait_after_pulse_duration'] =    0
par['CR_preselect'] =                 20
par['SSRO_repetitions'] =             nr_of_datapoints*repetitions_per_datapoint
par['SSRO_duration'] =                50
par['SSRO_stop_after_first_photon'] = 0
par['cycle_duration'] =               300
par['CR_probe'] =                     10
par['green_readout_duration'] =       1
par['datapoints'] =                   nr_of_datapoints

par['green_repump_amplitude'] =       200e-6
par['green_off_amplitude'] =          0e-6
par['Ex_CR_amplitude'] =              5e-9
par['A_CR_amplitude'] =               5e-9
par['Ex_SP_amplitude'] =              0e-9
par['A_SP_amplitude'] =               5e-9
par['Ex_RO_amplitude'] =              5e-9
par['A_RO_amplitude'] =               0e-9
par['green_readout_amplitude'] =      50e-6

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
par['green_readout_voltage'] = ins_green_aom.power_to_voltage(par['green_readout_amplitude'])

def generate_sequence(do_program=True):
    seq = Sequence('spin_control')
    chan_mw_pm = 'MW_pulsemod'
    awgcfg.configure_sequence(seq, mw = {chan_mw_pm: {'AWG_channel': 'ch1m1'}})

    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        seq.add_pulse('wait_'+str(i+1), chan_mw_pm, 'spin_control_'+str(i+1), 
                start = 0, duration = 1500, amplitude = 0)
        seq.add_pulse('microwave_'+str(length[i]), chan_mw_pm, 
                'spin_control_'+str(i+1), start = 0, duration = length[i], 
                start_reference='wait_'+str(i+1),
                link_start_to = 'end')
    

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()

def start_measurement():
    generate_sequence()
    awg.set_runmode('SEQ')
    awg.start()  
    while awg.get_state() != 'Waiting for trigger':
        qt.msleep(1)

    adwin.start_adwin_spin_manipulation(
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
        SSRO_repetitions = par['SSRO_repetitions'],
        SSRO_duration = par['SSRO_duration'],
        SSRO_stop_after_first_photon = par['SSRO_stop_after_first_photon'],
        cycle_duration = par['cycle_duration'],
        CR_probe = par['CR_probe'],
        green_readout_duration = par['green_readout_duration'],
        datapoints = par['datapoints'],
        green_repump_voltage = par['green_repump_voltage'],
        green_off_voltage = par['green_off_voltage'],
        Ex_CR_voltage = par['Ex_CR_voltage'],
        A_CR_voltage = par['A_CR_voltage'],
        Ex_SP_voltage = par['Ex_SP_voltage'],
        A_SP_voltage = par['A_SP_voltage'],
        Ex_RO_voltage = par['Ex_RO_voltage'],
        A_RO_voltage = par['A_RO_voltage'],
        green_readout_voltage = par['green_readout_voltage']
        )

    while (physical_adwin.Process_Status(9) == 1):
        reps_completed = physical_adwin.Get_Par(73)
        print('%s percent completed'%(100*reps_completed/par['SSRO_repetitions']))
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        qt.msleep(0.5)    


def save_data():
    mw_pulse_length = length
    counts_during_repump   = physical_adwin.Get_Data_Long(27,0, nr_of_datapoints+1)
    
    data.create_file()
    filename=data.get_filepath()[:-4]
    pqm.savez(filename, repetitions_per_datapoint = repetitions_per_datapoint,
            mw_pulse_length = length, 
            counts_during_repump = counts_during_repump,)
    data.close_file()

    print 'Data saved'


    

start_measurement()
save_data()
