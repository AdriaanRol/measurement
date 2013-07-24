import qt
import numpy as np
import msvcrt

def turn_off_lasers(names):
    for l in names:
        qt.instruments[l].apply_voltage(0)

def turn_off_all_lt1_lasers():
    turn_off_lasers(['GreenAOM_lt1', 'MatisseAOM_lt1', 'NewfocusAOM_lt1', 'YellowAOM_lt1'])

def turn_off_all_lt2_lasers():
    turn_off_lasers(['MatisseAOM', 'NewfocusAOM','GreenAOM'])

def turn_off_all_lasers():
    turn_off_all_lt1_lasers()
    turn_off_all_lt2_lasers()

def recalibrate_laser(name, servo, adwin):
    qt.instruments[adwin].set_simple_counting()
    qt.instruments[servo].move_in()
    qt.msleep(1)

    qt.msleep(0.1)
    print 'Calibrate', name
    qt.instruments[name].calibrate(31)
    qt.msleep(1)

    qt.instruments[name].apply_voltage(0)
    qt.instruments[servo].move_out()
    qt.msleep(1)

def recalibrate_lt1_lasers(names=['GreenAOM_lt1', 'MatisseAOM_lt1', 'NewfocusAOM_lt1', 'YellowAOM_lt1']):
    turn_off_all_lt1_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo_lt1', 'adwin_lt1')

def recalibrate_lt2_lasers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM']):
    turn_off_all_lt2_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo', 'adwin')


def check_power(name, setpoint, adwin, powermeter, servo):
    qt.instruments[adwin].set_simple_counting()
    qt.instruments[servo].move_in()    
    qt.instruments[powermeter].set_wavelength(qt.instruments[name].get_wavelength())
    qt.instruments[name].set_power(setpoint)
    qt.msleep(1)

    print name, 'setpoint:', setpoint, 'value:', qt.instruments[powermeter].get_power()

    qt.instruments[name].apply_voltage(0)
    qt.instruments[servo].move_out()
    qt.msleep(1)    


def check_lt1_powers(names=['GreenAOM_lt1', 'MatisseAOM_lt1', 'NewfocusAOM_lt1', 'YellowAOM_lt1'],
    setpoints = [50e-6, 10e-9, 100e-9, 50e-9]):
    
    turn_off_all_lt1_lasers()
    for n,s in zip(names, setpoints):
        check_power(n, s, 'adwin_lt1', 'powermeter_lt1', 'PMServo_lt1')

def check_lt2_powers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM'],
    setpoints = [10e-9, 20e-9, 50e-6]):
    
    turn_off_all_lt2_lasers()
    for n,s in zip(names, setpoints):
        check_power(n, s, 'adwin', 'powermeter', 'PMServo')
        
def connect_lt1_remote():
    global physical_adwin_lt1
    global adwin_lt1
    global counters_lt1
    global master_of_space_lt1
    global optimiz0r_lt1
    global powermeter_lt1
    global SMB100_lt1
    global PMServo_lt1
    global ZPLServo_lt1 
    global GreenAOM_lt1
    global NewfocusAOM_lt1
    global MatisseAOM_lt1
    global YellowAOM_lt1

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

def disconnect_lt1_remote():
    for i in qt.instruments.get_instrument_names():
        if len(i) >= 4 and i[-4:] == '_lt1':
            qt.instruments.remove(i)



