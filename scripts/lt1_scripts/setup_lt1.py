print 'loading setup tools...'
from tools import stools
reload(stools)

print 'reload all modules...'
execfile("setup/reload_all.py")

####
print 'reload all measurement parameters and calibrations...'
execfile("setup/msmt_params.py")

####
print 'configure the setup-specific hardware...'
ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt1_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['Velocity2AOM']
ssro.AdwinSSRO.A_aom = qt.instruments['Velocity1AOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']

sequence.SequenceSSRO.awg = qt.instruments['AWG']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100']
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['mw', 'rf', 'adwin']

mbi.MBIMeasurement.chan_RF  = 'RF' 
mbi.MBIMeasurement.chan_adwin_sync = 'adwin_sync'
mbi.MBIMeasurement.physical_adwin = qt.instruments['physical_adwin']

pulsar_msmt.PulsarMeasurement.awg = qt.instruments['AWG']
pulsar_msmt.PulsarMeasurement.mwsrc = qt.instruments['SMB100']
pulsar_msmt.MBI.physical_adwin = qt.instruments['physical_adwin']

#teleportation.Teleportation.adwin_processes_key = 'adwin_lt1_processes'
#teleportation.Teleportation.E_aom = qt.instruments['Velocity1AOM']
#teleportation.Teleportation.A_aom = qt.instruments['Velocity2AOM']
#teleportation.Teleportation.green_aom = qt.instruments['GreenAOM']
#teleportation.Teleportation.yellow_aom = qt.instruments['YellowAOM']
#teleportation.Teleportation.adwin = qt.instruments['adwin']
####

print 'configure the pulsar sequencer and update pulses and elements...'
execfile("setup/sequence.py")


