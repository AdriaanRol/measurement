"""
Class and script for characterizing SSRO with the Adwin

last version: 2013/01/02, Wolfgang
"""

import qt
import hdf5_data as h5
import numpy as np

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.AWG_HW_sequencer_v2 import Sequence


class AWGSSRO(m2.AdwinControlledMeasurement):

    mprefix = 'AWGSSRO'

    max_repetitions = 20000
    max_SP_bins = 500
    max_SSRO_dim = 1000000
    
    def __init__(self, name, adwin, awg):

        m2.AdwinControlledMeasurement.__init__(self, name, adwin)
        
        self.awg = awg
        self.seq = Sequence(name)
        self.adwin_process = 'singleshot_AWG'
        self.params['measurement_type'] = self.mprefix

    def autoconfig(self):
        self.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
        self.params['Ex_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.E_aom.get_pri_channel()]
        self.params['A_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.A_aom.get_pri_channel()]

    def setup(self):
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)
        
        self.E_aom.set_cur_controller('ADWIN')
        self.A_aom.set_cur_controller('ADWIN')
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)

        self.E_aom.set_cur_controller('AWG')
        self.E_aom.set_power(0.)
        self.params['AWG_Ex_RO_voltage'] = self.E_aom.power_to_voltage(
                self.params['Ex_RO_amplitude'])
        self.E_aom.set_cur_controller('ADWIN')

    def generate_sequence(self):
        awgcfg.configure_sequence(self.seq, 'adwin', 'light', 'picoharp')

        self.sequence()

        self.seq.set_instrument(self.awg)
        self.seq.set_clock(1e9)
        self.seq.set_send_waveforms(True)
        self.seq.set_send_sequence(True)
        self.seq.set_program_channels(True)
        self.seq.set_start_sequence(False)
        self.seq.force_HW_sequencing(True)
        self.seq.send_sequence()

    def sequence(self):
        ch_aom = 'velocity1aom'
        ch_apd = 'psbapdgate'
        ch_adwin = 'adwin_sync'
        ch_ph = 'PH_start'

        for i,t in enumerate(self.params['AWG_SSRO_durations']):
            elt = 'SSRO-'+str(i)
            
            if i == len(self.params['AWG_SSRO_durations'])-1:
                self.seq.add_element(elt, trigger_wait=True,
                        goto_target='SSRO-0')
            else:
                self.seq.add_element(elt, trigger_wait=True)

            self.seq.add_pulse('initial_wait', ch_ph, elt,
                    duration=10, amplitude=0., start=0)
            self.seq.add_pulse('ph_start', ch_ph, elt,
                    duration=10, amplitude=2.,
                    start=0,
                    start_reference='initial_wait',
                    link_start_to='end')
            
            self.seq.add_pulse('RO_wait', ch_aom, elt,
                    duration=10, amplitude=0., start=0,
                    start_reference='ph_start',
                    link_start_to='end')
            self.seq.add_pulse('APD_wait', ch_apd, elt,
                    duration=10, amplitude=0., start=0,
                    start_reference='ph_start',
                    link_start_to='end')
            
            self.seq.add_pulse('RO_pulse', ch_aom, elt,
                    duration=t,
                    amplitude=self.params['AWG_Ex_RO_voltage'],
                    start_reference='RO_wait',
                    link_start_to='end')
            self.seq.add_pulse('APD_off', ch_apd, elt,
                    duration=self.params['AWG_wait_for_Adwin_duration'],
                    amplitude=2.,
                    start=50,
                    start_reference='RO_pulse',
                    link_start_to='end')
            self.seq.add_pulse('Adwin_signal', ch_adwin, elt,
                    duration=self.params['AWG_wait_for_Adwin_duration'],
                    amplitude=2.,
                    start=50,
                    start_reference='RO_pulse',
                    link_start_to='end')
        
    
    def run(self):
        self.awg.set_runmode('SEQ')
        self.awg.start()

        while self.awg.get_state() != 'Waiting for trigger':
            print 'Waiting for AWG...'
            qt.msleep(1)
        
        # get adwin params
        for key,_val in adwins_cfg.config['adwin_lt1_processes']\
                ['singleshot_AWG']['params_long']:
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

        self.adwin_process_params['green_repump_voltage'] = \
                self.green_aom.power_to_voltage(
                        self.params['green_repump_amplitude'])

        self.adwin_process_params['green_off_voltage'] = 0.0
        
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort')
        
        CR_counts = 0
        while self.adwin_process_running():
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
            
            reps_completed = self.adwin_var('completed_reps')            
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, 
                        self.params['SSRO_repetitions'] * self.params['pts']))            
            qt.msleep(1)

        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, 
                    self.params['SSRO_repetitions'] * self.params['pts'] ))
        
    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', reps),
                    ('statistics', 10),
                    'completed_reps',
                    'total_CR_counts'])

    def finish(self):
        m2.AdwinControlledMeasurement.finish(self)

        self.awg.stop()
        self.awg.set_runmode('CONT')
        qt.instruments['counters'].set_is_running(True)
        self.green_aom.set_power(25e-6)
        
        self.E_aom.set_power(0)
        self.A_aom.set_power(0)

        self.E_aom.set_cur_controller('AWG')
        self.E_aom.set_power(0.)
        self.E_aom.set_cur_controller('ADWIN')
        self.E_aom.set_power(0)


def _prepare(m):
    m.green_aom = qt.instruments['GreenAOM']
    m.E_aom = qt.instruments['Velocity1AOM']
    m.A_aom = qt.instruments['Velocity2AOM']
    m.autoconfig()


def calibration(name):
    m = AWGSSRO(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)
    
    m.params['SSRO_repetitions'] = 5000
    m.params['CR_preselect'] = 40
    m.params['CR_probe'] = 40
    m.params['counter_channel'] = 1
    
    # laser powers
    m.params['A_SP_amplitude'] = 5e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 3e-9

    # adwin / awg interplay and timing
    m.params['AWG_wait_for_Adwin_duration'] = 10000
    m.params['wait_after_pulse_duration'] = 10
    
    # sweep settings
    m.params['AWG_SSRO_durations'] = np.arange(1,21).astype(int) * 200
    m.params['pts'] = len(m.params['AWG_SSRO_durations'])

    # go with ms = 0 calibration
    m.setup()
    m.generate_sequence()
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 3e-9

    m.run()
    m.save('ms1')

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    
    m.finish()

        

