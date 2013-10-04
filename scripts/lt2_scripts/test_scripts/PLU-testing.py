import qt
import numpy as np

import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import pprint

reload(pulse)
reload(element)
reload(pulsar)

# adwin reset:  ch1_marker1
# awg plu gate: ch1_marker2
# photon 1:     ch4_marker1
# photon 2:     ch4_marker2

qt.pulsar.define_channel(id='ch1_marker1', name='adwin_reset', type='marker', 
    high=1.0, low=0, offset=0., delay=0., active=True)
qt.pulsar.define_channel(id='ch1_marker2', name='plu_gate', type='marker', 
    high=1.0, low=0, offset=0., delay=0., active=True)
qt.pulsar.define_channel(id='ch2_marker1', name='photon_1', type='marker', 
    high=1.0, low=0, offset=0., delay=0., active=True)
qt.pulsar.define_channel(id='ch2_marker2', name='photon_2', type='marker', 
    high=1.0, low=0, offset=0., delay=0., active=True)

adwin_reset = pulse.SquarePulse(channel = 'adwin_reset', length=50e-9, amplitude = 1.0)
plu_gate = pulse.SquarePulse(channel = 'plu_gate', length=70e-9, amplitude = 1.0)
photon1 = pulse.SquarePulse(channel = 'photon_1', length=20e-9, amplitude = 1.0)
photon2 = pulse.SquarePulse(channel = 'photon_2', length=20e-9, amplitude = 1.0)

elt1 = element.Element('plu_test', pulsar = qt.pulsar)

elt1.add(pulse.cp(adwin_reset, amplitude = 0.0, length = 10e-9), name='initial_delay')
elt1.add(pulse.cp(adwin_reset), name = 'reset', refpulse = 'initial_delay')
elt1.add(pulse.cp(plu_gate), name = 'plu_gate_1', refpulse = 'reset', start = 200e-9)
elt1.add(pulse.cp(photon1), name = 'photon1', refpulse = 'plu_gate_1', refpoint = 'start', start = 20e-9)
elt1.add(pulse.cp(plu_gate), name = 'plu_gate_2', refpulse = 'plu_gate_1', start = 600e-9)
elt1.add(pulse.cp(photon2), name = 'photon2', refpulse = 'plu_gate_2', refpoint = 'start', start = 20e-9)
elt1.add(pulse.cp(plu_gate), name = 'plu_gate_3', refpulse = 'plu_gate_2', start = 100e-9)
elt1.add(pulse.cp(plu_gate), name = 'plu_gate_4', refpulse = 'plu_gate_3', start = 100e-9)
elt1.add(pulse.cp(adwin_reset, amplitude = 0.0, length = 300e-9), name='final_delay', refpulse = 'plu_gate_3')

qt.pulsar.upload(elt1)

seq = pulsar.Sequence('PLU Test')
seq.append(name = 'plu_test', wfname = elt1.name, trigger_wait = True, repetitions = 1)


qt.pulsar.program_sequence(seq)


