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
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

class EOMAOMPulse(pulse.Pulse):
    def __init__(self, eom_channel, aom_channel, name, **kw):
        pulse.Pulse.__init__(self, name)
        self._eom_channel = eom_channel
        self._aom_channel = aom_channel

        self.channels=[eom_channel,aom_channel] 
                                               
        self.eom_pulse_duration        = kw.pop('eom_pulse_duration'                ,2) 
        self.eom_off_duration          = kw.pop('eom_off_duration'                  ,300)
        self.eom_off_amplitude         = kw.pop('eom_off_amplitude'                 ,-.25) #NOTE
        self.eom_pulse_amplitude       = kw.pop('eom_pulse_amplitude'               ,1.2)
        self.eom_overshoot_duration1   = kw.pop('eom_overshoot_duration1'           ,14)
        self.eom_overshoot1            = kw.pop('eom_overshoot1'                    ,-0.03)
        self.eom_overshoot_duration2   = kw.pop('eom_overshoot_duration2'           ,0)
        self.eom_overshoot2            = kw.pop('eom_overshoot2'                    ,-0.03)
        self.timebase                  = kw.pop('eom_timebase'                      ,1e-9)
        self.aom_risetime              = kw.pop('aom_risetime'                      ,23)
        
        self.length=2.*(self.eom_off_duration+self.eom_pulse_duration+\
            self.eom_overshoot_duration1+self.eom_overshoot_duration2)*self.timebase 
                                                     
        
    def __call__(self):
        return self
        
       
    def wf(self, tvals):#IMPLEMENT
        
        self._t0=self._t0-self.eom_off_duration/2*self.timebase
        #print len(tvals), 2*(self.eom_off_duration+self.eom_pulse_duration+\
        #        self.eom_overshoot_duration1+self.eom_overshoot_duration2)
        if len(tvals)!=2*(self.eom_off_duration+self.eom_pulse_duration+\
                self.eom_overshoot_duration1+self.eom_overshoot_duration2):
            raise(Exception('error in eom waveform timebase: EOM pulse currently only supports ns timebase.'))
        
        eom_wf=np.zeros(0)
        eom_wf=np.append(eom_wf,np.ones(self.eom_off_duration/2)*self.eom_off_amplitude)
        eom_wf=np.append(eom_wf,np.ones(self.eom_pulse_duration)*self.eom_pulse_amplitude)
        eom_wf=np.append(eom_wf,np.ones(self.eom_overshoot_duration1)*self.eom_overshoot1)
        eom_wf=np.append(eom_wf,np.ones(self.eom_overshoot_duration2)*self.eom_overshoot2)
        eom_wf=np.append(eom_wf,np.ones(self.eom_off_duration/2)*self.eom_off_amplitude)
        #compensation_pulse
        eom_wf=np.append(eom_wf,-eom_wf)
        
        aom_wf=np.zeros(self.eom_off_duration/2-self.aom_risetime)
        aom_wf=np.append(aom_wf,np.ones(2*self.aom_risetime+self.eom_pulse_duration))
        aom_wf=np.append(aom_wf,np.zeros(len(tvals)-len(aom_wf)))
        

        return {
            self._eom_channel : eom_wf,
            self._aom_channel : aom_wf,
            }

