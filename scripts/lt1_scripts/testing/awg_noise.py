
import numpy as np
from qt import instruments
from measurement.lib.AWG_HW_sequencer_v2 import Sequence


ins_awg = qt.instruments['AWG']

def test_sequence(do_program=True):
    """
    an example sequence.
    """

    seq = Sequence('Noise')
    seq.add_channel('chan2', 'ch2', high=2.0,low=-2.0, cable_delay=0)
    
    seq.add_element('element1',trigger_wait = False, goto_target = 'element1')
    noise=False
    if noise:
        seq.add_pulse(name='hi'+'-1',
                channel='chan2',
                element='element1',
                shape='gaussian_noise',
                start = 0,
                amplitude = 2.,
                duration=10000)
    else:
        seq.add_pulse(name='hi'+'-1',
                channel='chan2',
                element='element1',
                shape='sine',
                start = 0,
                frequency=114e6/2,
                amplitude = 2.,
                duration=10000)
            
    seq.set_instrument(ins_awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()
        
    return True

test_sequence()

