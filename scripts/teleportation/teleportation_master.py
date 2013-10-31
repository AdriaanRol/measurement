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

        # self.params_lt1['do_N_polarization'] = 1 if DO_POLARIZE_N else 0
        #for the sequencer and saving
        self.params_lt2['MW_during_LDE'] = 1 if LDE_DO_MW_LT2 else 0
        self.params['opt_pi_pulses'] = OPT_PI_PULSES

        #for saving only
        self.params_lt1['do_sequences'] = 1 if DO_SEQUENCES else 0
        self.params_lt1['do_LDE_sequence'] = 1 if DO_LDE_SEQUENCE else 0
        self.params_lt1['use_yellow_lt2'] = YELLOW_lt2
        self.params_lt1['use_yellow_lt1'] = YELLOW_lt1

    
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

        # LT1 laser configuration

        self.params_lt1['E_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                [self.E_aom_lt1.get_pri_channel()]
        self.params_lt1['A_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                [self.A_aom_lt1.get_pri_channel()]
        self.params_lt1['yellow_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                [self.yellow_aom_lt1.get_pri_channel()]
        self.params_lt1['green_laser_DAC_channel'] = self.adwins['adwin_lt1']['ins'].get_dac_channels()\
                [self.green_aom_lt1.get_pri_channel()]
        # self.params['gate_DAC_channel'] = self.adwin.get_dac_channels()\
        #        ['gate']
            
        # self.params_lt1['repump_laser_DAC_channel'] = self.params_lt1['green_laser_DAC_channel']
        self.params_lt1['repump_laser_DAC_channel'] = self.params_lt1['yellow_laser_DAC_channel']

        self.params_lt1['E_CR_voltage'] = \
                self.E_aom_lt1.power_to_voltage(
                        self.params_lt1['E_CR_amplitude'])
        self.params_lt1['A_CR_voltage'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['A_CR_amplitude'])

        self.params_lt1['E_SP_voltage'] = \
                self.E_aom_lt1.power_to_voltage(
                        self.params_lt1['E_SP_amplitude'])
        self.params_lt1['A_SP_voltage'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['A_SP_amplitude'])

        self.params_lt1['E_RO_voltage'] = \
                self.E_aom_lt1.power_to_voltage(
                        self.params_lt1['E_RO_amplitude'])
        self.params_lt1['A_RO_voltage'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['A_RO_amplitude'])
                       
        self.params_lt1['repump_voltage'] = \
                self.repump_aom_lt1.power_to_voltage(
                        self.params_lt1['repump_amplitude'])

        self.params_lt1['E_N_randomize_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['E_N_randomize_amplitude'])

        self.params_lt1['A_N_randomize_voltage'] = \
            self.A_aom.power_to_voltage(
                    self.params['A_N_randomize_amplitude'])

        self.params_lt1['repump_N_randomize_voltage'] = \
            self.repump_aom.power_to_voltage(
                    self.params['repump_N_randomize_amplitude'])
               
        # LT2 laser configuration

        self.params_lt2['Ey_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                [self.Ey_aom_lt2.get_pri_channel()]
        self.params_lt2['A_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
                [self.A_aom_lt2.get_pri_channel()]
        self.params_lt2['green_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
               [self.green_aom_lt2.get_pri_channel()]
        self.params_lt2['yellow_laser_DAC_channel'] = self.adwins['adwin_lt2']['ins'].get_dac_channels()\
               [self.yellow_aom_lt2.get_pri_channel()]

        if YELLOW_lt2:
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
        # self.params_lt2['SP_voltage_AWG_yellow'] = \
        #         self.repump_aom_lt2.power_to_voltage(
        #                 self.params_lt2['AWG_yellow_power'], controller='sec')
        
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params_lt2['SP_voltage_AWG'])
        # qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params_lt2['SP_voltage_AWG_yellow'])

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """        
        self.yellow_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_power(0.)
        self.E_aom_lt1.set_power(0.)
        self.A_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_cur_controller('ADWIN')
        self.E_aom_lt1.set_cur_controller('ADWIN')
        self.A_aom_lt1.set_cur_controller('ADWIN')
        self.yellow_aom_lt1.set_cur_controller('ADWIN')
        self.yellow_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_power(0.)
        self.E_aom_lt1.set_power(0.)
        self.A_aom_lt1.set_power(0.)

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

        dummy_element = tseq._lt2_dummy_element(self)
        LDE_element = tseq._lt2_LDE_element(self)
        finished_element = tseq._lt2_sequence_finished_element(self)

        self.lt2_seq.append(name = 'LDE_LT2',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            trigger_wait = True,
            goto_target = 'LDE_LT2',
            repetitions = self.params['LDE_attempts_before_CR'])

        if DO_DD:
            self.lt2_seq, total_elt_time, elts = tseq._lt2_dynamical_decoupling(self,
                self.lt2_seq, 
                name = 'DD',
                time_offset = LDE_element.length(),
                use_delay_reps = not(DO_READOUT))
        else:
            self.lt2_seq.append(name = 'DD',
                wfname = dummy_element.name,
                goto_target = 'LT2_ready_for_RO')

        #A_[ms,mi]
        #Y:=0 phase, X:=90

        ################################################### FF, DD and RO ##################################################################
        #TWO OPTIONS 'ALLES, of NIETS':
        #alles:
        #1. First program feaad forward pulse(s), independent of source_state_basis, but dependent on BSM RO result (and psi-/+)
        #2. Then program tomography (ro pulse), dependent on source_state_basis, but independent on BSM RO result (and psi-/+)
        #niets:
        #both FF and RO in one pulse, depending on source_state_basis, BSM RO result (and psi-/+)
        if DO_DD and DO_READOUT:
            RO_time_offset = LDE_element.length() + total_elt_time

            id_el      = tseq._lt2_final_id(self,  name = 'FF_Id',  time_offset = RO_time_offset)
            piY_el     = tseq._lt2_final_pi(self,  name = 'FF_Y',   time_offset = RO_time_offset, CORPSE_pi_phase = 0)
            
            pi2y_el    = tseq._lt2_final_pi2(self, name = 'FF_y',   time_offset = RO_time_offset, CORPSE_pi2_phase = 0)
            pi2miny_el = tseq._lt2_final_pi2(self, name = 'FF_-y',  time_offset = RO_time_offset, CORPSE_pi2_phase = 180)

            pi2x_el    = tseq._lt2_final_pi2(self, name = 'FF_x',   time_offset = RO_time_offset, CORPSE_pi2_phase =  90)
            pi2minx_el = tseq._lt2_final_pi2(self, name = 'FF_-x',  time_offset = RO_time_offset, CORPSE_pi2_phase = -90)
              

            if  self.params['source_state_basis'] == 'Z' and self.params['ro_basis'] == 'Z': 
                
                A00_psimin_RO_el  = id_el
                A01_psimin_RO_el  = piY_el
                A10_psimin_RO_el  = id_el
                A11_psimin_RO_el  = piY_el
                
                A00_psiplus_RO_el = piY_el
                A01_psiplus_RO_el = id_el 
                A10_psiplus_RO_el = piY_el
                A11_psiplus_RO_el = id_el

            elif self.params['source_state_basis'] == 'Z' and self.params['ro_basis'] == '-Z': 
                
                A00_psimin_RO_el  = piY_el
                A01_psimin_RO_el  = id_el
                A10_psimin_RO_el  = piY_el
                A11_psimin_RO_el  = id_el
                
                A00_psiplus_RO_el = id_el
                A01_psiplus_RO_el = piY_el
                A10_psiplus_RO_el = id_el
                A11_psiplus_RO_el = piY_el

            elif  self.params['source_state_basis'] == 'X' and self.params['ro_basis'] == 'Z': 
                
                A00_psimin_RO_el  = pi2miny_el
                A01_psimin_RO_el  = pi2y_el
                A10_psimin_RO_el  = pi2y_el
                A11_psimin_RO_el  = pi2miny_el
                
                A00_psiplus_RO_el = pi2y_el
                A01_psiplus_RO_el = pi2miny_el
                A10_psiplus_RO_el = pi2miny_el
                A11_psiplus_RO_el = pi2y_el

            elif  self.params['source_state_basis'] == 'X' and self.params['ro_basis'] == '-Z': 
                
                A00_psimin_RO_el  = pi2y_el
                A01_psimin_RO_el  = pi2miny_el
                A10_psimin_RO_el  = pi2miny_el
                A11_psimin_RO_el  = pi2y_el
                
                A00_psiplus_RO_el = pi2miny_el
                A01_psiplus_RO_el = pi2y_el
                A10_psiplus_RO_el = pi2y_el
                A11_psiplus_RO_el = pi2miny_el

            elif  self.params['source_state_basis'] == 'Y' and self.params['ro_basis'] == 'Z': 
                
                A00_psimin_RO_el  = pi2x_el
                A01_psimin_RO_el  = pi2x_el
                A10_psimin_RO_el  = pi2minx_el
                A11_psimin_RO_el  = pi2minx_el
                
                A00_psiplus_RO_el = pi2minx_el
                A01_psiplus_RO_el = pi2minx_el
                A10_psiplus_RO_el = pi2x_el
                A11_psiplus_RO_el = pi2x_el

            elif  self.params['source_state_basis'] == 'Y' and self.params['ro_basis'] == '-Z': 

                A00_psimin_RO_el  = pi2minx_el
                A01_psimin_RO_el  = pi2minx_el
                A10_psimin_RO_el  = pi2x_el
                A11_psimin_RO_el  = pi2x_el
                
                A00_psiplus_RO_el = pi2x_el
                A01_psiplus_RO_el = pi2x_el
                A10_psiplus_RO_el = pi2minx_el
                A11_psiplus_RO_el = pi2minx_el
            else:
                raise Exception('source_state_basis/ro_basis not recognized. ')

            
            self.lt2_seq.append(name = 'A00_psi-', 
                wfname = A00_psimin_RO_el.name,
                goto_target = 'LT2_ready_for_RO')
            self.lt2_seq.append(name = 'A01_psi-', 
                wfname = A01_psimin_RO_el.name,
                goto_target = 'LT2_ready_for_RO')
            self.lt2_seq.append(name = 'A10_psi-', 
                wfname = A10_psimin_RO_el.name,
                goto_target = 'LT2_ready_for_RO')
            self.lt2_seq.append(name = 'A11_psi-', 
                wfname = A11_psimin_RO_el.name,
                goto_target = 'LT2_ready_for_RO')
            self.lt2_seq.append(name = 'A00_psi+', 
                wfname = A00_psiplus_RO_el.name,
                goto_target = 'LT2_ready_for_RO')
            self.lt2_seq.append(name = 'A01_psi+', 
                wfname = A01_psiplus_RO_el.name,
                goto_target = 'LT2_ready_for_RO')
            self.lt2_seq.append(name = 'A10_psi+', 
                wfname = A10_psiplus_RO_el.name,
                goto_target = 'LT2_ready_for_RO')
            self.lt2_seq.append(name = 'A11_psi+', 
                wfname = A11_psiplus_RO_el.name,
                goto_target = 'LT2_ready_for_RO')

        ################################################### END FF, DD and RO ##################################################################
        ### JUMPING
        # EV0: first BSM: ms0 = 0, ms-1 = 1
        # EV1: second BSM: ms0 = 0, ms-1 = 1
        # EV2: EMPTY - -- 1 = decoupling, 0 = FF
        # EV3: PLU: psi+ = 0,  psi- = 1
        # int('xxxx',2) --> EV (3210)

        self.lt2_seq.set_djump(True)
        if DO_DD:
            # note: A01 etc. gives out nitrogen value first, jump expects electron RO first. 
            self.lt2_seq.add_djump_address(int('1100',2),'A00_psi-') 
            self.lt2_seq.add_djump_address(int('1101',2),'A01_psi-')
            self.lt2_seq.add_djump_address(int('1110',2),'A10_psi-')
            self.lt2_seq.add_djump_address(int('1111',2),'A11_psi-')
            self.lt2_seq.add_djump_address(int('0100',2),'A00_psi+')
            self.lt2_seq.add_djump_address(int('0101',2),'A01_psi+')
            self.lt2_seq.add_djump_address(int('0110',2),'A10_psi+')
            self.lt2_seq.add_djump_address(int('0111',2),'A11_psi+')

            self.lt2_seq.add_djump_address(int('1000',2),'DD') 
            self.lt2_seq.add_djump_address(int('1001',2),'DD')
            self.lt2_seq.add_djump_address(int('1010',2),'DD') 
            self.lt2_seq.add_djump_address(int('1011',2),'DD') 
            self.lt2_seq.add_djump_address(int('0000',2),'DD') 
            self.lt2_seq.add_djump_address(int('0001',2),'DD') 
            self.lt2_seq.add_djump_address(int('0010',2),'DD') 
            self.lt2_seq.add_djump_address(int('0011',2),'DD')
        else:
            for i in range(16):
                self.lt2_seq.add_djump_address(i,'DD')

        self.lt2_seq.append(name = 'LT2_ready_for_RO',
            wfname = finished_element.name,
            goto_target = 'LDE_LT2')

        ### AND ADD READOUT PULSES
        elements = []
        elements.append(dummy_element)
        
        if DO_LDE_SEQUENCE:
            elements.append(LDE_element)

        if DO_DD:
            for e in elts: #the dynamical decoupling sequence elements
                if e not in elements:
                    elements.append(e)

            if DO_READOUT:
                elements.append(A00_psimin_RO_el)
                elements.append(A01_psimin_RO_el)
                elements.append(A10_psimin_RO_el)
                elements.append(A11_psimin_RO_el)
                elements.append(A00_psiplus_RO_el)
                elements.append(A01_psiplus_RO_el)
                elements.append(A10_psiplus_RO_el)
                elements.append(A11_psiplus_RO_el)
        elements.append(finished_element)

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
        T0 = time.time()

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
            
            self.hharp.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
            qt.msleep(1)

        # then the adwins; since the LT1 adwin triggers both adwin LT2 and AWGs, this is the last one
        self.start_lt2_process()
        qt.msleep(0.1)
        self.start_lt1_process()

        # monitor keystrokes
        self.start_keystroke_monitor('abort')

        print misc.start_msg
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
        
        self.adwins['adwin_lt1']['ins'].set_teleportation_var(kill_by_CR=1)
        self.adwins['adwin_lt2']['ins'].set_teleportation_var(kill_by_CR=1)
        qt.msleep(2)

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
                # ('PLU_Bell_states', reps), we took that out for now (oct 7, 2013)
                ('CR_before', reps),
                ('CR_probe_timer', reps), ])

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

        self.params_lt1['MW_during_LDE'] = 1 if LDE_DO_MW_LT1 else 0


    def update_definitions(self):
        tseq.pulse_defs_lt1(self)

    def autoconfig(self):

        ### AWG voltages
        self.params_lt1['SP_voltage_AWG'] = \
                self.A_aom_lt1.power_to_voltage(
                        self.params_lt1['AWG_SP_power'], controller='sec')

        self.params_lt1['SP_voltage_AWG_yellow'] = \
                self.repump_aom_lt1.power_to_voltage(
                        self.params_lt1['AWG_yellow_power'], controller='sec')    

        qt.pulsar_remote.set_channel_opt('Velocity1AOM', 'high', self.params_lt1['SP_voltage_AWG'])
        qt.pulsar_remote.set_channel_opt('YellowAOM', 'high', self.params_lt1['SP_voltage_AWG_yellow'])


    def lt1_sequence(self):
        self.lt1_seq = pulsar.Sequence('TeleportationLT1')
        
        mbi_elt = tseq._lt1_mbi_element(self)
        start_LDE_element = tseq._lt1_start_LDE_element(self)
        LDE_element = tseq._lt1_LDE_element(self)
        dummy_element = tseq._lt1_dummy_element(self)
        adwin_lt1_trigger_element = tseq._lt1_adwin_LT1_trigger_element(self)
        N_init_element, BSM_CNOT_elt, BSM_UNROT_elt = tseq._lt1_N_init_and_BSM_for_teleportation(self)
        N_RO_elt = tseq._lt1_N_RO_elt(self)

        self.lt1_seq.append(name = 'MBI',
            trigger_wait = True,
            wfname = mbi_elt.name,
            jump_target = 'start_LDE',
            goto_target = 'MBI')

        self.lt1_seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_LDE_element.name)

        self.lt1_seq.append(name = 'LDE_LT1',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            jump_target = ('N_init' if DO_BSM else 'BSM_dummy'),
            repetitions = self.params['LDE_attempts_before_CR'])

        self.lt1_seq.append(name = 'LDE_timeout',
            wfname = adwin_lt1_trigger_element.name,
            goto_target = 'MBI')

        if DO_BSM:
            self.lt1_seq.append(name = 'N_init', 
                wfname = N_init_element.name)

            self.lt1_seq.append(name = 'BSM_CNOT',
                wfname = BSM_CNOT_elt.name)

            self.lt1_seq.append(name = 'BSM_H_UNROT',
                wfname = BSM_UNROT_elt.name)

            self.lt1_seq.append(name = 'sync_before_first_ro', 
                wfname = adwin_lt1_trigger_element.name)

            for i in range(self.params_lt1['N_RO_repetitions']):
                
                self.lt1_seq.append(name = 'N_RO-{}'.format(i+1),
                    trigger_wait = True,
                    wfname = N_RO_elt.name)
                
                self.lt1_seq.append(name = 'N_RO-{}_sync'.format(i+1), 
                    wfname = adwin_lt1_trigger_element.name, 
                    goto_target = 'MBI' if i==(self.params_lt1['N_RO_repetitions']-1) else 'N_RO-{}'.format(i+2) )
        
        else:
            self.lt1_seq.append(name = 'BSM_dummy',
                wfname = dummy_element.name)
            
            if DO_READOUT:
                self.lt1_seq.append(name = 'trigger_ro',
                    wfname = adwin_lt1_trigger_element.name,
                    goto_target = 'MBI')

        elements = []
        elements.append(mbi_elt)
        elements.append(adwin_lt1_trigger_element)
        elements.append(start_LDE_element)
        elements.append(dummy_element)

        if DO_BSM:
            elements.append(N_init_element)
            elements.append(BSM_CNOT_elt)
            elements.append(BSM_UNROT_elt)
            elements.append(N_RO_CNOT_elt)

        # if DO_POLARIZE_N:
        #     elements.append(N_pol_element)
        
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
YELLOW_lt2 = False              # whether to use yellow on lt2
YELLOW_lt1 = True               # whether to use yellow on lt1
HH = True                  # if False no HH data acquisition from within qtlab.
DO_POLARIZE_N = True      # if False, don't initialize N on lt1
DO_SEQUENCES = True        # if False, we won't use the AWG at all
DO_LDE_SEQUENCE = True     # if False, no LDE sequence (both setups) will be done
LDE_DO_MW_LT1 = True          # if True, there will be MW in the LDE seq
LDE_DO_MW_LT2 = False
MAX_HHDATA_LEN = int(100e6)
DO_OPT_RABI_AMP_SWEEP = False # if true, we sweep the rabi parameters instead of doing LDE; essentially this only affects the sequence we make
HH_MIN_SYNC_TIME = 0 # 9 us
HH_MAX_SYNC_TIME = 3e6 # 10.2 us
OPT_PI_PULSES = 2
DO_BSM = False
DO_DD = False
DO_READOUT = True
       
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
TeleportationMaster.E_aom_lt1 = qt.instruments['MatisseAOM_lt1']
TeleportationMaster.A_aom_lt1 = qt.instruments['NewfocusAOM_lt1']
TeleportationMaster.mwsrc_lt1 = qt.instruments['SMB100_lt1']

if YELLOW_lt1:
    TeleportationMaster.repump_aom_lt1 = TeleportationMaster.yellow_aom_lt1
else:
TeleportationMaster.repump_aom_lt1 = TeleportationMaster.green_aom_lt1

TeleportationMaster.repump_aom_lt1 = TeleportationMaster.green_aom_lt1

TeleportationMaster.yellow_aom_lt2 = qt.instruments['YellowAOM']
TeleportationMaster.green_aom_lt2 = qt.instruments['GreenAOM']
TeleportationMaster.Ey_aom_lt2 = qt.instruments['MatisseAOM']
TeleportationMaster.A_aom_lt2 = qt.instruments['NewfocusAOM']
TeleportationMaster.mwsrc_lt2 = qt.instruments['SMB100']
TeleportationMaster.awg_lt2 = qt.instruments['AWG']

if YELLOW_lt2:
    TeleportationMaster.repump_aom_lt2 = TeleportationMaster.yellow_aom_lt2
else:
    TeleportationMaster.repump_aom_lt2 = TeleportationMaster.green_aom_lt2

TeleportationMaster.hharp = qt.instruments['HH_400']

### This is ugly at this point. better merge classes at some point?
TeleportationSlave.repump_aom_lt1 = qt.instruments['GreemAOM_lt1']
TeleportationSlave.A_aom_lt1 = qt.instruments['NewfocusAOM_lt1']

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
    m = setup_msmt(''+name)

    if not DO_POLARIZE_N:
        m.params_lt1['MBI_threshold'] = 0

    m.params_lt1['max_CR_starts'] = 1000
    m.params_lt1['teleportation_repetitions'] = -1
    m.params['measurement_time'] = 30*60 # seconds -- will actually stop 10 sec earlier.

    start_msmt(m)
    finish_msmnt()

def program_lt2_sequence_only(name):
    m = setup_msmt(''+name)
    global DO_DD 
    DO_DD= True
    m.update_definitions()
    m.lt2_sequence()
    qt.instruments['AWG'].stop()
    qt.instruments['AWG'].set_runmode('CONT')

if __name__ == '__main__':
    #default_msmt('LT1_spin_photon_with_MBI_and_calib_pulses')
    program_lt2_sequence_only('test_DD')
                                                                                                                                                                                                                                                                                          