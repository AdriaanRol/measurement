"""
This script runs the measurement from the LT1 computer. All adwin programming
and data handling is done here.

Before running in a mode that requires both AWGs, the Slave script
on LT3 needs to be run first!
"""


import numpy as np
import logging
import qt
import hdf5_data as h5
import time

from measurement.lib.cython.hh_optimize import hht4
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)

from HH import T2_tools

import parameters as bparams
bparams.CALIBRATION=False
reload(bparams)


import sequence as bseq
reload(bseq)

import misc
reload(misc)

### CONSTANTS

# ADWIN LT3:
#DEFINE max_repetitions         10000          ' the maximum number of datapoints taken
#DEFINE max_red_hist_cts        100            ' dimension of photon counts histogram for red CR
#DEFINE max_yellow_hist_cts     100            ' dimension of photon counts histogram for yellow Resonance check
#DEFINE max_statistics          15
#DEFINE max_hist_CR_probe_time  500            '*1000 = 0.5 s is max time of CR probe time statistics
ADWINLT3_MAX_REPS = 10000
ADWINLT3_MAX_RED_HIST_CTS = 100
ADWINLT3_MAX_REPUMP_HIST_CTS = 100
ADWINLT3_MAX_STAT = 15

#DEFINE max_repetitions   20000
#DEFINE max_CR_hist_bins    100
#DEFINE max_stat             10
ADWINLT1_MAX_REPS = 20000
ADWINLT1_MAX_CR_HIST_CTS = 100
ADWINLT1_MAX_REPUMP_HIST_CTS = 100
ADWINLT1_MAX_STAT = 10


