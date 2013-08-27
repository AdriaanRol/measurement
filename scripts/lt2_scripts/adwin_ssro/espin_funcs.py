import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

def prepare(m):
    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil9-default/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/sil9-default/AdwinSSRO-integrated'))
    m.params.from_dict(qt.cfgman.get('samples/sil9'))

    m.params.from_dict(qt.cfgman.get('protocols/sil9-default/pulses'))

    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+espin'))

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']

def finish(m, upload=True, debug=False, **kw):
    m.autoconfig()
    m.generate_sequence(upload=upload, **kw)

    if not debug:
        m.run()
        m.save()
        m.finish()