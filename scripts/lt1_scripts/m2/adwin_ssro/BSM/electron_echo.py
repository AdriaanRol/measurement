import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)


class RamseyPhaseSweep(BSM.ElectronReadoutMsmt):
    mprefix = 'BSM_ERamseyPhaseSweep'

    def generate_sequence(self, upload=True):
        self._pulse_defs()

        # we want to test the phase calculations here.
        # we use some offset here in the second element (where the
        # 2nd pulse is, the rest of the delay we append to the first pulse)
        of = 100e-9

        # waiting element that takes 1 us
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(self.T, length=1e-6))

        # the element that contains the first pi/2 pulse
        first_pi2_elt = element.Element('first_pi2', pulsar=qt.pulsar)
        first_pi2_name = first_pi2_elt.append(
            pulse.cp(self.pi2_4MHz,
                lock_phase_to_element_time = False))
        first_pi2_elt.append(
            pulse.cp(self.TIQ, 
                length=self.params['delay']-of))

        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix,
            self.name))

        sweep_elements = []

        for i,p in enumerate(self.params['phases']):
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'first_pi-{}'.format(i))
            seq.append(name = 'first_pi-{}'.format(i),
                wfname=first_pi2_elt.name,
                trigger_wait = True)

            second_pi2_elt = element.Element('second_pi2-{}'.format(i),
                pulsar=qt.pulsar)
            second_pi2_elt.append(
                pulse.cp(self.TIQ, length=of))

            # calculate the phase of the second pi pulse
            # there are some assumptions in here... (element length, etc)
            phase = p + ((self.pi2_4MHz.frequency * \
                (self.params['delay'] + \
                    self.pi2_4MHz.effective_length() + \
                    self.pi2_4MHz.start_offset)) % 1) * 360

            second_pi2_elt.append(
                pulse.cp(self.pi2_4MHz,
                    lock_phase_to_element_time = False,
                    phase = phase))

            sweep_elements.append(second_pi2_elt)            
            
            seq.append(name = 'second_pi2-{}'.format(i),
                wfname = second_pi2_elt.name)
            seq.append(name = 'sync-{}'.format(i), 
                wfname = self.sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, self.sync_elt, 
                first_pi2_elt, *sweep_elements)
        
        qt.pulsar.program_sequence(seq)

# class RamseyPhaseSweep

