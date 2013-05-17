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
        self.get_gate_voltage = None
        self.set_gate_voltage = None

    def repump_pulse(self):
        qt.msleep(1)
        self.set_repump_power(self.repump_power)
        qt.msleep(self.repump_duration)
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
        ###### HERE THE MEASUREMENT LOOP STARTS ######
        for j,gv in enumerate(np.linspace(self.gate_start_voltage, self.gate_stop_voltage, self.gate_pts)):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break  
            
            self.scan_to_voltage(self.start_voltage)
            
            if not self.use_repump_during:
                self.repump_pulse()
            
            if self.set_gate_after_repump:
                self.gate_scan_to_voltage(gv)                 
                        
            for i,v in enumerate(np.linspace(self.start_voltage, self.stop_voltage, self.pts)):
                if msvcrt.kbhit():
                    chr=msvcrt.getch()
                    if chr=='q': 
                        break
                    elif chr =='r': 
                        self.repump_pulse()
                
                self.set_laser_voltage(v)
                qt.msleep(stabilizing_time)

                cts = float(self.get_counts(self.integration_time)[self.counter_channel])/(self.integration_time*1e-3)
                frq = self.get_frequency(self.wm_channel)*self.frq_factor - self.frq_offset
                if frq < 0: 
                    continue
                d.add_data_point(v, frq, cts, gv)
                if np.mod(i,10)==0:
                    p.update()
                
            if self.set_gate_after_repump:
                self.gate_scan_to_voltage(0.)
            p.update()
            if self.plot_strain_lines:
                p.set_maxtraces(2)
                try:
                    from analysis.lib.nv import nvlevels
                    Ey_line=float(raw_input('Ey line?')) #GHz
                    Ex_line=float(raw_input('Ex line?')) #GHz
                    lx,ly=nvlevels.get_ES_ExEy_plottable(Ex_line,Ey_line,max(d.get_data()[:,2]))
                    tit=str('Frequency (GHz) lines: [%2.2f,%2.2f,%2.2f,%2.2f,%2.2f,%2.2f] ' % tuple(nvlevels.get_ES_ExEy(Ex_line,Ey_line)))
                    p.add(lx,ly,right=True, top=True, title=tit)
                except ValueError:
                    print 'Could not understand input for lines'
                    pass
            plotsavename=os.path.splitext(d.get_filepath())[0] + ('_gate_voltage_%2.3f' % gv) + '.png'
            p.set_plottitle(str(os.path.splitext(d.get_filename())[0]))
            p.save_png(filepath=plotsavename)
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
        


class LabjackAdwinLaserScan(LaserFrequencyScan):
    def __init__(self, name,labjack_dac_nr):
        LaserFrequencyScan.__init__(self, name)
        
        self.adwin = qt.instruments['adwin']
        self.mw = qt.instruments['SMB100']
        self.labjack= qt.instruments['labjack']
        
        self.name=self.name+'_gv_'+str(self.adwin.get_dac_voltage('gate'))

        self.set_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(labjack_dac_nr)](x)
        self.get_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(labjack_dac_nr)]()
        self.get_frequency = lambda x : \
                qt.instruments['wavemeter'].get_channel_frequency(x) * 1e3
        self.get_counts = self.adwin.measure_counts
        self.set_gate_voltage = lambda x: self.adwin.set_dac_voltage(('gate',x))
        self.get_gate_voltage = lambda: self.adwin.get_dac_voltage('gate')
      
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
    
    def repump_pulse(self):
        pass
        
    def finish_scan(self):
        self.set_laser_power(0)

        if self.use_mw:
            self.mw.set_status('off')

        if self.use_repump_during:
            self.set_repump_power(0)

            
class YellowLaserScan(LabjackAdwinLaserScan):
    def __init__(self, name):
        LabjackAdwinLaserScan.__init__(self, name,2)
        self.set_laser_power = qt.instruments['YellowAOM'].set_power
        self.set_repump_power = qt.instruments['Velocity1AOM'].set_power
        self.set_nf_repump_power=qt.instruments['Velocity2AOM'].set_power
        
    def repump_pulse(self):
        qt.msleep(1) 
        self.set_laser_power(0)
        self.set_repump_power(self.repump_power)
        self.set_nf_repump_power(self.nf_repump_power)
        print power
        qt.msleep(self.repump_duration)
        self.set_repump_power(0)
        self.set_nf_repump_power(0)
        self.set_laser_power(self.laser_power)
        qt.msleep(1)
        
            
