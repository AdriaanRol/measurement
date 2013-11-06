import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

class CORPSE_Pi2_Pi(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/2 pulse, followed by a pi-pulse; sweep the time between them.
    """
    mprefix = 'CORPSETest_Pi2_Pi'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
            eff_rotation_angle = 180)

        CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
            eff_rotation_angle = 90)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('CORPSE test')

        for i in range(self.params['pts']):
            e = element.Element('CORPSE_Pi2_Pi-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(CORPSE_pi2))
            e.append(pulse.cp(TIQ, length=self.params['delays'][i]))
            e.append(pulse.cp(CORPSE_pi))
            e.append(T)
            elts.append(e)
            seq.append(name='CORPSE_Pi2_Pi-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='sync-{}'.format(i),
                wfname = sync_elt.name)

        if upload:
            qt.pulsar.upload(sync_elt, wait_1us, *elts)
        qt.pulsar.program_sequence(seq)


class CORPSE_Pi2_Pi_sweep_p2_amp(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/2 pulse, followed by a pi-pulse; sweep the time between them.
    """
    mprefix = 'CORPSETest_Pi2_Pi'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
            eff_rotation_angle = 180)

        CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
            eff_rotation_angle = 90)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('CORPSE test')

        for i in range(self.params['pts_awg']):
            e = element.Element('CORPSE_Pi2-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(CORPSE_pi2, amplitude = self.params['CORPSE_pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=200e-9))
            e.append(pulse.cp(CORPSE_pi))
            e.append(T)
            elts.append(e)
            seq.append(name='CORPSE_Pi2-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='synca-{}'.format(i),
                wfname = sync_elt.name)
            e = element.Element('CORPSE_Pi2_Pi-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(CORPSE_pi2, amplitude = self.params['CORPSE_pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=200e-9))
            e.append(T)
            elts.append(e)
            seq.append(name='CORPSE_Pi2_Pi-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)

        if upload:
            qt.pulsar.upload(sync_elt, wait_1us, *elts)
        qt.pulsar.program_sequence(seq)

class CORPSE_Pi2_after_delay(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/2 pulse, after some delay.
    """
    mprefix = 'CORPSETest_Pi2_after_delay'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
            eff_rotation_angle = 90)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('CORPSE test')

        for i in range(self.params['pts']):
            e = element.Element('CORPSE_Pi2_after_delay{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(TIQ, length=self.params['delays'][i]))
            e.append(pulse.cp(CORPSE_pi2))
            e.append(T)
            elts.append(e)
            seq.append(name='CORPSE_Pi2_after_delay-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='sync-{}'.format(i),
                wfname = sync_elt.name)

        if upload:
            qt.pulsar.upload(sync_elt, wait_1us, *elts)
        qt.pulsar.program_sequence(seq)

class regular_Pi2_after_delay(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/2 pulse, after some delay.
    """
    mprefix = 'CORPSETest_Regular_Pi2_after_delay'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        pi2 = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['MW_pulse_duration'],
            amplitude = self.params['MW_pulse_amplitude'],
            frequency = self.params['MW_pulse_frequency'])

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('CORPSE test')

        for i in range(self.params['pts']):
            e = element.Element('regular_Pi2_after_delay{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(TIQ, length=self.params['delays'][i]))
            e.append(pulse.cp(pi2))
            e.append(T)
            elts.append(e)
            seq.append(name='regular_Pi2_after_delay-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='sync-{}'.format(i),
                wfname = sync_elt.name)

        if upload:
            qt.pulsar.upload(sync_elt, wait_1us, *elts)
        qt.pulsar.program_sequence(seq)

class CORPSE_Pi_after_delay(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi pulse, after some delay.
    """
    mprefix = 'CORPSETest_Pi_after_delay'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
            eff_rotation_angle = 180)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('CORPSE test')

        for i in range(self.params['pts']):
            e = element.Element('CORPSE_Pi_after_delay{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(TIQ, length=self.params['delays'][i]))
            e.append(pulse.cp(CORPSE_pi))
            e.append(T)
            elts.append(e)
            seq.append(name='CORPSE_Pi_after_delay-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='sync-{}'.format(i),
                wfname = sync_elt.name)

        if upload:
            qt.pulsar.upload(sync_elt, wait_1us, *elts)
        qt.pulsar.program_sequence(seq)

