import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


def prepare(m):
    m.params.from_dict(qt.cfgman.get('samples/sil2'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO-integrated'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+MBI'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO+MBI'))

    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/pulses'))

    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/BSM'))

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']

    m.params['MW_pulse_mod_risetime'] = 2e-9

def finish(m, sequence=True, upload=True, debug=False):
    m.autoconfig()

    if sequence:
        m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()

def phaseref(frequency, time, offset=0):
    return ((frequency*time + offset/360.) % 1) * 360.

def missing_grains(time, clock=1e9, granularity=4):
    if int(time*clock + 0.5) < 960:
        return 960 - int(time*clock + 0.5)

    grains = int(time*clock + 0.5)
    return granularity - grains%granularity

### msmt class
class BSMMsmt(pulsar_msmt.MBI):
    mprefix = 'BSM'

    def _pulse_defs(self):
        ### electron manipulation pulses
        
        # a waiting pulse on the MW pulsemod channel
        self.T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        self.TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        # some not yet specified pulse on the electron
        self.e_pulse = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        # slow pi-pulse for MBI
        self.slow_pi = pulselib.MW_IQmod_pulse('slow pi',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['selective_pi_mod_frq'],
            amplitude = self.params['selective_pi_amp'],
            length = self.params['selective_pi_duration'])

        # reasonably fast pi and pi/2 pulses
        self.pi_4MHz = pulselib.MW_IQmod_pulse('4MHz pi',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['4MHz_pi_mod_frq'],
            amplitude = self.params['4MHz_pi_amp'],
            length = self.params['4MHz_pi_duration'])

        self.pi2_4MHz = pulselib.MW_IQmod_pulse('4MHz pi2',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['4MHz_pi2_mod_frq'],
            amplitude = self.params['4MHz_pi2_amp'],
            length = self.params['4MHz_pi2_duration'])

        # shelving pi-pulse to bring electron to ms=-1 after mbi
        self.shelving_pulse = pulselib.MW_IQmod_pulse('MBI shelving pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
            amplitude = self.params['AWG_shelving_pulse_amp'],
            length = self.params['AWG_shelving_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        # CORPSE pi pulse
        self.CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_pi_mod_frq'],
            amplitude = self.params['CORPSE_pi_amp'],
            length_60 = self.params['CORPSE_pi_60_duration'],
            length_m300 = self.params['CORPSE_pi_m300_duration'],
            length_420 = self.params['CORPSE_pi_420_duration'])

        # CNOT operations on the electron
        self.pi2pi_m1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pi2pi_mIm1_mod_frq'],
            amplitude = self.params['pi2pi_mIm1_amp'],
            length = self.params['pi2pi_mIm1_duration'])

        self.pi2pi_0 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=0',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pi2pi_mI0_mod_frq'],
            amplitude = self.params['pi2pi_mI0_amp'],
            length = self.params['pi2pi_mI0_duration'])

        ### nuclear spin manipulation pulses
        self.TN = pulse.SquarePulse(channel='RF',
            length = 100e-9, amplitude = 0)

        self.N_pulse = pulselib.RF_erf_envelope(
            channel = 'RF',
            frequency = self.params['N_0-1_splitting_ms-1'])

        self.N_pi = pulselib.RF_erf_envelope(
            channel = 'RF',
            frequency = self.params['N_0-1_splitting_ms-1'],
            length = self.params['N_pi_duration'],
            amplitude = self.params['N_pi_amp'])

        self.N_pi2 = pulselib.RF_erf_envelope(
            channel = 'RF',
            frequency = self.params['N_0-1_splitting_ms-1'],
            length = self.params['N_pi2_duration'],
            amplitude = self.params['N_pi2_amp'])

        ### synchronizing, etc
        self.adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)

        ### useful elements
        self.mbi_elt = self._MBI_element()

        self.sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        self.sync_elt.append(self.adwin_sync)

        self.N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        self.N_RO_CNOT_elt.append(pulse.cp(self.T,
            length=100e-9))
        self.N_RO_CNOT_elt.append(self.pi2pi_m1)

        self.wait_1us_elt = element.Element('1us_delay', pulsar=qt.pulsar)
        self.wait_1us_elt.append(pulse.cp(self.T, length=1e-6))


    def generate_sequence(self, upload=True):
        pass

    def _flatten_sweep_element_list(self, sweep_elements):
        flattened_sweep_elements = []

        for e in sweep_elements:
            if type(e) != list:
                if e not in flattened_sweep_elements:
                    flattened_sweep_elements.append(e)

            else:
                for sub_e in e:
                    if sub_e not in flattened_sweep_elements:
                        flattened_sweep_elements.append(sub_e)

        return flattened_sweep_elements

    def _add_MBI_and_sweep_elements_to_sequence(self, sweep_elements,
            *N_RO_elements, **kw):

        append_sync = kw.pop('append_sync', True)

        # the sequence
        seq = pulsar.Sequence('{}_{} sequence'.format(self.mprefix, 
            self.name))
        for i,e in enumerate(sweep_elements):

            # the element we jump to after MBI depends on the type of
            # list we supply as sweep elements
            if type(e) == list:
                jmp = 'sweep_element-{}-{}'.format(i, 0)
            else:
                jmp = 'sweep_element-{}'.format(i)

            # for each sweep point we want first an MBI step
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = jmp)

            # append either the only element or the specified sequence of
            # elements for this sweep point
            if type(e) != list:
                seq.append(name = 'sweep_element-{}'.format(i),
                    wfname = e.name,
                    trigger_wait = True)

            else:
                for j,sub_e in enumerate(e):
                    seq.append(name = 'sweep_element-{}-{}'.format(i, j),
                        wfname = sub_e.name,
                        trigger_wait = (j==0))

            if append_sync:
                seq.append(name = 'sync-{}'.format(i), 
                    wfname = self.sync_elt.name)

            for j,e in enumerate(N_RO_elements):
                seq.append(name = 'N_RO-{}-{}'.format(i,j),
                    wfname = e.name,
                    trigger_wait = (j==0 and append_sync))

        return seq