class RedLaserScan(LabjackAdwinLaserScan):
    def __init__(self, name, labjack_dac_nr):
        LabjackAdwinLaserScan.__init__(self, name,labjack_dac_nr)
        self.set_laser_power = qt.instruments['Velocity2AOM'].set_power
        self.set_yellow_repump_power=qt.instruments['YellowAOM'].set_power
        self.set_red_repump_power=qt.instruments['Velocity1AOM'].set_power
        self.set_repump_power = qt.instruments['GreenAOM'].set_power
            
    def repump_pulse(self):
        if self.yellow_repump:
            self.set_laser_power(0)
            self.set_red_repump_power(self.red_repump_power)
            qt.msleep(self.repump_duration)
            self.set_red_repump_power(0)
            self.set_yellow_repump_power(self.yellow_repump_power)
            qt.msleep(self.yellow_repump_duration)
            self.set_yellow_repump_power(0)
            self.set_laser_power(self.laser_power)
        else:    
            qt.msleep(1)
            self.set_repump_power(self.repump_power)
            qt.msleep(self.repump_duration)
            self.set_repump_power(0)
            qt.msleep(1)

class LabjackResonantCountingScan(LabjackAdwinLaserScan):
    def __init__(self, name, labjack_dac_nr):
        LabjackAdwinLaserScan.__init__(self, name, labjack_dac_nr)

        self.average_pts = 10
        self.average_sleep = 0.01
        self.do_repump = False

        self.get_counts = self._get_counts

    def _get_counts(self, int_time):
        cts = np.array([0,0,0,0])
        
        for i in range(self.average_pts):
            cts += np.array(self.adwin.get_countrates())
            qt.msleep(self.average_sleep)

        return cts / self.average_pts
    
class LabjackAlternResonantCountingScan(LabjackAdwinLaserScan):
    def __init__(self, name, labjack_dac_nr):
        LabjackAdwinLaserScan.__init__(self, name, labjack_dac_nr)

        self.get_counts = self._get_counts
        self.do_repump = False
        
        self.repump_aom = 'green_aom'
        self.pump_aom = 'velocity1_aom'
        self.probe_aom = 'velocity2_aom'
        self.pump_aom_ins = 'Velocity1AOM'
        self.probe_aom_ins = 'Velocity2AOM'
        self.repump_duration = 0
        self.pump_duration = 5
        self.probe_duration = 5
        self.repump_voltage = 0
        self.pump_power = 5e-9
        self.probe_power = 2e-9
        self.floating_average = 100
        self.pp_cycles = 5
        self.single_shot = 1
        self.prepump = 1

    def _get_counts(self, int_time):
        self.adwin.set_altern_resonant_counting(
                repump_aom = self.repump_aom,
                pump_aom = self.pump_aom,
                probe_aom = self.probe_aom,
                pump_aom_ins = self.pump_aom_ins,
                probe_aom_ins = self.probe_aom_ins,
                repump_duration = self.repump_duration,
                pump_duration = self.pump_duration,
                probe_duration = self.probe_duration,
                repump_voltage = self.repump_voltage,
                pump_power = self.pump_power,
                probe_power = self.probe_power,
                floating_average = self.floating_average,
                pp_cycles = self.pp_cycles,
                single_shot = self.single_shot,
                prepump = self.prepump)
        qt.msleep(0.01)
        
        cts = self.adwin.get_counter_var('get_countrates')
        return np.array(cts)

    
