import time
import qt
import data
from analysis import fit, common
import matplotlib.pyplot as plt
from numpy import *

#measurement parameters
name = 'SIL9-ZPL'
steps=20
max_power=500e-6       #[w]
counter=2          #number of counter
bg_x=2            #delta x position of background [um]
bg_y=0             #delta y position of background [um]
int_time=1000          #integration time [ms] longer than 1000 does not work
mw = False
mw_power = 15
mw_frq = 2.878e9
#instruments
current_aom = GreenAOM




x = arange(0,steps)
y_NV = zeros(steps,dtype = float)
y_BG = zeros(steps,dtype = float)

current_x = master_of_space.get_x()
current_y = master_of_space.get_y()

current_aom.set_power(0)
time.sleep(1)

#adwin.stop_counter()
#time.sleep(1)
#adwin.start_counter(int_time)

if mw:
    SMB100.set_iq('off')
    SMB100.set_pulm('off')
    SMB100.set_power(mw_power)
    SMB100.set_frequency(mw_frq)
    SMB100.set_status('on')


for a in x:
    current_aom.set_power(float(max_power)/(steps-1)*a)
    time.sleep(1)
    y_NV[a] = adwin.get_countrates()[counter-1]
    print 'step %s, counts %s'%(a,y_NV[a])
        
master_of_space.set_x(current_x + bg_x)
master_of_space.set_y(current_y + bg_y)
current_aom.set_power(0)
time.sleep(1)

for a in x:
    current_aom.set_power(float(max_power)/(steps-1)*a)
    time.sleep(1)
    y_BG[a] = adwin.get_countrates()[counter-1]
    print 'step %s, counts %s'%(a,y_BG[a])
        
if mw:
    SMB100.set_status('off')

#path = 'D:\\measuring\\data'  + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_saturation_'+name+'\\'
#if not os.path.isdir(path):
#    os.makedirs(path)
    
x_axis = x/float(steps-1)*max_power*1e6
#p_init = [400000, 80]
#p_fit = fit.fit_SaturationFunction(x_axis,y_NV-y_BG,p_init)
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
    fd = fitres['fitdata']
    
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

#result = open(path+'powerdependence_'+name+'.dat', 'w')
#result.write('# r_max (cps): %s\n'%fit_A)
#result.write('# p_sat (mW):  %s\n'%fit_sat)
#result.write('\n')
#result.write('# P (mW)\tr (cps)\tbg (cps)\tr_NV (cps)\n')
#for a in x:
#    result.write('%.4f\t%.1f\t%.1f\t%.1f\n'%(x_axis[a]/1000.0,y_NV[a],y_BG[a],(y_NV[a]-y_BG[a])))
#result.close()
    
#fig = plt.figure()

#dat = fig.add_subplot(111)
#x = x_axis/1000.0
#y = y_NV-y_BG
#dat = dat.plot(x,y,'r.')
#plt.xlabel('Excitation power (mW)')
#plt.ylabel('counts / s (background subtracted)')
#plt.title('power saturation '+name+',\nP_sat = '+str(int(p_fit[0][1])/1000.0)+'mW, R_sat = '+str(int(p_fit[0][0])   )+' counts/s')
#fig.savefig(path + 'powerdependence_'+name+'.png')

master_of_space.set_x(current_x)
master_of_space.set_y(current_y)

