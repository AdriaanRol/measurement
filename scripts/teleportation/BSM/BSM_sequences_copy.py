import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

from measurement.scripts.teleportation import parameters as tparams
reload(tparams)
from measurement.scripts.teleportation import sequence as tseq
reload(tseq)

SIL_NAME = 'hans-sil4'
LDE_DO_MW = True # this is needed always when using the LDE element in calibration

def prepare(m, yellow = False):
    m.pulsar_lt1 = qt.pulsar

    m.params_lt1 = m2.MeasurementParameters('LT1Parameters')
    m.params_lt2 = m2.MeasurementParameters('LT2Parameters')

    m.load_settings()
    m.update_definitions()
    m.repump_aom = qt.instruments['GreenAOM']
    
    # m.params_lt1['MW_pulse_mod_risetime'] = 2e-9

def finish(m, sequence=True, upload=True, debug=False):
    for key in m.params_lt1.to_dict():
        m.params[key] = m.params_lt1[key]

    m.autoconfig()
    
    if sequence:
        m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()

# def phaseref(frequency, time, offset=0):
#     return ((frequency*time + offset/360.) % 1) * 360.

def missing_grains(time, clock=1e9, granularity=4):
    if int(time*clock + 0.5) < 960:
        return 960 - int(time*clock + 0.5)

    grains = int(time*clock + 0.5)
    return granularity - grains%granularity

### msmt class
class BSMMsmt(pulsar_msmt.MBI):
    mprefix = 'BSM'

    def load_settings(self):
        for k in tparams.params.parameters:
            self.params[k] = tparams.params[k]

        for k in tparams.params_lt1.parameters:
            self.params_lt1[k] = tparams.params_lt1[k]

        self.params['MW_during_LDE'] = 1 if LDE_DO_MW else 0

    def update_definitions(self):
        tseq.pulse_defs_lt1(self)

        self.mbi_elt = tseq._lt1_mbi_element(self)
        self.LDE_element = tseq._lt1_LDE_element(self)
        self.adwin_lt1_trigger_element = tseq._lt1_adwin_LT1_trigger_element(self)
        self.N_RO_CNOT_elt = tseq._lt1_N_RO_CNOT_elt(self)
        self.wait_1us_elt = tseq._lt1_wait_1us_elt(self)
        
    def UNROT_element(self, name, N_pulse, evolution_time, time_offset, **kw):
            return tseq._lt1_UNROT_element(self, name, N_pulse, evolution_time, time_offset, **kw)
    def N_init_element(self, name, basis, **kw):
            return tseq._lt1_N_init_element(self, name, basis, **kw)
    def BSM_elements(self, name, time_offset, start_buffer_time = 240e-9, **kw):
            return tseq._lt1_BSM_elements(self, name, time_offset, start_buffer_time, **kw)

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
                    wfname = self.adwin_lt1_trigger_element.name)

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

        self.params['A_SP_durations'] = [self.params_lt1['repump_after_MBI_duration']]
        self.params['A_SP_amplitudes'] = [self.params_lt1['repump_after_MBI_amplitude']]
        self.params['E_RO_durations'] = [self.params_lt1['SSRO1_duration']]
        self.params['E_RO_amplitudes'] = [self.params_lt1['Ey_RO_amplitude']]
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
            qt.pulsar.upload(self.mbi_elt, self.adwin_lt1_trigger_element, 
                *flattened_sweep_elements)
        
        qt.pulsar.program_sequence(seq)

class ElectronRabiMsmt(ElectronReadoutMsmt):
    mprefix = 'BSM_ERabi'

    def get_sweep_elements(self):        
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-{}'.format(i), pulsar=qt.pulsar)
            e.append(self.T)            
            for j in range(self.params_lt1['MW_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(self.e_pulse,
                        frequency = self.params_lt1['MW_pulse_mod_frqs'][i],
                        amplitude = self.params_lt1['MW_pulse_amps'][i],
                        length = self.params_lt1['MW_pulse_durations'][i]))
                e.append(
                    pulse.cp(self.T, length=self.params_lt1['MW_pulse_delays'][i]))
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
                    frequency = self.params_lt1['MW_pulse_mod_frqs'][i],
                    amplitude = self.params_lt1['MW_pulse_amps'][i],
                    length = self.params_lt1['MW_pulse_durations'][i]))
            pulse_elts.append(e)

        for i in range(self.params['pts']):
            if self.params_lt1['MW_pulse_multiplicities'][i] == 0:
                sweep_elts.append(pulse_elts[i])

            else:
                subelts = []
                for j in range(self.params_lt1['MW_pulse_multiplicities'][i]):
                    subelts.append(pulse_elts[i])
                    subelts.append(wait_elt)
                sweep_elts.append(subelts)

        return sweep_elts

### reading out the nuclear spin only

class NReadoutMsmt(ElectronReadoutMsmt):
    mprefix = 'BSM_NReadout'

    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self.sweep_elements = self.get_sweep_elements()
        
        N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        N_RO_CNOT_elt.append(pulse.cp(self.T, length=500e-9))
        N_RO_CNOT_elt.append(self.pi2pi_m1)

        # create the sequence
        seq = self._add_MBI_and_sweep_elements_to_sequence(
            self.sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element,
            append_sync = False)

        # make the list of elements required for uploading
        flattened_sweep_elements = self._flatten_sweep_element_list(
            self.sweep_elements)

        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, self.adwin_lt1_trigger_element, N_RO_CNOT_elt,
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
            for j in range(self.params_lt1['RF_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(self.N_pulse,
                        frequency = self.params_lt1['RF_pulse_frqs'][i],
                        amplitude = self.params_lt1['RF_pulse_amps'][i],
                        length = self.params_lt1['RF_pulse_durations'][i]))
                e.append(
                    pulse.cp(self.TN, length=self.params_lt1['RF_pulse_delays'][i]))
            elts.append(e)

        return elts

