# measure spin photon correlations as test before the actual LDE.

# TODO kill measurement sequence
# FIXME there are still some pars over 80! change!


debug_mode = False
long_pulse_settings = False

import qt
import numpy as np
import time
import msvcrt

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
        print 'Hydraharp not open!!!'
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

        # 2: Pi/2 pulses on both spins
        start_ref='spinpumping'
        
      

        # Define pars for CORPSE pi pulse
        seq.add_pulse('pulse_420_lt1_1', channel = chan_mwI_lt1, element = 'lde',
                start = self.wait_after_opt_pi, start_reference = start_ref,link_start_to = 'end', 
                duration = self.pulse_420_length, 
                amplitude = 0, shape = 'rectangular')
        seq.add_pulse('pulse_420_lt2_1', channel = chan_mwI_lt2, element = 'lde',
                start = self.wait_after_opt_pi, start_reference = start_ref,link_start_to = 'end', 
                duration = self.pulse_420_length, 
                amplitude = 0, shape = 'rectangular')
        seq.add_pulse('pulse_mod_420_1', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_420_length+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_420_length+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_420_length-self.pulse_420_length)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_420_lt2_1', link_start_to = 'start', 
                amplitude = 0)
                 
        seq.add_pulse('wait_3_1', channel = chan_mw_pm, element = 'lde',
                start = 0,start_reference = 'pulse_420_lt2_1',link_start_to ='end', 
                duration = self.time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_300_lt1_1', channel = chan_mwI_lt1, element = 'lde',
                start = 0, start_reference = 'wait_3_1', link_start_to = 'end',
                duration = self.pulse_300_length, 
                amplitude =0,shape = 'rectangular')
        seq.add_pulse('pulse_300_lt2_1', channel = chan_mwI_lt2, element = 'lde',
                start = 0, start_reference = 'wait_3_1', link_start_to = 'end',
                duration = self.pulse_300_length, 
                amplitude =0,shape = 'rectangular')
        seq.add_pulse('pulse_mod_300_1', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_300_length+\
                    2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_300_length+\
                    2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_300_length-self.pulse_300_length)/2 - \
                    self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_300_lt2_1', link_start_to = 'start', 
                amplitude =  0)
 
        seq.add_pulse('wait_4_1', channel = chan_mw_pm, element = 'lde',
                start = 0,start_reference = 'pulse_300_lt2_1',link_start_to ='end', 
                duration = self.time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_60_lt1_1', channel = chan_mwI_lt1, element = 'lde',
                start = 0, start_reference = 'wait_4_1', link_start_to = 'end', 
                duration = self.pulse_60_length, 
                amplitude = 0,shape = 'rectangular')
        seq.add_pulse('pulse_60_lt2_1', channel = chan_mwI_lt2, element = 'lde',
                start = 0, start_reference = 'wait_4_1', link_start_to = 'end', 
                duration = self.pulse_60_length, 
                amplitude = 0,shape = 'rectangular')
        seq.add_pulse('pulse_mod_60_1', channel = chan_mw_pm, element = 'lde',
                duration = max(self.pulse_60_length+\
                    2*self.MW_pulsemod_risetime_lt2,
                    self.pulse_60_length+\
                    2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pulse_60_length-self.pulse_60_length)/2 - \
                    self.MW_pulsemod_risetime_lt1),
                start_reference = 'pulse_60_lt2_1', link_start_to = 'start', 
                amplitude = 0)

        last = 'pulse_mod_60_1'

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
        seq.add_pulse('pulse_420_lt1', channel = chan_mwI_lt1, element = 'lde',
                start = self.wait_after_opt_pi, start_reference = last,link_start_to = 'end', 
                duration = self.pulse_420_length, 
                amplitude = self.CORPSE_pi_amp_lt1, shape = 'rectangular')
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

        seq.add_pulse('pulse_300_lt1', channel = chan_mwI_lt1, element = 'lde',
                start = 0, start_reference = 'wait_3', link_start_to = 'end',
                duration = self.pulse_300_length, 
                amplitude = -self.CORPSE_pi_amp_lt1,shape = 'rectangular')
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

        seq.add_pulse('pulse_60_lt1', channel = chan_mwI_lt1, element = 'lde',
                start = 0, start_reference = 'wait_4', link_start_to = 'end', 
                duration = self.pulse_60_length, 
                amplitude = self.CORPSE_pi_amp_lt1,shape = 'rectangular')
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


    def measure(self, adwin_lt2_params={}, adwin_lt1_params={}):
        self.adwin_lt1.process_params['lde'] = adwin_lt1_params
        self.adwin_lt2.process_params['lde'] = adwin_lt2_params

        awg.set_runmode('SEQ')
        awg.start()
        
        if not debug_mode:
            microwaves_lt2.set_status('on')
            microwaves_lt1.set_status('on')

            hharp.StartMeas(int(self.measurement_time * 1e3))
            adwin_lt1.start_lde(load=True, **adwin_lt1_params)
            qt.msleep(1)
            adwin_lt2.start_lde(load=True, 
                    set_phase_locking_on = self.set_phase_locking_on,
                    set_gate_good_phase = self.set_gate_good_phase,
                    **adwin_lt2_params)
            qt.msleep(1)

            ch0_events, ch1_events, markers = hharp.get_T3_pulsed_events(
                    sync_period = self.opt_pi_separation,
                    range_sync = int(self.opt_pi_separation / \
                            (2**self.binsize_T3)*1e-3),
                    start_ch0 = 0,
                    start_ch1 = 0,
                    max_pulses = 2,
                    save_markers = [2])
        else:
            adwin_lt1.start_lde(load=True, **adwin_lt1_params)
            qt.msleep(1)
            print 'adwin lt1 started'
            adwin_lt2.start_lde(load=True, **adwin_lt2_params)
            print 'adwin lt2 started'
            qt.msleep(self.measurement_time)

            ch0_events = ch1_events = markers = list()
        
        adwin_lt1.stop_lde()
        adwin_lt2.stop_lde()
        awg.stop()
        microwaves_lt1.set_status('off')
        microwaves_lt2.set_status('off')
        qt.msleep(0.1)
        awg.set_runmode('CONT')        

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
        adwin_lt2.boot()
        adwin_lt1.boot()
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
m = LDEMeasurement('Spin_photon_LT2_pi_between_400eomoff', 'LDESpinPhotonCorr')

