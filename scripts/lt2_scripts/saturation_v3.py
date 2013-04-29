import time
import qt
import data
from analysis.lib.fitting import fit, common
import matplotlib.pyplot as plt
from numpy import *

#measurement parameters
name = 'LT2-Sil9-PSB-FS-APD'
steps=31
max_power=350e-6       #[w]
counter=1      #number of counter
HH_count=True    # counting with the HH, assumes apd on channel 0
bg_x=2          #delta x position of background [um]
bg_y=2             #delta y position of background [um]
LT1 = False

#instruments


if LT1:
    current_aom = GreenAOM_lt1
    current_mos = master_of_space_lt1
    current_adwin = adwin_lt1
else:
    current_aom = GreenAOM
    current_mos = master_of_space
    current_adwin = adwin



x = arange(0,steps)
y_NV = zeros(steps,dtype = float)
y_BG = zeros(steps,dtype = float)

current_x = current_mos.get_x()
current_y = current_mos.get_y()

current_aom.set_power(0)
time.sleep(1)

for a in x:
    current_aom.set_power(float(max_power)/(steps-1)*a)
    time.sleep(1)
    if not HH_count:
        y_NV[a] = current_adwin.get_countrates()[counter-1]
    else:
        y_NV[a] = HH_400.get_CountRate0()
    print 'step %s, counts %s'%(a,y_NV[a])
        
current_mos.set_x(current_x + bg_x)
current_mos.set_y(current_y + bg_y)
current_aom.set_power(0)
time.sleep(1)

for a in x:
    current_aom.set_power(float(max_power)/(steps-1)*a)
    time.sleep(1)
    if not HH_count:
        y_BG[a] = current_adwin.get_countrates()[counter-1]
    else:
        y_BG[a] = HH_400.get_CountRate0()
    print 'step %s, counts %s'%(a,y_BG[a])
        
   
x_axis = x/float(steps-1)*max_power*1e6

A, sat = max(y_NV-y_BG), .5*max_power*1e6
fitres = fit.fit1d(x_axis,y_NV-y_BG, common.fit_saturation, 
        A, sat, do_print=True, do_plot=False, ret=True)

dat = qt.Data(name='Saturation_curve_'+name)
dat.create_file()
dat.add_coordinate('Power [uW]')
dat.add_value('Counts [Hz]')
plt = qt.Plot2D(dat, 'rO', name='Saturation curve', coorddim=0, valdim=1, clear=True)
fd = zeros(len(x_axis))        
if type(fitres) != type(False):
    p1 = fitres['params_dict']
    fit_A = p1['A']
    fit_sat = p1['xsat']
    #fd = fitres['fitdata']
    
    print ('maximum count rate: %.1f cps, saturation power: %.1f microwatt'%(fit_A,fit_sat))
   
    dat.add_value('fit')
    plt.add_data(dat, coorddim=0, valdim=2)
    dat.add_data_point(x_axis,y_NV-y_BG,fd)

    plt.set_plottitle('power saturation '+name+', P_sat = '+str(int(fit_sat))+'uW, R_sat = '+str(int(A))+' counts/s')

else:
    dat.add_data_point(x_axis,y_NV-y_BG)
    print 'could not fit calibration curve!'
plt.set_legend(False)
plt.save_png(dat.get_filepath()+'png')
dat.close_file()

current_mos.set_x(current_x)
current_mos.set_y(current_y)

