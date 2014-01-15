"""
Script for running Adwin teleportation
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

from measurement.lib.measurement2.adwin_ssro import teleportation

def test_cr_check_only(name):
    m = teleportation.Teleportation('test_cr_check_only_'+name)

    #load the teleportation parameters
    m.params.from_dict(qt.cfgman['protocols']['Teleportation'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['Teleportation'])

    #The only threshold set for the cr_check_only is the preselect.
    m.params['CR_threshold_preselect'] = 90

    #there is no sequence to be loaded for CR check only.
    m.autoconfig()
    m.setup()
    m.run()
    m.save()
    m.finish()