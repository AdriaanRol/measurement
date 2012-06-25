import time

import qt

T = 10

d = qt.Data(name='pid_newfocus')
d.add_coordinate('t')
d.add_value('ctrl param')
d.add_value('value')
d.add_value('SP')
d.create_file()

plt = qt.Plot2D(d, name='PID ctrl', coorddim=0, valdim=1, clear=True)
plt2 = qt.Plot2D(d, 'kO', name='PID', coorddim=0, valdim=2, clear=True)
plt2.add(d, 'b-', coorddim=0, valdim=3)

pidnewfocus.set_P(4)
pidnewfocus.set_I(200)
pidnewfocus.set_D(0.)

pidnewfocus.set_control_parameter(0.)
pidnewfocus.set_setpoint(470.456281)
pidnewfocus.set_read_interval(0.1)
pidnewfocus.start()

t0 = time.time()
while time.time() < t0 + T:
    #print pidnewfocus.get_control_parameter()
    #print pidnewfocus.get_value()
    #print pidnewfocus.get_setpoint()
    
    d.add_data_point(time.time()-t0, pidnewfocus.get_control_parameter(),
            pidnewfocus.get_value(), pidnewfocus.get_setpoint())
    qt.msleep(0.1)

pidnewfocus.stop()
d.close_file()