def yellow_laser_scan(name):
    m = YellowLaserScan(name)

    # Hardware setup
    m.wm_channel = 2
    m.frq_offset = 521220
    m.frq_factor = 1
    m.counter_channel = 0    
   
    # MW setup
    m.use_mw = False
    m.mw_frq = qt.cfgman['samples']['sil2']['MW frq']
    m.mw_power = -12

    # repump setup
    m.repump_power=0e-9 # sets the power of the Matisse
    m.nf_repump_power=0e-9 # sets the power of the NF
    m.repump_duration=0.0 #seconds
    m.use_repump_during = False
    m.repump_power_during = 0.5e-6
      
    #Scan setup
    m.laser_power = 1e-9
    m.start_voltage = 2
    m.stop_voltage = 10
    m.pts = 1501
    m.integration_time = 40 # ms
    
    #Gate scan setup
    m.set_gate_after_repump=False
    m.gate_start_voltage=0.
    m.gate_stop_voltage=0.
    m.gate_pts=1
    
    #strain lines
    m.plot_strain_lines=False
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()    

    
def red_resonant_counting_scan(name):
    labjack_dac_channel=0 #velocity 1
    m = LabjackResonantCountingScan(name,labjack_dac_channel)
    
    # Hardware setup
    m.wm_channel = 1
    m.frq_offset = 470400
    m.frq_factor = 1
    m.counter_channel = 0

    # MW setup
    m.use_mw = True
    m.mw_frq = qt.cfgman['samples']['sil2']['MW frq']
    m.mw_power = -12
    
    #Scan setup
    m.laser_power = 50e-9
    m.start_voltage = 0.6
    m.stop_voltage = -0.9
    m.pts = 1500
    m.integration_time = 40 # ms
    
    #Gate scan setup
    m.set_gate_after_repump=False
    m.gate_start_voltage=0.
    m.gate_stop_voltage=0.
    m.gate_pts=1
    
    #strain lines
    m.plot_strain_lines=True
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()
    
def red_alternating_resonant_counting(name):
    labjack_dac_channel = 0 # 0 = velocity 1 frq.
    m = LabjackAlternResonantCountingScan(name, labjack_dac_channel)
        
    # Hardware setup
    m.wm_channel = 1
    m.frq_offset = 470400
    m.frq_factor = 1
    m.counter_channel = 0

    # MW setup
    m.use_mw = True
    m.mw_frq = qt.cfgman['samples']['sil2']['MW frq']
    m.mw_power = -12
    
    #Scan setup
    m.laser_power = 50e-9
    m.start_voltage = 0.6
    m.stop_voltage = -0.9
    m.pts = 1500
    m.integration_time = 40 # ms
    
    #Gate scan setup
    m.set_gate_after_repump=False
    m.gate_start_voltage=0.
    m.gate_stop_voltage=0.
    m.gate_pts=1
    
    #strain lines
    m.plot_strain_lines=True
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()        

    
def red_laser_scan(name):
    labjack_dac_nr=1
    m = RedLaserScan(name,labjack_dac_nr)
    
    # Hardware setup
    m.wm_channel = 2
    m.frq_offset = 470400
    m.frq_factor = 1
    m.counter_channel = 0

    # MW setup
    m.use_mw = True
    m.mw_frq = qt.cfgman['samples']['sil2']['MW frq']
    m.mw_power = -12
    
    # repump setup
    m.yellow_repump=False
    m.yellow_repump_power=500e-9
    m.red_repump_power=0e-9
    m.yellow_repump_duration=4 #seconds
    m.repump_power = 50e-6
    m.repump_duration = 2 # seconds
    m.use_repump_during = False
    m.repump_power_during = 0.5e-6
    
    #Scan setup
    m.laser_power = 3e-9
    m.start_voltage = -0.5
    m.stop_voltage = -1.6
    m.pts = 1000
    m.integration_time = 40 # ms
    
    #Gate scan setup
    m.set_gate_after_repump=False
    m.gate_start_voltage=0.
    m.gate_stop_voltage=0.
    m.gate_pts=1
    
    #strain lines
    m.plot_strain_lines=True
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()

    
if __name__=='__main__':

    #Velocity1AOM.set_power(50e-9)
    #YellowAOM.set_power(50e-9)
    red_laser_scan('red_scan_go')
    #yellow_laser_scan('yellow_1nW')

        
