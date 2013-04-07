
import numpy as np
from qt import instruments
from measurement.lib.AWG_HW_sequencer_v2 import Sequence


ins_awg = qt.instruments['AWG']

def test_sequence(do_program=True):
    """
    an example sequence.
    """

    amp_hi = 2
    amp_lo = 1
    scaling = 0.5
    len_hi = 5000
    len_lo = 10000

    seq = Sequence('Example')
    seq.add_channel('chan1', 'ch1', high=2.0, cable_delay=0)
    seq.add_channel('chan2', 'ch2', high=2.0, cable_delay=0)
    
    seq.add_element('element1')
    
    seq.add_pulse(name='hi1',
            channel='chan1',
            element='element1',
            start = 0,
            amplitude = amp_hi,
            duration=len_hi)
    
    seq.add_pulse(name='lo1',
            channel='chan1',
            element='element1',
            start=0,
            start_reference='hi1',
            link_start_to='end',
            amplitude = amp_lo,
            duration=len_lo,
            envelope='erf',
            envelope_risetime=1000)

    seq.add_pulse(name='hi2',
            channel='chan2',
            element='element1',
            start = 0,
            start_reference='hi1',
            link_start_to='start',
            amplitude = amp_hi * scaling,
            duration=len_hi)
    
    seq.add_pulse(name='lo2',
            channel='chan2',
            element='element1',
            start=0,
            start_reference='hi2',
            link_start_to='end',
            amplitude = amp_lo * scaling,
            duration=len_lo)

    seq.add_pulse(name='wait',
            channel='chan1',
            element='element1',
            amplitude=0,
            start=0,
            start_reference='lo1',
            link_start_to = 'end',
            duration=5000)

    seq.add_element('element2', goto_target='element1',
            repetitions=20)

    seq.add_pulse(name='hi1',
            channel='chan1',
            element='element2',
            start = 0,
            amplitude = amp_hi,
            duration=len_hi)

    
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

