"""
This script runs the measurement from the LT2 computer. All adwin programming
and data handling is done here.

Before running in a mode that requires both AWGs, the Slave script
on LT1 needs to be run first!
"""


import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import parameters as tparams
reload(tparams)

import sequence as tseq
reload(tseq)

### CONSTANTS

# ADWIN LT1:
#DEFINE max_repetitions         10000          ' the maximum number of datapoints taken
#DEFINE max_red_hist_cts        100            ' dimension of photon counts histogram for red CR
#DEFINE max_yellow_hist_cts     100            ' dimension of photon counts histogram for yellow Resonance check
#DEFINE max_statistics          15
ADWINLT1_MAX_REPS = 10000
ADWINLT1_MAX_RED_HIST_CTS = 100
ADWINLT1_MAX_YELLOW_HIST_CTS = 100
ADWINLT1_MAX_STAT = 15

#DEFINE max_repetitions   20000
#DEFINE max_CR_hist_bins    100
#DEFINE max_stat             10
ADWINLT2_MAX_REPS = 20000
ADWINLT2_MAX_CR_HIST_CTS = 100
ADWINLT2_MAX_STAT = 10


### CODE
class TeleportationMaster(m2.MultipleAdwinsMeasurement):

    mprefix = 'Teleportation'

    def __init__(self, name):
        m2.MultipleAdwinsMeasurement.__init__(self, name)

        self.params_lt1 = m2.MeasurementParameters('LT1Parameters')
        self.params_lt2 = m2.MeasurementParameters('LT2Parameters')

    ### setting up
    def load_settings(self):
        for k in tparams.params.parameters:
            self.params[k] = tparams.params[k]

        for k in tparams.params_lt1.parameters:
            self.params_lt1[k] = tparams.params_lt1[k]
        
        for k in tparams.params_lt2.parameters:
            self.params_lt2[k] = tparams.params_lt2[k]
    
    def update_definitions(self):
        """
        After setting the measurement parameters, execute this function to
        update pulses, etc.
        """
        # tseq.pulse_defs_lt2(self)

    def autoconfig(self, use_lt1=True, use_lt2=True):
        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """

        if use_lt1:
            self.params_lt1['Ey_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                    [self.Ey_aom_lt1.get_pri_channel()]
            self.params_lt1['FT_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                    [self.FT_aom_lt1.get_pri_channel()]
            self.params_lt1['yellow_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                    [self.yellow_aom_lt1.get_pri_channel()]
            self.params_lt1['green_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                    [self.green_aom_lt1.get_pri_channel()]
            # self.params['gate_DAC_channel'] = self.adwin.get_dac_channels()\
            #        ['gate']
                 
            if self.params_lt1['use_yellow']:
                self.params_lt1['repump_laser_DAC_channel'] = self.params_lt1['yellow_laser_DAC_channel']
            else:
                self.params_lt1['repump_laser_DAC_channel'] = self.params_lt1['green_laser_DAC_channel']

            self.params_lt1['Ey_CR_voltage'] = \
                    self.Ey_aom_lt1.power_to_voltage(
                            self.params_lt1['Ey_CR_amplitude'])
            self.params_lt1['FT_CR_voltage'] = \
                    self.FT_aom_lt1.power_to_voltage(
                            self.params_lt1['FT_CR_amplitude'])

            self.params_lt1['Ey_SP_voltage'] = \
                    self.Ey_aom_lt1.power_to_voltage(
                            self.params_lt1['Ey_SP_amplitude'])
            self.params_lt1['FT_SP_voltage'] = \
                    self.FT_aom_lt1.power_to_voltage(
                            self.params_lt1['FT_SP_amplitude'])

            self.params_lt1['Ey_RO_voltage'] = \
                    self.Ey_aom_lt1.power_to_voltage(
                            self.params_lt1['Ey_RO_amplitude'])
            self.params_lt1['FT_RO_voltage'] = \
                    self.FT_aom_lt1.power_to_voltage(
                            self.params_lt1['FT_RO_amplitude'])
                           
            self.params_lt1['repump_voltage'] = \
                    self.repump_aom_lt1.power_to_voltage(
                            self.params_lt1['repump_amplitude'])

        if use_lt2:
            self.params_lt2['Ey_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                    [self.Ey_aom_lt2.get_pri_channel()]
            self.params_lt2['A_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                    [self.A_aom_lt2.get_pri_channel()]
            self.params_lt2['green_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                   [self.green_aom_lt2.get_pri_channel()]

            self.params_lt2['repump_laser_DAC_channel'] = self.params_lt2['green_laser_DAC_channel']

            self.params_lt2['Ey_CR_voltage'] = \
                    self.Ey_aom_lt2.power_to_voltage(
                            self.params_lt2['Ey_CR_amplitude'])
            self.params_lt2['A_CR_voltage'] = \
                    self.A_aom_lt2.power_to_voltage(
                            self.params_lt2['A_CR_amplitude'])

            self.params_lt2['Ey_SP_voltage'] = \
                    self.Ey_aom_lt2.power_to_voltage(
                            self.params_lt2['Ey_SP_amplitude'])
            self.params_lt2['A_SP_voltage'] = \
                    self.A_aom_lt2.power_to_voltage(
                            self.params_lt2['A_SP_amplitude'])

            self.params_lt2['Ey_RO_voltage'] = \
                    self.Ey_aom_lt2.power_to_voltage(
                            self.params_lt2['Ey_RO_amplitude'])
            self.params_lt2['A_RO_voltage'] = \
                    self.A_aom_lt2.power_to_voltage(
                            self.params_lt2['A_RO_amplitude'])
                           
            self.params_lt2['repump_voltage'] = \
                    self.repump_aom_lt2.power_to_voltage(
                            self.params_lt2['repump_amplitude'])

    def setup(self, use_lt1 = True, use_lt2 = True):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """        
        if use_lt1:
            self.yellow_aom_lt1.set_power(0.)
            self.green_aom_lt1.set_power(0.)
            self.Ey_aom_lt1.set_power(0.)
            self.FT_aom_lt1.set_power(0.)
            self.yellow_aom_lt1.set_cur_controller('ADWIN')
            self.green_aom_lt1.set_cur_controller('ADWIN')
            self.Ey_aom_lt1.set_cur_controller('ADWIN')
            self.FT_aom_lt1.set_cur_controller('ADWIN')
            self.yellow_aom_lt1.set_power(0.)
            self.green_aom_lt1.set_power(0.)
            self.Ey_aom_lt1.set_power(0.)
            self.FT_aom_lt1.set_power(0.)

            #self.mwsrc_lt1.set_iq('on')                # NOT USING MW YET
            #self.mwsrc_lt1.set_pulm('on')
            #self.mwsrc_lt1.set_frequency(self.params_lt1['mw_frq'])
            #self.mwsrc_lt1.set_power(self.params_lt1['mw_power'])
            #self.mwsrc_lt1.set_status('on')

        if use_lt2:
            self.green_aom_lt2.set_power(0.)
            self.Ey_aom_lt2.set_power(0.)
            self.A_aom_lt2.set_power(0.)
            self.green_aom_lt2.set_cur_controller('ADWIN')
            self.Ey_aom_lt2.set_cur_controller('ADWIN')
            self.A_aom_lt2.set_cur_controller('ADWIN')
            self.green_aom_lt2.set_power(0.)
            self.Ey_aom_lt2.set_power(0.)
            self.A_aom_lt2.set_power(0.)

            #self.mwsrc_lt2.set_iq('on')                 # NOT USING MW YET
            #self.mwsrc_lt2.set_pulm('on')
            #self.mwsrc_lt2.set_frequency(self.params_lt2['mw_frq'])
            #self.mwsrc_lt2.set_power(self.params_lt2['mw_power'])
            #self.mwsrc_lt2.set_status('on')
            
            # self.awg_lt2.set_runmode('SEQ')

    def lt2_sequence(self):     
        self.lt2_seq = pulsar.Sequence('TeleportationLT2')

    ### Start and program adwins; Process control
    def _auto_adwin_params(self, adwin):
        for key,_val in self.adwin_dict['{}_processes'.format(adwin)]\
            [self.adwins[adwin]['process']]['params_long']:
            try:
                self.adwin_process_params[adwin][key] = \
                    self.params_lt1[key] if adwin == 'adwin_lt1' else self.params_lt2[key]
            except:
                logging.error("Cannot set {} process variable '{}'".format(adwin, key))
                return False

        for key,_val in self.adwin_dict['{}_processes'.format(adwin)]\
            [self.adwins[adwin]['process']]['params_float']:
            try:
                self.adwin_process_params[adwin][key] = \
                    self.params_lt1[key] if adwin == 'adwin_lt1' else self.params_lt2[key]
            except:
                logging.error("Cannot set {} process variable '{}'".format(adwin, key))
                return False

    def start_lt1_process(self):
        self._auto_adwin_params('adwin_lt1')
        self.start_adwin_process('adwin_lt1', stop_processes=['counter'])

    def start_lt2_process(self):
        self._auto_adwin_params('adwin_lt2')
        self.start_adwin_process('adwin_lt2', stop_processes=['counter'])

    def start(self, use_lt1=True, use_lt2=True):
        self.autoconfig(use_lt1,use_lt2)
        if use_lt2:
            self.start_lt2_process()
            qt.msleep(1)
        if use_lt1:
            self.start_lt1_process()
            qt.msleep(1)

        self.start_keystroke_monitor('abort',timer=False)
        
        running = True
        while running:
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
            if use_lt2 and use_lt1:
                running = self.adwin_process_running('adwin_lt1') and self.adwin_process_running('adwin_lt2')
            elif use_lt2 and not use_lt1:
                running = self.adwin_process_running('adwin_lt2')
            elif use_lt1 and not use_lt2:
                running = self.adwin_process_running('adwin_lt1')
            qt.msleep(1)

    def stop(self, use_lt1=True, use_lt2=True):
        if use_lt1:
            self.stop_adwin_process('adwin_lt1')
        if use_lt2:
            self.stop_adwin_process('adwin_lt2')
        qt.msleep(1)

    def save(self, use_lt1=True, use_lt2=True):
        if use_lt1:
            reps = self.adwin_var('adwin_lt1', 'completed_reps')
            self.save_adwin_data('adwin_lt1', 'data', 
                ['CR_preselect', 'CR_probe', 'completed_reps', 'total_red_CR_counts', 
                    ('CR_hist_time_out', ADWINLT1_MAX_RED_HIST_CTS),
                    ('CR_hist_all', ADWINLT1_MAX_RED_HIST_CTS),
                    ('CR_hist_yellow_time_out', ADWINLT1_MAX_YELLOW_HIST_CTS),
                    ('CR_hist_yellow_all', ADWINLT1_MAX_YELLOW_HIST_CTS),
                    ('CR_after', reps),
                    ('statistics', ADWINLT1_MAX_STAT),
                    ('SSRO1_results', reps),
                    ('SSRO2_results', reps),
                    ('PLU_Bell_states', reps),
                    ('CR_before', reps) ])
        if use_lt2:
            reps = self.adwin_var('adwin_lt1', 'completed_reps')
            self.save_adwin_data('adwin_lt2', 'data', ['completed_reps', 'total_CR_counts',
                    ('CR_before', reps),
                    ('CR_after', reps),
                    ('CR_hist', ADWINLT2_MAX_CR_HIST_CTS),
                    ('SSRO_lt2_data', reps),
                    ('statistics', ADWINLT2_MAX_STAT)])

        if use_lt1:
            params_lt1 = self.params_lt1.to_dict()
            lt1_grp = h5.DataGroup("lt1_params", self.h5data, 
                    base=self.h5base)
            for k in params_lt1:
                lt1_grp.group.attrs[k] = self.params_lt1[k]
                self.h5data.flush()

        if use_lt2:
            params_lt2 = self.params_lt2.to_dict()
            lt2_grp = h5.DataGroup("lt2_params", self.h5data, 
                    base=self.h5base)
            for k in params_lt2:
                lt2_grp.group.attrs[k] = self.params_lt2[k]
                self.h5data.flush()

        self.h5data.close()