class LDEvsCR(pulsar_msmt.PulsarMeasurement):
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
                    print 'wait for awg, usually means awg is still busy and doesnt respond'
                    pass
                qt.msleep(0.5)
    
    
    
    def generate_sequence(self,upload=True):
        #rewrite
        chan_hhsync = 'HH_sync'         # historically PH_start
        chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
        chan_plusync = 'PLU_gate'
        chan_adwin='adwin_sync'
        
        chan_alaser = 'AOM_Newfocus'
        chan_yellowlaser = 'AOM_Yellow'
        chan_eom = 'EOM_Matisse'
        chan_eom_aom = 'EOM_AOM_Matisse'
        
        qt.pulsar.set_channel_opt(chan_alaser,'high', self.params['AWG_A_SP_voltage'])
        qt.pulsar.set_channel_opt(chan_yellowlaser,'high', self.params['AWG_yellow_voltage'])
        
        e_lde = element.Element('lde', pulsar=qt.pulsar)
        
        # 1: spin pumping
        p_wait=pulse.SquarePulse(chan_alaser, 'initialdelay',
                length = 10e-9, amplitude = 0)
        last=e_lde.add(p_wait)
        
        p_sp=pulse.SquarePulse(chan_alaser, 'spinpumping',
                length = self.params['AWG_SP_duration'], amplitude = 1)
        p_yellow=pulse.SquarePulse(chan_yellowlaser, 'yellowpumping',
                length = self.params['AWG_yellow_duration'], amplitude = 1)
        e_lde.add(p_yellow, refpulse=last, refpoint='end')
        last=e_lde.add(p_sp, refpulse=last, refpoint='end')
        
        p_sync=pulse.SquarePulse(chan_hhsync,'debug_sync',        
                length = 50e-9, amplitude = 1)      
        p_hh_marker=pulse.SquarePulse(chan_hh_ma1, 'hh_marker', length=50e-9,
                amplitude=1)
        P_eom_aom=EOMAOMPulse(chan_eom,chan_eom_aom,'opt_pi',**self.eom_pars)
        
        # opt pi 1
        i = 1
        if self.params['long_histogram']:
            e_lde.add(p_sync)
            hhsync_amp=0
        else:
            hhsync_amp=1
            
        last=e_lde.add(pulse.cp(p_sync(amplitude=hhsync_amp)),name='start'+str(i), t0= self.params['wait_after_sp'],
                refpulse=last, refpoint='end')   
        e_lde.add(p_hh_marker,name='mrkr'+str(i), t0 = -20e-9,
                refpulse=last, refpoint='start') 
        last=e_lde.add(pulse.cp(p_sync(amplitude=0)),name='start'+str(i)+'delay',
                refpulse=last, refpoint='end') 
        

        last=e_lde.add(P_eom_aom, name='eom_pulse'+str(i), t0= self.params['eom_start'],
                refpulse=last, refpoint = 'start')
        
        # opt pi 2
        
        i = 2    
            
        last=e_lde.add(pulse.cp(p_sync(amplitude=hhsync_amp)),name='start'+str(i), t0= self.params['opt_pi_separation'],
                refpulse='start'+str(i-1), refpoint='start')  
        last=e_lde.add(pulse.cp(p_sync(amplitude=0)),name='start'+str(i)+'delay',
                refpulse=last, refpoint='end') 
        
        last=e_lde.add(P_eom_aom, name='eom_pulse'+str(i), t0= self.params['eom_start'],
                refpulse=last, refpoint = 'start')
        

        #final delay
        e_lde.add(pulse.cp(p_wait(length=self.params['finaldelay'])), refpulse=last, refpoint = 'end')

        # idle element
        e_idle=element.Element('idle', pulsar=qt.pulsar)
        last=e_idle.add(pulse.cp(p_wait(length=200e-9)))
        p_adwin=pulse.SquarePulse(chan_adwin,'adwin_sync',        
                length = 2000e-9, amplitude = 1) 
        e_idle.add(p_adwin, refpulse=last, refpoint = 'end', t0 = 50e-9)
                    
        
        seq = pulsar.Sequence('LDE protocol test sequence wo MW')
        
        
        for i,r in enumerate(self.params['protocol_reps_sweep']):
            #print i, r
            seq.append(name = 'LDE-%d' % i, wfname = e_lde.name, 
                trigger_wait = True,
                repetitions=r)
            
            seq.append(name = 'wait-%d' % i, wfname = e_idle.name, 
                trigger_wait = False)
        if upload:
            qt.pulsar.upload(e_lde,e_idle)
        qt.pulsar.program_sequence(seq)
        
