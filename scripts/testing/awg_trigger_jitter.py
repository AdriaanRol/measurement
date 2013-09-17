import os
import qt
import numpy as np
import msvcrt

from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels_lt2 as awgcfg

reload(awgcfg)

 

AWG = qt.instruments['AWG']

def generate_sequence(do_program=True):
        seq = Sequence('Test')

        # vars for the channel names
        trigger_chan= 'trigger'
        
        
        awgcfg.configure_sequence(seq, 'awg_trigger_jitter')
        
        ename='trigger'
        seq.add_element(ename,goto_target='trigger')
        #start_reference='before',link_start_to='end',
        #seq.add_pulse('before',trigger_chan,ename,start=0,duration=1000,amplitude=0)
        seq.add_pulse('trigger',trigger_chan,ename,start=0,duration=500, amplitude=1)
        seq.add_pulse('wait',trigger_chan,ename,start=0,
                start_reference='trigger', link_start_to = 'end',duration=3000, amplitude=0)   
        seq.add_pulse('trigger2',trigger_chan,ename,start=0, 
                start_reference='wait',link_start_to = 'end',duration=500,
                amplitude=1)
        seq.add_pulse('wait2',trigger_chan,ename,start=0,
               start_reference='trigger2',link_start_to='end',duration=6000,
                amplitude=0)
        
         #sweep the pulse length
       
        seq.set_instrument(AWG)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        
        return True

    
if __name__ == "__main__":

    generate_sequence()
