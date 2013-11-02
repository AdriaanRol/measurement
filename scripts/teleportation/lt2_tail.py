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

import sequence as tseq
reload(tseq)
import parameters as tparams
reload(tparams)


import teleportation_master 
reload(teleportation_master)


class LT2Tail(pulsar_msmt.PulsarMeasurement):

    def generate_sequence(self):
        print 'generating'
        self.lt2_sequence()

    
    def autoconfig(self):
        pulsar_msmt.PulsarMeasurement.autoconfig(self)

        # add values from AWG calibrations
        self.params_lt2['SP_voltage_AWG'] = \
                self.A_aom_lt2.power_to_voltage(
                        self.params_lt2['AWG_SP_power'], controller='sec')

        print 'setting AWG SP voltage:', self.params_lt2['SP_voltage_AWG']
        
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params_lt2['SP_voltage_AWG'])


    def lt2_sequence(self):
        print "Make lt2 sequence... "

        self.lt2_seq = pulsar.Sequence('TeleportationLT2')

        dummy_element = tseq._lt2_dummy_element(self)
        LDE_element = tseq._lt2_LDE_element(self)
        finished_element = tseq._lt2_sequence_finished_element(self)

        self.lt2_seq.append(name = 'LDE_LT2',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            trigger_wait = True,
            # jump_target = 'DD', TODO: not implemented yet
            goto_target = 'LDE_LT2',
            repetitions = self.params['LDE_attempts_before_CR'])

        elements = []
        elements.append(dummy_element)
        elements.append(finished_element)

        if DO_LDE_SEQUENCE:
            elements.append(LDE_element)

        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.lt2_seq)
        self.awg_lt2.set_runmode('SEQ')
        self.awg_lt2.start()

        i=0
        awg_ready = False
        while not awg_ready and i<40:
            try:
                if self.awg_lt2.get_state() == 'Waiting for trigger':
                    awg_ready = True
            except:
                print 'waiting for awg: usually means awg is still busy and doesnt respond'
                print 'waiting', i, '/40'
                i=i+1
            qt.msleep(0.5)
        if not awg_ready: 
            raise Exception('AWG not ready')


LT2Tail.adwin_dict = adwins_cfg.config
LT2Tail.green_aom_lt2 = qt.instruments['GreenAOM']
LT2Tail.Ey_aom_lt2 = qt.instruments['MatisseAOM']
LT2Tail.A_aom_lt2 = qt.instruments['NewfocusAOM']
LT2Tail.mwsrc_lt2 = qt.instruments['SMB100']
LT2Tail.awg_lt2 = qt.instruments['AWG']
LT2Tail.repump_aom_lt2 = qt.instruments['GreenAOM']

LDE_DO_MW = False
DO_LDE_SEQUENCE = True   

def tail_lt2(name):

    m=LT2Tail(name)
    
    for k in tparams.params.parameters:
        m.params[k] = tparams.params[k]
    for k in tparams.params_lt2.parameters:
        m.params[k] = tparams.params_lt2[k]

    m.params_lt2=m.params
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params['Ex_CR_amplitude']= m.params['Ey_CR_amplitude']
    m.params['Ex_SP_amplitude']= m.params['Ey_SP_amplitude']
    m.params['Ex_RO_amplitude']=m.params['Ey_RO_amplitude']
    tseq.pulse_defs_lt2(m)


    m.params['pts']=1
    m.params['send_AWG_start'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['repetitions'] = 100000
    m.params['sequence_wait_time'] = m.params['LDE_attempts_before_CR']*m.params['LDE_element_length']*1e6 + 20
    m.params['SP_duration'] = 250

    m.params['opt_pi_pulses'] = 2
    m.params_lt2['MW_during_LDE'] = 0

    print  m.params['sequence_wait_time'] 
    m.autoconfig()
    m.generate_sequence()
    m.setup()
    m.run()    
    m.save()
    qt.instruments['AWG'].set_runmode('CONT')
    # m.finish()

if __name__ == '__main__':
    tail_lt2('lt2_tailS')