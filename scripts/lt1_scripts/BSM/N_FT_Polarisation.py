import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element

import BSM
reload(BSM)

import mbi_espin_funcs as funcs
reload(funcs)


class N_FT_Polarisation_Check(BSM.ElectronReadoutMsmt):
    mprefix = 'N_FT_Polarisation_Check'
     
    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self._pulse_defs()
        
        self.FT_pulse = pulse.SquarePulse(channel='Velocity1AOM',
            length = self.params['sp_duration'], amplitude = self.params['FT_pulse_amp'])
        
        self.yel_pulse = pulse.SquarePulse(channel='YellowAOM',
            length = self.params['sp_duration']*3/4., amplitude = self.params['yellow_pulse_amp'])
        
        N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        N_RO_CNOT_elt.append(pulse.cp(self.T, length=500e-9))
        
        if self.params['readout_line'] == '-1':
            N_RO_CNOT_elt.append(self.pi2pi_m1)
        elif self.params['readout_line'] == '0':
            N_RO_CNOT_elt.append(self.pi2pi_0)    
        elif self.params['readout_line'] == '+1':
            N_RO_CNOT_elt.append(self.pi2pi_p1)
        else:
            raise(Exception('Unknown readout line' + str(m.params['readout_line'])))
       

        # make the list of elements required for uploading
        e = element.Element('N_FT_Polarisation', pulsar=qt.pulsar, global_time = True)
        
        e.append(pulse.cp(self.T, length=200e-9))
        last=e.append(self.yel_pulse)
        e.add(self.FT_pulse, refpulse=last, refpoint='start')
        e.append(pulse.cp(self.T, length=200e-9))
        e.append(pulse.cp(self.CORPSE_pi)) # ,
            # frequency = self.params['CORPSE_pi_mod_frq'],
            # amplitude = 0.))        
        
        # create the sequence
        seq = pulsar.Sequence('N_FT_Polarisation_Check_sequence')
        
        for i,r in enumerate(self.params['FT_element_repetitions']):
            
            # 1: MBI 
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'ft_mw'+str(i))  
                    
            #2  then repeat (SP+MW pi)-element for the current number of times
            seq.append(name = 'ft_mw'+str(i), wfname=e.name,
                    repetitions= r,
                    trigger_wait = True)
            
            seq.append(name='N_ro'+str(i), wfname=N_RO_CNOT_elt.name,
                trigger_wait=False)
                
            seq.append(name = 'sync-{}'.format(i), 
                    wfname = self.sync_elt.name) 
                
        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, e, N_RO_CNOT_elt,self.sync_elt)
        
        qt.pulsar.program_sequence(seq)

class N_FT_Polarisation_Check_CW(BSM.ElectronReadoutMsmt):
    mprefix = 'N_FT_Polarisation_Check'
     
    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self._pulse_defs()
        
        self.slow_cw_mI0 = pulselib.MW_IQmod_pulse('slow_cw_mI0',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = 0,
            frequency = self.params['mI0_mod_frq'],
            amplitude = self.params['mw_amp'],
            length = self.params['sp_mw_el_duration'])
        self.slow_cw_mIp1 = pulselib.MW_IQmod_pulse('slow_cw_mIp1',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = 0,
            frequency = self.params['mIp1_mod_frq'],
            amplitude = self.params['mw_amp'],
            length = self.params['sp_mw_el_duration'])        
        
        self.FT_pulse = pulse.SquarePulse(channel='Velocity1AOM',
            length = self.params['sp_mw_el_duration'], amplitude = self.params['FT_pulse_amp'])
        
       # self.yel_pulse = pulse.SquarePulse(channel='YellowAOM',
        #    length = 10e-6, amplitude = self.params['FT_pulse_amp'])
        
        N_RO_CNOT_elt = element.Element('N-RO CNOT', pulsar=qt.pulsar)
        N_RO_CNOT_elt.append(pulse.cp(self.T, length=500e-9))
        
        if self.params['readout_line'] == '-1':
            N_RO_CNOT_elt.append(self.pi2pi_m1)
        elif self.params['readout_line'] == '0':
            N_RO_CNOT_elt.append(self.pi2pi_0)
        elif self.params['readout_line'] == '+1':
            N_RO_CNOT_elt.append(self.pi2pi_p1)
        else:
            raise(Exception('Unknown readout line' + str(m.params['readout_line'])))
       

        # make the list of elements required for uploading
        e = element.Element('N_FT_Polarisation', pulsar=qt.pulsar, ignore_delays=True)
        
        e.add(self.FT_pulse)
        e.add(self.slow_cw_mI0)
        e.add(self.slow_cw_mIp1)
        
        e_sp = element.Element('final_SP', pulsar=qt.pulsar)
        
        e_sp.add(pulse.cp(self.FT_pulse(length=50e-6)))
        
        # create the sequence
        seq = pulsar.Sequence('N_FT_Polarisation_Check_sequence')
        
        for i,r in enumerate(self.params['FT_element_repetitions']):
            
            # 1: MBI 
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'ft_mw'+str(i))  
                    
            #2  then repeat (SP+MW pi)-element for the current number of times
            seq.append(name = 'ft_mw'+str(i), wfname=e.name,
                    repetitions= r,
                    trigger_wait = True)
            seq.append(name = 'final_sp'+str(i), wfname=e_sp.name,
                    trigger_wait=False)
            
            seq.append(name='N_ro'+str(i), wfname=N_RO_CNOT_elt.name,
                trigger_wait=False)
                
            seq.append(name = 'sync-{}'.format(i), 
                    wfname = self.sync_elt.name) 
                
        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, e, N_RO_CNOT_elt,self.sync_elt,e_sp)
        
        qt.pulsar.program_sequence(seq)

