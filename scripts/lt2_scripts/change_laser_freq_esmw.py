import msvcrt

def laser(increment):
    difference = 5.05
    curr_mat_freq = pidmatisse.get_setpoint()
    pidmatisse.set_setpoint(curr_mat_freq+increment)
    pidnewfocus.set_setpoint(curr_mat_freq+increment+difference)

    print 'Matisse = ',pidmatisse.get_setpoint()
    print 'Newfocus = ',pidnewfocus.get_setpoint()
    
def newf_scan(start, stop, steps):
    for k in linspace(start,stop,steps):
        print 'f=',k
        pidnewfocus.set_setpoint(k)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        qt.msleep(0.5)

def mat_scan(start, stop, steps):
    for k in linspace(start,stop,steps):
        print 'f=',k
        pidmatisse.set_setpoint(k)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        qt.msleep(1.5)

def newflt1_scan(start, stop, steps):
    for k in linspace(start,stop,steps):
        print 'f=',k
        pidnewfocus_lt1.set_setpoint(k)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        qt.msleep(1.5)
