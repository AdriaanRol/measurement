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
        d.create_file()
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
        
        d2 = qt.Data(name=self.mprefix+'_'+self.name+'_yellow')
        d2.create_file()
        d2.add_coordinate('Voltage (V)')
        d2.add_coordinate('Frequency (GHz)')
        d2.add_coordinate('Counts [Hz]')
        d2.add_coordinate('Gate Voltage(V)')

        p2 = qt.Plot2D(d2, 'ro', title='Frq (left) vs Voltage (bottom)', plottitle=self.mprefix+'_yellow',
                name='Laser Scan_yellow', clear=True, coorddim=0, valdim=1, maxtraces=1)
        p2.add(d2, 'bo', title='Counts (right) vs Frq (top)', coorddim=1, valdim=2,
                right=True, top=True)
        p2.set_x2tics(True)
        p2.set_y2tics(True)
        p2.set_x2label('Frequency (GHz)')
        p2.set_y2label('Counts [Hz]')
        if self.plot_3D:
            p3D=qt.Plot3D(d, name='Laser_Scan2D', plottitle=self.mprefix, coorddims=(1,3), valdim=2, clear=True)
            p3D2=qt.Plot3D(d2, name='Laser_Scan2D_yellow', plottitle=self.mprefix, coorddims=(1,3), valdim=2, clear=True)

        d3 = qt.Data(name=self.mprefix+'_'+self.name+'_hene')
        d3.create_file()
        d3.add_coordinate('repetition')
        d3.add_coordinate('Frequency (GHz)')
        qt.mstart()
        
        
        ################################################
        
        
        for j,gv in enumerate(np.linspace(self.laser_power_scan_min, self.laser_power_scan_max, self.laser_power_scan_pts)):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break  
            
            qt.instruments['MatisseAOM'].set_power(gv)
            frq = self.get_frequency(self.wm_channel_hene)
            d3.add_data_point(j,frq)
            #######################      RED scan   
            self.set_laser_power(self.laser_power)            
            for i,v in enumerate(np.linspace(self.start_voltage, self.stop_voltage, self.pts)):
                if msvcrt.kbhit():
                    chr=msvcrt.getch()
                    if chr=='q': 
                        break
                
                self.set_laser_voltage(v)
                qt.msleep(stabilizing_time)

                cts = float(self.get_counts(self.integration_time)[self.counter_channel])/(self.integration_time*1e-3)
                frq = self.get_frequency(self.wm_channel)*self.frq_factor - self.frq_offset
                if frq < 0: 
                    continue
                d.add_data_point(v, frq, cts, gv)
                if np.mod(i,10)==0:
                    p.update()
            #      RED scan   back +repump
            self.set_laser_power(self.red_repump_power)
            self.scan_to_voltage(self.start_voltage)
            self.set_laser_power(0)
            

            p.update()
            plotsavename=os.path.splitext(d.get_filepath())[0] + ('_gate_voltage_%2.3f' % gv) + '.png'
            p.set_plottitle(str(os.path.splitext(d.get_filename())[0]))
            p.save_png(filepath=plotsavename)
            d.new_block()
            if self.laser_power_scan_pts>1 and self.plot_3D:
                p3D.update()
            #######################
            #######################    YELLOW scan
            self.set_laser_power_yellow(self.laser_power_yellow)             
            for i,v in enumerate(np.linspace(self.start_voltage_yellow, self.stop_voltage_yellow, self.pts_yellow)):
                if msvcrt.kbhit():
                    chr=msvcrt.getch()
                    if chr=='q': 
                        break
                
                self.set_laser_voltage_yellow(v)
                qt.msleep(stabilizing_time)

                cts = float(self.get_counts(self.integration_time_yellow)[self.counter_channel])/(self.integration_time*1e-3)
                frq = self.get_frequency(self.wm_channel_yellow)*self.frq_factor_yellow - self.frq_offset_yellow
                if frq < 0: 
                    continue
                d2.add_data_point(v, frq, cts, gv)
                if np.mod(i,10)==0:
                    p2.update()
            #      YELLOW scan   back +repump
            self.set_laser_power_yellow(self.yellow_repump_power)
            self.scan_to_voltage_yellow(self.start_voltage_yellow)
            self.set_laser_power_yellow(0)
            

            p2.update()
            plotsavename=os.path.splitext(d2.get_filepath())[0] + ('_gate_voltage_%2.3f' % gv) + '.png'
            p2.set_plottitle(str(os.path.splitext(d.get_filename())[0]))
            p2.save_png(filepath=plotsavename)
            d2.new_block()
            if self.laser_power_scan_pts>1 and self.plot_3D: 
                p3D2.update()
            #######################
            
            
            
        qt.mend()
        
        ##############################################################
        
        
        if self.laser_power_scan_pts>1 and self.plot_3D:
            p3D.reset()
            qt.msleep(1)
            p3D.save_png()
            p3D2.reset()
            qt.msleep(1)
            p3D2.save_png()
        np.savez(os.path.splitext(d.get_filepath())[0]+ '.npz', data=d.get_data())
        np.savez(os.path.splitext(d2.get_filepath())[0]+ '.npz', data=d2.get_data())
        np.savez(os.path.splitext(d3.get_filepath())[0]+ '.npz', data=d3.get_data())
        d.close_file()
        d2.close_file()
        d3.close_file()
        


