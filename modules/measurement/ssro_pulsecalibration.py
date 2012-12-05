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
from .measurement import Measurement
from AWG_HW_sequencer_v2 import Sequence
import PQ_measurement_generator_v2 as pqm
import ssro_ADwin_class as ssro_ADwin
import esr
from config import awgchannels_lt2 as awgcfg
from sequence import common as commonseq
from sequence import mwseq_calibration as cal
from analysis import lde_calibration, spin_control 



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

        
        self.set_phase_locking_on = 1
        self.set_gate_good_phase = -1

        self.f_drive            =                   2.828e9

        self.par = {}
        
        self.par['AWG_start_DO_channel'] =         1
        self.par['AWG_done_DI_channel'] =          8
        self.par['send_AWG_start'] =               1
        self.par['wait_for_AWG_done'] =            0
        self.par['green_repump_duration'] =        12
        self.par['CR_duration'] =                  250 # NOTE set to 60 for Ey, A1
        self.par['SP_duration'] =                  350 
        self.par['SP_filter_duration'] =           0
        self.par['sequence_wait_time'] =           int(np.ceil(1e-3)+2)
        self.par['wait_after_pulse_duration'] =    1
        self.par['CR_preselect'] =                 1000

        self.par['reps_per_datapoint'] =           1500
        self.par['sweep_length'] =                 int(21)
        self.par['RO_repetitions'] =               int(21*1500)
        self.par['RO_duration'] =                  17

        self.par['cycle_duration'] =               300
        self.par['CR_probe'] =                     100

        self.par['green_repump_amplitude'] =       160e-6
        self.par['green_off_amplitude'] =          0e-6
        self.par['Ex_CR_amplitude'] =              10e-9 #OK
        self.par['A_CR_amplitude'] =               13e-9 #NOTE set to 15 for A1
        self.par['Ex_SP_amplitude'] =              0#15e-9 
        self.par['A_SP_amplitude'] =               15e-9 #OK: PREPARE IN MS = 0
        self.par['Ex_RO_amplitude'] =              9e-9 #OK: READOUT MS = 0
        self.par['A_RO_amplitude'] =               0e-9

        self.par['min_sweep_par'] =                  0
        self.par['max_sweep_par'] =                  1
        self.par['sweep_par_name'] =                 ''
        self.par['sweep_par']   =                  np.linspace(1,21,21)


    def setup(self,lt1=False,phase_locking=0):
        self.mwpower_lt1 =               20              #in dBm
        self.mwpower_lt2 =               20              #in dBm
        if phase_locking:
            self.set_phase_locking_on = 1
        else:
            self.set_phase_locking_on = 0
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

        if lt1:
            self.adwin_lt2.start_check_trigger_from_lt1(stop_processes=['counter'])
            qt.msleep(1)

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
            CR_probe = self.par['CR_probe'],
            green_repump_voltage = self.par['green_repump_voltage'],
            green_off_voltage = self.par['green_off_voltage'],
            Ex_CR_voltage = self.par['Ex_CR_voltage'],
            A_CR_voltage = self.par['A_CR_voltage'],
            Ex_SP_voltage = self.par['Ex_SP_voltage'],
            A_SP_voltage = self.par['A_SP_voltage'],
            Ex_RO_voltage = self.par['Ex_RO_voltage'],
            A_RO_voltage = self.par['A_RO_voltage'])


            

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
        self.ins_green_aom.set_power(100e-6)   
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

#FIXME: should be external function
#Calibrate will be deleted from this scrips soon!

    
### Usefull functions that use the class



def Cal_regular_pi_pulse(m,nr_of_pulses,p_dict,lt1,ssro_dict):

    m.par['sweep_par_name'] = 'Amplitude of %d Pi pulses' % nr_of_pulses 
    p_dict['nr_of_pulses'] = nr_of_pulses
    m.start_measurement(cal.Pi_Pulse_amp,p_dict,lt1=lt1,ssro_dict=ssro_dict)
    
    
    dp=get_datapath()
    name=m.name
    path = lde_calibration.find_newest_data(dp,string=name)
    fit_dict = lde_calibration.rabi_calibration(path,close_fig=True)
    
    return fit_dict
    
