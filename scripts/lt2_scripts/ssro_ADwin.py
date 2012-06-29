import qt
import numpy as np
import ctypes
import inspect
import time
import msvcrt
import measurement.measurement as meas
import shutil


lt1=False
if lt1:
    ins_green_aom=qt.instruments['GreenAOM_lt1']
    ins_E_aom=qt.instruments['MatisseAOM_lt1']
    ins_A_aom=qt.instruments['NewfocusAOM_lt1']
    adwin=qt.instruments['adwin_lt1']
    counters=qt.instruments['counters_lt1']
    physical_adwin=qt.instruments['physical_adwin_lt1']
    ctr_channel=2
else:
    ins_green_aom=qt.instruments['GreenAOM']
    ins_E_aom=qt.instruments['MatisseAOM']
    ins_A_aom=qt.instruments['NewfocusAOM']
    adwin=qt.instruments['adwin']
    counters=qt.instruments['counters']
    physical_adwin=qt.instruments['physical_adwin']
    ctr_channel=1

par = {}
par['counter_channel'] =              ctr_channel
par['green_laser_DAC_channel'] =      adwin.get_dac_channels()['green_aom']
par['Ex_laser_DAC_channel'] =         adwin.get_dac_channels()['matisse_aom']
par['A_laser_DAC_channel'] =          adwin.get_dac_channels()['newfocus_aom']
par['AWG_start_DO_channel'] =         1
par['AWG_done_DI_channel'] =          8
par['send_AWG_start'] =               0
par['wait_for_AWG_done'] =            0
par['green_repump_duration'] =        10
par['CR_duration'] =                  45
par['SP_duration'] =                  250
par['SP_filter_duration'] =           0
par['sequence_wait_time'] =           10
par['wait_after_pulse_duration'] =    1
par['CR_preselect'] =                 1000
par['SSRO_repetitions'] =             5000
par['SSRO_duration'] =                100 #NOTE CHANGED THIS FOR MORE CR CHECKS
par['SSRO_stop_after_first_photon'] = 0
par['cycle_duration'] =               300

par['green_repump_amplitude'] =       200e-6
par['green_off_amplitude'] =          0e-6
par['Ex_CR_amplitude'] =              5e-9
par['A_CR_amplitude'] =               10e-9
par['Ex_SP_amplitude'] =              0e-9
par['A_SP_amplitude'] =               5e-9
par['Ex_RO_amplitude'] =              5e-9 #
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

max_repetitions = 10000
max_SP_bins = 500
max_SSRO_dim = 500000

##
###########################################################


