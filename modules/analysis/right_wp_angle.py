import numpy as np
try:
    import speech
except: pass

def get_rightwpangle(fig=True):
    try:
        t2piEx = float(raw_input('Oscillation period (ns) with Ex: '))
        t2piEy = float(raw_input('Oscillation period (ns) with Ey: '))
    except: 
        proceed = False
        print 'Could not understand input'

    ratio = t2piEx/t2piEy
    x = np.linspace(0,np.pi/2.,500)
    y = np.cos(x)/np.sin(x)

    def find_nearest(array,value):
        idx=(np.abs(array-value)).argmin()
        return idx
    

    if fig:
        plt.figure()
        plt.plot(x/np.pi,y,'-k', lw = 2.0,
                label = 'Theoretical curve')
        plt.ylabel('Ratio between the two periods: $E_x/E_y$')
        plt.xlabel('Excitation angle w.r.t. dipole orientation of $E_x$ in units of $\pi$')
        plt.plot(x[find_nearest(y,ratio)]/np.pi, ratio, 'or',
                label = 'Ratio from measured oscillation periods')
        plt.plot(np.array([0.25, 0.25]), np.array([0,5]), 'r', lw = 1.5,
                label = 'Point for 45$^\circ$ excitation')
        plt.ylim(0,5)
        plt.legend(shadow = True, fancybox = True)
        plt.title('')
        
    dif = 0.25*np.pi-x[find_nearest(y,ratio)]

    outcome = 'Rotate the waveplate angle by %s degrees for 45 degrees excitation.'%(dif/(2*np.pi)*180)
    
    print outcome

    return
        
