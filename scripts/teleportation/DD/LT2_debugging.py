"""
debugging functions for LDE and the dynamical decoupling used in teleportation
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

import measurement.scripts.espin.CORPSE_tests as CORPSE_tests
reload(CORPSE_tests)

from measurement.scripts.teleportation import parameters as tparams
reload(tparams)
from measurement.scripts.teleportation import sequence as tseq
reload(tseq)

import DD_funcs as funcs
reload(funcs)

name = 'sil10'

def CORPSE_pi2_pi(name):
    """
    Do a pi/2 pulse, followed by a pi-pulse; sweep the time between them.
    """

    m = CORPSE_tests.CORPSE_Pi2_Pi(name)
    funcs.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 5000
    m.params['wait_for_AWG_done'] = 1

    m.params['CORPSE_mod_frq'] = m.params['CORPSE_pi_mod_frq']
    m.params['delays'] = np.linspace(200, 800, pts) * 1e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'delay (ns)'
    m.params['sweep_pts'] = m.params['delays'] * 1e9

    funcs.finish(m, upload=UPLOAD, debug=DEBUG)

def CORPSE_pi2_after_delay(name):
    """
    Do a pi/2 pulse, after some delay.
    """

    m = CORPSE_tests.CORPSE_Pi2_after_delay(name)
    funcs.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 5000
    m.params['wait_for_AWG_done'] = 1

    m.params['CORPSE_mod_frq'] = m.params['CORPSE_pi_mod_frq']
    m.params['delays'] = np.linspace(200, 220, pts) * 1e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'delay (ns)'
    m.params['sweep_pts'] = m.params['delays'] * 1e9

    funcs.finish(m, upload=UPLOAD, debug=DEBUG)

def regular_pi2_after_delay(name):
    """
    Do a pi/2 pulse, after some delay.
    """

    m = CORPSE_tests.regular_Pi2_after_delay(name)
    funcs.prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params['wait_for_AWG_done'] = 1

    m.params['MW_pulse_amplitude'] = 0.8
    m.params['MW_pulse_duration'] = 20e-9
    m.params['MW_pulse_frequency'] = m.params['CORPSE_pi_mod_frq']
    m.params['delays'] = np.linspace(200, 240, pts) * 1e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'delay (ns)'
    m.params['sweep_pts'] = m.params['delays'] * 1e9

    funcs.finish(m, upload=UPLOAD, debug=DEBUG)

def CORPSE_pi_after_delay(name):
    """
    Do a pi pulse, after some delay.
    """

    m = CORPSE_tests.CORPSE_Pi_after_delay(name)
    funcs.prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 2000
    m.params['wait_for_AWG_done'] = 1

    m.params['CORPSE_mod_frq'] = m.params['CORPSE_pi_mod_frq']
    m.params['delays'] = np.linspace(200, 240, pts) * 1e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'delay (ns)'
    m.params['sweep_pts'] = m.params['delays'] * 1e9

    funcs.finish(m, upload=UPLOAD, debug=DEBUG)

def CORPSE_Pi2_Pi_sweep_p2_amp(name):
    """
    Do a pi/2 with and without a pi pulse afterward, sweeping the amplitude of the pi/2.
    """

    m = CORPSE_tests.CORPSE_Pi2_Pi_sweep_p2_amp(name)
    funcs.prepare(m)

    pts = 21
    
    m.params['pts_awg'] = pts
    m.params['pts'] = 2*pts
    m.params['repetitions'] = 5000
    m.params['wait_for_AWG_done'] = 1

    m.params['CORPSE_mod_frq'] = m.params['CORPSE_pi_mod_frq']
    sweep_axis = 0.42+linspace(-0.06,0.06,pts)
    m.params['CORPSE_pi2_sweep_amps'] = sweep_axis
    print sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    funcs.finish(m, upload=UPLOAD, debug=DEBUG)



UPLOAD = True
DEBUG = False

if __name__ == '__main__':
    # CORPSE_pi2_pi(name)
    #CORPSE_pi2_after_delay(name)
    #regular_pi2_after_delay(name)
    # CORPSE_pi_after_delay(name)
    CORPSE_Pi2_Pi_sweep_p2_amp(name)