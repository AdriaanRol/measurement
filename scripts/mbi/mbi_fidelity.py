"""
LT2 script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

import mbi_funcs 
reload(mbi_funcs)

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

class MBIFidelity(pulsar_mbi_espin.ElectronRabi):
    mprefix = 'MBIFidelity'

    def __init__(self, name):
        pulsar_mbi_espin.ElectronRabi.__init__(self, name)

    def autoconfig(self):
        pulsar_mbi_espin.ElectronRabi.autoconfig(self)

        self.adwin_process_params['Ex_N_randomize_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['Ex_N_randomize_amplitude'])

        self.adwin_process_params['A_N_randomize_voltage'] = \
            self.A_aom.power_to_voltage(
                    self.params['A_N_randomize_amplitude'])

        self.adwin_process_params['repump_N_randomize_voltage'] = \
            self.repump_aom.power_to_voltage(
                    self.params['repump_N_randomize_amplitude'])


def calibrate_MBI_fidelity_RO_pulses(name, params=None):
    m = pulsar_msmt.ElectronRabi(name+'_'+'MBI_fidelity_RO_pulses')
    
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    
    if params != None:
        m.params.from_dict(params.to_dict())

    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 5000

    # TODO these values should go into msmt params
    m.params['MBI_calibration_RO_pulse_duration'] = 8.3e-6
    m.params['MBI_calibration_RO_pulse_amplitude_sweep_vals'] = np.linspace(0.002,0.007,pts)
    m.params['MBI_calibration_RO_pulse_mod_frqs'] = \
        m.params['ms-1_cntr_frq'] - m.params['mw_frq'] + \
        np.array([-1,0,+1]) * m.params['N_HF_frq']
    
    m.params['MW_pulse_durations'] =  np.ones(pts) * m.params['MBI_calibration_RO_pulse_duration']  
    m.params['MW_pulse_amplitudes'] = m.params['MBI_calibration_RO_pulse_amplitude_sweep_vals']
 
    m.params['sweep_name'] = 'Pulse amplitudes (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10)

    for i,f in enumerate(m.params['MBI_calibration_RO_pulse_mod_frqs']):
        m.params['MW_pulse_frequency'] = f
        m.autoconfig()
        m.generate_sequence(upload=True)
        m.run()
        m.save('line-{}'.format(i))
        m.stop_sequence()
        qt.msleep(1)
    
    m.finish()

def calibrate_MBI_fidelity(name, params=None):
    m = MBIFidelity(name)
    mbi_funcs.prepare(m)

    if params != None:
        m.params.from_dict(params.to_dict())

    pts = 4
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 40000
     
    # overwrite this: at the moment the regular MBI program does not support that yet
    # (5 nov 2013)
    m.params['max_MBI_attempts'] = 100
    m.params['N_randomize_duration'] = 50
    m.params['Ex_N_randomize_amplitude'] = 10e-9
    m.params['A_N_randomize_amplitude'] = 10e-9
    m.params['repump_N_randomize_amplitude'] = 0

    # MW pulses
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 2000e-9

    # TODO put this into the msmt parameters file
    MIM1_AMP = 0.005254
    MI0_AMP = 0.005185
    MIP1_AMP = 0.005038
    m.params['MW_pulse_durations'] = np.ones(pts) * 8.3e-6 # the four readout pulse durations
    m.params['MW_pulse_amps'] = np.array([MIM1_AMP, MI0_AMP, MIP1_AMP, 0.]) # calibrated powers for equal-length pi-pulses

    # Assume for now that we're initializing into m_I = -1 (no other nuclear spins)
    f_m1 = m.params['AWG_MBI_MW_pulse_mod_frq']
    f_HF = m.params['N_HF_frq']

    m.params['MW_pulse_mod_frqs'] = f_m1 + np.array([0,1,2,5]) * f_HF

    # for the autoanalysis
    m.params['sweep_name'] = 'Readout transitions'
    m.params['sweep_pts'] = m.params['MW_pulse_mod_frqs']
    m.params['sweep_pt_names'] = ['$m_I = -1$', '$m_I = 0$', '$m_I = +1$', 'None']

    funcs.finish(m, debug=False)

if __name__ == '__main__':
    # calibrate_MBI_fidelity_RO_pulses(SAMPLE)
    calibrate_MBI_fidelity(SAMPLE) 
