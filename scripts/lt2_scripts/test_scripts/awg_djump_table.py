import qt
import numpy as np

import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import pprint

reload(pulse)
reload(element)
reload(pulsar)

test_pulse = pulse.SquarePulse(channel = 'HH_sync', amplitude = 1.0)


elt1 = element.Element('idle', pulsar = qt.pulsar)
elt2 = element.Element('djump1', pulsar = qt.pulsar)
elt3 = element.Element('djump2', pulsar = qt.pulsar)
elt4 = element.Element('djump3', pulsar = qt.pulsar)
elt5 = element.Element('djump4', pulsar = qt.pulsar)


#print 'Channel definitions: '
#pprint.pprint(test_element._channels)

elt1.add(pulse.cp(test_pulse, amplitude = 0.0, length = 10e-6))
elt2.add(pulse.cp(test_pulse, amplitude = 0.0, length = 10e-6))
elt2.add(pulse.cp(test_pulse, amplitude = 1.0, length = 1e-6), start = 5e-6)
elt3.add(pulse.cp(test_pulse, amplitude = 0.0, length = 10e-6))
elt3.add(pulse.cp(test_pulse, amplitude = 1.0, length = 1e-6), start = 6e-6)
elt4.add(pulse.cp(test_pulse, amplitude = 0.0, length = 10e-6))
elt4.add(pulse.cp(test_pulse, amplitude = 1.0, length = 1e-6), start = 7e-6)
elt5.add(pulse.cp(test_pulse, amplitude = 0.0, length = 10e-6))
elt5.add(pulse.cp(test_pulse, amplitude = 1.0, length = 1e-6), start = 8e-6)



seq = pulsar.Sequence('DJUMP Test')
seq.append(name = 'idle', wfname = elt1.name, trigger_wait = True, repetitions = 1)
seq.append(name = 'djump1', wfname = elt2.name, trigger_wait = False, repetitions = 1, goto_target = 'idle')
seq.append(name = 'djump2', wfname = elt3.name, trigger_wait = False, repetitions = 1, goto_target = 'idle')
seq.append(name = 'djump3', wfname = elt4.name, trigger_wait = False, repetitions = 1, goto_target = 'idle')
seq.append(name = 'djump4', wfname = elt5.name, trigger_wait = False, repetitions = 1, goto_target = 'idle')

seq.set_djump(True)
seq.add_djump_address('djump1', 0)
seq.add_djump_address('djump2', 1)
seq.add_djump_address('djump3', 2)
seq.add_djump_address('djump4', 3)

qt.pulsar.upload(elt1)
qt.pulsar.upload(elt2)
qt.pulsar.upload(elt3)
qt.pulsar.upload(elt4)
qt.pulsar.upload(elt5)

qt.pulsar.program_sequence(seq)


