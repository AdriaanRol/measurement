################################################################
################################################################
################################################################
# Template for the optical rabi script, LT2 version
# Updates:
# --------
# 13-04-12: GERWIN -    adapted to correct version for bath cryo
#                       FIXME need to add initialization pulse
# 15-04-12: GERWIN -    updated conditional repump pars
################################################################
################################################################
################################################################

GreenAOM.set_power(0)
MatisseAOM.set_power(0)
NewfocusAOM.set_power(0)

import numpy as np
import ctypes
import inspect
import time

from qt import instruments

from measurement.AWG_HW_sequencer_v2 import Sequence

from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq

exaom = instruments['MatisseAOM']
aaom = instruments['NewfocusAOM']
greenaom = instruments['GreenAOM']
wm = instruments['wavemeter']
ins_awg = instruments['AWG']
ins_adwin = instruments['physical_adwin']

name = 'optical_rabi'
par_cr_A_amplitude = aaom.power_to_voltage(3e-9) #OK: power in W
par_cr_Ex_amplitude = exaom.power_to_voltage(3e-9) #OK: power in W 
par_cr_duration = int(50e3) #in units of the AWG clockcycle, NOT 10 us!!!
par_rabi_reps = 100 #if greater than 200, loading the seq. takes long
par_rabi_elt_reps = 1
par_eom_start = 20+10
par_eom_off_duration = 100
par_eom_pulse_duration = 10
par_eom_pulse_offset = 0#-10
pulse_start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset
#print pulse_start
par_aom_start = pulse_start - 35 - 45 #subtract aom rise time
par_aom_duration = 2*35+par_eom_pulse_duration
##########################
#pulse amplitude and shape
##########################
par_eom_off_amplitude = -.25
par_eom_pulse_amplitude = 1.2
par_eom_overshoot_duration1 = 10
par_eom_overshoot1 = -0.05
par_eom_overshoot_duration2 = 10
par_eom_overshoot2 = -0.02

par_eom_aom_amplitude = 1.0

par_rabi_cycle_duration = 2*par_eom_off_duration

##########################
#cr and probe thresholds #
##########################
par_adwin_counter_process = 1
par_adwin_code = 'D:\\measuring\\user\\ADwin_Codes\\conditional_repump.tb9'
par_adwin_process = 9 #conditional repump process number in adwin (9)
par_adwin_counter = 1 #NOTE should be PSB counter
par_adwin_aom_dac = 7 #dac channel in adwin

par_adwin_aom_amp = 4. #greenaom.power_to_voltage(500e-6) #amplitude of (green) aom in volts
par_adwin_aom_duration = 6 #duration of (green) aom pulse in units on 10 us (3=20 us)
par_adwin_probe_duration = 6 #duration of red probe pulses BEFORE starting sequence (5=40 us)

par_adwin_probe_threshold = 2 #nr of counts to decide if on resonance BEFORE starting sequence
par_adwin_CR_threshold = 2 #nr of counts to decide if on resonance AFTER sequence

