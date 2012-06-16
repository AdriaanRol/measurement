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

pulse_reps = 50
name = 'cable_delay_test'

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
        
    seq.add_element('sync_pulse')

    seq.add_pulse('start',  chan_hhsync, name, start = 0, duration = 50, amplitude = 4.0)
    seq.add_pulse('pulse', chan_eom_aom, name, )
    
    
    
    
    #Define a start point for the sequence, set amplitude to 0. actual sync pulse comes later  
    seq.add_pulse('start',  chan_hhsync, 'optical_rabi', start = 0, duration = 50, amplitude = 0.0)
    last = 'start'
        
    for i in arange(pulse_reps):
        seq.add_pulse('start'+str(i),  chan_hhsync, 'optical_rabi', start = par_rabi_cycle_duration, duration = 50, 
                start_reference = last,  link_start_to = 'start') 
        last = 'start'+str(i)

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
