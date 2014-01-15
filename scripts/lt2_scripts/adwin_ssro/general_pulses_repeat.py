"""
Class and script for doing repetitive pulse sequences with the Adwin.
- Records a histogram of one of the elements
- stores counts or each element for each repetition 
- stores the arrival time of the first count one of the elements for each repetition 

last version: 2013/04/22, Bas
"""
import numpy as np

import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

class AdwinPulsesRepeat(m2.AdwinControlledMeasurement):
    #Hardcoded adwin stuff, change there simultaniously if neccesary. 
    MAX_ELEMENTS=10 #maximum number of different pulse/counting combinations: hardcoded in adwin
    MAX_HISTOGRAM_LENGTH=1000 #maximum length of timed histogram in cycles: hardcoded in adwin
    MAX_REPETITIONS=100000 #maximum number of repetitions allowed: hardcoded in adwin
    
    
    def __init__(self, name, adwin):

        m2.AdwinControlledMeasurement.__init__(self, name)
        self.adwin=adwin

        self.adwin_process = 'general_pulses_repeat'
        
      
    def setup(self):
        pass
    
    def run(self):
        
        # set adwin params
        for key,_val in adwins_cfg.config['adwin_lt2_processes']\
                [self.adwin_process]['params_long']:
            self.adwin_process_params[key] = self.params[key]
        
        for key in adwins_cfg.config['adwin_lt2_processes']\
                [self.adwin_process]['data_float']:
            self.adwin_process_params[key] = self.params[key]
            
        data_long_keys=['counter_on','element_durations']
        for key in data_long_keys:
            self.adwin_process_params[key] = self.params[key]
        
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
        
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
            
            reps_completed = self.adwin_var('repetition_counter')  
            print 'reps completed', reps_completed
            
            qt.msleep(1)

        self.stop_adwin_process()
        self.reps_completed = self.adwin_var('repetition_counter')
        total_counts = self.adwin_var('total_counts')
        print('completed %s repetitions, total counts: %s' % \
                (reps_completed,total_counts))

    def save(self, name='pulses'):
        #print 'results', self.params['max_element']*self.params['max_sweep']
        #print 'histogram', self.MAX_COUNTS*self.params['max_sweep']
        #print 'counts', self.params['max_element']
        self.save_adwin_data(name,
                [   ('results', int(self.params['max_element']*self.reps_completed)),
                    ('histogram', int(self.params['element_durations'][self.params['timed_element']-1]*self.reps_completed)),
                    ('first_count', int(self.reps_completed)),
                    'repetition_counter'])
        print 'saving done'

                    
    def finish(self):
        m2.AdwinControlledMeasurement.finish(self)
          
        
def yellow_pumping(name):
    m = AdwinPulsesRepeat(name, qt.instruments['adwin'])
    
    m.protocol_name='yellow_pumping'
    
    m.setup()
    
    
    m.yellow_aom=qt.instruments['YellowAOM']#TODO
    m.yellow_aom.set_cur_controller('ADWIN')
    m.a_aom=qt.instruments['MatisseAOM']
    m.ex_aom=qt.instruments['NewfocusAOM']
    
    m.params['counter_channel']     = 1

    m.params['dac1_channel']        = m.adwin.get_dac_channels()[m.yellow_aom.get_pri_channel()]
    m.params['dac2_channel']        = m.adwin.get_dac_channels()[m.ex_aom.get_pri_channel()]
    m.params['dac3_channel']        = m.adwin.get_dac_channels()[m.a_aom.get_pri_channel()]
    m.params['cycle_duration']      = 100*300 #us*3.3ns
    m.params['wait_after_pulse_duration'] = 1
    
    m.params['max_element']         = 2 
       
    m.params['timed_element']       = 2
   
    m.params['max_repetitions']    = 10000 
    
    yellow_voltages  = 'dac1_voltages'
    ex_voltages      = 'dac2_voltages'
    a_voltages      = 'dac3_voltages'
    
    #initiialize arrays
    m.params[yellow_voltages]       =  np.zeros(m.params['max_element'])
    m.params[ex_voltages]           =  np.zeros(m.params['max_element'])
    m.params[a_voltages]            =  np.zeros(m.params['max_element'])
    
    
    m.params['counter_on']          = np.ones(m.params['max_element'], dtype=np.int32)
    m.params['element_durations']   = np.ones(m.params['max_element'], dtype=np.int32)
    
    
    
    #define voltages
    m.params['ex_amplitude']        = 80e-9#XX
    m.params['a_amplitude']         = 200e-9#XX
    m.params['yellow_amplitude']    = 100e-9#XX
    m.params['ex_voltage']          = m.ex_aom.power_to_voltage(m.params['ex_amplitude'])
    m.params['a_voltage']           = m.a_aom.power_to_voltage(m.params['a_amplitude'])
    m.params['yellow_voltage']      = m.yellow_aom.power_to_voltage(m.params['yellow_amplitude'])
    
    ###############define sequence#################
  
    #element 1
    i=0
    m.params[yellow_voltages][i]    = 0
    m.params[ex_voltages][i]        = m.params['ex_voltage'] 
    m.params[a_voltages][i]         = m.params['a_voltage'] 
    m.params['counter_on'][i]       = 0
    m.params['element_durations'][i]= 100
    
    #element  2 
    i=1
    m.params[yellow_voltages][i]    = m.params['yellow_voltage']
    m.params[ex_voltages][i]        = 0
    m.params[a_voltages][i]         = 0
    m.params['counter_on'][i]       = 1
    m.params['element_durations'][i]= 100
       
    m.run()
    m.save()

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    m.save_instrument_settings_file()
    
    m.finish()

    
    
    
    