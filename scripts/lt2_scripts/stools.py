import qt
import numpy as np
import msvcrt

def turn_off_lasers():
    qt.instruments['GreenAOM'].apply_voltage(0)
    qt.instruments['NewfocusAOM'].apply_voltage(0)
    qt.instruments['MatisseAOM'].apply_voltage(0)
    qt.instruments['YellowAOM'].apply_voltage(0)

def recalibrate_aoms(names=['MatisseAOM', 'NewfocusAOM']):
    qt.instruments['adwin'].set_simple_counting()
    
    turn_off_lasers()

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

def check_powers(check_power=10e-9,names=['MatisseAOM', 'NewfocusAOM'] ):
    qt.instruments['adwin'].set_simple_counting()
    
    turn_off_lasers()
    qt.instruments['PMServo'].move_in()
    qt.msleep(1)
    
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        turn_off_lasers()
        print n
        qt.instruments[n].set_power(check_power)
        qt.instruments['powermeter'].set_wavelength(qt.instruments[n].get_wavelength()*1e9)
        qt.msleep(1)
        print qt.instruments['powermeter'].get_power(), 'setpoint: ',check_power
    
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
    
def set_laser_powers(names=['MatisseAOM', 'NewfocusAOM','YellowAOM','GreenAOM'], powers=[30e-9,20e-9,100e-9,0]):
    for i,n in enumerate(names):
        qt.instruments[n].set_power(powers[i])
        

speech_lasers={
    'off': 'None',
    'new': 'NewfocusAOM',
    'matter': 'MatisseAOM',
    'yellow' : 'YellowAOM',
    'green'  : 'GreenAOM'
    }        
def listener(command,*arg):
    print 'heard', command
    if command=='off':
        turn_off_lasers()
    else:
        turn_on_laser(speech_lasers[command])
        
def start_listening():
    
    import speech
    speech.stoplistening()
    speech.listenfor([i for i in speech_lasers],listener)      
        
def turn_on_laser(laser):
    las=qt.instruments[laser]
    if np.max(np.abs(las.get_V_min()))>las.get_V_max():
        v=las.get_V_min()
    else:
        v=las.get_V_max()
    las.apply_voltage(v)
