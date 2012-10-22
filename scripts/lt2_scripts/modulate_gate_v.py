import msvcrt
import qt


voltage=4
factor=1.0


while  msvcrt.kbhit() == 0:

    adwin.set_dac_voltage(('gate',factor*voltage))
    print 'out: ', factor*voltage 
    qt.msleep(.1)
    factor=-(factor)