### Measurements in which we only read out the electron spin

class ElectronReadoutMsmt(BSMMsmt):
    mprefix = 'BSM_EReadout'

    def autoconfig(self):
        BSMMsmt.autoconfig(self)

        self.params['A_SP_durations'] = [self.params['repump_after_MBI_duration']]
        self.params['A_SP_amplitudes'] = [self.params['repump_after_MBI_amplitude']]
        self.params['E_RO_durations'] = [self.params['SSRO_duration']]
        self.params['E_RO_amplitudes'] = [self.params['Ex_RO_amplitude']]
        self.params['send_AWG_start'] = [1]
        self.params['sequence_wait_time'] = [0]

    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self._pulse_defs()
        self.sweep_elements = self.get_sweep_elements()
        
        # create the sequence
        seq = self._add_MBI_and_sweep_elements_to_sequence(
            self.sweep_elements)

        # make the list of elements required for uploading
        flattened_sweep_elements = self._flatten_sweep_element_list(
            self.sweep_elements)

        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, self.sync_elt, 
                *flattened_sweep_elements)
        
        qt.pulsar.program_sequence(seq)

class ElectronRabiMsmt(ElectronReadoutMsmt):
    mprefix = 'BSM_ERabi'

    def get_sweep_elements(self):        
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-{}'.format(i), pulsar=qt.pulsar)
            e.append(self.T)            
            for j in range(self.params['MW_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(self.e_pulse,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_amps'][i],
                        length = self.params['MW_pulse_durations'][i]))
                e.append(
                    pulse.cp(self.T, length=self.params['MW_pulse_delays'][i]))
            elts.append(e)

        return elts

class ElectronMultiPulses(ElectronReadoutMsmt):
    mprefix = 'BSM_EMultiPulse'

    def get_sweep_elements(self):
        wait_elt = element.Element('pulse_delay', pulsar=qt.pulsar)
        wait_elt.append(pulse.cp(self.T, length=1e-6))

        pulse_elts = []
        sweep_elts = []
        
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-{}'.format(i), pulsar=qt.pulsar)
            e.append(self.T)
            e.append(
                pulse.cp(self.e_pulse,
                    frequency = self.params['MW_pulse_mod_frqs'][i],
                    amplitude = self.params['MW_pulse_amps'][i],
                    length = self.params['MW_pulse_durations'][i]))
            pulse_elts.append(e)

        for i in range(self.params['pts']):
            if self.params['MW_pulse_multiplicities'][i] == 0:
                sweep_elts.append(pulse_elts[i])

            else:
                subelts = []
                for j in range(self.params['MW_pulse_multiplicities'][i]):
                    subelts.append(pulse_elts[i])
                    subelts.append(wait_elt)
                sweep_elts.append(subelts)

        return sweep_elts

### reading out the nuclear spin only

class NReadoutMsmt(ElectronReadoutMsmt):
    mprefix = 'BSM_NReadout'

    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self._pulse_defs()
        self.sweep_elements = self.get_sweep_elements()
        
        N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        N_RO_CNOT_elt.append(pulse.cp(self.T, length=500e-9))
        N_RO_CNOT_elt.append(self.pi2pi_m1)

        # create the sequence
        seq = self._add_MBI_and_sweep_elements_to_sequence(
            self.sweep_elements, N_RO_CNOT_elt, self.sync_elt,
            append_sync = False)

        # make the list of elements required for uploading
        flattened_sweep_elements = self._flatten_sweep_element_list(
            self.sweep_elements)

        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, self.sync_elt, N_RO_CNOT_elt,
                *flattened_sweep_elements)
        
        qt.pulsar.program_sequence(seq)

