import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)

def phaseref(frequency, time, offset=0):
    return ((frequency*time + offset/360.) % 1) * 360.

def missing_grains(time, clock=1e9, granularity=4):
    if int(time*clock + 0.5) < 960:
        return 960 - int(time*clock + 0.5)

    grains = int(time*clock + 0.5)
    return granularity - grains%granularity


class Echo(BSM.ElectronReadoutMsmt):
    """
    Sweep the interpulse delay in a Hahn Echo sequence (in units of 1 us,
    varied by changing the repetition counter of a 1 us waiting element)

    TODO could also make that more general with arbitrary waiting times?
         Then we would need variable filler elements (or variable 
         fillings eg in the pi element)
    """

    mprefix = 'BSM_EEcho'

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

        # have to make sure we're not in trouble due to granularity
        fill_first_pi2_outer = fill_pi2_outer + \
            missing_grains(fill_pi2_outer + self.pi2_4MHz.effective_length() \
                + fill_pi2_inner) * 1e-9

        first_pi2_elt = element.Element('first_pi2', pulsar=qt.pulsar,
            global_time = True)
        
        first_pi2_elt.append(
            pulse.cp(self.TIQ, length=fill_first_pi2_outer),
            pulse.cp(self.pi2_4MHz),
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
            # pi_phase = phaseref(self.pi2_4MHz.frequency, 
            #     self.pi2_4MHz.effective_length() + d * 1e-6)

            fill_pi_after = fill_pi + missing_grains(2 * fill_pi + \
                self.pi_4MHz.effective_length()) * 1e-9

            pi_elt = element.Element('pi-{}'.format(i), pulsar=qt.pulsar,
                global_time = True, 
                time_offset = first_pi2_elt.length() + (d-1)*1e-6)
            
            pi_elt.append(
                pulse.cp(self.TIQ, length=fill_pi),
                pulse.cp(self.pi_4MHz), # , phase = pi_phase),
                pulse.cp(self.TIQ, length=fill_pi_after))

            elements.append(pi_elt)
            seq.append(name = 'pi-{}'.format(i),
                wfname = pi_elt.name)

            # second interpulse delay
            if d > 1:
                seq.append(name = 'delay2-{}'.format(i),
                    wfname = wait_1us.name,
                    repetitions = (d-1))

            # the second pi/2 pulse
            #pi2_phase = phaseref(self.pi2_4MHz.frequency,
            #    self.pi2_4MHz.effective_length() + 2*d*1e-6 + \
            #        self.pi_4MHz.effective_length()) + \
            #    self.params['second_pi2_phases'][i]

            fill_second_pi2_inner = 1e-6 - fill_pi_after

            second_pi2_elt = element.Element('second_pi2-{}'.format(i),
                pulsar = qt.pulsar, global_time = True,
                time_offset = first_pi2_elt.length() + 2*(d-1)*1e-6 + pi_elt.length() )
            
            second_pi2_elt.append(
                pulse.cp(self.TIQ, length = fill_second_pi2_inner),
                pulse.cp(self.pi2_4MHz), # , 
                #     lock_phase_to_element_time = False,
                #     phase = pi2_phase),
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

# class Echo

class EchoSweepPiPosition(BSM.ElectronReadoutMsmt):
    """
    Fix the total interpulse delay 2*tau, and sweep the position of the 
    pi-pulse in order to find the center of it. Msmt should have a short
    sequence, so no tinkering with elements here.
    """

    mprefix = 'BSM_EEcho'

    def generate_sequence(self, upload=True):
        self._pulse_defs()

        elements = []
        for i in range(self.params['pts']):
            e = element.Element('Echo-{}'.format(i),
                pulsar = qt.pulsar)
            e.append(pulse.cp(self.TIQ, length=500e-9))
            e.append(pulse.cp(self.pi2_4MHz,
                lock_phase_to_element_time = False))
            e.append(pulse.cp(self.TIQ, 
                length = self.params['2tau']/2. + \
                    self.params['pi_position_shifts'][i]))

            ### for doing a CORPSE pi
            pi_phase = BSM.phaseref(self.pi2_4MHz.frequency,
                self.pi2_4MHz.effective_length() + self.params['2tau']/2. + \
                    self.params['pi_position_shifts'][i])
            
            e.append(pulse.cp(self.CORPSE_pi,
                phase = pi_phase,
                frequency = self.pi2_4MHz.frequency))

            ### regular pi
            # pi_phase = BSM.phaseref(self.pi2_4MHz.frequency,
            #     self.pi2_4MHz.effective_length() + self.params['2tau']/2. + \
            #         self.params['pi_position_shifts'][i])
            
            # e.append(pulse.cp(self.pi_4MHz,
            #     lock_phase_to_element_time = False,
            #     phase = pi_phase))
            
            e.append(pulse.cp(self.TIQ,
                length = self.params['2tau']/2. - \
                    self.params['pi_position_shifts'][i]))

            ### pay attention here with which pi pulse we're using!
            second_pi2_phase = BSM.phaseref(self.pi2_4MHz.frequency,
                self.pi2_4MHz.effective_length() + self.params['2tau'] + \
                    self.CORPSE_pi.effective_length())
            
            # second_pi2_phase = BSM.phaseref(self.pi2_4MHz.frequency,
            #     self.pi2_4MHz.effective_length() + self.params['2tau'] + \
            #         self.pi_4MHz.effective_length())
            
            e.append(pulse.cp(self.pi2_4MHz,
                lock_phase_to_element_time = False,
                phase = second_pi2_phase))

            e.append(pulse.cp(self.TIQ,
                length = 500e-9))

            elements.append(e)

            # e.print_overview()

        seq = seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix,
            self.name))
        for i,e in enumerate(elements):
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'Echo-{}'.format(i))
            seq.append(name = 'Echo-{}'.format(i),
                wfname = e.name,
                trigger_wait = True)
            seq.append(name = 'sync-{}'.format(i),
                wfname = self.sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, self.sync_elt, *elements)
        
        qt.pulsar.program_sequence(seq)

