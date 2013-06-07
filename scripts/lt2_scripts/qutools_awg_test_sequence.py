import os
import qt
import numpy as np
import msvcrt

from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels_lt2 as awgcfg

Nreps = 50000
pulses_per_element = 100
syncs_per_pulse = 1
interpulse_delay = 2950 #(1000 - (2*syncs_per_pulse-1)*pulse_len) #ns
presync_delay = 50 #ns
sync_ch1_delay = 10 #ns
avg_stop_jitter = 0.0001 #ns
pulse_len = 50 #ns
for_evah = False


AWG = qt.instruments['AWG']

def generate_sequence(do_program=True):
    seq = Sequence('QuTau')
    jitters = 5*np.ones(pulses_per_element)
    #jitters = np.random.exponential(avg_stop_jitter, pulses_per_element)
    jitters = jitters.astype(int)
    #jitters[0] = 0
    #jitters[np.where(jitters > 50)[0]] = 1
    #jitters[np.where(jitters < 1)[0]] = 1
  
    #awgcfg.configure_sequence(seq, {'' : {'ch1m1', 'ch1m2'}})

    seq.add_channel(name = 'sync_chan', AWG_channel = 'ch3m1', high = 2.7)
    seq.add_channel(name = 'ch1_chan', AWG_channel = 'ch4m1', high = 2.7)
    seq.add_channel(name = 'ch2_chan', AWG_channel = 'ch4m2', high = 2.7)
    
    ename='Element1'

    if for_evah:
        seq.add_element(ename, repetitions = Nreps, goto_target = ename)
    else:    
        seq.add_element(ename, repetitions = Nreps)

    
    for k in range(pulses_per_element):
        #add the syncs
        if k>0:
            for p in range(syncs_per_pulse):
                if p == 0:
                    last = 'Wait_%d'%(k-1)
                else:
                    last = 'Wait_for_Next_Presync_%d_%d'%(p-1,k)
                
                seq.add_pulse('PreSync_%d_for_Sync_%d'%(p,k), 'sync_chan', ename, start = 0, 
                    start_reference = last, link_start_to = 'end',
                    duration = pulse_len, amplitude = 2.0)
                    
                seq.add_pulse('Wait_for_Next_Presync_%d_%d'%(p,k), 'sync_chan', ename ,start = 0, 
                    start_reference = 'PreSync_%d_for_Sync_%d'%(p,k), link_start_to = 'end', 
                    duration = presync_delay, amplitude = 0)
            
            last = 'PreSync_%d_for_Sync_%d'%(p,k)
            
            seq.add_pulse('Sync_%d'%k, 'sync_chan', ename, start = 0, 
                start_reference = 'Wait_%d'%(k-1), link_start_to = 'end',
                duration = pulse_len, amplitude = 2.0)
        else:
            for p in range(syncs_per_pulse):
                if p == 0:
                    #this is the first pulse in the pulse train
                    seq.add_pulse('PreSync_%d_for_Sync_%d'%(p,k), 'sync_chan', ename, start = 0, 
                        duration = pulse_len, amplitude = 2.0)
                else:
                    last = 'Wait_for_Next_Presync_%d_%d'%(p-1,k)
                
                    seq.add_pulse('PreSync_%d_for_Sync_%d'%(p,k), 'sync_chan', ename, start = 0, 
                        start_reference = last, link_start_to = 'end',
                        duration = pulse_len, amplitude = 2.0)
                    
                seq.add_pulse('Wait_for_Next_Presync_%d_%d'%(p,k), 'sync_chan', ename ,start = 0, 
                    start_reference = 'PreSync_%d_for_Sync_%d'%(p,k), link_start_to = 'end', 
                    duration = presync_delay, amplitude = 0)
            
            seq.add_pulse('Sync_%d'%k, 'sync_chan', ename, start = 0,
                duration = pulse_len, amplitude = 2.0)
        
        seq.add_pulse('Wait_%d'%k, 'sync_chan', ename ,start = 0, 
                start_reference = 'Sync_%d'%k, link_start_to = 'end', 
                duration = interpulse_delay, amplitude = 0)    

        #add the ch1 stops
        if k>0:
            seq.add_pulse('Stop_ch1_%d'%k, 'ch1_chan', ename, 
                    start = 0, 
                    start_reference = 'StopWait_ch1_%d'%(k-1), link_start_to = 'end',
                    duration = pulse_len, amplitude = 2.0)
        else:
            seq.add_pulse('Stop_ch1_%d'%k, 'ch1_chan', ename, 
                    start = sync_ch1_delay,
                    start_reference = 'PreSync_%d_for_Sync_%d'%(syncs_per_pulse-1,k), link_start_to = 'end',
                    duration = pulse_len, amplitude = 2.0)
        
        seq.add_pulse('StopWait_ch1_%d'%k, 'ch1_chan', ename ,start = 0, 
                start_reference = 'Stop_ch1_%d'%k, link_start_to = 'end', 
                duration = interpulse_delay, amplitude = 0)        
        
        #add the ch2 stops
        if k>0:
            
            seq.add_pulse('Stop_ch2_%d'%k, 'ch2_chan', ename, 
                    start = jitters[k], 
                    start_reference = 'StopWait_ch2_%d'%(k-1), link_start_to = 'end',
                    duration = pulse_len, amplitude = 2.0)
        else:
            seq.add_pulse('Stop_ch2_%d'%k, 'ch2_chan', ename, 
                    start = sync_ch1_delay + jitters[0],
                    start_reference = 'PreSync_%d_for_Sync_%d'%(syncs_per_pulse-1,k), link_start_to = 'end',
                    duration = pulse_len, amplitude = 2.0)
        
        seq.add_pulse('StopWait_ch2_%d'%k, 'ch2_chan', ename ,start = 0, 
                start_reference = 'Stop_ch2_%d'%k, link_start_to = 'end', 
                duration = interpulse_delay-jitters[k], amplitude = 0)                  
   
    seq.set_instrument(AWG)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()
    
    print "Total number of syncs in Sequence: %e pulses"%(Nreps*pulses_per_element)

    return True
    
if __name__ == '__main__':
    generate_sequence()

