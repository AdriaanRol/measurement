import qt
import numpy as np
import msvcrt

from measurement.lib.tools import stools
reload(stools)

AWG = 'AWG'
ADWIN = 'adwin'
PM = 'powermeter'
PMSERVO = 'PMServo'
GREENAOM = 'GreenAOM'
RED1AOM = 'NewfocusAOM'
RED2AOM = 'MatisseAOM'
YELLOWAOM = 'YellowAOM'

ALLAOMS = [GREENAOM, RED2AOM, RED1AOM, YELLOWAOM]
ALLCHECKPWRS = [50e-6, 5e-9, 5e-9, 50e-9]
ADWINAOMS = [GREENAOM, RED2AOM, RED1AOM, YELLOWAOM]
AWGAOMS = [RED1AOM, YELLOWAOM]

def turn_off_all_lasers():
    stools.set_simple_counting(ADWIN)
    stools.turn_off_lasers(ALLAOMS)

def recalibrate_lasers(names = ADWINAOMS, awg_names = AWGAOMS):    
    turn_off_all_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        stools.recalibrate_laser(n, PMSERVO, ADWIN)
    
    for n in awg_names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        stools.recalibrate_laser(n, PMSERVO, ADWIN, awg=True)

def check_powers(names = ALLAOMS, setpoints = ALLCHECKPWRS):
    turn_off_all_lasers()
    for n,s in zip(names, setpoints):
        stools.check_power(n, s, ADWIN, PM, PMSERVO)

def check_max_powers(names = ALLAOMS):
    turn_off_all_lasers()
    for n in names:
        stools.check_max_power(n, ADWIN, PM, PMSERVO)

def turn_off_AWG_laser_channel():
    qt.instruments['AWG'].set_ch2_offset(0.)


def set_lt1_remote():
    for i in ['labjack', 
        'setup_controller',
        'YellowAOM',
        'MatisseAOM',
        'NewfocusAOM',
        'GreenAOM',
        'optimiz0r',
        'opt1d_counts',
        'scan2d',
        'linescan_counts',
        'master_of_space',
        'counters',
        'adwin',
        'AWG']:

        try:
            qt.instruments.remove(i)
        except:
            logging.warning('could not remove instrument {}'.format(i))

def set_lt1_standalone():
    global adwin
    global AWG
    global counters
    global master_of_space
    global optimiz0r
    global GreenAOM
    global NewfocusAOM
    global MatisseAOM
    global ivvi

    AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', 
        address='TCPIP0::192.168.0.22::inst0::INSTR', 
        reset=False, numpoints=1e3)

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
    NewfocusAOM = qt.instruments.create('NewfocusAOM', 'AOM', 
            use_adwin='adwin', use_pm = 'powermeter')         
    MatisseAOM = qt.instruments.create('MatisseAOM', 'AOM', 
            use_adwin='adwin', use_pm = 'powermeter')
    YellowAOM = qt.instruments.create('YellowAOM', 'AOM', 
            use_adwin='adwin', use_pm ='powermeter')
    setup_controller = qt.instruments.create('setup_controller',
             'setup_controller',
            use = { 'master_of_space' : 'mos'} )
    
    from lib.network import object_sharer as objsh
    if objsh.start_glibtcp_client('192.168.0.80', port=12002, nretry=3):
        remote_ins_server = objsh.helper.find_object('qtlab_lasermeister:instrument_server')
        labjack = qt.instruments.create('labjack', 'Remote_Instrument',
        remote_name='labjack', inssrv=remote_ins_server)
        

