import qt
import numpy as np
import msvcrt

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
    

        
    