class N_FT_Polarisation_Check_ESR(BSM.ElectronReadoutMsmt):
    mprefix = 'N_FT_Polarisation_Check_ESR'
     
    def generate_sequence(self, upload=True):
        # load all the other pulsar resources
        self._pulse_defs()
        
        self.FT_pulse = pulse.SquarePulse(channel='Velocity1AOM',
            length = self.params['sp_duration'], amplitude = self.params['FT_pulse_amp'])
        
        self.yel_pulse = pulse.SquarePulse(channel='YellowAOM',
            length = self.params['sp_duration']*3/4., amplitude = self.params['yellow_pulse_amp'])
        
        # make the list of elements required for uploading
        e = element.Element('N_FT_Polarisation', pulsar=qt.pulsar, global_time = True)
        
        e.append(pulse.cp(self.T, length=200e-9))
        last = e.append(self.yel_pulse)
        e.add(self.FT_pulse, refpulse=last, refpoint='start')
        e.append(pulse.cp(self.T, length=200e-9))
        e.append(pulse.cp(self.CORPSE_pi)) # ,
            # frequency = self.params['CORPSE_pi_mod_frq'],
            # amplitude = 0.))        
        
        # create the sequence
        seq = pulsar.Sequence('N_FT_Polarisation_Check_ESR_sequence')
        
        ro_elts = []
        for i,f in enumerate(self.params['RO_mod_frqs']):
            
            # 1: MBI 
            seq.append(name = 'MBI-{}'.format(i),
                wfname = self.mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-{}'.format(i),
                jump_target = 'ft_mw'+str(i))  
                    
            #2  then repeat (SP+MW pi)-element for the current number of times
            seq.append(name = 'ft_mw'+str(i), wfname=e.name,
                    repetitions = self.params['FT_element_repetitions'],
                    trigger_wait = True)
            
            #3 ESR type readout
            ro_e = element.Element('N_RO-{}'.format(i), pulsar=qt.pulsar, global_time = True)
            ro_e.append(self.T)
            ro_e.append(pulse.cp(self.slow_pi, 
                frequency = f))
            
            seq.append(name='N_ro'+str(i), wfname=ro_e.name,
                trigger_wait=False)
            ro_elts.append(ro_e)
                
            seq.append(name = 'sync-{}'.format(i), 
                    wfname = self.sync_elt.name) 
                
        # program AWG
        if upload:
            qt.pulsar.upload(self.mbi_elt, e ,self.sync_elt, *ro_elts)
        
        qt.pulsar.program_sequence(seq)        

