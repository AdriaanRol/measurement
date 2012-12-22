#This measurement allows one to read out the spin after turning the spin using 
#self.microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
import ctypes
import inspect
import time as dtime
import msvcrt
from measurement import Measurement
from AWG_HW_sequencer_v2 import Sequence
import PQ_measurement_generator_v2 as pqm
import ssro_ADwin_class as ssro_ADwin
import esr
from config import awgchannels_lt2 as awgcfg
from sequence import common as commonseq
from sequence import mwseq_calibration as cal
from analysis import lde_calibration, spin_control 





awg = qt.instruments['AWG']
temp = qt.instruments['temperature_lt1']



class PulseCalibration(Measurement):

    def __init__(self,name):
        Measurement.__init__(self,name,mclass='Pulse_Cal')
    ###########################################################
##
##  hardcoded in ADwin program (adjust there if necessary!)
##

        self.max_SP_bins = 500
        self.max_RO_dim = 1000000

##
###########################################################
    def setup(self,lt1=False):
        mwpower_lt1 =               20               #in dBm
        mwpower_lt2 =               20              #in dBm

        if lt1:
            self.ins_green_aom=qt.instruments['GreenAOM_lt1']
            self.ins_E_aom=qt.instruments['MatisseAOM_lt1']
            self.ins_A_aom=qt.instruments['NewfocusAOM_lt1']
            self.adwin=qt.instruments['adwin_lt1']
            self.counters=qt.instruments['counters_lt1']
            self.physical_adwin=qt.instruments['physical_adwin_lt1']
            self.microwaves = qt.instruments['SMB100_lt1']
            self.ctr_channel=2
            mwpower = mwpower_lt1
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
            mwpower = mwpower_lt2
            self.microwaves.set_status('off')

        self.set_phase_locking_on = 0
        self.set_gate_good_phase = -1

        self.mwpower=mwpower
        self.nr_of_datapoints = 21
        self.repetitions_per_datapoint = 1000
        self.max_seq_time = 1
        self.par = {}
        self.par['counter_channel'] =              self.ctr_channel
        self.par['green_laser_DAC_channel'] =      self.adwin.get_dac_channels()['green_aom']
        self.par['Ex_laser_DAC_channel'] =         self.adwin.get_dac_channels()['matisse_aom']
        self.par['A_laser_DAC_channel'] =          self.adwin.get_dac_channels()['newfocus_aom']
        self.par['AWG_start_DO_channel'] =         1
        self.par['AWG_done_DI_channel'] =          8
        self.par['send_AWG_start'] =               1
        self.par['wait_for_AWG_done'] =            0
        self.par['green_repump_duration'] =        10
        self.par['CR_duration'] =                  60
        self.par['SP_duration'] =                  50
        self.par['SP_filter_duration'] =           0
        self.par['sequence_wait_time'] =           int(np.ceil(self.max_seq_time/1e3)+2)
        self.par['wait_after_pulse_duration'] =    1
        self.par['CR_preselect'] =                 1000
        self.par['RO_repetitions'] =               int(self.nr_of_datapoints*self.repetitions_per_datapoint)
        self.par['RO_duration'] =                  22
        self.par['sweep_length'] =                 int(self.nr_of_datapoints)
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
        self.f_drive            =                   2.82878e9
        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)
        self.ins_green_aom.set_cur_controller('ADWIN')
        self.ins_E_aom.set_cur_controller('ADWIN')
        self.ins_A_aom.set_cur_controller('ADWIN')
        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)



    def start_measurement(self,m,generate_sequence,sweep_param,pulse_dict,lt1=False,ssro_dict={},name=''):
        self.microwaves.set_iq('on')
        print 'Setting MW freq to '
        print (self.f_drive*1e-9)

        self.microwaves.set_frequency(self.f_drive)
        self.microwaves.set_pulm('on')
        self.microwaves.set_power(self.mwpower)
        self.counters.set_is_running(False)
        sequence = generate_sequence(sweep_param,pulse_dict,lt1)
        self.par['RO_repetitions'] =               int(self.nr_of_datapoints*self.repetitions_per_datapoint)
        self.par['sweep_length'] =                 int(self.nr_of_datapoints)
        self.par['sequence_wait_time'] =           int(np.ceil(sequence["max_seq_time"]/1e3)+2)
        
        self.par['min_sweep_par'] =                  sweep_param.min()
        self.par['max_sweep_par'] =                  sweep_param.max()
        
        awg.set_runmode('SEQ')
        awg.start()  
        while awg.get_state() != 'Waiting for trigger':
            qt.msleep(1)
        #data = meas.Measurement(sequence["seqname"],name)
        self.microwaves.set_status('on')
        self.spin_control(name,m,lt1,ssro_dict=ssro_dict)
        self.end_measurement()


    def spin_control(self,name, data,lt1,ssro_dict={}):
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
        savdat['noof_datapoints']=self.nr_of_datapoints
        
        data.save_dataset(name='statics_and_parameters', do_plot=False, 
            data = savdat, idx_increment = True)
       
        data.save_dataset(name='SSRO_calibration', do_plot=False, 
            data = ssro_dict, idx_increment = True)
        return 

    def end_measurement(self):
        awg.stop()
        awg.set_runmode('CONT')
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
    def SE_cal_tau2(self,m,name,lt1,ssro_dict={}):
        datafolder= 'D:/measuring/data/'
        date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
        datapath = datafolder+date + '/'
        
        pulse_dict = {
                "Pi":{"duration": 58., "amplitude":0.4845},
                    "Pi_2":   {"duration": 29., "amplitude": 0.7},
                    "nr_of_pulses": 1.,
                    "duty_cycle_time": 100.,
                    "time_between_CORPSE":10.,
                    "tau1": 272.,
                    "CORPSE":{"pi":0.4857,"pi_over_two":0.46466}
                    }
        if lt1:
            pulse_dict["CORPSE"]["pi"] = 0.595
            pulse_dict["CORPSE"]["pi_over_two"] = 0.535
        
        
        taumin= 12.
        taumax = 1532.
        tau=np.linspace(taumin,taumax,self.nr_of_datapoints)
        
        SE_cal=PulseCalibration(name='SE_sweep_tau2')
        self.start_measurement(SE_cal,cal.SE_DSC,tau,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='Single_Pi_amp')

    def SE_cal_phase(self,m,name,lt1):
        datafolder= 'D:/measuring/data/'
        date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
        datapath = datafolder+date + '/'
        
        pulse_dict = {
                "Pi":{"duration": 58., "amplitude":0.4845},
                    "Pi_2":   {"duration": 29., "amplitude": 0.7},
                    "nr_of_pulses": 1.,
                    "duty_cycle_time": 100.,
                    "time_between_CORPSE":10.,
                    "tau": 272.,
                    "CORPSE":{"pi":0.48,"pi_over_two":0.45}
                    }
        if lt1:
            pulse_dict["CORPSE"]["pi"] = 0.598
            pulse_dict["CORPSE"]["pi_over_two"] = 0.51
        
        
        phasemin= 0.
        phasemax = 360.
        phase=np.linspace(phasemin,phasemax,self.nr_of_datapoints)
        
        SE_cal=PulseCalibration(name='SE_sweep_phase')
        self.start_measurement(SE_cal,cal.SE_DSC_phase,phase,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='Single_Pi_amp')

    def SE_cal_pi_over_two_amp(self,m,name,lt1,ssro_dict={}):
        datafolder= 'D:/measuring/data/'
        date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
        datapath = datafolder+date + '/'
        
        pulse_dict = {
                "Pi":{"duration": 58., "amplitude":0.4845},
                    "Pi_2":   {"duration": 29., "amplitude": 0.7},
                    "nr_of_pulses": 1.,
                    "duty_cycle_time": 100.,
                    "time_between_CORPSE":20.,
                    "tau": 20.,
                    "CORPSE":{"pi":0.48,"pi_over_two":0.45}
                    }
        if lt1: 
            pulse_dict["CORPSE"]["pi"] = 0.59
            pulse_dict["CORPSE"]["pi_over_two"] = 0.5387
        
        SE_cal=PulseCalibration(name='SE_sweep_amp')
        SE_cal.nr_of_datapoints = 42
        SE_cal.repetitions_per_datapoint = 2500
        self.nr_of_datapoints = SE_cal.nr_of_datapoints
        ampmin= 0.4
        ampmax = 0.6
        amp_temp=np.linspace(ampmin,ampmax,SE_cal.nr_of_datapoints/2)
        amp=[]
        for i in amp_temp:
            amp.append(i)
            amp.append(i)

        
        self.start_measurement(SE_cal,cal.SE_DSC_check_sweep_first_pi_over_two,np.array(amp),pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='SE_cal_pi_over_two')
    
    def Calibrate_pi(self,m,name,lt1,ssro_dict={}):
        datafolder= 'D:/measuring/data/'
        date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
        datapath = datafolder+date + '/'
        
        
        min_pulse_amp =             0.0
        max_pulse_amp =             0.85
        #if lt1:
        #    max_pulse_amp = 0.65
        amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        
        pulse_dict = {
                "Pi":{"duration": 50., "amplitude":0.58},
                    "init_state_pulse": {"duration":29. , "amplitude":0.7,  
                                    "Do_Pulse": False},
                    "time_between_pulses": 10.,
                    "nr_of_pulses": 1.,
                    "duty_cycle_time": 100.,
                    
                    }
        if lt1:
            pulse_dict["Pi"]["duration"] = 56.
        ### Calibrate Single pi pulse
        single_pi = PulseCalibration(name='Single_Pi_amp')
        self.start_measurement(single_pi,cal.Pi_Pulse_amp,amplitude,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='Single_Pi_amp')
        self.par['sweep_par_name'] = 'Pi Pulse amp'
        path = lde_calibration.find_newest_data(datapath,string='Single_Pi_amp')
        rabi_dict = lde_calibration.rabi_calibration(path,close_fig=True)
        fit_amp = rabi_dict["minimum"]
        ms0_readout = rabi_dict["Amplitude"] + rabi_dict["offset"]
        ms1_readout=50.
        
        
        ##### For Calibration of 5 Pi pulses
        pulse_dict["nr_of_pulses"] = 5
        pulse_dict["duty_cycle_time"] = 500
        min_pulse_amp=fit_amp-0.1
        max_pulse_amp=fit_amp+0.1
        if lt1:
            min_pulse_amp=fit_amp-0.3
            max_pulse_amp=fit_amp+0.1
        amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        Five_pi = PulseCalibration(name='5_Pi_amp')
        self.start_measurement(Five_pi,cal.Pi_Pulse_amp,amplitude,pulse_dict,lt1=lt1,name='5_Pi_amp')
        path = lde_calibration.find_newest_data(datapath,string='5_Pi_amp')
        fit_amp = lde_calibration.rabi_calibration(path,new_fig=True,close_fig=True)
        fit_amp=fit_amp["minimum"]
        Cal_dict={}
        Cal_dict["Pi"] = fit_amp
        
        ##### For Calibration of 8 Pi pulses
        #pulse_dict["nr_of_pulses"] = 8
        #pulse_dict["duty_cycle_time"] = 500
        #min_pulse_amp=fit_amp-0.1
        #max_pulse_amp=fit_amp+0.1
        #amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        #Five_pi = PulseCalibration(name='8_Pi_amp')
        #self.start_measurement(Five_pi,cal.Pi_Pulse_amp,amplitude,pulse_dict,lt1=lt1,name='8_Pi_amp')
        #path = lde_calibration.find_newest_data(datapath,string='8_Pi_amp')
        #fit_amp = lde_calibration.rabi_calibration(path,new_fig=True,close_fig=True)
        #fit_amp=fit_amp["minimum"]
        
        ### Cal CORPSE Pi/2
        pulse_dict['nr_of_pulses']=1.
        pulse_dict["Pi"]["duration"] = 25.
        if lt1:
            pulse_dict["Pi"]["duration"] = 28.
        min_pulse_amp=fit_amp-0.1
        max_pulse_amp=fit_amp+0.1
        if lt1:
            min_pulse_amp = fit_amp - 0.12
            max_pulse_amp = fit_amp + 0.1
        amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        pi_over_two = PulseCalibration(name='_pi_over_two')
        self.start_measurement(pi_over_two,cal.Pi_Pulse_amp,
                amplitude,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='pi_over_two')

        path = lde_calibration.find_newest_data(datapath,string='pi_over_two')
        b= 2*np.pi*rabi_dict["Amplitude"]*rabi_dict["freq"]
        a = rabi_dict["offset"]+rabi_dict["Amplitude"]
        pi_over_two_dict = lde_calibration.pi_over_two_calibration(path,[ms0_readout,ms1_readout],[a,b],new_fig=True,close_fig=True)
        Cal_dict["Pi2"] = pi_over_two_dict 

        return Cal_dict

    def Calibrate(self,m,name,lt1):
        datafolder= 'D:/measuring/data/'
        date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
        datapath = datafolder+date + '/'
        
        
        min_pulse_amp =             0.0
        max_pulse_amp =             0.85
        #if lt1:
        #    max_pulse_amp = 0.65
        amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        
        pulse_dict = {
                "Pi":{"duration": 58., "amplitude":0.4845},
                    "Pi_2":   {"duration": 29., "amplitude": 0.7},
                    "init_state_pulse": {"duration":29. , "amplitude":0.7,  
                                    "Do_Pulse": False},
                    "time_between_pulses": 10.,
                    "nr_of_pulses": 1.,
                    "duty_cycle_time": 100.,
                    "time_between_CORPSE":20.,
                    
                    }

        ### Calibrate SSRO
        #name='SIL9_LT2'
        #m = ssro_ADwin(name)
        #par=m.setup()
        #m.measure(m,name,par)
        
        #ssro_ADwin.ssro_ADwin_Cal(lt1=lt1)
        
        path = lde_calibration.find_newest_data(datapath,string='ADwin_SSRO')
        ssro_dict=lde_calibration.ssro_calibration(path)
        #self.par['RO_duration'] = int(round(ssro_dict["t_max"]))
        
        ### Calibrate ESR freq
        #esr.measure_esr(lt1=lt1)
        path = lde_calibration.find_newest_data(datapath,string='ESR')
        f_fit=lde_calibration.esr_calibration(path)
        if lt1:
            f_fit=2.82878e9 # WE measured this more accurate
        else:
            f_fit=2.82877e9-0.418e6
        self.f_drive=f_fit

        self.microwaves.set_frequency(self.f_drive)
        
        #plt=qt.Plot2D(name='MWCal',clear=True)

        ### Calibrate Single pi pulse
        single_pi = PulseCalibration(name='Single_Pi_amp')
        #self.start_measurement(single_pi,cal.Pi_Pulse_amp,amplitude,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='Single_Pi_amp')
        self.par['sweep_par_name'] = 'Pi Pulse amp'
        path = lde_calibration.find_newest_data(datapath,string='Single_Pi_amp')
        rabi_dict = lde_calibration.rabi_calibration(path,close_fig=True)
        fit_amp = rabi_dict["minimum"]
        ms0_readout = rabi_dict["Amplitude"] + rabi_dict["offset"]
            
                
        ### Cal 1 CORPSE Pulse
        min_pulse_amp=fit_amp-0.15
        max_pulse_amp=fit_amp+0.15
        #if lt1:
        #    min_pulse_amp = fit_amp-0.25
        #    max_pulse_amp = fit_amp+0.05
        amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        pulse_dict["istate_pulse"] = {"duration":0,"amplitude":0,"Do_Pulse":False}
        pulse_dict["time_between_CORPSE"] = 10.
        pulse_dict["nr_of_pulses"] = 1.
        CORPSE = PulseCalibration(name='CORPSE_amp')
        #self.start_measurement(CORPSE,cal.DSC_pulse_amp,amplitude,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='CORPSE_amp')
        path = lde_calibration.find_newest_data(datapath,string='CORPSE_amp')
        CORPSE_dict = lde_calibration.rabi_calibration(path,new_fig=True,close_fig=True)
        ms1_readout = CORPSE_dict["lowest_meas_value"]


        ### Cal 5 Corpse pulses
        fit_amp=CORPSE_dict["minimum"]
        min_pulse_amp=fit_amp-0.1
        max_pulse_amp=fit_amp+0.1
        amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        Five_CORPSE = PulseCalibration(name='Five_CORPSE_amp')
        pulse_dict['nr_of_pulses'] = 5.
        #self.start_measurement(Five_CORPSE,cal.DSC_pulse_amp,amplitude,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='Five_CORPSE_amp')
        path = lde_calibration.find_newest_data(datapath,string='Five_CORPSE_amp')
        Five_CORPSE_dict = lde_calibration.rabi_calibration(path,new_fig=True,close_fig=True)
        fit_amp=Five_CORPSE_dict["minimum"]
 
        ### Cal CORPSE Pi/2
        pulse_dict['nr_of_pulses']=1.
        min_pulse_amp=fit_amp-0.1
        max_pulse_amp=fit_amp+0.1
        if lt1:
            min_pulse_amp = fit_amp - 0.12
            max_pulse_amp = fit_amp + 0.1
        amplitude = np.linspace(min_pulse_amp,max_pulse_amp,self.nr_of_datapoints)
        CORPSE_pi_over_two = PulseCalibration(name='CORPSE_pi_over_two')
        #self.start_measurement(CORPSE_pi_over_two,cal.DSC_pi_over_two_pulse_amp,
       #         amplitude,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,name='CORPSE_pi_over_two')

        path = lde_calibration.find_newest_data(datapath,string='CORPSE_pi_over_two')
        b= 2*np.pi*rabi_dict["Amplitude"]*rabi_dict["freq"]
        a = rabi_dict["offset"]+rabi_dict["Amplitude"]
       
        pi_over_two_dict = lde_calibration.pi_over_two_calibration(path,[ms0_readout,ms1_readout],[a,b],new_fig=True,close_fig=True)        ### Cal CORPSE Pi/2
        
        print 'ms0_readout:'
        print ms0_readout
        print 'ms1_readout:'
        print ms1_readout


        Cal_dict={"SSRO":ssro_dict,
                          "ESR":{"freq":f_fit},
                          "MW":rabi_dict,
                          "MW_CORPSE":CORPSE_dict,
                          "MW_Five_CORPSE": Five_CORPSE_dict ,
                          "MW_CORPSE_pi_over_two":pi_over_two_dict
                          }

        return Cal_dict

