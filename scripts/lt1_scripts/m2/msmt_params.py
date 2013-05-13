import types
import qt
cfg = qt.cfgman

### protocol settings ###
p_cfg = cfg['protocols']

### ADwin SSRO protocols
try: 
    if type(p_cfg['AdwinSSRO']) == types.NoneType:
        p_cfg['AdwinSSRO'] = {}
except KeyError:
    p_cfg['AdwinSSRO'] = {}
_cfg = p_cfg['AdwinSSRO']

_cfg['AWG_done_DI_channel'] = 16
_cfg['AWG_event_jump_DO_channel'] = 7
_cfg['AWG_start_DO_channel'] = 1
_cfg['A_laser_DAC_channel'] = 6
_cfg['Ex_laser_DAC_channel'] = 7
_cfg['counter_channel'] = 1
_cfg['cycle_duration'] = 300
_cfg['green_laser_DAC_channel'] = 4
_cfg['green_off_amplitude'] = 0.0
_cfg['green_repump_amplitude'] = 100e-6
_cfg['green_repump_duration'] = 10
_cfg['send_AWG_start'] = 0
_cfg['sequence_wait_time'] = 1
_cfg['wait_after_RO_pulse_duration'] = 3
_cfg['wait_after_pulse_duration'] = 3
_cfg['wait_for_AWG_done'] = 0



### more specfic settings

### settings for sil2-default ###
kw = 'sil2-default'

if type(p_cfg[kw]) == types.NoneType:
    p_cfg[kw] = {}
sp_cfg = p_cfg[kw]

### Adwin SSRO settings for sil2-default ###
try:
    if type(sp_cfg['AdwinSSRO']) == types.NoneType:
        sp_cfg['AdwinSSRO'] = {}
except KeyError:
    sp_cfg['AdwinSSRO'] = {}
_cfg = sp_cfg['AdwinSSRO']

_cfg['A_CR_amplitude'] = 10e-9
_cfg['A_RO_amplitude'] = 0.
_cfg['A_SP_amplitude'] = 10e-9
_cfg['CR_duration'] = 100
_cfg['CR_preselect'] = 40
_cfg['CR_probe'] = 40
_cfg['Ex_CR_amplitude'] = 10e-9
_cfg['Ex_RO_amplitude'] = 2e-9
_cfg['Ex_SP_amplitude'] = 0.
_cfg['SP_duration'] = 250
_cfg['SP_filter_duration'] = 0
_cfg['SSRO_duration'] = 50
_cfg['SSRO_repetitions'] = 5000
_cfg['SSRO_stop_after_first_photon'] = 0


### Adwin MBI settings for sil2-default ###
pstring = 'AdwinSSRO+MBI'
try:
    if type(sp_cfg[pstring]) == types.NoneType:
        sp_cfg[pstring] = {}
except KeyError:
    sp_cfg[pstring] = {}
_cfg = sp_cfg[pstring]

_cfg['AWG_wait_duration_before_MBI_MW_pulse'] = 1000
_cfg['Ex_MBI_amplitude'] = 2e-9
_cfg['MBI_duration'] = 5
_cfg['SP_E_duration'] = 100
_cfg['AWG_MBI_MW_pulse_ssbmod_frq'] = 43.862e6 - 2.189e6



cfg.save_all()
