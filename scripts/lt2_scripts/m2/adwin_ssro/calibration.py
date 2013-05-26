"""
LT2 script for calibration
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import measurement.lib.config.awgchannels_lt2 as awgcfg

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import sequence
from measurement.lib.measurement2.adwin_ssro import mbi
from measurement.lib.measurement2.adwin_ssro import mbi_espin

ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt2_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM']
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']

sequence.SequenceSSRO.awg = qt.instruments['AWG']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100']
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['spin']

mbi.MBIMeasurement.chan_RF = 'RF'
mbi.MBIMeasurement.chan_adwin_sync = 'adwin_sync'


def calslowpipulse(name):
    m = mbi_espin.ElectronRabi(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO+MBI'])
  
  # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 25
    pts=m.params['pts']
    m.params['MW_pulse_multiplicity'] = 5
      
    # slow pi pulses
    m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 2500
    m.params['AWG_RO_MW_pulse_amps'] = np.linspace(-0.0015, 0.0015, pts)+m.params['AWG_MBI_MW_pulse_amp']
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_ssbmod_frq']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW frq (MHz)'
    m.params['sweep_pts'] = (m.params['AWG_RO_MW_pulse_ssbmod_frqs'] +  m.params['mw_frq'])/1e6
    
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()   