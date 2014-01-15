# put everything in here that needs to be updated when changed

# reload adwin
import qt
import measurement.lib.config.adwins as adwins_cfg
adwin = qt.instruments['adwin']
reload(adwins_cfg)
qt.instruments.reload(adwin)

# reload AWG channel config and pulsar config
import measurement.lib.config.awgchannels_lt2 as awgcfg
reload(awgcfg)

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

from measurement.lib.measurement2.adwin_ssro import sequence
reload(sequence)

from measurement.lib.measurement2.adwin_ssro import mbi
reload(mbi)

from measurement.lib.measurement2.adwin_ssro import mbi_espin
reload(mbi_espin)

# pulsar measurements
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
reload(pulsar_msmt)

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
reload(pulsar_mbi_espin)