def Cal_regular_pitwo_pulse(m,p_dict,readout,fit_guess,lt1,ssro_dict):
    
    p_dict['nr_of_pulses']=1.
    m.par['sweep_par_name'] = 'Amplitude of Pi/2'
    m.start_measurement(cal.Pi_Pulse_amp,p_dict,lt1=lt1,ssro_dict=ssro_dict)
    
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    fit_dict = lde_calibration.pi_over_two_calibration(path,readout,fit_guess,new_fig=True,close_fig=True)

    return fit_dict

def Cal_CORPSE_pulse(m,nr_of_pulses,p_dict,lt1,ssro_dict):        
    p_dict['nr_of_pulses'] = nr_of_pulses
    m.par['sweep_par_name'] = 'Amplitude of %d Pi CORPSE pulses' % nr_of_pulses 
    m.start_measurement(cal.DSC_pulse_amp,p_dict,lt1=lt1,ssro_dict=ssro_dict)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    fit_dict = lde_calibration.rabi_calibration(path,new_fig=True,close_fig=True)

    return fit_dict

   
def Cal_CORPSE_pitwo(m,p_dict,readout,fit_guess,lt1,ssro_dict):
    p_dict['nr_of_pulses']=1.
    m.par['sweep_par_name'] = 'Amplitude of Pi/2 CORPSE'
    m.start_measurement(cal.DSC_pi_over_two_pulse_amp,p_dict,lt1=lt1,ssro_dict=ssro_dict)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    fit_dict = lde_calibration.pi_over_two_calibration(path,readout,fit_guess,new_fig=True,close_fig=True)

    return fit_dict

def cal_SE(f_drive,piamp,pi2amp,RO_dur=20,Ex_p=6e-9,lt1=False,ssro_dict={}):
    name='Cal_SE_tau2'
    m = PulseCalibration(name)
    m.setup(lt1)
    m.par['sweep_length']=61.
    m.par['reps_per_datapoint'] = 2000.
    p_dict = {"Pi":{  "duration": 58., 
                      "amplitude":0.595
                          },

              "init_state_pulse": {"duration":0., 
                            "amplitude":0.,  
                            "Do_Pulse": False},

              "time_between_pulses": 10.,
              "time_between_CORPSE":10., 
              "duty_cycle_time": 100.,
              "tau1": 272.,
              "CORPSE":{"pi":piamp,"pi_over_two":pi2amp},
             }
    taumin= 20.
    taumax = 6020.
    nr_of_datapoints = m.par['sweep_length']
    tau=np.linspace(taumin,taumax,41)
    m.par['sweep_par'] = tau
    m.f_drive=f_drive
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    
    m.start_measurement(cal.SE_DSC,p_dict,lt1=lt1,ssro_dict=ssro_dict)
    
def cal_SE_regular(f_drive,piamp,pi2amp,RO_dur=20,Ex_p=6e-9,lt1=False,ssro_dict={},phase_locking=1):
    """
    Calibration function for a spin echo measurement with regular pulses. Arguments:
    *   f_drive: Frequency in Hz (ex: 2.828E9)
    *   piamp, pi2amp: Amplitude of the pi and pi/2 pulse obtained from pulse calibration
    *   RO_dur: SSRO duration for each datapoint in us (ex: 20)
    *   Ex_p: SSRO read-out power in W (ex: 12e-9)
    *   lt1: True or False 
    """
    name='Cal_SE_regular_tau2'
    m = PulseCalibration(name)
    m.setup(lt1)
    m.par['sweep_length']=41.
    m.par['reps_per_datapoint'] = 2000.
    p_dict = {"Pi":{  "duration": 50., 
                      "amplitude": piamp
                          },
              "Pi_over_2":{ "duration": 25.,
                  "amplitude": pi2amp},
              "tau1": 232.,
             "duty_cycle_time": 100.,
             }
    taumin= 15.
    taumax = 3070.
    nr_of_datapoints = m.par['sweep_length']
    tau=np.linspace(taumin,taumax,41)
    m.par['sweep_par'] = tau
    m.f_drive=f_drive
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    
    m.start_measurement(cal.SE_regular,p_dict,lt1=lt1,ssro_dict=ssro_dict,phase_locking=phase_locking)

    
    #name='Calibrate_SE'
    #calibrate = PulseCalibration(name)
    #calibrate.setup(lt1)
    #calibrate.f_drive    =  2.82877e9
    #if lt1:
    #    calibrate.f_drive    =  2.82835e9 + 557.e3
    #calibrate.nr_of_datapoints = 41
    #calibrate.repetitions_per_datapoint = 2500
    #cal_dict=calibrate.SE_cal_tau2(calibrate,name,lt1,ssro_dict)
    #return cal_dict

