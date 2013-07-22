# class and measurement script sweeping number of pulses after MBI
#
# author: Bas Hensen

import numpy as np
import qt

from measurement.lib.config import awgchannels_lt2 as awgcfg
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


class OpticalPumpSweep(pulsar_msmt.MBI):
    mprefix = 'OpticalPumpSweep'
        
    def generate_sequence(self, upload=True):
        self.chan_nf_aom='AOM_Newfocus'
        self.chan_mwI = 'MW_Imod'
        self.chan_mwQ = 'MW_Qmod'
        self.chan_mw_pm = 'MW_pulsemod'
        self.chan_adwin_sync = 'adwin_sync'
        qt.pulsar.set_channel_opt(self.chan_nf_aom,'high', self.params['AWG_SP_pulse_voltage'])
        
        # MBI element
        e_mbi = self._MBI_element()
        e_spmw = element.Element('sp_mw', pulsar=qt.pulsar)
        e_sp_final =element.Element('sp_final', pulsar=qt.pulsar)
        e_ro = element.Element('readout', pulsar=qt.pulsar)
                
        p_sp=pulse.SquarePulse(self.chan_nf_aom,'sp',
                length=self.params['AWG_SP_pulse_duration'], 
                amplitude=1)
                
        p_mw=pulselib.MW_IQmod_pulse('mw_pi', 
                I_channel=self.chan_mwI, 
                Q_channel=self.chan_mwQ,
                PM_channel=self.chan_mw_pm ,
                PM_risetime=self.params['MW_pulse_mod_risetime'], 
                length = self.params['hard_pi_duration'],
                amplitude = self.params['hard_pi_amp'],
                frequency = self.params['hard_pi_frq'],)
        e_spmw.append(p_sp)
        e_spmw.append(p_mw)
        e_sp_final.append(p_sp)
        
        p_RO=pulselib.MW_IQmod_pulse('readout pulse', 
                I_channel=self.chan_mwI, 
                Q_channel=self.chan_mwQ,
                PM_channel=self.chan_mw_pm ,
                PM_risetime=int(self.params['MW_pulse_mod_risetime']), 
                length = self.params['AWG_RO_MW_pulse_duration'],
                amplitude = self.params['AWG_RO_MW_pulse_amp'],
                frequency = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
        
        p_ROsync=pulse.SquarePulse(self.chan_adwin_sync,'adwin_sync',
                length=self.params['AWG_to_adwin_ttl_trigger_duration'], 
                amplitude=1)
        e_ro.append(p_RO)
        e_ro.append(p_ROsync)
        
        seq = pulsar.Sequence('Nuclear spin flips')
        
        i_last=len(self.params['SP_sweep_repetitions'])-1
        for i,r in enumerate(self.params['SP_sweep_repetitions']):
            
            # 1: MBI 
            seq.append(name = 'MBI-%d' % i, wfname = e_mbi.name,
            trigger_wait = True, goto_target = 'MBI-%d' % i, 
                jump_target = 'sp_mw'+str(i))  
                    
            #2  then repeat (SP+MW pi)-element for the current number of times
            seq.append(name = 'sp_mw'+str(i), wfname=e_spmw.name,
                    repetitions= r,
                    trigger_wait = True)
                        
            # 3 spin pump a final time for the readout:
            seq.append(name = 'sp_final'+str(i), wfname=e_sp_final.name,
                    trigger_wait=False )
            
            seq.append(name='N_ro'+str(i), wfname=e_ro.name,
                trigger_wait=False)
        #print 'uploading'
        #print e_mbi.print_overview()
        #print e_spmw.print_overview()
        #print e_sp_final.print_overview()
        #print e_ro.print_overview()
        if upload:
            qt.pulsar.upload(e_mbi,e_spmw,e_sp_final,e_ro)    
        qt.pulsar.program_sequence(seq)        
                
current_setting = qt.cfgman['protocols']['current']                  
def sweep_optical_pump_cycles(name, init_line=-1, ro_line=-1, pts=11):
    name=name+'_init_'+str(init_line)+'_ro_'+str(ro_line)
    m = OpticalPumpSweep(name)
    
    cfg=qt.cfgman
    m.params.from_dict(cfg['protocols']['AdwinSSRO'])
    m.params.from_dict(cfg['protocols'][current_setting]['AdwinSSRO'])
    m.params.from_dict(cfg['protocols'][current_setting]['AdwinSSRO-integrated'])
    
    m.params.from_dict(cfg['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(cfg['protocols'][current_setting]['AdwinSSRO+MBI'])
    m.params.from_dict(cfg['protocols'][current_setting]['pulses'])

    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500
    m.params['SP_sweep_repetitions']       = np.linspace(1,500,pts).astype('int')
    
    # MW setup

    Nsplit = cfg['samples']['sil9']['N_HF_frq']

    m.params['AWG_MBI_MW_pulse_mod_frq']   = m.params['f0']+init_line*Nsplit

    m.params['AWG_RO_MW_pulse_ssbmod_frq'] =  m.params['f0']++ro_line*Nsplit#XXX
    m.params['AWG_RO_MW_pulse_duration']   =  m.params['pi2pi_mIm1_duration']
    m.params['AWG_RO_MW_pulse_amp']        =  m.params['pi2pi_mIm1_amp']
    
    m.params['AWG_MW_pulse_delay']         =  200e-9
    
    #m.params['AWG_RO_MW_pulse_delay']      =  200
    #SP pulse setup
    
   
    m.params['AWG_SP_pulse_duration']      = 5000e-9
    m.params['AWG_SP_pulse_voltage']       = get_SP_voltage(m) 
    m.params['AWG_SP_pulse_delay']         = 200e-9
    
    #green repump
    m.params['repump_duration'] = m.params['green_repump_duration']
    m.params['repump_amplitude'] = m.params['green_repump_amplitude']
    
    # for the autoanalysis
    m.params['sweep_name'] = 'SP pulse repetitions (#)'
    m.params['sweep_pts'] = m.params['SP_sweep_repetitions']
    
    
    #print m.A_aom.get_power()
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
        