### CONSTANTS AND FLAGS
EXEC_FROM = 'lt2'
USE_LT1 = True
USE_LT2 = True # and (EXEC_FROM == 'lt2')
YELLOW = True
DO_POLARIZE_N = True
DO_SEQUENCES = True

       
### configure the hardware (statics)
TeleportationMaster.adwins = {
    'adwin_lt1' : {
        'ins' : qt.instruments['adwin_lt1'] if EXEC_FROM=='lt2' else qt.instruments['adwin'],
        'process' : 'teleportation',
    },
}

if EXEC_FROM == 'lt2':    
    TeleportationMaster.adwins['adwin_lt2'] = {
            'ins' : qt.instruments['adwin'],
            'process' : 'teleportation'
        }

if EXEC_FROM == 'lt2':
    TeleportationMaster.adwin_dict = adwins_cfg.config
    TeleportationMaster.yellow_aom_lt1 = qt.instruments['YellowAOM_lt1']
    TeleportationMaster.green_aom_lt1 = qt.instruments['GreenAOM_lt1']
    TeleportationMaster.Ey_aom_lt1 = qt.instruments['MatisseAOM_lt1']
    TeleportationMaster.FT_aom_lt1 = qt.instruments['NewfocusAOM_lt1']
    TeleportationMaster.mwsrc_lt1 = qt.instruments['SMB100_lt1']

    if USE_LT2:
        TeleportationMaster.green_aom_lt2 = qt.instruments['GreenAOM']
        TeleportationMaster.Ey_aom_lt2 = qt.instruments['MatisseAOM']
        TeleportationMaster.A_aom_lt2 = qt.instruments['NewfocusAOM']
        TeleportationMaster.mwsrc_lt2 = qt.instruments['SMB100']
        TeleportationMaster.awg_lt2 = qt.instruments['AWG']
        TeleportationMaster.repump_aom_lt2 = TeleportationMaster.green_aom_lt2