def ssro(name, data, par):
    par['green_repump_voltage'] = ins_green_aom.power_to_voltage(par['green_repump_amplitude'])
    par['green_off_voltage'] = ins_green_aom.power_to_voltage(par['green_off_amplitude'])
    par['Ex_CR_voltage'] = ins_E_aom.power_to_voltage(par['Ex_CR_amplitude'])
    par['A_CR_voltage'] = ins_A_aom.power_to_voltage(par['A_CR_amplitude'])
    par['Ex_SP_voltage'] = ins_E_aom.power_to_voltage(par['Ex_SP_amplitude'])
    par['A_SP_voltage'] = ins_A_aom.power_to_voltage(par['A_SP_amplitude'])
    par['Ex_RO_voltage'] = ins_E_aom.power_to_voltage(par['Ex_RO_amplitude'])
    par['A_RO_voltage'] = ins_A_aom.power_to_voltage(par['A_RO_amplitude'])

    if (par['SSRO_repetitions'] > max_repetitions) or \
        (par['SP_duration'] > max_SP_bins) or \
        (par['SSRO_repetitions'] * par['SSRO_duration'] > max_SSRO_dim):
            print ('Error: maximum dimensions exceeded')
            return(-1)

    #print 'SP E amplitude: %s'%par['Ex_SP_voltage']
    #print 'SP A amplitude: %s'%par['A_SP_voltage']

    adwin.start_singleshot(
            load=True,
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
            green_repump_voltage = par['green_repump_voltage'],
            green_off_voltage = par['green_off_voltage'],
            Ex_CR_voltage = par['Ex_CR_voltage'],
            A_CR_voltage = par['A_CR_voltage'],
            Ex_SP_voltage = par['Ex_SP_voltage'],
            A_SP_voltage = par['A_SP_voltage'],
            Ex_RO_voltage = par['Ex_RO_voltage'],
            A_RO_voltage = par['A_RO_voltage'])

    qt.msleep(1)

    CR_counts = 0
    while (physical_adwin.Process_Status(9) == 1):
        reps_completed = physical_adwin.Get_Par(73)
        CR_counts = physical_adwin.Get_Par(70) - CR_counts
        cts = physical_adwin.Get_Par(26)
        trh = physical_adwin.Get_Par(25)
        print('completed %s / %s readout repetitions, %s CR counts/s'%(reps_completed,par['SSRO_repetitions'], CR_counts))
        print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        qt.msleep(5)
    physical_adwin.Stop_Process(9)
    
    reps_completed      = physical_adwin.Get_Par(73)
    print('completed %s / %s readout repetitions'%(reps_completed,par['SSRO_repetitions']))

    par_long   = physical_adwin.Get_Data_Long(20,1,25)
    par_float  = physical_adwin.Get_Data_Float(20,1,10)
    CR_before = physical_adwin.Get_Data_Long(22,1,reps_completed)
    CR_after  = physical_adwin.Get_Data_Long(23,1,reps_completed)
    SP_hist   = physical_adwin.Get_Data_Long(24,1,par['SP_duration'])
    RO_data   = physical_adwin.Get_Data_Long(25,1,
                    reps_completed * par['SSRO_duration'])
    RO_data = reshape(RO_data,(reps_completed,par['SSRO_duration']))
    statistics = physical_adwin.Get_Data_Long(26,1,10)

    repetitions = arange(reps_completed)
    sp_time = arange(par['SP_duration'])*par['cycle_duration']*3.333
    ssro_time = arange(par['SSRO_duration'])*par['cycle_duration']*3.333

    stat_str = ''
    stat_str += '# successful repetitions: %s\n'%(reps_completed)
    stat_str += '# total repumps: %s\n'%(statistics[0])
    stat_str += '# total repump counts: %s\n'%(statistics[1])
    stat_str += '# failed CR: %s\n'%(statistics[2])

    data.save()
    savdat={}
    savdat['repetitions']=repetitions
    savdat['counts']=CR_before
    data.save_dataset(name='ChargeRO_before', do_plot=False, 
        txt = {'statistics': stat_str}, data = savdat, idx_increment = False)
    savdat={}
    savdat['repetitions']=repetitions
    savdat['counts']=CR_after
    data.save_dataset(name='ChargeRO_after', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=sp_time
    savdat['counts']=SP_hist
    data.save_dataset(name='SP_histogram', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=ssro_time
    savdat['repetitions']=repetitions
    savdat['counts']=RO_data
    data.save_dataset(name='Spin_RO', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['par_long']=par_long
    savdat['par_float']=par_float
    data.save_dataset(name='parameters', do_plot=False, 
        data = savdat, idx_increment = False)
    data.save_dataset(name='parameters_dict', do_plot=False, 
        data = par, idx_increment = True)
   
    return 
    
def ssro_vs_Ex_amplitude(name, data, par, min_power, max_power, steps, reps_per_point):

    for i in linspace(min_power,max_power,steps):
        print '==============================='
        print 'Ex amplitude sweep: amplitude = ',(i)*1e-9
        print '==============================='
        par['SSRO_repetitions'] = reps_per_point
        par['Ex_RO_amplitude'] = (i)*1e-9
        par['A_RO_amplitude'] = 0

        ssro_init(name, data, par, do_ms0 = True, do_ms1 = True,
                A_SP_init_amplitude = 5e-9, Ex_SP_init_amplitude = 5e-9)

def ssro_vs_A_amplitude(name, data, par, min_power, max_power, steps, reps_per_point):

    for i in linspace(min_power,max_power,steps):
        print '==============================='
        print 'A amplitude sweep: amplitude = ',(i)*1e-9
        print '==============================='
        par['SSRO_repetitions'] = reps_per_point
        par['A_RO_amplitude'] = (i)*1e-9
        par['Ex_RO_amplitude'] = 0e-9
       
        ssro_init(name, data, par, do_ms0 = False, do_ms1 = True, 
        Ex_SP_init_amplitude    = 5e-9)


def ssro_vs_SP_amplitude(name, data, par, min_power, max_power, steps, reps_per_point):

    for i in linspace(min_power,max_power,steps):
        print '==============================='
        print 'SP amplitude sweep: amplitude = ',(i)*1e-9
        print '==============================='
        SP_amplitude = (i)*1e-9 
        par['SSRO_repetitions'] = reps_per_point
        par['A_RO_amplitude'] = 0
        par['Ex_RO_amplitude'] = 5e-9
        
        
        par['SP_duration'] = 5
        par['A_SP_amplitude']  = SP_amplitude
        par['Ex_SP_amplitude'] = 0.
        ssro(name,data,par)
        par['SP_duration'] = 250
        par['A_SP_amplitude']  = 0
        par['Ex_SP_amplitude'] = 5e-9
        ssro(name,data,par)

def ssro_vs_SP_duration(name, data, par, sp_power, max_duration, stepsize, reps_per_point):

    for i in range(1,max_duration+1,stepsize):
        print '==============================='
        print 'SP duration sweep:duration [us] = ',(i)*1e-6
        print '==============================='
        SP_duration = (i) 
        par['SSRO_repetitions'] = reps_per_point
        par['A_RO_amplitude'] = 0
        par['Ex_RO_amplitude'] = 5e-9
        
        
        par['SP_duration'] = SP_duration
        par['A_SP_amplitude']  = sp_power
        par['Ex_SP_amplitude'] = 0.
        ssro(name,data,par)
        par['SP_duration'] = 250
        par['A_SP_amplitude']  = 0
        par['Ex_SP_amplitude'] = 5e-9
        ssro(name,data,par)

def ssro_vs_SP(name, data, par, min_power, max_power,steps, max_duration, stepsize, reps_per_point):

    par['A_RO_amplitude'] = 0
    par['Ex_RO_amplitude'] = 5e-9
    for i in range(1,max_duration+1,stepsize):
        print '==============================='
        print 'SP duration sweep:duration [us] = ',(i)*1e-6
        print '==============================='
        SP_duration = (i)
        for j in linspace(min_power,max_power,steps):
            print '==============================='
            print 'SP amplitude sweep: amplitude = ',(j)*1e-9
            print '==============================='
            SP_amplitude = (j)*1e-9 
            par['SSRO_repetitions'] = reps_per_point
     
    
            par['SP_duration'] = SP_duration
            par['A_SP_amplitude']  = SP_amplitude
            par['Ex_SP_amplitude'] = 0.
            ssro(name,data,par)
            par['SP_duration'] = 250
            par['A_SP_amplitude']  = 0
            par['Ex_SP_amplitude'] = 5e-9
            ssro(name,data,par)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'w')): return
    qt.instruments['GreenAOM'].set_power(200e-6)
    qt.instruments['optimiz0r'].optimize(cnt=1,cycles=2,int_time=50)
    qt.instruments['GreenAOM'].set_power(0)

def ssro_vs_CR_duration(name, data, par, min_CR_duration, 
        max_CR_duration, steps, reps_per_point):

    for CR_duration in linspace(min_CR_duration,max_CR_duration,steps):
        if CR_duration == 0:
            print 'Invalid CR duration: CR_duration = 0.' 
            break
        
        print '================================='
        print 'CR duration sweep: duration = ', CR_duration,' us'
        print '================================='
        par['CR_duration'] = CR_duration
        par['SSRO_repetitions'] = reps_per_point
        par['Ex_CR_amplitude'] = 5e-9
        par['A_CR_amplitude'] = 5e-9
        #### INITIALIZE #####
        par['Ex_SP_amplitude'] = 0e-9
        par['A_SP_amplitude'] = 5e-9        
        ###### READOUT ######
        par['A_RO_amplitude'] = 0
        par['Ex_RO_amplitude'] = 5e-9
        ssro(name,data,par)

def ssro_vs_CR_power(name, data, par, min_CR_power, 
        max_CR_power, steps, reps_per_point):

    for CR_power in linspace(min_CR_power,max_CR_power,steps):
        if CR_power == 0:
            print 'Invalid CR power: CR_power = 0 nW.' 
        elif ins_E_aom.get_cal_a() < max_CR_power or ins_A_aom.get_cal_a() < max_CR_power:
            print 'Not enough power for the power sweep, check AOM calibration!'
            break
        
        print '================================='
        print 'CR power sweep: power = ', CR_power,' W'
        print '================================='
        par['CR_duration'] = 30
        par['SSRO_repetitions'] = reps_per_point
        par['Ex_CR_amplitude'] = CR_power
        par['A_CR_amplitude'] = CR_power
        #### INITIALIZE #####
        par['Ex_SP_amplitude'] = 0e-9
        par['A_SP_amplitude'] = 5e-9        
        ###### READOUT ######
        par['A_RO_amplitude'] = 0
        par['Ex_RO_amplitude'] = 5e-9
        ssro(name,data,par)


def ssro_init(name, data, par, do_ms0 = True, do_ms1 = True, 
        A_SP_init_amplitude     = 7e-9,
        Ex_SP_init_amplitude    = 7e-9):

    if do_ms0:
        par['A_SP_amplitude']  = A_SP_init_amplitude
        par['Ex_SP_amplitude'] = 0.
        ssro(name,data,par)

    if do_ms1:
        par['A_SP_amplitude']  = 0.
        par['Ex_SP_amplitude'] = Ex_SP_init_amplitude
        ssro(name,data,par)

def end_measurement():
    adwin.set_simple_counting()
    counters.set_is_running(True)
    ins_green_aom.set_power(200e-6)

    

def main():
    for i in range(50):
        name = 'SIL9'+str(i)
        qt.instruments['counters'].set_is_running(False)
        data = meas.Measurement(name,'ADwin_SSRO')
    #ssro_vs_SP_amplitude(name,data,par,min_power=1, max_power = 25, 
    #        steps = 25, reps_per_point = 5000)
    #
    #ssro_init(name,data,par)
    #ssro_vs_SP_duration(name,data,par,sp_power=25e-9, max_duration = 10, 
    #        stepsize = 1, reps_per_point = 5000)
    #ssro_vs_CR_duration(name, data, par, 20, 100, 5, 5000)
    #ssro_vs_CR_power(name, data, par, 15e-9, 15e-9, 1, 10000)
        ssro_vs_SP(name,data,par,min_power=1, max_power = 25, 
            steps = 25, max_duration=10, stepsize=1, reps_per_point = 5000)
        end_measurement()
        if (msvcrt.kbhit() and (msvcrt.getch() == 'e')): return


if __name__ == '__main__':
    main()

