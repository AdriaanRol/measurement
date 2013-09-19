# Implementation of sequence elements that are composed out of pulses
#
# author: Wolfgang Pfaff

import numpy as np
from copy import deepcopy
import pprint
import pulsar

class Element:
    """
    Implementation of a sequence element. 
    Basic idea: add different pulses, and compose the actual numeric
    arrays that form the amplitudes for the hardware (typically an AWG).
    """

    def __init__(self, name, **kw):
        self.name = name
        
        self.clock = kw.pop('clock', 1e9)
        self.granularity = kw.pop('granularity', 4)
        self.min_samples = kw.pop('min_samples', 960)
        self.pulsar = kw.pop('pulsar', None)

        self.global_time = kw.pop('global_time', False)
        self.time_offset = kw.pop('time_offset', 0)
        
        self.ignore_delays = kw.pop('ignore_delays',False)

        self.pulses = {}
        self._channels = {}
        self._last_added_pulse = None

        if self.pulsar != None:
            self.clock = self.pulsar.clock

            for c in self.pulsar.channels:
                chan = self.pulsar.channels[c]
                delay=chan['delay'] if not(self.ignore_delays) else 0.
                self.define_channel(name=c, type=chan['type'], 
                    high=chan['high'], low=chan['low'], offset=chan['offset'], 
                    delay=delay)


    ### tools for time calculations
    def _time2sample(self, t):
        return int(t * self.clock + 0.5)

    def _time2sampletime(self, t):
        return self._sample2time(self._time2sample(t))

    def _sample2time(self, s):
        return s / self.clock

    def offset(self):
        """
        Returns the smallest t0 of all pulses/channels after correcting for
        delay.
        """
        t0s = []
        for p in self.pulses:
            for c in self.pulses[p].channels:
                t0s.append(self.pulses[p].t0() - self._channels[c]['delay'])
                
        return min(t0s)

    def ideal_length(self):
        """
        Returns the nominal length of the element before taking into account
        the discretization using the clock.
        """
        ts = []
        for p in self.pulses:
            for c in self.pulses[p].channels:
                ts.append(self.pulse_end_time(p,c))

        return max(ts)

    def length(self):
        """
        Returns the actual length of the sequence, including all corrections.
        """
        return self.samples() / self.clock

    def samples(self):
        """
        Returns the number of samples the elements occupies.
        """
        ends = []
        for p in self.pulses:
            for c in self.pulses[p].channels:
                ends.append(self.pulse_end_sample(p,c))

        samples = max(ends)+1
        if samples < self.min_samples:
            samples = self.min_samples
        else:
            while(samples % self.granularity > 0):
                samples += 1
                
        return samples

    def real_time(self, t, channel):
        """
        Returns an actual time, i.e., the correction for delay 
        is reversed. It is, however, correctly discretized.
        """
        return int((t + self._channels[channel]['delay'])*self.clock \
            + 0.5) / self.clock

    def real_times(self, tvals, channel):
        return ((tvals + self._channels[channel]['delay'])*self.clock \
            + 0.5).astype(int) / self.clock


    ### channel management
    def define_channel(self, name, type='analog', high=1, low=-1, offset=0, 
            delay=0):
        
        self._channels[name] = {
            'type' : type,
            'delay' : delay,
            'offset' : offset,
            'high' : high,
            'low' : low,
            }

    def channel_delay(self, cname):
        return self._channels[cname]['delay']

    ### pulse management
    def _auto_pulse_name(self, base='pulse'):
        i = 0
        while base+'-'+str(i) in self.pulses:
            i += 1
        return base+'-'+str(i)

    def add(self, pulse, name=None, start=0, 
            refpulse=None, refpoint='end', refpoint_new='start'):

        pulse = deepcopy(pulse)
        if name == None:
            name = self._auto_pulse_name(pulse.name)

        t0 = start - pulse.start_offset

        if refpulse != None:
            if refpoint == None:
                refpoint = 'end'

            if refpoint_new == 'start':
                t0 += self.pulses[refpulse].effective_stop()

                if refpoint == 'start':
                    t0 -= self.pulses[refpulse].effective_length()
                elif refpoint == 'center':
                    t0 -= self.pulses[refpulse].effective_length()/2.

            elif refpoint_new == 'end':
                t0 += (self.pulses[refpulse].effective_stop() - pulse.effective_length())

                if refpoint == 'start':
                    t0 -= self.pulses[refpulse].effective_length()
                elif refpoint == 'center':
                    t0 -= self.pulses[refpulse].effective_length()/2.
            
            elif refpoint_new == 'center':
                t0 += (self.pulses[refpulse].effective_stop()- pulse.effective_length()/2.)

                if refpoint == 'start':
                    t0 -= self.pulses[refpulse].effective_length()
                elif refpoint == 'center':
                    t0 -= self.pulses[refpulse].effective_length()/2.                   



        pulse._t0 = t0
        self.pulses[name] = pulse
        self._last_added_pulse = name

        return name

    #def append(self, pulse):
    #    n = self.add(pulse, refpulse=self._last_added_pulse, 
    #        refpoint='end')
    #    
    #    return n

    def append(self, *pulses):
        for i,p in enumerate(pulses):
            if i == 0:
                n = self.add(p, refpulse=self._last_added_pulse, 
                    refpoint='end')
            else:
                n = self.add(p, refpulse=n, 
                    refpoint='end')
        return n

    def next_pulse_time(self, cname, t0=0):
        refpulse = self._last_added_pulse

        if refpulse == None:
            return 0

        t0 += self.pulses[refpulse].effective_stop()
        return t0 - self.channel_delay(cname) - self.offset()

    def next_pulse_global_time(self, cname, t0=0):
        refpulse = self._last_added_pulse

        if refpulse == None:
            return self.time_offset - self.channel_delay(cname)

        t0 += self.pulses[refpulse].effective_stop()
        return t0 + self.time_offset - self.offset()

    def pulse_start_time(self, pname, cname):
        return self.pulses[pname].t0() - self._channels[cname]['delay'] - \
            self.offset()

    def pulse_end_time(self, pname, cname):
        return self.pulses[pname].end() - self._channels[cname]['delay'] - \
            self.offset()

    def pulse_global_end_time(self, pname, cname):
        return self.pulse_end_time(pname, cname) + self.time_offset - self.offset()

    def pulse_length(self, pname):
        return self.pulses[pname].length

    def pulse_start_sample(self, pname, cname):
        return self._time2sample(self.pulse_start_time(pname, cname))

    def pulse_samples(self, pname):
        return self._time2sample(self.pulses[pname].length)

    def pulse_end_sample(self, pname, cname):
        return self.pulse_start_sample(pname, cname) + \
            self.pulse_samples(pname) - 1

    def effective_pulse_start_time(self, pname, cname):
        return self.pulse_start_time(pname, cname) + \
            self.pulses[pname].start_offset

    def effective_pulse_end_time(self, pname, cname):
        return self.pulse_end_time(pname, cname) - \
            self.pulses[pname].stop_offset

    
    ### computing the numerical waveform
    def ideal_waveforms(self):
        # tvals = np.arange(self.samples())/self.clock
        wfs = {}
        tvals = np.arange(self.samples())/self.clock

        for c in self._channels:
            wfs[c] = np.zeros(self.samples()) + self._channels[c]['offset']

        # we first compute the ideal function values
        for p in self.pulses:
            psamples = self.pulse_samples(p)            

            if not self.global_time:                
                pulse_tvals = tvals.copy()[:psamples]
                pulsewfs = self.pulses[p].get_wfs(pulse_tvals)
            else:                
                chan_tvals = {}
                
                for c in self.pulses[p].channels:
                    idx0 = self.pulse_start_sample(p,c)
                    idx1 = self.pulse_end_sample(p,c) + 1
                    c_tvals = np.round(tvals.copy()[idx0:idx1] + \
                        self.channel_delay(c) + self.time_offset, pulsar.SIGNIFICANT_DIGITS)
                    chan_tvals[c] = c_tvals
                
                pulsewfs = self.pulses[p].get_wfs(chan_tvals)

            for c in self.pulses[p].channels:
                idx0 = self.pulse_start_sample(p,c)
                idx1 = self.pulse_end_sample(p,c) + 1
                wfs[c][idx0:idx1] += pulsewfs[c]

        return tvals, wfs

    def waveforms(self):
        """
        Returns the waveforms for all used channels.
        """
        tvals, wfs = self.ideal_waveforms()
        for wf in wfs:
            hi = self._channels[wf]['high']
            lo = self._channels[wf]['low']
            
            # truncate all values that are out of bounds
            if self._channels[wf]['type'] == 'analog':
                wfs[wf][wfs[wf] > hi] = hi
                wfs[wf][wfs[wf] < lo] = lo
            elif self._channels[wf]['type'] == 'marker':
                wfs[wf][wfs[wf] > lo] = hi
                wfs[wf][wfs[wf] < lo] = lo

        return tvals, wfs

    def normalized_waveforms(self):
        """
        Returns the final numeric arrays, in which channel-imposed
        restrictions are obeyed (bounds, TTL)
        """
        tvals, wfs = self.waveforms()

        for wf in wfs:
            hi = self._channels[wf]['high']
            lo = self._channels[wf]['low']

            if self._channels[wf]['type'] == 'analog':
                wfs[wf] = (2.0*wfs[wf] - hi - lo) / (hi - lo)
            elif self._channels[wf]['type'] == 'marker':
                wfs[wf][wfs[wf] > lo] = 1
                wfs[wf][wfs[wf] <= lo] = 0

        return tvals, wfs

    ### testing and inspection
    def print_overview(self):
        overview = {}
        overview['length'] = self.length()
        overview['samples'] = self.samples()
        overview['offset'] = self.offset()
        overview['ideal length'] = self.ideal_length()

        overview['pulses'] = {}
        pulses = overview['pulses']     
        for p in self.pulses:
            pulses[p] = {}

            pulses[p]['length'] = self.pulse_length(p)
            pulses[p]['samples'] = self.pulse_samples(p)
            
            for c in self.pulses[p].channels:
                pulses[p][c] = {}
                pulses[p][c]['start time'] = self.pulse_start_time(p,c)
                pulses[p][c]['end time'] = self.pulse_end_time(p,c)
                pulses[p][c]['start sample'] = self.pulse_start_sample(p,c)
                pulses[p][c]['end sample'] = self.pulse_end_sample(p,c)
                

        pprint.pprint(overview)





