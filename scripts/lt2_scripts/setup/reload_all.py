# put everything in here that needs to be updated when changed

# reload adwin
import qt
import measurement.lib.config.adwins as adwins_cfg
adwin = qt.instruments['adwin']
reload(adwins_cfg)
qt.instruments.reload(adwin)

# reload AWG channel config and pulsar config

from measurement.lib.pulsar import pulse, element, pulsar, pulselib
reload(pulse)
reload(element)
reload(pulsar)
reload(pulselib)

# measurement classes
from measurement.lib.measurement2 import measurement
reload(measurement)

from measurement.lib.measurement2.adwin_ssro import ssro
reload(ssro)

# pulsar measurements
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
reload(pulsar_msmt)

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
reload(pulsar_mbi_espin)