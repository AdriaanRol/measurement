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

                print self.name, tvals[0]

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

                print self.name, tvals[0]

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

class IQ_CORPSE_pi2_pulse(MW_IQmod_pulse):
    # this is between the driving pulses (not PM)

    def __init__(self, *arg, **kw):
        MW_IQmod_pulse.__init__(self, *arg, **kw)

        self.length_24p3 = kw.pop('length_24p3', 0)
        self.length_m318p6 = kw.pop('length_m318p6', 0)
        self.length_384p3 = kw.pop('length_384p3', 0)
        self.pulse_delay = kw.pop('pulse_delay', 1e-9)

        self.length = self.length_24p3 + self.length_m318p6 + self.length_384p3 + \
            2*self.pulse_delay + 2*self.PM_risetime

        self.start_offset = self.PM_risetime
        self.stop_offset = self.PM_risetime

    def __call__(self, **kw):
        MW_IQmod_pulse.__call__(self, **kw)

        self.length_24p3 = kw.pop('length_24p3', self.length_24p3)
        self.length_m318p6 = kw.pop('length_m318p6', self.length_m318p6)
        self.length_384p3 = kw.pop('length_384p3', self.length_384p3)
        self.pulse_delay = kw.pop('pulse_delay', self.pulse_delay)

        self.length = self.length_24p3 + self.length_m318p6 + self.length_384p3 + \
            2*self.pulse_delay + 2*self.PM_risetime

        return self

    def chan_wf(self, chan, tvals):
        
        if chan == self.PM_channel:
            return np.ones(len(tvals))

        else:
            idx0 = np.where(tvals >= tvals[0] + self.PM_risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.PM_risetime)[0][-1] + 1

            start_384p3 = np.where(tvals <= (tvals[0] + self.PM_risetime))[0][-1]
            end_384p3 = np.where(tvals <= (tvals[0] + self.length_384p3 + self.PM_risetime))[0][-1]
            start_m318p6 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay))[0][-1]
            end_m318p6 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay + self.length_m318p6))[0][-1]
            start_24p3 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay + self.length_m318p6 + self.pulse_delay))[0][-1]
            end_24p3 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay + self.length_m318p6 + self.pulse_delay + \
                self.length_24p3))[0][-1]

            wf = np.zeros(len(tvals))
            
            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

                print self.name, tvals[0]

            if chan == self.I_channel:
                wf[start_384p3:end_384p3] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_384p3:end_384p3] + self.phase/360.))
                wf[start_m318p6:end_m318p6] -= self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_m318p6:end_m318p6] + self.phase/360.))
                wf[start_24p3:end_24p3] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_24p3:end_24p3] + self.phase/360.))

            if chan == self.Q_channel:
                wf[start_384p3:end_384p3] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_384p3:end_384p3] + self.phase/360.))
                wf[start_m318p6:end_m318p6] -= self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_m318p6:end_m318p6] + self.phase/360.))
                wf[start_24p3:end_24p3] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_24p3:end_24p3] + self.phase/360.))

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
                (ssp.erf(-2./rt*(tvals-tvals[-1]+rt))/2. + 0.5)

        return wf * env


