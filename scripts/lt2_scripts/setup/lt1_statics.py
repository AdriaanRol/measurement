ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt1_processes'

# REGULAR SETTING: A = NF, E = Matisse
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM_lt1']
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM_lt1']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM_lt1']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM_lt1']
ssro.AdwinSSRO.adwin = qt.instruments['adwin_lt1']

if qt.cfgman.get('protocols/AdwinSSRO/yellow'):
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.yellow_aom
else:
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.green_aom
 
mbi.MBIMeasurement.chan_RF  = 'RF' 
mbi.MBIMeasurement.chan_adwin_sync = 'adwin_sync'
mbi.MBIMeasurement.physical_adwin = qt.instruments['physical_adwin_lt1']

pulsar_msmt.PulsarMeasurement.mwsrc = qt.instruments['SMB100_lt1']
pulsar_msmt.PulsarMeasurement.awg = qt.instruments['AWG_lt1']
pulsar_msmt.PulsarMeasurement.physical_adwin = qt.instruments['physical_adwin_lt1']