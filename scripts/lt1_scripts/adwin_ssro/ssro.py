"""
Class and script for characterizing SSRO with the Adwin

last version: 2013/01/02, Wolfgang
"""

import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2



class AdwinSSRO(m2.AdwinControlledMeasurement):

    mprefix = 'AdwinSSRO'

    max_repetitions = 20000
    max_SP_bins = 500
    max_SSRO_dim = 1000000
    
    def __init__(self, name, adwin):

        m2.AdwinControlledMeasurement.__init__(self, name, adwin)

        self.adwin_process = 'singleshot'

    def setup(self):
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)

        self.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    
    def run(self):
        
        # get adwin params
        for key,_val in adwins_cfg.config['adwin_lt1_processes']\
                ['singleshot']['params_long']:
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
            CR_counts = self.adwin_var('total_CR_counts') - CR_counts
            cts = self.adwin_var('last_CR_counts')
            trh = self.adwin_var('CR_threshold')
            
            print('completed %s / %s readout repetitions, %s CR counts/s' % \
                    (reps_completed, self.params['SSRO_repetitions'], CR_counts))
            print('threshold: %s cts, last CR check: %s cts' % (trh, cts))
            
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


def calibration(name):
    m = AdwinSSRO(name, qt.instruments['adwin'])
    m.green_aom = qt.instruments['GreenAOM']
    m.E_aom = qt.instruments['MatisseAOM']
    m.A_aom = qt.instruments['NewfocusAOM']
    
    m.setup()
    
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration'] = 100
    m.params['CR_preselect'] = 30
    m.params['CR_probe'] = 30
    
    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 5e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_RO_amplitude'] = 0.
    m.params['Ex_RO_ampltude'] = 3e-9    
    
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 3e-9
    m.params['A_RO_amplitude'] = 0.
    m.params['Ex_RO_ampltude'] = 3e-9

    m.run()
    m.save('ms1')

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    
    m.finish()

        
#### script section
calibration('SIL3')

