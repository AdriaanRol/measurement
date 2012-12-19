import qt
import numpy as np
import ctypes
import inspect
import time as dtime
import msvcrt
from measurement.lib.measurement import Measurement
from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib import PQ_measurement_generator_v2 as pqm
from measurement.lib import ssro_ADwin_class as ssro_ADwin
from measurement.lib import esr
from measurement.lib.config import awgchannels_lt2 as awgcfg
from measruement.lib.sequence import common as commonseq
from measurement.lib.sequence import decoupling_v2 as dec
from analysis.lib.spin import pulse_calibration_fitandplot, spin_control 



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
        self.par['green_repump_duration'] =        12
        self.par['CR_duration'] =                  250 #NOTE set to 60 for Ey,A1
        self.par['SP_duration'] =                  350 # NOTE set to 50 for Ey, A1
        self.par['SP_filter_duration'] =           0
        self.par['sequence_wait_time'] =           int(np.ceil(1e-3)+2)
        self.par['wait_after_pulse_duration'] =    1
        self.par['CR_preselect'] =                 1000

        self.par['reps_per_datapoint'] =           500
        self.par['sweep_length'] =                 int(21)
        self.par['RO_repetitions'] =               int(21*1000)
        self.par['RO_duration'] =                  22

        self.par['cycle_duration'] =               300
        self.par['CR_probe'] =                     100

        self.par['green_repump_amplitude'] =       160e-6
        self.par['green_off_amplitude'] =          0e-6
        self.par['Ex_CR_amplitude'] =              10e-9 #OK
        self.par['A_CR_amplitude'] =               13e-9 # NOTE set to 15e-9 for Ey,A1
        self.par['Ex_SP_amplitude'] =              0 
        self.par['A_SP_amplitude'] =               15e-9 #OK: PREPARE IN MS = 0
        self.par['Ex_RO_amplitude'] =              9e-9 #OK: READOUT MS = 0
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



    def start_measurement(self,generate_sequence,pulse_dict,lt1=False,ssro_dict={},send_sequence_AWG=True):
        # Prepare MW source and counters
        print 'Setting MW freq to '
        print (self.f_drive*1e-9)

        self.microwaves.set_iq('on')
        self.microwaves.set_frequency(self.f_drive)
        self.microwaves.set_pulm('on')
        self.microwaves.set_power(self.mwpower)
        self.counters.set_is_running(False)
        
        #Generate sequence and send to AWG
        if send_sequence_AWG:
            sequence = generate_sequence(self.par['sweep_par'],pulse_dict,lt1)
        else:
            sequence=self.sequence
        #sequence["max_seq_time"]=100000
        self.par['RO_repetitions'] =               int(len(self.par['sweep_par'])*self.par['reps_per_datapoint'])
        self.par['sweep_length'] =                 int(len(self.par['sweep_par']))
        print 'seq max time in start meas'
        print int(np.ceil(sequence["max_seq_time"])+10)
        self.par['sequence_wait_time'] =           int(np.ceil(sequence["max_seq_time"])+10)
        
        
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
        self.par['green_off_voltage'] = 0.08#self.ins_green_aom.power_to_voltage(self.par['green_off_amplitude'])
        self.par['A_off_voltage'] = -0.08
        self.par['Ex_off_voltage'] = 0.0
        self.par['Ex_CR_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_CR_amplitude'])
        self.par['A_CR_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_CR_amplitude'])
        self.par['Ex_SP_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_SP_amplitude'])
        self.par['A_SP_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_SP_amplitude'])
        self.par['Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.par['Ex_RO_amplitude'])
        self.par['A_RO_voltage'] = self.ins_A_aom.power_to_voltage(self.par['A_RO_amplitude'])

        print 'SP duration'
        print self.par['SP_duration']
        print 'max_sp_bins'
        print self.max_SP_bins
        print 'sweep_length'
        print self.par['sweep_length']
        print 'RO duration'
        print self.par['RO_duration']
        print 'max_ro_dim'
        print self.max_RO_dim
    
        if  (self.par['SP_duration'] > self.max_SP_bins) or \
            (self.par['sweep_length']*self.par['RO_duration'] > self.max_RO_dim):
                print ('Error: maximum dimensions exceeded')
                return(-1)

        #print 'SP E amplitude: %s'%self.par['Ex_SP_voltage']
        #print 'SP A amplitude: %s'%self.par['A_SP_voltage']

        if not(lt1):
            self.adwin.set_spincontrol_var(set_phase_locking_on = self.set_phase_locking_on)
            self.adwin.set_spincontrol_var(set_gate_good_phase =  self.set_gate_good_phase)
        print 'seq max time set in ADwin'
        print self.par['sequence_wait_time']
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
            A_off_voltage = self.par['A_off_voltage'],
            Ex_off_voltage = self.par['Ex_off_voltage'],
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
        savdat['min_sweep_par']=self.par['fe_min']
        savdat['max_sweep_par']=self.par['fe_max']
        savdat['sweep_par_name'] = self.par['sweep_par_name']
        savdat['sweep_par'] = self.par['sweep_par']
        savdat['noof_datapoints'] = self.par['sweep_length']
        savdat['fe_max'] = self.par['fe_max']
        savdat['fe_min'] = self.par['fe_min']
        savdat['free_evol'] = self.par['free_evol']
        
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


def get_datapath():
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    return datapath

def XY8(RO_dur=48,Ex_p=12e-9,lt1=False,CORPSE_pi=0.577,CORPSE_pi2=0.631,CORPSE=False,MW_freq=2.8286e9,name='Decoupling'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    if CORPSE:
        name=name+'CORPSE'
    m = Decoupling(name)
    m.setup(lt1)

    # zoomed in SE
    nr_of_datapoints = 11
    min_tau =  0.1e3
    max_tau =  53.9064e3*10
    tau=np.linspace(0,max_tau,nr_of_datapoints)
    tau[0]=min_tau
    
    
    pulse_dict = {
                "Pi":{"amplitude":0.6615,"duration":50.},
                "init_state_pulse":{"amplitude":.743,"duration":25.},
                "CORPSE_pi":{"duration": 58., "amplitude":CORPSE_pi},
                "CORPSE_pi2":{"duration": 58., "amplitude":CORPSE_pi2},
                "time_between_pulses": 10.,
                "time_between_CORPSE":10.,
                "nr_of_XY8_cycles": 1/8.,
                "duty_cycle_time": 100.,                             
                }
    m.par['sweep_par'] = tau
    m.par['sweep_par_name'] = 'tau [ns]'
    m.par['sweep_length'] = len(tau)
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    fe_min = pulse_dict['nr_of_XY8_cycles']*16*min_tau
    fe_max = pulse_dict['nr_of_XY8_cycles']*16*max_tau
    m.par['fe_max'] = max_tau#fe_max*1e-6
    m.par['fe_min'] = min_tau#fe_min*1e-6
    m.par['free_evol'] = tau*16*pulse_dict['nr_of_XY8_cycles']
    m.sequence={}
    m.sequence['max_seq_time'] = 20645
    m.f_drive=MW_freq

    m.par['nr_of_pulses']=8*pulse_dict['nr_of_XY8_cycles']
    if CORPSE:
        m.start_measurement(dec.DEC_CORPSE,pulse_dict,lt1=lt1,send_sequence_AWG=True)
    else:
        m.start_measurement(dec.XY8_cycles,pulse_dict,lt1=lt1)

def XY8_rep_el(RO_dur=48,Ex_p=11.5e-9,MW_freq=2.8291e9,lt1=False,ssro_dict={},CORPSE=False,name='XY8'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    name = name
    m = Decoupling(name)
    m.setup(lt1)

    

    # Determine tau
    tau_el_len = 53.7239e3/11/3
    tau_el_len = 1628
    #tau_el_len = 2e3
    #tau_el_len_us = tau_el_len*1e3

    #tau_rep_min=0     # maxtau in units of tau_len
    #tau_rep_max=25     # maxtau in units of tau_len
    #tau_rep = np.linspace(tau_rep_min,tau_rep_max,nr_of_datapoints)
    #tau_rep[0]=1
    
    #tau_rep=np.array([1./500.,1,2,3,4])
    #tau_rep=np.array([1,1,2,3,4,5,6,7,8,10,13,15,17,20,30,40,50,60,70,75]) #XY4
    #tau_rep=np.array([1,1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20]) #XY16
    #tau_rep=np.array([1,1,2,3,4,5,6,7,8,9,10]) #XY32
    #tau_rep=np.array([1,1,2,3,4,5,6,7,8,9,10]) #XY64
    
    #on revivals
    #tau_rep=np.array([1/500.,1,2,3,4,5,6,7,8,9]) #XY4
    #tau_rep=np.array( [1/500.,1,2,3,4,5,6]) #XY8
    #tau_rep=np.array([33./500,31,32,33,34,35]) #XY16
    tau_rep=np.array([1/3.,1/3.])*3 #XY32
    #tau_rep=np.array([11/500.,1])*3 #XY64
    #tau_rep=np.array([11/500.,11*20]) #XY64
    #tau_rep=np.array([11./500.,50*11]) #XY16-pairs
    #tau_rep = np.linspace (0,15,16)
    #tau_rep[0] = 11./500
    
    m.par['sweep_par'] = tau_rep
    m.par['sweep_length'] = len(tau_rep)
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    m.f_drive=MW_freq
    pulse_dict = {
        "Pi":{"duration": 0*50., "amplitude": 0*0.40514},
        "CORPSE_pi":{"duration": 58., "amplitude":0.484},
        "CORPSE_pi2":{"duration": 58., "amplitude":0.498},
        "init_state_pulse": {"duration":50. , "amplitude":0.40514},  
            "time_between_pulses": 10.,
            "nr_of_XY8_cycles": 4/8.,
            "duty_cycle_time": 100.,  
            "tau_el_length":tau_el_len,
            "final_tau":50.,
            "time_between_CORPSE":20.,
            }    
    
    m.par['free_evol'] = pulse_dict['nr_of_XY8_cycles']*16*tau_el_len*tau_rep
    m.par['free_evol'][0]=1*pulse_dict['nr_of_XY8_cycles']*16
    print m.par['free_evol']
    m.par['fe_max'] = m.par['free_evol'].max()*1e-6
    m.par['fe_min'] = m.par['free_evol'].min()*1e-6
    m.par['sweep_par_name'] = 'Free evolution time (ms)'
    m.par['nr_of_pulses']=8*pulse_dict['nr_of_XY8_cycles']
    pulse_dict["duty_cycle_time"] = 100
    m.sequence={}
    m.sequence["max_seq_time"]=100000
    if CORPSE:
        m.start_measurement(dec.XY8_cycles_multiple_elements_CORPSE,pulse_dict,lt1=lt1,ssro_dict=ssro_dict)
    else:
        m.start_measurement(dec.XY8_cycles_multiple_elements,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,send_sequence_AWG=False)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    spin_control.plot_SE(path)    
    
    #min_tau =  0.010e3
    #max_tau =  164.503e3
    
def XY8_rep_el_tau(RO_dur=48,Ex_p=11.5e-9,MW_freq=2.8291e9,lt1=False,ssro_dict={},name='XY8'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    name = name
    m = Decoupling(name)
    m.setup(lt1)

    

    # Determine tau
    tau_el_len = 53.9064e3/11/3
    tau_el_len = np.round_(np.linspace(1578,1658,20)/4)*4
    tau_el_len[0] = 500./33.
    tau_rep_el = 33*3
    
    m.par['sweep_par'] = tau_el_len
    m.par['sweep_length'] = len(tau_el_len)
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    m.f_drive=MW_freq
    pulse_dict = {
        "Pi":{"duration": 50., "amplitude": 0.4028},
        "init_state_pulse": {"duration":25. , "amplitude":0.452},  
            "time_between_pulses": 10.,
            "nr_of_XY8_cycles": 32/8.,
            "duty_cycle_time": 100.,  
            "final_tau":50.,
            "tau_rep_el":tau_rep_el,
            }    
    
    m.par['free_evol'] = pulse_dict['nr_of_XY8_cycles']*16*tau_rep_el*tau_el_len
    m.par['free_evol'][0]=1*pulse_dict['nr_of_XY8_cycles']*16
    print m.par['free_evol']
    m.par['fe_max'] = m.par['free_evol'].max()*1e-6
    m.par['fe_min'] = m.par['free_evol'].min()*1e-6
    m.par['sweep_par_name'] = 'Free evolution time (ms)'
    m.par['nr_of_pulses']=8*pulse_dict['nr_of_XY8_cycles']
    pulse_dict["duty_cycle_time"] = 100
    m.sequence={}
    m.sequence["max_seq_time"]=10506

    m.start_measurement(dec.XY8_cycles_multiple_elements_tau,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,send_sequence_AWG=False)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    spin_control.plot_SE(path)    
    
    #min_tau =  0.010e3
    #max_tau =  164.503e3
  
def XY8_rep_el_final_tau(RO_dur=48,Ex_p=11.5e-9,MW_freq=2.8291e9,lt1=False,ssro_dict={},CORPSE=False,name='XY8'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    name = name
    m = Decoupling(name)
    m.setup(lt1)

    

    # Determine tau
    tau_el_len = 75
    final_tau=np.linspace(0,100,11)

    m.par['sweep_par'] = final_tau
    m.par['sweep_length'] = len(final_tau)
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    m.f_drive=MW_freq
    pulse_dict = {
        "Pi":{"duration": 50., "amplitude": 0*0.4028},
        "CORPSE_pi":{"duration": 58., "amplitude":0.484},
        "CORPSE_pi2":{"duration": 58., "amplitude":0.498},
        "init_state_pulse": {"duration":25. , "amplitude":0*0.429},  
            "time_between_pulses": 10.,
            "nr_of_XY8_cycles": 64/8.,
            "duty_cycle_time": 100.,  
            "tau_el_length":tau_el_len,
            "final_tau":final_tau,
            "tau_sweep":1,
            "time_between_CORPSE":20.,
            }    
    
    m.par['free_evol'] = final_tau
    print m.par['free_evol']
    m.par['fe_max'] = m.par['sweep_par'].max()
    m.par['fe_min'] = m.par['sweep_par'].min()
    m.par['sweep_par_name'] = 'final tau (ns)'
    m.par['nr_of_pulses']=8*pulse_dict['nr_of_XY8_cycles']
    pulse_dict["duty_cycle_time"] = 100
    m.sequence={}
    m.sequence["max_seq_time"]=17205
    if CORPSE:
        m.start_measurement(dec.XY8_cycles_multiple_elements_CORPSE,pulse_dict,lt1=lt1,ssro_dict=ssro_dict)
    else:
        m.start_measurement(dec.XY8_cycles_sweep_final_tau,pulse_dict,lt1=lt1,ssro_dict=ssro_dict,send_sequence_AWG=True)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    spin_control.plot_SE(path)    
    
    #min_tau =  0.010e3
    #max_tau =  164.503e3  
    
if __name__ == '__main__':
    XY8_rep_el()



