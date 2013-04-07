import qt
import time

pm = qt.instruments['powermeter']
v1aom = qt.instruments['Velocity1AOM']
v2aom = qt.instruments['Velocity2AOM']

tmax = 60 * 60 * 12 
t0 = time.time()

d1 = qt.Data(name='monitor_v1_power')
d1.add_coordinate('time (mins)')
d1.add_value('Velocity1 power (nW)')
d1.create_file()

d2 = qt.Data(name='monitor_v2_power')
d2.add_coordinate('time (mins)')
d2.add_value('Velocity2 power (nW)')
d2.create_file()

p1 = qt.Plot2D(d1, 'b-', coorddim=0, valdim=1, clear=True, name='Monitor Power')
p1.add(d2, 'r-', coordim=0, valdim=1)

p1.set_xlabel('t (mins)')
p1.set_ylabel('power (nW)')


qt.mstart()
while t0 + tmax > time.time():
    
    if msvcrt.kbhit():
        break

    v1aom.set_power(10e-9)
    v2aom.apply_voltage(0)

    qt.msleep(1)
    d1.add_data_point((time.time()-t0)/60., 
            pm.get_power()*1e9)
    qt.msleep(1)

    v1aom.apply_voltage(0)
    v2aom.set_power(10e-9)

    qt.msleep(1)
    d2.add_data_point((time.time()-t0)/60., 
            pm.get_power()*1e9)
    qt.msleep(1)
    
    p1.update()

qt.mend()
d1.close_file()
d2.close_file()
p1.save_png()
