import msvcrt
import qt
import numpy as np
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.config.experiment_lt2 as lt2_cfg

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
        self.get_gate_voltage = None
        self.set_gate_voltage = None

    def repump_pulse(self, duration):
        qt.msleep(1)
        self.set_repump_power(self.repump_power)
        qt.msleep(duration)
        self.set_repump_power(0)
        qt.msleep(1)
    
    def scan_to_voltage(self, voltage, pts=51, dwell_time=0.05):
        #print 'scan to voltage ...',
        #print 'current voltage: ' + str(self.get_laser_voltage())
        for v in np.linspace(self.get_laser_voltage(), voltage, pts):
            self.set_laser_voltage(v)
            qt.msleep(dwell_time)

        #print 'done.'
        
    def gate_scan_to_voltage(self, voltage, pts=51, dwell_time=0.05):
        print 'scan gate to voltage ...', str(voltage)
        print 'current gate voltage: ' + str(self.get_gate_voltage())
        for v in np.linspace(self.get_gate_voltage(), voltage, pts):
            self.set_gate_voltage(v)
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
        d.add_coordinate('Counts [Hz]')
        d.add_coordinate('Gate Voltage(V)')

        p = qt.Plot2D(d, 'ro', title='Frq (left) vs Voltage (bottom)', plottitle=self.mprefix,
                name='Laser Scan', clear=True, coorddim=0, valdim=1, maxtraces=1)
        p.add(d, 'bo', title='Counts (right) vs Frq (top)', coorddim=1, valdim=2,
                right=True, top=True)
        p.set_x2tics(True)
        p.set_y2tics(True)
        p.set_x2label('Frequency (GHz)')
        p.set_y2label('Counts [Hz]')
        
        if self.gate_pts>1:
            p3=qt.Plot3D(d, name='Laser_Scan2D', plottitle=self.mprefix, coorddims=(1,3), valdim=2, clear=True)

        qt.mstart()
######
        for gv in np.linspace(self.gate_start_voltage, self.gate_stop_voltage, self.gate_pts):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break  
            
            self.scan_to_voltage(self.start_voltage)
            
            if not self.use_repump_during:
                self.repump_pulse(self.repump_duration)
            
            if self.set_gate_after_repump:
                self.gate_scan_to_voltage(gv)                 
                        
            for j,v in enumerate(np.linspace(self.start_voltage, self.stop_voltage, self.pts)):
                if msvcrt.kbhit():
                    chr=msvcrt.getch()
                    if chr=='q': 
                        break
                    elif chr =='r': 
                        self.repump_pulse(self.repump_duration)
                
                self.set_laser_voltage(v)
                qt.msleep(stabilizing_time)

                cts = float(self.get_counts(self.integration_time)[self.counter_channel])/(self.integration_time*1e-3)
                frq = self.get_frequency(self.wm_channel)*self.frq_factor - self.frq_offset
                if frq < 0: 
                    continue
                d.add_data_point(v, frq, cts, gv)
                if np.mod(j,10)==0:
                    p.update()
                
            if self.set_gate_after_repump:
                self.gate_scan_to_voltage(0.)

            psave=p
            if self.plot_strain_lines:        
                try:
                    from analysis.lib.nv import nvlevels
                    Ey_line=float(raw_input('Ey line?')) #GHz
                    Ex_line=float(raw_input('Ex line?')) #GHz
                    lx,ly=nvlevels.get_ES_ExEy_plottable(Ex_line,Ey_line,max(d.get_data()[:,2]))
                    psave.add(lx,ly,right=True, top=True)
                    psave.set_x2label('Frequency (GHz) lines: [%2.2f,%2.2f,%2.2f,%2.2f,%2.2f,%2.2f] ' % tuple(nvlevels.get_ES_ExEy(Ex_line,Ey_line)))
                except ValueError:
                    print 'Could not understand input for lines'
                    pass
            plotsavename=os.path.splitext(d.get_filepath())[0] + ('_gate_voltage_%2.3f' % gv) + '.png'
            psave.save_png(filepath=plotsavename)
            d.new_block()
            if self.gate_pts>1: 
                p3.update()
            
        qt.mend()
        if self.gate_pts>1:
            p3.reset()
            qt.msleep(1)
            p3.save_png()
        np.savez(os.path.splitext(d.get_filepath())[0]+ '.npz', data=d.get_data())
        d.close_file()
        


class AdwinLaserScan(LaserFrequencyScan):
    def __init__(self, name):
        LaserFrequencyScan.__init__(self, name)

        self.adwin = qt.instruments['adwin']
        self.mw = qt.instruments['SMB100']

        self.set_laser_power = qt.instruments['NewfocusAOM'].set_power
        self.set_repump_power = lambda x: self.set_red_repump(x)
        self.set_laser_voltage = lambda x: self.adwin.set_dac_voltage(
                ('newfocus_frq', x))
        self.get_laser_voltage = lambda : self.adwin.get_dac_voltage(
                'newfocus_frq')
        self.get_frequency = lambda x : \
                qt.instruments['wavemeter'].get_channel_frequency(x) * 1e3
        self.get_counts = self.adwin.measure_counts
        self.set_gate_voltage = lambda x: self.adwin.set_dac_voltage(('gate',x))
        self.get_gate_voltage = lambda: self.adwin.get_dac_voltage('gate')
    
    def set_red_repump(self, power):
        if self.yellow_repump:
            qt.instruments['MatisseAOM'].set_power(power)
            qt.instruments['YellowAOM'].set_power(power)
            qt.msleep(1)
            self.set_laser_power(0)
            qt.instruments['MatisseAOM'].set_power(0)
            qt.msleep(1)
            self.set_laser_power(self.laser_power)
        else:
            qt.instruments['GreenAOM'].set_power(power)
    
    def prepare_scan(self):

        if self.use_repump_during:
            self.set_repump_power(self.repump_power_during)
        
        if self.use_mw:
            self.mw.set_frequency(self.mw_frq)
            self.mw.set_power(self.mw_power)
            self.mw.set_pulm('off')
            self.mw.set_iq('off')
            self.mw.set_status('on')
            
        self.set_laser_power(self.laser_power)


    def finish_scan(self):
        self.set_laser_power(0)

        if self.use_mw:
            self.mw.set_status('off')

        if self.use_repump_during:
            self.set_repump_power(0)

            
