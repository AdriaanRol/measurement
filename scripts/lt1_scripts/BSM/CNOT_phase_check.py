import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)

import mbi_espin_funcs as funcs
reload(funcs)


class CNOTPhaseCheck(BSM.NReadoutMsmt):
    mprefix = 'CNOTPhaseCheck'

    def get_sweep_elements(self):        
        elts = []

        for i in range(self.params['pts']):
            e = element.Element('CNOTPHaseCheck_pt-{}'.format(i), pulsar=qt.pulsar, global_time = True)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(self.T)
            e.append(self.N_pi2)
            e.append(pulse.cp(self.T, length=200e-9))
            for m in np.arange(self.params['multiplicity']/2):
                if m == 0:
                    e.append(self.pi2pi_m1)
                    e.append(self.TIQ)
                    e.append(self.pi2pi_m1)
                else:
                    e.append(self.TIQ)
                    e.append(self.pi2pi_m1)
                    e.append(self.TIQ)
                    e.append(self.pi2pi_m1)
            e.append(pulse.cp(self.T, length=200e-9))
            e.append(pulse.cp(self.N_pi2, 
                phase = self.params['analysis_phases'][i]))

            elts.append(e)

        return elts

class CNOTPhaseCheckSweepTime(BSM.NReadoutMsmt):
    mprefix = 'CNOTPhaseCheckSweepTime'

    def get_sweep_elements(self):        
        elts = []

        for i in range(self.params['pts']):
            e = element.Element('CNOTPHaseCheck_pt-{}'.format(i), pulsar=qt.pulsar, global_time = True)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(self.T)
            e.append(self.N_pi2)
            e.append(pulse.cp(self.T, length=200e-9))
            e.append(self.pi2pi_m1)
            e.append(self.TIQ)
            e.append(self.pi2pi_m1)
            e.append(pulse.cp(self.T, length = self.params['CNOT_to_pi2_time'][i]))
            e.append(self.N_pi2)

            elts.append(e)

        return elts

class CNOTPhaseCheckSweepCNOTphase(BSM.NReadoutMsmt):
    mprefix = 'CNOTPhaseCheckSweepCNOTphase'

    def get_sweep_elements(self):        
        elts = []

        for i in range(self.params['pts']):
            e = element.Element('CNOTPHaseCheck_pt-{}'.format(i), pulsar=qt.pulsar, global_time = True)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(self.T)
            e.append(self.N_pi2)
            e.append(pulse.cp(self.T, length=200e-9))
            e.append(pulse.cp(self.pi2pi_m1, phase = self.params['CNOT_phase'][i]))
            e.append(self.TIQ)
            e.append(self.pi2pi_m1)
            e.append(pulse.cp(self.T, length = 200e-9))
            e.append(self.N_pi2)

            elts.append(e)

        return elts

class CNOTPhaseCheckBothPi2Phases(BSM.NReadoutMsmt):
    mprefix = 'CNOTPhaseCheck_BothPi2Phases'

    def get_sweep_elements(self):        
        elts = []

        for i in range(self.params['pts']):
            e = element.Element('CNOTPHaseCheck_pt-{}'.format(i), pulsar=qt.pulsar, global_time = True)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(self.T)
            e.append(pulse.cp(self.N_pi2, 
                phase = self.params['prepare_phases'][i]))
            e.append(pulse.cp(self.T, length=200e-9))
            e.append(self.pi2pi_m1)
            e.append(self.TIQ)
            e.append(self.pi2pi_m1)
            e.append(pulse.cp(self.T, length=200e-9))
            e.append(pulse.cp(self.N_pi2, 
                phase = self.params['analysis_phases'][i]))

            elts.append(e)

        return elts

class CNOTPhaseCheckmI0BothPi2Phases(BSM.NReadoutMsmt):
    mprefix = 'CNOTPhaseCheck_mI0_BothPi2Phases'

    def get_sweep_elements(self):        
        elts = []

        for i in range(self.params['pts']):
            e = element.Element('CNOTPHaseCheck_pt-{}'.format(i), pulsar=qt.pulsar, global_time = True)
            e.append(self.T)
            e.append(self.shelving_pulse)
            e.append(self.T)
            e.append(pulse.cp(self.N_pi2, 
                phase = self.params['prepare_phases'][i]))
            e.append(pulse.cp(self.T, length=200e-9))
            e.append(self.pi2pi_0)
            e.append(pulse.cp(self.TIQ, length = 456e-9 - 406e-9)) #=1/A - 2*1/2*pi2pi
            e.append(self.pi2pi_0)
            e.append(pulse.cp(self.T, length=200e-9))
            e.append(pulse.cp(self.N_pi2, 
                phase = self.params['analysis_phases'][i]))

            elts.append(e)

        return elts

def CNOT_phase_check():
    m = CNOTPhaseCheck('2_times_CNOT')
    BSM.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # MW pulses
    m.params['multiplicity'] = 2 #number of CNOT pulses
    m.params['analysis_phases'] = np.linspace(0,360,pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'second pi/2 phase'
    m.params['sweep_pts'] = m.params['analysis_phases']
    
    funcs.finish(m, debug=False, upload=True)

def CNOT_phase_check_sweep_time():
    m = CNOTPhaseCheckSweepTime('CNOT_to_pi2')
    BSM.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # MW pulses
    m.params['CNOT_to_pi2_time'] = np.linspace(150e-9,250e-9,pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'second_CNOT_to_pi2_time'
    m.params['sweep_pts'] = m.params['CNOT_to_pi2_time']
    
    funcs.finish(m, debug=False, upload=True)

def CNOT_phase_check_sweep_CNOT_phase():
    m = CNOTPhaseCheckSweepCNOTphase('CNOT_phase')
    BSM.prepare(m)

    pts = 17
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # MW pulses
    m.params['CNOT_phase'] = np.linspace(0,360,pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'first CNOT phase'
    m.params['sweep_pts'] = m.params['CNOT_phase']
    
    funcs.finish(m, debug=False, upload=True)

def CNOT_phase_check_both_pi2_phases():
    m = CNOTPhaseCheckBothPi2Phases('pi2_phases_sweep_both')
    BSM.prepare(m)

    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # MW pulses
    m.params['analysis_phases'] = - 62 + np.linspace(0,360,pts)
    m.params['prepare_phases'] = - m.params['analysis_phases']

    # for the autoanalysis
    m.params['sweep_name'] = 'second pi/2 phase'
    m.params['sweep_pts'] = m.params['analysis_phases']
    
    funcs.finish(m, debug=False, upload=True)

def CNOT_phase_check_mI0_both_pi2_phases():
    m = CNOTPhaseCheckmI0BothPi2Phases('mI0_pi2_phases_sweep_both')
    BSM.prepare(m)

    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    # MW pulses
    m.params['analysis_phases'] = - 62 + np.linspace(0,360,pts)
    m.params['prepare_phases'] = - m.params['analysis_phases']

    # for the autoanalysis
    m.params['sweep_name'] = 'second pi/2 phase'
    m.params['sweep_pts'] = m.params['analysis_phases']
    
    funcs.finish(m, debug=False, upload=True)


if __name__ == '__main__':
    CNOT_phase_check()
    #CNOT_phase_check_sweep_time()
    #CNOT_phase_check_sweep_CNOT_phase()
    #CNOT_phase_check_both_pi2_phases()
    #CNOT_phase_check_mI0_both_pi2_phases()