# class NReadoutMsmt

class NRabiMsmt(NReadoutMsmt):
    mprefix = 'BSM_NRabi'

    def get_sweep_elements(self):        
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('NRabi_pt-{}'.format(i), pulsar=qt.pulsar)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(self.T)
            for j in range(self.params['RF_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(self.N_pulse,
                        frequency = self.params['RF_pulse_frqs'][i],
                        amplitude = self.params['RF_pulse_amps'][i],
                        length = self.params['RF_pulse_durations'][i]))
                e.append(
                    pulse.cp(self.TN, length=self.params['RF_pulse_delays'][i]))
            elts.append(e)

        return elts

# class NRabiMsmt

class NTomo(NReadoutMsmt):
    mprefix = 'BSM_NTomo'

    def autoconfig(self):
        NReadoutMsmt.autoconfig(self)

        self.params['pts'] = 3
        self.params['tomo_bases'] = ['Z', 'X', 'Y']
        self.params['tomo_pulse_amps'] = \
            [0, self.params['N_pi2_amp'], self.params['N_pi2_amp']]

        # Convention phi=0 makes |x>, i.e., rotates around +y
        self.params['tomo_pulse_phases'] = [0, 180., 90.]

        # for the autoanalysis
        self.params['sweep_name'] = 'Readout basis (Z, X, Y)'
        self.params['sweep_pts'] = range(3)


    # TODO: global time should be implemented in here
    def get_sweep_elements(self):

        z_element = element.Element('Z Tomo pulse', pulsar=qt.pulsar,
            global_time = True, 
            time_offset = self.params['tomo_time_offset'])
        z_element.append(pulse.cp(self.TN, length=1e-6))

        x_element = element.Element('X Tomo pulse', pulsar=qt.pulsar,
            global_time = True, 
            time_offset = self.params['tomo_time_offset'])
        xn = x_element.append(pulse.cp(self.N_pi2, 
            phase = self.params['tomo_pulse_phases'][1]))

        y_element = element.Element('Y Tomo pulse', pulsar=qt.pulsar,
            global_time = True,
            time_offset = self.params['tomo_time_offset'])
        yn = y_element.append(pulse.cp(self.N_pi2, 
            phase = self.params['tomo_pulse_phases'][2]))

        sweep_elements = []
        for n, tomo_elt in zip(self.params['tomo_bases'],
            [z_element, x_element, y_element]):

            if type(self.element) == list:
                elts = [e for e in self.element]
                elts.append(tomo_elt)
                sweep_elements.append(elts)
            else:
                elts = [self.element, tomo_elt]
                sweep_elements.append(elts)

        return sweep_elements

# class NTomo

### reading out first the electron then the nuclear spin

class ENReadoutMsmt(BSMMsmt):
    mprefix = 'BSM_ENReadout'

    def autoconfig(self):
        self.params['nr_of_ROsequences'] = 2

        BSMMsmt.autoconfig(self)
        
        self.params['A_SP_durations'] = [
            self.params['repump_after_MBI_duration'],
            self.params['repump_after_E_RO_duration'] ]
        self.params['A_SP_amplitudes'] = [
            self.params['repump_after_MBI_amplitude'],
            self.params['repump_after_E_RO_amplitude'] ]
        self.params['E_RO_durations'] = [
            self.params['SSRO_duration'],
            self.params['SSRO_duration'] ]
        self.params['E_RO_amplitudes'] = [
            self.params['Ex_RO_amplitude'],
            self.params['Ex_RO_amplitude'] ]
        self.params['send_AWG_start'] = [1, 1]
        self.params['sequence_wait_time'] = [0, 0]

    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self._pulse_defs()
        self.sweep_elements = self.get_sweep_elements()

        # CNOT element for nuclear spin readout
        N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        N_RO_CNOT_elt.append(self.pi2pi_m1)

        # create the sequence
        seq = self._add_MBI_and_sweep_elements_to_sequence(
            self.sweep_elements, N_RO_CNOT_elt, self.sync_elt)

        # make the list of elements required for uploading
        flattened_sweep_elements = self._flatten_sweep_element_list(
            self.sweep_elements)

        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, self.sync_elt, 
                N_RO_CNOT_elt, *flattened_sweep_elements)
        
        qt.pulsar.program_sequence(seq)

# class ENReadoutMsmt

