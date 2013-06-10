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

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']

    m.params['MW_pulse_mod_risetime'] = 2e-9

def finish(m, upload=True, debug=False):
    m.autoconfig()
    m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()

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

        # CNOT operation on the electron
        self.pi2pi_m1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pi2pi_mIm1_mod_frq'],
            amplitude = self.params['pi2pi_mIm1_amp'],
            length = self.params['pi2pi_mIm1_duration'])

        ### nuclear spin manipulation pulses
        self.TN = pulse.SquarePulse(channel='RF',
            length = 100e-9, amplitude = 0)

        self.N_pulse = pulselib.RF_erf_envelope(
            channel = 'RF')


        ### synchronizing, etc
        self.adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)


        ### useful elements
        self.mbi_elt = self._MBI_element()

        self.sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        self.sync_elt.append(self.adwin_sync)


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
    mprefix = 'BSM_Readout'

    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self._pulse_defs()
        self.sweep_elements = self.get_sweep_elements()
        
        N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        N_RO_CNOT_elt.append(self.T)
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

### reading out first the electron then the nuclear spin

class ENReadoutMsmt(BSMMsmt):
    mprefix = 'BSM_ENReadout'

    def autoconfig(self):
        BSMMsmt.autoconfig(self)

        self.params['A_SP_durations'] = [
            self.params['repump_after_MBI_duration'],
            self.params['repump_afer_E_RO_duration'] ]
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
        N_RO_CNOT_elt = element.Element('N-RO CNOT')
        N_RO_CNOT_elt.append(self.pi2pi_m1)

        # create the sequence
        seq = self._add_MBI_and_sweep_elements_to_sequence(
            self.sweep_elements, N_RO_CNOT_elt, self.sync_elt)

        # make the list of elements required for uploading
        flattened_sweep_elements = self._flatten_sweep_element_list(
            self.sweep_elements)

        # program AWG
        if upload:
            qt.pulsar.upload(mbi_elt, sync_elt, 
                N_RO_CNOT_elt, *flattened_sweep_elements)
        
        qt.pulsar.program_sequence(seq)



