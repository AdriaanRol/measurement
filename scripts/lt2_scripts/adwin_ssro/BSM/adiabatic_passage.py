import qt
import numpy as np
from measurement.lib.pulsar import pulse, pulselib, element
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

import pulsar_mbi_espin_funcs as funcs
reload(funcs)

### the adiabatic passage pulse
class AdiabaticPassagePulse(pulselib.MW_IQmod_pulse):
    def __init__(self, name, **kw):
        pulselib.MW_IQmod_pulse.__init__(self, name, 
            I_channel='MW_Imod', 
            Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            PM_risetime=2e-9, **kw)

        self.fstart = kw.pop('fstart', None)
        self.fstop = kw.pop('fstop', None)

    def __call__(self, **kw):
        pulselib.MW_IQmod_pulse.__call__(self, **kw)

        self.fstart = kw.pop('fstart', self.fstart)
        self.fstop = kw.pop('fstop', self.fstop)

        return self

    def wf(self, tvals):
        PM_wf = np.ones(len(tvals))     
        idx0 = np.where(tvals >= self.PM_risetime)[0][0]
        idx1 = np.where(tvals <= self.length - self.PM_risetime)[0][-1] + 1

        # correct the time axis -- we want the IQ pulses to be the reference
        self._t0 += tvals[idx0] # reference time within an element
        tvals -= tvals[idx0] # for the calculation of the wf

        fvals = np.linspace(self.fstart, self.fstop, len(tvals[idx0:idx1]))

        I_wf = np.zeros(len(tvals))
        I_wf[idx0:idx1] += self.amplitude * np.cos(2 * np.pi * \
                (fvals * tvals[idx0:idx1]))

        Q_wf = np.zeros(len(tvals))
        Q_wf[idx0:idx1] += self.amplitude * np.sin(2 * np.pi * \
                (fvals * tvals[idx0:idx1]))

        return {
            self.I_channel : I_wf,
            self.Q_channel : Q_wf,
            self.PM_channel : PM_wf,
            }

### msmt class
class ElectronAdiabaticPassage(pulsar_msmt.MBI):
    mprefix = 'AdiabaticPassage'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        Xpassage = AdiabaticPassagePulse('Adiabatic Passage',
            fstart=self.params['passage_start_mod_frq'],
            fstop=self.params['passage_stop_mod_frq'],
            amplitude=self.params['passage_amp'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('Passage_pt-%d' % i, pulsar=qt.pulsar)
            e.append(T, 
                pulse.cp(Xpassage,
                    length = self.params['passage_lengths'][i]),
                adwin_sync)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('MBI adiabatic passage sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name, 
                trigger_wait = True, goto_target = 'MBI-%d' % i, 
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name, 
                trigger_wait = True)

        # program AWG
        if upload:
            qt.pulsar.upload(mbi_elt, *elts)
        qt.pulsar.program_sequence(seq)

def run(name):
    m = ElectronAdiabaticPassage(name)
    funcs.prepare(m)

    pts = 5
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    # MW pulses
    m.params['passage_start_mod_frq'] = m.params['AWG_MBI_MW_pulse_mod_frq'] - 1e6
    m.params['passage_stop_mod_frq'] = m.params['AWG_MBI_MW_pulse_mod_frq'] + 1e6
    m.params['passage_amp'] = 0.015
    m.params['passage_lengths'] = np.linspace(100, 400, pts) * 1e-6

    # for the autoanalysis
    m.params['sweep_name'] = 'Passage length (us)'
    m.params['sweep_pts'] = m.params['passage_lengths'] * 1e6
    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run('sil9_only_mI=-1')