# Full BSM
class TheRealBSM(ENReadoutMsmt):
    mprefix = "TheRealBSM"
    
    ### functions for particular elements / msmt parts

    def UNROT_element(self, name,
        N_pulse, evolution_time, time_offset, **kw):
        """
        creates an unconditional operation:
        start at some zero-time, add the operation, and fill up
        with waiting time according to the specified
        'evolution_time' (measure to/from the center of the pi pulse).
        Then do a CORPSE pi pulse, and repeat the operation. fill up time
        after again such that the to evolution times are the same.
        
        for correct rotating frames we need a time offset. 
        electron pulse phase will be computed accordingly.
        For the N phase to match, we'll insert waiting time.
        """

        # to make sure that the zero-time of the element
        # is zero-time on the IQ channels
        start_buffer = kw.pop('start_buffer', 200e-9)

        # verbosity: if verbose, print info about all phases and lengths
        verbose = kw.pop('verbose', False)

        CORPSE_pi_phase_shift = kw.pop('CORPSE_pi_phase_shift',
            self.params['CORPSE_pi_phase_shift'])

        # optionally add/omit time at the end, which might facilitate
        # timing calculations for the next element. for the start this
        # is not required, on one side we just use the evolution time.
        end_offset_time = kw.pop('end_offset_time', 0)

        # the shiny new element
        elt = element.Element(name, pulsar=qt.pulsar,
            global_time = True, time_offset = time_offset)
        
        delay1_name = elt.append(pulse.cp(self.TIQ, 
            length = evolution_time))
        
        if N_pulse != None:
            
            # support for lists of pulses -- we need this for the H gate
            if type(N_pulse) != list:
                
                # first N operation, with adapted phase
                # the resulting time of the pulse within the element
                
                # eff_t_op1 = start_buffer - elt.channel_delay('RF') + \
                #    elt.channel_delay('MW_Imod')
                
                # op1_phase = (N_ref_phase + N_pulse.phase + \
                #     phaseref(N_pulse.frequency, eff_t_op1) )        
                
                op1_name = elt.add(N_pulse, start=start_buffer)

                # if verbose:
                #     print 'Phase of the first NROT:', op1_phase

            else:
                for i,op in enumerate(N_pulse):
                    if i == 0:
                        # eff_t_op = start_buffer - elt.channel_delay('RF') + \
                        #     elt.channel_delay('MW_Imod')
                        start = start_buffer
                    else:
                        # eff_t_op += N_pulse[i-1].length
                        start += N_pulse[i-1].length

                    # op_phase = (N_ref_phase + op.phase + \
                    #     phaseref(op.frequency, eff_t_op))
                    n = elt.add(op, start = start)

                    if i == 0:
                        # first_op_phase = op_phase
                        first_op_name = n
        
        # the CORPSE pi-pulse
        delta_t_CORPSE = - self.CORPSE_pi.effective_length()/2. + \
            self.params['CORPSE_pi_center_shift']
        
        # t_CORPSE = evolution_time + delta_t_CORPSE
        # CORPSE_phase = e_ref_phase + phaseref(
        #     self.params['e_ref_frq'], t_CORPSE) + \
        #     CORPSE_pi_phase_shift

        # want to have the CORPSE phase as a shift with respect to the current
        # rotating frame phase.
        CORPSE_phase = phaseref(self.params['e_ref_frq'],
            elt.pulse_global_end_time(delay1_name, 'MW_Imod') + delta_t_CORPSE) \
            + CORPSE_pi_phase_shift

        # if verbose:
        #     print 'Start time of the CORPSE:', t_CORPSE
        #     print 'Phase of the CORPSE:', CORPSE_phase

        pi_name = elt.add(pulse.cp(self.CORPSE_pi,
            phaselock = False,
            phase = CORPSE_phase),
            start = delta_t_CORPSE,
            refpulse = delay1_name)

        # second part of the evolution starts at the measured center of the
        # pi pulse. (note that delta_t_CORPSE is negative)
        delta_t_delay2 = self.CORPSE_pi.effective_length() + delta_t_CORPSE
        elt.add(pulse.cp(self.TIQ, 
            length = evolution_time + end_offset_time),
            start = -delta_t_delay2,
            refpulse = pi_name)

        if N_pulse != None:
            # second Nitrogen operation; start at evolution time
            # after the start of the first.
            
            if type(N_pulse) != list:
                
                t_op2 = evolution_time + self.CORPSE_pi.effective_length()/2.
                
                # op2_phase = op1_phase + phaseref(N_pulse.frequency, t_op2)

                elt.add(N_pulse,
                    start = t_op2,
                    refpulse = op1_name,
                    refpoint = 'start')

                # if verbose:
                #     print 'Phase of the second NROT:', op2_phase

            else:
                for i,op in enumerate(N_pulse):
                    if i == 0:
                        t_op = evolution_time + \
                            self.CORPSE_pi.effective_length()/2.
                    else:
                        t_op += N_pulse[i-1].length

                    # op_phase = first_op_phase + \
                    #     phaseref(op.frequency, t_op)
                    
                    elt.add(op,
                        start = t_op,
                        refpulse = first_op_name,
                        refpoint = 'start')
        return elt

    def BS_element(self, name, bs, **kw):
        ### some options
        CNOT_phase = kw.pop('CNOT_phase', 0)

        ### make the element
        BS_elt = element.Element('BS-{}'.format(name), 
            pulsar = qt.pulsar,
            global_time = True)
        BS_elt.append(self.T)
        BS_elt.append(self.shelving_pulse)
        BS_elt.append(pulse.cp(self.TIQ, length = 200e-9))

        if bs in ['phi+', 'psi+']:
            phase = 0
        
        elif bs in ['phi-', 'psi-']:
            phase = 180

        N_rot_name = BS_elt.append(pulse.cp(self.N_pi2,
            phase = phase))
        BS_elt.append(self.TIQ)

        if bs in ['phi+', 'phi-']:
            CNOT = pulse.cp(self.pi2pi_0,
                phase = CNOT_phase)
        
        elif bs in ['psi+', 'psi-']:
            CNOT = pulse.cp(self.pi2pi_m1,
                phase = CNOT_phase)

        CNOT_name = BS_elt.append(CNOT)

        # N_phase_ref = phaseref(self.N_pi2.frequency, 
        #     BS_elt.length() - BS_elt.effective_pulse_start_time(N_rot_name,
        #         'RF'))

        # e_phase_ref = phaseref(self.pi2pi_m1.frequency,
        #     BS_elt.length() - BS_elt.effective_pulse_start_time(CNOT_name,
        #         'MW_Imod'))

        return BS_elt

    def BSM_elements(self, name, time_offset, 
        start_buffer_time=240e-9, **kw):
        """
        Attention: Make sure that the CNOT element time adds up to a length
        that is a multiple of the granularity!
        """

        evo_offset = kw.pop('evo_offset', 1000e-9)
        CNOT_offset = kw.pop('CNOT_offset', 0)
        CNOT_phase_shift = kw.pop('CNOT_phase_shift', 0)

        evo_time = self.params['H_evolution_time']
        eff_evo_time = evo_time - evo_offset

        # we make the evolution time a bit shorter (default 1000 ns), 
        # then make an extra
        # element of length start_buffer_time plus this offset.
        # in this element we put the CNOT pulse such that it's centered
        # at the start of the effective evolution time (end - 1000 ns).
        CNOT_elt = element.Element('{}_BSM-CNOT'.format(name), 
            pulsar = qt.pulsar,
            global_time = True,
            time_offset = time_offset)

        t_CNOT = start_buffer_time - self.pi2pi_m1.effective_length()/2. + \
            CNOT_offset
        
        # phi_CNOT = phaseref(self.pi2pi_m1.frequency,
        #     t_CNOT) + e_ref_phase + CNOT_phase_shift

        CNOT_elt.append(pulse.cp(self.TIQ, 
            length = t_CNOT))
        CNOT_elt.append(self.pi2pi_m1)
        CNOT_elt.append(pulse.cp(self.TIQ,
            length = evo_offset + start_buffer_time - \
                self.pi2pi_m1.effective_length() - t_CNOT))

        # UNROT_e_ref_phase = e_ref_phase + phaseref(self.params['e_ref_frq'], 
        #     CNOT_elt.length())
        # UNROT_N_ref_phase = N_ref_phase + phaseref(self.params['N_ref_frq'],
        #     CNOT_elt.length())
        
        H_pulses = [ pulse.cp(self.N_pi2, phase=0),
            pulse.cp(self.N_pi, phase=90.) ]

        UNROT_elt = self.UNROT_element('{}_BSM-UNROT-H'.format(name),
            H_pulses, eff_evo_time, time_offset+CNOT_elt.length(), **kw)

        return CNOT_elt, UNROT_elt

    ### test/calibration and debug functions

    def test_UNROT_element_overview(self):
        """
        make a simple unconditional rotation element and print the info,
        just to see if the timings are correct.
        """
        self._pulse_defs()
        
        N_pulse = [ self.N_pi2, self.N_pi ]
        evolution_time = 140e-6
        time_offset = 0

        elt = self.UNROT_element(
            'test_UNROT_timings', N_pulse, evolution_time,
            time_offset, verbose=True)

        elt.print_overview()

    def test_BS_ZZ_correlations(self):
        self._pulse_defs()
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))

        for bs in self.params['bellstates']:
            bs_elt = self.BS_element(bs, bs)
            self.flattened_elements.append(bs_elt)
            sweep_elements.append(bs_elt)

        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.sync_elt)

    def test_BSM(self):
        self._pulse_defs()
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))
        
        for bs in self.params['bellstates']:
            bs_elt, N_phase, e_phase = self.BS_element(bs, bs)
            CNOT, UNROT_H = self.BSM_elements(bs, N_phase, e_phase)

            self.flattened_elements.append(bs_elt)
            self.flattened_elements.append(CNOT)
            self.flattened_elements.append(UNROT_H)
            sweep_elements.append([bs_elt, CNOT, UNROT_H])

        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.sync_elt)

    def test_BSM_vs_BSM_params(self):
        self._pulse_defs()
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))
        
        bs = self.params['bellstate']
        bs_elt, N_phase, e_phase = self.BS_element(bs, bs)
        self.flattened_elements.append(bs_elt)

        for i in range(self.params['pts']):

            CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
                N_phase, e_phase,
                CORPSE_pi_phase_shift = \
                    self.params['CORPSE_pi_phase_shifts'][i],
                CNOT_phase_shift = \
                    self.params['BSM_CNOT_phase_shifts'][i])

            self.flattened_elements.append(CNOT)
            self.flattened_elements.append(UNROT_H)
            sweep_elements.append([bs_elt, CNOT, UNROT_H])

        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.sync_elt)

    def test_BSM_and_BS_generation(self):
        self._pulse_defs()
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))
        
        bs = self.params['bellstate']
        for i in range(self.params['pts']):
            
            bs_elt = self.BS_element('{}-{}'.format(bs,i), bs,
                CNOT_phase = self.params['CNOT_phases'][i])

            CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
                time_offset = bs_elt.length(),
                start_buffer_time = self.params['BSM_start_buffer_times'][i])

            self.flattened_elements.append(bs_elt)
            self.flattened_elements.append(CNOT)
            self.flattened_elements.append(UNROT_H)
            sweep_elements.append([bs_elt, CNOT, UNROT_H])

        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.sync_elt)

    def test_BSM_CNOT(self):
        self._pulse_defs()
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))
        
        bs = self.params['bellstate']
        bs_elt, N_phase, e_phase = self.BS_element(bs, bs)
        self.flattened_elements.append(bs_elt)

        for i in range(self.params['pts']):
            CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
                N_phase, e_phase, 
                CNOT_offset = self.params['CNOT_offsets'][i])
            
            self.flattened_elements.append(CNOT)
            self.flattened_elements.append(UNROT_H)
            sweep_elements.append([bs_elt, CNOT, UNROT_H])

        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.sync_elt)

    def calibrate_CORPSE_pi_phase_shift(self):
        """
        Do a Hahn echo sequence with the CORPSE pi pulse, and sweep it's zero
        phase with respect the rotating frame at that time.
        """
        self._pulse_defs()
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))

        first_pi2_elt = element.Element('first pi2', pulsar=qt.pulsar,
            global_time = True)
        first_pi2_elt.append(pulse.cp(self.T, length=1e-6))
        first_pi2_name = first_pi2_elt.append(self.pi2_4MHz)
        first_pi2_elt.append(pulse.cp(self.TIQ, length=100e-9))

        self.flattened_elements.append(first_pi2_elt)

        # phase reference for the UNROT element
        # e_ref_phase = phaseref(self.pi2_4MHz.frequency,
        #     first_pi2_elt.length() - \
        #     first_pi2_elt.effective_pulse_start_time(first_pi2_name,'MW_Imod'))

        # calculate the evolution time from the interpulse delay
        etime = self.params['interpulse_delay'] - \
            self.CORPSE_pi.effective_length()/2.

        pi_elts = []
        for i in range(self.params['pts']):
            e = self.UNROT_element('pi-{}'.format(i),
                None, etime, first_pi2_elt.length(),
                CORPSE_pi_phase_shift = \
                    self.params['CORPSE_pi_phase_shifts'][i])
            
            self.flattened_elements.append(e)
            pi_elts.append(e)

        # the start time of the second pi2 depends on the time when the
        # pulse stops in the first pi2 element:
        t_pi2 = first_pi2_elt.length() - \
            first_pi2_elt.effective_pulse_end_time(first_pi2_name, 'MW_Imod')

        # the phase...
        # pi2_phase = phaseref(self.pi2_4MHz.frequency,
        #     first_pi2_elt.length() - \
        #         first_pi2_elt.effective_pulse_start_time(first_pi2_name,'MW_Imod') + \
        #         2*etime + t_pi2)

        # make the element
        second_pi2_elt = element.Element('second pi2', pulsar=qt.pulsar,
            global_time = True, 
            time_offset = e.length()+first_pi2_elt.length())        
        second_pi2_elt.append(pulse.cp(self.TIQ, length=t_pi2))
        second_pi2_elt.append(self.pi2_4MHz)

        self.flattened_elements.append(second_pi2_elt)
        self.flattened_elements.append(self.N_RO_CNOT_elt)

        for i in range(self.params['pts']):
            sweep_elements.append([first_pi2_elt, 
                pi_elts[i], second_pi2_elt])
        
        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.sync_elt)
    
    def calibrate_UNROT_X_timing(self, eigenstate='-1'):
        """
        Prepare e and N in an eigenstate, then do an UNROT X, followed by
        another X. if the e-eigenstate we started in is -1, then we
        do another CORPSE pi centered at the end of the second evolution 
        period to make sure we end in ms=-1 for readout.
        For the correct timing, the opposite state should be yielded
        for both eigenstates. We sweep the evolution time of the UNROT.

        I'm a bit lazy for now, make sure to only give evolution times such
        that 2 * evolution_time - 1e6 fits with the granularity.
        """
        self._pulse_defs()
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))

        prep_elt = element.Element('UNROT-prep', pulsar=qt.pulsar,
            global_time = True)
        prep_elt.append(self.T)
        
        if eigenstate == '-1':
            prep_elt.append(self.pi_4MHz)
        else:
            prep_elt.append(pulse.cp(self.pi_4MHz,
                amplitude = 0.))

        self.flattened_elements.append(self.mbi_elt)
        self.flattened_elements.append(prep_elt)

        for i,t in enumerate(self.params['evolution_times']):
            e = self.UNROT_element('UNROT-{}'.format(i),
                self.N_pi2, t, prep_elt.length(), 
                end_offset_time = 1e-6)

            self.flattened_elements.append(e)

            analysis_elt = element.Element('UNROT-analysis-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time = True,
                time_offset = prep_elt.length()+e.length())
            
            if eigenstate == '-1':
                t_CORPSE = 1e-6 - self.CORPSE_pi.effective_length()/2. + \
                    self.params['CORPSE_pi_center_shift']           
                
                # phi_CORPSE = 0 # only care about inversion here
                
                analysis_elt.append(pulse.cp(self.TIQ, 
                    length=t_CORPSE))
                analysis_elt.append(pulse.cp(self.CORPSE_pi,
                    phaselock = False))
                analysis_elt.append(pulse.cp(self.TIQ, 
                    length=200e-9))
            else:
                t_wait = 1.2e-6 + self.CORPSE_pi.effective_length()/2. + \
                    self.params['CORPSE_pi_center_shift']
                analysis_elt.append(pulse.cp(self.TIQ, length=t_wait))

            # t_total = 1.2e-6 + self.CORPSE_pi.effective_length()/2. + \
            #         self.params['CORPSE_pi_center_shift']

            # the phase of the analysis N rotation
            # delta_t_Nrot2 = t_total - analysis_elt.channel_delay('RF') + \
            #     analysis_elt.channel_delay('MW_Imod')
            # phi_Nrot2 = phaseref(self.N_pi2.frequency,
            #     e.length() + delta_t_Nrot2)
            
            analysis_elt.append(self.N_pi2)

            self.flattened_elements.append(analysis_elt)
            sweep_elements.append([prep_elt, e, analysis_elt])

        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.sync_elt)

    ### tools

    def generate_sequence(self, upload=True):
        self.flattened_elements.append(self.mbi_elt)
        self.flattened_elements.append(self.sync_elt)
        self.flattened_elements.append(self.N_RO_CNOT_elt)
        self.flattened_elements.append(self.wait_1us_elt)
        

        # program AWG
        if upload:
            qt.pulsar.upload(*self.flattened_elements)
        
        qt.pulsar.program_sequence(self.seq)


