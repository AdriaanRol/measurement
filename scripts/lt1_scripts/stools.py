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
RED1AOM = 'Velocity1AOM'
RED2AOM = 'Velocity2AOM'
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
        

