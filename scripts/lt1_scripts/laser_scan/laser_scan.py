import msvcrt
import qt
import numpy as np
import measurement.lib.config.adwins as adwins_cfg

class LaserFrequencyScan:

    mprefix = 'LaserFrequencyScan'
    

    def __init__(self, name):
        self.name = name
        
        self.set_laser_power = None
        self.set_repump_power = None
        self.set_laser_voltage = None   # callable with voltage as argument
        self.get_frequency = None       # callable with WM channel as argument
        self.get_counts = None          # callable with integration time as argument,
                                        # returning an array (one val per
                                        # channel)
        self.get_laser_voltage = None

    def repump_pulse(self, duration):
        self.set_repump_power(self.repump_power)
        qt.msleep(duration)
        self.set_repump_power(0)
    
    def scan_to_voltage(self, voltage, pts=51, dwell_time=0.05):
        print 'scan to voltage ...',
        
        print self.get_laser_voltage()
        for v in np.linspace(self.get_laser_voltage(), voltage, pts):
            self.set_laser_voltage(v)
            qt.msleep(dwell_time)

        print 'done.'
    
    def prepare_scan(self):
        pass

    def finish_scan(self):
        pass    
    
    def run_scan(self, **kw):
        stabilizing_time = kw.pop('stabilizing_time', 0.01)

        d = qt.Data(name=self.mprefix+'_'+self.name)
        d.add_coordinate('Voltage (V)')
        d.add_coordinate('Frequency (GHz)')
        d.add_coordinate('Counts')

        p = qt.Plot2D(d, 'ro', title='Frq (left) vs Voltage (bottom)', plottitle=self.mprefix,
                name='Laser Scan', clear=True, xlabel='Voltage (V)', 
                ylabel='Frequency (GHz)', coorddim=0, valdim=1)
        p.add(d, 'bo', title='Counts (right) vs Frq (top)', coorddim=1, valdim=2,
                right=True, top=True)
        p.set_x2tics(True)
        p.set_y2tics(True)
        p.set_x2label('Frequency (GHz)')
        p.set_y2label('Counts')

        qt.mstart()

        if not self.use_repump_during:
            self.repump_pulse(self.repump_duration)
        
        for v in np.linspace(self.start_voltage, self.stop_voltage, self.pts):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
            
            self.set_laser_voltage(v)
            qt.msleep(stabilizing_time)

            cts = self.get_counts(self.integration_time)[self.counter_channel]
            frq = self.get_frequency(self.wm_channel)*self.frq_factor - self.frq_offset
            d.add_data_point(v, frq, cts)
            p.update()

        qt.mend()
        d.close_file()

        p.save_png()


class AdwinLaserScan(LaserFrequencyScan):
    def __init__(self, name):
        LaserFrequencyScan.__init__(self, name)

        self.adwin = qt.instruments['adwin']
        self.mw = qt.instruments['SMB100']

        self.set_laser_power = qt.instruments['Velocity1AOM'].set_power
        self.set_repump_power = qt.instruments['GreenAOM'].set_power
        self.set_laser_voltage = lambda x: self.adwin.set_dac_voltage(
                ('velocity1_frq', x))
        self.get_laser_voltage = lambda : self.adwin.get_dac_voltage(
                'velocity1_frq')
        self.get_frequency = lambda x : \
                qt.instruments['wavemeter'].get_channel_frequency(x) * 1e3
        self.get_counts = self.adwin.measure_counts

    def prepare_scan(self):

        if self.use_repump_during:
            self.set_repump_power(self.repump_power_during)
        
        if self.use_mw:
            self.mw.set_frequency(self.mw_frq)
            self.mw.set_power(self.mw_power)
            self.mw.set_pulm('off')
            self.mw.set_iq('off')
            self.mw.set_status('on')

        self.scan_to_voltage(self.start_voltage)
        self.set_laser_power(self.laser_power)

    def finish_scan(self):
        self.set_laser_power(0)

        if self.use_mw:
            self.mw.set_status('off')

        if self.use_repump_during:
            self.set_repump_power(0)

class LabjackLaserScan(LaserFrequencyScan):
    def __init__(self, name, labjack_dac_nr):
        LaserFrequencyScan.__init__(self, name)

        self.labjack = qt.instruments['labjack']
        self.adwin = qt.instruments['adwin']
        self.mw = qt.instruments['SMB100']

        self.set_laser_power = qt.instruments['Velocity2AOM'].set_power
        self.set_repump_power = qt.instruments['GreenAOM'].set_power
        self.set_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(labjack_dac_nr)](x)
        self.get_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(labjack_dac_nr)]()
        self.get_frequency = lambda x : \
                qt.instruments['wavemeter'].get_channel_frequency(x) * 1e3
        self.get_counts = self.adwin.measure_counts

    def prepare_scan(self):

        if self.use_repump_during:
            self.set_repump_power(self.repump_power_during)
        
        if self.use_mw:
            self.mw.set_frequency(self.mw_frq)
            self.mw.set_power(self.mw_power)
            self.mw.set_pulm('off')
            self.mw.set_iq('off')
            self.mw.set_status('on')

        self.scan_to_voltage(self.start_voltage)
        self.set_laser_power(self.laser_power)

    def finish_scan(self):
        self.set_laser_power(0)

        if self.use_mw:
            self.mw.set_status('off')

        if self.use_repump_during:
            self.set_repump_power(0)

        qt.instruments['counters'].set_is_running(True)
        qt.instruments['GreenAOM'].set_power(10e-6)

def adwin_laser_scan(name):
    m = AdwinLaserScan(name)
    
    m.frq_offset = 470400
    m.frq_factor = 1

    # HW setup
    m.use_mw = True
    m.mw_frq = 2.863e9
    m.mw_power = -8
    m.repump_power = 100e-6
    m.laser_power = 5e-9
    m.repump_duration = 1 # seconds
    m.counter_channel = 0
    m.wm_channel = 2
    m.use_repump_during = False
    m.repump_power_during = 0.1e-6
    
    # sweep
    m.start_voltage = 1
    m.stop_voltage = -0.3
    m.pts = 1001
    m.integration_time = 20 # ms

    m.prepare_scan()
    m.run_scan()
    m.finish_scan()

def labjack_laser_scan(name):
    labjack_dac_channel=6 #6 is coarse, 7 is fine for NF1 LT1
    m = LabjackLaserScan(name,labjack_dac_channel)

    m.frq_offset = 470400 # red 470400
    m.frq_factor = 1 #red 1

    # HW setup
    m.use_mw = False # True
    m.mw_frq = 2.827e9
    m.mw_power = -8
    m.repump_power = 100e-6
    m.laser_power = 2e-9
    m.repump_duration = 1 # seconds
    m.counter_channel = 0
    m.wm_channel = 2
    m.use_repump_during = False # True
    m.repump_power_during = 0.1e-6
    
    # sweep
    m.start_voltage = -1
    m.stop_voltage = 1
    m.pts = 501
    m.integration_time = 50 # ms

    m.prepare_scan()
    m.run_scan()
    m.finish_scan()


              
if __name__=='__main__':
    labjack_laser_scan('red_scan_no_MW')

        
