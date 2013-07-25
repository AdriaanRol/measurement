"""
This script prepares LT1 for the measurement -- this is in order to program the AWG
for measurement modes where the two AWGs talk to each other.

We don't want to store any data or parameters in here.
The idea, for now, is the following:
We set all parameters in the master script.
This script imports the master and gets all the parameters from there.

(For future improvement, it'd be even better if all the preparations could be executed on
a remote machine from the master script in some way.)
"""

import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import parameters as tparams
reload(tparams)

import sequence as tseq
reload(tseq)

import teleportation_master as tm
reload(tm)

class TeleportationSlave:

    def __init__(self):
        self.params = m2.MeasurementParameters('JointParameters')
        self.params_lt1 = m2.MeasurementParameters('LT1Parameters')
        self.params_lt2 = m2.MeasurementParameters('LT2Parameters')

        self.awg = qt.instruments['AWG']

    def load_settings(self):
        for k in tparams.params.parameters:
            self.params[k] = tparams.params[k]

        for k in tparams.params_lt1.parameters:
            self.params_lt1[k] = tparams.params_lt1[k]
        
        for k in tparams.params_lt2.parameters:
            self.params_lt2[k] = tparams.params_lt2[k]

    def update_definitions(self):
        tseq.pulse_defs_lt1(self)

    ### Sequence
    def _lt1_N_polarization_decision_element(self):
        """
        This is just an empty element that needs to be long enough for the
        adwin to decide whether we need to do CR (then it times out) or
        jump to the LDE sequence.
        """

        e = element.Element('N_pol_decision', pulsar = qt.pulsar)
        e.append(pulse.cp(self.T_pulse, length=10e-6))

        return e

    def _lt1_N_pol_element(self):
        """
        This is the element we will run to polarize the nuclear spin after each CR
        checking.
        """
        e = element.Element('N_pol', pulsar = qt.pulsar)

        # TODO not yet implemented
        e.append(pulse.cp(self.T_pulse, length=1e-6))

        return e

    def _lt1_start_LDE_element(self):
        """
        This element triggers the LDE sequence on LT2.
        """
        e = element.Element('start_LDE', pulsar = qt.pulsar)
        e.append(pulse.cp(self.AWG_LT2_trigger_pulse, 
            length = 1e-6,
            amplitude = 0))
        e.append(self.AWG_LT2_trigger_pulse)

        return e


    def _lt1_LDE_element(self):
        """
        This element contains the LDE part for LT1, i.e., spin pumping and MW pulses
        for the LT1 NV in the real experiment.
        """
        e = element.Element('LDE_LT1', pulsar = qt.pulsar, global_time = True)

        # TODO not yet implemented
        e.append(pulse.cp(self.T_pulse, length=1e-6))

        return e

    def _lt1_BSM_element(self):
        """
        this element contains the BSM element. (Easiest way: only one element, then there's less
            chance for error when we don't need all the triggers -- however, then we need
            the timing to be correctly calibrated!)
        """
        e = element.Element('BSM', pulsar = qt.pulsar, global_time = True)

        # TODO not yet implemented
        e.append(pulse.cp(self.T_pulse, length=1e-6))

        return e

    def _lt1_dummy_element(self):
        """
        This is a dummy element. It contains nothing. 
        It replaces the LDE element if we do not want to do LDE.
        """
        e = element.Element('dummy', pulsar = qt.pulsar, global_time = True)
        
        e.append(pulse.cp(self.T_pulse, length=1e-6))

        return e

    def lt1_sequence(self):
        self.lt1_seq = pulsar.Sequence('TeleportationLT1')

        N_pol_decision_element = self._lt1_N_polarization_decision_element()
        N_pol_element = self._lt1_N_pol_element()
        start_LDE_element = self._lt1_start_LDE_element()
        LDE_element = self._lt1_LDE_element()
        BSM_element = self._lt1_BSM_element()
        dummy_element = self._lt1_dummy_element()

        self.lt1_seq.append(name = 'N_pol_decision',
            wfname = N_pol_decision_element.name,
            trigger_wait = True,
            goto_target = 'N_polarization' if tm.DO_POLARIZE_N else 'start_LDE',
            jump_target = 'start_LDE')

        if tm.DO_POLARIZE_N:
            self.lt1_seq.append(name = 'N_polarization',
                wfname = N_pol_element.name,
                trigger_wait = True,
                repetitions = self.params_lt1['N_pol_element_repetitions'])

        self.lt1_seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_LDE_element.name)

        self.lt1_seq.append(name = 'LDE_LT1',
            wfname = (LDE_element.name if DO_LDE_SEQUENCE else dummy_element.name),
            # jump_target = 'BSM', 
            goto_target = 'N_pol_decision',
            repetitions = self.params['LDE_attempts_before_CR'])


        elements = []
        elements.append(N_pol_decision_element)
        elements.append(N_pol_element)
        elements.append(start_LDE_element)
        #elements.append(BSM_element)
        elements.append(dummy_element)
        elements.append(finished_element)

        if tm.DO_POLARIZE_N:
            elements.append(LDE_element)

        qt.pulsar.upload(*elements)
        
        qt.pulsar.program_sequence(self.lt1_seq)
        self.awg.set_runmode('SEQ')
        self.awg.start()

        i=0
        awg_ready = False
        while not awg_ready and i<40:
            try:
                if self.awg.get_state() == 'Waiting for trigger':
                    awg_ready = True
            except:
                print 'waiting for awg: usually means awg is still busy and doesnt respond'
                print 'waiting', i, '/40'
                i=i+1
            qt.msleep(0.5)
        if not awg_ready: 
            raise Exception('AWG not ready')

def run_default():
    m = TeleportationSlave()
    m.load_settings()
    m.update_definitions()
    m.lt1_sequence()


if __name__ == '__main__':
    run_default()
