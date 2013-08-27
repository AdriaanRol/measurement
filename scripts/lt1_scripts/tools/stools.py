import qt
import numpy as np
import msvcrt
import logging

def turn_off_lasers():
    qt.instruments['GreenAOM'].apply_voltage(0)
    qt.instruments['Velocity1AOM'].apply_voltage(0)
    qt.instruments['Velocity2AOM'].apply_voltage(0)
    qt.instruments['YellowAOM'].apply_voltage(0)

def recalibrate_aoms(names=['Velocity1AOM', 'Velocity2AOM']):
    qt.instruments['adwin'].set_simple_counting()
    
    turn_off_lasers()

    qt.instruments['PMServo'].move_in()
    qt.msleep(1)
    qt.instruments['PMServo'].move_out()
    qt.msleep(1)
    qt.instruments['PMServo'].move_in()
    qt.msleep(1)

    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        turn_off_lasers()
        qt.msleep(0.1)
        print 'Calibrate', n
        qt.instruments[n].calibrate(31)
        qt.msleep(1)

    turn_off_lasers()
    qt.instruments['PMServo'].move_out()
    qt.msleep(1)

def check_powers(setpoints=(50e-9,10e-9)):
    qt.instruments['adwin'].set_simple_counting()
    
    turn_off_lasers()
    qt.instruments['PMServo'].move_in()
    qt.instruments['powermeter'].set_wavelength(637e-9)
    qt.msleep(1)

    print 'Velocity 1: ',
    qt.instruments['Velocity1AOM'].set_power(setpoints[0])
    qt.msleep(1)
    print qt.instruments['powermeter'].get_power()*1e9, '; setpoint:', setpoints[0]*1e9
    qt.instruments['Velocity1AOM'].apply_voltage(0)


    print 'Velocity 2: ',
    qt.instruments['Velocity2AOM'].set_power(setpoints[1])
    qt.msleep(1)
    print qt.instruments['powermeter'].get_power()*1e9, '; setpoint:', setpoints[1]*1e9
    qt.instruments['Velocity2AOM'].apply_voltage(0)

    turn_off_lasers()
    qt.instruments['PMServo'].move_out()
    qt.msleep(1)

def average_power(n=10, prepare=False):
    if prepare:
        qt.instruments['adwin'].set_simple_counting()
        turn_off_lasers()
        qt.instruments['PMServo'].move_in()
        qt.instruments['powermeter'].set_wavelength(637e-9)
        qt.msleep(1)
    
    powers = np.array([])
    print 'steps:',n, ':',
    for i in range(n):
        print i,
        powers = np.append(powers, qt.instruments['powermeter'].get_power()*1e9)
        qt.msleep(0.1)
    
    print ''

    print 'P = (%.3f +/- %.3f) nW' % (np.mean(powers), np.std(powers))
    print ''

def gate_scan_to_voltage(voltage, stepsize=0.01, dwell_time=0.05):
    cur_v=qt.instruments['adwin'].get_dac_voltage('gate')
    print 'scan gate to voltage ...',voltage
    print 'current gate voltage: ', cur_v 
    steps=int(abs(cur_v-voltage)/stepsize)
    for v in np.linspace(cur_v, voltage, steps):
        qt.instruments['adwin'].set_dac_voltage(('gate',v))
        qt.msleep(dwell_time)

    print 'done.'

def start_yellow_and_red(powers=(5e-9, 5e-9, 5e-9)):
    qt.instruments['adwin'].set_simple_counting()
    qt.instruments['YellowAOM'].set_power(powers[0])
    qt.instruments['Velocity1AOM'].set_power(powers[1])
    qt.instruments['Velocity2AOM'].set_power(powers[2])

def set_lt1_remote():
    for i in ['labjack', 
        'setup_controller',
        'YellowAOM',
        'Velocity2AOM',
        'Velocity1AOM',
        'GreenAOM',
        'optimiz0r',
        'opt1d_counts',
        'scan2d',
        'linescan_counts',
        'master_of_space',
        'counters',
        'adwin',
        'ivvi']:

        try:
            qt.instruments.remove(i)
        except:
            logging.warning('could not remove instrument {}'.format(i))

def set_lt1_standalone():
    global adwin
    global counters
    global master_of_space
    global optimiz0r
    global GreenAOM
    global Velocity1AOM
    global Velocity2AOM
    global ivvi

    adwin = qt.instruments.create('adwin', 'adwin_lt1', 
            physical_adwin='physical_adwin')
    
    counters = qt.instruments.create('counters', 'counters_via_adwin',
            adwin='adwin')
    
    master_of_space = qt.instruments.create('master_of_space',
            'master_of_space_lt1', adwin='adwin')

    linescan_counts = qt.instruments.create('linescan_counts', 
            'linescan_counts',  adwin='adwin', mos='master_of_space',
            counters='counters')
    
    scan2d = qt.instruments.create('scan2d', 'scan2d_counts',
             linescan='linescan_counts', mos='master_of_space',
            xdim='x', ydim='y', counters='counters')
     
    opt1d_counts = qt.instruments.create('opt1d_counts', 
             'optimize1d_counts', linescan='linescan_counts', 
            mos='master_of_space', counters='counters')

    optimiz0r = qt.instruments.create('optimiz0r', 'optimiz0r',opt1d_ins=
            opt1d_counts,mos_ins=master_of_space,dimension_set='lt1')
  
    GreenAOM = qt.instruments.create('GreenAOM', 'AOM', 
            use_adwin='adwin', use_pm= 'powermeter')
    Velocity1AOM = qt.instruments.create('Velocity1AOM', 'AOM', 
            use_adwin='adwin', use_pm = 'powermeter')         
    Velocity2AOM = qt.instruments.create('Velocity2AOM', 'AOM', 
            use_adwin='adwin', use_pm = 'powermeter')
    YellowAOM = qt.instruments.create('YellowAOM', 'AOM', 
            use_adwin='adwin', use_pm ='powermeter')
    #laser_scan = qt.instruments.create('laser_scan', 'laser_scan')
    ivvi = qt.instruments.create('ivvi', 'IVVI', address = 'ASRL1::INSTR', numdacs = 4)
    setup_controller = qt.instruments.create('setup_controller',
             'setup_controller',
            use = { 'master_of_space' : 'mos'} )
    
    from lib.network import object_sharer as objsh
    if objsh.start_glibtcp_client('192.168.0.80', port=12002, nretry=3):
        remote_ins_server = objsh.helper.find_object('qtlab_lasermeister:instrument_server')
        labjack = qt.instruments.create('labjack', 'Remote_Instrument',
        remote_name='labjack', inssrv=remote_ins_server)






        
    