current_setting = qt.cfgman['protocols']['current'] 
def lde_protocol_reps_vs_CR(name,yellow=False):
                  
    m = LDEvsCR(name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][current_setting]['AdwinSSRO-integrated'])
    
    _set_repump_settings(m,yellow)
    
    m.params['long_histogram']=False
    
    m.eom_pars={}
    m.eom_pars['eom_pulse_duration']        = 2
    m.eom_pars['eom_pulse_offset']          = 0    
    
    m.eom_pars['eom_aom_amplitude']         = 1.0
    m.eom_pars['eom_off_amplitude']         = -.25 #NOTE
    m.eom_pars['eom_pulse_amplitude']       = 1.2
    m.eom_pars['eom_overshoot_duration1']   = 10
    m.eom_pars['eom_overshoot1']            = -0.29
    m.eom_pars['eom_overshoot_duration2']   = 4
    m.eom_pars['eom_overshoot2']            = -0.29
    
    m.eom_pars['eom_off_duration']          = 300 #NOTE: change this to duration of CORPSE or regular!
    m.eom_pars['aom_risetime']              = 12 #subtract aom rise time
    m.params.from_dict(m.eom_pars)
    m.params['eom_start']                 = 190e-9
    m.params['rabi_cycle_duration']       = 2*m.params['eom_off_duration']*1e-9
    m.params['wait_after_opt_pi']         = 280-40 # 280 for regular, determines start of MW pi pulse NOTE: change this for regular pulses!
    m.params['wait_after_opt_pi2_lt1']    = 220-80+132#164 for regular# determines start of b
    m.params['wait_after_opt_pi2_lt2']    = 238-80+114#114 for regular # determines start of basis rotation NOTE: change this for regular pulses!
    m.params['opt_pi_separation']         = 2*m.params['eom_off_duration']*1e-9
    m.params['AWG_A_SP_power']            = 170e-9 
    m.params['AWG_A_SP_voltage']          = get_AWG_AOM_voltage(m.A_aom,m.params['AWG_A_SP_power'] )
    m.params['AWG_yellow_power']          = 300e-9#m.params['yellow_repump_amplitude'] if yellow else 0
    m.params['AWG_yellow_voltage']        = get_AWG_AOM_voltage(qt.instruments['YellowAOM'],m.params['AWG_yellow_power'])
    m.params['wait_after_sp']             = 500e-9
    m.params['finaldelay']                = 1000e-9
    m.params['AWG_SP_duration']           = 9000e-9 #changed this for second spin photon try
    m.params['AWG_yellow_duration']       = 9000e-9 #changed this for second spin photon try
     
    m.params['Ex_RO_amplitude']            = 0
    m.params['SSRO_repetitions'] = 1000
    m.params['send_AWG_start'] = 1
    m.params['wait_for_AWG_done'] = 1
    
    m.params['repetitions'] = m.params['SSRO_repetitions'] 
     
    m.awgcfg_args=['hydraharp']
    m.awgcfg_kws={'optical_rabi' : { 
                'EOM_AOM_Matisse' : { 'high' :  m.params['eom_aom_amplitude'] },
                'AOM_Newfocus': { 'high' : m.params['A_SP_amplitude'], }
                }}
    
    m.params['protocol_reps_sweep'] = [1,50,100,500,1000,5000,10000,50000]
    m.params['pts'] = len(m.params['protocol_reps_sweep'])
    
    m.params['sweep_pts']=m.params['protocol_reps_sweep']
    m.params['sweep_name']='Number of LDE repetitions'
    m.autoconfig()

    m.generate_sequence()
    m.setup()
    m.run()    
    m.save()
    m.finish()

def get_AWG_AOM_voltage(aom,power):
    ret=0.0
    if aom.get_cur_controller()=='AWG':
        ret= aom.power_to_voltage(power)
    else:
        aom.apply_voltage(0)
        aom.set_cur_controller('AWG')
        ret = aom.power_to_voltage(power)
        aom.set_cur_controller('ADWIN')
    return ret    
    
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