# class TheRealBSM

### scripts -- run BSM/BSM testing
def bsm_test_print_UNROT_element(name):
    m = TheRealBSM(name)
    prepare(m)

    # bogus msmt parameters, not actually used here
    pts = 3
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.test_UNROT_element_overview()

    finish(m, sequence=False, debug=True, upload=False)

def bsm_test_BS_ZZ_correlations():
    m = TheRealBSM('test_BS_ZZ_correlations')
    prepare(m)

    # bogus msmt parameters, not actually used here
    pts = 4
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['bellstates'] = ['phi+', 'phi-', 'psi+', 'psi-']
    m.test_BS_ZZ_correlations()
    
    m.params['sweep_name'] = 'Bell state'
    m.params['sweep_pts'] = np.arange(4)

    finish(m, debug=False, upload=True)

def bsm_calibrate_CORPSE_pi_phase_shift():
    m = TheRealBSM('CalibrateCORPSEPiPhase_154us')
    prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['CORPSE_pi_phase_shifts'] = np.linspace(0,180,pts)
    m.params['interpulse_delay'] = 154e-6
    m.calibrate_CORPSE_pi_phase_shift()

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_phase_shifts']

    finish(m, debug=False, upload=True)

def bsm_calibrate_UNROT_X_timing(name):
    m = TheRealBSM(name)
    prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['evolution_times'] = 140e-6 + np.linspace(-400e-9,400e-9,pts)
    m.calibrate_UNROT_X_timing(eigenstate='-1')

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (us)'
    m.params['sweep_pts'] = m.params['evolution_times'] * 1e6

    finish(m, debug=False, upload=True)

