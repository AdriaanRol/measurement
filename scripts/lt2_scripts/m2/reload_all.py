# put everything in here that needs to be updated when changed

# reload adwin
import qt
import measurement.lib.config.adwins as adwins_cfg
adwin = qt.instruments['adwin']
reload(adwins_cfg)
qt.instruments.reload(adwin)

# reload AWG channel config
import measurement.lib.config.awgchannels_lt2 as awg_cfg
reload(awg_cfg)

# measurement classes
from measurement.lib.measurement2 import measurement
reload(measurement)

from measurement.lib.measurement2.adwin_ssro import ssro
reload(ssro)

from measurement.lib.measurement2.adwin_ssro import sequence
reload(sequence)

# default measurement parameters
execfile(r'd:\measuring\measurement\scripts\lt2_scripts\m2\msmt_params.py')