### CODE
class BellMaster(m2.MultipleAdwinsMeasurement):

    mprefix = 'Bell'

    def __init__(self, name):
        m2.MultipleAdwinsMeasurement.__init__(self, name)

        self.params_lt3 = m2.MeasurementParameters('LT3Parameters')
        self.params_lt1 = m2.MeasurementParameters('LT1Parameters')

    ### setting up
    def load_settings(self):
        for k in bparams.params.parameters:
            self.params[k] = bparams.params[k]

        for k in bparams.params_lt3.parameters:
            self.params_lt3[k] = bparams.params_lt3[k]
        
        for k in bparams.params_lt1.parameters:
            self.params_lt1[k] = bparams.params_lt1[k]

        # self.params_lt3['do_N_polarization'] = 1 if DO_POLARIZE_N else 0
        #for the sequencer and saving
        self.params_lt1['MW_during_LDE'] = 1 if LDE_DO_MW_LT1 else 0
        self.params['opt_pi_pulses'] = OPT_PI_PULSES

        #for saving only
        self.params_lt3['do_sequences'] = 1 if DO_SEQUENCES else 0
        self.params_lt3['do_LDE_sequence'] = 1 if DO_LDE_SEQUENCE else 0
        self.params_lt3['use_yellow_lt1'] = YELLOW_lt1
        self.params_lt3['use_yellow_lt3'] = YELLOW_lt3
        self.params['do_ff'] = DO_FF

    
    def update_definitions(self):
        """
        After setting the measurement parameters, execute this function to
        update pulses, etc.
        """
        bseq.pulse_defs_lt1(self)

    def autoconfig(self):
        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """

        # LT3 laser configuration

        self.params_lt3['E_laser_DAC_channel'] = self.adwins['adwin_lt3']['ins'].get_dac_channels()\
                [self.E_aom_lt3.get_pri_channel()]
        self.params_lt3['A_laser_DAC_channel'] = self.adwins['adwin_lt3']['ins'].get_dac_channels()\
                [self.A_aom_lt3.get_pri_channel()]
        self.params_lt3['yellow_laser_DAC_channel'] = self.adwins['adwin_lt3']['ins'].get_dac_channels()\
                [self.yellow_aom_lt3.get_pri_channel()]
        self.params_lt3['green_laser_DAC_channel'] = self.adwins['adwin_lt3']['ins'].get_dac_channels()\
                [self.green_aom_lt3.get_pri_channel()]
        # self.params['gate_DAC_channel'] = self.adwin.get_dac_channels()\
        #        ['gate']
            
        # self.params_lt3['repump_laser_DAC_channel'] = self.params_lt3['green_laser_DAC_channel']
        self.params_lt3['repump_laser_DAC_channel'] = self.params_lt3['yellow_laser_DAC_channel']

        self.params_lt3['E_CR_voltage'] = \
                self.E_aom_lt3.power_to_voltage(
                        self.params_lt3['E_CR_amplitude'])
        self.params_lt3['A_CR_voltage'] = \
                self.A_aom_lt3.power_to_voltage(
                        self.params_lt3['A_CR_amplitude'])

        self.params_lt3['E_SP_voltage'] = \
                self.E_aom_lt3.power_to_voltage(
                        self.params_lt3['E_SP_amplitude'])
        self.params_lt3['A_SP_voltage'] = \
                self.A_aom_lt3.power_to_voltage(
                        self.params_lt3['A_SP_amplitude'])

        self.params_lt3['E_RO_voltage'] = \
                self.E_aom_lt3.power_to_voltage(
                        self.params_lt3['E_RO_amplitude'])
        self.params_lt3['A_RO_voltage'] = \
                self.A_aom_lt3.power_to_voltage(
                        self.params_lt3['A_RO_amplitude'])
                       
        self.params_lt3['repump_voltage'] = \
                self.repump_aom_lt3.power_to_voltage(
                        self.params_lt3['repump_amplitude'])

        self.params_lt3['E_off_voltage'] = self.E_aom_lt3.get_pri_V_off()
        self.params_lt3['A_off_voltage'] = self.A_aom_lt3.get_pri_V_off()
        self.params_lt3['repump_off_voltage'] = self.repump_aom_lt3.get_pri_V_off()

        
               
        # LT1 laser configuration

        self.params_lt1['Ey_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                [self.E_aom_lt1.get_pri_channel()]
        self.params_lt1['A_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                [self.A_aom_lt1.get_pri_channel()]
        self.params_lt1['green_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
               [self.green_aom_lt1.get_pri_channel()]
        self.params_lt1['yellow_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
               [self.yellow_aom_lt1.get_pri_channel()]

        if YELLOW_lt1:
            self.params_lt1['repump_laser_DAC_channel'] = self.params_lt1['yellow_laser_DAC_channel']
        else:
            self.params_lt1['repump_laser_DAC_channel'] = self.params_lt1['green_laser_DAC_channel']

        self.params_lt1['Ey_CR_voltage'] = \
                self.E_aom_lt1.power_to_voltage(
                        self.params_lt1['Ey_CR_amplitude'])
        self.params_lt1['A_CR_voltage'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['A_CR_amplitude'])

        self.params_lt1['Ey_SP_voltage'] = \
                self.E_aom_lt1.power_to_voltage(
                        self.params_lt1['Ey_SP_amplitude'])
        self.params_lt1['A_SP_voltage'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['A_SP_amplitude'])

        self.params_lt1['Ey_RO_voltage'] = \
                self.E_aom_lt1.power_to_voltage(
                        self.params_lt1['Ey_RO_amplitude'])
        self.params_lt1['A_RO_voltage'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['A_RO_amplitude'])

        self.params_lt1['Ey_off_voltage'] = self.E_aom_lt1.get_pri_V_off()
        self.params_lt1['A_off_voltage'] =  self.A_aom_lt1.get_pri_V_off()
        self.params_lt1['repump_off_voltage'] = self.repump_aom_lt1.get_pri_V_off()
                       
        self.params_lt1['repump_voltage'] = \
                self.repump_aom_lt1.power_to_voltage(
                        self.params_lt1['repump_amplitude'], controller='pri')

        # add values from AWG calibrations
        self.params_lt1['SP_voltage_AWG'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['AWG_SP_power'], controller='sec')
        
        # add values from AWG calibrations
        # self.params_lt1['SP_voltage_AWG_yellow'] = \
        #         self.repump_aom_lt1.power_to_voltage(
        #                 self.params_lt1['AWG_yellow_power'], controller='sec')
        
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params_lt1['SP_voltage_AWG'])
        # qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params_lt1['SP_voltage_AWG_yellow'])

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """        
        self.yellow_aom_lt3.set_power(0.)
        self.green_aom_lt3.set_power(0.)
        self.E_aom_lt3.set_power(0.)
        self.A_aom_lt3.set_power(0.)
        self.green_aom_lt3.set_cur_controller('ADWIN')
        self.E_aom_lt3.set_cur_controller('ADWIN')
        self.A_aom_lt3.set_cur_controller('ADWIN')
        self.yellow_aom_lt3.set_cur_controller('ADWIN')
        self.yellow_aom_lt3.set_power(0.)
        self.green_aom_lt3.set_power(0.)
        self.E_aom_lt3.set_power(0.)
        self.A_aom_lt3.set_power(0.)

        if DO_SEQUENCES:
            self.mwsrc_lt3.set_iq('on')
            self.mwsrc_lt3.set_pulm('on')
            self.mwsrc_lt3.set_frequency(self.params_lt3['mw_frq'])
            self.mwsrc_lt3.set_power(self.params_lt3['mw_power'])
        
        self.mwsrc_lt3.set_status('on' if (DO_SEQUENCES and LDE_DO_MW_LT3) else 'off')

        self.green_aom_lt1.set_power(0.)
        self.E_aom_lt1.set_power(0.)
        self.A_aom_lt1.set_power(0.)
        self.yellow_aom_lt1.set_cur_controller('ADWIN')
        self.green_aom_lt1.set_cur_controller('ADWIN')
        self.E_aom_lt1.set_cur_controller('ADWIN')
        self.A_aom_lt1.set_cur_controller('ADWIN')
        self.green_aom_lt1.set_power(0.)
        self.E_aom_lt1.set_power(0.)
        self.A_aom_lt1.set_power(0.)
        
        if DO_SEQUENCES:
            self.mwsrc_lt1.set_iq('on')
            self.mwsrc_lt1.set_pulm('on')
            self.mwsrc_lt1.set_frequency(self.params_lt1['mw_frq'])
            self.mwsrc_lt1.set_power(self.params_lt1['mw_power'])

            # have different types of sequences we can load.
            if DO_OPT_RABI_AMP_SWEEP:
                self.lt1_opt_rabi_sequence()
            else:
                self.lt1_sequence()

        self.mwsrc_lt1.set_status('on' if (DO_SEQUENCES and LDE_DO_MW_LT1) else 'off')

        if TH:
            self.tharp.start_T2_mode()
            self.tharp.calibrate()
  
    def lt1_sequence(self):
        print "Make lt1 sequence... "

        self.lt1_seq = pulsar.Sequence('TeleportationLT1')

        dummy_element = bseq._lt1_dummy_element(self)
        LDE_element = bseq._lt1_LDE_element(self)
        finished_element = bseq._lt1_sequence_finished_element(self)

        self.lt1_seq.append(name = 'LDE_LT1',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            trigger_wait = True,
            goto_target = 'LDE_LT1',
            repetitions = self.params['LDE_attempts_before_CR'])

          self.lt1_seq.append(name = 'LT1_ready_for_RO',
            wfname = finished_element.name,
            goto_target = 'LDE_LT1')

        ### AND ADD READOUT PULSES
        elements = []
        elements.append(dummy_element)
        
        if DO_LDE_SEQUENCE:
            elements.append(LDE_element)

        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.lt1_seq)
        self.awg_lt1.set_runmode('SEQ')
        self.awg_lt1.start()

        i=0
        awg_ready = False
        while not awg_ready and i<40:
            try:
                if self.awg_lt1.get_state() == 'Waiting for trigger':
                    awg_ready = True
            except:
                print 'waiting for awg: usually means awg is still busy and doesnt respond'
                print 'waiting', i, '/40'
                i=i+1
            qt.msleep(0.5)
        if not awg_ready: 
            raise Exception('AWG not ready')

    ### Start and program adwins; Process control
    def _auto_adwin_params(self, adwin):
        for key,_val in self.adwin_dict['{}_processes'.format(adwin)]\
            [self.adwins[adwin]['process']]['params_long']:
            try:
                self.adwin_process_params[adwin][key] = \
                    self.params_lt3[key] if adwin == 'adwin_lt3' else self.params_lt1[key]
            except:
                logging.error("Cannot set {} process variable '{}'".format(adwin, key))
                return False

        for key,_val in self.adwin_dict['{}_processes'.format(adwin)]\
            [self.adwins[adwin]['process']]['params_float']:
            try:
                self.adwin_process_params[adwin][key] = \
                    self.params_lt3[key] if adwin == 'adwin_lt3' else self.params_lt1[key]
            except:
                logging.error("Cannot set {} process variable '{}'".format(adwin, key))
                return False

    def start_lt3_process(self):
        self._auto_adwin_params('adwin_lt3')
        self.start_adwin_process('adwin_lt3', stop_processes=['counter'])

    def start_lt1_process(self):
        self._auto_adwin_params('adwin_lt1')
        self.start_adwin_process('adwin_lt1', stop_processes=['counter'])

    def stop_adwin_processes(self):
        self.stop_adwin_process('adwin_lt3')
        self.stop_adwin_process('adwin_lt1')

    
    def _TH_decode(self, data):
        """
        Decode the binary data into event time (absolute, highest precision),
        channel number and special bit. See TH documentation about the details.
        """
        event_time = np.bitwise_and(data, 2**25-1)
        channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
        special = np.bitwise_and(np.right_shift(data, 31), 1)
        return event_time, channel, special


    def measurement_loop(self):
        """
        TH stuff based on T2 mode and on Wolfgang's latest tests.
        """

        running = True
        T0 = time.time()

        # start up:
        # first the TH. for now, as the main stop condition for the loop use the TH measurement time.
        # NOTE: would be better to first stop the AWGs --- otherwise it's always possible to miss
        # successful events with some devices, which can possibly lead to sync issues.
        if TH:
            rawdata_idx = 1
            t_ofl = 0
            t_lastsync = 0
            last_sync_number = 0

            # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
            dset_hhtime = self.h5data.create_dataset('TH_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            dset_hhchannel = self.h5data.create_dataset('TH_channel-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhspecial = self.h5data.create_dataset('TH_special-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhsynctime = self.h5data.create_dataset('TH_sync_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            dset_hhsyncnumber = self.h5data.create_dataset('TH_sync_number-{}'.format(rawdata_idx), 
                (0,), 'u4', maxshape=(None,))      
            current_dset_length = 0
            
            self.tharp.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
            qt.msleep(1)

        # then the adwins; since the LT3 adwin triggers both adwin LT1 and AWGs, this is the last one
        self.start_lt1_process()
        qt.msleep(0.1)
        self.start_lt3_process()

        # monitor keystrokes
        self.start_keystroke_monitor('abort')

        print misc.start_msg
        print time.strftime('%H:%M')
        while running:


            if self.params['measurement_time'] - (time.time() - T0) < 10:
                print "Time's up!"
                break

            # Stop condition: user interrupt
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'Measurement aborted.'
                self.stop_keystroke_monitor('abort')
                break

            # Stop condition: Adwin done
            # TBD.

            # Stop condition: TH done
            if TH:
                if not self.tharp.get_MeasRunning():
                    print 'TH done.'
                    self.stop_keystroke_monitor('abort')
                    break

                _length, _data = self.tharp.get_TTTR_Data()
            
                if _length > 0:
                    _t, _c, _s = self._TH_decode(_data[:_length])
                    
                    hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                        newlength, t_ofl, t_lastsync, last_sync_number = \
                            T2_tools.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                                np.uint64(TH_MIN_SYNC_TIME), np.uint64(TH_MAX_SYNC_TIME))

                    if newlength > 0:

                        dset_hhtime.resize((current_dset_length+newlength,))
                        dset_hhchannel.resize((current_dset_length+newlength,))
                        dset_hhspecial.resize((current_dset_length+newlength,))
                        dset_hhsynctime.resize((current_dset_length+newlength,))
                        dset_hhsyncnumber.resize((current_dset_length+newlength,))

                        dset_hhtime[current_dset_length:] = hhtime
                        dset_hhchannel[current_dset_length:] = hhchannel
                        dset_hhspecial[current_dset_length:] = hhspecial
                        dset_hhsynctime[current_dset_length:] = sync_time
                        dset_hhsyncnumber[current_dset_length:] = sync_number

                        current_dset_length += newlength
                        self.h5data.flush()

                    if current_dset_length > MAX_THDATA_LEN:
                        rawdata_idx += 1
                        dset_hhtime = self.h5data.create_dataset('TH_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        dset_hhchannel = self.h5data.create_dataset('TH_channel-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        dset_hhspecial = self.h5data.create_dataset('TH_special-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        dset_hhsynctime = self.h5data.create_dataset('TH_sync_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        dset_hhsyncnumber = self.h5data.create_dataset('TH_sync_number-{}'.format(rawdata_idx), 
                            (0,), 'u4', maxshape=(None,))         
                        current_dset_length = 0

                        self.h5data.flush()
        
        self.adwins['adwin_lt3']['ins'].set_bell_var(kill_by_CR=1)
        self.adwins['adwin_lt1']['ins'].set_bell_var(kill_by_CR=1)
        qt.msleep(2)

        self.stop_adwin_processes()
        
        if TH:
            self.tharp.StopMeas()

    def run(self):
        self.autoconfig()
        data = self.measurement_loop()
        self.save(data)

    def save(self, TH_data=None):
        reps = self.adwin_var('adwin_lt3', 'completed_reps')
        self.save_adwin_data('adwin_lt3', 'data', 
            ['CR_preselect', 'CR_probe', 'completed_reps', 'noof_starts', 
                ('CR_hist_time_out', ADWINLT3_MAX_RED_HIST_CTS),
                ('CR_hist_all', ADWINLT3_MAX_RED_HIST_CTS),
                ('repump_hist_time_out', ADWINLT3_MAX_REPUMP_HIST_CTS),
                ('repump_hist_all', ADWINLT3_MAX_REPUMP_HIST_CTS),
                ('CR_after', reps),
                ('statistics', ADWINLT3_MAX_STAT),
                ('SSRO1_results', reps),
                ('SSRO2_results', reps),
                # ('PLU_Bell_states', reps), we took that out for now (oct 7, 2013)
                ('CR_before', reps),
                ('CR_probe_timer', reps), ])

        reps = self.adwin_var('adwin_lt3', 'completed_reps')
        self.save_adwin_data('adwin_lt1', 'data', ['completed_reps', 'total_CR_counts',
                ('CR_before', reps),
                ('CR_after', reps),
                ('CR_hist', ADWINLT1_MAX_CR_HIST_CTS),
                ('CR_hist_time_out', ADWINLT1_MAX_CR_HIST_CTS),
                ('repump_hist_time_out', ADWINLT1_MAX_REPUMP_HIST_CTS),
                ('repump_hist_all', ADWINLT1_MAX_REPUMP_HIST_CTS),
                ('SSRO_lt1_data', reps),
                ('statistics', ADWINLT1_MAX_STAT)])

        params_lt3 = self.params_lt3.to_dict()
        lt3_grp = h5.DataGroup("lt3_params", self.h5data, 
                base=self.h5base)
        for k in params_lt3:
            lt3_grp.group.attrs[k] = self.params_lt3[k]
            self.h5data.flush()

        params_lt1 = self.params_lt1.to_dict()
        lt1_grp = h5.DataGroup("lt1_params", self.h5data, 
                base=self.h5base)
        for k in params_lt1:
            lt1_grp.group.attrs[k] = self.params_lt1[k]
            self.h5data.flush()

        if TH_data != None:
            self.h5data['TH_data'] = TH_data
        
        self.h5data.flush()
        self.save_params()
        # self.save_instrument_settings_file()

#************************ sequence elements LT1   ******************************

class BellSlave:

    def __init__(self):
        self.params = m2.MeasurementParameters('JointParameters')
        self.params_lt3 = m2.MeasurementParameters('LT3Parameters')
        self.params_lt1 = m2.MeasurementParameters('LT1Parameters')

        self.awg = qt.instruments['AWG_lt3']
        self.pulsar_lt3 = qt.pulsar_remote

    def load_settings(self):
        for k in bparams.params.parameters:
            self.params[k] = bparams.params[k]

        for k in bparams.params_lt3.parameters:
            self.params_lt3[k] = bparams.params_lt3[k]
        
        for k in bparams.params_lt1.parameters:
            self.params_lt1[k] = bparams.params_lt1[k]

        self.params_lt3['MW_during_LDE'] = 1 if LDE_DO_MW_LT3 else 0


    def update_definitions(self):
        bseq.pulse_defs_lt3(self)

    def autoconfig(self):

        ### AWG voltages
        self.params_lt3['SP_voltage_AWG'] = \
                self.A_aom_lt3.power_to_voltage(
                        self.params_lt3['AWG_SP_power'], controller='sec')

        self.params_lt3['SP_voltage_AWG_yellow'] = \
                self.repump_aom_lt3.power_to_voltage(
                        self.params_lt3['AWG_yellow_power'], controller='sec')    

        qt.pulsar_remote.set_channel_opt('Velocity1AOM', 'high', self.params_lt3['SP_voltage_AWG'])
        qt.pulsar_remote.set_channel_opt('YellowAOM', 'high', self.params_lt3['SP_voltage_AWG_yellow'])


    def lt3_sequence(self):
        self.lt3_seq = pulsar.Sequence('TeleportationLT3')
        
        mbi_elt = bseq._lt3_mbi_element(self)
        start_LDE_element = bseq._lt3_start_LDE_element(self)
        LDE_element = bseq._lt3_LDE_element(self)
        dummy_element = bseq._lt3_dummy_element(self)
        adwin_lt3_trigger_element = bseq._lt3_adwin_LT3_trigger_element(self)
        N_init_element, BSM_CNOT_elt, BSM_UNROT_elt = bseq._lt3_N_init_and_BSM_for_bell(self)
        N_RO_elt = bseq._lt3_N_RO_elt(self)

        self.lt3_seq.append(name = 'MBI',
            trigger_wait = True,
            wfname = mbi_elt.name,
            jump_target = 'start_LDE',
            goto_target = 'MBI')

        self.lt3_seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_LDE_element.name)

        self.lt3_seq.append(name = 'LDE_LT3',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            jump_target = ('N_init' if DO_BSM else 'BSM_dummy'),
            repetitions = self.params['LDE_attempts_before_CR'])

        self.lt3_seq.append(name = 'LDE_timeout',
            wfname = adwin_lt3_trigger_element.name,
            goto_target = 'MBI')

        if DO_BSM:
            self.lt3_seq.append(name = 'N_init', 
                wfname = N_init_element.name)

            self.lt3_seq.append(name = 'BSM_CNOT',
                wfname = BSM_CNOT_elt.name)

            self.lt3_seq.append(name = 'BSM_H_UNROT',
                wfname = BSM_UNROT_elt.name)

            self.lt3_seq.append(name = 'sync_before_first_ro', 
                wfname = adwin_lt3_trigger_element.name)

            for i in range(self.params_lt3['N_RO_repetitions']):
                
                self.lt3_seq.append(name = 'N_RO-{}'.format(i+1),
                    trigger_wait = True,
                    wfname = N_RO_elt.name)
                
                self.lt3_seq.append(name = 'N_RO-{}_sync'.format(i+1), 
                    wfname = adwin_lt3_trigger_element.name, 
                    goto_target = 'MBI' if i==(self.params_lt3['N_RO_repetitions']-1) else 'N_RO-{}'.format(i+2) )
        
        else:
            self.lt3_seq.append(name = 'BSM_dummy',
                wfname = dummy_element.name)
            
            if DO_READOUT:

                self.lt3_seq.append(name = 'sync_before_first_ro', 
                    wfname = adwin_lt3_trigger_element.name)
                
                for i in range(self.params_lt3['N_RO_repetitions']):

                    self.lt3_seq.append(name='N_RO-{}'.format(i+1),
                        trigger_wait = True,
                        wfname = N_RO_elt.name)

                    self.lt3_seq.append(name = 'N_RO-{}_sync'.format(i+1), 
                        wfname = adwin_lt3_trigger_element.name, 
                        goto_target = 'MBI' if i==(self.params_lt3['N_RO_repetitions']-1) else 'N_RO-{}'.format(i+2) )



        elements = []
        elements.append(mbi_elt)
        elements.append(adwin_lt3_trigger_element)
        elements.append(start_LDE_element)
        elements.append(dummy_element)
        elements.append(N_RO_elt)

        if DO_BSM:
            elements.append(N_init_element)
            elements.append(BSM_CNOT_elt)
            elements.append(BSM_UNROT_elt)

        # if DO_POLARIZE_N:
        #     elements.append(N_pol_element)
        
        if DO_LDE_SEQUENCE:
            elements.append(LDE_element)

        qt.pulsar_remote.upload(*elements)
        
        qt.pulsar_remote.program_sequence(self.lt3_seq)
        self.awg.set_runmode('SEQ')
        self.awg.start()

        i=0
        awg_ready = False
        while not awg_ready and i<40:
            try:
                if self.awg.get_state() == 'Waiting for trigger':
                    awg_ready = True
            except:
                print 'waiting for awg: usually means awg is still busy and doesnt respond'
                print 'waiting', i, '/40'
                i=i+1
            qt.msleep(0.5)
        if not awg_ready: 
            raise Exception('AWG not ready')


### CONSTANTS AND FLAGS
TELEPORT = True
YELLOW_lt1 = False              # whether to use yellow on lt1
YELLOW_lt3 = True               # whether to use yellow on lt3
TH = True                  # if False no TH data acquisition from within qtlab.
DO_POLARIZE_N = True       # if False, don't initialize N on lt3
DO_SEQUENCES = True         # if False, we won't use the AWG at all
DO_LDE_SEQUENCE = True      # if False, no LDE sequence (both setups) will be done
LDE_DO_MW_LT3 = True         # if True, there will be MW in the LDE seq. If false, the MW source status is set to off
LDE_DO_MW_LT1 = True         # if True, there will be MW in the LDE seq. If false, the MW source status is set to off
MAX_THDATA_LEN = int(100e6)
DO_OPT_RABI_AMP_SWEEP = False # if true, we sweep the rabi parameters instead of doing LDE; essentially this only affects the sequence we make
TH_MIN_SYNC_TIME = 0 # 9 us
TH_MAX_SYNC_TIME = 3e6 # 10.2 us
OPT_PI_PULSES = 2

DO_READOUT = True ##don't change this!

if DO_POLARIZE_N and not(LDE_DO_MW_LT3):
    raise Exception('You cannot do MBI without MW, you moron.')
       
### configure the hardware (statics)
BellMaster.adwins = {
    'adwin_lt3' : {
        'ins' : qt.instruments['adwin_lt3'], # if EXEC_FROM=='lt1' else qt.instruments['adwin'],
        'process' : 'bell',
    },
    'adwin_lt1' : {
        'ins' : qt.instruments['adwin'],
        'process' : 'bell'
    }
}

BellMaster.adwin_dict = adwins_cfg.config
BellMaster.yellow_aom_lt3 = qt.instruments['YellowAOM_lt3']
BellMaster.green_aom_lt3 = qt.instruments['GreenAOM_lt3']
BellMaster.E_aom_lt3 = qt.instruments['MatisseAOM_lt3']
BellMaster.A_aom_lt3 = qt.instruments['NewfocusAOM_lt3']
BellMaster.mwsrc_lt3 = qt.instruments['SMB100_lt3']

if YELLOW_lt3:
    BellMaster.repump_aom_lt3 = BellMaster.yellow_aom_lt3
else:
    BellMaster.repump_aom_lt3 = BellMaster.green_aom_lt3

BellMaster.yellow_aom_lt1 = qt.instruments['YellowAOM']
BellMaster.green_aom_lt1 = qt.instruments['GreenAOM']
BellMaster.E_aom_lt1 = qt.instruments['MatisseAOM']
BellMaster.A_aom_lt1 = qt.instruments['NewfocusAOM']
BellMaster.mwsrc_lt1 = qt.instruments['SMB100']
BellMaster.awg_lt1 = qt.instruments['AWG']

if YELLOW_lt1:
    BellMaster.repump_aom_lt1 = BellMaster.yellow_aom_lt1
else:
    BellMaster.repump_aom_lt1 = BellMaster.green_aom_lt1

BellMaster.tharp = qt.instruments['TH_260N']

### This is ugly at this point. better merge classes at some point?
BellSlave.repump_aom_lt3 = BellMaster.repump_aom_lt3 
BellSlave.A_aom_lt3 = BellMaster.A_aom_lt3 

### tool functions
def setup_msmt(name): 
    m = BellMaster(name)
    m.load_settings()
    return m

def setup_remote_sequence():
    m = BellSlave()
    m.load_settings()
    m.autoconfig()
    m.update_definitions()
    m.lt3_sequence()

def start_msmt(m):
    m.autoconfig()
    m.update_definitions()
    m.setup()
    m.run()

def finish_msmnt():
    qt.instruments['AWG'].stop()
    qt.instruments['AWG_lt3'].stop()
    qt.msleep(1)
    qt.instruments['AWG'].set_runmode('CONT')
    qt.instruments['AWG_lt3'].set_runmode('CONT')

###measurements

def default_msmt(name):
    ### first start the slave
    ### TODO: make more like master if at some point more dynamic settings are needed
    if TH:
        if qt.instruments['HH_400'].OpenDevice():
            print 'HH opened'
        else:
            raise Exception('HH not opened, please close HH software, you moron.')

    if bparams.CALIBRATION:
        raise Exception('Params file has calibration settings, you dumb shit')
    if DO_SEQUENCES:
        setup_remote_sequence()

    # setup the master measurement
    m = setup_msmt(''+name)

    if not DO_POLARIZE_N:
        m.params_lt3['MBI_threshold'] = 0

    m.params_lt3['max_CR_starts'] = 1000
    m.params_lt3['bell_repetitions'] = -1
    m.params['measurement_time'] = 30*60 # seconds -- will actually stop 10 sec earlier.

    qt.instruments['ZPLServo'].move_out()
    qt.instruments['ZPLServo_lt3'].move_out()

    start_msmt(m)
    finish_msmnt()

def program_lt1_sequence_only(name):

    m = setup_msmt(''+name)
    global DO_DD 
    DO_DD= True
    m.update_definitions()
    m.lt1_sequence()
    qt.instruments['AWG'].stop()
    qt.instruments['AWG'].set_runmode('CONT')

if __name__ == '__main__':
    #name = raw_input('Name?')
    default_msmt('Bell')
    #program_lt1_sequence_only('test_DD')


