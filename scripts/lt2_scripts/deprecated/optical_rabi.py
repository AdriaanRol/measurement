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
wm = instruments['wavemeter']
ins_awg = instruments['AWG']
ins_adwin = instruments['physical_adwin']

name = 'optical_rabi'
par_cr_A_amplitude = 0.3
par_cr_Ex_amplitude = 0.75
par_cr_duration = int(100e3)
par_rabi_reps = 100
par_rabi_elt_reps = 10
par_aom_duration = 70
par_aom_start = -20 #determines start of pulse in HH
par_eom_start = 0 #shift eom start sequence
par_eom_off_duration = 150 
par_eom_pulse_start = +40 #start pulse measured from eom off start
par_eom_pulse_duration = 30

par_eom_off_amplitude = -.3
par_eom_pulse_amplitude = 0
par_eom_aom_amplitude = .2

par_rabi_cycle_duration = 2*par_eom_off_duration

par_adwin_counter_process = 1
par_adwin_code = 'D:\\measuring\\user\\ADwin_Codes\\conditional_repump.tb9'
par_adwin_process = 9
par_adwin_counter = 1
par_adwin_aom_dac = 4
par_adwin_aom_amp = 7
par_adwin_aom_duration = 2
par_adwin_CR_threshold = 0#10
par_adwin_probe_duration = 5
par_adwin_probe_threshold = 0#10

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

        awgcfg.configure_sequence(seq, 'basics', 'hydraharp', 
                optical_rabi = {chan_eom_aom: {'high': par_eom_aom_amplitude}}, 
                ssro={ chan_alaser: {'high': par_cr_A_amplitude } } )
        
        seq.add_element('preselect', event_jump_target = 'wait_for_ADwin')
        
        seq.add_pulse('cr1', chan_exlaser, 'preselect', duration = par_cr_duration, 
                amplitude = par_cr_Ex_amplitude)

        seq.add_pulse('cr1_2', chan_alaser, 'preselect', start = 0, duration = 0, 
                amplitude = par_cr_A_amplitude, start_reference = 'cr1', link_start_to = 'start', 
                duration_reference = 'cr1', link_duration_to = 'duration')

        seq.add_pulse('ADwin_ionization_probe', chan_adwinsync, 'preselect', start = 0, 
            duration = -20000, start_reference = 'cr1', link_start_to = 'start', 
            duration_reference = 'cr1', link_duration_to = 'duration')

        seq.add_element('optical_rabi', goto_target = 'preselect', repetitions = par_rabi_elt_reps)

        seq.add_pulse('start',  chan_hhsync, 'optical_rabi', start = 0, duration = 50, amplitude = 0.0)
        last = 'start'
        
        for i in arange(par_rabi_reps):
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
                    start = par_aom_start + int(par_aom_duration/2) + par_eom_pulse_start, duration = par_eom_pulse_duration, 
                    start_reference = last, link_start_to = 'start')

            seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'optical_rabi', 
                    amplitude = -par_eom_off_amplitude,
                    start = par_eom_start+par_eom_off_duration, duration = par_eom_off_duration, 
                    start_reference = last, link_start_to = 'start')

            seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'optical_rabi', 
                    amplitude = -par_eom_pulse_amplitude + par_eom_off_amplitude,
                    start = par_eom_off_duration + par_aom_start + par_eom_pulse_start + 
                    int(par_aom_duration/2), duration = par_eom_pulse_duration, 
                    start_reference = last, link_start_to = 'start')

        seq.add_element('wait_for_ADwin', trigger_wait = True, goto_target = 'optical_rabi')
        seq.add_pulse('probe1', chan_exlaser, 'wait_for_ADwin', start=0, duration = 1000, 
                amplitude = par_cr_Ex_amplitude)
        seq.add_pulse('probe2', chan_alaser, 'wait_for_ADwin', start=-125, duration = 1000, 
                amplitude = par_cr_A_amplitude)

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
ins_adwin.Set_Par(45,par_adwin_counter)
ins_adwin.Set_Par(63,par_adwin_aom_dac)
ins_adwin.Set_Par(73,par_adwin_aom_duration)
ins_adwin.Set_Par(74,par_adwin_probe_duration)
ins_adwin.Set_Par(75,par_adwin_CR_threshold)
ins_adwin.Set_Par(76,par_adwin_probe_threshold)
ins_adwin.Set_FPar(64,par_adwin_aom_amp)
generate_sequence()
ins_adwin.Start_Process(par_adwin_process)

