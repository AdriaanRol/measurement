import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.scripts.teleportation import parameters as tparams

def prepare(m):

    for k in tparams.params.parameters:
        m.params[k] = tparams.params[k]

    for k in tparams.params_lt2.parameters:
        m.params[k] = tparams.params_lt2[k]

    ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']

def finish(m, upload=True, debug=False, **kw):
    m.autoconfig()
    m.generate_sequence(upload=upload, **kw)

    if not debug:
        m.run()
        m.save()
        m.finish()