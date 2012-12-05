import msvcrt

cal_lt2=True
lt_1_cal = False
for i in range(1): 

    if cal_lt2:
        AWG.set_runmode('CONT')
        NewfocusAOM.set_power(0)
        MatisseAOM.set_power(0)
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating GreenAOM:'
        GreenAOM.calibrate(51)
        GreenAOM.set_power(0)
        NewfocusAOM.set_cur_controller('ADWIN')
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating NewfocusAOM on ADWIN:'
        NewfocusAOM.calibrate(41)
        NewfocusAOM.set_power(0)
        NewfocusAOM.set_cur_controller('AWG')
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating NewfocusAOM on AWG:'
        NewfocusAOM.calibrate(41)
        NewfocusAOM.set_power(0)
        NewfocusAOM.set_cur_controller('ADWIN')
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating MatisseAOM:'
        MatisseAOM.calibrate(41)
        MatisseAOM.set_power(0)

 
    if lt_1_cal:
        NewfocusAOM_lt1.set_power(0)
        MatisseAOM_lt1.set_power(0)
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating GreenAOM_lt1:'
        GreenAOM_lt1.calibrate(51)
        GreenAOM_lt1.set_power(0)
        NewfocusAOM_lt1.set_cur_controller('ADWIN')
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating NewfocusAOM_lt1 on ADWIN:'
        NewfocusAOM_lt1.calibrate(41)
        NewfocusAOM_lt1.set_power(0)
        NewfocusAOM_lt1.set_cur_controller('AWG')
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating NewfocusAOM_lt1 on AWG:'
        NewfocusAOM_lt1.calibrate(41)
        NewfocusAOM_lt1.set_power(0)
        NewfocusAOM_lt1.set_cur_controller('ADWIN')
        if msvcrt.kbhit() and msvcrt.getch() == "q" : break
        print 'Calibrating MatisseAOM_lt1:'
        MatisseAOM_lt1.calibrate(41)
        MatisseAOM_lt1.set_power(0)
