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
import time

from measurement.lib.cython.hh_optimize import hht4
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)

from HH import T2_tools

import parameters as tparams
reload(tparams)

import sequence as tseq
reload(tseq)

import misc
reload(misc)

### CONSTANTS

# ADWIN LT1:
#DEFINE max_repetitions         10000          ' the maximum number of datapoints taken
#DEFINE max_red_hist_cts        100            ' dimension of photon counts histogram for red CR
#DEFINE max_yellow_hist_cts     100            ' dimension of photon counts histogram for yellow Resonance check
#DEFINE max_statistics          15
#DEFINE max_hist_CR_probe_time  500            '*1000 = 0.5 s is max time of CR probe time statistics
ADWINLT1_MAX_REPS = 10000
ADWINLT1_MAX_RED_HIST_CTS = 100
ADWINLT1_MAX_REPUMP_HIST_CTS = 100
ADWINLT1_MAX_STAT = 15
ADWINLT1_MAX_CR_PROBE_TIMER_HIST_BINS = 500

#DEFINE max_repetitions   20000
#DEFINE max_CR_hist_bins    100
#DEFINE max_stat             10
ADWINLT2_MAX_REPS = 20000
ADWINLT2_MAX_CR_HIST_CTS = 100
ADWINLT2_MAX_REPUMP_HIST_CTS = 100
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

        self.params_lt1['do_N_polarization'] = 1 if DO_POLARIZE_N else 0
        self.params_lt1['do_sequences'] = 1 if DO_SEQUENCES else 0
        self.params_lt1['do_LDE_sequence'] = 1 if DO_LDE_SEQUENCE else 0
        self.params['MW_during_LDE'] = 1 if LDE_DO_MW else 0
        self.params['opt_pi_pulses'] = OPT_PI_PULSES

    
    def update_definitions(self):
        """
        After setting the measurement parameters, execute this function to
        update pulses, etc.
        """
        tseq.pulse_defs_lt2(self)

    def autoconfig(self):
        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """

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
       
        self.params_lt2['Ey_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                [self.Ey_aom_lt2.get_pri_channel()]
        self.params_lt2['A_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                [self.A_aom_lt2.get_pri_channel()]
        self.params_lt2['green_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
               [self.green_aom_lt2.get_pri_channel()]
        self.params_lt2['yellow_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
               [self.yellow_aom_lt2.get_pri_channel()]

        if YELLOW:
            self.params_lt2['repump_laser_DAC_channel'] = self.params_lt2['yellow_laser_DAC_channel']
        else:
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
                        self.params_lt2['repump_amplitude'], controller='pri')

        # add values from AWG calibrations
        self.params_lt2['SP_voltage_AWG'] = \
                self.A_aom_lt2.power_to_voltage(
                        self.params_lt2['AWG_SP_power'], controller='sec')
        # add values from AWG calibrations
        self.params_lt2['SP_voltage_AWG_yellow'] = \
                self.repump_aom_lt2.power_to_voltage(
                        self.params_lt2['AWG_yellow_power'], controller='sec')
        
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params_lt2['SP_voltage_AWG'])
        qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params_lt2['SP_voltage_AWG_yellow'])

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """        
        self.yellow_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_power(0.)
        self.Ey_aom_lt1.set_power(0.)
        self.FT_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_cur_controller('ADWIN')
        self.Ey_aom_lt1.set_cur_controller('ADWIN')
        self.FT_aom_lt1.set_cur_controller('ADWIN')
        self.yellow_aom_lt1.set_cur_controller('ADWIN')
        self.yellow_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_power(0.)
        self.Ey_aom_lt1.set_power(0.)
        self.FT_aom_lt1.set_power(0.)

        if DO_SEQUENCES:
            self.mwsrc_lt1.set_iq('on')
            self.mwsrc_lt1.set_pulm('on')
            self.mwsrc_lt1.set_frequency(self.params_lt1['mw_frq'])
            self.mwsrc_lt1.set_power(self.params_lt1['mw_power'])
        
        self.mwsrc_lt1.set_status('on' if DO_SEQUENCES else 'off')

        self.green_aom_lt2.set_power(0.)
        self.Ey_aom_lt2.set_power(0.)
        self.A_aom_lt2.set_power(0.)
        self.yellow_aom_lt2.set_cur_controller('ADWIN')
        self.green_aom_lt2.set_cur_controller('ADWIN')
        self.Ey_aom_lt2.set_cur_controller('ADWIN')
        self.A_aom_lt2.set_cur_controller('ADWIN')
        self.green_aom_lt2.set_power(0.)
        self.Ey_aom_lt2.set_power(0.)
        self.A_aom_lt2.set_power(0.)
        
        if DO_SEQUENCES:
            self.mwsrc_lt2.set_iq('on')
            self.mwsrc_lt2.set_pulm('on')
            self.mwsrc_lt2.set_frequency(self.params_lt2['mw_frq'])
            self.mwsrc_lt2.set_power(self.params_lt2['mw_power'])

            # have different types of sequences we can load.
            if DO_OPT_RABI_AMP_SWEEP:
                self.lt2_opt_rabi_sequence()
            else:
                self.lt2_sequence()

        self.mwsrc_lt2.set_status('on' if DO_SEQUENCES else 'off')

        if HH:
            self.hharp.start_T2_mode()
            self.hharp.calibrate()
  
    def lt2_sequence(self):
        print "Make lt2 sequence... "

        self.lt2_seq = pulsar.Sequence('TeleportationLT2')

        dummy_element = _lt2_dummy_element(self)
        LDE_element = _lt2_LDE_element(self)
        finished_element = _lt2_sequence_finished_element(self)

        def dynamical_decoupling(seq, name, time_offset):
            return _lt2_dynamical_decoupling(self, seq, name, time_offset)

        self.lt2_seq.append(name = 'LDE_LT2',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            trigger_wait = True,
            # jump_target = 'DD', TODO: not implemented yet
            goto_target = 'LDE_LT2',
            repetitions = self.params['LDE_attempts_before_CR'])

        self.lt2_seq, total_elt_time, elts = self.dynamical_decoupling(self.lt2_seq, 
            time_offset = LDE_element.length(),
            begin_offset_time = self.params_lt2['dd_spin_echo_time'])

        ### AND ADD READOUT PULSES 

        elements = []
        elements.append(dummy_element)
        elements.append(finished_element)

        for e in elts: #the dynamical decoupling sequence elements
            if e not in elements:
                elements.append(e) 

        if DO_LDE_SEQUENCE:
            elements.append(LDE_element)

        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.lt2_seq)
        self.awg_lt2.set_runmode('SEQ')
        self.awg_lt2.start()

        i=0
        awg_ready = False
        while not awg_ready and i<40:
            try:
                if self.awg_lt2.get_state() == 'Waiting for trigger':
                    awg_ready = True
            except:
                print 'waiting for awg: usually means awg is still busy and doesnt respond'
                print 'waiting', i, '/40'
                i=i+1
            qt.msleep(0.5)
        if not awg_ready: 
            raise Exception('AWG not ready')


    def lt2_opt_rabi_sequence(self):
        """
        Generates a sequence for calibration of optical rabi oscillations.
        We sweep the power of an optical pulse of a certain length here.
        """

        print 'Make optical Rabi sequence...'

        self.lt2_seq = pulsar.Sequence('OpticalRabi')
        elements = []
        
        for i in range(1,self.params['opt_rabi_sweep_pts']+1):
            lde_elt = _lt2_LDE_element(self, name = 'OpticalRabi-{}'.format(i),
                eom_pulse_amplitude = self.params['eom_pulse_amplitudes'][i-1])
            
            self.lt2_seq.append(name='OpticalRabi-{}'.format(i),
                wfname = lde_elt.name,
                trigger_wait = True,
                goto_target = 'OpticalRabi-{}'.format(i+1 if i < self.params['opt_rabi_sweep_pts'] else 1),
                repetitions = self.params['LDE_attempts_before_CR'])
            elements.append(lde_elt)
        
        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.lt2_seq)
        self.awg_lt2.set_runmode('SEQ')
        self.awg_lt2.start()

        i=0
        awg_ready = False
        while not awg_ready and i<40:
            try:
                if self.awg_lt2.get_state() == 'Waiting for trigger':
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

    def stop_adwin_processes(self):
        self.stop_adwin_process('adwin_lt1')
        self.stop_adwin_process('adwin_lt2')

    
    def _HH_decode(self, data):
        """
        Decode the binary data into event time (absolute, highest precision),
        channel number and special bit. See HH documentation about the details.
        """
        event_time = np.bitwise_and(data, 2**25-1)
        channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
        special = np.bitwise_and(np.right_shift(data, 31), 1)
        return event_time, channel, special


    def measurement_loop(self):
        """
        HH stuff based on T2 mode and on Wolfgang's latest tests.
        """

        running = True

        # start up:
        # first the HH. for now, as the main stop condition for the loop use the HH measurement time.
        # NOTE: would be better to first stop the AWGs --- otherwise it's always possible to miss
        # successful events with some devices, which can possibly lead to sync issues.
        if HH:
            rawdata_idx = 1
            t_ofl = 0
            t_lastsync = 0
            last_sync_number = 0

            # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
            dset_hhtime = self.h5data.create_dataset('HH_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            dset_hhchannel = self.h5data.create_dataset('HH_channel-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhspecial = self.h5data.create_dataset('HH_special-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhsynctime = self.h5data.create_dataset('HH_sync_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            dset_hhsyncnumber = self.h5data.create_dataset('HH_sync_number-{}'.format(rawdata_idx), 
                (0,), 'u4', maxshape=(None,))      
            current_dset_length = 0
            
            self.hharp.StartMeas(int(self.params['measurement_time']* 1e3)) # this is in ms
            qt.msleep(0.1)

        # then the adwins; since the LT1 adwin triggers both adwin LT2 and AWGs, this is the last one
        self.start_lt2_process()
        qt.msleep(0.1)
        self.start_lt1_process()

        # monitor keystrokes
        self.start_keystroke_monitor('abort')

        print misc.start_msg
        while running:

            # Stop condition: user interrupt
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'Measurement aborted.'
                self.stop_keystroke_monitor('abort')
                break

            # Stop condition: Adwin done
            # TBD.

            # Stop condition: HH done
            if HH:
                if not self.hharp.get_MeasRunning():
                    print 'HH done.'
                    self.stop_keystroke_monitor('abort')
                    break

                _length, _data = self.hharp.get_TTTR_Data()
            
                if _length > 0:
                    _t, _c, _s = self._HH_decode(_data[:_length])
                    
                    hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                        newlength, t_ofl, t_lastsync, last_sync_number = \
                            T2_tools.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                                np.uint64(HH_MIN_SYNC_TIME), np.uint64(HH_MAX_SYNC_TIME))

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

                    if current_dset_length > MAX_HHDATA_LEN:
                        rawdata_idx += 1
                        dset_hhtime = self.h5data.create_dataset('HH_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        dset_hhchannel = self.h5data.create_dataset('HH_channel-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        dset_hhspecial = self.h5data.create_dataset('HH_special-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        dset_hhsynctime = self.h5data.create_dataset('HH_sync_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        dset_hhsyncnumber = self.h5data.create_dataset('HH_sync_number-{}'.format(rawdata_idx), 
                            (0,), 'u4', maxshape=(None,))         
                        current_dset_length = 0

                        self.h5data.flush()
        
        self.stop_adwin_processes()
        
        if HH:
            self.hharp.StopMeas()

    def run(self):
        self.autoconfig()
        data = self.measurement_loop()
        self.save(data)

    def save(self, HH_data=None):
        reps = self.adwin_var('adwin_lt1', 'completed_reps')
        self.save_adwin_data('adwin_lt1', 'data', 
            ['CR_preselect', 'CR_probe', 'completed_reps', 'noof_starts', 
                ('CR_hist_time_out', ADWINLT1_MAX_RED_HIST_CTS),
                ('CR_hist_all', ADWINLT1_MAX_RED_HIST_CTS),
                ('repump_hist_time_out', ADWINLT1_MAX_REPUMP_HIST_CTS),
                ('repump_hist_all', ADWINLT1_MAX_REPUMP_HIST_CTS),
                ('CR_after', reps),
                ('statistics', ADWINLT1_MAX_STAT),
                ('SSRO1_results', reps),
                ('SSRO2_results', reps),
                ('PLU_Bell_states', reps),
                ('CR_before', reps),
                ('CR_probe_timer', reps),
                ('CR_probe_timer_all',ADWINLT1_MAX_CR_PROBE_TIMER_HIST_BINS),
                ('CR_timer_lt2',ADWINLT1_MAX_CR_PROBE_TIMER_HIST_BINS) ])

        reps = self.adwin_var('adwin_lt1', 'completed_reps')
        self.save_adwin_data('adwin_lt2', 'data', ['completed_reps', 'total_CR_counts',
                ('CR_before', reps),
                ('CR_after', reps),
                ('CR_hist', ADWINLT2_MAX_CR_HIST_CTS),
                ('CR_hist_time_out', ADWINLT2_MAX_CR_HIST_CTS),
                ('repump_hist_time_out', ADWINLT2_MAX_REPUMP_HIST_CTS),
                ('repump_hist_all', ADWINLT2_MAX_REPUMP_HIST_CTS),
                ('SSRO_lt2_data', reps),
                ('statistics', ADWINLT2_MAX_STAT)])

        params_lt1 = self.params_lt1.to_dict()
        lt1_grp = h5.DataGroup("lt1_params", self.h5data, 
                base=self.h5base)
        for k in params_lt1:
            lt1_grp.group.attrs[k] = self.params_lt1[k]
            self.h5data.flush()

        params_lt2 = self.params_lt2.to_dict()
        lt2_grp = h5.DataGroup("lt2_params", self.h5data, 
                base=self.h5base)
        for k in params_lt2:
            lt2_grp.group.attrs[k] = self.params_lt2[k]
            self.h5data.flush()

        if HH_data != None:
            self.h5data['HH_data'] = HH_data
        
        self.h5data.flush()
        self.save_params()
        # self.save_instrument_settings_file()


#************************ sequence elements LT2   ******************************


class TeleportationSlave:

    def __init__(self):
        self.params = m2.MeasurementParameters('JointParameters')
        self.params_lt1 = m2.MeasurementParameters('LT1Parameters')
        self.params_lt2 = m2.MeasurementParameters('LT2Parameters')

        self.awg = qt.instruments['AWG_lt1']
        self.pulsar_lt1 = qt.pulsar_remote

    def load_settings(self):
        for k in tparams.params.parameters:
            self.params[k] = tparams.params[k]

        for k in tparams.params_lt1.parameters:
            self.params_lt1[k] = tparams.params_lt1[k]
        
        for k in tparams.params_lt2.parameters:
            self.params_lt2[k] = tparams.params_lt2[k]

        self.params_lt2['use_yellow'] = YELLOW

    def update_definitions(self):
        tseq.pulse_defs_lt1(self)

    def autoconfig(self):

        ### AWG voltages
        self.params_lt1['SP_voltage_AWG'] = \
                self.FT_aom_lt1.power_to_voltage(
                        self.params_lt1['AWG_SP_power'], controller='sec')
        qt.pulsar_remote.set_channel_opt('Velocity1AOM', 'high', self.params_lt1['SP_voltage_AWG'])

  

    def lt1_sequence(self):
        self.lt1_seq = pulsar.Sequence('TeleportationLT1')

        N_pol_decision_element = tseq._lt1_N_polarization_decision_element(self)
        N_pol_element = tseq._lt1_N_pol_element(self)
        start_LDE_element = tseq._lt1_start_LDE_element(self)
        LDE_element = tseq._lt1_LDE_element(self)
        dummy_element = tseq._lt1_dummy_element(self)
        adwin_lt1_trigger_element = tseq._lt1_adwin_LT1_trigger_element(self)
        N_init_element, BSM_CNOT_elt, BSM_UNROT_elt = tseq._lt1_N_init_and_BSM_for_teleportation(self)
        N_RO_CNOT_elt = tseq._lt1_N_RO_CNOT_elt(self)

        self.lt1_seq.append(name = 'N_pol_decision',
            wfname = N_pol_decision_element.name,
            trigger_wait = True,
            goto_target = 'N_polarization' if DO_POLARIZE_N else 'start_LDE',
            jump_target = 'start_LDE')

        if DO_POLARIZE_N:
            self.lt1_seq.append(name = 'N_polarization',
                wfname = N_pol_element.name,
                trigger_wait = True,
                repetitions = self.params_lt1['N_pol_element_repetitions'])
            self.lt1_seq.append(name = 'N_polarization_done',
                wfname = adwin_lt1_trigger_element.name)

        self.lt1_seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_LDE_element.name)

        self.lt1_seq.append(name = 'LDE_LT1',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            jump_target = ('N_init' if DO_BSM else None),
            repetitions = self.params['LDE_attempts_before_CR'])

        self.lt1_seq.append(name = 'LDE_timeout',
            wfname = adwin_lt1_trigger_element.name,
            goto_target = 'N_pol_decision')

        if DO_BSM:
            self.lt1_seq.append(name = 'N_init', 
                wfname = N_init_element.name)

            self.lt1_seq.append(name = 'BSM_CNOT',
                wfname = BSM_CNOT_elt.name)

            self.lt1_seq.append(name = 'BSM_H_UNROT',
                wfname = BSM_UNROT_elt.name)

            self.lt1_seq.append(name = 'sync_before_first_ro', 
                wfname = adwin_lt1_trigger_element.name)

            self.lt1_seq.append(name = 'N_RO_CNOT',
                trigger_wait = True,
                wfname = N_RO_CNOT_elt.name)

            self.lt1_seq.append(name = 'sync_before_second_ro', 
                wfname = adwin_lt1_trigger_element.name, 
                goto_target = 'N_pol_decision')

        elements = []
        elements.append(N_pol_decision_element)
        elements.append(adwin_lt1_trigger_element)
        elements.append(start_LDE_element)

        if DO_BSM:
            elements.append(N_init_element)
            elements.append(BSM_CNOT_elt)
            elements.append(BSM_UNROT_elt)
            elements.append(N_RO_CNOT_elt)

        if DO_POLARIZE_N:
            elements.append(N_pol_element)
        
        if DO_LDE_SEQUENCE:
            elements.append(LDE_element)

        qt.pulsar_remote.upload(*elements)
        
        qt.pulsar_remote.program_sequence(self.lt1_seq)
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
YELLOW = True              # whether to use yellow on lt2
HH = True                # if False no HH data acquisition from within qtlab.
DO_POLARIZE_N = False      # if False, no N-polarization sequence on LT1 will be used
DO_SEQUENCES = True      # if False, we won't use the AWG at all
DO_LDE_SEQUENCE = True    # if False, no LDE sequence (both setups) will be done
LDE_DO_MW = False         # if True, there will be MW in the LDE seq
MAX_HHDATA_LEN = int(100e6)
DO_OPT_RABI_AMP_SWEEP = False # if true, we sweep the rabi parameters instead of doing LDE; essentially this only affects the sequence we make
HH_MIN_SYNC_TIME = 0 # 9 us
HH_MAX_SYNC_TIME = 3e6 # 10.2 us
OPT_PI_PULSES = 2
DO_BSM = False

       
### configure the hardware (statics)
TeleportationMaster.adwins = {
    'adwin_lt1' : {
        'ins' : qt.instruments['adwin_lt1'], # if EXEC_FROM=='lt2' else qt.instruments['adwin'],
        'process' : 'teleportation',
    },
    'adwin_lt2' : {
        'ins' : qt.instruments['adwin'],
        'process' : 'teleportation'
    }
}

TeleportationMaster.adwin_dict = adwins_cfg.config
TeleportationMaster.yellow_aom_lt1 = qt.instruments['YellowAOM_lt1']
TeleportationMaster.green_aom_lt1 = qt.instruments['GreenAOM_lt1']
TeleportationMaster.Ey_aom_lt1 = qt.instruments['MatisseAOM_lt1']
TeleportationMaster.FT_aom_lt1 = qt.instruments['NewfocusAOM_lt1']
TeleportationMaster.mwsrc_lt1 = qt.instruments['SMB100_lt1']
TeleportationMaster.repump_aom_lt1 = TeleportationMaster.green_aom_lt1

TeleportationMaster.yellow_aom_lt2 = qt.instruments['YellowAOM']
TeleportationMaster.green_aom_lt2 = qt.instruments['GreenAOM']
TeleportationMaster.Ey_aom_lt2 = qt.instruments['MatisseAOM']
TeleportationMaster.A_aom_lt2 = qt.instruments['NewfocusAOM']
TeleportationMaster.mwsrc_lt2 = qt.instruments['SMB100']
TeleportationMaster.awg_lt2 = qt.instruments['AWG']

if YELLOW:
    TeleportationMaster.repump_aom_lt2 = TeleportationMaster.yellow_aom_lt2
else:
    TeleportationMaster.repump_aom_lt2 = TeleportationMaster.green_aom_lt2

TeleportationMaster.hharp = qt.instruments['HH_400']

### This is ugly at this point. better merge classes at some point?
TeleportationSlave.repump_aom_lt1 = qt.instruments['GreemAOM_lt1']
TeleportationSlave.FT_aom_lt1 = qt.instruments['NewfocusAOM_lt1']

### tool functions
def setup_msmt(name): 
    m = TeleportationMaster(name)
    m.load_settings()
    return m

def setup_remote_sequence():
    m = TeleportationSlave()
    m.load_settings()
    m.autoconfig()
    m.update_definitions()
    m.lt1_sequence()

def start_msmt(m):
    m.autoconfig()
    m.update_definitions()
    m.setup()
    m.run()

def finish_msmnt():
    qt.instruments['AWG'].stop()
    qt.instruments['AWG_lt1'].stop()
    qt.instruments['AWG_lt1'].set_ch2_offset(0)
    qt.instruments['AWG'].set_runmode('CONT')
    qt.instruments['AWG_lt1'].set_runmode('CONT')



###measurements

def default_msmt(name):
    ### first start the slave
    ### TODO: make more like master if at some point more dynamic settings are needed
    if DO_SEQUENCES:
        setup_remote_sequence()

    # setup the master measurement
    m = setup_msmt('TPQI_'+name)

    m.params_lt1['max_CR_starts'] = -1
    m.params_lt1['teleportation_repetitions'] = -1
    m.params['measurement_time'] = 60 * 30 # seconds; only affects msmt with HH.

    # pts = 11
    # m.params['opt_rabi_sweep_pts'] = pts
    # m.params['eom_pulse_amplitudes'] = np.linspace(0.5,1.5,pts)

    start_msmt(m)
    finish_msmnt()

if __name__ == '__main__':
    default_msmt('lt2-tail')

                                                                                                                                                                                                                                                                                          