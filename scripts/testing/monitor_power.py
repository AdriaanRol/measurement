import qt
import time
import msvcrt

pm = qt.instruments['powermeter']

tmax = 180
t0 = time.time()
tsleep = 0.1

d = qt.Data(name='monitor_power')
d.add_coordinate('time (s)')
d.add_value('power (W)')

d.create_file()
p = qt.Plot2D(d, 'b-', coorddim=0, valdim=1, clear=True, name='Opt Power')
p.set_xlabel('t (s)')
p.set_ylabel('power (W)')


qt.mstart()
while t0 + tmax > time.time():
    
    if msvcrt.kbhit():
        break

    d.add_data_point((time.time()-t0), 
            pm.get_power())
    
    qt.msleep(tsleep)
    p.update()

qt.mend()
d.close_file()
p.save_png()