# class NRabiMsmt

# class NTomo(NReadoutMsmt):
#     mprefix = 'BSM_NTomo'

#     def autoconfig(self):
#         NReadoutMsmt.autoconfig(self)

#         self.params['pts'] = 3
#         self.params_lt1['tomo_bases'] = ['Z', 'X', 'Y']
#         self.params_lt1['tomo_pulse_amps'] = \
#             [0, self.params_lt1['N_pi2_amp'], self.params_lt1['N_pi2_amp']]

#         # Convention phi=0 makes |x>, i.e., rotates around +y
#         self.params_lt1['tomo_pulse_phases'] = [0, 180., 90.]

#         # for the autoanalysis
#         self.params_lt1['sweep_name'] = 'Readout basis (Z, X, Y)'
#         self.params_lt1['sweep_pts'] = range(3)


#     # TODO: global time should be implemented in here
#     def get_sweep_elements(self):

#         z_element = element.Element('Z Tomo pulse', pulsar=qt.pulsar,
#             global_time = True, 
#             time_offset = self.params_lt1['tomo_time_offset'])
#         z_element.append(pulse.cp(self.TN, length=1e-6))

#         x_element = element.Element('X Tomo pulse', pulsar=qt.pulsar,
#             global_time = True, 
#             time_offset = self.params_lt1['tomo_time_offset'])
#         xn = x_element.append(pulse.cp(self.N_pi2, 
#             phase = self.params_lt1['tomo_pulse_phases'][1]))

#         y_element = element.Element('Y Tomo pulse', pulsar=qt.pulsar,
#             global_time = True,
#             time_offset = self.params_lt1['tomo_time_offset'])
#         yn = y_element.append(pulse.cp(self.N_pi2, 
#             phase = self.params_lt1['tomo_pulse_phases'][2]))

#         sweep_elements = []
#         for n, tomo_elt in zip(self.params_lt1['tomo_bases'],
#             [z_element, x_element, y_element]):

#             if type(self.element) == list:
#                 elts = [e for e in self.element]
#                 elts.append(tomo_elt)
#                 sweep_elements.append(elts)
#             else:
#                 elts = [self.element, tomo_elt]
#                 sweep_elements.append(elts)

#         return sweep_elements

# # class NTomo

### reading out first the electron then the nuclear spin

class ENReadoutMsmt(BSMMsmt):
    mprefix = 'BSM_ENReadout'

    def autoconfig(self):
        self.params['nr_of_ROsequences'] = 2

        BSMMsmt.autoconfig(self)
        
        self.params['A_SP_durations'] = [
            self.params_lt1['repump_after_MBI_duration'],
            self.params_lt1['repump_after_E_RO_duration'] ]
        self.params['A_SP_amplitudes'] = [
            self.params_lt1['repump_after_MBI_amplitude'],
            self.params_lt1['repump_after_E_RO_amplitude'] ]
        self.params['E_RO_durations'] = [
            self.params_lt1['SSRO1_duration'],
            self.params_lt1['SSRO2_duration'] ]
        self.params['E_RO_amplitudes'] = [
            self.params_lt1['Ey_RO_amplitude'],
            self.params_lt1['Ey_RO_amplitude'] ]
        self.params['send_AWG_start'] = [1, 1]
        self.params['sequence_wait_time'] = [0, 0]

    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self.sweep_elements = self.get_sweep_elements()

        # # CNOT element for nuclear spin readout
        # N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        # N_RO_CNOT_elt.append(self.pi2pi_m1)

        # create the sequence
        seq = self._add_MBI_and_sweep_elements_to_sequence(
            self.sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

        # make the list of elements required for uploading
        flattened_sweep_elements = self._flatten_sweep_element_list(
            self.sweep_elements)

        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, self.adwin_lt1_trigger_element, 
                self.N_RO_CNOT_elt, *flattened_sweep_elements)
        
        qt.pulsar.program_sequence(seq)

# class ENReadoutMsmt

