import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro, pulsar_mbi_espin

def prepare(m):
    m.params.from_dict(qt.cfgman.get('samples/sil2'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO-integrated'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+MBI'))
    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO+MBI'))

    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/pulses'))

    m.params.from_dict(qt.cfgman.get('protocols/sil2-default/BSM'))

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']

    m.params['MW_pulse_mod_risetime'] = 2e-9

def finish(m, upload=True, debug=False):
    m.autoconfig()
    m.generate_sequence(upload=upload)
    
    if not debug:
        m.setup()
        m.run()
        m.save()
        m.finish()