elif EXEC_FROM == 'lt1':
    TeleportationMaster.adwin_dict = adwins_cfg.config
    TeleportationMaster.yellow_aom_lt1 = qt.instruments['YellowAOM']
    TeleportationMaster.green_aom_lt1 = qt.instruments['GreenAOM']
    TeleportationMaster.Ey_aom_lt1 = qt.instruments['Velocity1AOM']
    TeleportationMaster.FT_aom_lt1 = qt.instruments['Velocity2AOM']
    TeleportationMaster.mwsrc_lt1 = qt.instruments['SMB100']

if YELLOW:
    TeleportationMaster.repump_aom_lt1 = TeleportationMaster.yellow_aom_lt1
else:
    TeleportationMaster.repump_aom_lt1 = TeleportationMaster.green_aom_lt1

### tool functions
def setup_msmt(name): 
    m = TeleportationMaster(name)
    m.load_settings()
    return m

def start_msmt(m, use_lt1=True, use_lt2=True):
    m.update_definitions()
    m.setup(use_lt1, use_lt2)
    m.start(use_lt1, use_lt2)

def finish_msmt(m, use_lt1=True, use_lt2=True):
    m.stop(use_lt1, use_lt2)
    m.save(use_lt1, use_lt2)

### measurements
def CR_checking_debug(name):
    m = setup_msmt('CR_check_lt1_only_'+name)

    m.params_lt1['use_yellow'] = YELLOW
    m.params_lt1['do_N_polarization'] = 0
    m.params_lt1['do_sequences'] = 0

    m.params_lt1['max_CR_starts'] = 10000
    m.params_lt1['teleportation_repetitions'] = -1

    start_msmt(m, use_lt2=USE_LT2)
    finish_msmt(m, use_lt2=USE_LT2)


if __name__ == '__main__':
    CR_checking_debug('test')



