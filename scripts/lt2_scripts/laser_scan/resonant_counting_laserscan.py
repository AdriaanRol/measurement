###################################
## laserscan with resonant counting
###################################

import msvcrt, time, os, plot
import numpy as np

lt1 = False
Newfocus = True
probe_time = 30             #in ms
counter_par = 41            #LT2 PSB: 41, LT1 PSB: 43
green_power = 300e-6


if lt1:
    print 'LT1'
    ins_adwin = qt.instruments['adwin_lt1']
    measure_adwin = qt.instruments['physical_adwin']
    ins_green_aom = qt.instruments['GreenAOM_lt1']
    ins_matisse_aom = qt.instruments['MatisseAOM_lt1']
    ins_newfocus_aom = qt.instruments['NewfocusAOM_lt1']
    if Newfocus:
        wm_channel = 2
        name = '_newfocus_lt1'
    else:
        wm_channel = 1
        name = '_matisse_lt1'
else:
    print 'LT2'
    ins_adwin = qt.instruments['adwin']
    measure_adwin = qt.instruments['physical_adwin']
    ins_green_aom = qt.instruments['GreenAOM']
    ins_matisse_aom = qt.instruments['MatisseAOM']
    ins_newfocus_aom = qt.instruments['NewfocusAOM']
    if Newfocus:
        wm_channel = 3
        name = '_newfocus_lt2'
    else:
        wm_channel = 1
        name = '_matisse_lt2'

wavemeter.set_active_channel(wm_channel)
ins_newfocus_aom.set_power(0)
ins_matisse_aom.set_power(0)
ins_newfocus_aom.set_cur_controller('ADWIN')
ins_matisse_aom.set_cur_controller('ADWIN')
ins_adwin.set_resonant_counting(aom_voltage = \
        ins_green_aom.power_to_voltage(green_power), probe_duration = 10, \
        red_powers = [20e-9, 15e-9])

f = []          #frequency in GHz
counts = []     #normalized counts in Hz

while not(msvcrt.kbhit()):
    kbchar = msvcrt.getch()
    if kbchar == 'c':
        cont = True
        break
    elif kbchar == 'q':
        cont = False
        break
    print 'Press c to start the scan or q to quit.'
    qt.msleep(1)

if cont:
    print 'Starting scan...'
    while not(msvcrt.kbhit()):
        cur_f = (wavemeter.get_frequency(wm_channel)-470.40)*1E3
        
        cur_counts = 0

        for k in arange(10):
            cur_counts += measure_adwin.Get_Par(counter_par)
            qt.msleep(0.02)
        cur_counts = cur_counts/10.
        
        f.append(cur_f)
        counts.append(cur_counts)

        qt.msleep(probe_time/1E3)

    datfolder = os.path.join('D:\measuring\data',time.strftime('%Y%m%d'),\
            time.strftime('%H%M%S')+'_resonant_couting_scan'+name)

    if not(os.path.isdir(datfolder)):
        os.mkdir(datfolder)

    np.savez(os.path.join(datfolder, 'f_vs_counts.npz'),
            frequency = f,
            counts = counts)

    np.savetxt(os.path.join(datfolder, 'f_vs_counts.txt'),
            transpose((f, counts)),
            newline='\n', delimiter='\t')

    plot1 = plot.Plot2D(f,counts, 'or')
    plot1.set_xlabel('Frequency (GHz)')
    plot1.set_ylabel('Counts')
    plot1.set_plottitle('Resonant counting scan')
    plot1.save_png(os.path.join(datfolder,'f_vs_counts.png'))

ins_adwin.set_simple_counting()
ins_matisse_aom.set_power(0)
ins_newfocus_aom.set_power(0)
ins_green_aom.set_power(200e-6)