# class EchoSweepPiPosition

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
        
        # have to make sure we're not in trouble due to granularity
        fill_first_pi2_outer = fill_pi2_outer + \
            missing_grains(fill_pi2_outer + self.pi2_4MHz.effective_length() \
                + fill_pi2_inner) * 1e-9    

        first_pi2_elt.append(
            pulse.cp(self.TIQ, length=fill_first_pi2_outer),
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
            pi_ref_phase = phaseref(self.pi2_4MHz.frequency,
                self.pi2_4MHz.effective_length() + \
                    self.params['delay'])

            fill_pi_after = fill_pi + missing_grains(2 * fill_pi + \
                self.CORPSE_pi.effective_length()) * 1e-9

            pi_elt = element.Element('pi-{}'.format(i), pulsar=qt.pulsar)
            pi_elt.append(
                pulse.cp(self.TIQ, length=fill_pi),
                pulse.cp(self.CORPSE_pi, 
                    lock_phase_to_element_time = False,
                    phase = pi_ref_phase + p),
                pulse.cp(self.TIQ, length=fill_pi_after))

            elements.append(pi_elt)
            seq.append(name = 'pi-{}'.format(i),
                wfname = pi_elt.name)

            # second interpulse delay
            seq.append(name = 'delay2-{}'.format(i),
                wfname = wait_1us.name,
                repetitions = wait_elt_reps)

            # the second pi/2 pulse
            pi2_phase = phaseref(self.pi2_4MHz.frequency, 
                self.pi2_4MHz.effective_length() + 2*self.params['delay'] + \
                    self.CORPSE_pi.effective_length())

            fill_second_pi2_inner = self.params['delay'] - \
                wait_elt_reps*1e-6 - fill_pi_after

            second_pi2_elt = element.Element('second_pi2-{}'.format(i),
                pulsar=qt.pulsar)
            second_pi2_elt.append(
                pulse.cp(self.TIQ, length=fill_second_pi2_inner),
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
    """
    start in ms=-1, pi/2 on N, (CORPSE) pi on e, wait T, (CORPSE) pi on e,
        pi/2 on N (same phase as the first)

    -> sweep T, find good timing such that N has undergone n*2pi phase
       evolution while in ms=0.
    """
    mprefix = 'BSM_NUncondRotCalib'

    def generate_sequence(self, upload=True):
        self._pulse_defs()

        # waiting element that takes 1 us
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(self.T, length=1e-6))

        # filling for the pi element, symmetric
        min_fill_pi = 500e-9

        elements = []
        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix,
            self.name))

        elements.append(self.mbi_elt)
        elements.append(wait_1us)
        elements.append(self.sync_elt)

        for i,d in enumerate(self.params['delays']):
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'N_first_pi2-{}'.format(i))

            # shelving pulse to ms=-1, then the first pi/2 pulse
            N_first_pi2_elt = element.Element('N_first_pi2_elt',
                pulsar = qt.pulsar)
            N_first_pi2_elt.append(self.T)
            N_first_pi2_elt.append(self.shelving_pulse)
            N_first_pi2_elt.append(
                pulse.cp(self.T, length=200e-9))
            N_first_pi2_elt.append(self.N_pi2)

            elements.append(N_first_pi2_elt)
            seq.append(name = 'N_first_pi2-{}'.format(i),
                wfname = N_first_pi2_elt.name, 
                trigger_wait = True)

            pi1_ref_phase = 0 # no prior operations on the electron here

            pi1_elt = element.Element('pi1-{}'.format(i), pulsar=qt.pulsar)
            pi1_elt.append(pulse.cp(self.TIQ, length = min_fill_pi))
            pi1_elt.append(pulse.cp(self.CORPSE_pi,
                    phase = pi1_ref_phase + \
                        self.params['CORPSE_pi_phase_shift']))
            pi1_elt.append(pulse.cp(self.TIQ, length = min_fill_pi))

            elements.append(pi1_elt)
            seq.append(name = 'pi1-{}'.format(i), 
                wfname = pi1_elt.name)

            delay_reps = int((d - 2*min_fill_pi) / 1e-6)
            fill_pi2 = min_fill_pi + (d - 2*min_fill_pi) % 1e-6

            pi2_ref_phase = 0. # we only need inversion here, so phase is not relevant

            seq.append('delay-{}'.format(i),
                wfname = wait_1us.name,
                repetitions = delay_reps)

            pi2_elt = element.Element('pi2-{}'.format(i), pulsar=qt.pulsar)
            pi2_elt.append(pulse.cp(self.TIQ, length = fill_pi2))
            pi2_elt.append(pulse.cp(self.CORPSE_pi,
                    phase = pi2_ref_phase + \
                        self.params['CORPSE_pi_phase_shift']))
            pi2_elt.append(pulse.cp(self.TIQ, length = min_fill_pi))

            elements.append(pi2_elt)
            seq.append(name = 'pi2-{}'.format(i),
                wfname = pi2_elt.name)

            N_ref_phase = ((self.N_pi2.frequency * (
                self.N_pi2.length + pi1_elt.length() + \
                    delay_reps * 1e-6 + pi2_elt.length())) % 1) * 360

            N_second_pi2_elt = element.Element('N_second_pi2_elt-{}'.format(i),
                pulsar = qt.pulsar)
            N_second_pi2_elt.append(
                pulse.cp(self.N_pi2, phase = N_ref_phase))
            N_second_pi2_elt.append(
                pulse.cp(self.T, length = 500e-9))
            N_second_pi2_elt.append(self.pi2pi_m1)

            elements.append(N_second_pi2_elt)
            seq.append(name = 'N_second_pi2-{}'.format(i),
                wfname = N_second_pi2_elt.name)

            seq.append(name = 'sync-{}'.format(i), 
                wfname = self.sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(*elements)
        
        qt.pulsar.program_sequence(seq)

# class NitrogenUnconditonalRotationCalib

class NitrogenURotVsTiming(BSM.ElectronReadoutMsmt):
    """
    start in (-1,-1). Do first a pi/2 on the electron, then do the
    unconditional preparation: rotation on N, CORPSE, repeat rotation on N.
    We then do a pi/2 pulse on the electron again and read out the electron.
    For wrong timing, we should get an entangled state and a RO result of < 1,
    (or > 0, depending on pi/2 direction) whereas for right timing the result
    should be extremal. 
    """
    mprefix = 'BSM_NURot'

    def generate_sequence(self, upload=True):
        self._pulse_defs()

        # all elements (for upload)
        elements = []

        # our rotating frame driving frequency
        e_ref_frq = self.pi2_4MHz.frequency
        N_ref_frq = self.N_pi2.frequency

        # filling times to make sure delays are what we calculate phases with
        fill_pi2_inner = 100e-9
        fill_pi = 500e-9

        # waiting element that takes 1 us
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(self.T, length=1e-6))

        ### first create all the elements we need

        # the nitrogen rotation (easy)
        N_rot = element.Element('N_rot', pulsar = qt.pulsar)
        N_rot.append(self.N_pi2)

        # there's only one first pi2 element on the electron (fixed phase)
        e_pi2_1 = element.Element('e_pi2_1', pulsar = qt.pulsar)
        e_pi2_1.append(pulse.cp(self.TIQ, length=1e-6))
        e_pi2_1.append(pulse.cp(self.pi2_4MHz,
            lock_phase_to_element_time = False))
        
        # take into account the granularity
        # weird numbers to avoid rounding issues
        fill_pi2_inner = fill_pi2_inner + missing_grains(
            fill_pi2_inner + 1e-6 + \
            self.pi2_4MHz.effective_length()) * 1e-9

        e_pi2_1.append(pulse.cp(self.TIQ, length=fill_pi2_inner))

        # we sweep the interpulse delay, so we need a different phase for all
        # the CORPSE and pi2-2 elements
        e_CORPSE_elts = []
        e_pi2_2_elts = []
        for i in range(self.params['pts']):

            # CORPSE phase is given by the reference phase from the first
            # pi/2 pulse plus the calibrated phase offset

            e_CORPSE_phase = phaseref(e_ref_frq,
                self.pi2_4MHz.effective_length() + \
                    self.params['e_delays'][i]) + \
                self.params['CORPSE_pi_phase_shifts'][i]

            # phase of the second pi/2 pulse is simply 
            e_pi2_2_phase = phaseref(e_ref_frq,
                self.pi2_4MHz.effective_length() + \
                    2 * self.params['e_delays'][i] + \
                    self.CORPSE_pi.effective_length())

            e_CORPSE = element.Element('e_CORPSE-{}'.format(i),
                pulsar=qt.pulsar)
            
            # preprend the waiting time for the total delay after the N pulse
            # to the pi pulse
            fill_pi_before = self.params['e_delays'][i]-fill_pi2_inner-N_rot.length()
            e_CORPSE.append(pulse.cp(self.TIQ, 
                length = fill_pi_before))            
            e_CORPSE.append(pulse.cp(self.CORPSE_pi,
                phase = e_CORPSE_phase))            

            # append the right waiting time such that the second N rotation
            # pulse is in phase again.
            _t = N_rot.length() + fill_pi_before + \
                self.CORPSE_pi.effective_length()
            _n = int(N_ref_frq * _t  + 1)
            fill_pi_after = (_n - N_ref_frq * _t)/ N_ref_frq
            fill_pi_after += missing_grains(fill_pi_after + fill_pi_before + \
                self.CORPSE_pi.effective_length()) * 1e-9
            e_CORPSE.append(pulse.cp(self.TIQ, length=fill_pi_after))

            e_pi2_2 = element.Element('e_pi2_2-{}'.format(i),
                pulsar=qt.pulsar)
            
            # fill time before the second pi2 pulse
            fill_before_second_pi2 = self.params['e_delays'][i] - \
                N_rot.length() - fill_pi_after

            e_pi2_2.append(pulse.cp(self.TIQ, 
                length=fill_before_second_pi2))
            e_pi2_2.append(pulse.cp(self.pi2_4MHz,
                lock_phase_to_element_time = False,
                phase = e_pi2_2_phase))
            e_pi2_2.append(pulse.cp(self.TIQ, length=1e-6))

            e_CORPSE_elts.append(e_CORPSE)
            e_pi2_2_elts.append(e_pi2_2)

        # program AWG
        if upload:
            elements.append(self.mbi_elt)
            elements.append(e_pi2_1)
            elements.append(wait_1us)
            elements.append(N_rot)
            elements.append(self.sync_elt)
            
            elements.extend(e_CORPSE_elts)
            elements.extend(e_pi2_2_elts)

            qt.pulsar.upload(*elements)
        
        # make the sequence
        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix,
            self.name))

        for i in range(self.params['pts']):
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'e_pi2_1-{}'.format(i))
            seq.append(name = 'e_pi2_1-{}'.format(i),
                wfname = e_pi2_1.name,
                trigger_wait = True)
            seq.append(name = 'N_rot1-{}'.format(i),
                wfname = N_rot.name)
            seq.append(name = 'e_CORPSE_pi-{}'.format(i),
                wfname = e_CORPSE_elts[i].name)
            seq.append(name = 'N_rot2-{}'.format(i),
                wfname = N_rot.name)
            seq.append(name = 'e_pi2_2-{}'.format(i),
                wfname = e_pi2_2_elts[i].name)
            seq.append(name = 'sync-{}'.format(i), 
                wfname = self.sync_elt.name)

        qt.pulsar.program_sequence(seq)