class EOMAOMPulse(pulse.Pulse):
    def __init__(self, name, eom_channel, aom_channel,  **kw):
        pulse.Pulse.__init__(self, name)
        self.eom_channel = eom_channel
        self.aom_channel = aom_channel

        self.channels = [eom_channel,aom_channel] 
                                               
        self.eom_pulse_duration        = kw.pop('eom_pulse_duration'      ,2e-9) 
        self.eom_off_duration          = kw.pop('eom_off_duration'        ,150e-9)
        self.eom_off_amplitude         = kw.pop('eom_off_amplitude'       ,-.25)
        self.eom_pulse_amplitude       = kw.pop('eom_pulse_amplitude'     ,1.2)
        self.eom_overshoot_duration1   = kw.pop('eom_overshoot_duration1' ,10e-9)
        self.eom_overshoot1            = kw.pop('eom_overshoot1'          ,-0.03)
        self.eom_overshoot_duration2   = kw.pop('eom_overshoot_duration2' ,4e-9)
        self.eom_overshoot2            = kw.pop('eom_overshoot2'          ,-0.03)
        self.aom_risetime              = kw.pop('aom_risetime'            ,23e-9)

        self.start_offset   = self.eom_off_duration
        self.stop_offset    = 3*self.eom_off_duration+self.eom_pulse_duration
        self.length         = 4*self.eom_off_duration+2*self.eom_pulse_duration                                      
        
    def __call__(self,  **kw):
        self.eom_pulse_duration        = kw.pop('eom_pulse_duration'      ,self.eom_pulse_duration) 
        self.eom_off_duration          = kw.pop('eom_off_duration'        ,self.eom_off_duration)
        self.eom_off_amplitude         = kw.pop('eom_off_amplitude'       ,self.eom_off_amplitude)
        self.eom_pulse_amplitude       = kw.pop('eom_pulse_amplitude'     ,self.eom_pulse_amplitude)
        self.eom_overshoot_duration1   = kw.pop('eom_overshoot_duration1' ,self.eom_overshoot_duration1)
        self.eom_overshoot1            = kw.pop('eom_overshoot1'          ,self.eom_overshoot1)
        self.eom_overshoot_duration2   = kw.pop('eom_overshoot_duration2' ,self.eom_overshoot_duration2)
        self.eom_overshoot2            = kw.pop('eom_overshoot2'          ,self.eom_overshoot2)
        self.aom_risetime              = kw.pop('aom_risetime'            ,self.aom_risetime)
        
        self.start_offset   = self.eom_off_duration
        self.stop_offset    = 3*self.eom_off_duration+self.eom_pulse_duration        
        self.length         = 4*self.eom_off_duration+2*self.eom_pulse_duration

        return self
        
       
    def chan_wf(self, channel, tvals):
        
        tvals -= tvals[0]
        if channel == self.eom_channel:

            off_time1_start     = 0
            off_time1_stop      = np.where(tvals <= self.eom_off_duration)[0][-1]
            opt_pulse_stop      = np.where(tvals <= int(self.eom_off_duration*1e9 + \
                                                    self.eom_pulse_duration*1e9+0.5)*1e-9)[0][-1]   
            overshoot1_stop     = np.where(tvals <= int(self.eom_off_duration*1e9 + \
                                    self.eom_pulse_duration*1e9 + \
                                    self.eom_overshoot_duration1*1e9 + 0.5)*1e-9)[0][-1]
            overshoot2_stop     = np.where(tvals <= int(self.eom_off_duration*1e9 + \
                                    self.eom_pulse_duration*1e9 + self.eom_overshoot_duration1*1e9 + \
                                    self.eom_overshoot_duration2*1e9+0.5)*1e-9)[0][-1]
            off_time2_stop      = np.where(tvals <= int(self.eom_off_duration*1e9 + \
                                    self.eom_pulse_duration*1e9 + \
                                     self.eom_off_duration*1e9+0.5)*1e-9)[0][-1]
    
            #print len(tvals)
            wf = np.zeros(len(tvals)/2)
            wf[off_time1_start:off_time1_stop] += self.eom_off_amplitude
            wf[off_time1_stop:opt_pulse_stop]  += self.eom_pulse_amplitude
            wf[opt_pulse_stop:overshoot1_stop] += self.eom_overshoot1
            wf[overshoot1_stop:overshoot2_stop]+= self.eom_overshoot2
            wf[opt_pulse_stop:off_time2_stop]  += self.eom_off_amplitude

            #compensation_pulse
            wf = np.append(wf,-wf)


        if channel == self.aom_channel:

            wf = np.zeros(len(tvals))

            pulse_start = np.where(tvals <= round(self.eom_off_duration - self.aom_risetime, 9))[0][-1]
            pulse_stop  = np.where(tvals <= round(self.eom_off_duration + \
                            self.eom_pulse_duration + self.aom_risetime, 9))[0][-1]

            wf[pulse_start:pulse_stop] += 1
            
        return wf
                