##Other usefull functions to calibrate
def get_datapath():
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    return datapath

def Cal_SSRO(filename,lt1):
    
    if filename:
        name = filename
    else:
        if lt1:
            name = 'LT1'
        else:
            name = 'LT2'
  
    ssro_ADwin.ssro_ADwin_Cal(lt1=lt1)
    
    dp = get_datapath()
    path = lde_calibration.find_newest_data(dp,string='ADwin_SSRO')
    ssro_dict=lde_calibration.ssro_calibration(path)
    
    return ssro_dict

def Cal_ESR(lt1):
    
    f_fit = esr.measure_esr(lt1=lt1)

    #dp = get_datapath()
    #path = lde_calibration.find_newest_data(dp,string='ESR')
    
    #f_fit=lde_calibration.esr_calibration(path) #FIXME f_dip needs to be an argument
    
    #if lt1:
    #    f_fit=2.82878e9 # WE measured this more accurate
    #else:
    #    f_fit=2.82877e9-0.418e6
    #self.f_drive=f_fit

    #self.microwaves.set_frequency(self.f_drive)
    
    return f_fit

#these are the functions you actually call:
def Cal_N_pi(pulse_amp,N_pulse,pulse_axis="x",RO_dur=48,Ex_p=11.5e-9,lt1=False,ESR=2.82891e9,SSRO=False,ssro_dict={}):
        p_dict = {
                    "Pi":{  "duration": 50., 
                            "amplitude":0.4845
                          },

                    "init_state_pulse": {"duration":0., 
                            "amplitude":0.,  
                            "Do_Pulse": False},

                    "time_between_pulses": 15.,

                    "duty_cycle_time": 5000.,
                    "pulse_axis": "x",
                     }
        
        if ESR:
            ESR_dict={}
            ESR_dict['freq'] = ESR
        else:    
            ESR_dict={}
            ESR_dict['freq'] = Cal_ESR(lt1)
        f_drive = ESR_dict['freq']
        name = str(N_pulse)+'_pi_pulses'
        m = PulseCalibration(name)
        m.setup(lt1)
        
        m.par['sweep_par'] = pulse_amp
        m.par['sweep_length'] = len(pulse_amp)
        m.par['RO_duration'] = RO_dur
        m.par['Ex_RO_amplitude'] = Ex_p
        m.f_drive=f_drive

        Pi_dict = Cal_regular_pi_pulse(m,N_pulse,p_dict,lt1,ssro_dict)
        print 'Pi-pulse amp:'
        print Pi_dict['minimum']
