import numpy as np
import scipy.special as ssp

class Pulse():
    
    def __init__(self, pulse, samples, time_offset=0, clock=1e9):
        self.clock = clock    
        self.samples = samples
        self.time_offset = time_offset
        self.pulse = pulse

        self.wf_funcs = {
            'rectangular' : self._rect_wform,
            'cosine' : self._cosine_wform,
            'sine' : self._sine_wform,
            'ssb-i' : self._ssb_i_wform,
            'ssb-q' : self._ssb_q_wform,
            'IQmod-I' : self._ssb_i_wform,
            'IQmod-Q' : self._ssb_q_wform,
            'gaussian_noise' : self._gauss_rnd_wform,
            }

        self.envelope_funcs = {
            None : self._no_envelope,
            'erf' : self._erf_envelope,
            }
    
    def wform(self):
        return self.wf_funcs[self.pulse['shape']]()*self.envelope()

    def _rect_wform(self):
        return np.ones(self.samples)*self.pulse.get('amplitude', 0.)

    def _cosine_wform(self):
        f = self.pulse.get('frequency', 1e6)
        a = self.pulse.get('amplitude', 0.)
        phase = self.pulse.get('phase', 0.)
        t = np.arange(self.samples)/self.clock + self.time_offset
        d = a * np.cos(2*np.pi*(f*t + phase/360.))
        return d

    def _sine_wform(self):
        f = self.pulse.get('frequency', 1e6)
        a = self.pulse.get('amplitude', 0.)
        phase = self.pulse.get('phase', 0.)
        t = np.arange(self.samples)/self.clock + self.time_offset
        return a * np.sin(2*np.pi*(f*t + phase/360.))

    def _ssb_i_wform(self):
        return self._cosine_wform()

    def _ssb_q_wform(self):
        return self._sine_wform()
        
    def _gauss_rnd_wform(self):
        a = self.pulse.get('amplitude', 0.)
        rnd=np.random.normal(0.,a,self.samples)
        if max(rnd)>a:
            rnd=a*rnd/max(rnd)
        
        return rnd
            

    def envelope(self):
        return self.envelope_funcs[self.pulse.get('envelope', None)]()

    def _no_envelope(self):
        return 1

    def _erf_envelope(self):
        t = np.arange(self.samples)
        rt = self.pulse.get('envelope_risetime', 20)
        env = (ssp.erf(2./rt*(t-rt))/2.+0.5) * \
                (ssp.erf(-2./rt*(t-len(t)+rt))/2. + 0.5)
        return env
            



