"""
LT2 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
from measurement.lib.config import awgchannels_lt2 as awgcfg

from measurement.lib.measurement2.adwin_ssro import sequence

class LDEvsCR(sequence.SequenceSSRO):
    mprefix = 'LDEvsCR'
    
    def setup(self, wait_for_awg=True):
        ssro.IntegratedSSRO.setup(self)
        
        self.awg.set_runmode('SEQ')
        self.awg.start()
        
        if wait_for_awg:
            awg_ready = False
            while not awg_ready:
                try:
                    if self.awg.get_state() == 'Waiting for trigger':
                        awg_ready = True
                except:
                    # usually means awg is still busy and doesn't respond
                    pass
                qt.msleep(0.5)
    
    
    
    def sequence(self):
        
        chan_hhsync = 'HH_sync'         # historically PH_start
        chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
        chan_plusync = 'PLU_gate'
        chan_adwin='ADwin_trigger'
        
        chan_alaser = 'AOM_Newfocus'
        chan_eom = 'EOM_Matisse'
        chan_eom_aom = 'EOM_AOM_Matisse'
        
        self.seq.add_element('lde', goto_target='idle', 
                repetitions= self.params['protocol_reps'] ,
                trigger_wait=True)
                
         # 1: spin pumping
        self.seq.add_pulse('initialdelay', chan_alaser, 'lde',
                start = 0, duration = 10, amplitude=0, )
        self.seq.add_pulse('spinpumping', chan_alaser, 'lde', 
                start = 0, duration = self.params['SP_duration'],
                start_reference='initialdelay',
                link_start_to='end', amplitude=1)
                
        if self.params['long_histogram']:
            self.seq.add_pulse('debug_sync',  chan_hhsync, 'lde',         
                    start = 0, duration = 50, 
                    amplitude = 2.0)        
                
        start_ref='spinpumping'
         # 3a: optical pi-pulse no 1
        i = 1

        #NOTE should be 2.0 amp
        if  self.params['long_histogram']:
            hhsync1_amp=0.0
        else:
            hhsync1_amp=2.0

        self.seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.params['wait_after_sp'], duration = 50, 
                amplitude = hhsync1_amp, start_reference = start_ref,  
                link_start_to = 'end')
        last = 'start'+str(i)

        self.seq.add_pulse('mrkr'+str(i), chan_hh_ma1, 'lde',
                start=-20, duration=50,
                amplitude=2.0, start_reference=last,
                link_start_to='start')

        self.seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        self.seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = self.params['aom_start'], duration = self.params['aom_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_off_amplitude'],
                start = self.params['eom_start'], duration = self.params['eom_off_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_pulse_amplitude'] - self.params['eom_off_amplitude'],
                start = self.params['eom_start']+ self.params['eom_off_duration']/2 + \
                        self.params['eom_pulse_offset'], duration = self.params['eom_pulse_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_overshoot1'],
                start = self.params['eom_start'] + self.params['eom_off_duration']/2 + \
                        self.params['eom_pulse_offset'] + self.params['eom_pulse_duration'], 
                duration = self.params['eom_overshoot_duration1'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_overshoot2'],
                start = self.params['eom_start'] + self.params['eom_off_duration']/2 + \
                        self.params['eom_pulse_offset'] + self.params['eom_pulse_duration'] + \
                        self.params['eom_overshoot_duration1'], 
                duration = self.params['eom_overshoot_duration2'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_off_amplitude'],
                start = self.params['eom_start']+self.params['eom_off_duration'], 
                duration = self.params['eom_off_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_pulse_amplitude'] + self.params['eom_off_amplitude'],
                start = self.params['eom_start']+self.params['eom_off_duration'] + \
                        int(self.params['eom_off_duration']/2) + self.params['eom_pulse_offset'], 
                duration = self.params['eom_pulse_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_overshoot1'], 
                start = self.params['eom_start']+self.params['eom_off_duration'] + \
                        int(self.params['eom_off_duration']/2) + self.params['eom_pulse_offset'] + \
                        self.params['eom_pulse_duration'], 
                duration = self.params['eom_overshoot_duration1'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_overshoot2'], 
                start = self.params['eom_start']+self.params['eom_off_duration'] + \
                        int(self.params['eom_off_duration']/2) + self.params['eom_pulse_offset'] + \
                        self.params['eom_pulse_duration'] + self.params['eom_overshoot_duration1'], 
                duration = self.params['eom_overshoot_duration2'], 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_pulse'+str(i)

        if  self.params['long_histogram']:
            hhsync2_amp=0.0
        else:
            hhsync2_amp=2.0
        i = 2    
            
        self.seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.params['opt_pi_separation'], duration = 50, 
                amplitude = hhsync2_amp, start_reference = 'start'+str(i-1),  
                link_start_to = 'start') 
        last = 'start'+str(i)

        self.seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        self.seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = self.params['aom_start'], duration = self.params['aom_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_off_amplitude'],
                start = self.params['eom_start'], duration = self.params['eom_off_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_pulse_amplitude'] - self.params['eom_off_amplitude'],
                start = self.params['eom_start'] + self.params['eom_off_duration']/2 + \
                        self.params['eom_pulse_offset'], duration = self.params['eom_pulse_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_overshoot1'],
                start = self.params['eom_start'] + self.params['eom_off_duration']/2 + \
                        self.params['eom_pulse_offset'] + self.params['eom_pulse_duration'], 
                duration = self.params['eom_overshoot_duration1'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = self.params['eom_overshoot2'],
                start = self.params['eom_start'] + self.params['eom_off_duration']/2 + \
                        self.params['eom_pulse_offset'] + self.params['eom_pulse_duration'] + \
                        self.params['eom_overshoot_duration1'], 
                duration = self.params['eom_overshoot_duration2'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_off_amplitude'],
                start = self.params['eom_start']+self.params['eom_off_duration'], 
                duration = self.params['eom_off_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_pulse_amplitude'] + self.params['eom_off_amplitude'],
                start = self.params['eom_start']+self.params['eom_off_duration'] + \
                        int(self.params['eom_off_duration']/2) + self.params['eom_pulse_offset'], 
                duration = self.params['eom_pulse_duration'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_overshoot1'], 
                start = self.params['eom_start']+self.params['eom_off_duration'] + \
                        int(self.params['eom_off_duration']/2) + self.params['eom_pulse_offset'] + \
                        self.params['eom_pulse_duration'], 
                duration = self.params['eom_overshoot_duration1'], 
                start_reference = last, link_start_to = 'start')

        self.seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -self.params['eom_overshoot2'], 
                start = self.params['eom_start']+self.params['eom_off_duration'] + \
                        int(self.params['eom_off_duration']/2) + self.params['eom_pulse_offset'] + \
                        self.params['eom_pulse_duration'] + self.params['eom_overshoot_duration1'], 
                duration = self.params['eom_overshoot_duration2'], 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_pulse'+str(i)                   
                    
        self.seq.add_pulse('final delay', chan_hhsync, 'lde',
                amplitude = 0,
                duration = self.params['finaldelay'],
                start = 0,
                start_reference = last,
                link_start_to = 'end' )

        # idle element
        self.seq.add_element('idle', goto_target='lde')
        self.seq.add_pulse('empty', chan_alaser, 'idle', start=0, duration = 200, 
            amplitude = 0)
        self.seq.add_pulse('trigger_adwin', chan_adwin, 'idle', start=50,
            start_reference='empty',link_start_to='end', duration = 2000, amplitude = 1)
            
            
            
current_setting = qt.cfgman['protocols']['current'] 
def lde_protocol_reps_vs_CR(name):
                  
    m = LDEvsCR(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO-integrated'])
    
    _set_repump_settings(m,False)
    
    m.params['long_histogram']=False
    
    m.params['eom_pulse_duration']        = 3
    m.params['eom_pulse_offset']          = 0    

    m.params['eom_aom_amplitude']         = 1.0
    m.params['eom_off_amplitude']         = -.25 #NOTE
    m.params['eom_pulse_amplitude']       = 1.2
    m.params['eom_overshoot_duration1']   = 10
    m.params['eom_overshoot1']            = -0.03
    m.params['eom_overshoot_duration2']   = 4
    m.params['eom_overshoot2']            = -0.03
    m.params['eom_start']                 = 40
    m.params['eom_off_duration']          = 300 #NOTE: change this to duration of CORPSE or regular!
    m.params['pulse_start']               = m.params['eom_start'] + m.params['eom_off_duration']/2 + \
                                            m.params['eom_pulse_offset']
    m.params['aom_start']                 = m.params['pulse_start'] -5 -66 #subtract aom rise time
    m.params['aom_duration']              = 2*23+m.params['eom_pulse_duration'] #30XXX
    m.params['rabi_cycle_duration']       = 2*m.params['eom_off_duration']
    m.params['wait_after_opt_pi']         = 280-40 # 280 for regular, determines start of MW pi pulse NOTE: change this for regular pulses!
    m.params['wait_after_opt_pi2_lt1']    = 220-80+132#164 for regular# determines start of b
    m.params['wait_after_opt_pi2_lt2']    = 238-80+114#114 for regular # determines start of basis rotation NOTE: change this for regular pulses!
    m.params['opt_pi_separation']         = 2*m.params['eom_off_duration']
    m.params['A_SP_power']                = 20e-9 
    m.params['A_SP_amplitude']            = m.A_aom.power_to_voltage(m.params['A_SP_power'])
    m.params['wait_after_sp']             = 500
    m.params['finaldelay']                = 1000
    m.params['SP_duration']               = 9000 #changed this for second spin photon try
    
    m.params['SSRO_repetitions'] = 1000
    m.params['protocol_reps_sweep'] = np.linspace(1,100,10)
    m.params['send_AWG_start'] = 1
    m.params['wait_for_AWG_done'] = 1
    m.params['pts'] = 1
    m.params['repetitions'] = m.params['SSRO_repetitions'] 
     
    m.awgcfg_args=['hydraharp']
    m.awgcfg_kws={'optical_rabi' : { 
                'EOM_AOM_Matisse' : { 'high' :  m.params['eom_aom_amplitude'] },
                'AOM_Newfocus': { 'high' : m.params['A_SP_amplitude'], }
                }}
    
    m.params['protocol_reps'] = 1
    m.autoconfig()
    #for r in m.params['protocol_reps_sweep']:
    #    if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
    #    m.params['protocol_reps'] = r
    #    m.generate_sequence()
    #    m.run()
    #    m.save('reps_%d' % (r))
    m.generate_sequence()
    m.run()    
    m.save()
    m.finish()
    
    
def _set_repump_settings(m,yellow):
    if yellow:
        qt.instruments['GreenAOM'].set_power(0)
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=1
        m.params['repump_after_repetitions']=100
    else:
        qt.instruments['YellowAOM'].set_power(0)
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']