### measurement parameters

# gate parameters
m.set_gate_good_phase       = 1 #either 1 or -1
m.set_phase_locking_on      = 0 #either 0 (off) or 1 (on)

# laser pulses controlled by adwin
m.green_repump_power_lt1    = 200e-6
m.green_off_voltage_lt1     = 0.00
m.Ex_CR_power_lt1           = 10e-9
m.A_CR_power_lt1            = 15e-9
m.Ex_RO_power_lt1           = 5e-9     # FIXME: get these from calibration measurement
m.A_RO_power_lt1            = 0

m.green_repump_power_lt2    = 200e-6
m.green_off_voltage_lt2     = 0.01
m.Ex_CR_power_lt2           = 10e-9
m.A_CR_power_lt2            = 15e-9
m.Ex_RO_power_lt2           = 5e-9
m.A_RO_power_lt2            = 0

# general LDE
m.measurement_time          = 5*60 #in seconds
m.measurement_cycles        = 1
m.max_LDE_attempts          = 300 #NOTE
m.finaldelay                = 1000     # after last postsync pulse

#optimization and suppression checking
m.green_opt_power_lt1       = 200e-6
m.opt_counter_lt1           = 1     # ZPL: 1, PSB: 2
m.opt_threshold_lt1         = 1800
m.green_opt_power_lt2       = 200e-6
m.opt_counter_lt2           = 2     # ZPL: 2, PSB: 1
m.opt_threshold_lt2         = 2000
m.noof_opt_cycles           = 2

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
m.MW_freq_lt2               = 2.828352E9 #NOTE Adjust this by calibrating the pulses.
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
    m.eom_pulse_offset      = 0
else:
    m.eom_pulse_duration    = 2
    m.eom_pulse_offset      = 0    

m.eom_aom_amplitude         = 1.0
m.eom_off_amplitude         = -.25
m.eom_pulse_amplitude       = 1.2
m.eom_overshoot_duration1   = 10
m.eom_overshoot1            = -0.03
m.eom_overshoot_duration2   = 4
m.eom_overshoot2            = -0.03
m.eom_start                 = 40
m.eom_off_duration          = 400#200 #NOTE: change this to duration of CORPSE
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

# CORPSE pulse values
m.CORPSE_single_pi_pulse_duration       = 58.
m.CORPSE_pi_over_two_single_pi_duration = 58.
m.time_between_CORPSE                   = 10.

if not(debug_mode):
    m.CORPSE_pi_amp_lt1             = 0.595
    m.CORPSE_pi_over_two_amp_lt1    = 0.5387
    m.CORPSE_pi_amp_lt2             = 0.4857
    m.CORPSE_pi_over_two_amp_lt2    = 0.46466

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

m.total_pi_2_length = m.pulse_384_length+m.pulse_318_length+m.pulse_24_length+\
        2*m.time_between_CORPSE
m.total_pi_length = m.pulse_420_length+m.pulse_300_length+m.pulse_60_length+\
        2*m.time_between_CORPSE

# adwin process parameters
adpar = {}
adpar['counter_channel']            = 1
adpar['green_laser_DAC_channel']    = adwin_lt2.get_dac_channels()['green_aom']
adpar['Ex_laser_DAC_channel']       = adwin_lt2.get_dac_channels()['matisse_aom']
adpar['A_laser_DAC_channel']        = adwin_lt2.get_dac_channels()['newfocus_aom']
adpar['CR_duration']                = 50
adpar['CR_duration_lt1']            = 50
adpar['CR_preselect']               = 0 # is overwritten by the TPQI monitor
adpar['CR_probe']                   = 0 # is overwritten by the TPQI monitor
adpar['green_repump_duration']      = 10
adpar['wait_before_SSRO']           = 1
adpar['SSRO_duration']              = 24    #FIXME get this from calibration meas
adpar['SSRO_duration_lt1']          = 42    #FIXME get this from calibration meas.
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
adpar_lt1['CR_preselect']               = 0
adpar_lt1['CR_probe']                   = 0
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





#### actual code

def main():
    m.generate_sequence()
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
            

        #if  idx < m.measurement_cycles-1: m.optimize(lt1 = False, lt2 = True)

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
    
    