def Cal_all_regular(nr_of_datapoints,RO_dur=48,Ex_p=11.5e-9,lt1=True,ESR=None,
        SSRO=False,cal_five=True,cal_pi2=True, pi_duration=790,phase_locking=0):
    """
    Calibration function for regular pulses. Arguments:
    *   nr_of_datapoints: # of datapoints for each calibration measurement (ex: 21)
    *   RO_dur: SSRO duration for each datapoint in us (ex: 20)
    *   Ex_p: SSRO read-out power in W (ex: 12e-9)
    *   lt1: True or False 
    *   ESR: frequency of the microwaves. If not specified an ESR will be
        performed to find the frequency. Frequency in Hz (ex: 2.82E9)
    *   cal_five: True or False (for better calibration of the pi pulse)
    *   cal_pi2: True or False (for calibration of the pi/2 pulse)
    """

    p_dict = {
                "Pi":{  "duration": pi_duration,    # this will be the time of a pi pulse on which we calibrate!
                        "amplitude":0.4845
                      },

                "init_state_pulse": {"duration":0., 
                        "amplitude":0.,  
                        "Do_Pulse": False},

                "time_between_pulses": 15.,

                "duty_cycle_time": 5000.,
                "pulse_axis": "X",
                 }
    five_Pi_dict = {}
    pi2_dict = {}
    ## Calibrate SSRO
    p_dict["freq"]= 50E6
    p_dict["do_env"]= False
    p_dict["shape"]= 'rectangular'
    if SSRO:
        ssro_dict = Cal_SSRO(str(lt1),lt1)
    else:
        ssro_dict={}


    ## Calibrate ESR

    if ESR:
        ESR_dict={}
        ESR_dict['freq'] = ESR
    else:    
        ESR_dict={}
        ESR_dict['freq'] = Cal_ESR(lt1)
    
    f_drive=ESR_dict['freq']
    
    
    ##Calibrate single Pi pulse

    name = 'Cal_Single_Pi'
    m = PulseCalibration(name)
    m.setup(lt1,phase_locking=phase_locking)

    min_pulse_amp =             0
    max_pulse_amp =             0.8
    m.par['sweep_par'] = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
    m.par['sweep_length'] = nr_of_datapoints
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    m.f_drive=f_drive

    Pi_dict = Cal_regular_pi_pulse(m,1,p_dict,lt1,ssro_dict)
    ms0_readout = float(Pi_dict["highest_meas_value"])
    print 'highest_meas_value for pi2 cal', ms0_readout
    ms1_readout = 7.                                  # NOTE NOTE NOTE This is the ms=-1 readout value, important!!!!!!!!!!!!!!!
     ## Calibrate 5 Pi Pulses
    if cal_five:
        name = 'Cal_5_Pi'
        m = PulseCalibration(name)
        m.setup(lt1,phase_locking=phase_locking)

        nr_of_pulses= 5.
        fit_amp=Pi_dict["minimum"]
        min_pulse_amp=fit_amp-0.2
        max_pulse_amp=fit_amp+0.07
        
        m.par['sweep_par'] = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
        m.par['sweep_length'] = nr_of_datapoints
        m.par['RO_duration'] = RO_dur
        m.par['Ex_RO_amplitude'] = Ex_p
        m.f_drive=f_drive

        five_Pi_dict = Cal_regular_pi_pulse(m,nr_of_pulses,p_dict,lt1,ssro_dict)
    if cal_pi2:
        name = 'Cal_Pi2'
        m = PulseCalibration(name)
        m.setup(lt1,phase_locking=phase_locking)

        min_pulse_amp =fit_amp - 0.1
        max_pulse_amp = fit_amp + 0.1
        m.par['sweep_par'] = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
        m.par['sweep_length'] = nr_of_datapoints
        m.par['RO_duration'] = RO_dur
        m.par['Ex_RO_amplitude'] = Ex_p
        m.f_drive=f_drive
        p_dict['Pi']['duration'] = int(pi_duration/2)      # determines the lentgh of a pi/2 pulse!!!

        b= 2*np.pi*Pi_dict["Amplitude"]*Pi_dict["freq"]
        a = Pi_dict["offset"]+Pi_dict["Amplitude"]
        pi2_dict = Cal_regular_pitwo_pulse(m,p_dict,[ms0_readout,ms1_readout],[a,b],lt1,ssro_dict={})

        print 'ms0_readout:'
        print ms0_readout
        print 'ms1_readout:'
        print ms1_readout

        print 'CORPSE Pi amp :'
        print five_Pi_dict['minimum']
        print 'CORPSE Pi/2 amp :'
        print pi2_dict['pi_over_two']

    Cal_dict={"SSRO":ssro_dict,
              "ESR":{"freq":f_drive},
              "MW":Pi_dict,
              "MW_five_pi":five_Pi_dict,
              "MW_pi_over_two":pi2_dict
               }

    return Cal_dict

