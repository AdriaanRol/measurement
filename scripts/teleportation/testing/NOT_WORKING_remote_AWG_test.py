import qt
import numpy as np

from measurement.lib.pulsar import pulse, pulselib, element, pulsar

try:
    del qt.pulsar_remote
except:
    pass
qt.pulsar_remote = pulsar.Pulsar()
qt.pulsar_remote.AWG = qt.instruments['AWG_lt1']
qt.pulsar_remote.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=(44+165)*1e-9, active=True)

test_element = element.Element('a test element', pulsar=qt.pulsar_remote)

sq_pulse = pulse.SquarePulse(channel='MW_pulsemod', 
    name='A square pulse on MW pmod')

test_element.add(pulse.cp(sq_pulse, amplitude=1, length=1e-6),
    name='a pulse')
    
qt.pulsar.upload(test_element)

