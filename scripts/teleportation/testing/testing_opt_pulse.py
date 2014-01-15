
import numpy as np
import logging
import qt
import hdf5_data as h5
import time

from measurement.lib.cython.hh_optimize import hht4
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

e = element.Element('opt_pulse', clock=1e9, min_samples=0, pulsar=qt.pulsar)

opt_pulse = pulselib.EOMAOMPulse('Eom Aom Pulse', 
        eom_channel = 'EOM_Matisse',
        aom_channel = 'EOM_AOM_Matisse')

square_pulse = pulse.SquarePulse(channel = 'EOM_Matisse', length = 50e-9, amplitude = 1.0)

qt.pulsar.set_channel_opt('EOM_AOM_Matisse','high', 0.5)


e.add(opt_pulse)
e.add(square_pulse(amplitude = 0), refpulse = 'Eom Aom Pulse-0', refpoint = 'end', refpoint_new = 'end')
e.add(pulse.cp(square_pulse, amplitude = 0.5, channel = 'EOM_AOM_Matisse'), refpulse = 'Eom Aom Pulse-0',\
    start = 70e-9, refpoint_new = 'end')

qt.pulsar.upload(e)

seq = pulsar.Sequence('Opt Test')
seq.append('opt pulse 1', wfname = 'opt_pulse', trigger_wait = True)

qt.pulsar.program_sequence(seq)