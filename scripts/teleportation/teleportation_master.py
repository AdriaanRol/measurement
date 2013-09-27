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

        self.lt2_seq.append(name = 'LDE_LT2',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            trigger_wait = True,
            # jump_target = 'DD', TODO: not implemented yet
            goto_target = 'LDE_LT2',
            repetitions = self.params['LDE_attempts_before_CR'])

        elements = []
        elements.append(dummy_element)
        elements.append(finished_element)

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

def _lt2_sequence_finished_element(msmnt):
    """
    last element of a two-setup sequence. Sends a trigger to ADwin LT2.
    """
    e = element.Element('LT2_finished', pulsar = qt.pulsar)
    e.append(msmnt.adwin_lt2_trigger_pulse)
    return e

def _lt2_dummy_element(msmnt):
    """
    A 1us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('Dummy', pulsar = qt.pulsar)
    e.append(pulse.cp(msmnt.T_pulse, length=1e-6))
    return e

def _lt2_LDE_element(msmnt, **kw):
    """
    This element contains the LDE part for LT2, i.e., spin pumping and MW pulses
    for the LT2 NV and the optical pi pulses as well as all the markers for HH and PLU.
    """

    # variable parameters
    name = kw.pop('name', 'LDE_LT2')
    eom_pulse_amplitude = kw.pop('eom_pulse_amplitude', msmnt.params_lt2['eom_pulse_amplitude'])

    ###
    e = element.Element(name, pulsar = qt.pulsar, global_time = True)
    e.add(pulse.cp(msmnt.SP_pulse,
            amplitude = 0,
            length = msmnt.params['LDE_element_length']))

    #1 SP
    e.add(pulse.cp(msmnt.SP_pulse, 
            amplitude = 0, 
            length = msmnt.params_lt2['initial_delay']), 
        name = 'initial delay')
    
    e.add(pulse.cp(msmnt.SP_pulse, 
            length = msmnt.params['LDE_SP_duration'], 
            amplitude = 1.0), 
        name = 'spinpumping', 
        refpulse = 'initial delay')

    e.add(pulse.cp(msmnt.yellow_pulse, 
            length = msmnt.params['LDE_SP_duration_yellow'], 
            amplitude = 1.0), 
        name = 'spinpumpingyellow', 
        refpulse = 'initial delay')

    
    for i in range(OPT_PI_PULSES):
        name = 'opt pi {}'.format(i+1)
        refpulse = 'opt pi {}'.format(i) if i > 0 else 'spinpumping'
        start = msmnt.params_lt2['opt_pulse_separation'] if i > 0 else msmnt.params['wait_after_sp']
        refpoint = 'start' if i > 0 else 'end'

        e.add(pulse.cp(msmnt.eom_aom_pulse, 
                eom_pulse_amplitude = eom_pulse_amplitude),
            name = name, 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint)
   
    #4 MW pi/2
    if LDE_DO_MW:
        e.add(msmnt.CORPSE_pi2, 
            start = -msmnt.params_lt2['MW_opt_puls1_separation'],
            refpulse = 'opt pi 1', 
            refpoint = 'start', 
            refpoint_new = 'end')
    #5 HHsync
    syncpulse_name = e.add(msmnt.HH_sync, refpulse = 'opt pi 1', refpoint = 'start', refpoint_new = 'end')
    
    #6 plugate 1
    e.add(msmnt.plu_gate, name = 'plu gate 1', refpulse = 'opt pi 1')

    #8 MW pi
    # if LDE_DO_MW:
    #     e.add(msmnt.CORPSE_pi, start = - msmnt.params_lt2['MW_opt_puls2_separation'],
    #             refpulse = 'opt pi 2', refpoint = 'start', refpoint_new = 'end')
    
    #10 plugate 2
    e.add(msmnt.plu_gate, name = 'plu gate 2', refpulse = 'opt pi {}'.format(OPT_PI_PULSES))
    
    #11 plugate 3
    e.add(pulse.cp(msmnt.plu_gate, 
            length = msmnt.params_lt2['PLU_gate_3_duration']), 
        name = 'plu gate 3', 
        start = msmnt.params_lt2['PLU_3_delay'], 
        refpulse = 'plu gate 2')
    
    #12 plugate 4
    e.add(msmnt.plu_gate, name = 'plu gate 4', start = msmnt.params_lt2['PLU_4_delay'],
            refpulse = 'plu gate 3')
    
    #13 final delay
    # e.add(pulse.cp(msmnt.plu_gate, 
    #         amplitude = 0, 
    #         length = msmnt.params['finaldelay']), 
    #     refpulse = 'plu gate 4')
    
    #14 optional more opt pulses for TPQI

    return e

class TeleportationSlave:

    def __init__(self):
        self.params = m2.MeasurementParameters('JointParameters')
        self.params_lt1 = m2.MeasurementParameters('LT1Parameters')
        self.params_lt2 = m2.MeasurementParameters('LT2Parameters')

        self.awg = qt.instruments['AWG_lt1']

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

        N_pol_decision_element = _lt1_N_polarization_decision_element(self)
        N_pol_element = _lt1_N_pol_element(self)
        start_LDE_element = _lt1_start_LDE_element(self)
        LDE_element = _lt1_LDE_element(self)
        BSM_element = _lt1_BSM_element(self)
        dummy_element = _lt1_dummy_element(self)
        adwin_lt1_trigger_element = _lt1_adwin_LT1_trigger_element(self)

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
            # jump_target = 'BSM',
            repetitions = self.params['LDE_attempts_before_CR'])

        self.lt1_seq.append(name = 'LDE_timeout',
            wfname = adwin_lt1_trigger_element.name,
            goto_target = 'N_pol_decision')


        elements = []
        elements.append(N_pol_decision_element)
        elements.append(adwin_lt1_trigger_element)
        elements.append(start_LDE_element)
        elements.append(dummy_element)
        
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

#************************ Sequence elements LT1   ******************************
def _lt1_N_polarization_decision_element(msmnt):
    """
    This is just an empty element that needs to be long enough for the
    adwin to decide whether we need to do CR (then it times out) or
    jump to the LDE sequence.
    """

    e = element.Element('N_pol_decision', pulsar = qt.pulsar_remote)
    e.append(pulse.cp(msmnt.T_pulse, length=10e-6))

    return e

def _lt1_N_pol_element(msmnt):
    """
    This is the element we will run to polarize the nuclear spin after each CR
    checking.
    """
    e = element.Element('N_pol', pulsar = qt.pulsar_remote)

    # TODO not yet implemented
    e.append(pulse.cp(msmnt.T_pulse, length=1e-6))

    return e

def _lt1_start_LDE_element(msmnt):
    """
    This element triggers the LDE sequence on LT2.
    """
    e = element.Element('start_LDE', pulsar = qt.pulsar_remote)
    e.append(pulse.cp(msmnt.AWG_LT2_trigger_pulse, 
        length = 1e-6,
        amplitude = 0))
    e.append(msmnt.AWG_LT2_trigger_pulse)

    return e

def _lt1_LDE_element(msmnt):
    """
    This element contains the LDE part for LT1, i.e., spin pumping and MW pulses
    for the LT1 NV in the real experiment.
    """
    e = element.Element('LDE_LT1', pulsar = qt.pulsar_remote, global_time = True)

    # this pulse to ensure that the element has equal length as the lt2 element
    e.add(pulse.cp(msmnt.SP_pulse,
            amplitude = 0,
            length = msmnt.params['LDE_element_length']))
    #
    #1 SP
    e.add(pulse.cp(msmnt.SP_pulse,
            amplitude = 0, 
            length = msmnt.params_lt1['initial_delay']), 
            name = 'initial_delay')
    e.add(pulse.cp(msmnt.SP_pulse, 
            length = msmnt.params['LDE_SP_duration'], 
            amplitude = 1.0),
            name = 'spinpumping',
            refpulse = 'initial_delay')


    #2 MW pi/2
    if LDE_DO_MW:
        e.add(msmnt.pi2_pulse, name = 'mw_pi2_pulse', 
                start = msmnt.params_lt1['MW_wait_after_sp'],
                refpulse = 'spinpumping', refpoint = 'end', refpoint_new = 'start')

    #3 MW pi
    if LDE_DO_MW:
        e.add(msmnt.pi_pulse, name = 'mw_pi_pulse',
                start = msmnt.params_lt1['MW_separation'],
                refpulse = 'mw_pi2_pulse', refpoint = 'end', refpoint_new = 'start')
        
    # e.add(pulse.cp(msmnt.TIQ_pulse, duration = msmnt.params_lt1['finaldelay']))
    
    # need some waiting pulse on IQ here to be certain to operate on spin echo after

    return e

def _lt1_adwin_LT1_trigger_element(msmnt):
    """
    sends a trigger to Adwin LT1 to notify we go back to CR.
    """
    e = element.Element('adwin_LT1_trigger', pulsar = qt.pulsar_remote)
    e.append(msmnt.adwin_lt1_trigger_pulse)
    return e

def _lt1_BSM_element(msmnt):
    """
    this element contains the BSM element. (Easiest way: only one element, then there's less
        chance for error when we don't need all the triggers -- however, then we need
        the timing to be correctly calibrated!)
    """
    e = element.Element('BSM', pulsar = qt.pulsar_remote, global_time = True)

    # TODO not yet implemented
    e.append(pulse.cp(msmnt.T_pulse, length=1e-6))

    return e

def _lt1_dummy_element(msmnt):
    """
    This is a dummy element. It contains nothing. 
    It replaces the LDE element if we do not want to do LDE.
    """
    e = element.Element('dummy', pulsar = qt.pulsar_remote, global_time = True)
    
    e.append(pulse.cp(msmnt.T_pulse, length=1e-6))

    return e

### CONSTANTS AND FLAGS
YELLOW = True              # whether to use yellow on lt2
HH = False                # if False no HH data acquisition from within qtlab.
DO_POLARIZE_N = False      # if False, no N-polarization sequence on LT1 will be used
DO_SEQUENCES = True      # if False, we won't use the AWG at all
DO_LDE_SEQUENCE = True    # if False, no LDE sequence (both setups) will be done
LDE_DO_MW = False         # if True, there will be MW in the LDE seq
MAX_HHDATA_LEN = int(100e6)
DO_OPT_RABI_AMP_SWEEP = False # if true, we sweep the rabi parameters instead of doing LDE; essentially this only affects the sequence we make
HH_MIN_SYNC_TIME = 0 # 9 us
HH_MAX_SYNC_TIME = 3e6 # 10.2 us
OPT_PI_PULSES = 5


       
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
    default_msmt('hist-checking-lt2')

                                                                                                                                                                                                                                                                                          