NewfocusAOM_lt1.set_power(0)
MatisseAOM_lt1.set_power(0)
GreenAOM_lt1.set_power(0)
qt.msleep(1)

for k in arange(1):
    print 'Calibrating NewfocusAOM_lt1 on ADWIN:'
    NewfocusAOM_lt1.calibrate(41)
    NewfocusAOM_lt1.set_power(0)
    NewfocusAOM_lt1.set_cur_controller('AWG')
    print 'Calibrating NewfocusAOM_lt1 on AWG:'
    NewfocusAOM_lt1.calibrate(41)
    NewfocusAOM_lt1.set_power(0)
    NewfocusAOM_lt1.set_cur_controller('ADWIN')
    print 'Calibrating MatisseAOM_lt1:'
    MatisseAOM_lt1.calibrate(41)
    MatisseAOM_lt1.set_power(0)