# Full BSM
class TheRealBSM(ENReadoutMsmt):
    mprefix = "TheRealBSM"
    
    ### functions for particular elements / msmt parts
    # def BS_element(self, name, bs, **kw):
    #     ### some options
    #     CNOT_phase = kw.pop('CNOT_phase', 0)
    #     N_frq = kw.pop('N_frq', self.N_pi2.frequency)
    #     pi2_phase_phi = kw.pop('pi2_phase_phi', 0)
    #     pi2_phase_psi = kw.pop('pi2_phase_psi', 0)
    #     BS_CNOT_amp = kw.pop('BS_CNOT_amp', self.params_lt1['pi2pi_mIm1_amp'])
        
    #     ### make the element
    #     BS_elt = element.Element('BS-{}'.format(name), 
    #         pulsar = qt.pulsar,
    #         global_time = True)
    #     BS_elt.append(self.T)
    #     BS_elt.append(self.shelving_pulse)
    #     BS_elt.append(pulse.cp(self.TIQ, length = 200e-9))

    #     if 'phi' in bs:
    #         pi2_phase = pi2_phase_phi
    #     elif 'psi' in bs:
    #         pi2_phase = pi2_phase_psi

    #     if '+' in bs:
    #         phase = pi2_phase + 0
    #     elif '-' in bs:
    #         phase = pi2_phase + 180 
        
    #     N_rot_name = BS_elt.append(pulse.cp(self.N_pi2,
    #         frequency = N_frq,
    #         phase = phase))
    #     BS_elt.append(self.TIQ)
        
    #     if bs in ['phi+', 'phi-']:
    #         CNOT = pulse.cp(self.pi2pi_0,
    #             phase = CNOT_phase,
    #             amplitude = BS_CNOT_amp)
            
    #     elif bs in ['psi+', 'psi-']:
    #         CNOT = pulse.cp(self.pi2pi_m1,
    #             phase = CNOT_phase,
    #             amplitude = BS_CNOT_amp)
            
    #     CNOT_name = BS_elt.append(CNOT)

    #     # N_phase_ref = phaseref(self.N_pi2.frequency, 
    #     #     BS_elt.length() - BS_elt.effective_pulse_start_time(N_rot_name,
    #     #         'RF'))

    #     # e_phase_ref = phaseref(self.pi2pi_m1.frequency,
    #     #     BS_elt.length() - BS_elt.effective_pulse_start_time(CNOT_name,
    #     #         'MW_Imod'))

    #     return BS_elt


    # def tomo_element(self, basis, time_offset):

    #     if basis == 'z':
    #         z_element = element.Element('Z Tomo pulse', pulsar=qt.pulsar,
    #             global_time = True, 
    #             time_offset = time_offset)
    #         z_element.append(pulse.cp(self.TN, length=1e-6))

    #         return z_element

    #     elif basis == 'x':
    #         x_element = element.Element('X Tomo pulse', pulsar=qt.pulsar,
    #             global_time = True, 
    #             time_offset = time_offset)
    #         x_element.append(pulse.cp(self.N_pi2, 
    #             phase = 180.))

    #         return x_element

    #     elif basis == 'y':
    #         y_element = element.Element('Y Tomo pulse', pulsar=qt.pulsar,
    #             global_time = True,
    #             time_offset = self.params_lt1['tomo_time_offset'])
    #         y_element.append(pulse.cp(self.N_pi2, 
    #             phase = 90.))

    #         return y_element

    #     else:
    #         raise Exception('Unknown tomography basis')

    ### test/calibration and debug functions

    # def test_UNROT_element_overview(self):
    #     """
    #     make a simple unconditional rotation element and print the info,
    #     just to see if the timings are correct.
    #     """
    #     self._pulse_defs()
        
    #     N_pulse = [ self.N_pi2, self.N_pi ]
    #     evolution_time = 140e-6
    #     time_offset = 0

    #     elt = self.UNROT_element(
    #         'test_UNROT_timings', N_pulse, evolution_time,
    #         time_offset, verbose=True)

    #     elt.print_overview()

    # # NOT USEFUL LIKE THIS -- TIME IN ms=0 NOT MATCHED
    # def test_UNROT_H_phase(self, ms, input):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))

    #     prep_elt = element.Element('UNROT-prep', pulsar=qt.pulsar,
    #         global_time = True)
    #     prep_elt.append(self.T)
    #     prep_elt.append(pulse.cp(self.fast_pi,
    #         amplitude=1.))
    #     prep_elt.append(pulse.cp(self.T, length=200e-9))


    #     amplitude = 1
    #     phase = 0.
    #     if input == 'z':
    #         amplitude = 0
    #     elif input == 'y':
    #         phase = -90.

    #     prep_elt.append(pulse.cp(self.N_pi2,
    #         phase = phase,
    #         amplitude = amplitude))

    #     if ms == '0':
    #         prep_elt.append(pulse.cp(self.TIQ))
    #         prep_elt.append(pulse.cp(self.CORPSE_pi,
    #             phaselock = False))
    #         prep_elt.append(pulse.cp(self.TIQ, 
    #             length=200e-9))

    #     self.flattened_elements.append(prep_elt)

    #     # UNROT-H
    #     H_pulses = [ pulse.cp(self.N_pi2, phase=0),
    #         pulse.cp(self.N_pi, phase=90.) ]

    #     unrot_elt = self.UNROT_element('UNROT-H',
    #         H_pulses, self.params_lt1['H_evolution_time'], prep_elt.length())

    #     self.flattened_elements.append(unrot_elt)

    #     for i,phi in enumerate(self.params_lt1['analysis_phases']):
    #         analysis_elt = element.Element('UNROT-analysis-{}'.format(i), 
    #             pulsar = qt.pulsar,
    #             global_time = True,
    #             time_offset = prep_elt.length()+unrot_elt.length())
            
    #         if ms == '1':
    #             analysis_elt.append(pulse.cp(self.TIQ))
    #             analysis_elt.append(pulse.cp(self.CORPSE_pi,
    #                 phaselock = False))
    #             analysis_elt.append(pulse.cp(self.TIQ, 
    #                 length=200e-9))

    #         analysis_elt.append(pulse.cp(self.N_pi2,
    #             phase = phi))

    #         self.flattened_elements.append(analysis_elt)
    #         sweep_elements.append([prep_elt, unrot_elt, analysis_elt])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BS_ZZ_correlations(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))

    #     for bs in self.params_lt1['bellstates']:
    #         bs_elt = self.BS_element(bs, bs)
    #         self.flattened_elements.append(bs_elt)
    #         sweep_elements.append(bs_elt)

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     for bs in self.params_lt1['bellstates']:
    #         bs_elt = self.BS_element(bs, bs)
    #         CNOT, UNROT_H = self.BSM_elements(bs, bs_elt.length())

    #         self.flattened_elements.append(bs_elt)
    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM_vs_BSM_params(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']
    #     bs_elt = self.BS_element(bs, bs)
    #     self.flattened_elements.append(bs_elt)

    #     for i in range(self.params['pts']):

    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             time_offset = bs_elt.length(),
    #             CORPSE_pi_phase_shift = \
    #                 self.params_lt1['CORPSE_pi_phase_shifts'][i],
    #             CNOT_phase_shift = \
    #                 self.params_lt1['BSM_CNOT_phase_shifts'][i])

    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM_vs_evolution_time(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']
    #     bs_elt = self.BS_element(bs, bs)
    #     self.flattened_elements.append(bs_elt)

    #     for i in range(self.params['pts']):

    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             time_offset = bs_elt.length(),
    #             evolution_time = self.params_lt1['H_evolution_times'][i])

    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM_and_BS_generation(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']
    #     for i in range(self.params['pts']):
            
    #         bs_elt = self.BS_element('{}-{}'.format(bs,i), bs,
    #             CNOT_phase = self.params_lt1['CNOT_phases'][i])

    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             time_offset = bs_elt.length(),
    #             start_buffer_time = self.params_lt1['BSM_start_buffer_times'][i])

    #         self.flattened_elements.append(bs_elt)
    #                    self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM_vs_BS_N_frq(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']
    #     for i in range(self.params['pts']):
            
    #         bs_elt = self.BS_element('{}-{}'.format(bs,i), bs,
    #             N_frq = self.params_lt1['BS_N_frqs'][i])

    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             time_offset = bs_elt.length())

    #         self.flattened_elements.append(bs_elt)
    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM_CNOT(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']
    #     bs_elt, N_phase, e_phase = self.BS_element(bs, bs)
    #     self.flattened_elements.append(bs_elt)

    #     for i in range(self.params['pts']):
    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             N_phase, e_phase, 
    #             CNOT_offset = self.params_lt1['CNOT_offsets'][i])
            
    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)


    # def test_BSM_vs_Hadamard_phase(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']       

    #     for i in range(self.params['pts']):
            
    #         bs_elt = self.BS_element('{}-{}'.format(bs,i), bs, 
    #             pi2_phase_psi = self.params_lt1['bs_psi_pi2_phases'][i],
    #             pi2_phase_phi = self.params_lt1['bs_phi_pi2_phases'][i])

    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             time_offset = bs_elt.length(),
    #             H_phase = self.params_lt1['H_phases'][i],
    #             start_buffer_time = 259e-9 ) #= 1/A - 1/2*pi2pi.length

    #         self.flattened_elements.append(bs_elt)
    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM_eigenstates_in(self):
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     es = self.params_lt1['eigenstate']       

    #     for i in range(self.params['pts']):
            
    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(es,i), 
    #             time_offset = 0,
    #             H_phase = self.params_lt1['H_phases'][i])

    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    def test_BSM_superposition_in(self):
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))
 
        e_pi2_elt = element.Element('e_pi2', pulsar = qt.pulsar, 
            global_time = True, time_offset =0)

        e_pi2_elt.append(pulse.cp(self.TIQ, 
            length = 800e-9))

        e_pi2_elt.append(self.fast_pi2)

        e_pi2_elt.append(pulse.cp(self.TIQ, 
            length = 200e-9))

        
        UNROT_N_init = self.UNROT_element('N_init',
            self.N_pi2, 
            self.params_lt1['pi2_evolution_time']-self.fast_pi2.length/2 -200E-9, 
            #Above time: to start time at centre pi/2, and to subtract waiting time after pi/2
            e_pi2_elt.length(), 
            end_offset_time = self.fast_pi2.length/2 + 200e-9 - 240e-9)
            #end_offset time: to get 'pi2_evolution_time', 
            #and compensate for CNOT time in next element 
        
        for i in range(self.params['pts']):
            
            CNOT, UNROT_H = self.BSM_elements('{}'.format(i), 
                time_offset = e_pi2_elt.length()+UNROT_N_init.length(),
                H_phase = self.params_lt1['H_phases'][i], 
                evolution_time = self.params_lt1['H_evolution_times'][i])
            
            self.flattened_elements.append(e_pi2_elt)
            self.flattened_elements.append(UNROT_N_init)
            self.flattened_elements.append(CNOT)
            self.flattened_elements.append(UNROT_H)
            sweep_elements.append([e_pi2_elt,UNROT_N_init,CNOT, UNROT_H])
            
        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    def test_BSM_with_LDE_element_superposition_in(self):
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))

        for i in range(self.params['pts']):            
            N_init = self.N_init_element(self, 
                'N_init', 
                basis = 'X', 
                echo_time_after_LDE = self.params_lt1['echo_times_after_LDE'][i])

            CNOT, UNROT_H = self.BSM_elements('{}'.format(i), 
                time_offset = e_pi2_elt.length()+UNROT_N_init.length(),
                H_phase = self.params_lt1['H_phases'][i], 
                evolution_time = self.params_lt1['H_evolution_times'][i])
            
            self.flattened_elements.append(LDE_element)
            self.flattened_elements.append(N_init)
            self.flattened_elements.append(CNOT)
            self.flattened_elements.append(UNROT_H)
            sweep_elements.append([LDE_element,N_init,CNOT, UNROT_H])
            
        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    def test_BSM_with_LDE_element_calibrate_echo_time(self):
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))

        e_pi2_elt = element.Element('e_pi2', pulsar = qt.pulsar, 
            global_time = True, time_offset =0)
        e_pi2_elt.append(pulse.cp(self.TIQ, 
            length = 100e-9))
        e_pi2_elt.append(self.fast_pi2)
            

        for i in range(self.params['pts']):            
            N_init = self.N_init_element('N_init-{}'.format(i), 
                basis = 'Z', 
                echo_time_after_LDE = self.params_lt1['echo_times_after_LDE'][i], 
                end_offset_time = -100e-9)
            
            self.flattened_elements.append(self.LDE_element)
            self.flattened_elements.append(N_init)
            self.flattened_elements.append(e_pi2_elt)
            sweep_elements.append([self.LDE_element,N_init,e_pi2_elt])
            
        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)


    # def test_BSM_without_CORPSE_and_2nd_H(self):
    #     """
    #     Test the BSM by putting in a BS, and leaving out the CORPSE and 2nd Hadamard.
    #     The script below only works when putting in the psi+ state! 
    #     """
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']      

    #     for i in range(self.params['pts']):
            
    #         bs_elt = self.BS_element('{}-{}'.format(bs,i), bs, 
    #             pi2_phase_psi = self.params_lt1['bs_pi2_phases'][i],
    #             BS_CNOT_amp = self.params_lt1['BS_CNOT_amp'])
            
    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             time_offset = bs_elt.length(),
    #             H_phase = self.params_lt1['H_phases'][i],
    #             BSM_CNOT_amp = self.params_lt1['BSM_CNOT_amp'],
    #             first_N_pulse_only = True)

    #         self.flattened_elements.append(bs_elt)
    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])
        
    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    # #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    # def test_BSM_without_2nd_H(self):
    #     """
    #     Test the BSM by putting in a BS, and leaving out the CORPSE and 2nd Hadamard.
    #     The script below only works when putting in the psi+ state! 
    #     """
    #     self._pulse_defs()
    #     sweep_elements = []
    #     self.flattened_elements = []
    #     self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
    #         self.name))
        
    #     bs = self.params_lt1['bellstate']       

    #     for i in range(self.params['pts']):
            
    #         bs_elt = self.BS_element('{}-{}'.format(bs,i), bs, 
    #             pi2_phase_psi = self.params_lt1['bs_pi2_phases'][i])

    #         CNOT, UNROT_H = self.BSM_elements('{}-{}'.format(bs,i), 
    #             time_offset = bs_elt.length(),
    #             H_phase = self.params_lt1['H_phases'][i],
    #             no_second_N_pulse = True)

    #         self.flattened_elements.append(bs_elt)
    #         self.flattened_elements.append(CNOT)
    #         self.flattened_elements.append(UNROT_H)
    #         sweep_elements.append([bs_elt, CNOT, UNROT_H])

    #     self.seq = self._add_MBI_and_sweep_elements_to_sequence(
    #         sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    def calibrate_CORPSE_pi_phase_shift(self):
        """
        Do a Hahn echo sequence with the CORPSE pi pulse, and sweep it's zero
        phase with respect the rotating frame at that time.
        """
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))

        first_pi2_elt = element.Element('first pi2', pulsar=qt.pulsar,
            global_time = True)
        first_pi2_elt.append(pulse.cp(self.T, length=1e-6))
        first_pi2_name = first_pi2_elt.append(self.fast_pi2)
        first_pi2_elt.append(pulse.cp(self.TIQ, length=100e-9))

        self.flattened_elements.append(first_pi2_elt)

        # phase reference for the UNROT element
        # e_ref_phase = phaseref(self.fast_pi2.frequency,
        #     first_pi2_elt.length() - \
        #     first_pi2_elt.effective_pulse_start_time(first_pi2_name,'MW_Imod'))

        # calculate the evolution time from the interpulse delay
        etime = self.params_lt1['interpulse_delay'] - \
            self.CORPSE_pi.effective_length()/2.

        pi_elts = []
        for i in range(self.params['pts']):
            e = self.UNROT_element('pi-{}'.format(i),
                None, etime, first_pi2_elt.length(),
                CORPSE_pi_phase_shift = \
                    self.params_lt1['CORPSE_pi_phase_shifts'][i])
            
            self.flattened_elements.append(e)
            pi_elts.append(e)

        # the start time of the second pi2 depends on the time when the
        # pulse stops in the first pi2 element:
        t_pi2 = first_pi2_elt.length() - \
            first_pi2_elt.effective_pulse_end_time(first_pi2_name, 'MW_Imod')

        # the phase...
        # pi2_phase = phaseref(self.fast_pi2.frequency,
        #     first_pi2_elt.length() - \
        #         first_pi2_elt.effective_pulse_start_time(first_pi2_name,'MW_Imod') + \
        #         2*etime + t_pi2)

        # make the element
        second_pi2_elt = element.Element('second pi2', pulsar=qt.pulsar,
            global_time = True, 
            time_offset = e.length()+first_pi2_elt.length())        
        second_pi2_elt.append(pulse.cp(self.TIQ, length=t_pi2))
        second_pi2_elt.append(self.fast_pi2)

        self.flattened_elements.append(second_pi2_elt)
        self.flattened_elements.append(self.N_RO_CNOT_elt)

        for i in range(self.params['pts']):
            sweep_elements.append([first_pi2_elt, 
                pi_elts[i], second_pi2_elt])
        
        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)
    
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
        sweep_elements = []
        self.flattened_elements = []
        self.seq = pulsar.Sequence('{}_{}-Sequence'.format(self.mprefix, 
            self.name))

        prep_elt = element.Element('UNROT-prep', pulsar=qt.pulsar,
            global_time = True)
        prep_elt.append(self.T)
        
        if eigenstate == '-1':
            prep_elt.append(self.fast_pi)
        else:
            prep_elt.append(pulse.cp(self.fast_pi,
                amplitude = 0.))

        self.flattened_elements.append(self.mbi_elt)
        self.flattened_elements.append(prep_elt)

        for i,t in enumerate(self.params_lt1['evolution_times']):
            e = self.UNROT_element('UNROT-{}'.format(i),
                self.N_pi2, t, prep_elt.length(), 
                end_offset_time = -1e-6)

            self.flattened_elements.append(e)

            analysis_elt = element.Element('UNROT-analysis-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time = True,
                time_offset = prep_elt.length()+e.length())
            
            if eigenstate == '-1':
                t_CORPSE = 1e-6 - self.CORPSE_pi.effective_length()/2. + \
                    self.params_lt1['CORPSE_pi_center_shift']           
                
                # phi_CORPSE = 0 # only care about inversion here
                
                analysis_elt.append(pulse.cp(self.TIQ, 
                    length=t_CORPSE))
                analysis_elt.append(pulse.cp(self.CORPSE_pi,
                    phaselock = False))
                analysis_elt.append(pulse.cp(self.TIQ, 
                    length=200e-9))
            else:
                t_wait = 1.2e-6 + self.CORPSE_pi.effective_length()/2. + \
                    self.params_lt1['CORPSE_pi_center_shift']
                analysis_elt.append(pulse.cp(self.TIQ, length=t_wait))

            # t_total = 1.2e-6 + self.CORPSE_pi.effective_length()/2. + \
            #         self.params_lt1['CORPSE_pi_center_shift']

            # the phase of the analysis N rotation
            # delta_t_Nrot2 = t_total - analysis_elt.channel_delay('RF') + \
            #     analysis_elt.channel_delay('MW_Imod')
            # phi_Nrot2 = phaseref(self.N_pi2.frequency,
            #     e.length() + delta_t_Nrot2)
            
            analysis_elt.append(self.N_pi2)

            self.flattened_elements.append(analysis_elt)
            sweep_elements.append([prep_elt, e, analysis_elt])

        self.seq = self._add_MBI_and_sweep_elements_to_sequence(
            sweep_elements, self.N_RO_CNOT_elt, self.adwin_lt1_trigger_element)

    ### tools

    def generate_sequence(self, upload=True):
        self.flattened_elements.append(self.mbi_elt)
        self.flattened_elements.append(self.adwin_lt1_trigger_element)
        self.flattened_elements.append(self.N_RO_CNOT_elt)
        self.flattened_elements.append(self.wait_1us_elt)
        
        # program AWG
        if upload:
            qt.pulsar.upload(*self.flattened_elements)
        
        qt.pulsar.program_sequence(self.seq)