def do_N_FT_Polarisation_check():
    m = N_FT_Polarisation_Check('pulsed')
    BSM.prepare(m,yellow=True)
    
    #preparation line:
    m.params['init_line'] = '-1'  

    #readout pulse line:
    m.params['readout_line']='-1'
    
    m.name=m.name+'_init_'+ m.params['init_line']+'_ro_'+m.params['readout_line']
    
    m.params['FT_element_repetitions'] = np.array([1,1000,2000,3000,4000])
    pts = len(m.params['FT_element_repetitions'])
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['sp_duration'] = 20e-6
    
    m.params['FT_pulse_power']=100e-9
    m.params['FT_pulse_amp']=\
            m.A_aom.power_to_voltage(m.params['FT_pulse_power'], controller='sec')
    m.params['yellow_pulse_power'] = 50e-9
    m.params['yellow_pulse_amp'] =\
            m.yellow_aom.power_to_voltage(m.params['yellow_pulse_power'], controller='sec')
    

            # for the autoanalysis
    m.params['sweep_name'] = 'FT_element_repetitions'
    m.params['sweep_pts'] = m.params['FT_element_repetitions']
    
    
    if m.params['init_line'] == '-1':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mIm1_mod_frq'] #ms=-1
    elif m.params['init_line'] == '0':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mI0_mod_frq'] #ms=0
    elif m.params['init_line'] == '+1':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mIp1_mod_frq']#ms=+1 
        print 'dont use this --> CORPSE is bad for +1'
    else:
        raise(Exception('Unknown init line' + str(m.params['init_line'])))
    
    funcs.finish(m, debug=False, upload=True)
    
def do_N_FT_Polarisation_check_cw():
    m = N_FT_Polarisation_Check_CW('cw')
    BSM.prepare(m,yellow=True)
    
    
    #preparation line:
    m.params['init_line'] = '0'  

    #readout pulse line:
    m.params['readout_line']='-1'
    
    m.name=m.name+'_init_'+ m.params['init_line']+'_ro_'+m.params['readout_line']
    m.params['sp_mw_el_duration'] = 20e-6
    m.params['mw_amp']=0.05
    
    
    m.params['FT_element_repetitions'] = np.arange(0,100,10)
    pts = len(m.params['FT_element_repetitions'])
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    
    m.params['FT_pulse_amp']=\
            m.A_aom.power_to_voltage(100e-9, controller='sec')

            # for the autoanalysis
    m.params['sweep_name'] = 'FT_element_duration'
    m.params['sweep_pts'] = m.params['FT_element_repetitions']*m.params['sp_mw_el_duration']
    
    
    if m.params['init_line'] == '-1':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mIm1_mod_frq'] #ms=-1
    elif m.params['init_line'] == '0':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mI0_mod_frq'] #ms=0
    elif m.params['init_line'] == '+1':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mIp1_mod_frq']#ms=+1 
        print 'dont use this --> CORPSE is bad for +1'
    else:
        raise(Exception('Unknown init line' + str(m.params['init_line'])))
    
    funcs.finish(m, debug=False, upload=True)    
  
def do_N_FT_Polarisation_check_ESR():
    m = N_FT_Polarisation_Check_ESR('ESR')
    BSM.prepare(m,yellow=True)
    
    #preparation line:
    m.params['init_line'] = '-1'  
   
    m.name = m.name+'_init_'+ m.params['init_line']
    
    m.params['FT_element_repetitions'] = 1
    m.params['RO_mod_frqs'] = np.linspace(23e6, 31e6, 41)
    pts = len(m.params['RO_mod_frqs'])
    
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    m.params['sp_duration'] = 25e-6
    
    m.params['FT_pulse_power'] = 100e-9
    m.params['FT_pulse_amp'] = \
            m.A_aom.power_to_voltage(m.params['FT_pulse_power'], controller='sec')
    m.params['yellow_pulse_power'] = 0e-9
    m.params['yellow_pulse_amp'] = \
            m.yellow_aom.power_to_voltage(m.params['yellow_pulse_power'], controller='sec')
    
    # for the autoanalysis
    m.params['sweep_name'] = 'FT_element_repetitions'
    m.params['sweep_pts'] = m.params['FT_element_repetitions']
    
    
    if m.params['init_line'] == '-1':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mIm1_mod_frq'] #ms=-1
    elif m.params['init_line'] == '0':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mI0_mod_frq'] #ms=0
    elif m.params['init_line'] == '+1':
        m.params['AWG_MBI_MW_pulse_mod_frq']=m.params['mIp1_mod_frq']#ms=+1 
        print 'dont use this --> CORPSE is bad for +1'
    else:
        raise(Exception('Unknown init line' + str(m.params['init_line'])))
    
    funcs.finish(m, debug=True, upload=True)
  
if __name__ == '__main__':
    # do_N_FT_Polarisation_check()
    #do_N_FT_Polarisation_check_cw()
    do_N_FT_Polarisation_check_ESR()
    