def bsm_test_BSM():
    m = TheRealBSM('TestBSM')
    prepare(m)

    pts = 4
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['bellstates'] = ['phi+', 'phi-', 'psi+', 'psi-']
    m.params['H_evolution_time'] = 144.825e-6

    m.params['sweep_name'] = 'Bell state'
    m.params['sweep_pts'] = np.arange(4)

    m.test_BSM()

    finish(m, debug=False, upload=True)

def bsm_test_BSM_vs_CORPSE_phase(name):
    m = TheRealBSM('TestBSM_vs_CORPSE_phase_'+name)
    prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['bellstate'] = 'psi+'
    m.params['H_evolution_time'] = 139.814e-6
    
    m.params['CORPSE_pi_phase_shifts'] = np.linspace(0,360,pts)
    m.params['BSM_CNOT_phase_shifts'] = np.zeros(pts)

    m.params['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_phase_shifts']

    m.test_BSM_vs_BSM_params()

    finish(m, debug=False, upload=True)

def bsm_test_BSM_vs_CNOT_phase(name):
    m = TheRealBSM('TestBSM_vs_CNOT_phase_'+name)
    prepare(m)

    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['bellstate'] = 'psi+'
    m.params['H_evolution_time'] = 139.792e-6
    
    m.params['CORPSE_pi_phase_shifts'] = np.ones(pts) * m.params['CORPSE_pi_phase_shift']
    m.params['BSM_CNOT_phase_shifts'] = np.array([0]) # np.linspace(0,360,pts)

    m.params['sweep_name'] = 'CNOT relative phase shift (deg)'
    m.params['sweep_pts'] = m.params['BSM_CNOT_phase_shifts']

    m.test_BSM_vs_BSM_params()

    finish(m, debug=True, upload=False)

