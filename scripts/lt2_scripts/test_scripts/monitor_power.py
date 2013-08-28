import qt
import time
import msvcrt

pm = qt.instruments['powermeter_lt1']
# pm_wmpath = qt.instruments['powermeter']
# pm_beforefiber = qt.instruments['powermeter2']
# pm_lt2 = qt.instruments['powermeter_lt2']


tmax = 60 * 60 * 24
t0 = time.time()

d = qt.Data(name='monitor_power')
d.add_coordinate('time (mins)')
#d.add_value('power WM path')
#d.add_value('power before fiber')
d.add_value('power')
# d.add_value('setup temperature')
# d.add_value('absolute time')
# d.add_value('power sample lt2 (NF)')

d.create_file()
p = qt.Plot2D(d, 'b-', coorddim=0, valdim=1, clear=True, name='SP power LT1')
# p.add(d, 'g-', coorddim=0, valdim=2, right=True)

p.set_xlabel('t (mins)')
p.set_ylabel('power (uW)')
# p.set_y2label('T (C)')


qt.mstart()
while t0 + tmax > time.time():
    
    if msvcrt.kbhit():
        break

    d.add_data_point((time.time()-t0)/60., 
            pm.get_power()*1e6)
    
    qt.msleep(5)
    p.update()

qt.mend()
d.close_file()
p.save_png()
