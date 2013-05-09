# import matplotlib.pyplot as plt
import time
import qt

#adapted for the beam splitter!!!

#Measure the contribution to the counts on the ZPL and the PSB as a function of
#the red laser power. Note that the green laser power should be set to a saturation value.

power_init = 0e-9
power_step = 2e-9 #red power increment in Watt
maxcounts = 1e6 #SAVE THE PRECIOUS APDs!!! DO NOT ADJUST
n_steps = 20 #number of steps of value power_step
reps = 40 #number of repetitions per data point (integration time)
t_sleep_reps = 0.05 #time interval between repetitions

maxredpower = n_steps*power_step
maxcalibratedredpower = NewfocusAOM.get_cal_a()

if maxredpower > maxcalibratedredpower:
    print 'WARNING: script tries to exceed maximum red power'

power_vs_counts = zeros([n_steps, 3])

data = qt.Data(name = 'influence_redlaser')
data.add_coordinate('Red laser power (W)')
data.add_value('PSB counts')
data.add_value('ZPL counts')

data.create_file()

plt = qt.Plot2D(data, '-ob', name='psb_counts_vs_redlaser_power', coorddim=0, valdim=1, clear=True)
file_directory = data.get_filepath()



plt2 = qt.Plot2D(data, '-ob', name='zpl_counts_vs_redlaser_power', coorddim=0, valdim=2, clear=True)
qt.Plot2D.set_datastyle(plt2,'points')

def get_counts(repetitions = reps, t_sleep = t_sleep_reps):
    
    cum_cts_zpl = 0
    cum_cts_psb = 0

    for k in arange(repetitions):
        cum_cts_zpl = cum_cts_zpl + adwin.get_countrates()[1] + adwin_lt1.get_countrates()[0]
        cum_cts_psb = cum_cts_psb + adwin.get_countrates()[0] 
        qt.msleep(t_sleep)
    
    zpl_counts = cum_cts_zpl/reps
    psb_counts = cum_cts_psb/reps

    return zpl_counts, psb_counts


for i in range(n_steps):
    power = power_init + i*power_step 
    if counts_PSB < maxcounts and counts_ZPL < maxcounts:
        NewfocusAOM.set_power(power)
        zpl_counts, psb_counts = get_counts()    
    else:
        NewfocusAOM.set_power(power_init)
        break

    #save the data in an array
#    power_vs_counts[i,0] = power
#    power_vs_counts[i,1] = psb_counts
#    power_vs_counts[i,2] = counts_ZPL    
    
    #add data point
    data.add_data_point(power, psb_counts, zpl_counts)
    

data.close_file()

NewfocusAOM.set_power(power_init)

plt.save_png(file_directory[0:62]+'psb_counts_vs_redlaser_power.png')
plt2.save_png(file_directory[0:62]+'zpl_counts_vs_redlaser_power.png')
    
