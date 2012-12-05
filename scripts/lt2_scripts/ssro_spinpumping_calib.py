import qt
import numpy as np
import msvcrt
from measurement.measurement import Measurement
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels_lt2 as awgcfg
from measurement.sequence import common as commonseq

class SpinPumping(Measurement):

    def __init__(self,name):
        Measurement.__init__(self,name,mclass='SpinPumping')
        
        self.max_SP_bins = 500
        self.max_RO_dim = 1000000

        self.set_phase_locking_on = 1
        self.set_gate_good_phase = -1
        
        self.par = {}
        
        self.par['AWG_start_DO_channel'] =         1
        self.par['AWG_done_DI_channel'] =          8
        self.par['send_AWG_start'] =               1
        self.par['wait_for_AWG_done'] =            0
        self.par['green_repump_duration'] =        10
        self.par['CR_duration'] =                  60 #NOTE set to 60 for Ey,A1
        self.par['SP_duration'] =                  250 # NOTE set to 50 for Ey, A1
        self.par['SP_filter_duration'] =           0
        self.par['sequence_wait_time'] =           int(np.ceil(1e-3)+2)
        self.par['wait_after_pulse_duration'] =    1
        self.par['CR_preselect'] =                 1000

        self.par['reps_per_datapoint'] =           1500
        self.par['sweep_length'] =                 int(21)
        self.par['RO_repetitions'] =               int(21*1000)
        self.par['RO_duration'] =                  9

        self.par['cycle_duration'] =               300
        self.par['CR_probe'] =                     100

        self.par['green_repump_amplitude'] =       200e-6
        self.par['green_off_amplitude'] =          0e-6
        self.par['Ex_CR_amplitude'] =              15e-9 #OK
        self.par['A_CR_amplitude'] =               20e-9 # NOTE set to 15e-9 for Ey,A1
        self.par['Ex_SP_amplitude'] =              5e-9 
        self.par['A_SP_amplitude'] =               0e-9 #OK: PREPARE IN MS = 0
        self.par['Ex_RO_amplitude'] =              5e-9 #OK: READOUT MS = 0
        self.par['A_RO_amplitude'] =               0e-9

        self.par['min_sweep_par'] =                  0
        self.par['max_sweep_par'] =                  1
        self.par['sweep_par_name'] =                 ''
        self.par['sweep_par']   =                  np.linspace(1,21,21)

    def setup(self,lt1=False):

        if lt1:
            self.ins_green_aom=qt.instruments['GreenAOM_lt1']
            self.ins_E_aom=qt.instruments['MatisseAOM_lt1']
            self.ins_A_aom=qt.instruments['NewfocusAOM_lt1']
            self.adwin=qt.instruments['adwin_lt1']
            self.counters=qt.instruments['counters_lt1']
            self.physical_adwin=qt.instruments['physical_adwin_lt1']
            self.ctr_channel=2
            self.adwin_lt2=qt.instruments['adwin']
        else:
            self.ins_green_aom=qt.instruments['GreenAOM']
            self.ins_E_aom=qt.instruments['MatisseAOM']
            self.ins_A_aom=qt.instruments['NewfocusAOM']
            self.adwin=qt.instruments['adwin']
            self.counters=qt.instruments['counters']
            self.physical_adwin=qt.instruments['physical_adwin']
            self.ctr_channel=1

        self.awg = qt.instruments['AWG']
        
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

    def start_measurement(self,generate_sequence,lt1=False,ssro_dict={}):
       
        self.counters.set_is_running(False)
        
        #Generate sequence and send to AWG
        sequence = generate_sequence(self.par['sweep_par'])

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

        qt.msleep(1)

        self.spin_control(lt1,ssro_dict=ssro_dict)
        self.end_measurement()

    def spin_control(self,lt1,ssro_dict={}):
        self.par['green_repump_voltage'] = self.ins_green_aom.power_to_voltage(self.par['green_repump_amplitude'])
        self.par['green_off_voltage'] = 0.08#self.ins_green_aom.power_to_voltage(self.par['green_off_amplitude'])
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
        self.ins_E_aom.set_power(0)
        self.ins_A_aom.set_power(0)


def SP_seq(sweep_param, SP_duration = 40000, do_program=True):
    '''
    This sequence consists of single pulse on the Newfocus AW|G channel
                }
    '''
    awg = qt.instruments['AWG']
    seq = Sequence('spinpumping')
    awgcfg.configure_sequence(seq,'optical_rabi','hydraharp')
    
    # vars for the channel names
    chan_hhsync = 'HH_sync'         # historically PH_start
    chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
      
    chan_alaser = 'AOM_Newfocus'

    nr_of_datapoints = len(sweep_param)
    
   
    for i in np.arange(nr_of_datapoints):
       
        #create element for each datapoint and link last element to first   
        el_name = 'spinpumping'+str(i+1)
        if i == nr_of_datapoints-1:
            target= 'spinpumping'+str(1)
        else:
            target='none'
        
        seq.add_element(name = el_name, 
            trigger_wait = True, goto_target=target)

        seq.add_pulse('debug_sync',  chan_hhsync, el_name,         
                    start = 0, duration = 50, 
                    amplitude = 2.0)
        
        seq.add_pulse('initialdelay', chan_alaser, el_name,
                start = 0, duration = 500, amplitude=0, )
        
        seq.add_pulse('spinpumping', chan_alaser, el_name, 
                start = 0, duration = SP_duration,
                start_reference='initialdelay',
                link_start_to='end', amplitude=sweep_param[i])
        seq.add_pulse('singletdelay', chan_alaser, el_name,
                start = 0, duration = 1000, start_reference='spinpumping',
                link_start_to='end', amplitude=0, )
        seq.add_pulse('singletpumping', chan_alaser, el_name,
                start = 0, duration = 10000, start_reference='singletdelay',
                link_start_to='end', amplitude=sweep_param[i])
        seq.add_pulse('finaldelay', chan_alaser, el_name,
                start = 0, duration = 500, start_reference='singletpumping',
                link_start_to='end', amplitude=0, )

        
    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()

    name= 'spinpumping'
    return {"seqname":name, "max_seq_time":max_seq_time}

    



def main(lt1=False, name='spinpumping', ssro_dict={}):
    m = SpinPumping(name)
    m.setup(lt1)

    
    
    nr_of_datapoints=1
    sp_min_power=15e-9
    #sp_max_power=30e-9
    m.ins_A_aom.set_cur_controller('AWG')
    sp_min_amp=m.ins_A_aom.power_to_voltage(sp_min_power)
    #sp_max_amp=m.ins_A_aom.power_to_voltage(sp_max_power)
    m.ins_A_aom.set_cur_controller('ADWIN')
    #sp_amp=np.linspace(sp_min_amp,sp_max_amp,nr_of_datapoints)
    sp_amp=np.array([sp_min_amp])
    m.par['sweep_par_name'] = 'SP_power'
    m.par['fe_max'] = sp_min_power
    m.par['fe_min'] = sp_min_power
    m.par['sweep_par'] = sp_amp
    m.par['sweep_length'] = len(sp_amp)
    #m.par['RO_duration'] = 26
    m.par['Ex_RO_amplitude'] = 12e-9
    m.par['reps_per_datapoint'] = 100000

    m.start_measurement(SP_seq,lt1=lt1,ssro_dict=ssro_dict)

if __name__ == '__main__':
    main(lt1=False)
