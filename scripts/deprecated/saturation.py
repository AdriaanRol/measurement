import time
import qt
import data
from analysis import fit_oldschool as fit
import matplotlib.pyplot as plt
from numpy import *

#measurement parameters
name = 'SIL9_SM'
steps=20
max_power=500       #[mw]
counter=2           #number of counter
bg_x=3              #delta x position of background [um]
bg_y=0              #delta y position of background [um]
int_time=1000          #integration time [ms] longer than 1000 does not work

#instruments


x = arange(0,steps)
y_NV = zeros(steps,dtype = float)
y_BG = zeros(steps,dtype = float)

current_x = master_of_space.get_x()
current_y = master_of_space.get_y()

GreenAOM.set_power(0)
time.sleep(1)

#adwin.stop_counter()
#time.sleep(1)
#adwin.start_counter(int_time)

for a in x:
    GreenAOM.set_power(float(max_power*1e-6)/(steps-1)*a)
    time.sleep(1)
    y_NV[a] = adwin.get_countrates()[counter-1]
    print 'step %s, counts %s'%(a,y_NV[a])
        
master_of_space.set_x(current_x + bg_x)
master_of_space.set_y(current_y + bg_y)
GreenAOM.set_power(0)
time.sleep(1)

for a in x:
    GreenAOM.set_power(float(max_power*1e-6)/(steps-1)*a)
    time.sleep(1)
    y_BG[a] = adwin.get_countrates()[counter-1]
    print 'step %s, counts %s'%(a,y_BG[a])
        

    
x_axis = x/float(steps-1)*max_power
p_init = [400000, 80]
p_fit = fit.fit_SaturationFunction(x_axis,y_NV-y_BG,p_init)
    
path = 'D:\\measuring\\data'  + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_saturation_'+name+'\\'
if not os.path.isdir(path):
    os.makedirs(path)
result = open(path+'powerdependence_'+name+'.dat', 'w')
result.write('# r_max (cps): %s\n'%p_fit[0][0])
result.write('# p_sat (mW):  %s\n'%(p_fit[0][1]/1000.0))
result.write('\n')
result.write('# P (mW)\tr (cps)\tbg (cps)\tr_NV (cps)\n')
for a in x:
    result.write('%.4f\t%.1f\t%.1f\t%.1f\n'%(x_axis[a]/1000.0,y_NV[a],y_BG[a],(y_NV[a]-y_BG[a])))
result.close()
    
print ('maximum count rate: %.1f cps, saturation power: %.1f microwatt'%(p_fit[0][0],p_fit[0][1]))

fig = plt.figure()
dat = fig.add_subplot(111)
x = x_axis/1000.0
y = y_NV-y_BG
dat = dat.plot(x,y,'r.')
plt.xlabel('Excitation power (mW)')
plt.ylabel('counts / s (background subtracted)')
plt.title('power saturation '+name+',\nP_sat = '+str(int(p_fit[0][1])/1000.0)+'mW, R_sat = '+str(int(p_fit[0][0])   )+' counts/s')
fig.savefig(path + 'powerdependence_'+name+'.png')

master_of_space.set_x(current_x)
master_of_space.set_y(current_y)

#adwin.stop_counter()
#adwin.start_counter(100)