def generate_sequence(do_program=True):
    seq = Sequence(name)
    
    # vars for the channel names
    chan_hhsync = 'HH_sync'         # historically PH_start
    chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
    chan_exlaser = 'AOM_Matisse'    # ok
    chan_alaser = 'AOM_Newfocus'    # ok
    chan_adwinsync = 'ADwin_sync'   # ok
    chan_eom = 'EOM_Matisse'
    chan_eom_aom = 'EOM_AOM_Matisse'

    awgcfg.configure_sequence(seq, 'hydraharp', 
            optical_rabi = {chan_eom_aom: {'high': par_eom_aom_amplitude}}, 
            ssro={ chan_alaser: {'high': par_cr_A_amplitude } } )
        
    seq.add_element('preselect', event_jump_target = 'wait_for_ADwin')
        
    seq.add_pulse('cr1', chan_exlaser, 'preselect', duration = par_cr_duration, 
            amplitude = par_cr_Ex_amplitude)

    seq.add_pulse('cr1_2', chan_alaser, 'preselect', start = 0, duration = 0, 
            amplitude = par_cr_A_amplitude, start_reference = 'cr1', link_start_to = 'start', 
            duration_reference = 'cr1', link_duration_to = 'duration')

    seq.add_pulse('ADwin_ionization_probe', chan_adwinsync, 'preselect', start = 0, 
            duration = -20000, amplitude = par_adwin_aom_amp, start_reference = 'cr1', link_start_to = 'start', 
            duration_reference = 'cr1', link_duration_to = 'duration')

    #int(par_adwin_aom_duration*1e4)

    seq.add_element('optical_rabi', goto_target = 'preselect', repetitions = par_rabi_elt_reps)

    #Define a start point for the sequence, set amplitude to 0. actual sync pulse comes later  
    seq.add_pulse('start',  chan_hhsync, 'optical_rabi', start = 0, duration = 50, amplitude = 0.0)
    last = 'start'
        
    for i in arange(par_rabi_reps):
        #FIXME position for the initialization pulse
        
        seq.add_pulse('start'+str(i),  chan_hhsync, 'optical_rabi', start = par_rabi_cycle_duration, duration = 50, 
                start_reference = last,  link_start_to = 'start') 
        last = 'start'+str(i)

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'optical_rabi', 
                start = par_aom_start, duration = par_aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_off_amplitude,
                start = par_eom_start, duration = par_eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_pulse_amplitude - par_eom_off_amplitude,
                start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset, duration = par_eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_overshoot1,
                start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset + par_eom_pulse_duration, duration = par_eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = par_eom_overshoot2,
                start = par_eom_start + par_eom_off_duration/2 + par_eom_pulse_offset + par_eom_pulse_duration + par_eom_overshoot_duration1, 
                duration = par_eom_overshoot_duration2, start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_off_amplitude,
                start = par_eom_start+par_eom_off_duration, 
                duration = par_eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_pulse_amplitude + par_eom_off_amplitude,
                start = par_eom_start+par_eom_off_duration + int(par_eom_off_duration/2) + par_eom_pulse_offset, 
                duration = par_eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_overshoot1, 
                start = par_eom_start+par_eom_off_duration + int(par_eom_off_duration/2) + par_eom_pulse_offset + par_eom_pulse_duration, 
                duration = par_eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'optical_rabi', 
                amplitude = -par_eom_overshoot2, 
                start = par_eom_start+par_eom_off_duration + int(par_eom_off_duration/2) + par_eom_pulse_offset + par_eom_pulse_duration + par_eom_overshoot_duration1, 
                duration = par_eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')


    seq.add_element('wait_for_ADwin', trigger_wait = True, goto_target = 'optical_rabi')
    seq.add_pulse('probe1', chan_exlaser, 'wait_for_ADwin', start=0, duration = 1000, 
            amplitude = par_cr_Ex_amplitude)
    seq.add_pulse('probe2', chan_alaser, 'wait_for_ADwin', start=-125, duration = 1000, 
            amplitude = par_cr_A_amplitude)
    #seq.add_pulse('probemw', chan_mw, 'wait_for_ADwin', start=-525, duration = 1000, 
    #       amplitude = 1.0)

    seq.set_instrument(ins_awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(True)
    seq.force_HW_sequencing(True)
    seq.send_sequence()
        
    return True

ins_adwin.Stop_Process(par_adwin_counter_process)
ins_adwin.Stop_Process(par_adwin_process)
ins_adwin.Load(par_adwin_code)
ins_adwin.Set_Par(78,par_adwin_counter) #OK 
ins_adwin.Set_Par(26,par_adwin_aom_dac) #OK
ins_adwin.Set_Par(27,par_adwin_aom_duration) #OK
ins_adwin.Set_Par(28,par_adwin_probe_duration) #OK
ins_adwin.Set_Par(75,par_adwin_CR_threshold) #OK
ins_adwin.Set_Par(76,par_adwin_probe_threshold) #OK
ins_adwin.Set_FPar(30,par_adwin_aom_amp) #OK

generate_sequence()
ins_adwin.Start_Process(par_adwin_process)
