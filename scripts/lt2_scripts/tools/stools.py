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
        
    
