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


def calibration(name, mode=''):
    m = AdwinSSRO(name+mode, qt.instruments['adwin'])
    m.green_aom = qt.instruments['GreenAOM']
    m.yellow_aom = qt.instruments['YellowAOM']
    m.E_aom = qt.instruments['Velocity2AOM']
    m.A_aom = qt.instruments['Velocity1AOM']
    
    m.setup()
    
    if mode=='yellow_only':
        #then just pretend green is yellow
        m.green_aom = m.yellow_aom
        m.params['green_repump_amplitude'] = m.params['yellow_repump_amplitude'] 
        m.params['green_repump_duration'] = m.params['yellow_repump_duration']
        m.params['green_laser_DAC_channel'] = m.params['yellow_laser_DAC_channel']
        qt.instruments['GreenAOM'].set_power(0)
    elif mode=='double_repump':
        #then use the double repump
        m.params['green_repump_duration'] = 200
        m.params['green_after_yellow_failed'] = 10 
        
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration'] = 50 
    m.params['CR_preselect'] = 40
    m.params['CR_probe'] =  40
    m.params['counter_channel'] = 1
    m.params['Ex_CR_amplitude'] = 10e-9
    m.params['A_CR_amplitude'] = 10e-9#500e-9

    # ms = 0 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 5e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_RO_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 5e-9
    

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 5e-9
    m.params['A_RO_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 5e-9

    m.run()
    m.save('ms1')

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    m.save_intrument_settings_file()
    
    m.finish()

        
#### script section
# calibration('SIL9')

