"""
This script prepares LT1 for the measurement -- this is in order to program the AWG
for measurement modes where the two AWGs talk to each other.

We don't want to store any data or parameters in here.
The idea, for now, is the following:
We set all parameters in the master script.
This script imports the master and gets all the parameters from there.

For future improvement, it'd be even better if all the preparations could be executed on
a remote machine from the master script in some way.
"""

import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import sequence as tseq
reload(tseq)

import teleportation_master as tm
reload(tm)

class TeleportationSlave:

    def __init__(self):
        pass

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
        e.append(pulse.cp(self.T_pulse), length=1e-6)

        return e

    def _lt1_LDE_element(self): # TODO need to be two elements!
        """
        This element contains the LDE part for LT1, i.e., spin pumping and MW pulses
        for the LT1 NV in the real experiment.
        Also, this element contains the start trigger for the LT2 AWG.
        """
        e = element.Element('LDE_LT1', pulsar = qt.pulsar, global_time = True)

        # TODO not yet implemented
        e.append(pulse.cp(self.T_pulse), length=1e-6)

        return e


    def lt1_sequence(self):
        self.lt1_seq = pulsar.Sequence('TeleportationLT1')

        N_pol_decision_element = self._lt1_N_polarization_decision_element()
        N_pol_element = self._lt1_N_pol_element()
        LDE_element = self._lt1_LDE_element()

        self.lt1_seq.append(name = 'N_pol_decision',
            wfname = N_pol_decision_element.name,
            trigger_wait = True,
            goto_target = 'N_polarization' if tm.DO_POLARIZE_N else 'LDE_LT1',
            jump_target = 'LDE_LT1')

        self.lt1_seq.append(name = 'N_polarization',
            wfname = N_pol_element.name,
            trigger_wait = True,
            repetitions = self.params['']) ### TODO not sure yet how to transfer params; tomorrow




