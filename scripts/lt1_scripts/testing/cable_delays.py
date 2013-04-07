#GreenAOM.set_power(0)
#Velocity1AOM.set_power(0)
#Velocity2AOM.set_power(0)

import numpy as np
import time
from qt import instruments
from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.sequence import common as commonseq

ins_awg = qt.instruments['AWG']
ins_mw = qt.instruments['SMB100']

mw_frq = 2.820e9
mw_power = 6
mw_amp_ssb = 0.9
mw_frq_ssb = 30e6
mw_pulse_mod_risetime = 5

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


def mw_and_rf_sequence(do_program=True):
    """
    Use this sequence for checking on the fast sampling scope
    """

    mw_frq = 1e9 - 25e6
    mw_power = 0

    ins_mw.set_iq('on')
    ins_mw.set_pulm('on')
    ins_mw.set_frequency(mw_frq)
    ins_mw.set_power(mw_power)
    ins_mw.set_status('on')

    seq = Sequence('Test')
    seq.add_channel('MW_pulsemod', 'ch1m1', high=2.0, cable_delay=44)
    seq.add_channel('MW_Imod', 'ch3', high=0.9, low=-0.9, 
        cable_delay = 27)
    seq.add_channel('MW_Qmod', 'ch4', high=0.9, low=-0.9, 
        cable_delay = 27)
    
    seq.add_channel('RF', 'ch1', high=2, low=-2, 
        cable_delay = 0)

    seq.add_channel('trigger', 'ch2', high=.5, low=0, cable_delay=0)

    seq.add_element('test', goto_target='test')
    
    seq.add_pulse('trigger', 'trigger', 'test', amplitude=.5,
            duration=20, start=0)
    seq.add_pulse('filler', 'trigger', 'test', amplitude=0,
            duration=1000, start=0)
    
    seq.add_IQmod_pulse(name='mwpulse', channel=('MW_Imod', 'MW_Qmod'),
            element = 'test', 
            start = 300,
            duration = 20, 
            frequency = 25e6,
            amplitude = 0.9)

    seq.add_pulse('pmod', 'MW_pulsemod', 'test', amplitude=2.0,
            duration=26, start=-3, start_reference='mwpulse-I',
            link_start_to='start')

    seq.add_pulse('rf', 'RF', 'test',
            shape='sine', frequency=1e6, amplitude=1, duration=50, start=10,
            start_reference='mwpulse-I', link_start_to='end')

    seq.set_instrument(ins_awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(True)
    seq.force_HW_sequencing(True)
    seq.send_sequence()
        
    return True

def aom_sequence(do_program=True):
    """
    Simple sequence for aom cable delay and apd gate cable delay.
    Test with PH software.
    """
    seq = Sequence('Test')
    seq.add_channel('AOM', 'ch2', high=1.0, cable_delay=690, low=0.0)
    seq.add_channel('PH_start', 'ch2m2', high=2.0, low=0.0,
            cable_delay=0)
    seq.add_channel('APD_gate', 'ch2m1', high=2.0, low=0.0,
            cable_delay=163)

    seq.add_element('test', goto_target='test')
    seq.add_pulse('trigger', 'PH_start', 'test',
            duration=50, amplitude=2, start=0)
    
    seq.add_pulse('laser_low1', 'AOM', 'test',
            start=0, duration=5000, amplitude=0.0)
    
    seq.add_pulse('laser', 'AOM', 'test',
            start=1000, duration=1000, amplitude=1.0,
            start_reference='laser_low1',
            link_start_to='end')
    
    seq.add_pulse('laser_low2', 'AOM', 'test',
            start=0, duration=5000, amplitude=0.0,
            start_reference='laser',
            link_start_to='end')

    seq.add_pulse('apd_off', 'APD_gate', 'test',
            start=400, duration=200, amplitude=2.0,
            start_reference='laser',
            link_start_to='start')
    
    seq.set_instrument(ins_awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(True)
    seq.set_send_sequence(True)
    seq.set_program_channels(True)
    seq.set_start_sequence(True)
    seq.force_HW_sequencing(True)
    seq.send_sequence()

    return True

aom_sequence()