def bsm_test_BSM_vs_BS_CNOT_phase(name):
    m = TheRealBSM('TestBSM_vs_BS_CNOT_phase_'+name)
    prepare(m)

    m.params['CNOT_phases'] = np.linspace(0,360,9)
    m.params['BSM_start_buffer_times'] = np.ones(9) * 240e-9

    pts = len(m.params['CNOT_phases'])
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['bellstate'] = 'psi+'
    m.params['H_evolution_time'] = 139.791e-6

    m.params['sweep_name'] = 'CNOT phase (deg)'
    m.params['sweep_pts'] = m.params['CNOT_phases']

    m.test_BSM_and_BS_generation()

    finish(m, debug=False, upload=True)

def bsm_test_BSM_and_BS_vs_delay(name):
    m = TheRealBSM('TestBSM+BS_vs_delay_'+name)
    prepare(m)

    m.params['CNOT_phases'] = np.zeros(11) # np.linspace(0,360,9)
    m.params['BSM_start_buffer_times'] = np.linspace(0, 480e-9, 11) + 240e-9

    pts = len(m.params['CNOT_phases'])
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['bellstate'] = 'psi+'
    m.params['H_evolution_time'] = 139.814e-6

    m.params['sweep_name'] = 'Post-BS generation delay'
    m.params['sweep_pts'] = m.params['BSM_start_buffer_times']

    m.test_BSM_and_BS_generation()

    finish(m, debug=False, upload=True)