# class TheRealBSM

# ### scripts -- run BSM/BSM testing
# def bsm_test_print_UNROT_element(name):
#     m = TheRealBSM(name)
#     prepare(m)

#     # bogus msmt parameters, not actually used here
#     pts = 3
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 500

#     m.test_UNROT_element_overview()

#     finish(m, sequence=False, debug=True, upload=False)

# # NOT USEFUL LIKE THIS -- TIME IN ms=0 NOT MATCHED
# def bsm_test_UNROT_H_phase(name):
#     m = TheRealBSM('TestBSM_UNROT_H_phase_'+name)
#     prepare(m)

#     pts = 9
#     m.params_lt1['analysis_phases'] = np.linspace(0,360,pts)

#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['H_evolution_time'] = 139.797e-6

#     m.params_lt1['sweep_name'] = 'final pi/2 phase (deg)'
#     m.params_lt1['sweep_pts'] = m.params_lt1['analysis_phases']

#     m.test_UNROT_H_phase('1', 'z')

#     finish(m, debug=False, upload=True)

# def bsm_test_BS_ZZ_correlations():
#     m = TheRealBSM('test_BS_ZZ_correlations')
#     prepare(m)

#     # bogus msmt parameters, not actually used here
#     pts = 4
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstates'] = ['phi+', 'phi-', 'psi+', 'psi-']
#     m.test_BS_ZZ_correlations()
    
