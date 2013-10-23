import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro, pulsar_mbi_espin
from measurement.scripts.teleportation import parameters as tparams

def prepare(m, sil_name):

    for k in tparams.params.parameters:
        m.params[k] = tparams.params[k]

    for k in tparams.params_lt1.parameters:
        m.params[k] = tparams.params_lt1[k]

    ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']

def finish(m, upload=True, debug=False):
    m.autoconfig()

    m.params['A_SP_durations'] = [tparams.params_lt1['repump_after_MBI_duration']]
    m.params['A_SP_amplitudes'] = [tparams.params_lt1['repump_after_MBI_amplitude']]
    m.params['E_RO_durations'] = [tparams.params_lt1['SSRO1_duration']]
    m.params['E_RO_amplitudes'] = [tparams.params_lt1['E_RO_amplitude']]
    m.params['send_AWG_start'] = [1]
    m.params['sequence_wait_time'] = [0]
    
    m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()