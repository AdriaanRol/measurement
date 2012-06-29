# measure spin photon correlations as test before the actual LDE.

# TODO kill measurement sequence
# TODO make sure the awg config is correct
# FIXME there are still some pars over 80! change!

import qt
import numpy as np

import measurement.measurement as meas
from measurement.AWG_HW_sequencer import Sequence
from measurement.config import awchannels_lt2 as awgcfg

# instruments

adwin_lt2 = qt.instruments['adwin_lt2']
awg = qt.instruments['AWG']
hharp = qt.instruments['HH_400']

green_aom_lt2 = qt.instruments['GreenAOM']
E_aom_lt2 = qt.instruments['MatisseAOM']
A_aom_lt2 = qt.instruments['NewfocusAOM']
green_aom_lt1 = qt.instruments['GreenAOM_lt1']
E_aom_lt1 = qt.instruments['MatisseAOM_lt1']
A_aom_lt1 = qt.instruments['NewfocusAOM_lt1']

class LDEMeasurement(meas.Measurement):

    def setup(self, adwin):
        self.measurement_devices.append(adwin)

    def generate_sequence(self, do_program=True):
        self.seq = Sequence('lde')
        
        # channels
        chan_hhsync = 'HH_sync'         # historically PH_start
        chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
        chan_plusync = 'PLU_gate'
        
        chan_exlaser = 'AOM_Matisse'    # ok
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
                'LDE' = { 
                    chan_eom_aom: { 'high' : self.eom_aom_amplitude },
                    chan_alaser: { 'high' : self.A_SP_amplitude, }
                    },
                )
        seq.add_element('lde', goto_target='idle', 
                repeat=self.max_LDE_attempts, event_jump_target='idle',
                trigger_wait=True)
                
        # 1: spin pumping
        seq.add_pulse('initialdelay', chan_alaser, 'lde',
                start = 0, duration = 10)
        seq.add_pulse('spinpumping', chan_alaser, 'lde', 
                start = 0, duration = self.SP_duration,
                start_reference='initialdelay',
                link_start_to='end')

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
                amplitude = 2.0, start_reference = last,  
                link_start_to = 'end') 
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
            Iamplt1 = m.basis_rot_I_amplitude_lt1
            Qamplt1 = m.basis_rot_Q_amplitude_lt1
            Iamplt2 = m.basis_rot_I_amplitude_lt2
            Qamplt2 = m.basis_rot_Q_amplitude_lt2
        else:
            Iamplt1=Qamplt1=Iamplt2=Qamplt2=0

        seq.add_pulse('basis rot lt2 I', chan_mwI_lt2, 'lde',
                duration = self.basis_rot_duration_lt2,
                amplitude = Iamplt2,
                start_reference = last,
                start = self.wait_after_opt_pi, 
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
                amplitude = self.MW_pulsemod_amplitude,
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
                start_reference = 'postsync'+str(self.postsync_pulses-1),
                link_start_to = 'end' )

        # idle element
        seq.add_element('idle', goto_target='lde')
        seq.add_pulse('empty', chan_exlaser, 'idle', start=0, duration = 1000, 
            amplitude = 0)

        seq.set_instrument(awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()        

    def measure(self):

        pass

# intial setup
m = LDEMeasurement('test1', 'LDESpinPhotonCorr')

green_aom_lt2.set_power(0.)
E_aom_lt2.set_power(0.)
A_aom_lt2.set_power(0.)
green_aom_lt1.set_power(0.)
E_aom_lt1.set_power(0.)
A_aom_lt1.set_power(0.)

### measurement parameters

# laser pulses controlled by adwin
m.green_repump_power        = 200e-6
m.green_off_voltage         = 0
m.Ex_CR_power               = 5e-9
m.A_CR_power                = 5e-9
m.Ex_RO_power               = 5e-9
m.A_RO_power                = 0

# general LDE
m.max_LDE_attempts          = 100
m.finaldelay                = 0     # after last postsync pulse

# spin pumping
m.A_SP_amplitude            = 1.0
m.SP_duration               = 2000
m.wait_after_SP             = 100

# spin manipulation
m.MW_pulsemod_risetime_lt2  = 10
m.MW_pulsemod_risetime_lt1  = 10
m.MW_pulsemod_amplitude     = 1.0
m.pi2_lt2_duration          = 100
m.pi2_lt1_duration          = 100
m.pi2_lt2_amplitude         = 1.0
m.pi2_lt1_amplitude         = 1.0
m.wait_after_pi2            = 0
m.pi_lt2_duration           = 100
m.pi_lt1_duration           = 100
m.pi_lt2_amplitude          = 1.0
m.pi_lt1_amplitude          = 1.0
m.basis_rot                 = False
m.basis_rot_I_amplitude_lt1 = 1.0
m.basis_rot_Q_amplitude_lt1 = 0.0
m.basis_rot_I_amplitude_lt2 = 1.0
m.basis_rot_Q_amplitude_lt2 = 0.0
m.basis_rot_duration_lt1    = 100
m.basis_rot_duration_lt2    = 100

# optical pi-pulses
m.eom_aom_amplitude         = 1.0
m.eom_off_amplitude         = -.25
m.eom_pulse_amplitude       = 1.2
m.eom_overshoot_duration1   = 10
m.eom_overshoot1            = -0.05
m.eom_overshoot_duration2   = 10
m.eom_overshoot2            = -0.02
m.eom_start                 = 0
m.eom_off_duration          = 65
m.eom_pulse_duration        = 2
m.eom_pulse_offset          = -4
m.pulse_start               = m.eom_start + m.eom_off_duration/2 + \
        m.eom_pulse_offset
m.aom_start                 = m.pulse_start - 35 -45 #subtract aom rise time
m.aom_duration              = 2*23+m.eom_pulse_duration #30
m.rabi_cycle_duration       = 2*m.eom_off_duration
m.wait_after_opt_pi         = 0
m.wait_after_opt_pi2        = 0
m.opt_pi_separation         = max(m.pi_lt2_duration, m.pi_lt1_duration) + 0

# HH settings
m.presync_pulses            = 10
m.postsync_pulses           = 10

# PLU pulses
m.plu_gate_duration         = 50
m.plu_3_delay               = 100   # (ns, after 2nd plu pulse)
m.plu_4_delay               = 200   # (ns, after 2nd plu pulse)

# adwin process parameters
adpar = {}
adpar['counter_channel'] = 1
adpar['green_laser_DAC_channel']    = adwin_lt2.get_dac_channels()['green_aom']
adpar['Ex_laser_DAC_channel']       = adwin_lt2.get_dac_channels()['matisse_aom']
adpar['A_laser_DAC_channel']        = adwin_lt2.get_dac_channels()['newfocus_aom']
adpar['CR_duration']                = 100
adpar['CR_preselect']               = 10
adpar['CR_probe']                   = 10
adpar['green_repump_duration']      = 6
adpar['wait_before_SSRO']           = 1
adpar['SSRO_duration']              = 20
adpar['max_LDE_duration']           = 1000 # TODO depends on sequence length!
adpar['AWG_start_DO_channel']       = 1
adpar['PLU_arm_DO_channel']         = 18 # TODO figure out!
adpar['remote_CR_DO_channel']       = 16
adpar['remote_CR_done_DI_bit']      = 2**8
adpar['remote_CR_SSRO_DO_channel']  = 17
adpar['PLU_success_DI_bit']         = 2**9 # TODO figure out

adpar['green_repump_voltage']       = ins_green_aom.power_to_voltage(
        m.green_repump_power)
adpar['green_off_voltage']          = m.green_off_voltage
adpar['Ex_CR_voltage']              = ins_E_aom.power_to_voltage(
        m.Ex_CR_power)
adpar['A_CR_voltage']               = ins_A_aom.power_to_voltage(
        m.A_CR_power)
adpar['Ex_RO_voltage']              = ins_Ex_aom.power_to_voltage(
        m.Ex_RO_power)
adpar['A_RO_voltage']               = 0
