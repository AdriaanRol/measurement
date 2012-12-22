# measure spin photon correlations as test before the actual LDE.

# TODO kill measurement sequence
# FIXME there are still some pars over 80! change!


debug_mode = False
debug_get_histogram=False
long_pulse_settings = False

import qt
import numpy as np
import time
from time import strftime
import msvcrt
import shutil

import measurement.measurement as meas
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels_lt2 as awgcfg
from measurement.config import adwins as adwincfg
from analysis import lde_calibration

# instruments
adwin_lt2 = qt.instruments['adwin']
adwin_lt1 = qt.instruments['adwin_lt1']
awg = qt.instruments['AWG']
hharp = qt.instruments['HH_400']
green_aom_lt2 = qt.instruments['GreenAOM']
E_aom_lt2 = qt.instruments['MatisseAOM']
A_aom_lt2 = qt.instruments['NewfocusAOM']
optimizor_lt2 = qt.instruments['optimiz0r']
optimizor_lt1 = qt.instruments['optimiz0r_lt1']
counters_lt2 = qt.instruments['counters']
counters_lt1 = qt.instruments['counters_lt1']
green_aom_lt1 = qt.instruments['GreenAOM_lt1']
E_aom_lt1 = qt.instruments['MatisseAOM_lt1']
A_aom_lt1 = qt.instruments['NewfocusAOM_lt1']
microwaves_lt2 = qt.instruments['SMB100']
microwaves_lt1 = qt.instruments['SMB100_lt1']
counters_lt2 = qt.instruments['counters']
counters_lt1 = qt.instruments['counters_lt1']
adwin_mdevice_lt1 = meas.AdwinMeasurementDevice(adwin_lt1, 'adwin_lt1')
adwin_mdevice_lt2 = meas.AdwinMeasurementDevice(adwin_lt2, 'adwin_lt2')

# prepare
awg.set_runmode('CONT')
green_aom_lt2.set_power(0.)
E_aom_lt2.set_power(0.)
A_aom_lt2.set_power(0.)
green_aom_lt1.set_power(0.)
E_aom_lt1.set_power(0.)
A_aom_lt1.set_power(0.)
counters_lt2.set_is_running(False)
counters_lt1.set_is_running(False)
microwaves_lt1.set_status('off')
microwaves_lt2.set_status('off')

#try opening the hydraharp: #NOTE needs to be a kb quit
if not(debug_mode):
    try:
        hharp.OpenDevice()
    except:
        print 'Failed opening Hydraharp!'
        for k in range(0,10):
            print 'Close the HYDRAHARP!'
            print 'You have %s seconds left'%k
            qt.msleep(1)
        try:
            hharp.OpenDevice()
        except:
            print 'Prepare for epic fail...'
else:
    try:
        hharp.CloseDevice()
    except:
        print 'Hydraharp not closed!!!'