def Cal_all_CORPSE(nr_of_datapoints,RO_dur=47,Ex_p=9e-9,lt1=False,ESR=None,SSRO=False):
        p_dict = {
                    "Pi":{  "duration": 58.,        # this determines the rabi frequency of the single pulses that make up one CORPSE pulse
                            "amplitude":0.4845
                          },

                    "init_state_pulse": {"duration":0., 
                            "amplitude":0.,  
                            "Do_Pulse": False},

                    "time_between_pulses": 50.,

                    "duty_cycle_time": 100.,
                     }
        
        ## Calibrate SSRO

        if SSRO:
            ssro_dict = Cal_SSRO(str(lt1),lt1)
        else:
            ssro_dict={}


        ## Calibrate ESR

        if ESR:
            ESR_dict={}
            ESR_dict['freq'] = ESR
        else:    
            ESR_dict={}
            ESR_dict['freq'] = Cal_ESR(lt1)
        
        f_drive=ESR_dict['freq']
        
        
        ##Calibrate single Pi pulse

        name = 'Cal_Single_Pi'
        m = PulseCalibration(name)
        m.setup(lt1)

        min_pulse_amp =             0.0
        max_pulse_amp =             0.85
        m.par['sweep_par'] = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
        m.par['sweep_length'] = nr_of_datapoints
        m.par['RO_duration'] = RO_dur
        m.par['Ex_RO_amplitude'] = Ex_p
        m.f_drive=f_drive

        Pi_dict = Cal_regular_pi_pulse(m,1,p_dict,lt1,ssro_dict)
        ms0_readout = float(Pi_dict["highest_meas_value"])


        ## Cal 1 CORPSE

        name = 'Cal_CORPSE_1_Pi'
        m = PulseCalibration(name)
        m.setup(lt1)

        nr_of_pulses=1.
        p_dict["time_between_CORPSE"] = 10.
        fit_amp = Pi_dict["minimum"]
        min_pulse_amp=fit_amp-0.15
        max_pulse_amp=fit_amp+0.15
        
        m.par['sweep_par'] = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
        m.par['sweep_length'] = nr_of_datapoints
        m.par['RO_duration'] = RO_dur
        m.par['Ex_RO_amplitude'] = Ex_p
        m.f_drive=f_drive
        
        CORPSE_Pi_dict = Cal_CORPSE_pulse(m,nr_of_pulses,p_dict,lt1,ssro_dict)
        #ms1_readout = CORPSE_Pi_dict["lowest_meas_value"]   ## THIS NUMBER DETERMINES THE pi/2 pulse largely!!!!!!
        ms1_readout = 10. 

        ## Calibrate 5 CORPSE

        name = 'Cal_CORPSE_5_Pi'
        m = PulseCalibration(name)
        m.setup(lt1)

        nr_of_pulses= 5.
        fit_amp=CORPSE_Pi_dict["minimum"]
        min_pulse_amp=fit_amp-0.1
        max_pulse_amp=fit_amp+0.075
        
        m.par['sweep_par'] = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
        m.par['sweep_length'] = nr_of_datapoints
        m.par['RO_duration'] = RO_dur
        m.par['Ex_RO_amplitude'] = Ex_p
        m.f_drive=f_drive

        CORPSE_5_Pi_dict = Cal_CORPSE_pulse(m,nr_of_pulses,p_dict,lt1,ssro_dict)
 
        ## Calibrate CORPSE pi/2

        name = 'Cal_CORPSE_Pi2'
        m = PulseCalibration(name)
        m.setup(lt1)

        nr_of_pulses= 5.
        fit_amp=CORPSE_5_Pi_dict["minimum"]
        min_pulse_amp=fit_amp-0.1
        max_pulse_amp=fit_amp+0.1
        #if lt1:
        #    min_pulse_amp = fit_amp - 0.12
        #    max_pulse_amp = fit_amp + 0.1
        m.par['sweep_par'] = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
        m.par['RO_duration'] = RO_dur
        m.par['Ex_RO_amplitude'] = Ex_p
        m.f_drive=f_drive

        b= 2*np.pi*Pi_dict["Amplitude"]*Pi_dict["freq"]
        a = Pi_dict["offset"]+Pi_dict["Amplitude"]
        CORPSE_pi2_dict = Cal_CORPSE_pitwo(m,p_dict,[ms0_readout,ms1_readout],[a,b],lt1,ssro_dict={})
        
    
        print 'ms0_readout:'
        print ms0_readout
        print 'ms1_readout:'
        print ms1_readout

        print 'CORPSE Pi amp :'
        print CORPSE_5_Pi_dict['minimum']
        print 'CORPSE Pi/2 amp :'
        print CORPSE_pi2_dict['pi_over_two']

        Cal_dict={"SSRO":ssro_dict,
                  "ESR":{"freq":f_drive},
                  "MW":Pi_dict,
                  "MW_CORPSE":CORPSE_Pi_dict,
                  "MW_Five_CORPSE": CORPSE_5_Pi_dict ,
                  "MW_CORPSE_pi_over_two":CORPSE_pi2_dict
                   }

        return Cal_dict

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


