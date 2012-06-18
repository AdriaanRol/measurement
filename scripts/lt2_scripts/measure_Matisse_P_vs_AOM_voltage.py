# shortcuts for functions to set voltage and get power
set_v = AWG.set_ch2_offset
get_p = PM.get_power
title = 'Matisse'

v_start = 0.5
v_stop = 1.0
v_steps = 51
reps = 3
wait = 0.1 # seconds

# imports
import time
import qt
from matplotlib import pyplot as plt

# prep data
v_vals = linspace(v_start, v_stop, v_steps)
data = zeros((reps, v_steps))

for i in range(reps):
    
    print 'start repetition %d/%d' % (i+1, len(range(reps)))

    for j,v in enumerate(v_vals):

        print 'set AOM voltage %.2f (%d/%d)' % (v, j+1, len(v_vals)) ,

        set_v(v)
        time.sleep(0.5)
        
        data[i,j] = get_p()*1e9 - bg
        print ' ... P = ', data[i,j], 'nW' 
        time.sleep(0.1)

    time.sleep(wait)

mean = zeros(v_steps)
error = zeros(v_steps)
for i,v in enumerate(v_vals):
    mean[i] = average(data[:,i])
    error[i] = std(data[:,i])

# saves the data in nanowatts
name = '%s_AOM_voltage_vs_red_power_%s' % (time.strftime('%H%M%S'), title)
folder = os.path.join(qt.config['datadir'], time.strftime('%Y%m%d'), name)
if not os.path.exists(folder):
    os.makedirs(folder)

savez(os.path.join(folder,name), voltage=v_vals, power=mean, 
        power_err=error)
f = plt.figure()
plt.errorbar(v_vals, mean, fmt='o', yerr=error)
plt.xlabel('AOM voltage [V]')
plt.ylabel('P [nW]')
f.savefig(os.path.join(folder, name+'.pdf'), format='pdf')
plt.close('all')
    


