import os
import qt
import numpy as np
import msvcrt

from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels_lt2 as awgcfg

sync_separation = 250
click_probability = 3E-1
presyncs = 5
postsyncs = 5
pulse_len = 50
forever = True
noof_entanglement_tries = 1E1
marker_after_sync = 10
click_after_sync = 25
plu_after_apd = 25

AWG = qt.instruments['AWG']

apd1_pulse1 = np.random.binomial(1, click_probability, size = noof_entanglement_tries)
apd2_pulse1 = np.random.binomial(1, click_probability, size = noof_entanglement_tries)

apd1_pulse2 = np.random.binomial(1, click_probability, size = noof_entanglement_tries)
apd2_pulse2 = np.random.binomial(1, click_probability, size = noof_entanglement_tries)

print "There should be %d entanglement events in the sequence"\
        %sum(np.logical_and(np.logical_or(apd1_pulse1,apd2_pulse1), 
                         np.logical_or(apd1_pulse2,apd2_pulse2))) 

def generate_sequence(do_program=True):
    seq = Sequence('QuTau')

    seq.add_channel(name = 'sync_chan', AWG_channel = 'ch2m2', high = 2.7)
    seq.add_channel(name = 'apd1_chan', AWG_channel = 'ch3m1', high = 2.7)
    seq.add_channel(name = 'apd2_chan', AWG_channel = 'ch3m2', high = 2.7)
    seq.add_channel(name = 'mrkr1_chan', AWG_channel = 'ch4m1', high = 2.7)
    seq.add_channel(name = 'mrkr2_chan', AWG_channel = 'ch4m2', high = 2.7)

    ename='Entanglement_Simulation'

    if forever:
        seq.add_element(ename, repetitions = 1, goto_target = ename)
    else:    
        seq.add_element(ename, repetitions = 1)
    
    for k in range(int(noof_entanglement_tries)):

        if k==0:
            last = ''
        else:
            last = last
            
        #presyncs
        for p in range(presyncs):
            if p == 0:
                seq.add_pulse('PreSync_%d_%d'%(p,k), 'sync_chan', 
                        ename, start = 0, start_reference = last, link_start_to = 'end',
                        duration = 50, amplitude = 2.7)
            elif p > 0:
                seq.add_pulse('PreSync_%d_%d'%(p,k), 'sync_chan', 
                        ename, start = sync_separation-50, 
                        start_reference = last, link_start_to = 'end',
                        duration = 50, amplitude = 2.7)

            last = 'PreSync_%d_%d'%(p,k)
        
        #marker
        seq.add_pulse('Marker1_%d'%k, 'mrkr1_chan', 
                ename, start = marker_after_sync, 
                start_reference = last, link_start_to = 'end',
                duration = 50, amplitude = 2.7)
        
        #real sync 1
        seq.add_pulse('RealSync1_%d'%k, 'sync_chan', 
                ename, start = sync_separation-50, 
                start_reference = last, link_start_to = 'end',
                duration = 50, amplitude = 2.7)

        #possible click apd 1 or apd 2
        if apd1_pulse1[k]:
            seq.add_pulse('1st_APD1_%d'%k, 'apd1_chan', 
                    ename, start = click_after_sync, 
                    start_reference = 'RealSync1_%d'%k, link_start_to = 'end',
                    duration = 50, amplitude = 2.7)
        if apd2_pulse1[k]:
            seq.add_pulse('1st_APD2_%d'%k, 'apd2_chan', 
                    ename, start = click_after_sync, 
                    start_reference = 'RealSync1_%d'%k, link_start_to = 'end',
                    duration = 50, amplitude = 2.7)

        #real sync 2
        seq.add_pulse('RealSync2_%d'%k, 'sync_chan', 
                ename, start = sync_separation-50, 
                start_reference = 'RealSync1_%d'%k, link_start_to = 'end',
                duration = 50, amplitude = 2.7)

        #possible click apd 1 or apd 2
        if apd1_pulse2[k]:
            seq.add_pulse('2nd_APD1_%d'%k, 'apd1_chan', 
                    ename, start = click_after_sync, 
                    start_reference = 'RealSync2_%d'%k, link_start_to = 'end',
                    duration = 50, amplitude = 2.7)
        if apd2_pulse2[k]:
            seq.add_pulse('2nd_APD2_%d'%k, 'apd2_chan', 
                    ename, start = click_after_sync, 
                    start_reference = 'RealSync2_%d'%k, link_start_to = 'end',
                    duration = 50, amplitude = 2.7)

        #if two clicks, then a marker on mrkr2_chan
        if (apd1_pulse1[k] or apd2_pulse1[k]) and (apd1_pulse2[k] or apd2_pulse2[k]):
            print "Entanglemet event generated!"
            
            if apd1_pulse2[k] > 0:
                start_ref = '2nd_APD1_%d'%k
            else:
                start_ref = '2nd_APD2_%d'%k
            
            seq.add_pulse('Entanglement_from_PLU_%d'%k, 'mrkr2_chan', 
                    ename, start = plu_after_apd, 
                    start_reference = start_ref, link_start_to = 'end',
                    duration = 50, amplitude = 2.7)
        
        last = 'RealSync2_%d'%k

        #postsyncs
        for p in range(postsyncs):
            seq.add_pulse('PostSync_%d_%d'%(p,k), 'sync_chan', 
                    ename, start = sync_separation-50, 
                    start_reference = last, link_start_to = 'end',
                    duration = 50, amplitude = 2.7)

            last = 'PostSync_%d_%d'%(p,k)
            
        #wait some time
        seq.add_pulse('Wait_%d'%k, 'sync_chan', 
            ename, start = 0, 
            start_reference = last, link_start_to = 'end',
            duration = 7200, amplitude = 0)

        last = 'Wait_%d'%k

    seq.set_instrument(AWG)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()
    
    return True
    
if __name__ == '__main__':
    generate_sequence()