def bsm_test_BSM_vs_CNOT_offset(name):
    m = TheRealBSM('TestBSM_vs_CNOT_offset_'+name)
    prepare(m)

    m.params['CNOT_offsets'] = np.linspace(0,100e-9,11)

    pts = len(m.params['CNOT_offsets'])
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['bellstate'] = 'psi+'
    m.params['H_evolution_time'] = 144.825e-6

    m.params['sweep_name'] = 'CNOT time offset (ns)'
    m.params['sweep_pts'] = m.params['CNOT_offsets'] * 1e9

    m.test_BSM_CNOT()

    finish(m, debug=False, upload=True)


if __name__ == '__main__':
    # bsm_test_print_UNROT_element('testing')
    # bsm_calibrate_CORPSE_pi_phase_shift()
    bsm_calibrate_UNROT_X_timing('test_H_timing_ms=-1_140us')
    # bsm_test_BS_ZZ_correlations()
    # bsm_test_BSM()
    # bsm_test_BSM_vs_CORPSE_phase('psi+')
    # bsm_test_BSM_vs_CNOT_phase('psi+')
    # bsm_test_BSM_vs_BS_CNOT_phase('psi+')
    # bsm_test_BSM_and_BS_vs_delay('psi+')
    # bsm_test_BSM_vs_CNOT_offset('psi+')