class EchoDelaySweep(BSM.ElectronReadoutMsmt):
    """
    Sweep the interpulse delay in a Hahn Echo sequence (in units of 1 us,
    varied by changing the repetition counter of a 1 us waiting element)

    TODO could also make that more general with arbitrary waiting times?
         Then we would need variable filler elements (or variable 
         fillings eg in the pi element)
    """

    mprefix = 'BSM_EEchoDelaySweep'

    def generate_sequence(self, upload=True):
        self._pulse_defs()

        # waiting element that takes 1 us
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(self.T, length=1e-6))

        # to make sure all elements are long enough
        # time to prepend to the first and append to the second pi2 pulse
        fill_pi2_outer = 1e-6

        # time to append to the first and append to the second pi2 pulse
        # to make sure this really defines the timing (and not some delay)
        fill_pi2_inner = 100e-9

        # filling for the pi element, symmetric
        fill_pi = 900e-9

        elements = []
        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix,
            self.name))

        first_pi2_elt = element.Element('first_pi2', pulsar=qt.pulsar)
        first_pi2_elt.append(
            pulse.cp(self.TIQ, length=fill_pi2_outer),
            pulse.cp(self.pi2_4MHz, 
                lock_phase_to_element_time = False),
            pulse.cp(self.TIQ, length=fill_pi2_inner))
        
        elements.append(first_pi2_elt)
        elements.append(self.mbi_elt)
        elements.append(wait_1us)
        elements.append(self.sync_elt)
        
        for i,d in enumerate(self.params['delay_repetitions']):
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'first_pi2-{}'.format(i))
            seq.append(name = 'first_pi2-{}'.format(i),
                wfname = first_pi2_elt.name,
                trigger_wait = True)

            # waiting time - one us is already covered by the filling times
            if d > 1:
                seq.append(name = 'delay1-{}'.format(i),
                    wfname = wait_1us.name,
                    repetitions = (d-1))

            # calculate the phase of the pi pulse - want it to be in phase
            # with the pi/2 pulse
            pi_phase = ((self.pi2_4MHz.frequency * (
                self.pi2_4MHz.effective_length() + d * 1e-6)) % 1 ) * 360

            pi_elt = element.Element('pi-{}'.format(i), pulsar=qt.pulsar)
            pi_elt.append(
                pulse.cp(self.TIQ, length=fill_pi),
                pulse.cp(self.pi_4MHz, 
                    lock_phase_to_element_time = False,
                    phase = pi_phase),
                pulse.cp(self.TIQ, length=fill_pi))

            elements.append(pi_elt)
            seq.append(name = 'pi-{}'.format(i),
                wfname = pi_elt.name)

            # second interpulse delay
            if d > 1:
                seq.append(name = 'delay2-{}'.format(i),
                    wfname = wait_1us.name,
                    repetitions = (d-1))

            # the second pi/2 pulse
            pi2_phase = ((self.pi2_4MHz.frequency * (
                self.pi2_4MHz.effective_length() + 2*d*1e-6 + \
                    self.pi_4MHz.effective_length())) % 1 ) * 360

            second_pi2_elt = element.Element('second_pi2-{}'.format(i),
                pulsar=qt.pulsar)
            second_pi2_elt.append(
                pulse.cp(self.TIQ, length=fill_pi2_inner),
                pulse.cp(self.pi2_4MHz, 
                    lock_phase_to_element_time = False,
                    phase = pi2_phase),
                pulse.cp(self.TIQ, length=fill_pi2_outer))

            elements.append(second_pi2_elt)
            seq.append(name = 'second_pi2-{}'.format(i),
                wfname = second_pi2_elt.name)

            seq.append(name = 'sync-{}'.format(i), 
                wfname = self.sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(*elements)
        
        qt.pulsar.program_sequence(seq)

    # def generate_sequence

# class EchoDelaySweep

class CORPSEEchoPhaseSweep(BSM.ElectronReadoutMsmt):

    mprefix = 'BSM_CORPSEEchoPhaseSweep'

    def generate_sequence(self, upload=True):
        self._pulse_defs()

        # waiting element that takes 1 us
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(self.T, length=1e-6))

        # to make sure all elements are long enough
        # time to prepend to the first and append to the second pi2 pulse
        fill_pi2_outer = 1e-6

        # time to append to the first and append to the second pi2 pulse
        # to make sure this really defines the timing (and not some delay)
        fill_pi2_inner = 100e-9

        # filling for the pi element, symmetric
        fill_pi = 900e-9

        # calculate the number of repetitions of the 1us wait element, add the
        # residual to 
        wait_elt_reps = int((self.params['delay'] - 1e-6) / 1e-6)
        fill_pi += (self.params['delay'] - 1e-6) % 1e-6

        elements = []
        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix,
            self.name))

        first_pi2_elt = element.Element('first_pi2', pulsar=qt.pulsar)
        first_pi2_elt.append(
            pulse.cp(self.TIQ, length=fill_pi2_outer),
            pulse.cp(self.pi2_4MHz, 
                lock_phase_to_element_time = False),
            pulse.cp(self.TIQ, length=fill_pi2_inner))
        
        elements.append(first_pi2_elt)
        elements.append(self.mbi_elt)
        elements.append(wait_1us)
        elements.append(self.sync_elt)
        
        for i,p in enumerate(self.params['phases']):
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'first_pi2-{}'.format(i))
            seq.append(name = 'first_pi2-{}'.format(i),
                wfname = first_pi2_elt.name,
                trigger_wait = True)

            # waiting time 1
            seq.append(name = 'delay1-{}'.format(i),
                wfname = wait_1us.name,
                repetitions = wait_elt_reps)

            # calculate the reference phase of the pi pulse - want it to be 
            # in phase with the pi/2 pulse
            pi_ref_phase = ((self.pi2_4MHz.frequency * (
                self.pi2_4MHz.effective_length() + \
                    self.params['delay'])) % 1 ) * 360

            pi_elt = element.Element('pi-{}'.format(i), pulsar=qt.pulsar)
            pi_elt.append(
                pulse.cp(self.TIQ, length=fill_pi),
                pulse.cp(self.CORPSE_pi, 
                    lock_phase_to_element_time = False,
                    phase = pi_ref_phase + p),
                pulse.cp(self.TIQ, length=fill_pi))

            elements.append(pi_elt)
            seq.append(name = 'pi-{}'.format(i),
                wfname = pi_elt.name)

            # second interpulse delay
            seq.append(name = 'delay2-{}'.format(i),
                wfname = wait_1us.name,
                repetitions = wait_elt_reps)

            # the second pi/2 pulse
            pi2_phase = ((self.pi2_4MHz.frequency * (
                self.pi2_4MHz.effective_length() + 2*self.params['delay'] + \
                    self.CORPSE_pi.effective_length())) % 1 ) * 360

            second_pi2_elt = element.Element('second_pi2-{}'.format(i),
                pulsar=qt.pulsar)
            second_pi2_elt.append(
                pulse.cp(self.TIQ, length=fill_pi2_inner),
                pulse.cp(self.pi2_4MHz, 
                    lock_phase_to_element_time = False,
                    phase = pi2_phase),
                pulse.cp(self.TIQ, length=fill_pi2_outer))

            elements.append(second_pi2_elt)
            seq.append(name = 'second_pi2-{}'.format(i),
                wfname = second_pi2_elt.name)

            seq.append(name = 'sync-{}'.format(i), 
                wfname = self.sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(*elements)
        
        qt.pulsar.program_sequence(seq)

    # def generate_sequence

# class CORPSEEchoPhaseSweep

class NitrogenUnconditonalRotationCalib(BSM.ElectronReadoutMsmt):
    mprefix = 'BSM_NUncondRotCalib'

    def generate_sequence(self, upload=True):
        self._pulse_defs()

        # waiting element that takes 1 us
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(self.T, length=1e-6))

        # filling for the pi element, symmetric
        fill_pi = 500e-9

        elements = []
        elements.append(self.mbi_elt)
        elements.append(wait_1us)
        elements.append(self.sync_elt)




