'''
This is my first attempt to use the measurement class (measurement.measurement)
to write a measurement (ssro with adwin), which is a class on its self.
-Machiel
'''

import qt
import numpy as np
import ctypes
import inspect
import time
import msvcrt
from measurement import Measurement
from analysis.lib.ssro import ssro_adwin as ssro_analyse
from config import experiment_lt2 as expdict


lt1=False


class ssroADwinMeasurement(Measurement):
        


    def __init__(self,name):
        Measurement.__init__(self,name,mclass='ADwin_SSRO')
        
            ########################################################### 
    ##
    ##  hardcoded in ADwin program (adjust there if necessary!)
    ##
        self.max_repetitions = 20000
        self.max_SP_bins = 500
        self.max_SSRO_dim = 3500000
        self.d = expdict.ssroprotocol
    def setup(self,lt1,phase_lock):
        
        if lt1:
            self.ins_green_aom=qt.instruments['GreenAOM_lt1']
            self.ins_E_aom=qt.instruments['MatisseAOM_lt1']
            self.ins_A_aom=qt.instruments['NewfocusAOM_lt1']
            self.adwin=qt.instruments['adwin_lt1']
            self.counters=qt.instruments['counters_lt1']
            self.physical_adwin=qt.instruments['physical_adwin_lt1']
            self.ctr_channel=2
        else:
            self.ins_green_aom=qt.instruments['GreenAOM']
            self.ins_E_aom=qt.instruments['NewfocusAOM']
            self.ins_A_aom=qt.instruments['MatisseAOM']
            self.adwin= qt.instruments['adwin']
            self.counters=qt.instruments['counters']
            self.physical_adwin=qt.instruments['physical_adwin']
            self.ctr_channel=1
        if phase_lock:
            self.set_phase_locking_on = 1
            self.set_gate_good_phase = -1
        else:
            self.set_phase_locking_on = 0
            self.set_gate_good_phase = -1
        if lt1:
            self.lt1 = True
        else:
            self.lt1 = False

        self.par = {}
        self.par['counter_channel'] =              self.ctr_channel
        self.par['green_laser_DAC_channel'] =      self.adwin.get_dac_channels()['green_aom']
        self.par['Ex_laser_DAC_channel'] =         self.adwin.get_dac_channels()['newfocus_aom']
        self.par['A_laser_DAC_channel'] =          self.adwin.get_dac_channels()['matisse_aom']
        self.par['AWG_start_DO_channel'] =         1
        self.par['AWG_done_DI_channel'] =          8
        self.par['send_AWG_start'] =               0
        self.par['wait_for_AWG_done'] =            0
        self.par['green_repump_duration'] =        self.d['green_repump_duration']
        self.par['CR_duration'] =                  self.d['CR_duration']
        self.par['SP_duration'] =                  self.d['SP_A_duration']
        self.par['SP_filter_duration'] =           self.d['SP_filter_duration']
        self.par['sequence_wait_time'] =           self.d['sequence_wait_time']
        self.par['wait_after_pulse_duration'] =    self.d['wait_after_pulse_duration']
        self.par['CR_preselect'] =                 self.d['CR_preselect']
        self.par['SSRO_repetitions'] =             10000
        self.par['SSRO_duration'] =                50 #NOTE this times reps must not exceed 1E6
        self.par['SSRO_stop_after_first_photon'] = 0
        self.par['cycle_duration'] =               300

        self.par['green_repump_amplitude'] =       self.d['green_repump_amplitude']
        self.par['green_off_amplitude'] =          self.d['green_off_amplitude']
        self.par['Ex_CR_amplitude'] =              self.d['Ex_CR_amplitude']
        self.par['A_CR_amplitude'] =               self.d['A_CR_amplitude']
        self.par['Ex_SP_amplitude'] =              self.d['Ex_SP_amplitude']
        self.par['A_SP_amplitude'] =               self.d['A_SP_amplitude']
        self.par['Ex_RO_amplitude'] =              self.d['Ex_RO_amplitude']
        self.par['A_RO_amplitude'] =               self.d['A_RO_amplitude']


        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)
        self.ins_green_aom.set_cur_controller('ADWIN')
        self.ins_E_aom.set_cur_controller('ADWIN')
        self.ins_A_aom.set_cur_controller('ADWIN')
        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)

        self.par['green_repump_voltage'] = self.ins_green_aom.power_to_voltage(self.par['green_repump_amplitude'])
        self.par['green_off_voltage'] = self.ins_green_aom.power_to_voltage(self.par['green_off_amplitude'])
        self.par['Ex_CR_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_CR_amplitude'])
        self.par['A_CR_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_CR_amplitude'])
        self.par['Ex_SP_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_SP_amplitude'])
        self.par['A_SP_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_SP_amplitude'])
        self.par['Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_RO_amplitude'])
        self.par['A_RO_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_RO_amplitude'])

    def ssro(self,name, data):
        
        self.par['green_repump_voltage'] = self.ins_green_aom.power_to_voltage(self.par['green_repump_amplitude'])
        self.par['green_off_voltage'] = 0.07
        self.par['Ex_CR_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_CR_amplitude'])
        self.par['A_CR_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_CR_amplitude'])
        self.par['Ex_SP_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_SP_amplitude'])
        self.par['A_SP_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_SP_amplitude'])
        self.par['Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_RO_amplitude'])
        self.par['A_RO_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_RO_amplitude'])


        if (self.par['SSRO_repetitions'] > self.max_repetitions) or \
            (self.par['SP_duration'] > self.max_SP_bins) or \
            (self.par['SSRO_repetitions'] * self.par['SSRO_duration'] > self.max_SSRO_dim):
                print ('Error: maximum dimensions exceeded')
                return(-1)

        #print 'SP E amplitude: %s'%self.par['Ex_SP_voltage']
        #print 'SP A amplitude: %s'%self.par['A_SP_voltage']

        if not(self.lt1):
            self.adwin.set_spincontrol_var(set_phase_locking_on = self.set_phase_locking_on)
            self.adwin.set_spincontrol_var(set_gate_good_phase =  self.set_gate_good_phase)            

        self.adwin.start_singleshot(
                load=True, stop_processes=['counter'],
                counter_channel = self.par['counter_channel'],
                green_laser_DAC_channel = self.par['green_laser_DAC_channel'],
                Ex_laser_DAC_channel = self.par['Ex_laser_DAC_channel'],
                A_laser_DAC_channel = self.par['A_laser_DAC_channel'],
                AWG_start_DO_channel = self.par['AWG_start_DO_channel'],
                AWG_done_DI_channel = self.par['AWG_done_DI_channel'],
                send_AWG_start = self.par['send_AWG_start'],
                wait_for_AWG_done = self.par['wait_for_AWG_done'],
                green_repump_duration = self.par['green_repump_duration'],
                CR_duration = self.par['CR_duration'],
                SP_duration = self.par['SP_duration'],
                SP_filter_duration = self.par['SP_filter_duration'],
                sequence_wait_time = self.par['sequence_wait_time'],
                wait_after_pulse_duration = self.par['wait_after_pulse_duration'],
                CR_preselect = self.par['CR_preselect'],
                SSRO_repetitions = self.par['SSRO_repetitions'],
                SSRO_duration = self.par['SSRO_duration'],
                SSRO_stop_after_first_photon = self.par['SSRO_stop_after_first_photon'],
                cycle_duration = self.par['cycle_duration'],
                green_repump_voltage = self.par['green_repump_voltage'],
                green_off_voltage = self.par['green_off_voltage'],
                Ex_CR_voltage = self.par['Ex_CR_voltage'],
                A_CR_voltage = self.par['A_CR_voltage'],
                Ex_SP_voltage = self.par['Ex_SP_voltage'],
                A_SP_voltage = self.par['A_SP_voltage'],
                Ex_RO_voltage = self.par['Ex_RO_voltage'],
                A_RO_voltage = self.par['A_RO_voltage'])


        qt.msleep(1)

        CR_counts = 0
        while (self.physical_adwin.Process_Status(9) == 1):
            reps_completed = self.physical_adwin.Get_Par(73)
            CR_counts = self.physical_adwin.Get_Par(70) - CR_counts
            cts = self.physical_adwin.Get_Par(26)
            trh = self.physical_adwin.Get_Par(25)
            print('completed %s / %s readout repetitions, %s CR counts/s'%(reps_completed,self.par['SSRO_repetitions'], CR_counts))

            print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
            qt.msleep(1)
        self.physical_adwin.Stop_Process(9)
        
        reps_completed      = self.physical_adwin.Get_Par(73)
        print('completed %s / %s readout repetitions'%(reps_completed,self.par['SSRO_repetitions']))
        if not(self.lt1):
            self.adwin.set_spincontrol_var(set_phase_locking_on = 0)

        self.par_long   = self.physical_adwin.Get_Data_Long(20,1,25)
        self.par_float  = self.physical_adwin.Get_Data_Float(20,1,10)
        CR_before = self.physical_adwin.Get_Data_Long(22,1,reps_completed)
        CR_after  = self.physical_adwin.Get_Data_Long(23,1,reps_completed)
        SP_hist   = self.physical_adwin.Get_Data_Long(24,1,self.par['SP_duration'])
        RO_data   = self.physical_adwin.Get_Data_Long(25,1,
                        reps_completed * self.par['SSRO_duration'])
        RO_data = np.reshape(RO_data,(reps_completed,self.par['SSRO_duration']))
        statistics = self.physical_adwin.Get_Data_Long(26,1,10)

        repetitions = np.arange(reps_completed)
        sp_time = np.arange(self.par['SP_duration'])*self.par['cycle_duration']*3.333
        ssro_time = np.arange(self.par['SSRO_duration'])*self.par['cycle_duration']*3.333

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
        savdat['par_long']=self.par_long
        savdat['par_float']=self.par_float
        data.save_dataset(name='parameters', do_plot=False, 
            data = savdat, idx_increment = False)
        data.save_dataset(name='parameters_dict', do_plot=False, 
            data = self.par, idx_increment = True)
       
        return 
        
    def ssro_vs_Ex_amplitude(self,name, data, min_power, max_power, steps, reps_per_point, do_ms0 = True, do_ms1=True):


        for i in np.linspace(min_power,max_power,steps):
            print '==============================='
            print 'Ex amplitude sweep: amplitude = ',(i)*1e-9
            print '==============================='
            self.par['SSRO_repetitions'] = reps_per_point
            self.par['Ex_RO_amplitude'] = (i)*1e-9
            self.par['A_RO_amplitude'] = 0

            self.ssro_init(name, data, do_ms0 = do_ms0, do_ms1 = do_ms1,
                    A_SP_init_amplitude = 5e-9, Ex_SP_init_amplitude = 5e-9)

    def ssro_vs_A_amplitude(self,name, data, min_power, max_power, steps, reps_per_point):

        for i in linspace(min_power,max_power,steps):
            print '==============================='
            print 'A amplitude sweep: amplitude = ',(i)*1e-9
            print '==============================='
            self.par['SSRO_repetitions'] = reps_per_point
            self.par['A_RO_amplitude'] = (i)*1e-9
            self.par['Ex_RO_amplitude'] = 0e-9
           
            self.ssro_init(name, data,  do_ms0 = False, do_ms1 = True, 
            Ex_SP_init_amplitude    = 12e-9)


    def ssro_vs_SP_amplitude(self,name, data,  min_power, max_power, steps, reps_per_point):


        for i in linspace(min_power,max_power,steps):
            print '==============================='
            print 'SP amplitude sweep: amplitude = ',(i)*1e-9
            print '==============================='
            SP_amplitude = (i)*1e-9 
            self.par['SSRO_repetitions'] = reps_per_point
            self.par['A_RO_amplitude'] = 0
            self.par['Ex_RO_amplitude'] = 5e-9
            
            
            self.par['SP_duration'] = 50
            self.par['A_SP_amplitude']  = SP_amplitude
            self.par['Ex_SP_amplitude'] = 0.
            self.ssro(name,data)
            self.par['SP_duration'] = 50
            self.par['A_SP_amplitude']  = 0
            self.par['Ex_SP_amplitude'] = 5e-9
            self.ssro(name,data)

    def ssro_vs_SP_duration(self,name, data,  sp_power, max_duration, stepsize, reps_per_point):


        for i in range(1,max_duration+1,stepsize):
            print '==============================='
            print 'SP duration sweep:duration [us] = ',(i)*1e-6
            print '==============================='
            SP_duration = (i) 
            self.par['SSRO_repetitions'] = reps_per_point
            self.par['A_RO_amplitude'] = 0
            self.par['Ex_RO_amplitude'] = 5e-9
            
            
            self.par['SP_duration'] = SP_duration
            self.par['A_SP_amplitude']  = sp_power
            self.par['Ex_SP_amplitude'] = 0.
            self.ssro(name,data)
            self.par['SP_duration'] = 250
            self.par['A_SP_amplitude']  = 0
            self.par['Ex_SP_amplitude'] = 5e-9
            self.ssro(name,data)

    def ssro_vs_SP(self,name, data, min_power, max_power,steps, max_duration, stepsize, reps_per_point):

        self.par['A_RO_amplitude'] = 0
        self.par['Ex_RO_amplitude'] = 5e-9

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
                self.par['SSRO_repetitions'] = reps_per_point
         
        
                self.par['SP_duration'] = SP_duration
                self.par['A_SP_amplitude']  = SP_amplitude
                self.par['Ex_SP_amplitude'] = 0.
                self.ssro(name,data)
                self.par['SP_duration'] = 250
                self.par['A_SP_amplitude']  = 0
                self.par['Ex_SP_amplitude'] = 5e-9
                self.ssro(name,data)

                if (msvcrt.kbhit() and (msvcrt.getch() == 'w')): return
        qt.instruments['GreenAOM'].set_power(200e-6)
        qt.instruments['optimiz0r'].optimize(cnt=1,cycles=2,int_time=50)
        qt.instruments['GreenAOM'].set_power(0)

    def ssro_vs_CR_duration(self,name, data, min_CR_duration, 

            max_CR_duration, steps, reps_per_point):

        for CR_duration in linspace(min_CR_duration,max_CR_duration,steps):
            if CR_duration == 0:
                print 'Invalid CR duration: CR_duration = 0.' 
                break
            
            print '================================='
            print 'CR duration sweep: duration = ', CR_duration,' us'
            print '================================='
            self.par['CR_duration'] = CR_duration
            self.par['SSRO_repetitions'] = reps_per_point
            self.par['Ex_CR_amplitude'] = 5e-9
            self.par['A_CR_amplitude'] = 5e-9
            #### INITIALIZE #####
            self.par['Ex_SP_amplitude'] = 0e-9
            self.par['A_SP_amplitude'] = 5e-9        
            ###### READOUT ######
            self.par['A_RO_amplitude'] = 0
            self.par['Ex_RO_amplitude'] = 5e-9
            self.ssro(name,data)

    def ssro_vs_CR_power(self,name, data,  min_CR_power, 

            max_CR_power, steps, reps_per_point):

        for k,CR_power in enumerate(linspace(min_CR_power,max_CR_power,steps)):
            if CR_power == 0:
                print 'Invalid CR power: CR_power = 0 nW.' 
            elif self.ins_E_aom.get_cal_a() < max_CR_power or self.ins_A_aom.get_cal_a() < max_CR_power:
                print 'Not enough power for the power sweep, check AOM calibration!'
                break
            
            print '================================='
            print 'CR power sweep: power = ', CR_power,' W'
            print '================================='
            self.par['CR_duration'] = 30
            self.par['SSRO_repetitions'] = reps_per_point
            self.par['Ex_CR_amplitude'] = CR_power
            self.par['A_CR_amplitude'] = 0#CR_power


            #### INITIALIZE #####
            self.par['Ex_SP_amplitude'] = 0e-9
            self.par['A_SP_amplitude'] = 15e-9
            self.par['SP_duration'] = 2
            ###### READOUT ######
            self.par['A_RO_amplitude'] = 0
            self.par['Ex_RO_amplitude'] = 5e-9
            self.ssro(name,data)

    def ssro_vs_Ex_CR_power(self,name, data,  min_Ex_CR_power, 

            max_Ex_CR_power, steps, reps_per_point):

        for k,CR_power in enumerate(linspace(min_Ex_CR_power,max_Ex_CR_power,steps)):
            if CR_power == 0:
                print 'Invalid CR power: CR_power = 0 nW.' 
            elif self.ins_E_aom.get_cal_a() < max_Ex_CR_power:
                print 'Not enough power for the power sweep, check AOM calibration!'
                break
            
            print '================================='
            print 'CR power sweep: power = ', CR_power,' W'
            print '================================='
            self.par['CR_duration'] = 30
            self.par['SSRO_repetitions'] = reps_per_point
            self.par['Ex_CR_amplitude'] = CR_power
            self.par['A_CR_amplitude'] = 0e-9


            #### INITIALIZE #####
            self.par['Ex_SP_amplitude'] = 0e-9
            self.par['A_SP_amplitude'] = 15e-9
            self.par['SP_duration'] = 2
            ###### READOUT ######
            self.par['A_RO_amplitude'] = 0
            self.par['Ex_RO_amplitude'] = 5e-9
            self.ssro(name,data)



    def ssro_init(self,name, data, do_ms0 = True, do_ms1 = True, 
            A_SP_init_amplitude     = 5e-9,
            Ex_SP_init_amplitude    = 5e-9):

        if do_ms0:
            self.par['A_SP_amplitude']  =  A_SP_init_amplitude
            self.par['Ex_SP_amplitude'] =  0.
            self.par['do_ms0'] = 1
            self.par['do_ms1'] = 0
            self.ssro(name,data)

        if do_ms1:
            self.par['A_SP_amplitude']  = 0.
            self.par['Ex_SP_amplitude'] = Ex_SP_init_amplitude
            self.par['do_ms0'] = 0
            self.par['do_ms1'] = 1
            self.ssro(name,data)

    def end_measurement(self,):
        self.adwin.set_simple_counting()
        self.counters.set_is_running(True)
        self.ins_green_aom.set_power(100e-6)

        

    def measure(self,m,name,sweep_power):

        self.counters.set_is_running(False)
        #data = Measurement.Measurement(name,'ADwin_SSRO')
        #ssro_vs_SP_amplitude(name,data,par,min_power=2, max_power = 20, 
        #        steps = 10, reps_per_point = 5000)
        #ssro_vs_Ex_amplitude(name, data, par, 2, 30, 15, 10000, do_ms1=True)
        #ssro_vs_A_amplitude(name, data, par, 1, 25, 13, 5000)

        #ssro_vs_SP_duration(name,data,par,sp_power=25e-9, max_duration = 10, 
        #        stepsize = 1, reps_per_point = 5000)
        #ssro_vs_CR_duration(name, data, par, 20, 100, 5, 5000)
         
        #ssro_vs_Ex_CR_power(name, data, par, 
        #        min_Ex_CR_power = 5e-9, max_Ex_CR_power = 15e-9, 
        #        steps = 5, reps_per_point = 5000) 

        if sweep_power:
            self.ssro_vs_Ex_amplitude(name,m, 1, 20, 7, 5000)
        else:
            self.ssro_init(name,m, A_SP_init_amplitude = self.d['A_SP_amplitude'], Ex_SP_init_amplitude = self.d['Ex_SP_amplitude'])
        

        self.end_measurement()

        ### 2D Spin Pumping sweep
        #for i in range(50):
        #    name = 'SIL9'+str(i)
        #    self.counters.set_is_running(False)
        #    data = meas.Measurement(name,'ADwin_SSRO')
        #    ssro_vs_SP(name,data,par,min_power=1, max_power = 25, 
        #        steps = 25, max_duration=10, stepsize=1, reps_per_point = 5000)
        #    end_measurement()
        #    if (msvcrt.kbhit() and (msvcrt.getch() == 'e')): return

def ssro_ADwin_Cal(reps=20000,Ex_p='exp_dic',A_p=0,sweep_power=False,lt1=False,phase_lock=1,A_SP_power='exp_dic',name=''):
    if lt1:
        name='_LT1_'+name
    else:
        name='_LT2_' +name
    m = ssroADwinMeasurement(name)
    m.setup(lt1,phase_lock)
    m.par['SSRO_repetitions'] = reps
    if Ex_p == 'exp_dic':
        m.par['Ex_RO_amplitude'] = m.d['Ex_RO_amplitude']
    else:    
        m.par['Ex_RO_amplitude'] = Ex_p
    if A_SP_power != 'exp_dic':
        m.par['A_SP_amplitude']=A_SP_power    
    m.measure(m,name,sweep_power)
    ssro_analyse.run_all(ssro_analyse.get_latest_data())

