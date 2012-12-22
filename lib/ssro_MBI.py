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
        

        if self.power_and_mw_ok():
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

        self.adwin.start_MBI_Multiple_RO(
            counter_channel = self.hardwaredic['counter_channel'],
            green_laser_DAC_channel = self.par['green_laser_DAC_channel'],
            Ex_laser_DAC_channel = self.par['Ex_laser_DAC_channel'],
            A_laser_DAC_channel = self.par['A_laser_DAC_channel'],
            AWG_start_DO_channel = self.MBIdic['AWG_start_DO_channel'],
            AWG_done_DI_channel = self.MBIdic['AWG_done_DI_channel'],
            send_AWG_start = self.MBIdic['send_AWG_start'],
            wait_for_AWG_done = self.MBIdic['wait_for_AWG_done'],
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
            nr_of_RO_steps = self.nr_of_RO_steps,
            do_incr_RO_steps = self.do_incr_RO_steps,
            incr_RO_steps = self.incr_RO_steps,
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
        SSRO_data   = self.physical_adwin.Get_Data_Long(27,1,sweep_length)
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
        savdat['time']=sp_time
        savdat['counts']=SP_hist
        data.save_dataset(name='SP_histogram', do_plot=False, 
            data = savdat, idx_increment = False)
        savdat={}
        savdat['time']=ro_time

        #FIXME: sweep_axis doesnt do anything useful ?
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

    else:
        f=(m.sildic['MW_freq_center']-m.sildic['MW_source_freq'])
    return f

def sweep_MW_amp (lt1 = False, name = 'SIL9_lt2_sweep_MW_amp', min_amp = 0.6, max_amp = 1.2, MW_len=140,nr_of_MW_pulses=1,nr_of_datapoints = 21,reps=500,RO_reps=1,do_shel=False,init_line='-1',RO_line='-1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    m.setup (lt1)
    reload(MBIseq)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    m.nr_of_RO_steps = RO_reps

    #set sweep parameter
    MW_amp=np.linspace(min_amp,max_amp,nr_of_datapoints)
    m.MW_pulse_amp = MW_amp
    
    # other measurement variables
    m.nr_of_MW_pulses = nr_of_MW_pulses    
    m.MW_pulse_len = MW_len*np.ones(nr_of_datapoints)
    #m.MW_pulse_len = np.linspace (0., 400., RO_reps)
    m.do_shelv_pulse = do_shel
    m.do_incr_RO_steps = 0
    
    m.MBI_mod_freq = get_freq(m,init_line)*np.ones(nr_of_datapoints)
    m.MW_mod_freq = get_freq(m,RO_line)*np.ones(nr_of_datapoints)
    print 'init on mI = ', init_line, m.MBI_mod_freq
    print 'RO on mI = ', RO_line, m.MW_mod_freq

    m.par['sweep_par'] = MW_amp
    m.par['sweep_par_name'] = 'MW pulse amplitude (V)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)
    
    m.start_measurement(m.generate_MW_sweep_sequence)
    dp = get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)

def sweep_MW_len (lt1 = False, name = 'SIL9_lt2_sweep_MW_len', min_len = 10, max_len = 200, MW_amp=0.5,nr_of_MW_pulses=1,nr_of_datapoints = 21,reps=500,RO_reps=1,do_shel=False,init_line='-1',RO_line='-1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    m.nr_of_RO_steps = RO_reps
    print m.nr_of_RO_steps
    MW_len=np.linspace(min_len,max_len,nr_of_datapoints)
    m.nr_of_MW_pulses = nr_of_MW_pulses
    m.do_shelv_pulse = do_shel
    m.do_incr_RO_steps = 0

    m.MW_pulse_amp = MW_amp*np.ones(nr_of_datapoints)
    m.MW_pulse_len = MW_len

    m.MBI_mod_freq = get_freq(m,init_line)*np.ones(nr_of_datapoints)
    m.MW_mod_freq = get_freq(m,RO_line)*np.ones(nr_of_datapoints)
    print 'init on mI = ', init_line, m.MBI_mod_freq
    print 'RO on mI = ', RO_line, m.MW_mod_freq
    
    m.par['sweep_par'] = MW_len
    m.par['sweep_par_name'] = 'MW pulse length (ns)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)

#    m.start_measurement (m.generate_MW_sweep_sequence)
    m.start_measurement (MBIseq.MW_sweep)
    dp = get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)

def sweep_nr_of_cycle_steps (lt1 = False, name = 'SIL9_lt2_multiple_pump_cycles', RO_incr = 5, nr_of_MW_pulses=1,nr_of_datapoints = 21,reps=500,RO_reps=1,do_shel=False,init_line='-1',RO_line='-1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    m.setup (lt1)
    reload(MBIseq)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    m.nr_of_RO_steps = RO_reps
    m.do_incr_RO_steps = 1
    m.incr_RO_steps = RO_incr

    #set laser powers
    m.Ex_final_RO_amplitude = m.ssrodic['Ex_RO_amplitude']
    m.A_final_RO_amplitude = 0.
    m.Ex_RO_amplitude = m.ssrodic['Ex_RO_amplitude']*0
    m.A_RO_amplitude = 0.
    
    
    # other measurement variables
    m.nr_of_MW_pulses = nr_of_MW_pulses    
    m.MW_pulse_len = np.ones(nr_of_datapoints)*m.pulsedic['pi2pi_len']
    m.MW_pulse_amp = np.ones(nr_of_datapoints)*m.pulsedic['pi2pi_amp']
    m.MW_pulse_len = np.ones(nr_of_datapoints)*m.pulsedic['pi2pi_len']
    m.MW_pulse_amp = np.ones(nr_of_datapoints)*m.pulsedic['pi2pi_amp']
    m.MW1_pulse_len = np.ones(nr_of_datapoints)*120
    m.MW1_pulse_amp = np.ones(nr_of_datapoints)*0.8
    m.do_shelv_pulse = do_shel
    
    m.MBI_mod_freq = get_freq(m,init_line)*np.ones(nr_of_datapoints)
    m.MW_mod_freq = get_freq(m,RO_line)*np.ones(nr_of_datapoints)
    m.MW1_mod_freq = get_freq(m,'0')*np.ones(nr_of_datapoints)
    print 'init on mI = ', init_line, m.MBI_mod_freq
    print 'RO on mI = ', RO_line, m.MW_mod_freq
    
    sp = np.linspace(1,1+((nr_of_datapoints-1)*RO_incr),nr_of_datapoints)
    print sp
    m.par['sweep_par'] = sp
    m.par['sweep_par_name'] = 'Pump cycles'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)
    
    m.start_measurement(MBIseq.MW_sweep)
    dp = get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)

