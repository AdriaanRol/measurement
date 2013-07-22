import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)

N_rabi_frequency = 5.532e3

class TomoDebug(BSM.NTomo):

    def get_sweep_elements(self):
        
        # just make an empty element, i.e., do tomography on the initialized state
        e = element.Element('Empty', pulsar=qt.pulsar)
        e.append(self.T)
        e.append(self.shelving_pulse)
        e.append(self.T)
        e.append(pulse.cp(self.N, length=1e-6))
        self.element = e

        self.params['tomo_time_offset'] = 0

        return BSM.NTomo.get_sweep_elements(self)\

class NPhaseCheck(BSM.NReadoutMsmt):
    mprefix = 'BSM_PhaseCheck'

    def get_sweep_elements(self):        
        
        e = element.Element('e1', pulsar=qt.pulsar)
        e.append(self.T)
        e.append(self.shelving_pulse)
        e.append(pulse.cp(self.T, length=100e-9))
        n = e.append(self.N_pi2)
        t = e.length()-e.pulse_start_time(n, 'RF')

        elts = []
        for i in range(self.params['pts']):            
            e2 = element.Element('e2-{}'.format(i), 
                pulsar=qt.pulsar)            
            e2.append(pulse.cp(self.N_pi2,
                phase = BSM.phaseref(self.N_pi2.frequency,t) + self.params['phases'][i]))
            e2.append(self.TN)
            # e2.append(self.pi2pi_m1)
            
            elts.append([e,e2])
        
        return elts

class HadamardTomo(BSM.NTomo):
    mprefix = 'BSM_TomoHadamard'

    def get_sweep_elements(self):
        e = element.Element('Hadamard', pulsar=qt.pulsar)
        e.append(self.T)
        e.append(self.shelving_pulse)
        e.append(pulse.cp(self.T, length=100e-9))
        
        # this is for using the detuned pi pulse
        # prep_name = e.append(pulse.cp(self.N_pi2,
        #     phase = BSM.phaseref(self.N_pi2.frequency, 
        #         -self.N_pi2.length) - 90.,
        #     amplitude = 1))

        # hadamard_name = e.append(pulse.cp(self.N_pulse,
        #     frequency = self.N_pi.frequency - self.params['N_rabi_frequency'],
        #     length = self.N_pi.length / np.sqrt(2),
        #     amplitude = 1,
        #     phase = 36.5))

        # t = e.length()-e.pulse_start_time(hadamard_name, 'RF')

        # this is by using two rotations around x/y -- This works much better!

        prep_name = e.append(pulse.cp(self.N_pi2,
            phase = -90,
            amplitude = 1))

        # first a pi/2 over +Y
        h_pi2_name = e.append(pulse.cp(self.N_pi2,
            phase = BSM.phaseref(self.N_pi2.frequency, 
                e.pulse_length(prep_name)),
            amplitude = 1))
        
        # then a pi over +X
        h_pi_name = e.append(pulse.cp(self.N_pi,
            phase = BSM.phaseref(self.N_pi2.frequency,
                e.pulse_length(prep_name)+e.pulse_length(h_pi2_name)) + 90.,
            amplitude = 1))

        self.element = e
        self.params['tomo_time_offset'] = e.length() - e.pulse_start_time(prep_name, 'RF')

        return BSM.NTomo.get_sweep_elements(self)

class HadamardPhaseSweep(BSM.NReadoutMsmt):
    mprefix = 'BSM_HadamardPhaseSweep'

    def generate_sequence(self, upload=True):
        self._pulse_defs()        

        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix,
            self.name))
        
        elements = []
        elements.append(self.mbi_elt)
        elements.append(self.sync_elt)

        e = element.Element('H pulse', pulsar=qt.pulsar)
        e.append(self.T)
        e.append(self.shelving_pulse)
        e.append(pulse.cp(self.T, length=100e-9))
        n = e.append(pulse.cp(self.N_pulse,
            frequency = self.N_pi.frequency - self.params['N_rabi_frequency'],
            length = self.N_pi.length / np.sqrt(2),
            amplitude = 1))
        t = e.length()-e.pulse_start_time(n, 'RF')

        e2 = element.Element('pi2', pulsar=qt.pulsar)            
        e2.append(pulse.cp(self.N_pi2,
            phase = BSM.phaseref(
                self.N_pi2.frequency, t)))
        e2.append(self.TN)
        e2.append(pulse.cp(self.pi2pi_m1))

        elements.append(e2)

        for i in range(self.params['pts']):
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'H-{}'.format(i))
            
            e = element.Element('H pulse-{}'.format(i), pulsar=qt.pulsar)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(pulse.cp(self.T, length=100e-9))
            n = e.append(pulse.cp(self.N_pulse,
                frequency = self.N_pi.frequency - self.params['N_rabi_frequency'],
                length = self.N_pi.length / np.sqrt(2),
                amplitude = 1,
                phase = self.params['phases'][i]))
            elements.append(e)

            seq.append(name = 'H-{}'.format(i),
                wfname = e.name,
                trigger_wait = True)

            seq.append(name = 'pi2-{}'.format(i),
                wfname = e2.name)            

            seq.append(name = 'sync-{}'.format(i),
                wfname = self.sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(*elements)
        
        qt.pulsar.program_sequence(seq)


def tomo_debug():
    m = TomoDebug('debug')
    BSM.prepare(m)

    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 3 # must be 3 for any N-tomography msmt
    
    BSM.finish(m, debug=False)

def phase_check(name):
    m = NPhaseCheck(name)
    BSM.prepare(m)

    m.params['reps_per_ROsequence'] = 1000

    m.params['phases'] = np.array([0,180,90])
    m.params['pts'] = len(m.params['phases'])

    # for the autoanalysis
    m.params['sweep_name'] = 'second pi2 phase (deg)'
    m.params['sweep_pts'] = m.params['phases']

    BSM.finish(m, debug=False)

def H_phase_sweep(name):
    m = HadamardPhaseSweep(name)
    BSM.prepare(m)

    m.params['reps_per_ROsequence'] = 1000

    m.params['phases'] = np.linspace(0, 360, 9)
    m.params['pts'] = len(m.params['phases'])
    m.params['N_rabi_frequency'] = 5.532e3

    # for the autoanalysis
    m.params['sweep_name'] = 'second pi2 phase (deg)'
    m.params['sweep_pts'] = m.params['phases']

    BSM.finish(m, debug=False, upload=False)


def hadamard_tomo(name):
    m = HadamardTomo(name)
    BSM.prepare(m)

    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 3 # must be 3 for any N-tomography msmt

    m.params['N_rabi_frequency'] = 5.532e3
    
    BSM.finish(m, debug=False, upload=True)

if __name__ == '__main__':
    # H_phase_sweep('sweep_H_phase')
    hadamard_tomo('input=Y')
