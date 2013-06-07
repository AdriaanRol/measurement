# module for visualizing sequences.
#
# author: Wolfgang Pfaff

import numpy as np
from matplotlib import pyplot as plt

def show_wf(tvals, wf, name='', ax=None, ret=None, dt=None):

    if ax == None:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    if dt == None:
        dt = tvals[1]-tvals[0]  
    
    # ax.bar(tvals, wf, width=dt, linewidth=0, alpha=0.5)
    ax.step(np.append(tvals, 2*tvals[-1]-tvals[-2]), 
        np.append(wf,0), 'b-', where='post')
    
    ax.set_xlim(tvals[0], 2*tvals[-1]-tvals[-2])
    ax.set_ylabel(name + ' Amplitude')

    if ret=='ax':
        return ax
    else:
        return None

def show_element(element, delay=True):
    tvals, wfs = element.waveforms()
    cnt = len(wfs)
    i = 0

    fig, axs = plt.subplots(cnt, 1, sharex=True)
    t0 = 0
    t1 = 0

    for wf in wfs:
        i += 1
        hi = element._channels[wf]['high']
        lo = element._channels[wf]['low']
        
        # some prettifying
        ax = axs[i-1]
        ax.set_axis_bgcolor('gray')
        ax.axhspan(lo, hi, facecolor='w', linewidth=0)

        # the waveform
        if delay:
            t = tvals
        else:
            t = element.real_times(tvals, wf)

        t0 = min(t0, t[0])
        t1 = max(t1, t[-1])

        # TODO style options
        show_wf(t, wfs[wf], name=wf, ax=ax, dt=1./element.clock)

        # a reasonable range
        y0,y1 = ax.get_ylim()
        dy = y1 - y0
        ax.set_ylim(y0 - dy*0.1, y1 + dy*0.1)

        if i == cnt:
            ax.set_xlabel('Time')
            ax.set_xlim(t0,t1)





