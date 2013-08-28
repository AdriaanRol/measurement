import qt
import numpy as np
import msvcrt

def set_simple_counting(adwins=['adwin', 'adwin_lt1']):
    for adwin in adwins:
        qt.instruments[adwin].set_simple_counting()

def turn_off_lasers(names):
    for l in names:
        qt.instruments[l].apply_voltage(0)

def turn_off_all_lt1_lasers():
    set_simple_counting(['adwin_lt1'])
    turn_off_lasers(['GreenAOM_lt1', 'MatisseAOM_lt1', 'NewfocusAOM_lt1', 'YellowAOM_lt1'])

def turn_off_all_lt2_lasers():
    set_simple_counting(['adwin'])
    turn_off_lasers(['MatisseAOM', 'NewfocusAOM','GreenAOM'])

def turn_off_all_lasers():
    turn_off_all_lt1_lasers()
    turn_off_all_lt2_lasers()

def recalibrate_laser(name, servo, adwin,awg=False):
    qt.instruments[adwin].set_simple_counting()
    qt.instruments[servo].move_in()
    qt.msleep(1)

    qt.msleep(0.1)
    print 'Calibrate', name
    qt.instruments[name].apply_voltage(0)
    if awg: qt.instruments[name].set_cur_controller('AWG')
    qt.instruments[name].calibrate(31)
    qt.instruments[name].apply_voltage(0)
    if awg: qt.instruments[name].set_cur_controller('ADWIN')
    qt.msleep(1)

    qt.instruments[name].apply_voltage(0)
    qt.instruments[servo].move_out()
    qt.msleep(1)

def recalibrate_lt1_lasers(names=['GreenAOM_lt1', 'MatisseAOM_lt1', 'NewfocusAOM_lt1', 'YellowAOM_lt1'], 
        awg_names=['NewfocusAOM_lt1', 'YellowAOM_lt1']):
    turn_off_all_lt1_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo_lt1', 'adwin_lt1')
    for n in awg_names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo_lt1', 'adwin_lt1',awg=True)

def recalibrate_lt2_lasers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM'], awg_names=['NewfocusAOM']):
    turn_off_all_lt2_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo', 'adwin')
    for n in awg_names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo', 'adwin',awg=True)


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
    setpoints = [50e-6, 5e-9, 100e-9, 50e-9]):
    
    turn_off_all_lt1_lasers()
    for n,s in zip(names, setpoints):
        check_power(n, s, 'adwin_lt1', 'powermeter_lt1', 'PMServo_lt1')

def check_lt2_powers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM'],
    setpoints = [10e-9, 20e-9, 50e-6]):
    
    turn_off_all_lt2_lasers()
    for n,s in zip(names, setpoints):
        check_power(n, s, 'adwin', 'powermeter', 'PMServo')
        
def disconnect_lt1_remote():
    for i in qt.instruments.get_instrument_names():
        if len(i) >= 4 and i[-4:] == '_lt1':
            qt.instruments.remove(i)

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


def check_fast_path_power(powermeter, servo, awg='AWG', chan='ch4_marker1',
    voltage=1.0, off_voltage=0.02, ret=False):

    qt.instruments[powermeter].set_wavelength(637e-9)
    qt.instruments[servo].move_in()
    qt.msleep(1)
    apply_awg_voltage(awg, chan, voltage)
    qt.msleep(0.1)

    pwr = qt.instruments[powermeter].get_power()
    print 'Fast path power; {}: {:.3f} uW'.format(powermeter, pwr * 1e6)

    apply_awg_voltage(awg, chan, off_voltage)
    qt.msleep(0.1)
    qt.instruments[servo].move_out()
    qt.msleep(1)

    if ret:
        return pwr

def check_fast_path_power_lt1(ret=False, **kw):
    turn_off_all_lt1_lasers()
    pwr = check_fast_path_power('powermeter_lt1', 'PMServo_lt1', ret=ret, **kw)
    if ret:
        return pwr

def check_fast_path_power_lt2(ret=False, **kw):
    turn_off_all_lt2_lasers()
    pwr = check_fast_path_power('powermeter', 'PMServo', ret=ret, **kw)
    if ret:
        return pwr

def set_lt1_optimization_powers():
    turn_off_all_lt1_lasers()
    qt.instruments['YellowAOM_lt1'].set_power(50e-9)
    qt.instruments['MatisseAOM_lt1'].set_power(5e-9)
    qt.instruments['NewfocusAOM_lt1'].set_power(10e-9)