def sweep_RF_amp (lt1 = False, name = 'SIL9_lt2_sweep_RF_amp', min_amp = 0., max_amp = 0.200, RF_len=0.5,nr_of_datapoints = 21,reps=500,init_line='-1',RO_line='-1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    m.do_incr_RO_steps = 0.
    m.incr_RO_steps=1.
    
    RF_amp=np.linspace(min_amp,max_amp,nr_of_datapoints)
    RF_freq = m.sildic['mI_m1_freq']
    
    m.MBI_mod_freq = get_freq(m,init_line)
    m.MW_mod_freq = get_freq(m,RO_line)
    m.RF_pulse_len = RF_len*np.ones(nr_of_datapoints)
    m.RF_pulse_amp = RF_amp
    m.RF_freq = RF_freq*np.ones(nr_of_datapoints)
    m.par['sweep_par'] = RF_amp
    m.par['sweep_par_name'] = 'RF amplitude (V)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)

    m.start_measurement (MBIseq.RF_sweep)
    dp = get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)


def sweep_RF_len (lt1 = False, name = 'SIL9_lt2_sweep_RF_len', min_len = 0., max_len = 50000, RF_amp=0.1,nr_of_datapoints = 21,reps=500,init_line='-1',RO_line='-1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints

    RF_len=np.linspace(min_len,max_len,nr_of_datapoints)
    RF_freq = m.sildic['mI_m1_freq']
    m.do_incr_RO_steps = 0.
    m.incr_RO_steps=1.

    m.MBI_mod_freq = get_freq(m,init_line)
    m.RO_mod_freq = get_freq(m,RO_line)
    m.MW_mod_freq = get_freq(m,init_line)

    m.RF_pulse_amp = RF_amp*np.ones(nr_of_datapoints)
    m.RF_pulse_len = RF_len
    m.RF_freq = RF_freq*np.ones(nr_of_datapoints)
    m.par['sweep_par'] = RF_len*1e-3
    m.par['sweep_par_name'] = 'RF pulse length (us)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)

    m.start_measurement (MBIseq.RF_sweep)
    dp = get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)

