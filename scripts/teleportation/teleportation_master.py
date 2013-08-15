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


        self.params_lt1['use_yellow'] = YELLOW
        self.params_lt1['do_N_polarization'] = 1 if DO_POLARIZE_N else 0
        self.params_lt1['do_sequences'] = 1 if DO_SEQUENCES else 0
        self.params_lt1['do_LDE_sequence'] = 1 if DO_LDE_SEQUENCE else 0
        self.params['single_sync'] = 1 if LDE_SINGLE_SYNC else 0
        self.params['long_histogram'] =1 if LDE_LONG_HIST else 0
        self.params['MW_during_LDE'] = 1 if LDE_DO_MW else 0

    
    def update_definitions(self):
        """
        After setting the measurement parameters, execute this function to
        update pulses, etc.
        """
        tseq.pulse_defs_lt2(self)

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

            if DO_SEQUENCES:
                self.mwsrc_lt1.set_iq('on')
                self.mwsrc_lt1.set_pulm('on')
                self.mwsrc_lt1.set_frequency(self.params_lt1['mw_frq'])
                self.mwsrc_lt1.set_power(self.params_lt1['mw_power'])
                self.mwsrc_lt1.set_status('on' if DO_SEQUENCES else 'off')

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
            
            if DO_SEQUENCES:
                self.mwsrc_lt2.set_iq('on')
                self.mwsrc_lt2.set_pulm('on')
                self.mwsrc_lt2.set_frequency(self.params_lt2['mw_frq'])
                self.mwsrc_lt2.set_power(self.params_lt2['mw_power'])
                self.mwsrc_lt2.set_status('on' if DO_SEQUENCES else 'off')
                
                # have different types of sequences we can load.
                if DO_OPT_RABI_MSMT:
                    self.lt2_opt_rabi_sequence()
                else:
                    self.lt2_sequence()

        if HH:
            self.hharp.start_T2_mode()
            self.hharp.calibrate()

    ### sequence stuff
    def _lt2_sequence_finished_element(self):
        """
        last element of a two-setup sequence. Sends a trigger to ADwin LT2.
        """
        e = element.Element('LT2_finished', pulsar = qt.pulsar)
        e.append(self.adwin_lt2_trigger_pulse)
        return e

    def _lt2_dummy_element(self):
        """
        A 1us empty element we can use to replace 'real' elements for certain modes.
        """
        e = element.Element('Dummy', pulsar = qt.pulsar)
        e.append(pulse.cp(self.T_pulse, length=1e-6))
        return e

    def _lt2_LDE_element(self, **kw):
        """
        This element contains the LDE part for LT2, i.e., spin pumping and MW pulses
        for the LT2 NV and the optical pi pulses as well as all the markers for HH and PLU.
        """

        # variable parameters
        name = kw.pop('name', 'LDE_LT2')
        eom_pulse_amplitude = kw.pop('eom_pulse_amplitude', self.params_lt2['eom_pulse_amplitude'])

        ###
        e = element.Element(name, pulsar = qt.pulsar)#, global_time = True)

        #1 SP
        e.add(self.SP_pulse(amplitude = 0, length = self.params['initial_delay']), name = 'initial delay')
        e.add(self.SP_pulse(length = self.params['LDE_SP_duration'], amplitude = 1.0), 
                name = 'spinpumping', refpulse = 'initial delay')

        #2 Long histogram        
        if LDE_LONG_HIST:
            syncpulse_name = e.add(self.HH_sync, refpulse = 'spinpumping', refpoint = 'start', refpoint_new = 'end')
        
        #3 opt puls 1    
        e.add(pulse.cp(self.eom_aom_pulse, 
                eom_pulse_amplitude = eom_pulse_amplitude),
            name = 'opt pi 1', 
            start = self.params['wait_after_sp'],
            refpulse = 'spinpumping')
        
        #4 MW pi/2
        if LDE_DO_MW:
            e.add(self.CORPSE_pi2, start = - self.params_lt2['MW_opt_puls1_separation'],
                    refpulse = 'opt pi 1', refpoint = 'start', refpoint_new = 'end')
        #5 HHsync
        if not LDE_LONG_HIST:
            syncpulse_name = e.add(self.HH_sync, refpulse = 'opt pi 1', refpoint = 'start', refpoint_new = 'end')
        
        #6 plugate 1
        e.add(self.plu_gate, name = 'plu gate 1', refpulse = 'opt pi 1')

        #7 opt puls 2
        e.add(pulse.cp(self.eom_aom_pulse, 
                eom_pulse_amplitude = eom_pulse_amplitude), 
            name = 'opt pi 2', 
            start = self.params_lt2['opt_puls_separation'],
            refpulse = 'opt pi 1', refpoint = 'start')        

        #8 MW pi
        if LDE_DO_MW:
            e.add(self.CORPSE_pi, start = - self.params_lt2['MW_opt_puls2_separation'],
                    refpulse = 'opt pi 2', refpoint = 'start', refpoint_new = 'end')

        #9 HH sync 2 optional
        if not LDE_LONG_HIST and not LDE_SINGLE_SYNC:
            e.add(self.HH_sync, refpulse = 'opt pi 2', refpoint = 'start', refpoint_new = 'end')
        
        #10 plugate 2
        e.add(self.plu_gate, name = 'plu gate 2', refpulse = 'opt pi 2')
        #11 plugate 3
        e.add(pulse.cp(self.plu_gate, 
                length = self.params_lt2['PLU_gate_3_duration']), 
            name = 'plu gate 3', 
            start = self.params_lt2['PLU_3_delay'], 
            refpulse = 'plu gate 2')
        
        #12 plugate 4
        e.add(self.plu_gate, name = 'plu gate 4', start = self.params_lt2['PLU_4_delay'],
                refpulse = 'plu gate 3')
        #13 final delay
        e.add(pulse.cp(self.plu_gate, 
                amplitude = 0, 
                length = self.params['finaldelay']), 
            refpulse = 'plu gate 4')
        
        #14 optional more opt pulses for TPQI

        # if required, insert a marker after the sync pulse
        if DO_LDE_ATTEMPT_MARKER:
            e.add(self.HH_marker, name = 'attempt marker', start = 200e-9,
                refpulse = syncpulse_name, refpoint = 'start')

        return e

    def lt2_sequence(self):
        print "Make sequence... "

        self.lt2_seq = pulsar.Sequence('TeleportationLT2')

        dummy_element = self._lt2_dummy_element()
        LDE_element = self._lt2_LDE_element()
        finished_element = self._lt2_sequence_finished_element()

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
            lde_elt = self._lt2_LDE_element(name = 'OpticalRabi-{}'.format(i),
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

            # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
            dset_hhtime = self.h5data.create_dataset('HH_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            dset_hhchannel = self.h5data.create_dataset('HH_channel-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhspecial = self.h5data.create_dataset('HH_special-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhsynctime = self.h5data.create_dataset('HH_sync_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))        
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
                    hhtime, hhchannel, hhspecial, sync_time, newlength, t_ofl, t_lastsync = \
                        T2_tools.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync)

                    if newlength > 0:

                        dset_hhtime.resize((current_dset_length+newlength,))
                        dset_hhchannel.resize((current_dset_length+newlength,))
                        dset_hhspecial.resize((current_dset_length+newlength,))
                        dset_hhsynctime.resize((current_dset_length+newlength,))

                        dset_hhtime[current_dset_length:] = hhtime
                        dset_hhchannel[current_dset_length:] = hhchannel
                        dset_hhspecial[current_dset_length:] = hhspecial
                        dset_hhsynctime[current_dset_length:] = sync_time

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
                        current_dset_length = 0

                        self.h5data.flush()

        
        self.stop_adwin_processes()
        self.hharp.StopMeas()

    def run(self):
        self.autoconfig()
        data = self.measurement_loop()
        self.save(data)

    def save(self, HH_data=None):
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

        reps = self.adwin_var('adwin_lt1', 'completed_reps')
        self.save_adwin_data('adwin_lt2', 'data', ['completed_reps', 'total_CR_counts',
                ('CR_before', reps),
                ('CR_after', reps),
                ('CR_hist', ADWINLT2_MAX_CR_HIST_CTS),
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

    def update_definitions(self):
        tseq.pulse_defs_lt1(self)

    ### Sequence
    def _lt1_N_polarization_decision_element(self):
        """
        This is just an empty element that needs to be long enough for the
        adwin to decide whether we need to do CR (then it times out) or
        jump to the LDE sequence.
        """

        e = element.Element('N_pol_decision', pulsar = qt.pulsar_remote)
        e.append(pulse.cp(self.T_pulse, length=10e-6))

        return e

    def _lt1_N_pol_element(self):
        """
        This is the element we will run to polarize the nuclear spin after each CR
        checking.
        """
        e = element.Element('N_pol', pulsar = qt.pulsar_remote)

        # TODO not yet implemented
        e.append(pulse.cp(self.T_pulse, length=1e-6))

        return e

    def _lt1_start_LDE_element(self):
        """
        This element triggers the LDE sequence on LT2.
        """
        e = element.Element('start_LDE', pulsar = qt.pulsar_remote)
        e.append(pulse.cp(self.AWG_LT2_trigger_pulse, 
            length = 1e-6,
            amplitude = 0))
        e.append(self.AWG_LT2_trigger_pulse)

        return e

    def _lt1_LDE_element(self):
        """
        This element contains the LDE part for LT1, i.e., spin pumping and MW pulses
        for the LT1 NV in the real experiment.
        """
        e = element.Element('LDE_LT1', pulsar = qt.pulsar_remote, global_time = True)

        # TODO not yet implemented
        e.append(pulse.cp(self.T_pulse, length=11828e-9))

        return e

    def _lt1_adwin_LT1_trigger_element(self):
        """
        sends a trigger to Adwin LT1 to notify we go back to CR.
        """
        e = element.Element('adwin_LT1_trigger', pulsar = qt.pulsar_remote)
        e.append(self.adwin_lt1_trigger_pulse)
        return e

    def _lt1_BSM_element(self):
        """
        this element contains the BSM element. (Easiest way: only one element, then there's less
            chance for error when we don't need all the triggers -- however, then we need
            the timing to be correctly calibrated!)
        """
        e = element.Element('BSM', pulsar = qt.pulsar_remote, global_time = True)

        # TODO not yet implemented
        e.append(pulse.cp(self.T_pulse, length=1e-6))

        return e

    def _lt1_dummy_element(self):
        """
        This is a dummy element. It contains nothing. 
        It replaces the LDE element if we do not want to do LDE.
        """
        e = element.Element('dummy', pulsar = qt.pulsar_remote, global_time = True)
        
        e.append(pulse.cp(self.T_pulse, length=1e-6))

        return e

    def lt1_sequence(self):
        self.lt1_seq = pulsar.Sequence('TeleportationLT1')

        N_pol_decision_element = self._lt1_N_polarization_decision_element()
        N_pol_element = self._lt1_N_pol_element()
        start_LDE_element = self._lt1_start_LDE_element()
        LDE_element = self._lt1_LDE_element()
        BSM_element = self._lt1_BSM_element()
        dummy_element = self._lt1_dummy_element()
        adwin_lt1_trigger_element = self._lt1_adwin_LT1_trigger_element()

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

### CONSTANTS AND FLAGS
EXEC_FROM = 'lt2'
USE_LT1 = True
USE_LT2 = True
YELLOW = True
HH = True                 # if False no HH data acquisition from within qtlab.
DO_POLARIZE_N = True      # if False, no N-polarization sequence on LT1 will be used
DO_SEQUENCES = True       # if False, we won't use the AWG at all
DO_LDE_SEQUENCE = True    # if False, no LDE sequence (both setups) will be done
LDE_LONG_HIST = True      # if True there will be only 1 HH sync at the beginning of LDE
LDE_SINGLE_SYNC = True    # if False, every opt puls has its own sync
LDE_DO_MW = False         # if True, there will be MW in the LDE seq
MAX_HHDATA_LEN = int(100e6)
DO_LDE_ATTEMPT_MARKER = True # if True, insert a marker to the HH after each sync
DO_OPT_RABI_MSMT = True # if true, we sweep the rabi parameters instead of doing LDE; essentially this only affects the sequence we make
       
### configure the hardware (statics)
TeleportationMaster.adwins = {
    'adwin_lt1' : {
        'ins' : qt.instruments['adwin_lt1'] if EXEC_FROM=='lt2' else qt.instruments['adwin'],
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

TeleportationMaster.green_aom_lt2 = qt.instruments['GreenAOM']
TeleportationMaster.Ey_aom_lt2 = qt.instruments['MatisseAOM']
TeleportationMaster.A_aom_lt2 = qt.instruments['NewfocusAOM']
TeleportationMaster.mwsrc_lt2 = qt.instruments['SMB100']
TeleportationMaster.awg_lt2 = qt.instruments['AWG']
TeleportationMaster.repump_aom_lt2 = TeleportationMaster.green_aom_lt2

if YELLOW:
    TeleportationMaster.repump_aom_lt1 = TeleportationMaster.yellow_aom_lt1
else:
    TeleportationMaster.repump_aom_lt1 = TeleportationMaster.green_aom_lt1

TeleportationMaster.hharp = qt.instruments['HH_400']

### tool functions
def setup_msmt(name): 
    m = TeleportationMaster(name)
    m.load_settings()
    return m

def setup_slave_msmt():
    m = TeleportationSlave()
    m.load_settings()
    m.update_definitions()
    m.lt1_sequence()

def start_msmt(m):
    m.update_definitions()
    m.setup()
    m.run()

### measurements
def default_msmt(name):
    ### first start the slave
    ### TODO: make more like master if at some point more dynamic settings are needed
    setup_slave_msmt()

    # setup the master measurement
    m = setup_msmt('testing'+name)

    m.params_lt1['max_CR_starts'] = -1
    m.params_lt1['teleportation_repetitions'] = -1
    m.params['measurement_time'] = 5 # seconds; only affects msmt with HH.

    pts = 5
    m.params['opt_rabi_sweep_pts'] = pts
    m.params['eom_pulse_amplitudes'] = np.linspace(1,1.2,pts)

    start_msmt(m)

if __name__ == '__main__':
    default_msmt('optical_rabi_debug')

                                                                                                                                                                                                                                                                                          