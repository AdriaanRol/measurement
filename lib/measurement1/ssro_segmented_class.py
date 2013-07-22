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
from AWG_HW_sequencer_v2 import Sequence
from config import awgchannels_lt2 as awgcfg
#from analysis.lib.ssro import ssro_adwin as ssro_analyse
from config import experiment_lt2 as expdict
import ssro_MBI
from sequence import MBI_seq as MBIseq

lt1=False


class ssroADwinMeasurement(Measurement):
        


    def __init__(self,name):
        Measurement.__init__(self,name,mclass='Seg_RO')
        
            ########################################################### 
    ##
    ##  hardcoded in ADwin program (adjust there if necessary!)
    ##
        self.sildic = expdict.current_sample
        self.ssrodic = expdict.ssroprotocol
        self.MBIdic = expdict.MBIprotocol
        self.hardwaredic = expdict.hardware
        self.pulsedic = expdict.pulses

        self.MW_freq = self.sildic['MW_source_freq']
        self.MW_power = self.sildic['MW_source_power']
        
        
        self.max_repetitions = 1000000
        self.max_SP_bins = 500
        self.max_SSRO_dim = 3500000
        self.d = expdict.ssroprotocol
    def setup(self,lt1):
        self.awg = qt.instruments['AWG']
        self.microwaves=qt.instruments['SMB100']
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
            self.ins_E_aom=qt.instruments['MatisseAOM']
            self.ins_A_aom=qt.instruments['NewfocusAOM']
            self.adwin= qt.instruments['adwin']
            self.counters=qt.instruments['counters']
            self.physical_adwin=qt.instruments['physical_adwin']
            self.ctr_channel=1
        #if phase_lock:
        #    self.set_phase_locking_on = 1
        #    self.set_gate_good_phase = -1
        #else:
            #self.set_phase_locking_on = 0
            #self.set_gate_good_phase = -1
        if lt1:
            self.lt1 = True
        else:
            self.lt1 = False

        self.par = {}
        self.par['counter_channel'] =              self.ctr_channel
        self.par['laser_DAC_channel'] =      self.adwin.get_dac_channels()['green_aom']
        self.par['Ex_laser_DAC_channel'] =         self.adwin.get_dac_channels()['matisse_aom']
        self.par['A_laser_DAC_channel'] =          self.adwin.get_dac_channels()['newfocus_aom']
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
        self.par['segmented_RO_duration'] =         20
        self.par['do_MBI'] =                        0
        self.par['MBI_duration']=                   9
        self.par['wait_for_MBI_pulse'] =            self.MBIdic['wait_for_MBI_pulse']
        self.par['MBI_threshold'] =                 1
        
        self.par['green_repump_amplitude'] =       self.d['green_repump_amplitude']
        self.par['green_off_amplitude'] =          self.d['green_off_amplitude']
        self.par['Ex_CR_amplitude'] =              self.d['Ex_CR_amplitude']
        self.par['A_CR_amplitude'] =               self.d['A_CR_amplitude']
        self.par['Ex_SP_amplitude'] =              self.d['Ex_SP_amplitude']
        self.par['A_SP_amplitude'] =               self.d['A_SP_amplitude']
        self.par['Ex_RO_amplitude'] =              self.d['Ex_RO_amplitude']
        self.par['A_RO_amplitude'] =               self.d['A_RO_amplitude']
        self.par['segmented_Ex_RO_amplitude'] =    self.d['Ex_RO_amplitude']

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
        self.par['segmented_Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.par['segmented_Ex_RO_amplitude'])
        
        print self.par['segmented_Ex_RO_voltage']
        print self.par['segmented_RO_duration']
        print self.par['laser_DAC_channel']
    def prepare_AWG(self,seq_func,do_program=True):
        self.microwaves.set_iq('on')
        self.microwaves.set_frequency(self.MW_freq)
        self.microwaves.set_pulm('on')
        self.microwaves.set_power(self.MW_power)
        self.counters.set_is_running(False)
        
        seq = Sequence('spin_control')
        awgcfg.configure_sequence(seq,'mw_weak_meas')

        seq_wait_time = seq_func(self,seq)
        self.par['sequence_wait_time'] = seq_wait_time
        
        seq.set_instrument(self.awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
    
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        if (True==True):
            #start AWG
            self.awg.set_runmode('SEQ')
            self.awg.start()  
            while self.awg.get_state() != 'Waiting for trigger':
                qt.msleep(1)
        
            self.microwaves.set_status('on')
            qt.msleep(1)
            
            #start ADwin
            #self.spin_control(lt1,ssro_dict=ssro_dict)

        else:
            print 'Measurement aborted'
        return seq_wait_time    
    def ssro(self,name, data):

        self.par['green_repump_voltage'] = self.ins_green_aom.power_to_voltage(self.par['green_repump_amplitude'])
        self.par['green_off_voltage'] = 0.07
        self.par['Ex_CR_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_CR_amplitude'])
        self.par['A_CR_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_CR_amplitude'])
        self.par['Ex_SP_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_SP_amplitude'])
        self.par['A_SP_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_SP_amplitude'])
        self.par['Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_RO_amplitude'])
        self.par['A_RO_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_RO_amplitude'])
        self.par['segmented_Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.par['segmented_Ex_RO_amplitude'])

        if (self.par['SSRO_repetitions'] > self.max_repetitions) or \
            (self.par['SP_duration'] > self.max_SP_bins): 
            #(self.par['SSRO_repetitions'] * self.par['SSRO_duration'] > self.max_SSRO_dim):
                print ('Error: maximum dimensions exceeded')
                return(-1)
                print self.par['SSRO_repetitions']
                print self.max_repetitions
                print self.par['SP_duration']
                print self.max_SP_bins

        #print 'SP E amplitude: %s'%self.par['Ex_SP_voltage']
        #print 'SP A amplitude: %s'%self.par['A_SP_voltage']

        #if not(self.lt1):
            #self.adwin.set_singleshot_var(set_phase_locking_on = self.set_phase_locking_on)
            #self.adwin.set_singleshot_var(set_gate_good_phase =  self.set_gate_good_phase)            
        if (self.par['do_MBI'] == 0):
            print 'adwin.start_segmented_ssro'
            self.adwin.start_segmented_ssro(
                    load=True, stop_processes=['counter'],
                    counter_channel = self.par['counter_channel'],
                    laser_DAC_channel = self.par['laser_DAC_channel'],
                    Ex_laser_DAC_channel = self.par['Ex_laser_DAC_channel'],
                    A_laser_DAC_channel = self.par['A_laser_DAC_channel'],
                    AWG_start_DO_channel = self.par['AWG_start_DO_channel'],
                    AWG_done_DI_channel = self.par['AWG_done_DI_channel'],
                    send_AWG_start = self.par['send_AWG_start'],
                    wait_for_AWG_done = self.par['wait_for_AWG_done'],
                    repump_duration = self.par['green_repump_duration'],
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
                    segmented_RO_duration=self.par['segmented_RO_duration'],
                    repump_voltage = self.par['green_repump_voltage'],
                    #green_off_voltage = self.par['green_off_voltage'],
                    Ex_CR_voltage = self.par['Ex_CR_voltage'],
                    A_CR_voltage = self.par['A_CR_voltage'],
                    Ex_SP_voltage = self.par['Ex_SP_voltage'],
                    A_SP_voltage = self.par['A_SP_voltage'],
                    Ex_RO_voltage = self.par['Ex_RO_voltage'],
                    A_RO_voltage = self.par['A_RO_voltage'],
                    segmented_Ex_RO_voltage=self.par['segmented_Ex_RO_voltage'])
        else:
            print 'adwin.start_MBI_segmented_ssro'
            self.adwin.start_MBI_segmented_ssro(
                    load=True, stop_processes=['counter'],
                    counter_channel = self.par['counter_channel'],
                    laser_DAC_channel = self.par['laser_DAC_channel'],
                    Ex_laser_DAC_channel = self.par['Ex_laser_DAC_channel'],
                    A_laser_DAC_channel = self.par['A_laser_DAC_channel'],
                    AWG_start_DO_channel = self.MBIdic['AWG_start_DO_channel'],
                    AWG_done_DI_channel = self.MBIdic['AWG_done_DI_channel'],
                    send_AWG_start = self.MBIdic['send_AWG_start'],
                    wait_for_AWG_done = self.MBIdic['wait_for_AWG_done'],
                    repump_duration = self.par['green_repump_duration'],
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
                    segmented_RO_duration=self.par['segmented_RO_duration'],
                    AWG_event_jump_DO_channel = self.MBIdic['AWG_event_jump_DO_channel'],
                    MBI_duration=self.par['MBI_duration'],
                    wait_for_MBI_pulse = self.par['wait_for_MBI_pulse'],
                    MBI_threshold = self.par['MBI_threshold'],
                    sweep_length=len(self.par['sweep_par']),
                    repump_voltage = self.par['green_repump_voltage'],
                    #green_off_voltage = self.par['green_off_voltage'],
                    Ex_CR_voltage = self.par['Ex_CR_voltage'],
                    A_CR_voltage = self.par['A_CR_voltage'],
                    Ex_SP_voltage = self.par['Ex_SP_voltage'],
                    A_SP_voltage = self.par['A_SP_voltage'],
                    Ex_RO_voltage = self.par['Ex_RO_voltage'],
                    A_RO_voltage = self.par['A_RO_voltage'],
                    segmented_Ex_RO_voltage=self.par['segmented_Ex_RO_voltage'])
        qt.msleep(1)

        CR_counts = 0
        while (self.physical_adwin.Process_Status(9) == 1):
            reps_completed = self.physical_adwin.Get_Par(73)
            CR_counts = self.physical_adwin.Get_Par(70) - CR_counts
            CR_failed = self.physical_adwin.Get_Par(71)
            MBI_starts = self.physical_adwin.Get_Par(78)
            MBI_failed = self.physical_adwin.Get_Par(74)
            if reps_completed > 0:    
                CR_failed_percentage = 100*float(MBI_starts)/(float(CR_failed)+1*MBI_starts)
                MBI_failed_percentage = 100*float(reps_completed)/(float(MBI_failed)+1*reps_completed)
            else:
                CR_failed_percentage = 0
                MBI_failed_percentage = 0
            cts = self.physical_adwin.Get_Par(26)
            trh = self.physical_adwin.Get_Par(25)
            print('completed %s / %s readout repetitions, %.2f CR percentage succes,%.2f MBI percentage succes'%(reps_completed,self.par['SSRO_repetitions'], CR_failed_percentage,MBI_failed_percentage))
            print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                break
            qt.msleep(2.5)    
        self.physical_adwin.Stop_Process(9)
        
        reps_completed      = self.physical_adwin.Get_Par(73)
        print('completed %s / %s readout repetitions'%(reps_completed,self.par['SSRO_repetitions']))
        #if not(self.lt1):
        #    self.adwin.set_singleshot_var(set_phase_locking_on = 0)

        print 'end measurement'

        self.end_measurement()

        self.par_long   = self.physical_adwin.Get_Data_Long(20,1,25)
        self.par_float  = self.physical_adwin.Get_Data_Float(20,1,10)
        #CR_before = self.physical_adwin.Get_Data_Long(22,1,reps_completed)
        #CR_after  = self.physical_adwin.Get_Data_Long(23,1,reps_completed)
        CR_before=np.zeros(reps_completed)
        CR_after=np.zeros(reps_completed)
        SP_hist   = self.physical_adwin.Get_Data_Long(24,1,self.par['SP_duration'])
        #RO_data   = self.physical_adwin.Get_Data_Long(25,1,
        #                reps_completed * self.par['SSRO_duration'])
        #RO_data = np.reshape(RO_data,(reps_completed,self.par['SSRO_duration']))
        print 'stats'
        statistics = self.physical_adwin.Get_Data_Long(26,1,10)
        segment_number = self.physical_adwin.Get_Data_Long(27,1,self.par['segmented_RO_duration']+1)
        full_RO_data = self.physical_adwin.Get_Data_Long(28,1, reps_completed)
        segmented_RO_data = self.physical_adwin.Get_Data_Long(29,1, reps_completed)
        repetitions = np.arange(reps_completed)
        sp_time = np.arange(self.par['SP_duration'])*self.par['cycle_duration']*3.333
        ssro_time = np.arange(self.par['SSRO_duration'])*self.par['cycle_duration']*3.333
        if (self.par['do_MBI'] == 1):
            cond_RO_data = self.physical_adwin.Get_Data_Long(31,1, len(self.par['sweep_par'])*(self.par['segmented_RO_duration']+1))
            savdat={}
            SSRO_RO_data = self.physical_adwin.Get_Data_Long(30,1, len(self.par['sweep_par']))
            savdat['SSRO_counts']=SSRO_RO_data
            savdat['cond_RO_data']=cond_RO_data
            savdat['sweep_axis']=self.par['sweep_par']
            savdat['sweep_par_name'] = self.par['sweep_par_name']
            savdat['time']=self.par['SSRO_duration']
            data.save_dataset(name='Spin_RO', do_plot=False, 
            data = savdat, idx_increment = False)
        else:
            savdat={}
            savdat['time']=ssro_time
            savdat['repetitions']=repetitions
            savdat['counts']=full_RO_data
            savdat['sweep_axis']=self.par['sweep_par']
            savdat['sweep_par_name'] = self.par['sweep_par_name']
            data.save_dataset(name='Spin_RO', do_plot=False, 
                data = savdat, idx_increment = False)
        

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
        savdat['segment_number']=segment_number
        data.save_dataset(name='segment_number', do_plot=False, 
        data = savdat, idx_increment = False)

        savdat={}
        savdat['full_RO_data']=full_RO_data
        data.save_dataset(name='full_RO_data', do_plot=False, 
            data = savdat, idx_increment = False)

        savdat={}
        savdat['segmented_RO_data']=segmented_RO_data
        data.save_dataset(name='segmented_RO_data', do_plot=False, 
            data = savdat, idx_increment = False)
        

        
        savdat={}
        savdat['time']=sp_time
        savdat['counts']=SP_hist
        data.save_dataset(name='SP_histogram', do_plot=False, 
            data = savdat, idx_increment = False)
 
        savdat={}
        savdat['par_long']=self.par_long
        savdat['par_float']=self.par_float
        data.save_dataset(name='parameters', do_plot=False, 
            data = savdat, idx_increment = False)
        data.save_dataset(name='parameters_dict', do_plot=False, 
            data = self.par, idx_increment = True)
        if (self.par['do_MBI'] == 1):
            ######################
            ###statistics file####
            ######################
            savdat={}
            savdat['completed_repetitions']=(reps_completed/len(self.par['sweep_par']))
            savdat['total_repumps']=statistics[0]
            savdat['total_repump_counts']=statistics[1]
            savdat['noof_failed_CR_checks']=statistics[2]
            savdat['mw_center_freq']=self.sildic['MW_freq_center']
            savdat['mw_drive_freq']=self.MW_freq
            savdat['mw_power']=self.MW_power
            
            ####
            savdat['RO_reps'] = self.nr_of_RO_steps  
            savdat['sweep_par_name'] = self.par['sweep_par_name']
            savdat['sweep_par'] = self.par['sweep_par']
            savdat['noof_datapoints'] =len(self.par['sweep_par'])
                
            data.save_dataset(name='statics_and_parameters', do_plot=False, 
                data = savdat, idx_increment = True)
        return 


    def end_measurement(self):
        self.awg.stop()
        self.awg.set_runmode('CONT')
        #self.adwin.set_simple_counting()
        
        self.microwaves.set_status('off')
        self.microwaves.set_iq('off')
        self.microwaves.set_pulm('off')
        
    def ssro_vs_segmented_Ex_amplitude(self,name, data, min_power, max_power, steps, reps_per_point, do_ms0 = True, do_ms1=False):
        self.par['sweep_par_name']='seg RO duration (us)'
        durations=[4,6,8,10,15,25,50,75,100]
        self.par['sweep_par']=durations
        #for i in np.linspace(min_power,max_power,steps):
        for i in durations:
            print '==============================='
            print 'segmented Ex amplitude sweep: amplitude = ',(i)*1e-9
            print '==============================='
            self.par['SSRO_repetitions'] = reps_per_point
            #self.par['segmented_Ex_RO_amplitude'] = 1e-9
            self.par['segmented_RO_duration'] = i
            self.par['A_RO_amplitude'] = 0

            self.ssro_init(name, data, do_ms0 = do_ms0, do_ms1 = do_ms1)

       

    def ssro_init(self,name, data, do_ms0 = True, do_ms1 = True):
        A_SP_init_amplitude     = self.par['A_SP_amplitude']
        Ex_SP_init_amplitude    = self.par['Ex_SP_amplitude']
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
        #self.adwin.set_simple_counting()
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
            self.ssro_vs_segmented_Ex_amplitude(name,m, 0, 150, 12, 50000)
        else:
            self.ssro_init(name,m)
        

        self.end_measurement()

            
        
def ssro_segmented_sweep(reps=5000,Ex_p='exp_dic',A_p=0,sweep_power=True,lt1=False,A_SP_power='exp_dic',name=''):
    if lt1:
        name='_LT1_'+name
    else:
        name='_LT2_' +name
    m = ssroADwinMeasurement(name)
    m.setup(lt1)
    m.par['SSRO_repetitions'] = reps
    m.par['segmented_Ex_RO_amplitude']=5e-9
    m.par['segmented_RO_duration'] = 100
    if Ex_p == 'exp_dic':
        m.par['Ex_RO_amplitude'] = m.d['Ex_RO_amplitude']
    else:    
        m.par['Ex_RO_amplitude'] = Ex_p
    if A_SP_power != 'exp_dic':
        m.par['A_SP_amplitude']=A_SP_power    
    m.measure(m,name,sweep_power)
    #ssro_analyse.run_all(ssro_analyse.get_latest_data())

def nuclear_ramsey_segmented_RO(reps=5000,nr_of_datapoints=21,lt1=False,A_SP_power='exp_dic',init_line='-1',RO_line='0-1',name='', seg_RO_dur = 100.):
    if lt1:
        name='_LT1_'+name
    else:
        name='_LT2_' +name
    m = ssroADwinMeasurement(name)
    m.setup(lt1)
    
    m.par['segmented_Ex_RO_amplitude']=5e-9
    m.par['segmented_RO_duration'] = seg_RO_dur
    m.par['Ex_RO_amplitude'] = 25e-9
    m.par['A_SP_amplitude']=m.d['A_SP_amplitude']
    m.par['do_MBI']=1
    m.par['send_AWG_start'] =          1
   

    m.nr_of_datapoints = nr_of_datapoints
    m.par['SSRO_repetitions'] = reps*nr_of_datapoints
    
    m.RF_phase=np.linspace(0,360,nr_of_datapoints)
    
    m.par['send_AWG_start'] = 1
    RF_freq = m.sildic['mI_m1_freq']
    m.do_incr_RO_steps = 0.
    m.incr_RO_steps=1.
    m.nr_of_RO_steps = 2.
    m.Ex_RO_amplitude = m.ssrodic['Ex_RO_amplitude']
    m.MBI_duration=m.MBIdic['MBI_RO_duration']
    m.wait_for_MBI_pulse = m.MBIdic['wait_for_MBI_pulse']
    m.MBI_threshold = 1
    m.MBI_mod_freq = ssro_MBI.get_freq(m,init_line)
    m.RO_mod_freq = ssro_MBI.get_freq(m,RO_line)
    m.MW_mod_freq = (ssro_MBI.get_freq(m,init_line))*np.ones(nr_of_datapoints)
    m.MW_pulse_len = m.pulsedic['shelving_len']*np.ones(nr_of_datapoints)
    m.MW_pulse_amp = m.pulsedic['shelving_amp']*np.ones(nr_of_datapoints)
    m.do_MW_pulse_after_RF=True
    m.RO_element_do_trigger=False

    m.wait_after_RO = 100+(m.pulsedic['RF_pi2_len']/1000)
    m.rep_wait_el = m.par['segmented_RO_duration']+17
    m.RF_freq = RF_freq*np.ones(nr_of_datapoints)
    m.par['sweep_par'] = m.RF_phase
    m.par['sweep_par_name'] = 'RF phase (degree)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps)  
    m.par['sweep_par_name'] = 'Phase'
    m.par['sequence_wait_time']=(m.prepare_AWG(MBIseq.Nucl_Ramsey)-m.par['segmented_RO_duration'])/2.
    print m.par['sequence_wait_time']
    m.ssro(name,m)
    #ssro_analyse.run_all(ssro_analyse.get_latest_data())