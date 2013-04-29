import numpy as np
import qt

def sweep_setpoint(ins, start, stop, pts, delay=0.5):    
    for p in np.linspace(start, stop, pts):
        print 'setpoint:', p

        qt.instruments[ins].set_setpoint(p)
        qt.msleep(delay)

    return

