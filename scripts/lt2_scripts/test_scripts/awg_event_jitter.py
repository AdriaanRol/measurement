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
        strobe_chan='strobe'
        event_chan='event'
        
        
        
        awgcfg.configure_sequence(seq, 'awg_event_jitter')
        
        ename='before_jump'
        seq.add_element(ename,goto_target='before_jump')
        seq.add_pulse('trigger',trigger_chan,ename,start=0,duration=2000,
                amplitude=1)
        seq.add_pulse('strobe',strobe_chan,ename,start=45000,
                start_reference='trigger', link_start_to = 'end',duration=2000, amplitude=1)   
        seq.add_pulse('event',event_chan,ename,start=0,
                    link_start_to = 'end',duration=60000,
                amplitude=1)

        
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
