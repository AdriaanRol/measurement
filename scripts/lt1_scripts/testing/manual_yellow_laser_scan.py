import qt
import time

## this is just a script that records the wavemeter channel of the IR and records
## countrates. real measurements will follow once the yellow laser is fully
## integrated with the adwin

wm = qt.instruments['wavemeter']
ctr = qt.instruments['counters']

#### Settings
frq_offset = 260.61 #offset of the IR in THz



tmax = 20*60 
t0 = time.time()

d = qt.Data(name='yellow_laser_scan_test')


d.add_coordinate('time (ms)')
d.add_value('IR frequency (GHz)')
d.add_value('resonant count rate')


d.create_file()

p = qt.Plot2D(d, 'b-', coorddim=0, valdim=1, clear=True, name='Yellow_Laser_Scan')
p.add(d, 'g-', coorddim=0, valdim=2, right=True)

p.set_xlabel('time (ms)')
p.set_ylabel('frequency (GHz)')
p.set_y2label('counts')

qt.mstart()
while t0 + tmax > time.time():
    
    if msvcrt.kbhit(): 
        break

    d.add_data_point((time.time()-t0)*1000,
                    (wm.get_channel_frequency(3)-frq_offset)*1000,
                    ctr.get_cntr1_countrate()
                    )
    
    qt.msleep(0.1)
    p.update()

qt.mend()
d.close_file()
p.save_png()