class YellowLaserScan(LaserFrequencyScan):
    def __init__(self, name):
        LaserFrequencyScan.__init__(self, name)

        self.adwin = qt.instruments['adwin']
        self.awg = qt.instruments['AWG']
        self.mw = qt.instruments['SMB100']
        
        self.set_laser_power = qt.instruments['YellowAOM'].set_power
        self.set_repump_power = lambda x: self.set_red_repump(x)
        self.set_laser_voltage = lambda x: self.adwin.set_dac_voltage(('newfocus_aom',x))
        self.get_laser_voltage = lambda : self.adwin.get_dac_voltage('newfocus_aom')
        self.get_frequency = lambda x : \
                qt.instruments['wavemeter'].get_channel_frequency(x) * 1e3
        self.get_counts = self.adwin.measure_counts
        self.set_gate_voltage = lambda x: self.adwin.set_dac_voltage(('gate',x))
        self.get_gate_voltage = lambda: self.adwin.get_dac_voltage('gate')
    
    def set_red_repump(self, power):
        self.set_laser_power(0)
        qt.instruments['MatisseAOM'].set_power(power)
        qt.instruments['NewfocusAOM'].set_power(power*self.nf_repump_factor)
        print power
        self.set_laser_power(self.laser_power)
        #pass
        #qt.instruments['GreenAOM'].set_power(power)
        
    
    def prepare_scan(self):
        
        self.awg.set_runmode('CONT')
        qt.instruments['GreenAOM'].set_power(0)
        
        if self.use_repump_during:
            self.set_repump_power(self.repump_power_during)
        
        if self.use_mw:
            self.mw.set_frequency(self.mw_frq)
            self.mw.set_power(self.mw_power)
            self.mw.set_pulm('off')
            self.mw.set_iq('off')
            self.mw.set_status('on')
             
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

        self.set_laser_power = qt.instruments['Velocity1AOM'].set_power
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
        #self.set_laser_power(self.laser_power)

    def finish_scan(self):
        self.set_laser_power(0)

        if self.use_mw:
            self.mw.set_status('off')

        if self.use_repump_during:
            self.set_repump_power(0)

#####################TODO not implemented for lt2 (yet)
def labjack_laser_scan(name):


    labjack_dac_channel=2
    m = LabjackLaserScan(name,labjack_dac_channel)

    m.frq_offset = 521220 # red 470400
    m.frq_factor = 2 #red 1

    # HW setup
    m.use_mw = False
    m.mw_frq = 2.863e9
    m.mw_power = -8
    m.repump_power = 100e-6
    m.laser_power = 5e-9
    m.repump_duration = 1 # seconds
    m.counter_channel = 0
    m.wm_channel = 3
    m.use_repump_during = True
    m.repump_power_during = 0.e-6
    
    # sweep
    m.start_voltage = -.5
    m.stop_voltage = 1.5
    m.pts = 1001
    m.integration_time = 50 # ms

    m.prepare_scan()
    m.run_scan()
    m.finish_scan()

###################################################    

def yellow_laser_scan(name):
    m = YellowLaserScan(name)
    
    m.frq_offset = 521220
    m.frq_factor = 1

    # HW setup
    m.use_mw = False
    m.mw_frq = lt2_cfg.sil9['MW_freq_center']
    m.mw_power = -12
    m.repump_power = 100e-9
    m.laser_power = 2e-9
    m.repump_duration = 4. # seconds
    m.counter_channel = 0
    m.wm_channel = 2
    m.use_repump_during = False
    m.repump_power_during = 50e-9
    
    m.plot_strain_lines=False
    
    m.nf_repump_factor=3.
    
    m.start_voltage = 0
    m.stop_voltage = 0
    m.pts = 701
    m.integration_time = 20 # ms
    
    m.set_gate_after_repump=False
    m.gate_start_voltage=0
    m.gate_stop_voltage=0.5
    m.gate_pts=1
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()    
    
def adwin_laser_scan(name):
    m = AdwinLaserScan(name)
    
    # Hardware setup
    m.wm_channel = 3
    m.frq_offset = 470400
    m.frq_factor = 1
    m.counter_channel = 0

    # MW setup
    m.use_mw = True
    m.mw_frq = lt2_cfg.sil9['MW_freq_center']
    m.mw_power = -12
    
    # repump setup
    m.yellow_repump=True
    m.repump_power = 100e-6
    m.repump_duration = 1.5 # seconds
    m.use_repump_during = False
    m.repump_power_during = 0.5e-6
    
    #Scan setup
    m.laser_power = 5e-9
    m.start_voltage = -0.9
    m.stop_voltage = -2.6
    m.pts = 901
    m.integration_time = 20 # ms
    
    #Gate scan setup
    m.set_gate_after_repump=False
    m.gate_start_voltage=0.
    m.gate_stop_voltage=0.
    m.gate_pts=100
    
    #strain lines
    m.plot_strain_lines=False
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()
              
              
if __name__=='__main__':
    adwin_laser_scan('red_scan_go')
    #yellow_laser_scan('yellow_test')

        
