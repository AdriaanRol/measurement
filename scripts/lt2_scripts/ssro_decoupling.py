import qt
import numpy as np
import ctypes
import inspect
import time as dtime
import msvcrt
from .measurement import Measurement
from AWG_HW_sequencer_v2 import Sequence
import PQ_measurement_generator_v2 as pqm
import ssro_ADwin_class as ssro_ADwin
import esr
from config import awgchannels_lt2 as awgcfg
from sequence import common as commonseq
from sequence import decoupling_v2 as dec
from analysis import lde_calibration, spin_control 



class Decoupling(Measurement):

    def __init__(self,name):
        Measurement.__init__(self,name,mclass='Decoupling')
    ###########################################################
##
##  hardcoded in ADwin program (adjust there if necessary!)
##

        self.max_SP_bins = 500
        self.max_RO_dim = 1000000

##
###########################################################


        self.set_phase_locking_on = 0
        self.set_gate_good_phase = -1

        self.f_drive            =                   2.828e9

        self.par = {}
        
        self.par['AWG_start_DO_channel'] =         1
        self.par['AWG_done_DI_channel'] =          8
        self.par['send_AWG_start'] =               1
        self.par['wait_for_AWG_done'] =            0
        self.par['green_repump_duration'] =        10
        self.par['CR_duration'] =                  60
        self.par['SP_duration'] =                  50
        self.par['SP_filter_duration'] =           0
        self.par['sequence_wait_time'] =           int(np.ceil(1e-3)+2)
        self.par['wait_after_pulse_duration'] =    1
        self.par['CR_preselect'] =                 1000

        self.par['reps_per_datapoint'] =           1000
        self.par['sweep_length'] =                 int(21)
        self.par['RO_repetitions'] =               int(21*1000)
        self.par['RO_duration'] =                  22

        self.par['cycle_duration'] =               300
        self.par['CR_probe'] =                     100

        self.par['green_repump_amplitude'] =       200e-6
        self.par['green_off_amplitude'] =          0e-6
        self.par['Ex_CR_amplitude'] =              20e-9 #OK
        self.par['A_CR_amplitude'] =               15e-9 #OK
        self.par['Ex_SP_amplitude'] =              0 
        self.par['A_SP_amplitude'] =               15e-9 #OK: PREPARE IN MS = 0
        self.par['Ex_RO_amplitude'] =              8e-9 #OK: READOUT MS = 0
        self.par['A_RO_amplitude'] =               0e-9

        self.par['min_sweep_par'] =                  0
        self.par['max_sweep_par'] =                  1
        self.par['sweep_par_name'] =                 ''
        self.par['sweep_par']   =                  np.linspace(1,21,21)


    def setup(self,lt1=False):
        self.mwpower_lt1 =               20               #in dBm
        self.mwpower_lt2 =               20              #in dBm

        if lt1:
            self.ins_green_aom=qt.instruments['GreenAOM_lt1']
            self.ins_E_aom=qt.instruments['MatisseAOM_lt1']
            self.ins_A_aom=qt.instruments['NewfocusAOM_lt1']
            self.adwin=qt.instruments['adwin_lt1']
            self.counters=qt.instruments['counters_lt1']
            self.physical_adwin=qt.instruments['physical_adwin_lt1']
            self.microwaves = qt.instruments['SMB100_lt1']
            self.ctr_channel=2
            self.mwpower = self.mwpower_lt1
            self.microwaves.set_status('off')
            self.adwin_lt2=qt.instruments['adwin']
        else:
            self.ins_green_aom=qt.instruments['GreenAOM']
            self.ins_E_aom=qt.instruments['MatisseAOM']
            self.ins_A_aom=qt.instruments['NewfocusAOM']
            #self.adwin = adwin_lt2 
            self.adwin=qt.instruments['adwin']
            self.counters=qt.instruments['counters']
            self.physical_adwin=qt.instruments['physical_adwin']
            self.microwaves = qt.instruments['SMB100']
            self.ctr_channel=1
            self.mwpower = self.mwpower_lt2
            self.microwaves.set_status('off')

        self.awg = qt.instruments['AWG']
        self.temp = qt.instruments['temperature_lt1']
        
        self.par['counter_channel'] =              self.ctr_channel
        self.par['green_laser_DAC_channel'] =      self.adwin.get_dac_channels()['green_aom']
        self.par['Ex_laser_DAC_channel'] =         self.adwin.get_dac_channels()['matisse_aom']
        self.par['A_laser_DAC_channel'] =          self.adwin.get_dac_channels()['newfocus_aom']

        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)
        self.ins_green_aom.set_cur_controller('ADWIN')
        self.ins_E_aom.set_cur_controller('ADWIN')
        self.ins_A_aom.set_cur_controller('ADWIN')
        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)



    def start_measurement(self,generate_sequence,pulse_dict,lt1=False,ssro_dict={},):
        # Prepare MW source and counters
        print 'Setting MW freq to '
        print (self.f_drive*1e-9)

        self.microwaves.set_iq('on')
        self.microwaves.set_frequency(self.f_drive)
        self.microwaves.set_pulm('on')
        self.microwaves.set_power(self.mwpower)
        self.counters.set_is_running(False)
        
        #Generate sequence and send to AWG
        sequence = generate_sequence(self.par['sweep_par'],pulse_dict,lt1)

        self.par['RO_repetitions'] =               int(len(self.par['sweep_par'])*self.par['reps_per_datapoint'])
        self.par['sweep_length'] =                 int(len(self.par['sweep_par']))
        self.par['sequence_wait_time'] =           int(np.ceil(sequence["max_seq_time"]/1e3)+2)
        
        self.par['min_sweep_par'] =                self.par['sweep_par'].min()
        self.par['max_sweep_par'] =                self.par['sweep_par'].max()
        
        self.awg.set_runmode('SEQ')
        self.awg.start()  
        while self.awg.get_state() != 'Waiting for trigger':
            qt.msleep(1)

        self.microwaves.set_status('on')
        qt.msleep(1)

        self.spin_control(lt1,ssro_dict=ssro_dict)
        self.end_measurement()


    def spin_control(self,lt1,ssro_dict={}):
        self.par['green_repump_voltage'] = self.ins_green_aom.power_to_voltage(self.par['green_repump_amplitude'])
        self.par['green_off_voltage'] = 0.01#self.ins_green_aom.power_to_voltage(self.par['green_off_amplitude'])
        self.par['Ex_CR_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_CR_amplitude'])
        self.par['A_CR_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_CR_amplitude'])
        self.par['Ex_SP_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_SP_amplitude'])
        self.par['A_SP_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_SP_amplitude'])
        self.par['Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_RO_amplitude'])
        self.par['A_RO_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_RO_amplitude'])

        if  (self.par['SP_duration'] > self.max_SP_bins) or \
            (self.par['sweep_length']*self.par['RO_duration'] > self.max_RO_dim):
                print ('Error: maximum dimensions exceeded')
                return(-1)

        #print 'SP E amplitude: %s'%self.par['Ex_SP_voltage']
        #print 'SP A amplitude: %s'%self.par['A_SP_voltage']

        if not(lt1):
            self.adwin.set_spincontrol_var(set_phase_locking_on = self.set_phase_locking_on)
            self.adwin.set_spincontrol_var(set_gate_good_phase =  self.set_gate_good_phase)

        self.adwin.start_spincontrol(
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
            RO_repetitions = self.par['RO_repetitions'],
            RO_duration = self.par['RO_duration'],
            sweep_length = self.par['sweep_length'],
            cycle_duration = self.par['cycle_duration'],
            green_repump_voltage = self.par['green_repump_voltage'],
            green_off_voltage = self.par['green_off_voltage'],
            Ex_CR_voltage = self.par['Ex_CR_voltage'],
            A_CR_voltage = self.par['A_CR_voltage'],
            Ex_SP_voltage = self.par['Ex_SP_voltage'],
            A_SP_voltage = self.par['A_SP_voltage'],
            Ex_RO_voltage = self.par['Ex_RO_voltage'],
            A_RO_voltage = self.par['A_RO_voltage'])

        if lt1:
            self.adwin_lt2.start_check_trigger_from_lt1()
            

        CR_counts = 0
        while (self.physical_adwin.Process_Status(9) == 1):
            reps_completed = self.physical_adwin.Get_Par(73)
            CR_counts = self.physical_adwin.Get_Par(70) - CR_counts
            cts = self.physical_adwin.Get_Par(26)
            trh = self.physical_adwin.Get_Par(25)
            print('completed %s / %s readout repetitions, %s CR counts/s'%(reps_completed,self.par['RO_repetitions'], CR_counts))
            print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                break

            qt.msleep(2.5)
        self.physical_adwin.Stop_Process(9)
        
        if lt1:
            self.adwin_lt2.stop_check_trigger_from_lt1()

        reps_completed  = self.physical_adwin.Get_Par(73)
        print('completed %s / %s readout repetitions'%(reps_completed,self.par['RO_repetitions']))

        sweep_length = self.par['sweep_length']
        par_long   = self.physical_adwin.Get_Data_Long(20,1,25)
        par_float  = self.physical_adwin.Get_Data_Float(20,1,10)
        CR_before = self.physical_adwin.Get_Data_Long(22,1,1)
        CR_after  = self.physical_adwin.Get_Data_Long(23,1,1)
        SP_hist   = self.physical_adwin.Get_Data_Long(24,1,self.par['SP_duration'])
        RO_data   = self.physical_adwin.Get_Data_Long(25,1,
                        sweep_length * self.par['RO_duration'])
        RO_data = np.reshape(RO_data,(sweep_length,self.par['RO_duration']))
        SSRO_data   = self.physical_adwin.Get_Data_Long(27,1,
                        sweep_length * self.par['RO_duration'])
        SSRO_data = np.reshape(SSRO_data,(sweep_length,self.par['RO_duration']))
        statistics = self.physical_adwin.Get_Data_Long(26,1,10)

        sweep_index = np.arange(sweep_length)
        sp_time = np.arange(self.par['SP_duration'])*self.par['cycle_duration']*3.333
        ro_time = np.arange(self.par['RO_duration'])*self.par['cycle_duration']*3.333

    
        self.save()
        savdat={}
        savdat['counts']=CR_after
        self.save_dataset(name='ChargeRO_after', do_plot=False, 
            data = savdat, idx_increment = False)
        savdat={}
        savdat['time']=sp_time
        savdat['counts']=SP_hist
        self.save_dataset(name='SP_histogram', do_plot=False, 
            data = savdat, idx_increment = False)
        savdat={}
        savdat['time']=ro_time
        savdat['sweep_axis']=sweep_index
        savdat['counts']=RO_data
        savdat['SSRO_counts']=SSRO_data
        self.save_dataset(name='Spin_RO', do_plot=False, 
            data = savdat, idx_increment = False)
        savdat={}
        savdat['par_long']=par_long
        savdat['par_float']=par_float
        self.save_dataset(name='parameters', do_plot=False, 
            data = savdat, idx_increment = False)
        
        ######################
        ###statistics file####
        ######################
        savdat={}
        savdat['completed_repetitions']=(reps_completed/sweep_length)
        savdat['total_repumps']=statistics[0]
        savdat['total_repump_counts']=statistics[1]
        savdat['noof_failed_CR_checks']=statistics[2]
        savdat['mw_center_freq']=self.f_drive
        savdat['mw_drive_freq']=self.f_drive
        savdat['mw_power']=self.mwpower
        savdat['min_pulse_nr']=self.par['min_sweep_par']
        savdat['max_pulse_nr']=self.par['max_sweep_par']
        savdat['min_pulse_amp']=self.par['min_sweep_par']
        savdat['max_pulse_amp']=self.par['max_sweep_par']
        savdat['min_time'] = self.par['min_sweep_par']
        savdat['max_time'] = self.par['max_sweep_par']
        savdat['min_sweep_par']=self.par['min_sweep_par']
        savdat['max_sweep_par']=self.par['max_sweep_par']
        savdat['sweep_par_name'] = self.par['sweep_par_name']
        savdat['sweep_par'] = self.par['sweep_par']
        savdat['noof_datapoints'] = self.par['sweep_length']
        savdat['fe_max'] = self.par['fe_max']
        savdat['fe_min'] = self.par['fe_min']
        
        self.save_dataset(name='statics_and_parameters', do_plot=False, 
            data = savdat, idx_increment = True)
       
        self.save_dataset(name='SSRO_calibration', do_plot=False, 
            data = ssro_dict, idx_increment = True)
        return 

    def end_measurement(self):
        self.awg.stop()
        self.awg.set_runmode('CONT')
        self.adwin.set_simple_counting()
        self.counters.set_is_running(True)
        self.ins_green_aom.set_power(200e-6)   
        self.microwaves.set_status('off')
        self.microwaves.set_iq('off')
        self.microwaves.set_pulm('off')
        self.ins_E_aom.set_power(0)
        self.ins_A_aom.set_power(0)



    def power_and_mw_ok(self):
        ret = True
        max_E_power = self.ins_E_aom.get_cal_a()
        max_A_power = self.ins_A_aom.get_cal_a()
        if (max_E_power < self.par['Ex_CR_amplitude']) or \
                (max_E_power < self.par['Ex_SP_amplitude']) or \
                (max_E_power < self.par['Ex_RO_amplitude']):
            print 'Trying to set too large value for E laser, quiting!'
            ret = False    
        if (max_A_power < self.par['A_CR_amplitude']) or \
                (max_A_power < self.par['A_SP_amplitude']) or \
                (max_A_power < self.par['A_RO_amplitude']):
            print 'Trying to set too large value for A laser, quiting'
            ret = False
        if self.mwpower > 0:
            print 'MW power > 0 dBm, are you sure you want to continue? Press q to quit, c to continue.'
            idx = 0
            max_idx = 5
            kb_hit = None
            while (idx<max_idx) and kb_hit == None:
                kb_hit = msvcrt.getch()
                if kb_hit == 'q':
                    ret = False
                if kb_hit == 'c':
                    ret = True
                qt.msleep(1)
                idx += 1
           
        return ret