class LabjackAdwinLaserScan(LaserFrequencyScan):
    def __init__(self, name,labjack_dac_nr,labjack_dac_nr_yellow):
        LaserFrequencyScan.__init__(self, name)
        
        self.adwin = qt.instruments['adwin']
        self.mw = qt.instruments['SMB100']
        self.labjack= qt.instruments['labjack']
        
        self.name=self.name+'_gv_'+str(self.adwin.get_dac_voltage('gate'))
        
        self.set_laser_power = qt.instruments['NewfocusAOM'].set_power
        self.set_laser_power_yellow = qt.instruments['YellowAOM'].set_power
        
        self.set_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(labjack_dac_nr)](x)
        self.get_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(labjack_dac_nr)]()
        self.get_frequency = lambda x : \
                qt.instruments['wavemeter'].get_channel_frequency(x) * 1e3
        
            
        self.set_laser_voltage_yellow = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(labjack_dac_nr_yellow)](x)
        self.get_laser_voltage_yellow = lambda : self.labjack.__dict__['get_bipolar_dac'+str(labjack_dac_nr_yellow)]()
         
        self.get_counts = self.adwin.measure_counts
        self.set_gate_voltage = lambda x: self.adwin.set_dac_voltage(('gate',x))
        self.get_gate_voltage = lambda: self.adwin.get_dac_voltage('gate')
      
    def prepare_scan(self):
        
        if self.use_mw:
            self.mw.set_frequency(self.mw_frq)
            self.mw.set_power(self.mw_power)
            self.mw.set_pulm('off')
            self.mw.set_iq('off')
            self.mw.set_status('on')
        self.scan_to_voltage(self.start_voltage)
        self.set_laser_power_yellow(self.yellow_repump_power)
        self.scan_to_voltage_yellow(self.start_voltage_yellow)
        self.set_laser_power_yellow(0)
    
    def scan_to_voltage(self, voltage, pts=101, dwell_time=0.1):
        #print 'scan to voltage ...',
        #print 'current voltage: ' + str(self.get_laser_voltage())
        for v in np.linspace(self.get_laser_voltage(), voltage, pts):
            self.set_laser_voltage(v)
            qt.msleep(dwell_time)

        #print 'done.'
        
    def scan_to_voltage_yellow(self, voltage, pts=101, dwell_time=0.1):
        #print 'scan to voltage ...',
        #print 'current voltage: ' + str(self.get_laser_voltage())
        for v in np.linspace(self.get_laser_voltage_yellow(), voltage, pts):
            self.set_laser_voltage_yellow(v)
            qt.msleep(dwell_time)

        #print 'done.'
        

    def finish_scan(self):

        if self.use_mw:
            self.mw.set_status('off')


def red_yellow_laser_scan(name):
    labjack_dac_nr=1 # 0 is coarse and 1 is fine for NF
    labjack_dac_nr_yellow=3 # 2 is coarse and 3 is fine for yellow
    m = LabjackAdwinLaserScan(name,labjack_dac_nr,labjack_dac_nr_yellow)
    
    # Hardware setup
    m.wm_channel = 3
    m.frq_offset = 470400
    m.frq_factor = 1
    m.counter_channel = 0

    m.wm_channel_yellow = 2
    m.frq_offset_yellow = 521220
    m.frq_factor_yellow = 1
    
    m.wm_channel_hene = 5

    # MW setup
    m.use_mw = True
    m.mw_frq = qt.cfgman['samples']['sil9']['ms-1_cntr_frq']
    m.mw_power = -12
    
    # repump setup
    m.yellow_repump_power=30e-9
    m.red_repump_power=50e-9
    
    #Scan setup red
    m.laser_power = 1e-9
    m.start_voltage = 8
    m.stop_voltage = -8
    m.pts = 800
    m.integration_time = 50 # ms
    
    #Scan setup yellow
    m.laser_power_yellow = 0.3e-9
    m.start_voltage_yellow = -8
    m.stop_voltage_yellow = 8
    m.pts_yellow = 800
    m.integration_time_yellow = 50 # ms
    
    #Laser scan setup
 
    m.laser_power_scan_min=0
    m.laser_power_scan_max=1.5e-6
    
    m.laser_power_scan_pts=30
    m.plot_3D = True
    
    #strain lines
    m.plot_strain_lines=False
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()

if __name__=='__main__':

    stools.turn_off_lasers()
    red_yellow_laser_scan('red_scan_coarse')
    #yellow_laser_scan('yellow_1nW')

        
