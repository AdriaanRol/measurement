import time
import qt
import data
from analysis.lib.fitting import fit, common
from numpy import *
import msvcrt

#measurement parameters
name = '111no2_Sil2_ZPL_SM_lt3'
steps=31
max_power=270e-6       #[w]
counter=2    #number of counter
TH_count=False    # counting with the HH, assumes apd on channel 0
bg_x=3.0          #delta x position of background [um]
bg_y=3.0             #delta y position of background [um]

#instruments
if TH_count:
    current_HH_400=qt.instruments['TH_260N']

current_aom = qt.instruments['GreenAOM']
current_mos = qt.instruments['master_of_space']
current_adwin = qt.instruments['adwin']

x = linspace(0,max_power,steps)
y_NV = zeros(steps,dtype = float)
y_BG = zeros(steps,dtype = float)

current_x = current_mos.get_x()
current_y = current_mos.get_y()

current_aom.set_power(0)
time.sleep(1)

for i,pwr in enumerate(x):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
    current_aom.set_power(pwr)
    time.sleep(1)
    if not TH_count:
        y_NV[i] = current_adwin.get_countrates()[counter-1]
    else:
        y_NV[i] = current_HH_400.get_CountRate0()
    print 'step %s, counts %s'%(i,y_NV[i])
        
current_mos.set_x(current_x + bg_x)
current_mos.set_y(current_y + bg_y)
current_aom.set_power(0)
time.sleep(1)

for i,pwr in enumerate(x):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
    current_aom.set_power(pwr)
    time.sleep(1)
    if not TH_count:
        y_BG[i] = current_adwin.get_countrates()[counter-1]
    else:
        y_BG[i] = current_HH_400.get_CountRate0()
    print 'step %s, counts %s'%(i,y_BG[i])
       
 
x_axis = x*1e6

A, sat = max(y_NV-y_BG), .5*max_power*1e6
fitres = fit.fit1d(x_axis,y_NV-y_BG, common.fit_saturation, 
        A, sat, do_print=True, do_plot=False, ret=True)

dat = qt.Data(name='Saturation_curve_'+name)
dat.create_file()
dat.add_coordinate('Power [uW]')
dat.add_value('Counts [Hz]')
dat.add_value('Counts fitted [Hz]')
plt = qt.Plot2D(dat, 'rO', name='Saturation curve', coorddim=0, valdim=1, clear=True)
plt.add_data(dat, coorddim=0, valdim=2)
fd = zeros(len(x_axis))    
if type(fitres) != type(False):
    fd = fitres['fitfunc'](x_axis)
    plt.set_plottitle('Saturation counts: {:d}, saturation power: {:.2f} uW'.format(int(fitres['params_dict']['A']),fitres['params_dict']['xsat']))
else:
    print 'could not fit calibration curve!'

dat.add_data_point(x_axis,y_NV-y_BG,fd)
plt.set_legend(False)

plt.save_png(dat.get_filepath()+'png')
dat.close_file()

current_mos.set_x(current_x)
current_mos.set_y(current_y)

