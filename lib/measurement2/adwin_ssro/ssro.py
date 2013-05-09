"""
Class for characterizing SSRO with the Adwin

last version: 2013/01/02, Wolfgang
"""
import numpy as np

import qt
import hdf5_data as h5
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

class AdwinSSRO(m2.AdwinControlledMeasurement):

    mprefix = 'AdwinSSRO'
    max_repetitions = 20000
    max_SP_bins = 500
    max_SSRO_dim = 1000000
	adwin_process = 'singleshot'
    adwin_dict = adwins_cfg.config
    adwin_processes_key = ''
    E_aom = None
    A_aom = None
    green_aom = None
    yellow_aom = None
    
    def __init__(self, name, adwin):
        m2.AdwinControlledMeasurement.__init__(self, name, adwin)

    def setup(self):
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)

        self.params['Ex_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.E_aom.get_pri_channel()]
        self.params['A_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.A_aom.get_pri_channel()]
        self.params['green_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.green_aom.get_pri_channel()]
        self.params['yellow_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.yellow_aom.get_pri_channel()]
        self.params['gate_DAC_channel'] = self.adwin.get_dac_channels()\
                ['gate']        
    
    def run(self):
        for key,_val in self.adwins_dict[self.adwin_processes_key]\
                [self.adwin_process]['params_long']:
            self.adwin_process_params[key] = self.params[key]

        for key in self.params.parameters:
            self.adwin_process_params[key] = self.params[key]

        self.adwin_process_params['Ex_CR_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_CR_amplitude'])
        
        self.adwin_process_params['A_CR_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_CR_amplitude'])

        self.adwin_process_params['Ex_SP_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_SP_amplitude'])

        self.adwin_process_params['A_SP_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_SP_amplitude'])

        self.adwin_process_params['Ex_RO_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_RO_amplitude'])

        self.adwin_process_params['A_RO_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_RO_amplitude'])

        self.adwin_process_params['green_repump_voltage'] = \
                self.green_aom.power_to_voltage(
                        self.params['green_repump_amplitude'])
        
        self.adwin_process_params['yellow_repump_voltage'] = \
                self.yellow_aom.power_to_voltage(
                        self.params['yellow_repump_amplitude'])
        
        self.adwin_process_params['green_off_voltage'] = 0.0
        
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
        
        CR_counts = 0
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
            
            reps_completed = self.adwin_var('completed_reps')
            CR_counts = self.adwin_var('total_CR_counts') - CR_counts
            cts = self.adwin_var('last_CR_counts')
            trh = self.adwin_var('CR_threshold')
            
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['SSRO_repetitions']))
            # print('threshold: %s cts, last CR check: %s cts' % (trh, cts))
            
            qt.msleep(1)

        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))
        
    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', reps * self.params['SSRO_duration']),
                    ('statistics', 10),
                    'completed_reps',
                    'total_CR_counts',
                    'CR_threshold',
                    'last_CR_counts' ])

    def finish(self):
        m2.AdwinControlledMeasurement.finish(self)

class AdwinSSROAlternCR(AdwinSSRO):
   
    adwin_process = 'singleshot_altern_CR'

    def __init__(self, name, adwin):
        AdwinSSRO.__init__(self, name, adwin)
