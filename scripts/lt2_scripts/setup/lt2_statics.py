ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt2_processes'
ssro.AdwinSSRO.E_aom = qt.current_instruments('MatisseAOM')
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']


if qt.cfgman.get('protocols/AdwinSSRO/yellow'):
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.yellow_aom
else:
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.green_aom

sequence.SequenceSSRO.awg = qt.instruments['AWG']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100']
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.chan_nf_aom = 'AOM_Newfocus'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['spin','optical_rabi']



mbi.MBIMeasurement.chan_RF  = 'RF' 
mbi.MBIMeasurement.chan_adwin_sync = 'adwin_sync'
mbi.MBIMeasurement.physical_adwin = qt.instruments['physical_adwin']

pulsar_msmt.PulsarMeasurement.mwsrc = qt.instruments['SMB100']
pulsar_msmt.PulsarMeasurement.awg = qt.instruments['AWG']
pulsar_msmt.PulsarMeasurement.physical_adwin = qt.instruments['physical_adwin']