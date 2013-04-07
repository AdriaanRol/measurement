import qt
import time

pm_afterfiber = qt.instruments['powermeter2']
# pm_wmpath = qt.instruments['powermeter']
# pm_beforefiber = qt.instruments['powermeter2']
tsp = qt.instruments['tsp01']
# pm_lt2 = qt.instruments['powermeter_lt2']


tmax = 60 * 60 * 24
t0 = time.time()

d = qt.Data(name='monitor_power')
d.add_coordinate('time (mins)')
#d.add_value('power WM path')
#d.add_value('power before fiber')
d.add_value('power after fiber')
d.add_value('setup temperature')
# d.add_value('absolute time')
# d.add_value('power sample lt2 (NF)')

d.create_file()
p = qt.Plot2D(d, 'b-', coorddim=0, valdim=1, clear=True, name='Monitor LT1')
p.add(d, 'g-', coorddim=0, valdim=2, right=True)

p.set_xlabel('t (mins)')
p.set_ylabel('power (uW)')
p.set_y2label('T (C)')


qt.mstart()
while t0 + tmax > time.time():
    
    if msvcrt.kbhit():
        break

    d.add_data_point((time.time()-t0)/60., 
            pm_afterfiber.get_power()*1e6,
            tsp.get_probe2_temperature())
    
    qt.msleep(5)
    p.update()

qt.mend()
d.close_file()
p.save_png()
