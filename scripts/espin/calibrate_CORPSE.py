import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import espin_funcs as funcs
reload(funcs)


### msmt class
class CORPSEPiCalibration(pulsar_msmt.PulsarMeasurement):
    mprefix = 'CORPSEPiCalibration'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_pi_mod_frq'],
            amplitude = self.params['CORPSE_pi_amp'],
            length_60 = self.params['CORPSE_pi_60_duration'],
            length_m300 = self.params['CORPSE_pi_m300_duration'],
            length_420 = self.params['CORPSE_pi_420_duration'])

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        for i in range(self.params['pts']):
            e = element.Element('CORPSE-{}'.format(i), pulsar=qt.pulsar)
            e.append(T,
                pulse.cp(CORPSE_pi,
                    amplitude=self.params['CORPSE_pi_sweep_amps'][i]))
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('CORPSE pi calibration')
        for i,e in enumerate(elts):           
            for j in range(self.params['multiplicity']):
                seq.append(name = e.name+'-{}'.format(j), 
                    wfname = e.name,
                    trigger_wait = (j==0))
                seq.append(name = 'wait-{}-{}'.format(i,j), 
                    wfname = wait_1us.name, 
                    repetitions = self.params['delay_reps'])
            seq.append(name='sync-{}'.format(i),
                 wfname = sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(sync_elt, wait_1us, *elts)
        qt.pulsar.program_sequence(seq)

# class CORPSEPi2Calibration

class CORPSEPi2Calibration(pulsar_msmt.PulsarMeasurement):
    mprefix = 'CORPSEPi2Calibration'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi2 = pulselib.IQ_CORPSE_pi2_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_pi2_mod_frq'],
            amplitude = self.params['CORPSE_pi2_amp'],
            length_24p3 = self.params['CORPSE_pi2_24p3_duration'],
            length_m318p6 = self.params['CORPSE_pi2_m318p6_duration'],
            length_384p3 = self.params['CORPSE_pi2_384p3_duration'])

        delay_pulse = (pulse.cp(T, length=self.params['delay_element_length']))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        for i in range(self.params['pts']):
            e = element.Element('CORPSE-{}'.format(i), pulsar=qt.pulsar, global_time = True)
            e.append(T)
            for j in range(self.params['multiplicity']):
                e.append(pulse.cp(CORPSE_pi2,
                    amplitude=self.params['CORPSE_pi2_sweep_amps'][i]), delay_pulse)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('CORPSE pi over 2 calibration')
        for i,e in enumerate(elts):           
            seq.append(name = e.name+'-{}'.format(j), 
                    wfname = e.name,
                    trigger_wait = True)
            seq.append(name='sync-{}'.format(i),
                 wfname = sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(sync_elt, *elts)
        qt.pulsar.program_sequence(seq)

# class CORPSEPi2Calibration

def sweep_amplitude(name):
    m = CORPSEPiCalibration(name)
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.6, 0.8, pts)
    m.params['multiplicity'] = 11
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    
    funcs.finish(m, debug=False)

def lt1_hans4_calibrate_msm1_pi(name='hans4_msm1_pi'):
    m = CORPSEPiCalibration(name)
    funcs.prepare(m)

    pts = 11
    CORPSE_frq = 8e6
    m.params['CORPSE_pi_60_duration'] = 1./CORPSE_frq/6.
    m.params['CORPSE_pi_m300_duration'] = 5./CORPSE_frq/6.
    m.params['CORPSE_pi_420_duration'] = 7./CORPSE_frq/6.
    m.params['CORPSE_pi_mod_frq'] = m.params['ms-1_cntr_frq'] - m.params['mw_frq']

    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.65, 0.9, pts)
    m.params['multiplicity'] = 5
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    m.params['wait_for_AWG_done'] = 1
    
    funcs.finish(m, debug=False)

def lt1_hans4_calibrate_msm1_pi2(name='hans4_msm1_pi'):
    m = CORPSEPi2Calibration(name)
    funcs.prepare(m)

    pts = 11
    CORPSE_frq = 8e6
    m.params['CORPSE_pi2_24p3_duration'] = 1./CORPSE_frq/6.
    m.params['CORPSE_pi2_m318p6_duration'] = 5./CORPSE_frq/6.
    m.params['CORPSE_pi2_384p3_duration'] = 7./CORPSE_frq/6.
    m.params['CORPSE_pi2_mod_frq'] = m.params['ms-1_cntr_frq'] - m.params['mw_frq']

    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    # sweep params
    m.params['CORPSE_pi2_sweep_amps'] = np.linspace(0.65, 0.9, pts)
    m.params['multiplicity'] = 1
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi2_sweep_amps']
    m.params['wait_for_AWG_done'] = 1
    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    # sweep_amplitude('sil9_test')
    # lt1_hans4_calibrate_msm1_pi()
    lt1_hans4_calibrate_msm1_pi2()