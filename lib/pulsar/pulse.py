# This module implements the basic class for pulses as well as some very
# generic pulse types.
#
# author: Wolfgang Pfaff

import numpy as np
from copy import deepcopy

def cp(pulse, *arg, **kw):
    """
    create a copy of the pulse, configure it by given arguments (using the
        call method of the pulse class), and return the copy
    """
    pulse_copy = deepcopy(pulse)
    return pulse_copy(*arg, **kw)


class Pulse:
    """
    A generic pulse. The idea is that a certain implementation of a pulse
    is able to return a 'waveform', which we define as an array of time values
    and an array of amplitude values for each channel of the pulse.
    
    There are three stages of configuring a pulse:
    1) Implementation of the specific class
    2) when adding to a sequence element (when __call__ is implemented 
       in that way)
    3) when the sequence element object calls wf() (this 'finalizes' the 
       numerical values).

    A pulse does not yet know about any discretization using a clock. 
    This is all done in the sequence element.
    
    See the examples for more information.
    """

    def __init__(self, name):
        self.length = None
        self.name = name
        self.channels = []

        self.start_offset = 0 # the time within (or outside) the pulse that is the
                              # 'logical' start of the pulse (for referencing)
        self.stop_offset = 0  # the time within (or outside) the pulse that is the
                              # 'logical' stop of the pulse (for referencing)

        self._t0 = None
        self._clock = None

    def __call__(self):
        return self

    def get_wfs(self, tvals):
        """
        The time values in tvals can always be given as one array of time
        values, or as a separate array for each channel of the pulse.
        """
        wfs = {}
        for c in self.channels:
            if type(tvals) == dict:
                wfs[c] = self.chan_wf(c, tvals[c])
            else:
                if hasattr(self, 'chan_wf'):
                    wfs[c] = self.chan_wf(c, tvals)
                elif hasattr(self, 'wf'):
                    wfs = self.wf(tvals)
                else:
                    raise Exception('Could not find a waveform-generator function!')

        return wfs

    def t0(self):
        """
        returns start time of the pulse. This is typically
        set by the sequence element at the time the pulse is added to the
        element.
        """
        return self._t0

    def effective_start(self):
        return self._t0 + self.start_offset

    def end(self):
        """
        returns the end time of the pulse.
        """
        return self._t0 + self.length

    def effective_stop(self):
        return self.end() - self.stop_offset

    def effective_length(self):
        return self.length - self.start_offset - self.stop_offset

### Some simple pulse definitions.
class SquarePulse(Pulse):
    def __init__(self, channel, name='square pulse', **kw):
        Pulse.__init__(self, name)
        
        self.channel = channel # this is just for convenience, internally
        self.channels.append(channel) # this is the part the sequencer element 
                                      # wants to communicate with
        self.amplitude = kw.pop('amplitude', 0)
        self.length = kw.pop('length', 0)

    def __call__(self, **kw):
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length)
        self.channel = kw.pop('channel', self.channel)

        self.channels = []
        self.channels.append(self.channel)

        return self

    def chan_wf(self, chan, tvals):
        return np.ones(len(tvals)) * self.amplitude


class SinePulse(Pulse):
    def __init__(self, channel, name='sine pulse', **kw):
        Pulse.__init__(self, name)
        
        self.channel = channel # this is just for convenience, internally
        self.channels.append(channel) # this is the part the sequencer element
                                      # wants to communicate with
        self.frequency = kw.pop('frequency', 1e6)
        self.amplitude = kw.pop('amplitude', 0.)
        self.length = kw.pop('length', 0.)
        self.phase = kw.pop('phase', 0.)

    def __call__(self, **kw):
        self.frequency = kw.pop('frequency', self.frequency)
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length)
        self.phase = kw.pop('phase', self.phase)

        return self

    def chan_wf(self, chan, tvals):
        return self.amplitude * np.sin(2*np.pi * \
                (self.frequency * tvals + self.phase/360.))

