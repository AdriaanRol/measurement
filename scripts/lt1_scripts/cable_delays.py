GreenAOM.set_power(0)
MatisseAOM.set_power(0)
NewfocusAOM.set_power(0)

import numpy as np
import time
from qt import instruments
from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.sequence import common as commonseq

ins_awg = qt.instruments['AWG']
ins_mw = qt.instruments['SMB100']

mw_frq = 2.820e9
mw_power = 0
mw_amp_ssb = 0.9
mw_frq_ssb = 35e6
mw_pulse_mod_risetime = 20

def mw_sequence(do_program=True, name='cable_delay'):
    """
    with this sequence the delay of the MW pulses with respect to the
    PH sync can be determined;
    here, we simply leave on green during the whole time;
    """    
    GreenAOM.set_power(10e-6)
    ins_mw.set_iq('on')
    ins_mw.set_pulm('on')
    ins_mw.set_frequency(mw_frq)
    ins_mw.set_power(mw_power)
    ins_mw.set_status('on')
        
    seq = Sequence(name)
    
    # vars for the channel names
    chan_phstart = 'PH_start'         # historically PH_start
    chan_phsync = 'PH_MA1'          # historically PH_sync

    awgcfg.configure_sequence(seq, 'picoharp', 'mw')
        
    seq.add_element('sync', goto_target='sync')
    seq.add_pulse('PH_sync', 'PH_start', 'sync', duration=50)
    seq.add_pulse('PH_sync_wait', 'PH_start', 'sync', start=0, 
            duration = 20000, start_reference = 'PH_sync', 
            link_start_to = 'start', amplitude = 0)

    seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod', 'MW_Qmod'), 
                element='sync', start=5000, duration = 10000, 
                start_reference='PH_sync', 
                link_start_to='start', frequency=mw_frq_ssb, 
                amplitude=mw_amp_ssb)

    seq.clone_channel('MW_pulsemod', 'MW_Imod', 'sync', 
        start=-mw_pulse_mod_risetime, duration=2*mw_pulse_mod_risetime, 
        link_start_to = 'start', link_duration_to = 'duration',
        amplitude = 2.0)

    seq.set_instrument(ins_awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(True)
    seq.force_HW_sequencing(True)
    seq.send_sequence()
        
    return True

def rf_sequence(do_program=True):
    """
    this sequence is suited to check the relative delay between MW and RF 
    on a scope (use after calibrating MW by NV ESR using the function above).
    """
   
    mw_frq = 0.1e9
    mw_power = -20

    ins_mw.set_iq('on')
    ins_mw.set_pulm('on')
    ins_mw.set_frequency(mw_frq)
    ins_mw.set_power(mw_power)
    ins_mw.set_status('on')

    seq = Sequence('RFDelay')
    seq.add_channel('sync', 'ch1m2', high=2.0, cable_delay=0)
    seq.add_channel('MW_pulsemod', 'ch4m2', high=2.0, cable_delay = 140)
    seq.add_channel('MW_Imod', 'ch3', high=0.9, low=-0.9, 
        cable_delay = 120)
    
    seq.add_element('rfdelay', goto_target='rfdelay')
    
    seq.add_pulse('sync', 'sync', 'rfdelay', duration=1000)
    seq.add_pulse('delay', 'sync', 'rfdelay', 
            duration=20000, amplitude=0, start=0,
            start_reference='sync', link_start_to='start')

    seq.add_pulse('mw', 'MW_Imod', 'rfdelay', amplitude=0.5,
            duration=5000, start=5000, start_reference='sync',
            link_start_to='start')
    
    seq.clone_channel('MW_pulsemod', 'MW_Imod', 'rfdelay', 
            start=-mw_pulse_mod_risetime, duration=2*mw_pulse_mod_risetime, 
            link_start_to = 'start', link_duration_to = 'duration',
            amplitude = 2.0)
    
    seq.set_instrument(ins_awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(True)
    seq.force_HW_sequencing(True)
    seq.send_sequence()
        
    return True



rf_sequence()