def cal_all(lt1=False):
    name='Calibrate_pulses'
    calibrate = PulseCalibration(name)
    calibrate.setup(lt1)
    cal_dict=calibrate.Calibrate(calibrate,name,lt1)
    return cal_dict

def cal_pi(lt1=False):
    name='Calibrate_pi'
    calibrate = PulseCalibration(name)
    calibrate.setup(lt1)
    calibrate.f_drive    =  2.8289e9
    cal_dict=calibrate.Calibrate_pi(calibrate,name,lt1)
    return cal_dict

def cal_SE(lt1=False,ssro_dict={}):
    name='Calibrate_SE'
    calibrate = PulseCalibration(name)
    calibrate.setup(lt1)
    calibrate.f_drive    =  2.82877e9
    if lt1:
        calibrate.f_drive    =  2.82835e9 + 557.e3
    calibrate.nr_of_datapoints = 41
    calibrate.repetitions_per_datapoint = 2500
    cal_dict=calibrate.SE_cal_tau2(calibrate,name,lt1,ssro_dict)
    return cal_dict

def cal_SE_phase(lt1=False):
    name='Calibrate_SE_phase'
    calibrate = PulseCalibration(name)
    calibrate.setup(lt1)
    calibrate.nr_of_datapoints = 21
    cal_dict=calibrate.SE_cal_phase(calibrate,name,lt1)
    return cal_dict

def cal_SE_sweep_pi_over_two_amp(lt1=False,ssro_dict={}):
    name='Calibrate_SE_pi_over_two'
    calibrate = PulseCalibration(name)
    calibrate.setup(lt1)
    calibrate.nr_of_datapoints = 21
    calibrate.repetitions_per_datapoint = 2500
    cal_dict=calibrate.SE_cal_pi_over_two_amp(calibrate,name,lt1,ssro_dict=ssro_dict)
    return cal_dict


