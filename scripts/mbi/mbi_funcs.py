import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro, pulsar_mbi_espin

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

def prepare(m, sil_name=SAMPLE, yellow=False):
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/'+SAMPLE_CFG+'/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/'+SAMPLE_CFG+'/AdwinSSRO-integrated'))
    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+MBI'))
    m.params.from_dict(qt.cfgman.get('protocols/'+SAMPLE_CFG+'/AdwinSSRO+MBI'))
    m.params.from_dict(qt.cfgman.get('protocols/'+SAMPLE_CFG+'/pulses'))
    # m.params.from_dict(qt.cfgman.get('protocols/hans-sil4-default/BSM'))

    if yellow:
        ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.yellow_aom
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=m.params['yellow_CR_repump']
        m.params['repump_after_repetitions']=m.params['yellow_repump_after_repetitions']
    else:
        ssro.AdwinSSRO.repump_aom =  ssro.AdwinSSRO.green_aom
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']
        m.params['CR_repump']=m.params['green_CR_repump']
        m.params['repump_after_repetitions']=m.params['green_repump_after_repetitions']

def finish(m, upload=True, debug=False):
    m.autoconfig()

    m.params['A_SP_durations'] = [m.params['repump_after_MBI_duration']]
    m.params['A_SP_amplitudes'] = [m.params['repump_after_MBI_amplitude']]
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