def get_datapath():
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    return datapath

def Cal_CORPSE_pulse(m,nr_of_pulses,p_dict,lt1,ssro_dict):        
    p_dict['nr_of_pulses'] = nr_of_pulses
    m.par['sweep_par_name'] = 'Amplitude of %d Pi CORPSE pulses' % nr_of_pulses 
    m.start_measurement(cal.DSC_pulse_amp,p_dict,lt1=lt1,ssro_dict=ssro_dict)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    fit_dict = lde_calibration.rabi_calibration(path,new_fig=True,close_fig=True)

    return fit_dict

def XY8(self,m,name,lt1):
    datafolder= 'D:/measuring/data/'
    date = time.strftime('%Y') + time.strftime('%m') + time.strftime('%d')
    datapath = datafolder+date + '/'
    nr_of_datapoints = 11
    #min_tau =  0.010e3
    #max_tau =  164.503e3
    min_tau=55e3
    max_tau=65e3
    tau = np.linspace(min_tau,max_tau,nr_of_datapoints)
    
    pulse_dict = {
            "Pi":{"duration": 58., "amplitude": 0.4845},
                "Pi_2":   {"duration": 29., "amplitude": 0.7},
                "init_state_pulse": {"duration":29. , "amplitude":0.7,  
                                "Do_Pulse": False},
                "time_between_pulses": 10.,
                "nr_of_XY8_cycles": 1.,
                "duty_cycle_time": 100.,                             
                }

    par['sweep_par_name'] = 'Pi Pulse amp'
    par['nr_of_pulses']=8*pulse_dict['nr_of_XY8_cycles']
    pulse_dict["duty_cycle_time"] = 100
    start_measurement(dec.XY8_cycles,tau,pulse_dict,name='Cal_5_Pi_amp')

