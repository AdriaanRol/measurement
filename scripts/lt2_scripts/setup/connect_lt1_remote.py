physical_adwin_lt1 = qt.instruments.create('physical_adwin_lt1','ADwin_Gold_II',
                 address=353)
adwin_lt1 = qt.instruments.create('adwin_lt1', 'adwin_lt1')
counters_lt1 = qt.instruments.create('counters_lt1', 'counters_via_adwin',
        adwin='adwin_lt1')
master_of_space_lt1 = qt.instruments.create('master_of_space_lt1', 
        'master_of_space_lt1', adwin='adwin_lt1')
linescan_counts_lt1 = qt.instruments.create('linescan_counts_lt1', 
        'linescan_counts', adwin='adwin_lt1', mos='master_of_space_lt1',
        counters='counters_lt1')
scan2d_lt1 = qt.instruments.create('scan2d_lt1', 'scan2d_counts',
        linescan='linescan_counts_lt1', mos='master_of_space_lt1',
        xdim='x', ydim='y', counters='counters_lt1')
opt1d_counts_lt1 = qt.instruments.create('opt1d_counts_lt1', 
        'optimize1d_counts', linescan='linescan_counts_lt1', 
        mos='master_of_space_lt1', counters='counters_lt1')
optimiz0r_lt1 = qt.instruments.create('optimiz0r_lt1', 'optimiz0r',opt1d_ins=
        opt1d_counts_lt1, mos_ins = master_of_space_lt1, dimension_set='lt1')
c_optimiz0r_lt1 = qt.instruments.create('c_optimiz0r_lt1', 'convex_optimiz0r', 
        adwin_ins=adwin_lt1, mos_ins=master_of_space_lt1)


def _do_remote_connect_lt1():
    global powermeter_lt1, SMB100_lt1, PMServo_lt1, ZPLServo_lt1, ivvi_lt1, AWG_lt1
    
    from lib.network import object_sharer as objsh
    if objsh.start_glibtcp_client('192.168.0.20',port=12002, nretry=3, timeout=5):
        remote_ins_server_lt1=objsh.helper.find_object('qtlab_lt1:instrument_server')
        powermeter_lt1 = qt.instruments.create('powermeter_lt1', 'Remote_Instrument',
                remote_name='powermeter', inssrv=remote_ins_server_lt1)
        SMB100_lt1 = qt.instruments.create('SMB100_lt1', 'Remote_Instrument',
                remote_name='SMB100', inssrv=remote_ins_server_lt1)
        AWG_lt1 = qt.instruments.create('AWG_lt1', 'Remote_Instrument',
                remote_name='AWG', inssrv=remote_ins_server_lt1)
        PMServo_lt1= qt.instruments.create('PMServo_lt1', 'Remote_Instrument',
                remote_name='PMServo', inssrv=remote_ins_server_lt1)
        ZPLServo_lt1= qt.instruments.create('ZPLServo_lt1', 'Remote_Instrument',
                remote_name='ZPLServo', inssrv=remote_ins_server_lt1)
        #ivvi = qt.instruments.create('ivvi_lt1', 'Remote_Instrument',
                #remote_name='ivvi', inssrv=remote_ins_server_lt1)

        return True
    
    logging.warning('Failed to start remote instruments') 
    return False

remote_ins_connect=_do_remote_connect_lt1
if remote_ins_connect():        
    powermeter_lt1 = qt.instruments['powermeter_lt1']
else:
    logging.warning('LT1 AOMs USE INCORRECT POWER METER!!!1111')
    powermeter_lt1 = qt.instruments['powermeter_lt1']    

GreenAOM_lt1 = qt.instruments.create('GreenAOM_lt1', 'AOM', 
        use_adwin='adwin_lt1', use_pm = powermeter_lt1.get_name())         
NewfocusAOM_lt1 = qt.instruments.create('NewfocusAOM_lt1', 'AOM', 
        use_adwin='adwin_lt1', use_pm = powermeter_lt1.get_name(), use_awg='AWG_lt1')         
MatisseAOM_lt1 = qt.instruments.create('MatisseAOM_lt1', 'AOM', 
        use_adwin='adwin_lt1', use_pm = powermeter_lt1.get_name())
YellowAOM_lt1 = qt.instruments.create('YellowAOM_lt1', 'AOM',
        use_adwin = 'adwin_lt1', use_pm = powermeter_lt1.get_name(),use_awg='AWG_lt1')

setup_controller_lt1 = qt.instruments.create('setup_controller_lt1',
    'setup_controller',
    use = { 'master_of_space_lt1' : 'mos'} )


pos_maxjog_cfg_lt1 = { 1 : {'positive' : 1.000,
                            'negative' : 0.940},
                       2 : {'positive' : 1.000,
                            'negative' : 0.900},
                     }

#normalized to ~ 481 steps/degree
pos_maxpr_cfg_lt1  = { 1 : {'positive' : 1.000,
                            'negative' : 0.981},
                       2 : {'positive' : 1.000,
                            'negative' : 1.130},
                      }

#values provided here are in deg/step
pos_step_deg_cfg_lt1 = { 1 : 10/5000.,
                      2 : 10/5000.}

positioner_lt1 = qt.instruments.create('positioner_lt1', 'NewportAgilisUC2_v2', 
        address = 'COM6', maxjog_cfg=pos_maxjog_cfg_lt1, maxpr_cfg=pos_maxpr_cfg_lt1,
        step_deg_cfg=pos_step_deg_cfg_lt1 )
rejecter_lt1 = qt.instruments.create('rejecter_lt1', 'laser_reject0r', positioner=positioner_lt1, 
        adwin=adwin_lt1, red_laser= MatisseAOM_lt1)

#### make a remote pulsar and configure it
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

try:
    del qt.pulsar_remote
except:
    pass
qt.pulsar_remote = pulsar.Pulsar()
qt.pulsar_remote.AWG = qt.instruments['AWG_lt1']

### channels

# for the remote LDE setup. effectively this is the relative delay between SP AOM and MWs.
spin_of = -69e-9

# RF
qt.pulsar_remote.define_channel(id='ch1', name='RF', type='analog', high=1.0,
    low=-1.0, offset=0., delay=spin_of+165e-9, active=True)

# MW
qt.pulsar_remote.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=spin_of+(44+165)*1e-9, active=True)
qt.pulsar_remote.define_channel(id='ch3', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=spin_of+(27+165)*1e-9, active=True)
qt.pulsar_remote.define_channel(id='ch4', name='MW_Qmod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=spin_of+(27+165)*1e-9, active=True)

# sync ADwin
qt.pulsar_remote.define_channel(id='ch3_marker2', name='adwin_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

# light -- delay of SP is here *defined* as 700 (trigger comes from the other AWG); 
# all other delays are then relative to that.
qt.pulsar_remote.define_channel(id='ch2', name='Velocity1AOM', type='analog', 
    high=0.4, low=0, offset=0., delay=700e-9, active=True)

qt.pulsar_remote.define_channel(id='ch2_marker2', name='YellowAOM', type='marker', 
    high=0.4, low=0, offset=0., delay=750e-9, active=True) 

# Trigger AWG LT2
qt.pulsar_remote.define_channel(id='ch3_marker1', name='AWG_LT2_trigger', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

# Sync for HH
qt.pulsar_remote.define_channel(id='ch4_marker1', name='HH_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)