#     m.params_lt1['sweep_name'] = 'Bell state'
#     m.params_lt1['sweep_pts'] = np.arange(4)

#     finish(m, debug=False, upload=True)

def bsm_calibrate_CORPSE_pi_phase_shift():
    m = TheRealBSM('CalibrateCORPSEPiPhase_51us')
    prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['CORPSE_pi_phase_shifts'] = np.linspace(0,180,pts)
    m.params_lt1['interpulse_delay'] = 51e-6
    m.calibrate_CORPSE_pi_phase_shift()

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'CORPSE relative phase shift (deg)'
    m.params_lt1['sweep_pts'] = m.params_lt1['CORPSE_pi_phase_shifts']

    finish(m, debug=False, upload=True)

def bsm_calibrate_UNROT_X_timing(name):
    m = TheRealBSM(name)
    prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params_lt1['evolution_times'] = 50.9e-6 + np.linspace(-400e-9,400e-9,pts)
    m.calibrate_UNROT_X_timing(eigenstate='-1')

    # for the autoanalysis
    m.params_lt1['sweep_name'] = 'evolution time (us)'
    m.params_lt1['sweep_pts'] = m.params_lt1['evolution_times'] * 1e6

    finish(m, debug=False, upload=True)

# def bsm_test_BSM():
#     m = TheRealBSM('TestBSM')
#     prepare(m)

