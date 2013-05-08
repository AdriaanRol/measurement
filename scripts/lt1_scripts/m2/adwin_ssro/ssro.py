"""
Class and script for characterizing SSRO with the Adwin

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
    
    def __init__(self, name, adwin):
        m2.AdwinControlledMeasurement.__init__(self, name, adwin)
        self.adwin_process = 'singleshot'

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
        for key,_val in adwins_cfg.config['adwin_lt1_processes']\
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

class AdwinSSROAlternCR(AdwinSSRO):
    def __init__(self, name, adwin):
        AdwinSSRO.__init__(self, name, adwin)

        self.adwin_process = 'singleshot_altern_CR'


def RO_saturation(name):
    m = AdwinSSRO('RO_saturation_power_'+name, qt.instruments['adwin'])
    m.green_aom = qt.instruments['GreenAOM']
    m.yellow_aom = qt.instruments['YellowAOM']
    m.E_aom = qt.instruments['Velocity2AOM']
    m.A_aom = qt.instruments['Velocity1AOM']

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.setup()

    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitudes'] = np.arange(20)*1e-9 + 1e-9

    for p in m.params['Ex_RO_amplitudes']:
        m.params['Ex_RO_amplitude'] = p
        m.run()
        m.save('P_%dnW' % (p*1e9))

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    m.save_instrument_settings_file()
    
    m.finish()

def SP_vs_power(name):
    CRmode = 'altern_CR' # 'altern_CR' # (options: 'altern_CR' or anything else for regular)
    
    if CRmode == 'altern_CR':
        m = AdwinSSROAlternCR(name, qt.instruments['adwin'])
    else:
        m = AdwinSSRO(name, qt.instruments['adwin'])

    m.green_aom = qt.instruments['GreenAOM']
    m.yellow_aom = qt.instruments['YellowAOM']
    m.E_aom = qt.instruments['Velocity2AOM']
    m.A_aom = qt.instruments['Velocity1AOM']
    m.setup()

    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration'] = 50
    m.params['CR_preselect'] = 25
    m.params['CR_probe'] = 25
    m.params['counter_channel'] = 1
    m.params['Ex_CR_amplitude'] = 15e-9 #20e-9 #30e-9
    m.params['A_CR_amplitude'] = 50e-9 #200e-9  #500e-9

    # needed only for altern CR checking
    m.params['CR_pump_duration'] = 10
    m.params['CR_probe_duration'] = 10
    m.params['CR_prepump_duration'] = 100
    m.params['CR_pp_cycles'] = 5

    m.params['SP_duration'] = 10 # we'll measure the SP fidelity at a given pump time
    m.params['A_RO_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 7e-9 #10e-9

    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_SP_amplitudes'] = np.arange(10)*5e-9

    for p in m.params['A_SP_amplitudes']:
        m.params['A_SP_amplitude'] = p
        m.run()
        m.save('P_%dnW' % (p*1e9))

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    # m.save_intrument_settings_file()
    
    m.finish()
    


def calibration(name, mode=''):
    CRmode = '' #'altern_CR' # (options: 'altern_CR' or anything else for regular)
    
    if CRmode == 'altern_CR':
        m = AdwinSSROAlternCR(name+mode, qt.instruments['adwin'])
    else:
        m = AdwinSSRO(name+mode, qt.instruments['adwin'])
    
    m.green_aom = qt.instruments['GreenAOM']
    m.yellow_aom = qt.instruments['YellowAOM']
    m.E_aom = qt.instruments['Velocity2AOM']
    m.A_aom = qt.instruments['Velocity1AOM']

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    
    m.setup()
    
#     if mode=='yellow_only':
#         #then just pretend green is yellow
#         m.green_aom = m.yellow_aom
#         m.params['green_repump_amplitude'] = m.params['yellow_repump_amplitude'] 
#         m.params['green_repump_duration'] = m.params['yellow_repump_duration']
#         m.params['green_laser_DAC_channel'] = m.params['yellow_laser_DAC_channel']
#         qt.instruments['GreenAOM'].set_power(0)
#     
#     elif mode=='double_repump':
#         #then use the double repump
#         m.params['green_repump_duration'] = 200
#         m.params['green_after_yellow_failed'] = 10
        
    m.params['Ex_CR_amplitude'] = 10e-9 #20e-9 #30e-9
    m.params['A_CR_amplitude'] = 10e-9 #200e-9  #500e-9
    m.params['Ex_RO_amplitude'] = 2e-9 #10e-9
    
    # needed only for altern CR checking
    # m.params['CR_pump_duration'] = 10
    # m.params['CR_probe_duration'] = 10
    # m.params['CR_prepump_duration'] = 100
    # m.params['CR_pp_cycles'] = 5

    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 5e-9 #10e-9

    m.run()
    m.save('ms1')

    m.save_params()
    m.save_stack()
    m.save_cfg_files()
    m.save_instrument_settings_file()
    
    m.finish()

        
#### script section
# calibration('SIL9')

