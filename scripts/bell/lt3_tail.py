"""
LT3 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
# XX from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmnt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import sequence as bseq
reload(bseq)
import parameters as bparams
reload(bparams)

#XX pulsar_pq.PQPulsarMeasurement
class LT3Tail(pulsar_msmnt.PulsarMeasurement):

    def generate_sequence(self):
        print 'generating'
        self.lt3_sequence()

    
    def autoconfig(self, **kw):
        #XX pulsar_pq.PQPulsarMeasurement.autoconfig(self, **kw)
        pulsar_msmnt.PulsarMeasurement.autoconfig(self, **kw)
        # add values from AWG calibrations
        self.params_lt3['SP_voltage_AWG'] = \
                self.A_aom_lt3.power_to_voltage(
                        self.params_lt3['AWG_SP_power'], controller='sec')

        print 'setting AWG SP voltage:', self.params_lt3['SP_voltage_AWG']
        
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params_lt3['SP_voltage_AWG'])


    def lt3_sequence(self):
        print "Make lt3 sequence... "
               
        self.lt3_seq = pulsar.Sequence('TailLT3')

        elements = [] 

        dummy_element = bseq._lt3_dummy_element(self)
        finished_element = bseq._lt3_sequence_finished_element(self)
        elements.append(dummy_element)
        elements.append(finished_element)

        for i in range(self.params['pts']):
            eom_p = self.create_eom_pulse(i)

            e = bseq._lt3_LDE_element(self, 
                name = 'LT3 Tail sweep element {}'.format(i),
                eom_pulse =  eom_p)
            #print e.print_overview()    
            elements.append(e)
            self.lt3_seq.append(name = 'LT3 Tail sweep {}'.format(i),
                wfname = e.name,
                trigger_wait = self.params['trigger_wait'],
                repetitions = self.params['LDE_attempts_before_CR'])
            
        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.lt3_seq)

    def create_eom_pulse(self, i):
        if self.params['use_short_eom_pulse']:
            print 'using short eom pulse'
            return pulselib.short_EOMAOMPulse('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse',
                    eom_off_duration = self.params['eom_off_duration'],
                    eom_off_amplitude = self.params['eom_off_amplitude'],
                    eom_off_2_amplitude  = 2.65, #msmt.params_lt3['eom_off_2_amplitude'],
                    eom_overshoot_duration1 = self.params['eom_overshoot_duration1'],
                    eom_overshoot1 = 0.0, #msmt.params_lt3['eom_overshoot1'],
                    eom_overshoot_duration2 = self.params['eom_overshoot_duration2'],
                    eom_overshoot2 = 0.0, #msmt.params_lt3['eom_overshoot2'],
                    aom_risetime = self.params['aom_risetime'])  
        else: 
            return pulselib.EOMAOMPulse('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse',
                    eom_pulse_duration      = self.params['eom_pulse_duration'][i],
                    eom_off_duration        = self.params['eom_off_duration'],
                    eom_off_amplitude       = self.params['eom_off_amplitude'][i],
                    eom_pulse_amplitude     = self.params['eom_pulse_amplitude'][i],
                    eom_overshoot_duration1 = self.params['eom_overshoot_duration1'],
                    eom_overshoot1          = self.params['eom_overshoot1'],
                    eom_overshoot_duration2 = self.params['eom_overshoot_duration2'],
                    eom_overshoot2          = self.params['eom_overshoot2'],
                    eom_comp_pulse_amplitude= self.params['eom_comp_pulse_amplitude'] , 
                    eom_comp_pulse_duration = self.params['eom_comp_pulse_duration'],
                    aom_risetime            = self.params['aom_risetime'])
    
     


LT3Tail.adwin_dict = adwins_cfg.config
LT3Tail.green_aom_lt3 = qt.instruments['GreenAOM']
LT3Tail.Ey_aom_lt3 = qt.instruments['MatisseAOM']
LT3Tail.A_aom_lt3 = qt.instruments['NewfocusAOM']
LT3Tail.mwsrc_lt3 = qt.instruments['SMB100']
LT3Tail.awg_lt3 = qt.instruments['AWG']
LT3Tail.repump_aom_lt3 = qt.instruments['GreenAOM']


def tail_lt3(name):

    m=LT3Tail(name)
    
    for k in bparams.params.parameters:
        m.params[k] = bparams.params[k]
    for k in bparams.params_lt3.parameters:
        m.params[k] = bparams.params_lt3[k]

    m.params_lt3=m.params
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+PQ'])
    m.params['Ex_CR_amplitude']= m.params['Ey_CR_amplitude']
    m.params['Ex_SP_amplitude']= m.params['Ey_SP_amplitude']
    m.params['Ex_RO_amplitude']=m.params['Ey_RO_amplitude']

    pts=1
    m.params['pts']=pts
    
    #EOM pulse ----------------------------------
    m.params['use_short_eom_pulse']=False
    qt.pulsar.set_channel_opt('EOM_trigger', 'delay', 175e-9)
    #qt.pulsar.set_channel_opt('EOM_trigger', 'high', 2.)#2.0

    m.params['eom_pulse_duration']        = np.ones(pts)* 2e-9
    m.params['EOM_trigger_length']        = 20e-9
    m.params['eom_off_amplitude']         = np.ones(pts)* -0.05# calibration from 6-03-2014
    m.params['eom_pulse_amplitude']       = np.ones(pts)* 1.5# np.linspace(1.4, 2.0, pts) # calibration to be done!
    m.params['eom_off_duration']          = 200e-9
    m.params['eom_overshoot_duration1']   = 10e-9
    m.params['eom_overshoot1']            = 0#-0.03   *2
    m.params['eom_overshoot_duration2']   = 4e-9
    m.params['eom_overshoot2']            = 0#-0.03   *2
    m.params['eom_comp_pulse_amplitude']  = m.params['eom_pulse_amplitude']
    m.params['eom_comp_pulse_duration']   = m.params['eom_pulse_duration']#m.params['EOM_trigger_length']
    m.params['aom_risetime']              = 30e-9#42e-9 # calibration to be done!
    m.params['eom_aom_on']                = True

    

    m.params['sweep_name'] = 'eom_pulse_amplitude'
    m.params['sweep_pts'] = m.params_lt3['eom_pulse_amplitude']  

    bseq.pulse_defs_lt3(m)

    m.params['send_AWG_start'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['repetitions'] = 20000
    m.params['sequence_wait_time'] = m.params['LDE_attempts_before_CR']*m.params['LDE_element_length']*1e6 + 20
    m.params['SP_duration'] = 250

    m.params['opt_pi_pulses'] = 1
    m.params_lt3['MW_during_LDE'] = 0
    m.params['trigger_wait'] = 1
    qt.instruments['AWG'].set_runmode('CONT')
    qt.instruments['AWG'].get_runmode()
    qt.instruments['AWG'].get_runmode()
    qt.instruments['AWG'].get_runmode()
    m.autoconfig()
    m.generate_sequence()
    m.setup(mw=m.params_lt3['MW_during_LDE'])#XX, pq_calibrate=False)
    m.run(autoconfig=False, setup=False)    
    m.save()
    m.finish()

if __name__ == '__main__':
    tail_lt3('lt3_tailS')
