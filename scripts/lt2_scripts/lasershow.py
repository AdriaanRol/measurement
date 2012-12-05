import msvcrt
for i in range(100):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        break
    GreenAOM.set_power(i*1e-6)
    qt.msleep(0.1)
    MatisseAOM.set_power(15e-9)
    qt.msleep(0.1)
    GreenAOM.set_power(0)
    qt.msleep(0.1)
    MatisseAOM.set_power(0)
    qt.msleep(0.1)
