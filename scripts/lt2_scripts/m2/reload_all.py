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

# default measurement parameters
execfile(r'd:\measuring\measurement\scripts\lt2_scripts\m2\msmt_params.py')

# set all the static variables for lt2
ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt2_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM']
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']
ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']

sequence.SequenceSSRO.awg = qt.instruments['AWG']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100']
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['spin']

mbi.MBIMeasurement.chan_RF  = 'RF' 
mbi.MBIMeasurement.chan_adwin_sync = 'ADwin_trigger'
mbi.MBIMeasurement.physical_adwin = qt.instruments['physical_adwin']
