import numpy as np
from matplotlib import pyplot as plt

def plot_the_shit():
    
    print 1
    f = np.load('LDESpinPhotonCorr-000.npz')
    dstate = f['adwin_lt2_state']
    dssro = f['adwin_lt2_SSRO']
    print 2
    while dssro[-1]==0: dssro=dssro[:-1]

    f.close()

    dstate = dstate[:len(dssro)]
    dstate = dstate/max(dstate) #array with 0 and 1

    select ro data according to which window...
    idx0 = -1
    idx1 = -1
    for k in np.arange(dssro):
        if dstate == 1:
            idx1 += 1
            first_window[idx1] = dssro[k]
        else:
            idx0 += 1
            second_window[idx0] = dssro[k]
        
        print k
            

    #ssro_first_window = dssro[dstate == 1]
    #ssro_second_window = dssro[dstate == 0]

    #print len(ssro_first_window)

    #zero_first_window = ssro_first_window[ssro_first_window == 0]
    #one_first_window = ssro_first_window[ssro_first_window >= 1]

    #print len(one_first_window)
    
    #noof_events_zero_first_window = len(zero_first_window)
    #noof_events_one_first_window = len(one_first_window)

    #print noof_events_zero_first_window
    #print noof_events_one_first_window 

    #zero_second_window = ssro_second_window[ssro_second_window == 0]
    #one_second_window = ssro_second_window[ssro_second_window >= 1]

    #noof_events_zero_second_window = len(zero_second_window)
    #noof_events_one_second_window = len(one_second_window)
    
    #print noof_events_zero_second_window
    #print noof_events_one_second_window

    print 3

    #plt.figure()

    #plt.subplot(121)
    #plt.title('First window')
    #plt.bar([0,1], [noof_events_zero_first_window, noof_events_one_first_window],
    #        align = 'center')
    #plt.xticks([0,1],['0','>1'])
    
    print 4

    #plt.subplot(122)
    #plt.title('Second window')
    #plt.bar([0,1], [noof_events_zero_second_window,noof_events_one_second_window],
    #        align = 'center')    
    #plt.xticks([0,1],['0','>1'])

plot_the_shit()

