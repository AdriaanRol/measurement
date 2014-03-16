"""
LT3 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import sequence as bseq
reload(bseq)
import parameters as tparams
reload(tparams)


class LT3Tail(pulsar_msmt.PulsarMeasurement):

    def generate_sequence(self):
        print 'generating'
        self.lt3_sequence()

    
    def autoconfig(self):
        pulsar_msmt.PulsarMeasurement.autoconfig(self)

        # add values from AWG calibrations
        self.params_lt3['SP_voltage_AWG'] = \
                self.A_aom_lt3.power_to_voltage(
                        self.params_lt3['AWG_SP_power'], controller='sec')

        print 'setting AWG SP voltage:', self.params_lt3['SP_voltage_AWG']
        
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params_lt3['SP_voltage_AWG'])


    def lt3_sequence(self):
        print "Make lt3 sequence... "

        self.lt3_seq = pulsar.Sequence('TailLT3')

        dummy_element = bseq._lt3_dummy_element(self)
        LDE_element = bseq._lt3_LDE_element(self,use_short_eom_pulse=self.params['use_short_eom_pulse'])
        finished_element = bseq._lt3_sequence_finished_element(self)

        self.lt3_seq.append(name = 'LDE_LT3',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            trigger_wait = True,
            # jump_target = 'DD', TODO: not implemented yet
            goto_target = 'LDE_LT3',
            repetitions = self.params['LDE_attempts_before_CR'])

        elements = []
        elements.append(dummy_element)
        elements.append(finished_element)

        if DO_LDE_SEQUENCE:
            elements.append(LDE_element)

        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.lt3_seq)
        self.awg_lt3.set_runmode('SEQ')
        self.awg_lt3.start()

        i=0
        awg_ready = False
        while not awg_ready and i<40:
            try:
                if self.awg_lt3.get_state() == 'Waiting for trigger':
                    awg_ready = True
            except:
                print 'waiting for awg: usually means awg is still busy and doesnt respond'
                print 'waiting', i, '/40'
                i=i+1
            qt.msleep(0.5)
        if not awg_ready: 
            raise Exception('AWG not ready')

        def finish(self):
                self.awg_lt3.stop()
                self.awg_lt3.set_runmode('CONT')


LT3Tail.adwin_dict = adwins_cfg.config
LT3Tail.green_aom_lt3 = qt.instruments['GreenAOM']
LT3Tail.Ey_aom_lt3 = qt.instruments['MatisseAOM']
LT3Tail.A_aom_lt3 = qt.instruments['NewfocusAOM']
LT3Tail.mwsrc_lt3 = qt.instruments['SMB100']
LT3Tail.awg_lt3 = qt.instruments['AWG']
LT3Tail.repump_aom_lt3 = qt.instruments['GreenAOM']

LDE_DO_MW = False
DO_LDE_SEQUENCE = True   

def tail_lt3(name):

    m=LT3Tail(name)
    
    for k in tparams.params.parameters:
        m.params[k] = tparams.params[k]
    for k in tparams.params_lt3.parameters:
        m.params[k] = tparams.params_lt3[k]

    m.params_lt3=m.params
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params['Ex_CR_amplitude']= m.params['Ey_CR_amplitude']
    m.params['Ex_SP_amplitude']= m.params['Ey_SP_amplitude']
    m.params['Ex_RO_amplitude']=m.params['Ey_RO_amplitude']


    #EOM pulse ----------------------------------
    m.params['use_short_eom_pulse']=False
    qt.pulsar.set_channel_opt('EOM_trigger', 'delay', 147e-9)
    qt.pulsar.set_channel_opt('EOM_trigger', 'high', 2.)#2.0
    m.params_lt3['eom_pulse_duration']        = 2e-9
    m.params_lt3['eom_off_duration']          = 100e-9
    m.params_lt3['eom_off_amplitude']         = -.28    *2# calibration from 23-08-2013
    m.params_lt3['eom_pulse_amplitude']       = -.28     *2
    m.params_lt3['eom_overshoot_duration1']   = 10e-9
    m.params_lt3['eom_overshoot1']            = 0#-0.03   *2
    m.params_lt3['eom_overshoot_duration2']   = 4e-9
    m.params_lt3['eom_overshoot2']            = 0#-0.03   *2
    m.params_lt3['aom_risetime']              = 42e-9
    m.params_lt3['eom_aom_on']                = True

    bseq.pulse_defs_lt3(m)
    m.params['pts']=1
    m.params['send_AWG_start'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['repetitions'] = 500000
    m.params['sequence_wait_time'] = m.params['LDE_attempts_before_CR']*m.params['LDE_element_length']*1e6 + 20
    m.params['SP_duration'] = 250

    m.params['opt_pi_pulses'] = 2
    m.params_lt3['MW_during_LDE'] = 0

    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()    
    m.save()
    m.finish()

if __name__ == '__main__':
    tail_lt3('lt3_tailS')