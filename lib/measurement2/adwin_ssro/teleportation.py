"""
Class for the teleportation measurement, 
based on teleportation Adwin programme
"""
import numpy as np
import logging

import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
reload(adwins_cfg)

import measurement.lib.measurement2.measurement as m2
reload(m2)

from measurement.lib.AWG_HW_sequencer_v2 import Sequence

class Teleportation(m2.AdwinControlledMeasurement):

    mprefix = 'teleportation'
    max_successful_attempts = 10000 #after this the adwin stops, in CR debug mode
    max_red_hist_bins = 100
    max_yellow_hist_bins = 100
    adwin_process = 'teleportation'
    adwin_dict = adwins_cfg.config
    E_aom = None
    A_aom = None
    green_aom = None
    yellow_aom = None
    adwin = None

    def __init__(self, name):
        m2.AdwinControlledMeasurement.__init__(self, name)

    def autoconfig(self):
        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """
        self.params['Ex_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.E_aom.get_pri_channel()]
        self.params['A_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.A_aom.get_pri_channel()]
        self.params['yellow_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.yellow_aom.get_pri_channel()]
        self.params['green_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.green_aom.get_pri_channel()]         
        # self.params['gate_DAC_channel'] = self.adwin.get_dac_channels()\
        #        ['gate']

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """
        
        self.yellow_aom.set_power(0.)
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)
        self.yellow_aom.set_cur_controller('ADWIN')
        self.green_aom.set_cur_controller('ADWIN')
        self.E_aom.set_cur_controller('ADWIN')
        self.A_aom.set_cur_controller('ADWIN')
        self.yellow_aom.set_power(0.)
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)  

    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()
            
        for key,_val in self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['params_long']:
            try:
                self.adwin_process_params[key] = self.params[key]
            except:
                logging.error("Cannot set adwin process variable '%s'" \
                        % key)
                return False

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
                       
        self.adwin_process_params['yellow_repump_voltage'] = \
                self.yellow_aom.power_to_voltage(
                        self.params['yellow_repump_amplitude'])

        self.adwin_process_params['green_repump_voltage'] = \
                self.green_aom.power_to_voltage(
                        self.params['green_repump_amplitude'])
                
        self.adwin_process_params['yellow_off_voltage'] = \
                self.params['yellow_off_voltage']
        self.adwin_process_params['green_off_voltage'] = \
                self.params['green_off_voltage']
        self.adwin_process_params['A_off_voltage'] = \
                self.params['A_off_voltage']
        self.adwin_process_params['Ex_off_voltage'] = \
                self.params['Ex_off_voltage']

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
            
            print('completed %s / %s teleportation events' % \
                    (reps_completed, self.params['teleportation_repetitions']))
            # print('threshold: %s cts, last CR check: %s cts' % (trh, cts))
            
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s teleportation events' % \
                (reps_completed, self.params['teleportation_repetitions']))

    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_hist_time_out', self.max_red_hist_bins),
                    ('CR_hist_all', self.max_red_hist_bins),
                    ('CR_hist_yellow_time_out', self.max_yellow_hist_bins),
                    ('CR_hist_yellow_all', self.max_yellow_hist_bins),
                    ('CR_after', reps),
                    'completed_reps',
                    'total_red_CR_counts'])
        
    def finish(self, save_params=True, save_stack=True, 
            stack_depth=4, save_cfg=True, save_ins_settings=True):
               
        if save_params:
            self.save_params()
            
        if save_stack:
            self.save_stack(depth=stack_depth)
            
        if save_ins_settings:
            self.save_instrument_settings_file()
            
        qt.instruments['counters'].set_is_running(True)
        self.yellow_aom.set_power(0)
        self.green_aom.set_power(0)
        self.E_aom.set_power(0)
        self.A_aom.set_power(0)
            
        m2.AdwinControlledMeasurement.finish(self)