class LDEMeasurement(meas.Measurement):

    def setup(self, adwin_mdevice_lt2, adwin_mdevice_lt1):
        self.adwin_lt1 = adwin_mdevice_lt1
        self.adwin_lt2 = adwin_mdevice_lt2
        self.measurement_devices.append(self.adwin_lt1)
        self.measurement_devices.append(self.adwin_lt2)

        self.adwin_lt1.process_data['lde'] = \
                [p for p in adwincfg.config['adwin_lt1_processes']['lde']['par']]
        self.adwin_lt2.process_data['lde'] = \
                [p for p in adwincfg.config['adwin_lt2_processes']['lde']['par']]
        
        if not debug_mode:
            hharp.start_T3_mode()
            hharp.calibrate()
            hharp.set_Binning(self.binsize_T3)

            microwaves_lt2.set_iq('on')
            microwaves_lt2.set_frequency(self.MW_freq_lt2)
            microwaves_lt2.set_pulm('on')
            microwaves_lt2.set_power(self.MW_power_lt2)
            
            microwaves_lt1.set_iq('on')
            microwaves_lt1.set_frequency(self.MW_freq_lt1)
            microwaves_lt1.set_pulm('on')
            microwaves_lt1.set_power(self.MW_power_lt1)
        
        return True

    def generate_sequence(self, do_program=True):
        awg.set_event_jump_timing('SYNC')
        self.seq = Sequence('lde')
        seq = self.seq
        
        # channels
        chan_hhsync = 'HH_sync'         # historically PH_start
        chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
        chan_plusync = 'PLU_gate'
        chan_plureset = 'debug_channel' 
        
        chan_alaser = 'AOM_Newfocus'
        chan_eom = 'EOM_Matisse'
        chan_eom_aom = 'EOM_AOM_Matisse'
        
        chan_mw_pm = 'MW_pulsemod'
        chan_mwI_lt2 = 'MW_Imod'
        chan_mwQ_lt2 = 'MW_Qmod'
        chan_mwI_lt1 = 'MW_Imod_lt1'
        chan_mwQ_lt1 = 'MW_Qmod_lt1'

        # check if MWpi and optical pi don't overlap:
        
        if self.wait_after_opt_pi >= self.opt_pi_separation - \
                self.eom_pulse_duration - self.total_pi_length:
            print '!!! =================== !!!'
            print 'WARNING: pi pulse and 2nd optical pi pulse might overlap!' 
            print 'Decrease variable wait_after_opt_pi' 
            print '!!! =================== !!!'
            

        # TODO study the current AWG configuration, then adapt this
        awgcfg.configure_sequence(self.seq, 'hydraharp', 'mw',
                LDE = { 
                    chan_eom_aom: { 'high' : self.eom_aom_amplitude },
                    chan_alaser: { 'high' : self.A_SP_amplitude, }
                    },
                )
        seq.add_element('lde', goto_target='idle', 
                repetitions=self.max_LDE_attempts, event_jump_target='idle',
                trigger_wait=True)

        # 1: spin pumping
        seq.add_pulse('initialdelay', chan_alaser, 'lde',
                start = 0, duration = 10, amplitude=0, )
        seq.add_pulse('spinpumping', chan_alaser, 'lde', 
                start = 0, duration = self.SP_duration,
                start_reference='initialdelay',
                link_start_to='end', amplitude=1)

        # 1a: PLU reset now on AWG
        seq.add_pulse('plu_reset_marker', chan_plureset, 'lde',
                start=0, duration=100,
                amplitude=2.0, start_reference='initialdelay',
                link_start_to='end')

        # 2: Pi/2 pulses on both spins
        start_ref='spinpumping'
        
        # Define pars for CORPSE pi/2 pulse
        seq.add_pulse('pi2_pulse_lt1', channel = chan_mwI_lt1, element = 'lde',
                start = self.wait_after_SP+(self.pulse_384_length+self.pulse_318_length+self.pulse_24_length-self.pi2_lt1_duration)/2.,
                start_reference = start_ref,link_start_to = 'end', 
                duration = self.pi2_lt1_duration, 
                amplitude = self.pi2_lt1_amplitude, shape = 'rectangular')
        seq.add_pulse('pulse_384_lt2', channel = chan_mwI_lt2, element = 'lde',
                start = self.wait_after_SP, start_reference = start_ref,link_start_to = 'end', 
                duration = self.pulse_384_length, 
                amplitude = self.CORPSE_pi_over_two_amp_lt2, shape = 'rectangular')
        seq.add_pulse('pulse_mod_384', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_384_length+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_384_length+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_384_length-self.pulse_384_length)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_384_lt2', link_start_to = 'start', 
                amplitude = self.MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_1', channel = chan_mw_pm, element = 'lde',
                start = 0,start_reference = 'pulse_384_lt2',link_start_to ='end', 
                duration = self.time_between_CORPSE, amplitude = 0)
        
        seq.add_pulse('pulse_318_lt2', channel = chan_mwI_lt2, element = 'lde',
                start = 0, start_reference = 'wait_1', link_start_to = 'end',
                duration = self.pulse_318_length, 
                amplitude = -self.CORPSE_pi_over_two_amp_lt2,shape = 'rectangular')
        seq.add_pulse('pulse_mod_318', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_318_length+\
                    2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_318_length+\
                    2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_318_length-self.pulse_318_length)/2 - \
                    self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_318_lt2', link_start_to = 'start', 
                amplitude = self.MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_2', channel = chan_mw_pm, element = 'lde',
                start = 0,start_reference = 'pulse_318_lt2',link_start_to ='end', 
                duration = self.time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24_lt2', channel = chan_mwI_lt2, element = 'lde',
                start = 0, start_reference = 'wait_2', link_start_to = 'end', 
                duration = self.pulse_24_length, 
                amplitude = self.CORPSE_pi_over_two_amp_lt2,shape = 'rectangular')
        seq.add_pulse('pulse_mod_24', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_24_length+\
                    2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_24_length+\
                    2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_24_length-self.pulse_24_length)/2 - \
                    self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_24_lt2', link_start_to = 'start', 
                amplitude = self.MW_pulsemod_amplitude)

        last = 'pulse_mod_24'

        # 3a: optical pi-pulse no 1
        i = 1

        
        seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.wait_after_pi2, duration = 50, 
                amplitude = 2.0, start_reference = last,  
                link_start_to = 'end')
        last = 'start'+str(i)

        seq.add_pulse('mrkr'+str(i), chan_hh_ma1, 'lde',
                start=-20, duration=50,
                amplitude=2.0, start_reference=last,
                link_start_to='start')

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = self.aom_start, duration = self.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_off_amplitude,
                start = self.eom_start, duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_pulse_amplitude - self.eom_off_amplitude,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset, duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot1,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot2,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration + \
                        self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration, 
                duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_pulse_amplitude + self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset, 
                duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot1, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot2, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration + self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_pulse'+str(i)

        # 3b: add pre-sync pulses for the HH
        for j in range(self.presync_pulses):
            if not debug_mode:
                pre_sync_amp = 2.0
            else:
                pre_sync_amp = 0.0

            seq.add_pulse('presync'+str(j), chan_hhsync, 'lde',         
                    start = -(j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = pre_sync_amp, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 3c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = 0,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )


        # 4: spin pi pulses
        
        # Define pars for CORPSE pi pulse
        seq.add_pulse('pi_pulse_lt1', channel = chan_mwI_lt1, element = 'lde',
                start = self.wait_after_opt_pi+(self.pulse_300_length+self.pulse_60_length+self.pulse_420_length-self.pi_lt1_duration)/2,
                start_reference = last,link_start_to = 'end', 
                duration = self.pi_lt1_duration, 
                amplitude = self.pi_lt1_amplitude, shape = 'rectangular')
        seq.add_pulse('pulse_420_lt2', channel = chan_mwI_lt2, element = 'lde',
                start = self.wait_after_opt_pi, start_reference = last,link_start_to = 'end', 
                duration = self.pulse_420_length, 
                amplitude = self.CORPSE_pi_amp_lt2, shape = 'rectangular')
        seq.add_pulse('pulse_mod_420', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_420_length+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_420_length+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_420_length-self.pulse_420_length)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_420_lt2', link_start_to = 'start', 
                amplitude = self.MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_3', channel = chan_mw_pm, element = 'lde',
                start = 0,start_reference = 'pulse_420_lt2',link_start_to ='end', 
                duration = self.time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_300_lt2', channel = chan_mwI_lt2, element = 'lde',
                start = 0, start_reference = 'wait_3', link_start_to = 'end',
                duration = self.pulse_300_length, 
                amplitude = -self.CORPSE_pi_amp_lt2,shape = 'rectangular')
        seq.add_pulse('pulse_mod_300', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_300_length+\
                    2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_300_length+\
                    2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_300_length-self.pulse_300_length)/2 - \
                    self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_300_lt2', link_start_to = 'start', 
                amplitude = self.MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_4', channel = chan_mw_pm, element = 'lde',
                start = 0,start_reference = 'pulse_300_lt2',link_start_to ='end', 
                duration = self.time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_60_lt2', channel = chan_mwI_lt2, element = 'lde',
                start = 0, start_reference = 'wait_4', link_start_to = 'end', 
                duration = self.pulse_60_length, 
                amplitude = self.CORPSE_pi_amp_lt2,shape = 'rectangular')
        seq.add_pulse('pulse_mod_60', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_60_length+\
                    2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_60_length+\
                    2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_60_length-self.pulse_60_length)/2 - \
                    self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_60_lt2', link_start_to = 'start', 
                amplitude = self.MW_pulsemod_amplitude)

        last = 'pulse_mod_60'

        # 5a: optical pi-pulse no2
        i = 2

        seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.opt_pi_separation, duration = 50, 
                amplitude = 2.0, start_reference = 'start'+str(i-1),  
                link_start_to = 'start') 
        last = 'start'+str(i)

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = self.aom_start, duration = self.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_off_amplitude,
                start = self.eom_start, duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_pulse_amplitude - self.eom_off_amplitude,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset, duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot1,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot2,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration + \
                        self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration, 
                duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_pulse_amplitude + self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset, 
                duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot1, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot2, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration + self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_pulse'+str(i)

        # 5b: add post-sync pulses for the HH
        for j in range(self.postsync_pulses):
            if not debug_mode:
                post_sync_amp = 2.0
            else:
                post_sync_amp = 0.0

            seq.add_pulse('postsync'+str(j),  chan_hhsync, 'lde',         
                    start = (j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = post_sync_amp, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 5c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = self.plu_2_start_offset,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )

        # 5d: two additional PLU gates
        seq.add_pulse('plu-gate3', chan_plusync, 'lde',
                start = self.plu_3_delay,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')
        seq.add_pulse('plu-gate4', chan_plusync, 'lde',
                start = self.plu_4_delay,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')

        # 6: basis rotation
        if self.basis_rot:
            Iamplt1 = np.cos(np.pi*self.basis_rot_angle/180.)*self.CORPSE_pi_over_two_amp_lt1
            Qamplt1 = np.sin(np.pi*self.basis_rot_angle/180.)*self.CORPSE_pi_over_two_amp_lt1
            Iamplt2 =  np.cos(np.pi*self.basis_rot_angle/180.)*self.CORPSE_pi_over_two_amp_lt2
            Qamplt2 = np.sin(np.pi*self.basis_rot_angle/180.)*self.CORPSE_pi_over_two_amp_lt2
            PMamp = self.MW_pulsemod_amplitude
        else:
            Iamplt1=Qamplt1=Iamplt2=Qamplt2=PMamp=0.

        seq.add_pulse('basis rot lt2 I', chan_mwI_lt2, 'lde',
                duration = self.basis_rot_duration_lt2,
                amplitude = Iamplt2,
                start_reference = last,
                start = self.wait_after_opt_pi2, 
                link_start_to = 'end' )
        seq.add_pulse('basis rot lt2 Q', chan_mwQ_lt2, 'lde',
                duration = self.basis_rot_duration_lt2,
                amplitude = Qamplt2,
                start_reference = last,
                start = self.wait_after_opt_pi2, 
                link_start_to = 'end' )        

        seq.add_pulse('basis rot lt1 I', chan_mwI_lt1, 'lde',
                duration = self.basis_rot_duration_lt1,
                amplitude = Iamplt1,
                start_reference = 'basis rot lt2 I',
                start = (self.basis_rot_duration_lt2-\
                        self.basis_rot_duration_lt1)/2,
                link_start_to = 'start' )
        seq.add_pulse('basis rot lt1 Q', chan_mwQ_lt1, 'lde',
                duration = self.basis_rot_duration_lt1,
                amplitude = Qamplt1,
                start_reference = 'basis rot lt2 I',
                start = (self.basis_rot_duration_lt2-\
                        self.basis_rot_duration_lt1)/2,
                link_start_to = 'start' )

        seq.add_pulse('basis rot pm', chan_mw_pm, 'lde',
                amplitude = PMamp,
                duration = max(self.basis_rot_duration_lt2+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.basis_rot_duration_lt1+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.basis_rot_duration_lt2-\
                            self.basis_rot_duration_lt1)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'basis rot lt2 I',
                link_start_to = 'start')

        
        # 7: final delay
        seq.add_pulse('final delay', chan_hhsync, 'lde',
                amplitude = 0,
                duration = self.finaldelay,
                start = 0,
                start_reference = 'plu-gate4',
                link_start_to = 'end' )

        # idle element
        seq.add_element('idle', goto_target='lde')
        seq.add_pulse('empty', chan_alaser, 'idle', start=0, duration = 1000, 
            amplitude = 0) 
        
       
        seq.set_instrument(awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()        
        
        return seq

    def generate_sequence_regular_pulses(self, do_program=True):
        awg.set_event_jump_timing('SYNC')
        self.seq = Sequence('lde')
        seq = self.seq
        
        # channels
        chan_hhsync = 'HH_sync'         # historically PH_start
        chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
        chan_plusync = 'PLU_gate'
        
        chan_alaser = 'AOM_Newfocus'
        chan_eom = 'EOM_Matisse'
        chan_eom_aom = 'EOM_AOM_Matisse'
        
        chan_mw_pm = 'MW_pulsemod'
        chan_mwI_lt2 = 'MW_Imod'
        chan_mwQ_lt2 = 'MW_Qmod'
        chan_mwI_lt1 = 'MW_Imod_lt1'
        chan_mwQ_lt1 = 'MW_Qmod_lt1'

        # check if MWpi and optical pi don't overlap:
        
        if self.wait_after_opt_pi >= self.opt_pi_separation - \
                self.eom_pulse_duration - self.pi_lt2_duration:
            print '!!! =================== !!!'
            print 'WARNING: pi pulse and 2nd optical pi pulse might overlap!' 
            print 'Decrease variable wait_after_opt_pi' 
            print '!!! =================== !!!'
            

        # TODO study the current AWG configuration, then adapt this
        awgcfg.configure_sequence(self.seq, 'hydraharp', 'mw',
                LDE = { 
                    chan_eom_aom: { 'high' : self.eom_aom_amplitude },
                    chan_alaser: { 'high' : self.A_SP_amplitude, }
                    },
                )
        seq.add_element('lde', goto_target='idle', 
                repetitions=self.max_LDE_attempts, event_jump_target='idle',
                trigger_wait=True)
                
        # 1: spin pumping
        seq.add_pulse('initialdelay', chan_alaser, 'lde',
                start = 0, duration = 10, amplitude=0, )
        seq.add_pulse('spinpumping', chan_alaser, 'lde', 
                start = 0, duration = self.SP_duration,
                start_reference='initialdelay',
                link_start_to='end', amplitude=1)

        # 2: Pi/2 pulses on both spins
        seq.add_pulse('pi/2-1 lt2', chan_mwI_lt2, 'lde',
                duration = self.pi2_lt2_duration,
                amplitude = self.pi2_lt2_amplitude,
                start_reference = 'spinpumping',
                start = self.wait_after_SP, 
                link_start_to = 'end' )
        seq.add_pulse('pi/2-1 lt1', chan_mwI_lt1, 'lde',
                duration = self.pi2_lt1_duration,
                amplitude = self.pi2_lt1_amplitude,
                start_reference = 'pi/2-1 lt2',
                start = (self.pi2_lt2_duration-self.pi2_lt1_duration)/2,
                link_start_to = 'start' )
        
        seq.add_pulse('pi/2-1 pm', chan_mw_pm, 'lde',
                amplitude = self.MW_pulsemod_amplitude,
                duration = max(self.pi2_lt2_duration+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.pi2_lt1_duration+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pi2_lt2_duration-self.pi2_lt1_duration)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'pi/2-1 lt2',
                link_start_to = 'start' )

        # 3a: optical pi-pulse no 1
        i = 1
        last = 'pi/2-1 pm'
        
        seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.wait_after_pi2, duration = 50, 
                amplitude = 2.0, start_reference = last,  
                link_start_to = 'end')
        last = 'start'+str(i)

        seq.add_pulse('mrkr'+str(i), chan_hh_ma1, 'lde',
                start=-20, duration=50,
                amplitude=2.0, start_reference=last,
                link_start_to='start')

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = self.aom_start, duration = self.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_off_amplitude,
                start = self.eom_start, duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_pulse_amplitude - self.eom_off_amplitude,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset, duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot1,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot2,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration + \
                        self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration, 
                duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_pulse_amplitude + self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset, 
                duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot1, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot2, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration + self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_pulse'+str(i)

        # 3b: add pre-sync pulses for the HH
        for j in range(self.presync_pulses):
            if not debug_mode:
                pre_sync_amp = 2.0
            else:
                pre_sync_amp = 0.0

            seq.add_pulse('presync'+str(j), chan_hhsync, 'lde',         
                    start = -(j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = pre_sync_amp, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 3c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = 0,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )


        # 4: spin pi pulses
        seq.add_pulse('pi lt2', chan_mwI_lt2, 'lde',
                duration = self.pi_lt2_duration,
                amplitude = self.pi_lt2_amplitude,
                start_reference = last,
                start = self.wait_after_opt_pi, 
                link_start_to = 'end' )
        seq.add_pulse('pi lt1', chan_mwI_lt1, 'lde',
                duration = self.pi_lt1_duration,
                amplitude = self.pi_lt1_amplitude,
                start_reference = 'pi lt2',
                start = (self.pi_lt2_duration-self.pi_lt1_duration)/2,
                link_start_to = 'start' )
        seq.add_pulse('pi pm', chan_mw_pm, 'lde',
                amplitude = self.MW_pulsemod_amplitude,
                duration = max(self.pi_lt2_duration+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.pi_lt1_duration+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pi_lt2_duration-self.pi_lt1_duration)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'pi lt2',
                link_start_to = 'start')

        # 5a: optical pi-pulse no2
        i = 2

        seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.opt_pi_separation, duration = 50, 
                amplitude = 2.0, start_reference = 'start'+str(i-1),  
                link_start_to = 'start') 
        last = 'start'+str(i)

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = self.aom_start, duration = self.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_off_amplitude,
                start = self.eom_start, duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_pulse_amplitude - self.eom_off_amplitude,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset, duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot1,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = self.eom_overshoot2,
                start = self.eom_start + self.eom_off_duration/2 + \
                        self.eom_pulse_offset + self.eom_pulse_duration + \
                        self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration, 
                duration = self.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_pulse_amplitude + self.eom_off_amplitude,
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset, 
                duration = self.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot1, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration, 
                duration = self.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.eom_overshoot2, 
                start = self.eom_start+self.eom_off_duration + \
                        int(self.eom_off_duration/2) + self.eom_pulse_offset + \
                        self.eom_pulse_duration + self.eom_overshoot_duration1, 
                duration = self.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_pulse'+str(i)

        # 5b: add post-sync pulses for the HH
        for j in range(self.postsync_pulses):
            if not debug_mode:
                post_sync_amp = 2.0
            else:
                post_sync_amp = 0.0

            seq.add_pulse('postsync'+str(j),  chan_hhsync, 'lde',         
                    start = (j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = post_sync_amp, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 5c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = self.plu_2_start_offset,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )

        # 5d: two additional PLU gates
        seq.add_pulse('plu-gate3', chan_plusync, 'lde',
                start = self.plu_3_delay,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')
        seq.add_pulse('plu-gate4', chan_plusync, 'lde',
                start = self.plu_4_delay,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')

        # 6: basis rotation
        if m.basis_rot:
            Iamplt1 = self.basis_rot_I_amplitude_lt1
            Qamplt1 = self.basis_rot_Q_amplitude_lt1
            Iamplt2 = self.basis_rot_I_amplitude_lt2
            Qamplt2 = self.basis_rot_Q_amplitude_lt2
            PMamp = self.MW_pulsemod_amplitude
        else:
            Iamplt1=Qamplt1=Iamplt2=Qamplt2=PMamp=0

        seq.add_pulse('basis rot lt2 I', chan_mwI_lt2, 'lde',
                duration = self.basis_rot_duration_lt2,
                amplitude = Iamplt2,
                start_reference = last,
                start = self.wait_after_opt_pi2, 
                link_start_to = 'end' )
        seq.add_pulse('basis rot lt2 Q', chan_mwQ_lt2, 'lde',
                duration = self.basis_rot_duration_lt2,
                amplitude = Qamplt2,
                start_reference = last,
                start = self.wait_after_opt_pi2, 
                link_start_to = 'end' )        

        seq.add_pulse('basis rot lt1 I', chan_mwI_lt1, 'lde',
                duration = self.basis_rot_duration_lt1,
                amplitude = Iamplt1,
                start_reference = 'basis rot lt2 I',
                start = (self.basis_rot_duration_lt2-\
                        self.basis_rot_duration_lt1)/2,
                link_start_to = 'start' )
        seq.add_pulse('basis rot lt1 Q', chan_mwQ_lt1, 'lde',
                duration = self.basis_rot_duration_lt1,
                amplitude = Qamplt1,
                start_reference = 'basis rot lt2 I',
                start = (self.basis_rot_duration_lt2-\
                        self.basis_rot_duration_lt1)/2,
                link_start_to = 'start' )

        seq.add_pulse('basis rot pm', chan_mw_pm, 'lde',
                amplitude = PMamp,
                duration = max(self.basis_rot_duration_lt2+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.basis_rot_duration_lt1+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.basis_rot_duration_lt2-\
                            self.basis_rot_duration_lt1)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'basis rot lt2 I',
                link_start_to = 'start')

        
        # 7: final delay
        seq.add_pulse('final delay', chan_hhsync, 'lde',
                amplitude = 0,
                duration = self.finaldelay,
                start = 0,
                start_reference = 'plu-gate4',
                link_start_to = 'end' )

        # idle element
        seq.add_element('idle', goto_target='lde')
        seq.add_pulse('empty', chan_alaser, 'idle', start=0, duration = 1000, 
            amplitude = 0) 
        
       
        seq.set_instrument(awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()        
        
        return seq


    def measure(self, adwin_lt2_params={}, adwin_lt1_params={}):
        self.adwin_lt1.process_params['lde'] = adwin_lt1_params
        self.adwin_lt2.process_params['lde'] = adwin_lt2_params

        awg.set_runmode('SEQ')
        awg.start()
        
        if not debug_mode:
            microwaves_lt2.set_status('on')
            microwaves_lt1.set_status('on')

            hharp.StartMeas(int(self.measurement_time * 1e3))
            qt.msleep(1)
            self.start_adwins(adwin_lt2_params,adwin_lt1_params)

            ch0_events, ch1_events, markers, rawdir = self.get_T3_pulsed_events(
                    sync_period = self.opt_pi_separation,
                    range_sync = int(self.opt_pi_separation / \
                            (2**self.binsize_T3)*1e-3),
                    start_ch0 = 0,
                    start_ch1 = 0,
                    max_pulses = 2,
                    save_markers = [2])

            self.rawdir = rawdir

        else:
            if debug_get_histogram:
                hharp.start_histogram_mode()
                hharp.calibrate()
                hharp.set_Binning(self.binsize_T3)
                hharp.set_HistoLen(self.histogram_length)
                hharp.StartMeas(int(self.measurement_time * 1e3))
                qt.msleep(1)
                self.start_adwins(adwin_lt2_params,adwin_lt1_params)
                while hharp.get_MeasRunning():
                    if(msvcrt.kbhit() and msvcrt.getch()=='q'):
                        print 'x pressed, quitting current run'
                        hharp.StopMeas()
                ch0_events=hharp.get_Histogram(0, clear=1)
                ch1_events=hharp.get_Histogram(1, clear=1)
                markers = list()
            else:
                self.start_adwins(adwin_lt2_params,adwin_lt1_params)
                ii=0
                while (ii<100):
                    qt.msleep(self.measurement_time/100)
                    if(msvcrt.kbhit() and msvcrt.getch()=='x'):
                       print 'x pressed, quitting current run'
                       break
                    ii+=1
                ch0_events = ch1_events = markers = list()
        
        adwin_lt1.stop_lde()
        adwin_lt2.stop_lde()
        awg.stop()
        microwaves_lt1.set_status('off')
        microwaves_lt2.set_status('off')
        qt.msleep(0.1)
        awg.set_runmode('CONT')        

        return ch0_events, ch1_events, markers

    def start_adwins():
        adwin_lt1.start_lde(load=True, **adwin_lt1_params)
        qt.msleep(1)
        adwin_lt2.start_lde(load=True, 
                set_phase_locking_on = self.set_phase_locking_on,
                set_gate_good_phase = self.set_gate_good_phase,
                **adwin_lt2_params)
        qt.msleep(1)  
   
    def get_T3_pulsed_events(self, sync_period, 
            range_sync, start_ch0=0, start_ch1=0, 
            max_pulses = 2, save_markers=[2,3,4], save_raw=True,
            raw_max_len=100000):
        """
        Get ch0 and ch1 events in T3 mode.
        Author: Wolfgang, July 1, 2012.

        Filtering options:
        range_sync: 
            how many bins after a sync are accepted
        start_ch0, start_ch1:
            minimum event time (in bins) after the sync
        max_pulses:
            how many syncs after a marker on channel 1 are taken into
            account
        
        other options:
        save_markers:
            all markers with channel in that list will be returned.

        returns:
            (ch0, ch1, markers)
            ch0: array with two columns: col1 = absolute sync no, col2 = time
            ch1: ditto
            markers: array with three columns:
                col1 = sync no, col2 = time, col3 = marker channel
        """
        
        if .001*hharp.get_ResolutionPS() * 2**15 < sync_period:
            print('Warning: resolution is too high to cover entire sync \
                    period in T3 mode, events might get lost.')

        ch0_events = zeros((0,2), dtype=int) # col 1: sync no (abs), col 2: event time
        ch1_events = zeros((0,2), dtype=int)
        markers = zeros((0,3), dtype=int) # col1 sync no, col2 time, col3 marker channel
        
        nsync_overflow = 0
        ch0_sync = 0
        ch0_time = 0
        ch1_sync = 0
        ch1_time = 0
        nsync_ma1 = -max_pulses

        if save_raw:
            timestamp = strftime('%Y%m%d%H%M%S')
            rawdir = os.path.join(qt.config['datadir'], strftime('%Y%m%d'), \
                strftime('%H%M%S')+'_LDE_rawdata')
            if not os.path.isdir(rawdir):
                os.makedirs(rawdir)
            rawdat = array([])
            rawidx = 0
            lengths = array([])
            times = array([])

        while hharp.get_MeasRunning() == True:
            length, data = hharp.get_TTTR_Data()

            # print length

            if save_raw:
                rawdat = append(rawdat, data[:length])
                lengths = append(lengths, length)
                times = append(times, int(strftime('%M%S')))
                
                if len(rawdat) > raw_max_len:
                    
                    #print len(rawdat)

                    savez(os.path.join(rawdir, 
                        timestamp+'_LDE_rawdata-%.3d' % rawidx), 
                        length=len(rawdat), data=rawdat)
                    
                    rawdat = array([])
                    rawidx += 1
            if(msvcrt.kbhit() and msvcrt.getch()=='x'):
                print 'x pressed, quitting current run'
                hharp.StopMeas()

        if save_raw:
            savez(os.path.join(rawdir, 'lengths'), lengths=lengths)
            savez(os.path.join(rawdir, 'times'), times=times)
            savez(os.path.join(rawdir, timestamp+'_LDE_rawdata-%.3d' % rawidx), 
                        length=len(rawdat), data=rawdat)
                            
        print "Detected events: %d / %d." % (len(ch0_events), len(ch1_events))

        if save_raw:
            return ch0_events, ch1_events, markers, rawdir
        return ch0_events, ch1_events, markers


    def get_adwin_data(self, noof_readouts=500000, crhist_length=100):
        #get adwin lt1 data
        a1_crhist_first = self.adwin_lt1.adwin.get_lde_var(
                'CR_hist_first', start=1, length=crhist_length)
        a1_crhist = self.adwin_lt1.adwin.get_lde_var(
                'CR_hist', start=1, length=crhist_length)
        a1_ssro = self.adwin_lt1.adwin.get_lde_var(
                'SSRO_counts', start=1, length=noof_readouts)
        a1_cr = self.adwin_lt1.adwin.get_lde_var(
                'CR_after_SSRO', start=1, length=noof_readouts)
        a1_pars = self.adwin_lt1.adwin.get_lde_var('par')
        
        #get adwin lt2 data
        a2_crhist_first = self.adwin_lt2.adwin.get_lde_var(
                'CR_hist_first', start=1, length=crhist_length)
        a2_crhist = self.adwin_lt2.adwin.get_lde_var(
                'CR_hist', start=1, length=crhist_length)
        a2_ssro = self.adwin_lt2.adwin.get_lde_var(
                'SSRO_counts', start=1, length=noof_readouts)
        a2_cr = self.adwin_lt2.adwin.get_lde_var(
                'CR_after_SSRO', start=1, length=noof_readouts)
        a2_state = self.adwin_lt2.adwin.get_lde_var(
                'PLU_state', start=1, length=noof_readouts)
        a2_pars= self.adwin_lt2.adwin.get_lde_var('par')

        return {'adwin_lt1_CRhist_first' : a1_crhist_first,
                'adwin_lt1_CRhist' : a1_crhist,
                'adwin_lt1_SSRO'   : a1_ssro,
                'adwin_lt1_CR'     : a1_cr,
                'adwin_lt1_pars'   : a1_pars,
                'adwin_lt2_CRhist_first' : a2_crhist_first,
                'adwin_lt2_CRhist' : a2_crhist,
                'adwin_lt2_SSRO'   : a2_ssro,
                'adwin_lt2_CR'     : a2_cr,
                'adwin_lt2_state'  : a2_state,
                'adwin_lt2_pars'   : a2_pars}

    def save(self, **kw):
        self.save_dataset(data=kw, do_plot=False)
        shutil.move(self.rawdir, os.path.join(self.save_folder, 'rawdata'))
        self.rawdir = ''

        # TODO here: plotting stuff and transferring to website
        
    def power_and_debug_check_ok(self):
        ret = True
        max_E_power_lt1 = E_aom_lt1.get_cal_a()
        max_A_power_lt1 = A_aom_lt1.get_cal_a()
        max_E_power_lt2 = E_aom_lt2.get_cal_a()
        max_A_power_lt2 = A_aom_lt2.get_cal_a()
        if (max_E_power_lt2 < self.Ex_CR_power_lt2) or \
                (max_E_power_lt2 < self.Ex_RO_power_lt2):
            print 'Trying to set too large value for LT2 E laser, quiting!'
            ret = False    
        if (max_E_power_lt1 < self.Ex_CR_power_lt1) or \
                (max_E_power_lt1 < self.Ex_RO_power_lt1):
            print 'Trying to set too large value for LT1 E laser, quiting!'
            ret = False

        if (max_A_power_lt2 < self.A_CR_power_lt2) or \
                (max_A_power_lt2 < self.A_SP_power):
            print 'Trying to set too large value for LT2 A laser, quiting'
            ret = False
        if (max_A_power_lt1 < self.A_CR_power_lt1) or \
                (max_A_power_lt1 < self.A_SP_power):
            print 'Trying to set too large value for LT1 A laser, quiting'
            ret = False

        if debug_mode:
            print 'Warning: script is executed in debug mode! Press q to quit, c to continue.'
            idx = 0
            max_idx = 5
            kb_hit = None
            while (idx<max_idx) and kb_hit == None:
                kb_hit = msvcrt.getch()
                if kb_hit == 'q':
                    ret = False
                if kb_hit == 'c':
                    ret = True
                qt.msleep(1)
                idx += 1
        return ret

    def optimize(self, lt1 = False, lt2 = True): #TODO: NEEDS TO BE TESTED
        
        counters_lt2.set_is_running(True)
        counters_lt1.set_is_running(True)

        green_aom_lt2.set_power(0.)
        E_aom_lt2.set_power(0.)
        A_aom_lt2.set_power(0.)
        green_aom_lt1.set_power(0.)
        E_aom_lt1.set_power(0.)
        A_aom_lt1.set_power(0.)
        
        awg.set_ch4_marker1_low(0.)

        if lt1:
            counts = adwin.get_countrates()[self.opt_counter_lt1+1]

            if counts < self.opt_threshold_lt1:
                print 'Optimizing LT1...'
                adwin_lt1.set_simple_counting()
                green_aom_lt1.set_power(self.green_opt_power_lt1)
                optimizor_lt1.optimize(counter = self.opt_counter_lt1, 
                        cycles = self.noof_opt_cycles)
                green_aom_lt1.set_power(0.)
            else:
                print '\tLT1 counts high enough...'

        if lt2:
            counts = adwin.get_countrates()[self.opt_counter_lt2-1]

            if counts < self.opt_threshold_lt2:
                print 'Optimizing LT2...'
                adwin_lt2.set_simple_counting()
                green_aom_lt2.set_power(self.green_opt_power_lt2)
                optimizor_lt2.optimize(counter = self.opt_counter_lt2, 
                        cycles = self.noof_opt_cycles)
                green_aom_lt1.set_power(0.)
            else: 
                print '\tLT2 counts high enough...'

        if not(lt1) and not(lt2):
            print 'Skipped optimization cycle...'

        counters_lt2.set_is_running(False)
        counters_lt1.set_is_running(False)

    def check_suppression(self, lt1 = False, lt2 = True): #TODO: NEEDS TO BE TESTED
        green_aom_lt2.set_power(0.)
        E_aom_lt2.set_power(0.)
        A_aom_lt2.set_power(0.)
        green_aom_lt1.set_power(0.)
        E_aom_lt1.set_power(0.)
        A_aom_lt1.set_power(0.)
        
        ret = list()
    
        if lt1:
            #check suppression from LT1
            ZPLServo.move_in()
            qt.msleep(2)
            awg.set_ch4_marker1_low(self.check_sup_voltage)
            qt.msleep(0.1)
            counts = adwin_lt2.get_countrates()[1]
            print '\tLT1 countrate with red at ', self.ceck_sup_voltage, 'V: ', counts            
            if counts < self.zpl_counts_break:
                ret.append(True)
            else:
                ret.append(False)
            awg.set_ch4_marker1_low(0.)
            ZPLServo.move_out()

        if lt2:
            #check suppression from LT2
            ZPLServo_lt1.move_in()
            qt.msleep(2)
            awg.set_ch4_marker1_low(self.check_sup_voltage)
            qt.msleep(0.1)
            counts = adwin_lt2.get_countrates()[2]
            print '\tLT2 countrate with red at ', self.ceck_sup_voltage, 'V: ', counts
            if counts < self.zpl_counts_break:
                ret.append(True)
            else:
                ret.append(False)
            awg.set_ch4_marker1_low(0.)
            ZPLServo_lt1.move_out()
            qt.msleep(2)

        #ret is a list of two elements. The first element is True if LT1 is ok, 
        #the second element is True if LT2 is ok.
        return ret

    def calibrate(self, set_vals = True):
        # here comes the actual calibration measurements.

        # get the optimal values using the qtlab analyze module
        # this module uses gnuplot and should not crash therefore.
        lt1_cal_dict = cal.cal_all(lt1=False)
        lt2_cal_dict = cal.cal_all(lt1=True)
        
        
        delta=[]
        if set_vals:
         
            delta.append(abs((lt1_cal_dict['MW_Five_CORPSE']['minimum']-self.CORPSE_pi_amp_lt1))/self.CORPSE_pi_amp_lt1)
            delta.append(abs((lt1_cal_dict['MW_CORPSE_pi_over_two']['minimum']-self.CORPSE_pi_over_two_amp_lt1))/self.CORPSE_pi_over_two_amp_lt1)
            delta.append(abs((lt2_cal_dict['MW_Five_CORPSE']['minimum']-self.CORPSE_pi_amp_lt2))/self.CORPSE_pi_amp_lt2)
            delta.append(abs((lt2_cal_dict['MW_CORPSE_pi_over_two']['minimum']-self.CORPSE_pi_over_two_amp_lt2))/self.CORPSE_pi_over_two_amp_lt2)
            delta.append(abs((lt1_cal_dict["ESR"]["freq"]-self.MW_freq_lt1))/self.MW_freq_lt1)
            delta.append(abs((lt2_cal_dict["ESR"]["freq"]-self.MW_freq_lt2))/self.MW_freq_lt2)
            par_idx=0
            
            par=["Amp of Five CORPSE pulses lt 1", "Amp of Pi over two CORPSE pulse lt 1",
                 "Amp of Five CORPSE pulses lt 2", "Amp of Pi over two CORPSE pulse lt 2",
                 "MW frequency of lt 1", "MW frequency of lt 2"]
            
            old_values=[self.CORPSE_pi_amp_lt1, self.CORPSE_pi_over_two_amp_lt1, 
                        self.CORPSE_pi_amp_lt2, self.CORPSE_pi_over_two_amp_lt2,            
                        self.MW_freq_lt1,self.MW_freq_lt2]
            
            new_values=[lt1_cal_dict['MW_Five_CORPSE']['minimum'],
                        lt1_cal_dict['MW_CORPSE_pi_over_two']['minimum'], 
                        lt2_cal_dict['MW_Five_CORPSE']['minimum'],
                        lt2_cal_dict['MW_CORPSE_pi_over_two']['minimum'],
                        lt1_cal_dict["ESR"]["freq"], lt2_cal_dict["ESR"]["freq"]]
            
            for i in delta:
                if i > 0.15: 
                    print '%s has changed with more that 15 percent. Do you still want to set new value?' %par[par_idx]
                    print 'Old value: %d' %old_values[par_idx]
                    print 'New value: %d' %new_values[par_idx]
                    print 'press y      to set the value and continue'
                    print 'press n      to continue with the old value'
                    print 'press q      to quit'
                par_idx = par_idx+1 
                
            max_idx = 5
            kb_hit = None
            while (idx<max_idx) and kb_hit == None:
                kb_hit = msvcrt.getch()
                if kb_hit == 'q':
                    ret = False
                if kb_hit == 'y':
                    ret = True
                if kb_hit == 'n':
                    ret=True
                    set_vals=False
                qt.msleep(1)
                idx += 1
            if set_vals:    
                self.CORPSE_pi_amp_lt1= lt1_cal_dict['MW_Five_CORPSE']['minimum']       
                self.CORPSE_pi_over_two_amp_lt1 = lt1_cal_dict['MW_CORPSE_pi_over_two']['minimum'] 
                self.CORPSE_pi_amp_lt2 = lt2_cal_dict['MW_Five_CORPSE']['minimum']
                self.CORPSE_pi_over_two_amp_lt2 = lt2_cal_dict['MW_CORPSE_pi_over_two']['minimum']
            
                self.MW_freq_lt1 = lt1_cal_dict["ESR"]["freq"]
                self.MW_freq_lt2 = lt2_cal_dict["ESR"]["freq"]
            return ret
        else:
            return True



    def end(self):
        qt.msleep(5)
        gate_amplitude = adwin_lt2.get_gate_modulation_var('gate_voltage')
        gate_mod_period = adwin_lt2.get_gate_modulation_var('modulation_period')
        gate_dac = adwin_lt2.get_gate_modulation_var('gate_dac')
        adwin_lt2.boot()
        adwin_lt1.boot()
        if (self.set_phase_locking_on):
            adwin_lt2.start_gate_modulation(load = True,
                modulation_on = 1,
                gate_voltage = gate_amplitude,
                modulation_period = gate_mod_period,
                gate_dac = gate_dac)
        A_aom_lt1.set_power(0)
        A_aom_lt2.set_power(0)
        E_aom_lt1.set_power(0)
        E_aom_lt2.set_power(0) 
        counters_lt1.set_is_running(True)
        counters_lt2.set_is_running(True)
        adwin_lt1.set_simple_counting()
        adwin_lt2.set_simple_counting()
        GreenAOM.set_power(200E-6)
        GreenAOM_lt1.set_power(200E-6)
        microwaves_lt2.set_iq('off')
        microwaves_lt2.set_pulm('off')
        microwaves_lt2.set_power(-30)
        
        

# intial setup
m = LDEMeasurement('only-LT2-5min-plu-reset-on-AWG-one-apd-switched-off-AWGADWINgrounded-usb-unplugged', 'LDE')

### measurement parameters

# gate parameters
m.set_gate_good_phase       = -1 #either 1 or -1
m.set_phase_locking_on      = 1 #either 0 (off) or 1 (on)

# laser pulses controlled by adwin
m.green_repump_power_lt1    = 200e-6
m.green_off_voltage_lt1     = 0.00
m.Ex_CR_power_lt1           = 20e-9
m.A_CR_power_lt1            = 15e-9
m.Ex_RO_power_lt1           = 8e-9     # FIXME: get these from calibration measurement
m.A_RO_power_lt1            = 0

m.green_repump_power_lt2    = 200e-6
m.green_off_voltage_lt2     = 0.01
m.Ex_CR_power_lt2           = 20e-9
m.A_CR_power_lt2            = 15e-9
m.Ex_RO_power_lt2           = 11e-9
m.A_RO_power_lt2            = 0

# general LDE
m.measurement_time          = 20*60 #in seconds
m.measurement_cycles        = 1
m.max_LDE_attempts          = 300 #NOTE
m.finaldelay                = 1000     # after last postsync pulse

#optimization and suppression checking
m.green_opt_power_lt1       = 100e-6
m.opt_counter_lt1           = 1     # ZPL: 1, PSB: 2
m.opt_threshold_lt1         = 2000
m.green_opt_power_lt2       = 200e-6
m.opt_counter_lt2           = 2     # ZPL: 2, PSB: 1
m.opt_threshold_lt2         = 1700
m.noof_opt_cycles           = 1

m.check_sup_voltage         = 0.4   #Matisse EOM AOM voltage
m.zpl_counts_break          = 2E5

# spin pumping
A_aom_lt2.set_cur_controller('AWG')
A_aom_lt1.set_cur_controller('AWG')
m.A_SP_power                = 15e-9
m.A_SP_amplitude            = A_aom_lt2.power_to_voltage(m.A_SP_power)
m.SP_duration               = 3000 #NOTE: changed this for second spin photon try
m.wait_after_SP             = 100

# spin manipulation
m.MW_power_lt1              = 20 
m.MW_power_lt2              = 20 
m.MW_freq_lt1               = 2.82878E9 #NOTE Needs to be adjusted
m.MW_freq_lt2               = 2.8289E9 #NOTE Adjust this by calibrating the pulses.
m.wait_after_pi2            = 0

m.MW_pulsemod_risetime_lt2  = 10
m.MW_pulsemod_risetime_lt1  = 10

#basis rotation
m.basis_rot                 = False
m.basis_rot_angle           = 0 # the rotation angle of the readout pulse (w.r.t. x-axis)
m.basis_rot_duration_lt1    = 0
m.basis_rot_duration_lt2    = 0

# optical pi-pulses
if long_pulse_settings:
    m.eom_pulse_duration    = 10
    m.eom_pulse_offset      = -8
else:
    m.eom_pulse_duration    = 2
    m.eom_pulse_offset      = 0    

m.eom_aom_amplitude         = 1.0
m.eom_off_amplitude         = 0.0 #-.25 #NOTE
m.eom_pulse_amplitude       = 1.2
m.eom_overshoot_duration1   = 10
m.eom_overshoot1            = -0.03
m.eom_overshoot_duration2   = 4
m.eom_overshoot2            = -0.03
m.eom_start                 = 40
m.eom_off_duration          = 200 #NOTE: change this to duration of CORPSE
m.pulse_start               = m.eom_start + m.eom_off_duration/2 + \
        m.eom_pulse_offset
m.aom_start                 = m.pulse_start - 35 -186 #subtract aom rise time
m.aom_duration              = 2*23+m.eom_pulse_duration #30
m.rabi_cycle_duration       = 2*m.eom_off_duration
m.wait_after_opt_pi         = 70 # determines start of MW pi pulse
m.wait_after_opt_pi2        = 0 # determines start of basis rotation
m.opt_pi_separation         = 2*m.eom_off_duration

# HH settings
m.presync_pulses            = 5
m.postsync_pulses           = 5 #NOTE Set to 10
m.binsize_T3                = 8

# PLU pulses
m.plu_gate_duration         = 70
m.plu_2_start_offset        = 4
m.plu_3_delay               = 100   # (ns, after 2nd plu pulse)
m.plu_4_delay               = 200   # (ns, after 2nd plu pulse)

# MW Pulses (regular)
    # Pi2 pulse
m.pi2_lt1_duration           = 28
m.pi2_lt2_duration           = 25
m.pi2_lt1_amplitude          = 0#0.727
m.pi2_lt2_amplitude          = 0.58

    # Pi pulse
m.pi_lt1_duration           = 56
m.pi_lt2_duration           = 50
m.pi_lt1_amplitude          = 0#0.658
m.pi_lt2_amplitude          = 0.58

# MW Pulses (CORPSE)
m.CORPSE_pulses             = True
m.CORPSE_single_pi_pulse_duration       = 58.
m.CORPSE_pi_over_two_single_pi_duration = 58.
m.time_between_CORPSE                   = 20.

if not(debug_mode):
    m.CORPSE_pi_amp_lt1             = 0.595
    m.CORPSE_pi_over_two_amp_lt1    = 0.5387
    m.CORPSE_pi_amp_lt2             = 0.4857
    m.CORPSE_pi_over_two_amp_lt2    = 0.473

    m.MW_pulsemod_amplitude         = 2.
else:
    m.CORPSE_pi_amp_lt1             = 0
    m.CORPSE_pi_over_two_amp_lt1    = 0
    m.CORPSE_pi_amp_lt2             = 0
    m.CORPSE_pi_over_two_amp_lt2    = 0

    m.MW_pulsemod_amplitude         = 0.


m.pulse_384_length = int(2.*m.CORPSE_pi_over_two_single_pi_duration*(384.3/360.))
m.pulse_318_length = int(2.*m.CORPSE_pi_over_two_single_pi_duration*(318.6/360.))
m.pulse_24_length = int(2.*m.CORPSE_pi_over_two_single_pi_duration*(24.3/360.))

m.pulse_420_length = int(2.*m.CORPSE_single_pi_pulse_duration*(420./360.))
m.pulse_300_length = int(2.*m.CORPSE_single_pi_pulse_duration*(300./360.))
m.pulse_60_length = int(2.*m.CORPSE_single_pi_pulse_duration*(60./360.))

m.total_pi_2_length = m.pulse_384_length+m.pulse_318_length+m.pulse_24_length
m.total_pi_length = m.pulse_420_length+m.pulse_300_length+m.pulse_60_length

# adwin process parameters
adpar = {}
adpar['counter_channel']            = 1
adpar['green_laser_DAC_channel']    = adwin_lt2.get_dac_channels()['green_aom']
adpar['Ex_laser_DAC_channel']       = adwin_lt2.get_dac_channels()['matisse_aom']
adpar['A_laser_DAC_channel']        = adwin_lt2.get_dac_channels()['newfocus_aom']
adpar['CR_duration']                = 60
adpar['CR_duration_lt1']            = 60
adpar['CR_preselect']               = 17 # is overwritten by the TPQI monitor
adpar['CR_probe']                   = 12 # is overwritten by the TPQI monitor
adpar['green_repump_duration']      = 10
adpar['wait_before_SSRO']           = 1
adpar['SSRO_duration']              = 38   #FIXME get this from calibration meas
adpar['SSRO_duration_lt1']          = 22    #FIXME get this from calibration meas.
adpar['max_LDE_duration']           = 530 # depends on sequence length! (overwritten)
adpar['AWG_start_DO_channel']       = 1
adpar['PLU_arm_DO_channel']         = 5
adpar['remote_CR_DO_channel']       = 16
adpar['remote_CR_done_DI_bit']      = 2**8
adpar['remote_SSRO_DO_channel']     = 17
adpar['PLU_success_DI_bit']         = 2**13
adpar['PLU_state_DI_bit']           = 2**14
green_aom_lt2.set_cur_controller('ADWIN')
E_aom_lt2.set_cur_controller('ADWIN')
A_aom_lt2.set_cur_controller('ADWIN')
adpar['green_repump_voltage']       = green_aom_lt2.power_to_voltage(
        m.green_repump_power_lt2)
adpar['green_off_voltage']          = m.green_off_voltage_lt2
adpar['Ex_CR_voltage']              = E_aom_lt2.power_to_voltage(
        m.Ex_CR_power_lt2)
adpar['A_CR_voltage']               = A_aom_lt2.power_to_voltage(
        m.A_CR_power_lt2)
adpar['Ex_RO_voltage']              = E_aom_lt2.power_to_voltage(
        m.Ex_RO_power_lt2)
adpar['A_RO_voltage']               = 0


# remote adwin process parameters
adpar_lt1 = {}
adpar_lt1['counter_channel']            = 2
adpar_lt1['green_laser_DAC_channel']    = adwin_lt1.get_dac_channels()['green_aom']
adpar_lt1['Ex_laser_DAC_channel']       = adwin_lt1.get_dac_channels()['matisse_aom']
adpar_lt1['A_laser_DAC_channel']        = adwin_lt1.get_dac_channels()['newfocus_aom']
adpar_lt1['CR_duration']                = adpar['CR_duration_lt1'] # is specified at adpar for lt2
adpar_lt1['CR_preselect']               = 25
adpar_lt1['CR_probe']                   = 18
adpar_lt1['green_repump_duration']      = 10
adpar_lt1['remote_CR_DI_channel']       = 10
adpar_lt1['remote_CR_done_DO_channel']  = 1
adpar_lt1['remote_SSRO_DI_channel']     = 9
adpar_lt1['SSRO_duration']              = adpar['SSRO_duration_lt1']  # is specified at adpar for lt2
green_aom_lt1.set_cur_controller('ADWIN')
E_aom_lt1.set_cur_controller('ADWIN')
A_aom_lt1.set_cur_controller('ADWIN')
adpar_lt1['green_repump_voltage']       = green_aom_lt1.power_to_voltage(
        m.green_repump_power_lt1)
adpar_lt1['green_off_voltage']          = m.green_off_voltage_lt1
adpar_lt1['Ex_CR_voltage']              = E_aom_lt1.power_to_voltage(
        m.Ex_CR_power_lt1)
adpar_lt1['A_CR_voltage']               = A_aom_lt1.power_to_voltage(
        m.A_CR_power_lt1)
adpar_lt1['Ex_RO_voltage']              = E_aom_lt1.power_to_voltage(
        m.Ex_RO_power_lt1)
adpar_lt1['A_RO_voltage']               = 0



#### tail measurement

def measure_both_tails():
    m_name=m.name
    m.measurement_cycles = 1
    debug_mode=True
    debug_get_histogram=True
    m.histogram_length = 2 # length in bins is 2**histogram_length*1024

    qt.instruments['ZPLServo'].move_out()
    qt.instruments['ZPLServo_lt1'].move_in()
    par_cr_preselect_lt1 = adpar_lt1['CR_preselect']
    par_cr_probe_lt1 = adpar_lt1['CR_probe']
    adpar_lt1['CR_preselect'] = 0
    adpar_lt1['CR_probe']     = 0
    
    m.name = m_name + '_tail_measurment_lt2'
    main()
    
    qt.instruments['ZPLServo'].move_in()
    qt.instruments['ZPLServo_lt1'].move_out()
    adpar_lt1['CR_preselect'] = par_cr_preselect_lt1
    adpar_lt1['CR_probe'] = par_cr_probe_lt1
    adpar_lt2['CR_preselect'] = 0
    adpar_lt2['CR_probe']     = 0

    m.name = m_name + '_tail_measurment_lt1'
    main()

#### actual code

def main():
    if m.CORPSE_pulses:
        m.generate_sequence()
    else:
        m.generate_sequence_regular_pulses()
    adpar['max_LDE_duration'] = int(m.seq.element_lengths['lde'] * \
            float(m.max_LDE_attempts) * 1e6 + 1.)

    for idx in arange(m.measurement_cycles):
        m.setup(adwin_mdevice_lt2=adwin_mdevice_lt2, 
                adwin_mdevice_lt1=adwin_mdevice_lt1)
        
        print '============================='
        print 'Starting measurement cycle', idx
        print 'current time:', time.strftime('%H:%M',time.localtime())
        print '============================='
        
        ch0, ch1, mrkr = m.measure(adwin_lt2_params = adpar,
                adwin_lt1_params = adpar_lt1)
        addata = m.get_adwin_data()
        m.save(ch0_events=ch0, ch1_events=ch1, markers=mrkr, **addata)
        
        if m.measurement_cycles != 0:
            print 'Press q to abort next cycle'
            qt.msleep(2)
            if msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q": 
                    break
            

        if  idx < m.measurement_cycles-1: m.optimize(lt1 = True, lt2 = True)

        #if False in m.check_suppression(lt1 = False, lt2 = True):
        #    print 'Bad suppression detected, breaking.'
        #    break

    m.end()
    print 'Measurement finished!'
    

if __name__ == '__main__':
    if m.power_and_debug_check_ok(): 
        main()
    else:
        print 'Measurement aborted by user!'
    
    #
    #m.measurement_time = 60
    #m.generate_sequence()
    #adpar['max_LDE_duration'] = int(m.seq.element_lengths['lde'] * \
    #        m.max_LDE_attempts / 1e3 + 1)

    #m.setup(adwin_mdevice_lt2=adwin_mdevice_lt2)
    
    #ch0, ch1, mrkr = m.measure(adwin_lt2_params = adpar)
    #addata = m.get_adwin_data()
    #m.save(ch0_events=ch0, ch1_events=ch1, markers=mrkr, **addata)
    
    

