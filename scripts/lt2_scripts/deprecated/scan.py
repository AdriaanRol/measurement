# controls a single dimension of a position that is set via an
# adwin DAC voltage

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import qt
import time
import types
import gobject
import numpy as np

master_of_space.set_front_z(16)
scan2d_stage.set_is_running(True)
while scan2d_stage.get_is_running() == True:
	print 'wacht nou effetjes'
master_of_space.set_front_z(17)
scan2d_stage.set_is_running(True)

