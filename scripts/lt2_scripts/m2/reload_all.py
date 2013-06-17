# put everything in here that needs to be updated when changed

# reload adwin
import qt
import measurement.lib.config.adwins as adwins_cfg
adwin = qt.instruments['adwin']
reload(adwins_cfg)
qt.instruments.reload(adwin)

# reload AWG channel config
import measurement.lib.config.awgchannels_lt2 as awgcfg
reload(awgcfg)

# measurement classes
from measurement.lib.measurement2 import measurement
reload(measurement)

from measurement.lib.measurement2.adwin_ssro import ssro
reload(ssro)

from measurement.lib.measurement2.adwin_ssro import sequence
reload(sequence)

from measurement.lib.measurement2.adwin_ssro import mbi
reload(mbi)

from measurement.lib.measurement2.adwin_ssro import mbi_espin
reload(mbi_espin)

# pulsar measurements
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
reload(pulsar_msmt)

# default measurement parameters
execfile(r'd:\measuring\measurement\scripts\lt2_scripts\m2\msmt_params.py')

# set all the static variables for lt2
execfile(r'd:\measuring\measurement\scripts\lt2_scripts\m2\sequence.py')

# set all the static variables for lt2
execfile(r'd:\measuring\measurement\scripts\lt2_scripts\m2\lt2_statics.py')