#     pts = 4
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstates'] = ['phi+', 'phi-', 'psi+', 'psi-']
#     m.params_lt1['H_evolution_time'] = 139.797e-6

#     m.params_lt1['sweep_name'] = 'Bell state'
#     m.params_lt1['sweep_pts'] = np.arange(4)

#     m.test_BSM()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_CORPSE_phase(name):
#     m = TheRealBSM('TestBSM_vs_CORPSE_phase_'+name)
#     prepare(m)

#     pts = 17
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 139.797e-6
    
#     m.params_lt1['CORPSE_pi_phase_shifts'] = np.linspace(0,360,pts)
#     m.params_lt1['BSM_CNOT_phase_shifts'] = np.zeros(pts)

#     m.params_lt1['sweep_name'] = 'CORPSE relative phase shift (deg)'
#     m.params_lt1['sweep_pts'] = m.params_lt1['CORPSE_pi_phase_shifts']

#     m.test_BSM_vs_BSM_params()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_CNOT_phase(name):
#     m = TheRealBSM('TestBSM_vs_CNOT_phase_'+name)
#     prepare(m)

#     pts = 9
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 139.797e-6
    
#     m.params_lt1['CORPSE_pi_phase_shifts'] = np.ones(pts) * m.params_lt1['CORPSE_pi_phase_shift']
#     m.params_lt1['BSM_CNOT_phase_shifts'] = np.linspace(0,360,pts)

