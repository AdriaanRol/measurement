"""
LT1 script for e-spin manipulations
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import measurement.lib.config.awgchannels as awgcfg

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import sequence

# set the static variables for LT1
ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt1_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['Velocity2AOM']
ssro.AdwinSSRO.A_aom = qt.instruments['Velocity1AOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']

sequence.SequenceSSRO.awg = qt.instruments['AWG']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100']
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['mw', 'rf', 'adwin']

def darkesr(name):
    m = sequence.DarkESR(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    
    m.params['mw_frq'] = 2.8e9
    m.params['ssbmod_frq_start'] = 40e6
    m.params['ssbmod_frq_stop'] = 48e6
    m.params['pts'] = 81
    m.params['mw_power'] = 20
    m.params['pulse_length'] = 2000 
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.01
    m.params['MW_pulse_mod_risetime'] = 2
    
    m.autoconfig()
    m.generate_sequence()
    m.run()
    m.save()
    m.finish()   
   
