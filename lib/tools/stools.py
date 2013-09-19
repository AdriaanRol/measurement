import qt
import numpy as np
import msvcrt

def set_simple_counting(adwin='adwin'):
    qt.instruments[adwin].set_simple_counting()

def turn_off_lasers(names):
    for l in names:
        qt.instruments[l].turn_off()

def recalibrate_laser(name, servo, adwin, awg=False):
    qt.instruments[adwin].set_simple_counting()    
    if servo != None:
        qt.instruments[servo].move_in()
        qt.msleep(0.5) 

    qt.msleep(1)
    print 'Calibrate', name
    qt.instruments[name].apply_voltage(0)
    if awg: qt.instruments[name].set_cur_controller('AWG')
    qt.instruments[name].calibrate(31)
    qt.instruments[name].apply_voltage(0)
    if awg: qt.instruments[name].set_cur_controller('ADWIN')
    qt.msleep(1)

    qt.instruments[name].apply_voltage(0)
    
    if servo != None:
        qt.instruments[servo].move_out()
        qt.msleep(1)

def check_power(name, setpoint, adwin, powermeter, servo=None):
    qt.instruments[adwin].set_simple_counting()    
    if servo != None:
        qt.instruments[servo].move_in()
        qt.msleep(0.5) 
    
    qt.instruments[powermeter].set_wavelength(qt.instruments[name].get_wavelength())
    qt.instruments[name].set_power(setpoint)
    qt.msleep(1)

    print name, 'setpoint:', setpoint, 'value:', qt.instruments[powermeter].get_power()

    qt.instruments[name].apply_voltage(0)
    
    if servo != None:
        qt.instruments[servo].move_out()
        qt.msleep(1)

def check_max_power(name, adwin, powermeter, servo=None):
    qt.instruments[adwin].set_simple_counting()    
    if servo != None:
        qt.instruments[servo].move_in()
        qt.msleep(0.5)

    qt.instruments[name].turn_on()
    qt.instruments[powermeter].set_wavelength(qt.instruments[name].get_wavelength())
    qt.msleep(1)
    
    print name, 'max. power:', qt.instruments[powermeter].get_power()
    qt.instruments[name].turn_off()

    if servo != None:
        qt.instruments[servo].move_out()
        qt.msleep(1)

def apply_awg_voltage(awg, chan, voltage):
    """
    applies a voltage on an awg channel;
    if its a marker, by setting its LO-value to the given voltage.
    if an analog channel, by setting the offset.
    """
    if 'marker' in chan:
        return getattr(qt.instruments[awg], 'set_{}_low'.format(chan))(voltage)
    else:
        return getattr(qt.instruments[awg], 'set_{}_offset'.format(chan))(voltage)


