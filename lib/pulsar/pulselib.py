import numpy as np
import scipy.special as ssp
import pulse


### Basic multichannel pulses
class MW_IQmod_pulse(pulse.Pulse):
    def __init__(self, name, I_channel, Q_channel, PM_channel, **kw):
        pulse.Pulse.__init__(self, name)

        self.I_channel = I_channel
        self.Q_channel = Q_channel
        self.PM_channel = PM_channel
        self.channels = [I_channel, Q_channel, PM_channel]

        self.frequency = kw.pop('frequency', 1e6)
        self.amplitude = kw.pop('amplitude', 0.1)
        self.length = kw.pop('length', 1e-6)
        self.phase = kw.pop('phase', 0.)
        self.PM_risetime = kw.pop('PM_risetime', 0)
        self.phaselock = kw.pop('phaselock', True)

        self.length += 2*self.PM_risetime
        self.start_offset = self.PM_risetime
        self.stop_offset = self.PM_risetime


    def __call__(self, **kw):
        self.frequency = kw.pop('frequency', self.frequency)
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length-2*self.PM_risetime) + \
            2*self.PM_risetime
        self.phase = kw.pop('phase', self.phase)
        self.phaselock = kw.pop('phaselock', self.phaselock)

        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return np.ones(len(tvals))

        else:  
            idx0 = np.where(tvals >= tvals[0] + self.PM_risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.PM_risetime)[0][-1]

            wf = np.zeros(len(tvals))
            
            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

            if chan == self.I_channel:
                wf[idx0:idx1] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[idx0:idx1] + self.phase/360.))

            if chan == self.Q_channel:
                wf[idx0:idx1] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[idx0:idx1] + self.phase/360.))

            return wf

# class MW_IQmod_pulse

### Shaped pulses
class IQ_CORPSE_pi_pulse(MW_IQmod_pulse):
    
     # this is between the driving pulses (not PM)

    def __init__(self, *arg, **kw):
        MW_IQmod_pulse.__init__(self, *arg, **kw)

        self.length_60 = kw.pop('length_60', 0)
        self.length_m300 = kw.pop('length_m300', 0)
        self.length_420 = kw.pop('length_420', 0)
        self.pulse_delay = kw.pop('pulse_delay', 1e-9)

        self.length = self.length_60 + self.length_m300 + self.length_420 + \
            2*self.pulse_delay + 2*self.PM_risetime

        self.start_offset = self.PM_risetime
        self.stop_offset = self.PM_risetime

    def __call__(self, **kw):
        MW_IQmod_pulse.__call__(self, **kw)

        self.length_60 = kw.pop('length_60', self.length_60)
        self.length_m300 = kw.pop('length_m300', self.length_m300)
        self.length_420 = kw.pop('length_420', self.length_420)
        self.pulse_delay = kw.pop('pulse_delay', self.pulse_delay)

        self.length = self.length_60 + self.length_m300 + self.length_420 + \
            2*self.pulse_delay + 2*self.PM_risetime

        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return np.ones(len(tvals))

        else:
            idx0 = np.where(tvals >= tvals[0] + self.PM_risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.PM_risetime)[0][-1] + 1

            start_420 = np.where(tvals <= (tvals[0] + self.PM_risetime))[0][-1]
            end_420 = np.where(tvals <= (tvals[0] + self.length_420 + self.PM_risetime))[0][-1]
            start_m300 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_420 + \
                self.pulse_delay))[0][-1]
            end_m300 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_420 + \
                self.pulse_delay + self.length_m300))[0][-1]
            start_60 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_420 + \
                self.pulse_delay + self.length_m300 + self.pulse_delay))[0][-1]
            end_60 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_420 + \
                self.pulse_delay + self.length_m300 + self.pulse_delay + \
                self.length_60))[0][-1]

            wf = np.zeros(len(tvals))
            
            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

            if chan == self.I_channel:
                wf[start_420:end_420] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_420:end_420] + self.phase/360.))
                wf[start_m300:end_m300] -= self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_m300:end_m300] + self.phase/360.))
                wf[start_60:end_60] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_60:end_60] + self.phase/360.))

            if chan == self.Q_channel:
                wf[start_420:end_420] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_420:end_420] + self.phase/360.))
                wf[start_m300:end_m300] -= self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_m300:end_m300] + self.phase/360.))
                wf[start_60:end_60] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_60:end_60] + self.phase/360.))

            return wf

class RF_erf_envelope(pulse.SinePulse):
    def __init__(self, *arg, **kw):
        pulse.SinePulse.__init__(self, *arg, **kw)

        self.envelope_risetime = kw.pop('envelope_risetime', 500e-9)

    def chan_wf(self, chan, tvals):
        wf = pulse.SinePulse.chan_wf(self, chan, tvals)
        
        # TODO make this nicer
        rt = self.envelope_risetime
        env = (ssp.erf(2./rt*(tvals-tvals[0]-rt))/2.+0.5) * \
                (ssp.erf(-2./rt*(tvals-tvals[0]-tvals[-1]+rt))/2. + 0.5)

        return wf * env