def nuclear_ramsey (lt1 = False, name = 'SIL9_lt2_N_ramsey',nr_of_datapoints = 21,reps=500,init_line='-1',RO_line='-1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints

    m.RF_phase=np.linspace(0,360,nr_of_datapoints)
    
    RF_freq = m.sildic['mI_m1_freq']
    m.do_incr_RO_steps = 0.
    m.incr_RO_steps=1.
    m.nr_of_RO_steps = 2.
    m.Ex_RO_amplitude = m.ssrodic['Ex_RO_amplitude']


    m.MBI_mod_freq = get_freq(m,init_line)
    m.RO_mod_freq = get_freq(m,RO_line)
    m.MW_mod_freq = (get_freq(m,init_line))*np.ones(nr_of_datapoints)
    m.MW_pulse_len = m.pulsedic['shelving_len']*np.ones(nr_of_datapoints)
    m.MW_pulse_amp = m.pulsedic['shelving_amp']*np.ones(nr_of_datapoints)
    m.do_MW_pulse_after_RF=True
    m.RO_duration =12


    m.wait_after_RO = 50+(m.pulsedic['RF_pi2_len']/1000)
    m.rep_wait_el = 25 + m.ssrodic['RO_duration']
    m.RF_freq = RF_freq*np.ones(nr_of_datapoints)
    m.par['sweep_par'] = m.RF_phase
    m.par['sweep_par_name'] = 'RF phase (degree)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)

    m.start_measurement (MBIseq.Nucl_Ramsey)
    dp = get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)

def nmr (lt1 = False, name = 'SIL9_lt2_nmr', min_freq = 2.743e6, max_freq = 2.78e6, nr_of_datapoints = 21,reps=500,init_line='+1',RO_line='+1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    m.do_incr_RO_steps = 0.
    m.incr_RO_steps=1.

    m.MBI_mod_freq = get_freq(m,init_line)
    m.RO_mod_freq = get_freq(m,RO_line)
    m.MW_mod_freq = get_freq(m,init_line)

    RF_freq=np.linspace(min_freq,max_freq,nr_of_datapoints)
    RF_amp = m.pulsedic['RF_pi_amp']
    RF_len = m.pulsedic['RF_pi_len']

    m.RF_pulse_amp = RF_amp*np.ones(nr_of_datapoints)
    m.RF_pulse_len = RF_len*np.ones(nr_of_datapoints)
    m.RF_freq = RF_freq
    m.par['sweep_par'] = RF_freq*1e-6
    m.par['sweep_par_name'] = 'RF frequency (MHz)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)

    m.start_measurement (MBI_seq.RF_sweep)
    dp = get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)

#def calibrate_readout (lt1=False, name = 'SIL9_lt2_calibrateRO', min_amp=0.12, max_amp=0.22, nr_of_datapoints = 16, reps = 1000):

