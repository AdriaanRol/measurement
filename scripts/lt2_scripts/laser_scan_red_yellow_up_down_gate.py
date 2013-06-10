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
 
        
    def gate_scan_to_voltage(self,voltage, stepsize=0.01, dwell_time=0.05):
        cur_v=qt.instruments['adwin'].get_dac_voltage('gate')
        print 'scan gate to voltage ...',voltage
        print 'current gate voltage: ', cur_v 
        steps=int(abs(cur_v-voltage)/stepsize)
        for v in np.linspace(cur_v, voltage, steps):
            qt.instruments['adwin'].set_dac_voltage(('gate',v))
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
        p2.add(d2, 'b', title='Counts (right) vs Frq (top)', coorddim=1, valdim=2,
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
        
        
        for j,gv in enumerate(np.linspace(self.gate_start_voltage, self.gate_stop_voltage, self.gate_pts)):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break  
            if self.set_gate:                        
                self.gate_scan_to_voltage(gv)
            else:
                gv=j
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
                    print 'WARNING: WM gives frq',frq
                    continue
                d.add_data_point(v, frq, cts, gv)
                if np.mod(i,10)==0:
                    p.update()
            #      RED scan   back +repump
            self.set_laser_power(self.red_repump_power)
            self.scan_to_voltage(self.pump_voltage-0.2)
            self.scan_to_voltage(self.pump_voltage+0.2)
            self.scan_to_voltage(self.start_voltage)
            self.set_laser_power(0)
            
            if self.set_gate_to_zero_before_repump:
                self.gate_scan_to_voltage(0.)
            p.update()
            plotsavename=os.path.splitext(d.get_filepath())[0] + ('_gate_voltage_%2.3f' % gv) + '.png'
            p.set_plottitle(str(os.path.splitext(d.get_filename())[0]))
            p.save_png(filepath=plotsavename)
            d.new_block()
            if self.gate_pts>1 and self.plot_3D:
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
            
            if self.set_gate_to_zero_before_repump:
                self.gate_scan_to_voltage(0.)
            p2.update()
            plotsavename=os.path.splitext(d2.get_filepath())[0] + ('_gate_voltage_%2.3f' % gv) + '.png'
            p2.set_plottitle(str(os.path.splitext(d.get_filename())[0]))
            p2.save_png(filepath=plotsavename)
            d2.new_block()
            if self.gate_pts>1 and self.plot_3D: 
                p3D2.update()
            #######################
            
            
            
        qt.mend()
        
        ##############################################################
        
        
        if self.gate_pts>1 and self.plot_3D:
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
    
    def scan_to_voltage(self, voltage, pts=201, dwell_time=0.05):
        #print 'scan to voltage ...',
        #print 'current voltage: ' + str(self.get_laser_voltage())
        for v in np.linspace(self.get_laser_voltage(), voltage, pts):
            self.set_laser_voltage(v)
            qt.msleep(dwell_time)

        #print 'done.'
        
    def scan_to_voltage_yellow(self, voltage, pts=301, dwell_time=0.05):
        #print 'scan to voltage ...',
        #print 'current voltage: ' + str(self.get_laser_voltage())
        for v in np.linspace(self.get_laser_voltage_yellow(), voltage, pts):
            self.set_laser_voltage_yellow(v)
            qt.msleep(dwell_time)

        #print 'done.'
        

    def finish_scan(self):

        if self.use_mw:
            self.mw.set_status('off')
        self.gate_scan_to_voltage(0.)


def red_yellow_laser_scan(name,gate):
    labjack_dac_nr=0 # 0 is coarse and 1 is fine for NF
    labjack_dac_nr_yellow=2 # 2 is coarse and 3 is fine for yellow
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
    m.yellow_repump_power=50e-9
    m.red_repump_power=70e-9
    
    #Scan setup red
    m.laser_power = 5e-9
    m.start_voltage = 0
    m.pump_voltage = -1.15
    m.stop_voltage = -6.
    m.pts = 1000
    m.integration_time = 50 # ms
    
    #Scan setup yellow
    m.laser_power_yellow = 1e-9
    m.start_voltage_yellow = -10
    m.stop_voltage_yellow = 10#XXX
    m.pts_yellow = 1800
    m.integration_time_yellow = 40 # ms
    
    #Gate scan setup
    m.set_gate_to_zero_before_repump=False
    m.set_gate=False
    m.gate_start_voltage=0
    m.gate_stop_voltage=gate
    m.gate_pts=1
    m.plot_3D = False
    
    #strain lines
    m.plot_strain_lines=False
    
    m.prepare_scan()
    m.run_scan()
    m.finish_scan()

if __name__=='__main__':

    stools.turn_off_lasers()
    red_yellow_laser_scan('red_scan',0)
    
    #stools.turn_off_lasers()
    #GreenAOM.set_power(200e-6)
    #qt.msleep(100)
    #optimiz0r.optimize(cnt=1,cycles=3,int_time=30)
    #qt.msleep(100)
    #GreenAOM.set_power(20e-6)
    #if optimiz0r.optimize(cnt=1,cycles=3,int_time=30):
    #    stools.turn_off_lasers()
    #    red_yellow_laser_scan('red_scan_',-1.5)
    #stools.turn_off_lasers()


        
