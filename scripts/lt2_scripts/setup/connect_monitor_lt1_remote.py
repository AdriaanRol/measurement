from lib.network import object_sharer as objsh
    
if objsh.start_glibtcp_client('192.168.0.80',port=12002, nretry=3, timeout=5):
    remote_ins_server_lasers=objsh.helper.find_object('qtlab_lasermeister:instrument_server')
    pidvelocity1 = qt.instruments.create('pidvelocity1', 'Remote_Instrument',
                 remote_name='pid_lt1_newfocus1', inssrv=remote_ins_server_lasers)    
    pidvelocity2 = qt.instruments.create('pidvelocity2', 'Remote_Instrument',
                 remote_name='pid_lt1_newfocus2', inssrv=remote_ins_server_lasers)
else:
    logging.warning('Failed to start remote instruments for pids lt1') 


if objsh.start_glibtcp_client('192.168.0.20',port=12002, nretry=3, timeout=5):
    remote_ins_server_lt1=objsh.helper.find_object('qtlab_lt1:instrument_server')
    ivvi_lt1 = qt.instruments.create('ivvi_lt1', 'Remote_Instrument',
            remote_name='ivvi', inssrv=remote_ins_server_lt1)
else:
    logging.warning('Failed to start remote instruments for ivvi lt1') 
