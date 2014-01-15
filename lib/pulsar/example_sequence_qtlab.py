import qt
import numpy as np

import pulsar
import pulse
import element
import pprint

reload(pulse)
reload(element)
reload(pulsar)

test_element = element.Element('a test element', pulsar=qt.pulsar)
# we copied the channel definition from out global pulsar
# print 'Channel definitions: '
# pprint.pprint(test_element._channels)
# print 

# define some bogus pulses.
sin_pulse = pulse.SinePulse(channel='RF', name='A sine pulse on RF')
sq_pulse = pulse.SquarePulse(channel='MW_pulsemod', 
    name='A square pulse on MW pmod')

special_pulse = pulse.SinePulse(channel='RF', name='special pulse')
special_pulse.amplitude = 0.2
special_pulse.length = 2e-6
special_pulse.frequency = 10e6
special_pulse.phase = 0

# create a few of those
test_element.add(pulse.cp(sin_pulse, frequency=1e6, amplitude=1, length=1e-6), 
    name='first pulse')
test_element.add(pulse.cp(sq_pulse, amplitude=1, length=1e-6), 
	name='second pulse', refpulse='first pulse', refpoint='end')
test_element.add(pulse.cp(sin_pulse, frequency=2e6, amplitude=0.5, length=1e-6), 
    name='third pulse', refpulse='second pulse', refpoint='end')

# print 'Element overview:'
# test_element.print_overview()
# print 

special_element = element.Element('Another element', pulsar=qt.pulsar)
special_element.add(special_pulse)

# upload waveforms
qt.pulsar.upload(test_element, special_element)

# create the sequnce
# note that we re-use the same waveforms (just with different identifier
# names)
seq = pulsar.Sequence('A Sequence')
seq.append(name='first element', wfname='a test element', trigger_wait=True, 
    goto_target='first element', jump_target='first special element')
seq.append('first special element', 'Another element', 
    repetitions=5)
seq.append('third element', 'a test element', trigger_wait=True,
    goto_target='third element', jump_target='second special element')
seq.append('second special element', 'Another element', 
    repetitions=5)

# program the Sequence
awg_pulsar.program_sequence(seq)