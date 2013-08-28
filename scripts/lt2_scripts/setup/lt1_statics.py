ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt1_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM_lt1']
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM_lt1']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM_lt1']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM_lt1']
ssro.AdwinSSRO.adwin = qt.instruments['adwin_lt1']
ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM_lt1']

sequence.SequenceSSRO.awg = qt.instruments['AWG_lt1']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100_lt1']
#below is not yet LT1; we cannot do AWG things remotely yet
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.chan_nf_aom = 'AOM_Newfocus'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['spin','optical_rabi']

mbi.MBIMeasurement.chan_RF  = 'RF' 
mbi.MBIMeasurement.chan_adwin_sync = 'adwin_sync'
mbi.MBIMeasurement.physical_adwin = qt.instruments['physical_adwin_lt1']

pulsar_msmt.PulsarMeasurement.mwsrc = qt.instruments['SMB100_lt1']
pulsar_msmt.PulsarMeasurement.awg = qt.instruments['AWG_lt1']
pulsar_msmt.PulsarMeasurement.physical_adwin = qt.instruments['physical_adwin_lt1']