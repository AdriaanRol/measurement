import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

def prepare(m):
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/'+SAMPLE_CFG+'/AdwinSSRO'))
    m.params.from_dict(qt.cfgman.get('protocols/'+SAMPLE_CFG+'/AdwinSSRO-integrated'))
    m.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+espin'))
    m.params.from_dict(qt.cfgman.get('protocols/'+SAMPLE_CFG+'/pulses'))

def finish(m, upload=True, debug=False, **kw):
    m.autoconfig()
    m.generate_sequence(upload=upload, **kw)

    if not debug:
        m.run()
        m.save()
        m.finish()