def run_ramsey_phase_sweep(name):
    m = RamseyPhaseSweep(name)
    BSM.prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['phases'] = np.linspace(0, 360., pts)
    m.params['delay'] = 2000e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'phase (deg)'
    m.params['sweep_pts'] = m.params['phases']
    
    BSM.finish(m, debug=True)

def run_echo_delay_sweep(name):
    m = EchoDelaySweep(name)
    BSM.prepare(m)

    reps = np.arange(30,72,2)

    pts = len(reps)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['delay_repetitions'] = reps

    # for the autoanalysis
    m.params['sweep_name'] = 'Interpulse delay (us)'
    m.params['sweep_pts'] = m.params['delay_repetitions']
    
    BSM.finish(m, debug=False)

def run_CORPSE_echo_phase_sweep(name):
    m = CORPSEEchoPhaseSweep(name)
    BSM.prepare(m)

    phases = np.linspace(0,360,25)

    pts = len(phases)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['delay'] = 50.1e-6
    m.params['phases'] = phases

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params['sweep_pts'] = phases
    
    BSM.finish(m, debug=False)

if __name__ == '__main__':
    # run_ramsey_phase_sweep('sil2_test')
    # run_echo_delay_sweep('sil2_first_revival')
    run_CORPSE_echo_phase_sweep('sil2_first_revival')

