import qt
import numpy as np

#reload all parameters and modules
execfile(qt.reload_current_setup)

from measurement.lib.measurement2.adwin_ssro import ssro, pulsar_mbi_espin

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def prepare(m, sil_name=SAMPLE):
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

def finish(m, upload=True, debug=False):
    m.autoconfig()

    m.params['E_RO_durations'] = [m.params['SSRO_duration']]
    m.params['E_RO_amplitudes'] = [m.params['Ex_RO_amplitude']]
    m.params['send_AWG_start'] = [1]
    m.params['sequence_wait_time'] = [0]
    m.generate_sequence(upload=upload)

    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()