# class NitrogenURotVsTiming

#### scripts
def echo_delay_sweep(name):
    m = Echo('_DelaySweep_{}'.format(name))
    BSM.prepare(m)

    reps = np.arange(30,72,2)
    # reps = np.arange(1, 12, 2)

    pts = len(reps)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['delay_repetitions'] = reps
    m.params['second_pi2_phases'] = zeros(pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'Interpulse delay (us)'
    m.params['sweep_pts'] = m.params['delay_repetitions']
    
    BSM.finish(m, debug=False)

def echo_phase_sweep(name):
    m = Echo('_PhaseSweep_{}'.format(name))
    BSM.prepare(m)

    phases = np.linspace(0,360,25)
    # reps = np.arange(1, 12, 2)

    pts = len(phases)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['delay_repetitions'] = np.ones(pts) * 51
    m.params['second_pi2_phases'] = phases

    # for the autoanalysis
    m.params['sweep_name'] = 'Phase of second pi-pulse (deg)'
    m.params['sweep_pts'] = m.params['second_pi2_phases']
    
    BSM.finish(m, debug=False)

def pi_position_sweep(name):
    m = EchoSweepPiPosition(name)
    BSM.prepare(m)

    m.params['2tau'] = 3000e-9
    shifts = np.linspace(-500e-9, 500e-9, 21)

    pts = len(shifts)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 2500

    # m.params['CORPSE_pi_phase_shift'] = 65.2
    m.params['pi_position_shifts'] = shifts

    # for the autoanalysis
    m.params['sweep_name'] = 'position shift of the pi-pulse (ns)'
    m.params['sweep_pts'] = shifts * 1e9
    
    BSM.finish(m, debug=False, upload=True)

def run_CORPSE_echo_phase_sweep(name):
    m = CORPSEEchoPhaseSweep(name)
    BSM.prepare(m)

    phases = np.linspace(0,360,25)

    pts = len(phases)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['delay'] = 51e-6
    m.params['phases'] = phases

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params['sweep_pts'] = phases
    
    BSM.finish(m, debug=False)

def run_UNROT_calib(name):
    m = NitrogenUnconditonalRotationCalib(name)
    BSM.prepare(m)

    delays = 51.1e-6 + np.linspace(-0.5e-6, 0.5e-6, 17)

    pts = len(delays)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    # DEBUG
    # m.params['CORPSE_pi_amp'] = 0.

    m.params['CORPSE_pi_phase_shift'] = 65.2
    m.params['delays'] = delays

    # for the autoanalysis
    m.params['sweep_name'] = 'Interpulse delay (us)'
    m.params['sweep_pts'] = delays * 1e6
    
    BSM.finish(m, debug=False)

def run_UNROT_vs_timing(name):
    m = NitrogenURotVsTiming(name)
    BSM.prepare(m)

    delays = 50.9e-6 + np.linspace(-0.5e-6, 0.5e-6, 26)

    # DEBUG
    # m.params['N_pi2_amp'] = 0

    pts = len(delays)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['CORPSE_pi_phase_shift'] = 65.2
    m.params['CORPSE_pi_phase_shifts'] = \
        np.ones(pts) * m.params['CORPSE_pi_phase_shift']

    m.params['e_delays'] = delays

    # for the autoanalysis
    m.params['sweep_name'] = 'Interpulse delay (us)'
    m.params['sweep_pts'] = delays * 1e6
    
    BSM.finish(m, debug=True)

if __name__ == '__main__':
    echo_delay_sweep('sil2_zeroth_revival')
    # echo_phase_sweep('sil2_first_revival')
    # pi_position_sweep('sil2_short_delay_CORPSE_pi')
    
    # run_CORPSE_echo_phase_sweep('sil2_first_revival')
    
    # BEFORE USING FIX TIMINGS run_N_uncond_rot_calib('sil2_test')
    
    # BEFORE USING FIX TIMINGS run_NUrot_vs_timing('sil2_try1')
