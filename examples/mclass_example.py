# demo of the measurment class by wolfgang.
#
import numpy as np


from measurement import measurement

class MyMeasurement(measurement.Measurement):
    
    def setup(self, adwin):
        self.adwin = adwin
        self.measurement_devices.append(adwin)

    def measure(self, **adwinsettings):
        self.adwin.process_params['test1'] = adwinsettings
        self.adwin.process_data['test1'] = ['data_t', 'data_y']
        self.adwin.start_process('test1')

        self.x = np.arange(10)
        self.y = self.x**2

class DummyAdwin:

    def __init__(self):
        self.data_t = np.array([])
        self.data_y = np.array([])

    def start_test1(self, **kw):
        a = kw.get('a', 1)
        f = kw.get('f', 1)
        t0 = kw.get('t0', 0)
        t1 = kw.get('t1', 10)
        pts = kw.get('pts', 101)

        self.data_t = np.linspace(t0,t1,pts)
        self.data_y = np.sin(self.data_t)
    
    def get_test1_var(self, name):
        return getattr(self, name)


params = {}
params['a'] = 0.5
params['f'] = 2.
params['t0'] = 0.
params['t1'] = 5.
params['pts'] = 501

m = MyMeasurement('example', 'DummyMeasurement')
adwin = DummyAdwin()
adwindevice = measurement.AdwinMeasurementDevice(adwin, 'dummy_adwin')

m.setup(adwindevice)
m.measure(**params)
m.save_dataset(data={'x': m.x, 'y':m.y})

print 'all done'





