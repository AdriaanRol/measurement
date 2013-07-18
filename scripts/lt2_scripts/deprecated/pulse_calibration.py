# measure spin photon correlations as test before the actual LDE.

# TODO kill measurement sequence
# TODO make sure the awg config is correct
# FIXME there are still some pars over 80! change!

import qt
import numpy as np

import measurement.measurement as meas
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels_lt2 as awgcfg
from measurement.config import adwins as adwincfg

# instruments
adwin_lt2 = qt.instruments['adwin']
# adwin_lt1 = qt.instruments['adwin_lt1']
awg = qt.instruments['AWG']
hharp = qt.instruments['HH_400']
green_aom_lt2 = qt.instruments['GreenAOM']
E_aom_lt2 = qt.instruments['MatisseAOM']
A_aom_lt2 = qt.instruments['NewfocusAOM']
# green_aom_lt1 = qt.instruments['GreenAOM_lt1']
# E_aom_lt1 = qt.instruments['MatisseAOM_lt1']
# A_aom_lt1 = qt.instruments['NewfocusAOM_lt1']

# adwin_mdevice_lt1 = meas.AdwinMeasurementDevice(adwin_lt1, 'adwin_lt1')
adwin_mdevice_lt2 = meas.AdwinMeasurementDevice(adwin_lt2, 'adwin_lt2')

# prepare
awg.set_runmode('CONT')
green_aom_lt2.set_power(0.)
E_aom_lt2.set_power(0.)
A_aom_lt2.set_power(0.)
# green_aom_lt1.set_power(0.)
# E_aom_lt1.set_power(0.)
# A_aom_lt1.set_power(0.)