'''
def decoupling (lt1 = False,  name = 'SIL9_lt2_MBI_XY32',nr_of_pulses=32, RO_dur=48, Ex_p=11.5e-9):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI(name)
    set_measurement_parameters(m)
    m.setup(lt1)

    # Determine tau
    tau_el_len = 53.7239e3/11/3
    tau_el_len = 1628
    tau_rep=np.array([.110, 11.,22.,33.])*3 #XY32
    m.par['tau_sweep']=tau_rep
    m.par['sweep_length'] = len(tau_rep)
    m.par['RO_duration'] = RO_dur
    m.par['Ex_RO_amplitude'] = Ex_p
    m.pulse_dict = {
        "Pi":{"duration": 263., "amplitude": 0.77},
        "CORPSE_pi":{"duration": 58., "amplitude":0.484},
        "CORPSE_pi2":{"duration": 58., "amplitude":0.498},
        "init_state_pulse": {"duration":131. , "amplitude":0.79},  
            "time_between_pulses": 10.,
            "nr_of_XY8_cycles": nr_of_pulses/8.,
            "duty_cycle_time": 100.,  
            "tau_el_length":tau_el_len,
            "final_tau":50.,
            "time_between_CORPSE":20.,
            }    
    
    m.par['sweep_par'] = m.pulse_dict['nr_of_XY8_cycles']*16*tau_el_len*tau_rep
    m.par['sweep_par'][0] = m.pulse_dict['nr_of_XY8_cycles']*16*tau_el_len*tau_rep[0]
    m.par['free_evol'] = m.pulse_dict['nr_of_XY8_cycles']*16*tau_el_len*tau_rep
    m.par['free_evol'][0]=tau_rep[0]*m.pulse_dict['nr_of_XY8_cycles']*16
    m.par['sweep_par'] = m.par['sweep_par']*1e-6
    m.par['free_evol'] = m.par['free_evol']*1e-6
    print m.par['free_evol']
    m.par['fe_max'] = m.par['free_evol'].max()*1e-6
    m.par['fe_min'] = m.par['free_evol'].min()*1e-6
    m.par['sweep_par_name'] = 'Free evolution time (ms)'
    m.par['nr_of_pulses']=8*m.pulse_dict['nr_of_XY8_cycles']
    m.pulse_dict["duty_cycle_time"] = 100
    m.sequence={}
    m.sequence["max_seq_time"]=17205
    m.start_measurement(m.XY8_cycles_multiple_elements_MBI,lt1=lt1)
    
    dp=get_datapath()
    path = lde_calibration.find_newest_data(dp,string=m.name)
    spin_control.plot_data_MBI(path)    
    


'''
### old generate sequence functions:
"""
    def generate_sequence(self,do_program=True, lt1 = False):
        seq = Sequence('spin_control')
        MBIseq.load_channels()

        for i in np.arange(self.nr_of_datapoints):
            MBIseq.MBI_element(seq,name='MBI_pulse'+str(i), 
                   jump_target='spin_control_'+str(i+1),
                   goto_target='MBI_pulse'+str(i))

            if i == self.nr_of_datapoints-1:
                seq.add_element(name = 'spin_control_'+str(i+1), 
                    trigger_wait = True, goto_target = 'MBI_pulse0')
            else:
                seq.add_element(name = 'spin_control_'+str(i+1), 
                    trigger_wait = True)
            
            for j in np.arange(self.nr_of_shelving_pulses):

                if j ==0:
                    seq.add_pulse('wait'+str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                        start = 0, duration = 100+self.par['first_wait_time'], amplitude = 0)
                else:
                    seq.add_pulse('wait'+str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                        start = 0, duration = 15, start_reference=last,link_start_to='end',amplitude = 0)
             
            
            seq.add_pulse('wait_after_shel', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                    start = 0, duration =self.par['first_wait_time'], amplitude = 0, start_reference = last,
                    link_start_to = 'end', shape = 'rectangular') 
            seq.add_pulse('RF', channel = chan_RF, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference='wait_after_shel',link_start_to='end', duration = self.RF_dur[i], amplitude = self.RF_amp[i],shape='sine',frequency=self.RF_freq[i],envelope='erf')
           
            seq.add_pulse('wait3', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                    start = 0, duration =self.par['first_wait_time'], amplitude = 0, start_reference = 'RF',
                    link_start_to = 'end', shape = 'rectangular')

            seq.add_pulse('readout_pulse', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                    start = 0, duration =self.pi2pi_duration[i], amplitude = self.pi2pi_amp[i], start_reference = 'wait3',
                    link_start_to = 'end', shape = 'rectangular')

            seq.add_pulse('pulse_modRO', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'readout_pulse', link_start_to = 'start', 
                duration_reference = 'readout_pulse', link_duration_to = 'duration', 
                amplitude = 2.0)

            
        self.par['sequence_wait_time'] = int(math.ceil((4*self.par['first_wait_time']+wait_for_adwin_dur+self.nr_of_shelving_pulses*(self.shelving_duration.max()+30)+self.RF_dur.max()+self.pi2pi_duration.max()+2000)/1000.))
#        self.par['sequence_wait_time'] = self.sequence_wait_time
        seq.set_instrument(self.awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        
        seq.force_HW_sequencing(True)
        seq.send_sequence()


 def generate_sequence_Ramsey (self, do_program = True, lt1=False):
        '''
        Ramsey experiment with tau repeated in order 
        to decrease the number of points and allow long waiting times (~ms)
        '''

        seq = Sequence ('nuclear_Ramsey')
        awgcfg.configure_sequence(seq,'mw_weak_meas')
        # vars for the channel names
        chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
        wait_for_adwin_dur = 1000*(self.par['MBI_RO_duration']+self.par['wait_for_MBI_pulse'])-self.par['MBI_pulse_length']+1000.
       
        if lt1:
            chan_mwI = 'MW_Imod_lt1'
            chan_mwQ = 'MW_Qmod_lt1'
        else:
            chan_mwI = 'MW_Imod'
            chan_mwQ = 'MW_Qmod'
            chan_RF  = 'RF'
        
        if lt1:
            MW_pulse_mod_risetime = 2
        else:
            MW_pulse_mod_risetime = 6

        Dtau = 1000. #size of each repeated tau chunck [ns]
        tau_ramsey = np.linspace (self.par['min_tau'], self.par['max_tau'], self.nr_of_datapoints)

        for i in np.arange(self.nr_of_datapoints):

            N_tau = int(math.floor(tau_ramsey[i]/Dtau)) #number of times we repeat Dtau
            tau_left = tau_ramsey[i]-N_tau*Dtau 


            #element: MBI_pulse
            seq.add_element(name='MBI_pulse'+str(i+1),trigger_wait=True, event_jump_target='spin_control_'+str(i+1),goto_target='MBI_pulse'+str(i+1))
            seq.add_pulse('wait', channel = chan_mwI, element ='MBI_pulse'+str(i+1),
                    start = 0, duration = 100+self.par['first_wait_time'], amplitude = 0)
            
            seq.add_pulse('MBI_pulse', channel = chan_mwI, element = 'MBI_pulse'+str(i+1),
                    start = 0, duration = self.par['MBI_pulse_length'], amplitude = self.par['MBI_amp'], shape = 'rectangular',start_reference = 'wait',
                    link_start_to = 'end')            
            seq.add_pulse('pulse_mod2', channel = chan_mw_pm, element = 'MBI_pulse'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'MBI_pulse', link_start_to = 'start', 
                    duration_reference = 'MBI_pulse', link_duration_to = 'duration', 
                    amplitude = 2.0)

            seq.add_pulse('wait_for_ADwin', channel = chan_mwI, element = 'MBI_pulse'+str(i+1),
                    start = 0, duration = 1000*(self.par['MBI_RO_duration']+self.par['wait_for_MBI_pulse'])-self.par['MBI_pulse_length']+1000., amplitude = 0, start_reference = 'MBI_pulse',
                    link_start_to = 'end', shape = 'rectangular')

            seq.add_element (name = 'spin_control_'+str(i+1), trigger_wait = True, repetitions=1)
            seq.add_pulse('wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0, duration = 100+self.par['first_wait_time'], amplitude = 0)
            seq.add_pulse('shelving_pulse', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                     start = 0, duration =self.shelving_duration[i], amplitude = self.shelving_amp[i], start_reference = 'wait',
                    link_start_to = 'end', shape = 'rectangular')            
            seq.add_pulse('pulse_mod', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'shelving_pulse', link_start_to = 'start', 
                    duration_reference = 'shelving_pulse', link_duration_to = 'duration', 
                    amplitude = 2.0)

            seq.add_pulse('wait2', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                    start = 0, duration =self.par['first_wait_time'], amplitude = 0, start_reference = 'shelving_pulse',
                    link_start_to = 'end', shape = 'rectangular')    

            seq.add_pulse('RF_first_pi2', channel = chan_RF, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference='wait2',link_start_to='end', duration = self.par['RF_pi']/2., amplitude = self.par['RF_amp'],shape='sine',frequency=self.par['RF_freq'],envelope='erf')
        
            #element: tau
            cur_el_name = 'tau_'+str(i+1)
            seq.add_element (name = cur_el_name, trigger_wait = False, repetitions = N_tau-1)
            seq.add_pulse (name='tau'+str(i+1), channel = chan_RF, element = cur_el_name,
                    start=0, duration= Dtau, amplitude=0.)


            #element: readout
            if i == self.nr_of_datapoints-1:
                seq.add_element(name = 'readout_'+str(i+1), 
                        trigger_wait = False, goto_target = 'MBI_pulse1')
            else:
                seq.add_element(name = 'readout_'+str(i+1), 
                        trigger_wait = False)

            seq.add_pulse('last_tau', channel=chan_RF, element = 'readout_'+str(i+1), start=0, duration = Dtau+tau_left, amplitude = 0.)
            seq.add_pulse('RF_second_pi2', channel = chan_RF, element = 'readout_'+str(i+1),
                    start = 0,start_reference='last_tau',link_start_to='end', duration = self.par['RF_pi']/2., amplitude = self.par['RF_amp'],shape='sine',frequency=self.par['RF_freq'], envelope='erf')

            seq.add_pulse('wait3', channel = chan_mwI, element = 'readout_'+str(i+1),
                    start = 0, duration =self.par['first_wait_time'], amplitude = 0, start_reference = 'RF_second_pi2',
                    link_start_to = 'end', shape = 'rectangular')

            seq.add_pulse('readout_pulse', channel = chan_mwI, element = 'readout_'+str(i+1),
                    start = 0, duration =self.pi2pi_duration[i], amplitude = self.pi2pi_amp[i], start_reference = 'wait3',
                    link_start_to = 'end', shape = 'rectangular')

            seq.add_pulse('pulse_mod2', channel = chan_mw_pm, element = 'readout_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'readout_pulse', link_start_to = 'start', 
                    duration_reference = 'readout_pulse', link_duration_to = 'duration', 
                    amplitude = 2.0)

       

        self.par['sequence_wait_time'] = int(math.ceil((4*self.par['first_wait_time']+wait_for_adwin_dur+self.shelving_duration.max()+self.par['RF_pi']+self.par['max_tau']+self.pi2pi_duration.max()+10000)/1000.))   
        seq.set_instrument(self.awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        


    ###FIXME: this guy should be somewhere else!
    def XY8_cycles_multiple_elements_MBI(self, do_program = True, lt1=False):
        '''
        This sequence consists of a number of decoupling-pulses per sweepparam
        every pulse is in a single element, tau is repeated to decrease number of points
    
        sweep_param = numpy array with number of Pi-pulses per element
        pulse_dict={
                    "Pi":{"duration": ...,
                        "amplitude": ...},

                    "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state
                
                
                    "duty_cycle_time": ...,            waiting time at the end of each element
                    "tau_el_length":...
                    }
        '''
        seq = Sequence('XY8')
        awgcfg.configure_sequence(seq,'mw')
        wait_for_adwin_dur = int(math.ceil((1000*(self.par['MBI_RO_duration']+self.par['wait_for_MBI_pulse'])-self.par['MBI_pulse_length']+20000.)))
        # vars for the channel names
        if lt1:
            chan_mwI = 'MW_Imod_lt1'
            chan_mwQ = 'MW_Qmod_lt1'
            chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
        else:
            chan_mwI = 'MW_Imod' #ch1
            chan_mwQ = 'MW_Qmod' #ch3
            chan_mw_pm = 'MW_pulsemod' #is connected to 
    #FIXME: take this from a dictionary
        if lt1:
            MW_pulse_mod_risetime = 10
        else:
            MW_pulse_mod_risetime = 10
        
        self.nr_of_datapoints = len(self.par['sweep_par'])
        nr_of_XY8_cycles =  self.pulse_dict["nr_of_XY8_cycles"]
        pulse_nr = 8*nr_of_XY8_cycles

        pi = self.pulse_dict["Pi"]
        tau_sweep = self.par['tau_sweep']
        duty_cycle_time = self.pulse_dict["duty_cycle_time"]
        istate_pulse = self.pulse_dict["init_state_pulse"]

        tau_len=self.pulse_dict["tau_el_length"]          # ns


        # Start building sequence!
        #
        # First data point (not with repeated element, just to take first point of
    # decoupling curve)

    
        seq.add_element(name='MBI_pulse'+str(0),trigger_wait=True, event_jump_target='Pi_over2_'+str(0),goto_target='MBI_pulse'+str(0))
        seq.add_pulse('wait', channel = chan_mwI, element ='MBI_pulse'+str(0),
                start = 0, duration = 100+self.par['first_wait_time'], amplitude = 0)
            
        seq.add_pulse('MBI_pulse', channel = chan_mwI, element = 'MBI_pulse'+str(0),
                start = 0, duration = self.par['MBI_pulse_length'], amplitude = self.par['MBI_amp'], shape = 'rectangular',start_reference = 'wait',
                link_start_to = 'end')            
        seq.add_pulse('pulse_mod2', channel = chan_mw_pm, element = 'MBI_pulse'+str(0),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'MBI_pulse', link_start_to = 'start', 
                duration_reference = 'MBI_pulse', link_duration_to = 'duration', 
                amplitude = 2.0)

        seq.add_pulse('wait_for_ADwin', channel = chan_mwI, element = 'MBI_pulse'+str(0),
                start = 0, duration = wait_for_adwin_dur, amplitude = 0, start_reference = 'MBI_pulse',
                link_start_to = 'end', shape = 'rectangular')

        el_name='Pi_over2_'+str(0)
        seq.add_element(name = el_name,trigger_wait = True)
        seq.add_pulse(name='first_wait', channel = chan_mwI, element = el_name,start = 0, 
                duration = 990, amplitude = 0)
    
        seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
            start_reference = 'first_wait', link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')
        seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'Pi/2_pulse', link_start_to = 'start', 
            duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
            amplitude =2.0)
    
        seq.add_pulse(name='tau1',channel=chan_mwI,element=el_name,
                    start=0, start_reference= 'Pi/2_pulse',link_start_to='end',
                    duration=int((tau_sweep[0]*tau_len-pi['duration']/2-istate_pulse['duration']/2)),
                    amplitude=0.)
    
        seq.add_pulse('pi' + str(1), channel = chan_mwI, element = el_name,
                start = 0, duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular',
                start_reference='tau1',link_start_to='end')
        seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(1), link_start_to = 'start', 
                duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
                amplitude = 2.0)
    
        seq.add_pulse(name='tau2',channel=chan_mwI,element=el_name,
                start=0, start_reference= 'pi' + str(1),link_start_to='end',
                duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),amplitude=0)

        last = 'tau2'
        tau_idx=3
        for j in np.arange(1,pulse_nr-1):
                if np.mod(j,8) in [0,2,5,7]:
                    chan = chan_mwI
                else:
                    chan = chan_mwQ
                if np.mod(int(j/8),2) == 0:
                    do_min = 1
                else:
                    do_min=-1
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                        start=0,start_reference = last, link_start_to='end',
                        duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),amplitude=0.)

                seq.add_pulse('pi' + str(j), channel = chan, element = el_name,
                    start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                    start_reference='tau'+str(tau_idx),link_start_to='end')
                seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = el_name,
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pi' + str(j), link_start_to = 'start', 
                    duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)

                tau_idx+=1
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                    start=0,start_reference='pi' + str(j),link_start_to='end',
                    duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),amplitude=0.)
                last='tau'+str(tau_idx)
                tau_idx+=1

        if pulse_nr ==4:
            chan = chan_mwQ
        else:
            chan = chan_mwI

        seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
               start=0,start_reference=last,link_start_to='end',
               duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),
               amplitude=0.)
        seq.add_pulse('pi' + str(pulse_nr), channel = chan, element = el_name,
                start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                start_reference='tau'+str(tau_idx),link_start_to='end')
        seq.add_pulse('pulse_mod' + str(pulse_nr), channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(pulse_nr), link_start_to = 'start', 
                duration_reference = 'pi'+str(pulse_nr), link_duration_to = 'duration', 
                amplitude = 2.0)
        tau_idx+=1
        seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                    start=0, start_reference= 'pi' + str(pulse_nr),link_start_to='end',
                    duration=int((tau_sweep[0]*tau_len-pi['duration']/2-istate_pulse['duration']/2)),amplitude=0)
    
        seq.add_pulse(name='readout_pulse' , channel = chan_mwI, element = el_name,
            start_reference = 'tau'+str(tau_idx), link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = -istate_pulse["amplitude"], shape = 'rectangular')
        seq.add_pulse(name='readout_pulse_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'readout_pulse', link_start_to = 'start', 
            duration_reference = 'readout_pulse', link_duration_to = 'duration', 
            amplitude =2.0)

        last='readout_pulse'
 


        seq.add_pulse('final_wait', channel = chan_mwI, element = el_name,
                start_reference = last,link_start_to ='end',start = 0, 
                duration = 1000.+duty_cycle_time, amplitude = 0)

        # Now for all other datapoints
        #

        for i in np.arange(self.nr_of_datapoints-1):
            i=i+1
            seq.add_element(name='MBI_pulse'+str(i),trigger_wait=True, event_jump_target='Pi_over2_'+str(i+1),goto_target='MBI_pulse'+str(i))
            seq.add_pulse('wait', channel = chan_mwI, element ='MBI_pulse'+str(i),
                    start = 0, duration = 100+self.par['first_wait_time'], amplitude = 0)
            
            seq.add_pulse('MBI_pulse', channel = chan_mwI, element = 'MBI_pulse'+str(i),
                    start = 0, duration = self.par['MBI_pulse_length'], amplitude = self.par['MBI_amp'], shape = 'rectangular',start_reference = 'wait',
                    link_start_to = 'end')            
            seq.add_pulse('pulse_mod2', channel = chan_mw_pm, element = 'MBI_pulse'+str(i),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'MBI_pulse', link_start_to = 'start', 
                duration_reference = 'MBI_pulse', link_duration_to = 'duration', 
                amplitude = 2.0)

            seq.add_pulse('wait_for_ADwin', channel = chan_mwI, element = 'MBI_pulse'+str(i),
                start = 0, duration = wait_for_adwin_dur, amplitude = 0, start_reference = 'MBI_pulse',
                link_start_to = 'end', shape = 'rectangular')
        
        
            pulse_idx = 0
            #create element for each datapoint and link last element to first   
            el_name = 'Pi_over2_'+str(i+1)
            seq.add_element(name = el_name,trigger_wait = True)
            seq.add_pulse(name='first_wait', channel = chan_mwI, element = el_name,start = 0, 
                    duration = 960, amplitude = 0)
            seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
                start_reference = 'first_wait', link_start_to = 'end', start = 0, 
                duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')
            seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'Pi/2_pulse', link_start_to = 'start', 
                duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
                amplitude =2.0)

            seq.add_element(name='tau0'+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau0',channel=chan_mwI,element='tau0'+str(i+1),
                        start=0, duration=int(round((tau_sweep[i]*tau_len-750.)/tau_sweep[i])),
                        amplitude=0.)
        
            pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
            seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
            seq.add_pulse(name='wait',channel=chan_mwI,element=pulse_el_name,
                        start=0, duration=750-int(round((istate_pulse['duration']/2+pi['duration']/2))),amplitude=0)
            seq.add_pulse('pi' + str(1), channel = chan_mwI, element = pulse_el_name,
                    start = 0, duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular',
                    start_reference='wait',link_start_to='end')
            seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = pulse_el_name,
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pi' + str(1), link_start_to = 'start', 
                    duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
                    amplitude = 2.0)
            seq.add_pulse(name='wait2',channel=chan_mwI,element=pulse_el_name,
                        start=0, start_reference= 'pi' + str(1),link_start_to='end',
                        duration=750-int(round((pi['duration']/2))),amplitude=0)

            seq.add_element(name='tau1'+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau1',channel=chan_mwI,element='tau1'+str(i+1),
                        start=0, duration=int(round((tau_sweep[i]*tau_len-750.)/tau_sweep[i])),
                        amplitude=0.)

            pulse_idx+=1
            tau_idx=2
            for j in np.arange(1,pulse_nr-1):
                if np.mod(j,8) in [0,2,5,7]:
                    chan = chan_mwI
                    pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
                else:
                    chan = chan_mwQ
                    pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
                if np.mod(int(j/8),2) == 0:
                    do_min = 1
                else:
                    do_min=-1
                ## tau1
                cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
                seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=cur_el_name,
                        start=0,duration=int(round((tau_sweep[i]*tau_len-750.)/tau_sweep[i])),amplitude=0.)
                tau_idx+=1
    
                ## pi pulse
                seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
                
                seq.add_pulse(name='extra_wait'+str(j), channel = chan_mwI, 
                    element = pulse_el_name,start = 0, 
                    duration = 750.-int(round(pi["duration"]/2)), amplitude = 0)
                seq.add_pulse('pi' + str(j), channel = chan, element = pulse_el_name,
                    start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                    start_reference='extra_wait'+str(j),link_start_to='end')
                seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = pulse_el_name,
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pi' + str(j), link_start_to = 'start', 
                    duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)
                seq.add_pulse(name='extra_wait2'+str(j), channel = chan_mwI, 
                    element = pulse_el_name,start = 0,start_reference='pi'+str(j),link_start_to='end', 
                    duration = 750.-int(round(pi["duration"]/2)), amplitude = 0)
           
                pulse_idx+=1
            
            
                cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
                seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=cur_el_name,
                        start=0,duration=int(round((tau_sweep[i]*tau_len-750.)/tau_sweep[i])),amplitude=0.)
                tau_idx+=1
                    
            ##Final  elements
        
        
            seq.add_element(name='tau'+str(tau_idx)+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau',channel=chan_mwI,element='tau'+str(tau_idx)+str(i+1),
                        start=0, duration=int(round((tau_sweep[i]*tau_len-750.)/tau_sweep[i])),
                        amplitude=0.)
            tau_idx+=1
        
            if pulse_nr ==4:
                chan = chan_mwQ
                pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
            else:
                chan = chan_mwI
                pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
        
            seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
            seq.add_pulse(name='wait',channel=chan_mwI,element=pulse_el_name,
                        start=0, duration=750-int(round((pi['duration']/2))),amplitude=0)
            seq.add_pulse('pi' + str(1), channel = chan, element = pulse_el_name,
                    start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                    start_reference='wait',link_start_to='end')
            seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = pulse_el_name,
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pi' + str(1), link_start_to = 'start', 
                    duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
                    amplitude = 2.0)
            extra_wait_time=100
            seq.add_pulse(name='wait2',channel=chan_mwI,element=pulse_el_name,
                        start=0, start_reference= 'pi' + str(1),link_start_to='end',
                        duration=750-int(round((istate_pulse['duration']/2+pi['duration']/2)))-extra_wait_time,amplitude=0)
        
            seq.add_element(name='tau'+str(tau_idx)+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau',channel=chan_mwI,element='tau'+str(tau_idx)+str(i+1),
                        start=0, duration=int(round((tau_sweep[i]*tau_len-750.)/tau_sweep[i])),
                        amplitude=0.)
            tau_idx+=1

            # readout pulse
            el_name = 'readout'+str(i+1)
            if i == self.nr_of_datapoints-1:
     seq.add_pulse('RF', channel = chan_RF, element = 'spin_control'+str(i),
                    start = 0,start_reference=last,link_start_to='end', duration = self.RF_pulse_len[i],
                    amplitude = self.RF_pulse_amp[i],shape='sine',frequency=self.RF_freq[i],envelope='erf')
     """
