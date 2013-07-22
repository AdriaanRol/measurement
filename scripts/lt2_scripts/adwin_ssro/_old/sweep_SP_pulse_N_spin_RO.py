# class and measurement script sweeping number of pulses after MBI
#
# author: Bas Hensen

import numpy as np
import qt
from measurement.lib.measurement2.adwin_ssro import mbi

class OpticalPumpSweep(mbi.MBIMeasurement):
    mprefix = 'OpticalPumpSweep'
    
    def sequence(self):
        for i in np.arange(self.params['pts']):
            
            # 1: MBI 
            self._MBI_seq_element(el_name='MBI_pulse'+str(i),
                jump_target='spin_control'+str(i),
                goto_target='MBI_pulse'+str(i)+'-0')
            
            #2: Wait for trigger
            self.seq.add_element(name = 'spin_control_wait'+str(i), 
                trigger_wait = True)
            
            self.seq.add_pulse('wait_pulse', 
                    self.chan_nf_aom, 
                    element = 'spin_control_wait'+str(i),
                    duration = self.params['AWG_wait_element_duration'],
                    amplitude = 0)
                    
            #3  then repeat (SP+MW pi)-element for the current number of times
            if self.params['SP_sweep_repetitions'][i] > 0:
                self.seq.add_element(name = 'spin_control'+str(i), 
                        repetitions= self.params['SP_sweep_repetitions'][i]) #XXXXXXXXXXXXX
                
                self.seq.add_pulse('SP_pulse', 
                        self.chan_nf_aom, 
                        element = 'spin_control'+str(i),
                        duration = self.params['AWG_SP_pulse_duration'],
                        amplitude = self.params['AWG_SP_pulse_voltage'],
                        start = self.params['AWG_SP_pulse_delay'])
                
                self.seq.add_IQmod_pulse(name = 'MW_pulse',
                        channel = (self.chan_mwI,self.chan_mwQ),
                        element = 'spin_control'+str(i),
                        start = self.params['AWG_MW_pulse_delay'], 
                        duration = int(self.params['AWG_MW_pulse_duration']),
                        amplitude = self.params['AWG_MW_pulse_amp'],
                        frequency = self.params['AWG_MW_pulse_ssbmod_frq'],
                        start_reference = 'SP_pulse',
                        link_start_to = 'end')           
                
                self.seq.clone_channel(self.chan_mw_pm, self.chan_mwI, 'spin_control'+str(i),
                    start = -self.params['MW_pulse_mod_risetime'],
                    duration = 2 * self.params['MW_pulse_mod_risetime'], 
                    link_start_to = 'start', 
                    link_duration_to = 'duration',
                    amplitude = 2.0)
                    
            # 4 spin pump a final time for the readout:
            self.seq.add_element(name = 'spin_control_final_sp'+str(i))
            self.seq.add_pulse('SP_pulse', 
                    self.chan_nf_aom, 
                    element = 'spin_control_final_sp'+str(i),
                    duration = self.params['AWG_SP_pulse_duration'],
                    amplitude = self.params['AWG_SP_pulse_voltage'],
                    start = self.params['AWG_SP_pulse_delay'])
                    
            # 5: then N-spin readout MW pulse
            self._N_RO_seq_element('n_ro'+str(i), 'MBI_pulse0-0', i, self.params['pts'], trigger_wait=False)
                
                
current_setting = qt.cfgman['protocols']['current']                  
def sweep_optical_pump_cycles(name):

    m = OpticalPumpSweep(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO-integrated'])
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO+MBI'])

    pts = 20
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1
    
    # MW setup
    m.params['AWG_MW_pulse_duration']      =  200
    m.params['AWG_MW_pulse_amp']           =  0.17
    m.params['AWG_MW_pulse_ssbmod_frq']    =  qt.cfgman['samples']['sil9']['ms-1_cntr_frq'] \
                                                    - m.params['mw_frq']
    m.params['AWG_MW_pulse_delay']         =  200
    
    m.params['AWG_RO_MW_pulse_ssbmod_frq'] =  m.params['AWG_MBI_MW_pulse_ssbmod_frq']#XXX
    m.params['AWG_RO_MW_pulse_duration']   =  m.params['AWG_MBI_MW_pulse_duration']
    m.params['AWG_RO_MW_pulse_amp']        =  m.params['AWG_MBI_MW_pulse_amp']

    #m.params['AWG_RO_MW_pulse_delay']      =  200
    #SP pulse setup
    
    m.params['AWG_wait_element_duration']  = 200
    m.params['SP_sweep_repetitions']       = np.linspace(0,200,pts).astype('int')
    m.params['AWG_SP_pulse_duration']      = 250000
    m.params['AWG_SP_pulse_voltage']       = get_SP_voltage(m) 
    m.params['AWG_SP_pulse_delay']         = 200
    
    #green repump
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'SP pulse repetitions (#)'
    m.params['sweep_pts'] = m.params['SP_sweep_repetitions']
    
    #go
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()
    m.save()
    m.finish()
    
    
def get_SP_voltage(m):
    ret=0.0
    if m.A_aom.get_cur_controller()=='AWG':
        ret= m.A_aom.power_to_voltage(m.params['A_SP_amplitude'])
    else:
        m.A_aom.apply_voltage(0)
        m.A_aom.set_cur_controller('AWG')
        ret = m.A_aom.power_to_voltage(m.params['A_SP_amplitude'])
        m.A_aom.set_cur_controller('ADWIN')
    return ret
    
    