#     m.params_lt1['sweep_name'] = 'CNOT relative phase shift (deg)'
#     m.params_lt1['sweep_pts'] = m.params_lt1['BSM_CNOT_phase_shifts']

#     m.test_BSM_vs_BSM_params()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_evolution_time(name):
#     m = TheRealBSM('TestBSM_vs_evolution_time_'+name)
#     prepare(m)

#     pts = 17
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 139.797e-6
#     m.params_lt1['H_evolution_times'] = 139.797e-6 + np.linspace(-400e-9,400e-9,pts)    

#     m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H evolution time (us)'
#     m.params_lt1['sweep_pts'] = m.params_lt1['H_evolution_times'] * 1e6

#     m.test_BSM_vs_evolution_time()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_BS_CNOT_phase(name):
#     m = TheRealBSM('TestBSM_vs_BS_CNOT_phase_'+name)
#     prepare(m)

#     m.params_lt1['CNOT_phases'] = np.linspace(0,360,9)
#     m.params_lt1['BSM_start_buffer_times'] = np.ones(9) * 240e-9

#     pts = len(m.params_lt1['CNOT_phases'])
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 139.797e-6

#     m.params_lt1['sweep_name'] = 'CNOT phase (deg)'
#     m.params_lt1['sweep_pts'] = m.params_lt1['CNOT_phases']

#     m.test_BSM_and_BS_generation()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_BS_N_frq(name):
#     m = TheRealBSM('TestBSM_vs_BS_N_frq_'+name)
#     prepare(m)

#     pts = 17
#     m.params_lt1['BS_N_frqs'] = 7.13444e6 + np.linspace(-1e3,1e3,pts)

#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 139.797e-6

#     m.params_lt1['sweep_name'] = 'BS N driving frq (MHz)'
#     m.params_lt1['sweep_pts'] = m.params_lt1['BS_N_frqs'] * 1e-6

#     m.test_BSM_vs_BS_N_frq()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_BS_delay(name):
#     m = TheRealBSM('TestBSM_vs_BS_delay_'+name)
#     prepare(m)

#     m.params_lt1['CNOT_phases'] = np.zeros(11) # np.linspace(0,360,9)
#     m.params_lt1['BSM_start_buffer_times'] = np.linspace(0, 480e-9, 11) + 240e-9

#     pts = len(m.params_lt1['CNOT_phases'])
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 139.797e-6

#     m.params_lt1['sweep_name'] = 'Post-BS generation delay'
#     m.params_lt1['sweep_pts'] = m.params_lt1['BSM_start_buffer_times']

#     m.test_BSM_and_BS_generation()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_CNOT_offset(name):
#     m = TheRealBSM('TestBSM_vs_CNOT_offset_'+name)
#     prepare(m)

#     m.params_lt1['CNOT_offsets'] = np.linspace(0,100e-9,11)

#     pts = len(m.params_lt1['CNOT_offsets'])
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 139.797e-6

#     m.params_lt1['sweep_name'] = 'CNOT time offset (ns)'
#     m.params_lt1['sweep_pts'] = m.params_lt1['CNOT_offsets'] * 1e9

#     m.test_BSM_CNOT()

#     finish(m, debug=False, upload=True)

# def bsm_test_BSM_vs_Hadamard_phase(name):
#     m = TheRealBSM('TestBSM_vs_Hadamard_phase_'+name)
#     prepare(m, yellow=True)

#     pts = 11
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 51.070e-6
#     m.params_lt1['H_phases'] = np.linspace(0,360,pts) 
#     m.params_lt1['bs_psi_pi2_phases'] = 0. * np.ones(pts) #62
#     m.params_lt1['bs_phi_pi2_phases'] = 0. * np.ones(pts) #71

#     m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
#     m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

#     m.test_BSM_vs_Hadamard_phase()

#     finish(m, debug=False, upload=True)
  

# def bsm_test_BSM_eigenstates_in(name):
#     m = TheRealBSM('TestBSM_eigenstates_in_'+name)
#     prepare(m)

#     pts = 11
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['eigenstate'] = '-1,0'
#     m.params_lt1['H_evolution_time'] = 139.797e-6
#     m.params_lt1['H_phases'] = np.linspace(0,360,pts) 

#     m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
#     m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

#     m.test_BSM_eigenstates_in()

#     finish(m, debug=False, upload=True)
  

def bsm_test_BSM_superposition_in_sweep_H_phase(name):
    m = TheRealBSM('TestBSM_superposition_in_'+name)
    prepare(m)
    
    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['pi2_evolution_time'] = 51.089e-6 #calibrated value
    m.params_lt1['H_evolution_times'] = np.ones(pts)*51.089e-6 #139.995e-6 + 194e-9#calibrated value + correction (234 deg).
    m.params_lt1['H_phases'] = np.linspace(0,720,pts) 

    m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

    m.test_BSM_superposition_in()
    
    finish(m, debug=False, upload=True)    


