"""
LT1 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.scripts.lt1_scripts import stools

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

from measurement.scripts.ssro import ssro_funcs as funcs
reload(funcs)


class YellowRepumpCalibration(pulsar_msmt.PulsarMeasurement):

    def autoconfig(self):
        pulsar_msmt.PulsarMeasurement.autoconfig(self)
                       
    def generate_sequence(self, **kw):

        upload = kw.pop('upload', True)

        T = pulse.SquarePulse(channel = 'Velocity1AOM', length = 1e-6, amplitude = 0.)
        R = pulse.SquarePulse(channel = 'Velocity1AOM', amplitude = 1.0)
        Y = pulse.SquarePulse(channel = 'YellowAOM', amplitude = 1.0)
        MW = pulselib.MW_IQmod_pulse('Long weak pulse', 
            I_channel='MW_Imod', Q_channel='MW_Qmod', 
            PM_channel='MW_pulsemod',
            frequency = self.params['ms-1_cntr_frq'] - self.params['mw_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'], 
            amplitude = 0.1)

        ionization_element = element.Element('ionization_element', pulsar = qt.pulsar)
        ionization_element.add(pulse.cp(R,
                amplitude = self.params['red_ionization_amplitude'], 
                length = 10e-6),
                name = 'red ionization pulse')
        ionization_element.add(pulse.cp(MW, length = 9.5e-6),
                refpulse = 'red ionization pulse', 
                refpoint = 'start')
        delay_element  = element.Element('delay_element', pulsar = qt.pulsar)
        delay_element.append(T)

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        seq = pulsar.Sequence('Yellow RP Calibration sequence')
        elements = []
        for i in range(self.params['pts']):    
            self.params['AWG_yellow_rp_amplitude'] = \
                self.repump_aom.power_to_voltage(
                    self.params['AWG_yellow_rp_powers'][i], controller='sec')

            repump_element = element.Element('repump_element-{}'.format(i), pulsar = qt.pulsar)
            repump_element.append(pulse.cp(Y, length = 10e-6, amplitude = self.params['AWG_yellow_rp_amplitude']))
            elements.append(repump_element)

            seq.append(name = ionization_element.name+'_{}'.format(i), 
                wfname = ionization_element.name,
                trigger_wait = True,
                repetitions = int(self.params['red_ionization_durations'][i]/10e-6))

            seq.append(name = delay_element.name+'_{}'.format(i),
                wfname = delay_element.name)

            seq.append(name = repump_element.name+'_{}'.format(i), 
                wfname = repump_element.name,
                repetitions = int(self.params['yellow_rp_durations'][i]/10e-6))
            seq.append(name = sync_elt.name+'-{}'.format(i), 
                wfname = sync_elt.name)

        # upload the waveforms to the AWG
        if upload:
            qt.pulsar.upload(ionization_element, delay_element, sync_elt, *elements)

        # program the AWG
        qt.pulsar.program_sequence(seq)


def yellowrepumpcalibration(name, yellow=False):
    m = YellowRepumpCalibration('Yellow_Repump_Calibration_'+name)
   
    funcs.prepare(m, yellow)
        
    # parameters
    m.params['wait_for_AWG_done'] = 1
    m.params['repetitions'] = 500
    m.params['pts'] = 5

    pts = m.params['pts']

    # sweep parameters
    m.params['red_ionization_durations'] = np.ones(pts)*100000e-6 # in chunks of 10 us, with minimum 1 us. 
    m.params['red_ionization_amplitude'] = 1.0
    m.params['yellow_rp_durations'] = np.linspace(1000e-6, 51000e-6, pts) # in chunks of 10 us, with minimum 1 us. 
    m.params['AWG_yellow_rp_powers'] =80e-9*np.ones(pts)

    m.params['sweep_pts'] = m.params['yellow_rp_durations']/1e-6
    m.params['sweep_name'] = 'yellow repump duration (us)'

    funcs.finish(m, mw=True, debug = False, upload = True)

if __name__ == '__main__':
    yellowrepumpcalibration('Hans-SIL4', yellow=True)
    #for lt1:
    stools.turn_off_AWG_laser_channel()
    


