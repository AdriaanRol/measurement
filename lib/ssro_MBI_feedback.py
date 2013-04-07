#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
import ctypes
import inspect
import time as dtime
import msvcrt
import math
from measurement import Measurement 
from AWG_HW_sequencer_v2 import Sequence
from config import awgchannels_lt2 as awgcfg
from sequence import common as commonseq
from analysis.lib.spin import pulse_calibration_fitandplot_lib as lde_calibration
from analysis.lib.spin import spin_control
from config import experiment_lt2 as exp
from sequence import MBI_seq as MBIseq


#import measurement.measurement as meas
#from measurement.AWG_HW_sequencer_v2 import Sequence
#import measurement.PQ_measurement_generator_v2 as pqm
#from measurement import Measurement
#from analysis import spin_control as sc
#from measurement.config import awgchannels_lt2 as awgcfg
#from measurement.sequence import common as commonseq


class MBI(Measurement):
    
    def __init__(self,name):
        Measurement.__init__(self,name,mclass='MBI')


###########################################################
##
##  hardcoded in ADwin program (adjust there if necessary!)
##

        self.max_SP_bins = 500
        self.max_RO_dim = 1000000

##
###########################################################
        
# load dictionary of sil
        self.sildic = exp.current_sample
        self.ssrodic = exp.ssroprotocol
        self.MBIdic = exp.MBIprotocol
        self.hardwaredic = exp.hardware
        self.pulsedic = exp.pulses

        self.MW_freq = self.sildic['MW_source_freq']
        self.MW_power = self.sildic['MW_source_power']
        self.set_phase_locking_on=0
        self.set_gate_good_phase=-1
       
        self.nr_of_datapoints= 21
        self.repetitions_per_datapoint = 500
        self.nr_of_RO_steps =    1
        self.do_shelv_pulse = False
        self.do_incr_RO_steps = exp.MBIprotocol['do_incr_RO_steps']
        self.incr_RO_steps = exp.MBIprotocol['incr_RO_steps']
        self.Ex_RO_amplitude = self.ssrodic['Ex_RO_amplitude']
        self.A_RO_amplitude = self.ssrodic['A_RO_amplitude']
        self.Ex_final_RO_amplitude = self.ssrodic['Ex_RO_amplitude']
        self.A_final_RO_amplitude = self.ssrodic['A_RO_amplitude']
        self.final_RO_duration= self.ssrodic['RO_duration']
        self.RO_duration= self.ssrodic['RO_duration']
        self.wait_after_RO = self.ssrodic['wait_after_pulse_duration']
        self.wait_for_AWG_done = 1.
        self.par = {}
        
        self.par['MBI_threshold']    =              1 # pass if counts > (MBI_threshold-1)
        self.par['RO_repetitions']  =               100

    # FIXME: this should be in the measurement class
    def setup(self,lt1=False):

        self.awg = qt.instruments['AWG']
        self.temp = qt.instruments['temperature_lt1']
        if lt1:
            self.ins_green_aom=qt.instruments['GreenAOM_lt1']
            self.ins_E_aom=qt.instruments['MatisseAOM_lt1']
            self.ins_A_aom=qt.instruments['NewfocusAOM_lt1']
            self.adwin=qt.instruments['adwin_lt1']
            self.counters=qt.instruments['counters_lt1']
            self.physical_adwin=qt.instruments['physical_adwin_lt1']
            self.microwaves = qt.instruments['SMB_100_lt1']
            self.microwaves.set_status('off')
            self.ctr_channel=2
            self.mwpower = self.MW_power
        else:
            self.ins_green_aom=qt.instruments['GreenAOM']
            self.ins_E_aom=qt.instruments['MatisseAOM']
            self.ins_A_aom=qt.instruments['NewfocusAOM']
            self.adwin=qt.instruments['adwin']
            self.counters=qt.instruments['counters']
            self.physical_adwin=qt.instruments['physical_adwin']
            self.microwaves = qt.instruments['SMB100']
            self.ctr_channel=exp.hardware['counter_channel']
            self.mwpower = self.MW_power
            self.microwaves.set_status('off')
        self.par['counter_channel'] = self.ctr_channel
        self.par['green_laser_DAC_channel'] =      self.adwin.get_dac_channels()['green_aom']
        self.par['Ex_laser_DAC_channel'] =         self.adwin.get_dac_channels()['matisse_aom']
        self.par['A_laser_DAC_channel'] =          self.adwin.get_dac_channels()['newfocus_aom']




    def start_measurement(self, gen_seq_function, lt1 = False):
        #Prepare Vector source and AOMs

        self.microwaves.set_iq('on')
        self.microwaves.set_frequency(self.MW_freq)
        self.microwaves.set_pulm('on')
        self.microwaves.set_power(self.MW_power)
        self.counters.set_is_running(False)

        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)
        self.ins_green_aom.set_cur_controller('ADWIN')
        self.ins_E_aom.set_cur_controller('ADWIN')
        self.ins_A_aom.set_cur_controller('ADWIN')
        self.ins_green_aom.set_power(0.)
        self.ins_E_aom.set_power(0.)
        self.ins_A_aom.set_power(0.)

        
        self.generate_sequence(gen_seq_function)
        
        # Set measurement parameters to par
        #self.par['sequence_wait_time'] =            self.sequence_wait_time
        

        #if self.power_and_mw_ok():
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
            self.spin_control(self, lt1)

            self.end_measurement()
        else:
            print 'Measurement aborted'
   
    def generate_sequence(self,gen_seq_func,do_program=True,lt1=False):
        seq = Sequence('spin_control')
        awgcfg.configure_sequence(seq,'mw_weak_meas')

        seq_wait_time = gen_seq_func(self,seq)
        
        if self.wait_for_AWG_done ==1 :
            self.par['sequence_wait_time'] = 1
        else:    
            self.par['sequence_wait_time'] = seq_wait_time
        
        seq.set_instrument(self.awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
    
        seq.force_HW_sequencing(True)
        seq.send_sequence()


    def spin_control(self, data, lt1=False):
        

        self.par['green_repump_voltage'] = self.ins_green_aom.power_to_voltage(self.ssrodic['green_repump_amplitude'])
        self.par['green_off_voltage'] = self.hardwaredic['green_off_voltage']
        self.par['Ex_CR_voltage'] = self.ins_E_aom.power_to_voltage(self.ssrodic['Ex_CR_amplitude'])
        self.par['A_CR_voltage'] = self.ins_A_aom.power_to_voltage(self.ssrodic['A_CR_amplitude'])
        self.par['Ex_SP_voltage'] = self.ins_E_aom.power_to_voltage(self.ssrodic['Ex_SP_amplitude'])
        self.par['A_SP_voltage'] = self.ins_A_aom.power_to_voltage(self.ssrodic['A_SP_amplitude'])
        self.par['Ex_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.Ex_RO_amplitude)
        self.par['A_RO_voltage'] = self.ins_A_aom.power_to_voltage(self.A_RO_amplitude)
        self.par['Ex_final_RO_voltage'] = self.ins_E_aom.power_to_voltage(self.Ex_final_RO_amplitude)
        self.par['A_final_RO_voltage'] = self.ins_A_aom.power_to_voltage(self.A_final_RO_amplitude)

        if  (self.ssrodic['SP_A_duration'] > self.max_SP_bins) or \
            (len(self.par['sweep_par'])*self.ssrodic['RO_duration'] > self.max_RO_dim):
                print ('Error: maximum dimensions exceeded')
                return(-1)

            #print 'SP E amplitude: %s'%self.par['Ex_SP_voltage']
            #print 'SP A amplitude: %s'%self.par['A_SP_voltage']

        if not(lt1):
            self.adwin.set_spincontrol_var(set_phase_locking_on = self.set_phase_locking_on)
            self.adwin.set_spincontrol_var(set_gate_good_phase =  self.set_gate_good_phase)
        
        print "SEQ_WAIT_TIME: "+str(self.par['sequence_wait_time'])+"us"
        print "Sweep parameter:" +str(self.par['sweep_par'])
        
        self.adwin.start_MBI_feedback(
            counter_channel = self.hardwaredic['counter_channel'],
            green_laser_DAC_channel = self.par['green_laser_DAC_channel'],
            Ex_laser_DAC_channel = self.par['Ex_laser_DAC_channel'],
            A_laser_DAC_channel = self.par['A_laser_DAC_channel'],
            AWG_start_DO_channel = self.MBIdic['AWG_start_DO_channel'],
            AWG_done_DI_channel = self.MBIdic['AWG_done_DI_channel'],
            send_AWG_start = self.MBIdic['send_AWG_start'],
            wait_for_AWG_done = self.wait_for_AWG_done,
            green_repump_duration = self.ssrodic['green_repump_duration'],
            CR_duration = self.ssrodic['CR_duration'],
            SP_E_duration = self.ssrodic['SP_E_duration'],
            SP_A_duration = self.ssrodic['SP_A_duration'],
            SP_filter_duration = self.ssrodic['SP_filter_duration'],
            sequence_wait_time = self.par['sequence_wait_time'],
            wait_after_pulse_duration = self.ssrodic['wait_after_pulse_duration'],
            CR_preselect = self.ssrodic['CR_preselect'],
            RO_repetitions = self.par['RO_repetitions'],
            RO_duration = self.RO_duration,
            sweep_length = len(self.par['sweep_par']),
            cycle_duration = self.MBIdic['cycle_duration'],
            CR_probe = self.ssrodic['CR_probe'],
            AWG_event_jump_DO_channel = self.MBIdic['AWG_event_jump_DO_channel'],
            MBI_duration = self.MBIdic['MBI_RO_duration'],
            MBI_threshold = self.par['MBI_threshold'],
            wait_after_RO_pulse_duration = self.wait_after_RO,
            final_RO_duration = self.final_RO_duration,
            wait_for_MBI_pulse=self.MBIdic['wait_for_MBI_pulse'],
            green_repump_voltage = self.par['green_repump_voltage'],
            green_off_voltage = self.hardwaredic['green_off_voltage'],
            Ex_CR_voltage = self.par['Ex_CR_voltage'],
            A_CR_voltage = self.par['A_CR_voltage'],
            Ex_SP_voltage = self.par['Ex_SP_voltage'],
            A_SP_voltage = self.par['A_SP_voltage'],
            Ex_RO_voltage = self.par['Ex_RO_voltage'],
            A_RO_voltage = self.par['A_RO_voltage'],
            Ex_final_RO_voltage = self.par['Ex_final_RO_voltage'],
            A_final_RO_voltage = self.par['A_final_RO_voltage'],
            wait_before_final_SP=(exp.pulses['RF_pi2_len']/1000.)+16,
            )

        if lt1:
            self.adwin_lt2.start_check_trigger_from_lt1()
                

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
            print('completed %s / %s readout repetitions, %.2f CR percentage succes,%.2f MBI percentage succes'%(reps_completed,self.par['RO_repetitions'], CR_failed_percentage,MBI_failed_percentage))
            print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                break

            qt.msleep(2.5)
        self.physical_adwin.Stop_Process(9)
            
        if lt1:
            self.adwin_lt2.stop_check_trigger_from_lt1()

        reps_completed  = self.physical_adwin.Get_Par(73)
        print('completed %s / %s readout repetitions'%(reps_completed,self.par['RO_repetitions']))

        sweep_length = len(self.par['sweep_par'])
        par_long   = self.physical_adwin.Get_Data_Long(20,1,35)
        par_float  = self.physical_adwin.Get_Data_Float(20,1,10)
        CR_before = self.physical_adwin.Get_Data_Long(22,1,1)
        CR_after  = self.physical_adwin.Get_Data_Long(23,1,1)
        SP_hist   = self.physical_adwin.Get_Data_Long(24,1,self.ssrodic['SP_A_duration'])
        print 'start getting datar'
        SN = self.adwin.get_MBI_feedback_var('SN', start=1, length=sweep_length)
        FS = self.adwin.get_MBI_feedback_var('FS', start=1, length=sweep_length)
        FF = self.adwin.get_MBI_feedback_var('FF', start=1, length=sweep_length)
        FinalRO_SN = self.adwin.get_MBI_feedback_var('FinalRO_SN', start=1, length=sweep_length)
        FinalRO_FS = self.adwin.get_MBI_feedback_var('FinalRO_FS', start=1, length=sweep_length)
        FinalRO_FF = self.adwin.get_MBI_feedback_var('FinalRO_FF', start=1, length=sweep_length)

        #SSRO_data = np.reshape(SSRO_data,(sweep_length,self.par['RO_duration']))
        statistics = self.physical_adwin.Get_Data_Long(26,1,10)

        sweep_index = np.arange(sweep_length)
        sp_time = np.arange(self.ssrodic['SP_A_duration'])*self.MBIdic['cycle_duration']*3.333
        ro_time = np.arange(self.ssrodic['RO_duration'])*self.MBIdic['cycle_duration']*3.333


        #try replacing data with self???
        data.save()
        savdat={}
        savdat['counts']=CR_after
        data.save_dataset(name='ChargeRO_after', do_plot=False, 
            data = savdat, idx_increment = False)
        savdat={}
        savdat['counts']=SP_hist
        data.save_dataset(name='SP_histogram', do_plot=False, 
            data = savdat, idx_increment = False)
        savdat={}
        savdat['time']=ro_time

        #FIXME: sweep_axis doesnt do anything useful ?
        savdat['sweep_par'] = self.par['sweep_par']
        savdat['sweep_par_name'] = self.par['sweep_par_name']
        savdat['SN']=SN
        savdat['FS']=FS
        savdat['FF']=FF
        savdat['FinalRO_SN']=FinalRO_SN
        savdat['FinalRO_FS']=FinalRO_FS
        savdat['FinalRO_FF']=FinalRO_FF
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
           
        # ata.save_dataset(name='SSRO_calibration', do_plot=False, 
           #     data = ssro_dict, idx_increment = True)
        return  

    def end_measurement(self):
        self.awg.stop()
        self.awg.set_runmode('CONT')
        self.adwin.set_simple_counting()
        self.counters.set_is_running(1)
        self.ins_green_aom.set_power(180e-6)

        self.microwaves.set_status('off')
        self.microwaves.set_iq('off')
        self.microwaves.set_pulm('off')
        self.ins_E_aom.set_power(0)
        self.ins_A_aom.set_power(0)


    def power_and_mw_ok(self):
        ret = True
        max_E_power = self.ins_E_aom.get_cal_a()
        max_A_power = self.ins_A_aom.get_cal_a()
        if (max_E_power < self.ssrodic['Ex_CR_amplitude']) or \
                (max_E_power < self.ssrodic['Ex_SP_amplitude']) or \
                (max_E_power < self.ssrodic['Ex_RO_amplitude']):
            print 'Trying to set too large value for E laser, quiting!'
            ret = False    
        if (max_A_power < self.ssrodic['A_CR_amplitude']) or \
                (max_A_power < self.ssrodic['A_SP_amplitude']) or \
                (max_A_power < self.ssrodic['A_RO_amplitude']):
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



####
# Here are all the functions that make use of the MBI class
#
# 



def get_datapath():
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    return datapath

def get_freq(m,line):
    if line=='-1':
        f = (m.sildic['MW_freq_center']-m.sildic['MW_source_freq']-
                          m.sildic['hf_splitting'])
    elif line == '+1':
        f = (m.sildic['MW_freq_center']-m.sildic['MW_source_freq']+
                          m.sildic['hf_splitting'])

    elif line == '0':
        f=(m.sildic['MW_freq_center']-m.sildic['MW_source_freq'])
    elif line == '0+1':
        f=(m.sildic['MW_freq_center']-m.sildic['MW_source_freq']+
                          m.sildic['hf_splitting']/2.)
    elif line == '0-1':
        f=(m.sildic['MW_freq_center']-m.sildic['MW_source_freq']-
                     m.sildic['hf_splitting']/2.)    
    else:
        f=line
    return f