def bsm_test_BSM_with_LDE_superposition_in_sweep_H_phase(name):
    m = TheRealBSM('TestBSM_superposition_in_'+name)
    prepare(m)
    
    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['repump_after_MBI_amplitude'] = 0. #SP is in LDE element!! :)

    m.params_lt1['echo_times_after_LDE'] = np.ones*m.params_lt1['echo_time_after_LDE']
    m.params_lt1['pi2_evolution_time'] = 51.089e-6 #calibrated value
    m.params_lt1['H_evolution_times'] = np.ones(pts)*51.089e-6 #139.995e-6 + 194e-9#calibrated value + correction (234 deg).
    m.params_lt1['H_phases'] = np.linspace(0,720,pts) 

    m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

    m.test_BSM_superposition_in()
    
    finish(m, debug=False, upload=True)    


def bsm_test_BSM_with_LDE_superposition_in_calibrate_echo_time(name):
    m = TheRealBSM('TestBSM_superposition_in_'+name)
    prepare(m)
    
    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params_lt1['repump_after_MBI_amplitude'] = 0. #SP is in LDE element!! :)

    m.params_lt1['echo_times_after_LDE'] = np.linspace(0,500e-9,pts)
    m.params_lt1['pi2_evolution_time'] = 51.089e-6 #calibrated value
    m.params_lt1['H_evolution_times'] = np.ones(pts)*51.089e-6 #139.995e-6 + 194e-9#calibrated value + correction (234 deg).
    m.params_lt1['H_phases'] = np.linspace(0,720,pts) 

    m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
    m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

    m.test_BSM_superposition_in()
    
    finish(m, debug=False, upload=True)    

# def bsm_test_BSM_w_time_corr_superposition_in(name):
#     m = TheRealBSM('TestBSM_w_time_corr_superposition_in_'+name)
#     prepare(m)
    
#     #this mmt tests the BSM by feeding in a superposition of psi+ and phi+.
#     #here the time t_pi - t_0 is corrected for the expected difference 
#     #between phi_00 and phi_01: t_pi - t_0 = 
#     pts = 11
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['pi2_evolution_time'] = 50.162e-6 #110/A
#     m.params_lt1['phi_00'] = 14 #+- 3
#     m.params_lt1['phI_01'] = 190 #+- 5
#     m.params_lt1['H_evolution_time'] = 139.997e-6 + 220e-9 #307/A + (phi_00-phi_01)/360 *1/A
#     m.params_lt1['H_phases'] = np.linspace(0,360,pts) 

#     m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
#     m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

#     m.test_BSM_superposition_in()
    
#     finish(m, debug=False, upload=True)  


# def bsm_test_BSM_without_CORPSE_and_2nd_H(name):
#     m = TheRealBSM('TestBSM_without_CORPSE_and_2nd_H_'+name)
#     prepare(m, yellow = True)
    
#     pts = 11
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     #option to also not do the BS and BSM CNOTs.
#     m.params_lt1['N_pi2_amp'] = 0.
#     m.params_lt1['BSM_CNOT_amp'] = 0.#m.params_lt1['pi2pi_mIm1_amp']
#     m.params_lt1['BS_CNOT_amp'] = 0.#m.params_lt1['pi2pi_mIm1_amp']
    
#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 51.070e-6
#     m.params_lt1['H_phases'] = np.linspace(0,360,pts) 
#     m.params_lt1['bs_pi2_phases'] = 0. * np.ones(pts)

#     m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
#     m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 
    
#     m.test_BSM_without_CORPSE_and_2nd_H()
    
#     finish(m, debug=False, upload=False)

# def bsm_test_BSM_without_2nd_H(name):
#     m = TheRealBSM('TestBSM_without_2nd_H'+name)
#     prepare(m)

#     pts = 11
#     m.params['pts'] = pts
#     m.params['reps_per_ROsequence'] = 1000

#     m.params_lt1['bellstate'] = 'psi+'
#     m.params_lt1['H_evolution_time'] = 51.070e-6
#     m.params_lt1['H_phases'] = np.linspace(0,360,pts) 
#     m.params_lt1['bs_pi2_phases'] = 0. * np.ones(pts)

#     m.params_lt1['sweep_name'] = 'CORPSE-UNROT-H phase'
#     m.params_lt1['sweep_pts'] = m.params_lt1['H_phases'] 

#     m.test_BSM_without_2nd_H()

#     finish(m, debug=False, upload=True)


if __name__ == '__main__':
    # bsm_test_print_UNROT_element('testing')
    # NOT USEFUL LIKE THIS bsm_test_UNROT_H_phase('input=Z_ms=1')
    bsm_calibrate_CORPSE_pi_phase_shift()
    bsm_calibrate_UNROT_X_timing('test_H_timing_ms=-1_191us')
    # bsm_test_BS_ZZ_correlations()
    # bsm_test_BSM()
    # bsm_test_BSM_vs_CORPSE_phase('psi+')
    # bsm_test_BSM_vs_CNOT_phase('psi+')
    # bsm_test_BSM_vs_evolution_time('psi+')
    # bsm_test_BSM_vs_BS_CNOT_phase('psi+')
    # bsm_test_BSM_vs_BS_N_frq('psi+')
    # bsm_test_BSM_vs_BS_delay('psi+')
    # bsm_test_BSM_vs_CNOT_offset('psi+')
    # bsm_test_BSM_vs_Hadamard_phase('psi+')
    # bsm_test_BSM_without_CORPSE_and_2nd_H('_and_nothing_else_psi+')
    # bsm_test_BSM_without_2nd_H('psi+')
    # bsm_test_BSM_eigenstates_in('-1,0')
    bsm_test_BSM_superposition_in('sil2_pi2_as_H_no_time_corr')
    # bsm_test_BSM_w_time_corr_superposition_in('sil2')



