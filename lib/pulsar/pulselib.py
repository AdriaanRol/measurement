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
        self.lock_phase_to_element_time = kw.pop(
            'lock_phase_to_element_time', True)
        self.phase_lock_time_offset = kw.pop(
            'phase_lock_time_offset', 0)

        self.length += 2*self.PM_risetime
        self.start_offset = self.PM_risetime
        self.stop_offset = self.PM_risetime


    def __call__(self, **kw):
        self.frequency = kw.pop('frequency', self.frequency)
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length-2*self.PM_risetime) + \
            2*self.PM_risetime
        self.phase = kw.pop('phase', self.phase)
        self.lock_phase_to_element_time = kw.pop(
            'lock_phase_to_element_time', self.lock_phase_to_element_time)
        self.phase_lock_time_offset = kw.pop(
            'phase_lock_time_offset', self.phase_lock_time_offset)

        return self

    def wf(self, tvals):
        PM_wf = np.ones(len(tvals))     
        idx0 = np.where(tvals >= self.PM_risetime)[0][0]
        idx1 = np.where(tvals <= self.length - self.PM_risetime)[0][-1] + 1

        # correct the time axis -- we want the IQ pulses to be the reference
        tvals -= tvals[idx0] # for the calculation of the wf

        if self.lock_phase_to_element_time:
            self.phase += ((self.frequency * \
                (self._t0 + self.phase_lock_time_offset)) % 1) * 360

        I_wf = np.zeros(len(tvals))
        I_wf[idx0:idx1] += self.amplitude * np.cos(2 * np.pi * \
                (self.frequency * tvals[idx0:idx1] + self.phase/360.))

        Q_wf = np.zeros(len(tvals))
        Q_wf[idx0:idx1] += self.amplitude * np.sin(2 * np.pi * \
                (self.frequency * tvals[idx0:idx1] + self.phase/360.))

        return {
            self.I_channel : I_wf,
            self.Q_channel : Q_wf,
            self.PM_channel : PM_wf,
            }

# class MW_IQmod_pulse

### Shaped pulses
class IQ_CORPSE_pi_pulse(MW_IQmod_pulse):
    
     # this is between the driving pulses (not PM)

    def __init__(self, *arg, **kw):
        MW_IQmod_pulse.__init__(self, *arg, **kw)

        self.length_60 = kw.pop('length_60', 0)
        self.length_m300 = kw.pop('length_m300', 0)
        self.length_420 = kw.pop('length_420', 0)
        self.pulse_delay = kw.pop('pulse_delay', 2e-9)

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

    def wf(self, tvals):
        PM_wf = np.ones(len(tvals))
        idx0 = np.where(tvals >= self.PM_risetime)[0][0]
        idx1 = np.where(tvals <= self.length - self.PM_risetime)[0][-1] + 1

        start_420 = np.where(tvals <= (self.PM_risetime))[0][-1]
        end_420 = np.where(tvals <= (self.length_420 + self.PM_risetime))[0][-1]
        start_m300 = np.where(tvals <= (self.PM_risetime + self.length_420 + \
            self.pulse_delay))[0][-1]
        end_m300 = np.where(tvals <= (self.PM_risetime + self.length_420 + \
            self.pulse_delay + self.length_m300))[0][-1]
        start_60 = np.where(tvals <= (self.PM_risetime + self.length_420 + \
            self.pulse_delay + self.length_m300 + self.pulse_delay))[0][-1]
        end_60 = np.where(tvals <= (self.PM_risetime + self.length_420 + \
            self.pulse_delay + self.length_m300 + self.pulse_delay + \
            self.length_60))[0][-1]

        # correct the time axis -- we want the IQ pulses to be the reference
        tvals -= tvals[start_420] # for the calculation of the wf

        I_wf = np.zeros(len(tvals))
        Q_wf = np.zeros(len(tvals))

        I_wf[start_420:end_420] += self.amplitude * np.cos(2 * np.pi * \
                (self.frequency * tvals[start_420:end_420] + self.phase/360.))
        Q_wf[start_420:end_420] += self.amplitude * np.sin(2 * np.pi * \
                (self.frequency * tvals[start_420:end_420] + self.phase/360.))

        I_wf[start_m300:end_m300] -= self.amplitude * np.cos(2 * np.pi * \
                (self.frequency * tvals[start_m300:end_m300] + self.phase/360.))
        Q_wf[start_m300:end_m300] -= self.amplitude * np.sin(2 * np.pi * \
                (self.frequency * tvals[start_m300:end_m300] + self.phase/360.))

        I_wf[start_60:end_60] += self.amplitude * np.cos(2 * np.pi * \
                (self.frequency * tvals[start_60:end_60] + self.phase/360.))
        Q_wf[start_60:end_60] += self.amplitude * np.sin(2 * np.pi * \
                (self.frequency * tvals[start_60:end_60] + self.phase/360.))

        return {
            self.I_channel : I_wf,
            self.Q_channel : Q_wf,
            self.PM_channel : PM_wf,
            }

class RF_erf_envelope(pulse.SinePulse):
    def __init__(self, *arg, **kw):
        pulse.SinePulse.__init__(self, *arg, **kw)

        self.envelope_risetime = kw.pop('envelope_risetime', 500e-9)

    def wf(self, tvals):
        wf = pulse.SinePulse.wf(self, tvals)[self.channel]
        
        # TODO make this nicer
        rt = self.envelope_risetime
        env = (ssp.erf(2./rt*(tvals-rt))/2.+0.5) * \
                (ssp.erf(-2./rt*(tvals-tvals[-1]+rt))/2. + 0.5)

        return {
            self.channel : wf * env
            }