class LDEMeasurement(meas.Measurement):

    def setup(self, adwin_mdevice_lt2):
        # self.adwin_lt1 = adwin_mdevice_lt1
        self.adwin_lt2 = adwin_mdevice_lt2
        # self.measurement_devices.append(self.adwin_lt1)
        self.measurement_devices.append(self.adwin_lt2)

        # self.adwin_lt1.process_data['lde'] = \
        #         [p for p in adwincfg.config['adwin_lt1_processes']['lde']['par']]

        self.adwin_lt2.process_data['lde'] = \
                [p for p in adwincfg.config['adwin_lt2_processes']['lde']['par']]
        
        
        hharp.start_T3_mode()
        hharp.calibrate()
        hharp.set_Binning(self.binsize_T3)
        
        return True

    def generate_sequence(self, do_program=True):
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

        # TODO study the current AWG configuration, then adapt this
        awgcfg.configure_sequence(self.seq, 'hydraharp', 'mw',
                LDE = { 
                    chan_eom_aom: { 'high' : self.eom_aom_amplitude },
                    chan_alaser: { 'high' : self.A_SP_amplitude, }
                    },
                )
        seq.add_element('lde', goto_target='lde', trigger_wait=False)
                
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
                amplitude=0.0, start_reference=last,
                link_start_to='start')

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = m.aom_start, duration = m.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_off_amplitude,
                start = m.eom_start, duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_pulse_amplitude - m.eom_off_amplitude,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset, duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot1,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot2,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration + \
                        m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration, 
                duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_pulse_amplitude + m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset, 
                duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot1, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot2, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration + m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_overshoot2_comp'+str(i)
        last = 'EOM_pulse'+str(i)

        # 3b: add pre-sync pulses for the HH
        for j in range(self.presync_pulses):
            seq.add_pulse('presync'+str(j),  chan_hhsync, 'lde',         
                    start = -(j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = 2.0, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 3c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = 0,
                duration = self.plu_gate_duration,
                amplitude = 0.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )


        # 4: spin pi pulses
        seq.add_pulse('pi lt2', chan_mwI_lt2, 'lde',
                duration = self.pi_lt2_duration,
                amplitude = self.pi_lt2_amplitude,
                start_reference = last,
                start = self.wait_after_opt_pi, 
                link_start_to = 'start' )
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
                start = m.aom_start, duration = m.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_off_amplitude,
                start = m.eom_start, duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_pulse_amplitude - m.eom_off_amplitude,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset, duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot1,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot2,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration + \
                        m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration, 
                duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_pulse_amplitude + m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset, 
                duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot1, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot2, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration + m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_overshoot2_comp'+str(i)

        # 5b: add post-sync pulses for the HH
        for j in range(self.postsync_pulses):
            seq.add_pulse('postsync'+str(j),  chan_hhsync, 'lde',         
                    start = (j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = 2.0, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 5c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = 0,
                duration = self.plu_gate_duration,
                amplitude = 0.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )

        # 5d: two additional PLU gates
        seq.add_pulse('plu-gate3', chan_plusync, 'lde',
                start = self.plu_3_delay,
                duration = self.plu_gate_duration,
                amplitude = 0.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')
        seq.add_pulse('plu-gate4', chan_plusync, 'lde',
                start = self.plu_4_delay,
                duration = self.plu_gate_duration,
                amplitude = 0.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')

        # idle element
        seq.add_element('idle', goto_target='lde')
        seq.add_pulse('empty', chan_alaser, 'idle', start=0, duration = 1000, 
            amplitude = 0)

        seq.set_instrument(awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(True)
        seq.force_HW_sequencing(True)
        seq.send_sequence()        
        
        return seq


# intial setup
m = LDEMeasurement('test1', 'LDESpinPhotonCorr')

### measurement parameters

# laser pulses controlled by adwin
m.green_repump_power        = 200e-6
m.green_off_voltage         = 0
m.Ex_CR_power               = 5e-9
m.A_CR_power                = 5e-9
m.Ex_RO_power               = 5e-9
m.A_RO_power                = 0

# general LDE
m.measurement_time          = 60 * 15
m.max_LDE_attempts          = 100
m.finaldelay                = 0     # after last postsync pulse

# spin pumping
A_aom_lt2.set_cur_controller('AWG')
# A_aom_lt1.set_cur_controller('AWG')
m.A_SP_power                = 15e-9
m.A_SP_amplitude            = A_aom_lt2.power_to_voltage(m.A_SP_power)
m.SP_duration               = 0
m.wait_after_SP             = 100

# spin manipulation
m.MW_pulsemod_risetime_lt2  = 10
m.MW_pulsemod_risetime_lt1  = 10
m.MW_pulsemod_amplitude     = 0
m.pi2_lt2_duration          = 25
m.pi2_lt1_duration          = 25
m.pi2_lt2_amplitude         = 0
m.pi2_lt1_amplitude         = 0
m.wait_after_pi2            = 0
m.pi_lt2_duration           = 50
m.pi_lt1_duration           = 50
m.pi_lt2_amplitude          = 0
m.pi_lt1_amplitude          = 0
m.basis_rot                 = False
m.basis_rot_I_amplitude_lt1 = 0
m.basis_rot_Q_amplitude_lt1 = 0.0
m.basis_rot_I_amplitude_lt2 = 0
m.basis_rot_Q_amplitude_lt2 = 0.0
m.basis_rot_duration_lt1    = 25
m.basis_rot_duration_lt2    = 25

# optical pi-pulses
m.eom_aom_amplitude         = 1.0
m.eom_off_amplitude         = -.25
m.eom_pulse_amplitude       = 1.2
m.eom_overshoot_duration1   = 10
m.eom_overshoot1            = -0.03
m.eom_overshoot_duration2   = 10
m.eom_overshoot2            = -0.0
m.eom_start                 = 40
m.eom_off_duration          = 70
m.eom_pulse_duration        = 2
m.eom_pulse_offset          = 0
m.pulse_start               = m.eom_start + m.eom_off_duration/2 + \
        m.eom_pulse_offset
m.aom_start                 = m.pulse_start - 35 -45 #subtract aom rise time
m.aom_duration              = 2*23+m.eom_pulse_duration #30
m.rabi_cycle_duration       = 2*m.eom_off_duration
m.wait_after_opt_pi         = 0
m.wait_after_opt_pi2        = 0
m.opt_pi_separation         = 2*m.eom_off_duration

# HH settings
m.presync_pulses            = 0
m.postsync_pulses           = 0
m.binsize_T3                = 8

# PLU pulses
m.plu_gate_duration         = 50
m.plu_3_delay               = 100   # (ns, after 2nd plu pulse)
m.plu_4_delay               = 200   # (ns, after 2nd plu pulse)

m.generate_sequence()

