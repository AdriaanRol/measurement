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

def _do_remote_connect_lt1():
    global powermeter_lt1, SMB100_lt1, PMServo_lt1, ZPLServo_lt1
    
    from lib.network import object_sharer as objsh
    if objsh.start_glibtcp_client('192.168.0.20',port=12002, nretry=3, timeout=5):
        remote_ins_server_lt1=objsh.helper.find_object('qtlab_lt1:instrument_server')
        powermeter_lt1 = qt.instruments.create('powermeter_lt1', 'Remote_Instrument',
                     remote_name='powermeter', inssrv=remote_ins_server_lt1)
        SMB100_lt1 = qt.instruments.create('SMB100_lt1', 'Remote_Instrument',
                     remote_name='SMB100', inssrv=remote_ins_server_lt1)
        PMServo_lt1= qt.instruments.create('PMServo_lt1', 'Remote_Instrument',
                     remote_name='PMServo', inssrv=remote_ins_server_lt1)
        ZPLServo_lt1= qt.instruments.create('ZPLServo_lt1', 'Remote_Instrument',
                     remote_name='ZPLServo', inssrv=remote_ins_server_lt1)
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
        use_adwin='adwin_lt1', use_pm = powermeter_lt1.get_name())         
MatisseAOM_lt1 = qt.instruments.create('MatisseAOM_lt1', 'AOM', 
        use_adwin='adwin_lt1', use_pm = powermeter_lt1.get_name())
YellowAOM_lt1 = qt.instruments.create('YellowAOM_lt1', 'AOM',
        use_adwin = 'adwin_lt1', use_pm = powermeter_lt1.get_name())

setup_controller_lt1 = qt.instruments.create('setup_controller_lt1',
    'setup_controller',
    use = { 'master_of_space_lt1' : 'mos'} )