import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro, pulsar_mbi_espin

def prepare(m, yellow = False):
    m.params.from_dict(qt.cfgman.get('samples/sil2'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO-integrated'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+MBI'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO+MBI'))

    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/pulses'))

    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/BSM'))

    if yellow:
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=m.params['yellow_CR_repump']
        m.params['repump_after_repetitions']=m.params['yellow_repump_after_repetitions']
    else:
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']
        m.params['CR_repump']=m.params['green_CR_repump']
        m.params['repump_after_repetitions']=m.params['green_repump_after_repetitions']

def finish(m, upload=True, debug=False):
    m.autoconfig()
    m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()