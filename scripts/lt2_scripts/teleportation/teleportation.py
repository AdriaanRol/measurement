import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import sequence as tseq
reload(tseq)

class TeleportationMaster(m2.MultipleAdwinsMeasurement):

    mprefix = 'Teleportation'
    # max_successful_attempts = 10000 # after this the adwin stops, in CR debug mode
    # max_red_hist_bins = 100
    # max_yellow_hist_bins = 100
    Ey_aom_lt1 = None
    FT_aom_lt1 = None
    green_aom_lt1 = None
    yellow_aom_lt1 = None

    def __init__(self, name):
        m2.MultipleAdwinsMeasurement.__init__(self, name)

        self.params_lt1 = m2.MeasurementParameters('LT1Parameters')
        self.params_lt2 = m2.MeasurementParameters('LT2Parameters')

    def load_settings(self):
	    pass
    
    def update_definitions(self):
    	"""
    	After setting the measurement parameters, execute this function to
    	update pulses, etc.
    	"""
    	#tseq.pulse_defs(self) #but not if not use MW's

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
                 
            if self.params['use_yellow_lt1']:
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
            self.params_lt2['FT_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                    [self.FT_aom_lt2.get_pri_channel()]
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
            
            self.awg_lt2.set_runmode('SEQ')

    def _auto_adwin_params(self, adwin):
        for key,_val in self.adwin_dict['{}_processes'.format(adwin)]\
            [self.adwins[adwin]['process']]['params_long']:
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
                running = self.adwin_process_running('adwin_lt1') and self.adwin_process_runnin('adwin_lt2')
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
            self.save_adwin_data('adwin_lt1', 'data', ['CR_preselect','CR_probe','completed_reps',
                        'total_red_CR_counts', 'CR_hist_time_out' ,'CR_hist_all',
                        'CR_hist_yellow_time_out', 'CR_hist_yellow_all', 'CR_after', 
                        'statistics', 'SSRO1_results', 'SSRO2_results', 'PLU_Bell_states', 'CR_before'])
        if use_lt2:
            self.save_adwin_data('adwin_lt2', 'data', ['completed_reps',
                        'total_CR_counts', 'CR_before' , 'CR_after',
                        'CR_hist','SSRO_lt2_data', 'statistics'])

        if use_lt1:
            params_lt1 = self.params_lt1.to_dict()
            lt1_grp = h5.DataGroup("lt1_params", self.h5data, 
                    base=self.h5base)
            for k in params_lt1:
                lt1_grp.group.attrs[k] = self.params_lt1[k]

        if use_lt2:
            params_lt2 = self.params_lt2.to_dict()
            lt2_grp = h5.DataGroup("lt2_params", self.h5data, 
                    base=self.h5base)
            for k in params_lt2:
                lt2_grp.group.attrs[k] = self.params_lt2[k]


        
# configure the hardware (statics)
TeleportationMaster.adwins = {
    'adwin_lt1' : {
        'ins' : qt.instruments['adwin_lt1'],
        'process' : 'teleportation',
    },

    'adwin_lt2' : {
        'ins' : qt.instruments['adwin_lt2'],
        'process' : 'teleportation'
    }
}

TeleportationMaster.adwin_dict = adwins_cfg.config
TeleportationMaster.yellow_aom_lt1 = qt.instruments['YellowAOM_lt1']
TeleportationMaster.green_aom_lt1 = qt.instruments['GreenAOM_lt1']
TeleportationMaster.Ey_aom_lt1 = qt.instruments['MatisseAOM_lt1']
TeleportationMaster.FT_aom_lt1 = qt.instruments['NewfocusAOM_lt1']
TeleportationMaster.mwsrc_lt1 = qt.instruments['SMB100_lt1']

TeleportationMaster.green_aom_lt2 = qt.instruments['GreenAOM']
TeleportationMaster.Ey_aom_lt2 = qt.instruments['MatisseAOM']
TeleportationMaster.A_aom_lt2 = qt.instruments['NewfocusAOM']
TeleportationMaster.mwsrc_lt2 = qt.instruments['SMB100']
TeleportationMaster.awg_lt2 = qt.instruments['AWG']



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

def get_general_settings_lt1(m):
    m.params_lt1['counter_channel'] = 1
    m.params_lt1['CR_duration'] = 50
    m.params_lt1['CR_threshold_preselect'] = 0
    m.params_lt1['CR_threshold_probe'] = 0
    m.params_lt1['repump_duration'] = 1000
    m.params_lt1['time_before_forced_CR'] = 20000
    m.params_lt1['teleportation_repetitions'] = 1000
    m.params_lt1['SSRO1_duration'] = 15
    m.params_lt1['ADwin_lt2_trigger_do_channel'] = 8 # OK
    m.params_lt1['ADWin_lt2_di_channel'] = 17 # OK
    m.params_lt1['AWG_lt1_trigger_do_channel'] = 10 # OK
    m.params_lt1['AWG_lt1_di_channel'] = 16 # OK
    m.params_lt1['PLU_arm_do_channel'] = 10
    m.params_lt1['PLU_di_channel'] = 2
    m.params_lt1['wait_before_SSRO1'] = 3
    m.params_lt1['wait_before_SP_after_RO'] = 3
    m.params_lt1['SP_after_RO_duration']            = 50
    m.params_lt1['wait_before_SSRO2']               = 3
    m.params_lt1['SSRO2_duration'] = 15
    m.params_lt1['repump_after_repetitions'] = 1
    m.params_lt1['CR_repump'] = 1000
    m.params_lt1['AWG_lt1_event_do_channel'] = 3
    m.params_lt1['debug_mode'] = 0
    m.params_lt1['AWG_lt2_address0_do_channel'] = 0
    m.params_lt1['AWG_lt2_address1_do_channel'] = 1
    m.params_lt1['AWG_lt2_address2_do_channel'] =2
    m.params_lt1['AWG_lt2_address3_do_channel'] =3
    m.params_lt1['AWG_lt2_address_LDE'] = 1
    m.params_lt1['AWG_lt2_address_U1'] = 2                    
    m.params_lt1['AWG_lt2_address_U2'] = 3
    m.params_lt1['AWG_lt2_address_U3'] = 4
    m.params_lt1['AWG_lt2_address_U4'] = 5
    m.params_lt1['repump_amplitude'] = 0            
    m.params_lt1['repump_off_voltage'] = 0         
    m.params_lt1['Ey_CR_amplitude'] = 0             
    m.params_lt1['FT_CR_amplitude'] = 0              
    m.params_lt1['Ey_SP_amplitude'] = 0              
    m.params_lt1['FT_SP_amplitude'] = 0             
    m.params_lt1['Ey_RO_amplitude'] = 0            
    m.params_lt1['FT_RO_amplitude'] = 0        
    m.params_lt1['Ey_off_voltage'] = 0 
    m.params_lt1['FT_off_voltage'] = 0 

def get_general_settings_lt2(m):
    m.params_lt2['counter_channel'] =1
    m.params_lt2['repump_duration'] = 50
    m.params_lt2['CR_duration'] = 50
    m.params_lt2['CR_preselect'] = 0
    m.params_lt2['teleportation_repetitions'] = 5000
    m.params_lt2['SSRO_lt2_duration'] = 50
    m.params_lt2['CR_probe'] = 0
    m.params_lt2['repump_after_repetitions'] = 1
    m.params_lt2['CR_repump'] = 1000
    m.params_lt2['Adwin_lt1_do_channel'] = 8
    m.params_lt2['Adwin_lt1_di_channel'] = 17
    m.params_lt2['AWG_lt2_di_channel'] = 16
    m.params_lt2['repump_amplitude'] = 0            
    m.params_lt2['repump_off_voltage'] = 0         
    m.params_lt2['Ey_CR_amplitude'] = 0             
    m.params_lt2['A_CR_amplitude'] = 0              
    m.params_lt2['Ey_SP_amplitude'] = 0              
    m.params_lt2['A_SP_amplitude'] = 0             
    m.params_lt2['Ey_RO_amplitude'] = 0            
    m.params_lt2['A_RO_amplitude'] = 0        
    m.params_lt2['Ey_off_voltage'] = 0 
    m.params_lt2['A_off_voltage'] = 0 

def CR_check_lt1_only(name):
    m = setup_msmt('CR_check_lt1_only_'+name)
    
    get_general_settings_lt1(m)
    
    m.params['use_yellow_lt1'] = True
    if m.params['use_yellow_lt1']:
        m.repump_aom_lt1 = m.yellow_aom_lt1
    else:
        m.repump_aom_lt1 = m.green_aom_lt1

    start_msmt(m, use_lt2=False)
    finish_msmt(m, use_lt2=False)


CR_check_lt1_only('test')










