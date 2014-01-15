# some example and test code for the pulsar sequencer

import numpy as np
from copy import deepcopy
import pulse
import element
import view

reload(pulse)
reload(element)
reload(view)

# This is an example on how to define a pulse. In practice we can then, e.g.,
# define very specific pulses, i.e., X, Y, etc., inheriting from more general 
# ones. Note that we can basically have as many channels per pulse as we want.
# this makes it easy to create pulses such as IQ modulation pulses, which
# could consist of I, Q, and pulse modulation channels.
class SomePulse(pulse.Pulse):
    def __init__(self, name='some pulse'):
        pulse.Pulse.__init__(self, name)

        self.ch1 = 'ch2'
        self.ch2 = 'ch3'
        
        # this list is required for the pulse to work nicely together with the
        # element class
        self.channels = [self.ch1, self.ch2]
        
        self.amp = None
        self.frq = None

    def __call__(self, frq, amp, length):
        self.frq = frq
        self.amp = amp
        self.length = length
        return self

    # this function is called by the element class. it'll always
    # pass a list of time values that start with 0 and have a spacing
    # given by the clock. how many, depends on self.length and the clock
    # of the element (element determines the best raster)
    # the nominal start time of the pulse within the element is given
    # by self._t0 (set by the element).
    def chan_wf(self, chan, tvals):
        ch1vals = self.amp * np.sin(2*pi*self.frq*tvals)
        ch2vals = self.amp/2. * np.cos(2*pi*self.frq*tvals)
        
        if chan == self.ch1:
            return ch1vals
        elif chan == self.ch2:
            return ch2vals
        else:
            raise Exception('unknown channel {}'.format(chan))

# e = element.Element('sequence_element', clock=1e9, min_samples=0)
# e.define_channel('ch1', delay=0e-9)
# e.define_channel('ch2', delay=0e-9)
# e.define_channel('ch3', delay=0e-9)

# p1 = pulse.SquarePulse('ch1', 'square')
# p2 = SomePulse('what a useless pulse')

# # note here that by calling the pulse with options we can configure 
# # at insertion time.
# # a difference with Lucio's sequencer: the reference time is evaluated
# # at insertion time, i.e. manipulation of pulses inside the element
# # (they are deep copies) can break the reference relation!
# e.add(pulse.cp(p1, amplitude=1, length=10e-8), name='reference')
# e.add(pulse.cp(p1, amplitude=0.5, length=10e-9), start=10e-9, 
#     refpulse='reference', refpoint='end')
# e.add(pulse.cp(p2, 1e7, 1, 1e-7), start=10e-9)

# e.print_overview()
# view.show_element(e, delay=True) # if delay is false, the channel delay shift
#                                  # is omitted in the plots (channels are offset then)

e2 = element.Element('sequence_element', clock=1e9, min_samples=0,
    global_time=True, time_offset=1.236e-6)

e2.define_channel('ch1', delay=110e-9)
e2.define_channel('ch2', delay=100e-9)
e2.define_channel('ch3', delay=120e-9)

e2.append(
    pulse.cp(p1, amplitude=1, length=100e-9),
    pulse.cp(p1, amplitude=0.5, length=10e-9),
    pulse.cp(p2, 1e7, 1, 1e-7))

e2.print_overview()

print e2.next_pulse_time('ch1'), e2.next_pulse_time('ch2'), \
    e2.next_pulse_time('ch3')
print e2.next_pulse_global_time('ch1'), e2.next_pulse_global_time('ch2'), \
    e2.next_pulse_global_time('ch3')

view.show_element(e2, delay=True)