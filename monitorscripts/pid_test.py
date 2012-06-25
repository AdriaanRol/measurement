import time

import qt

T = 10

d = qt.Data(name='pid_testing')
d.add_coordinate('t')
d.add_value('ctrl param')
d.add_value('value')
d.add_value('SP')
d.create_file()

plt = qt.Plot2D(d, name='PID', coorddim=0, valdim=1, clear=True)
plt.add(d, 'kO', coorddim=0, valdim=2)
plt.add(d, coorddim=0, valdim=3)

pidtest.set_P(-0.004)
pidtest.set_I(-0.01)
pidtest.set_D(0.)

pidtest.set_control_parameter(0.)
pidtest.set_setpoint(-100)
pidtest.set_read_interval(0.1)
pidtest.start()

t0 = time.time()
while time.time() < t0 + T:
    d.add_data_point(time.time()-t0, pidtest.get_control_parameter(),
            pidtest.get_value(), pidtest.get_setpoint())
    qt.msleep(0.1)

pidtest.stop()
d.close_file()