def XY8_rep_el(nr_of_datapoints,RO_dur=47,Ex_p=9e-9,MW_freq=2.8289e9,lt1=False,ssro_dict={}):
    datafolder= 'D:/measuring/data/'
    date = time.strftime('%Y') + time.strftime('%m') + time.strftime('%d')
    datapath = datafolder+date + '/'
    
    name = 'XY8'
    m = Decoupling(name)
    m.setup(lt1)

    pulse_dict = {
            "Pi":{"duration": 50., "amplitude": 0.578},
                "init_state_pulse": {"duration":25. , "amplitude":0.54},  
                "time_between_pulses": 10.,
                "nr_of_XY8_cycles": 1.,
                "duty_cycle_time": 100.,  
                "tau_el_length":tau_el_len,
                "rep_elements":True,
                }

    # Determine tau
    tau_el_len = .525e4
    tau_el_len_us = tau_el_len*1e3
    tau_rep_min=0     # maxtau in units of tau_len
    tau_rep_max=200     # maxtau in units of tau_len
    tau_rep = np.linspace(tau_rep_min,tau_rep_max,nr_of_datapoints)
    tau_rep[0]=1
        
    m.par['sweep_par'] = tau_rep
    m.par['sweep_length'] = len(tau_rep)
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    m.f_drive=MW_freq
        
    p_dict['nr_of_pulses'] = nr_of_pulses
    fe_min = pulse_dict['nr_of_XY8_cycles']*16*tau_el_len*tau_rep[0]
    fe_max = pulse_dict['nr_of_XY8_cycles']*16*tau_rep_max*tau_el_len
    print fe_min
    print fe_max
    m.par['fe_max'] = fe_max
    m.par['fe_min'] = fe_min
    m.par['sweep_par_name'] = 'Free evolution time'
    m.par['nr_of_pulses']=8*pulse_dict['nr_of_XY8_cycles']
    pulse_dict["duty_cycle_time"] = 100
    
    m.start_measurement(dec.XY8_cycles_multiple_elements,pulse_dict,lt1=lt1,ssro_dict=ssro_dict)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    lde_calibration.plot_data(path,new_fig=True,close_fig=True)    
    
    #min_tau =  0.010e3
    #max_tau =  164.503e3
    
    
  
    
if __name__ == '__main__':
    XY8_rep_el()



