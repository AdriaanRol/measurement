import numpy as np
import ctypes
import inspect
import time

from qt import instruments

from measurement.AWG_HW_sequencer_v2 import Sequence

from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq

exaom = instruments['MatisseAOM']
ins_awg = instruments['AWG']

name = 'optical_rabi'

par_aom_duration = 200
par_aom_start = 800
par_eom_off_duration = 100
par_eom_pulse_duration = 30
par_eom_pulse_offset = -30

par_eom_off_amplitude = -.2
par_eom_pulse_amplitude = -.1

par_eom_aom_amplitude = 0.1
par_eom_initial_idle_duration = 0


seq = Sequence(name)

# vars for the channel names
chan_HHsync = 'HH_sync'
chan_eom_aom = 'AOM_EOM_Matisse'
chan_eom = 'EOM_Matisse'

seq.add_channel('EOM_Matisse', 'ch4', cable_delay = 0, low = par_eom_off_amplitude, high = par_eom_pulse_amplitude)
seq.add_channel('AOM_EOM_Matisse', 'ch4m1', cable_delay = 0, low = 0., high = 1.)
seq.add_channel('HH_sync', 'ch2m2', cable_delay = 0, low = 0., high = 2.)


seq.add_element(name, repetitions = 1, goto_target = name)

offset = 25 #somewhere there is an offset?!
time_remaining = 1000 - (par_eom_initial_idle_duration + 2*par_eom_off_duration) + offset

def generate_sequence(do_program=True):


        #syntax: seq.add_pulse('name of element', name channel, name overall sequence, start = ..., duration = ..., link_start_to = 'start/end', start_reference = previous element name, amplitude = ...)
        
        # HH CHANNEL ELEMENTS
        seq.add_pulse('hh_sync',  chan_HHsync, 'optical_rabi', start = 0, duration = 50)
        
        # AOM CHANNEL ELEMENTS
        seq.add_pulse('aom_on',  chan_eom_aom, 'optical_rabi', 
                    start = par_aom_start, duration = par_aom_duration)

        # EOM CHANNEL ELEMENTS
        
        seq.add_pulse('eom_idle',  chan_eom, 'optical_rabi', 
                    amplitude = 0, start = 0, duration = par_eom_initial_idle_duration)
        
        seq.add_pulse('eom_off',  chan_eom, 'optical_rabi', 
                    amplitude = par_eom_off_amplitude,
                    start = 0, duration = par_eom_off_duration, 
                    start_reference = 'eom_idle', link_start_to = 'end')

        seq.add_pulse('eom_pulse',  chan_eom, 'optical_rabi', 
                    amplitude = par_eom_pulse_amplitude - par_eom_off_amplitude,
                    start = int(par_eom_off_duration/2)+par_eom_pulse_offset, duration = par_eom_pulse_duration, 
                    start_reference = 'eom_off', link_start_to = 'start')

        seq.add_pulse('eom_off_comp',  chan_eom, 'optical_rabi', 
                    amplitude = -par_eom_off_amplitude,
                    start = 0, duration = par_eom_off_duration, 
                    start_reference = 'eom_off', link_start_to = 'end')

        seq.add_pulse('eom_pulse_comp',  chan_eom, 'optical_rabi', 
                    amplitude = -par_eom_pulse_amplitude + par_eom_off_amplitude,
                    start = int(par_eom_off_duration/2)+par_eom_pulse_offset, duration = par_eom_pulse_duration, 
                    start_reference = 'eom_off_comp', link_start_to = 'start')

        seq.add_pulse('eom_idle_2',  chan_eom, 'optical_rabi', 
                    amplitude = 0, start = 0, duration = time_remaining, 
                    start_reference = 'eom_pulse_comp', link_start_to = 'end')


        seq.set_instrument(ins_awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(True)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        
        return True

generate_sequence()

