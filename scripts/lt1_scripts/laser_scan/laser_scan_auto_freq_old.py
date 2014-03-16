import msvcrt
import qt
import os
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
            p3=qt.Plot3D(d, name='Laser_Scan2D', 
                plottitle=self.mprefix, coorddims=(1,3), valdim=2, clear=True)

        qt.mstart()

        for j,gv in enumerate(np.linspace(self.gate_start_voltage, self.gate_stop_voltage, self.gate_pts)):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break  
            
            prev_v = v = self.scan_to_frequency(self.start_frequency)
            self.set_laser_power(self.laser_power)

            
            if not self.use_repump_during:
                self.repump_pulse()
            
            if self.set_gate:
                self.gate_scan_to_voltage(gv)                 
            
            i=0
            while ((v < self.max_v) and (v> self.min_v)):
                i=i+1
                if msvcrt.kbhit():
                    chr=msvcrt.getch()
                    if chr=='q': 
                        break
                    elif chr =='r': 
                        self.repump_pulse()
                v=prev_v-self.v_step
                prev_v=v
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
                if frq>self.stop_frequency:
                    break
            
            self.set_laser_power(0)
            if self.set_gate_to_zero_before_repump:
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
        self.physical_adwin=qt.instruments['physical_adwin_lt2']
        self.mw = qt.instruments['SMB100']
        self.labjack= qt.instruments['labjack']
        
        self.name=self.name+'_gv_'+str(self.adwin.get_dac_voltage('gate'))

        self.set_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(labjack_dac_nr)](x)
        self.get_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(labjack_dac_nr)]()
        
        # matisse NOT TESTED
        #self.set_laser_voltage = lambda x : qt.instruments['physical_adwin'].Get_FPar(38)
        #self.get_laser_voltage = lambda : qt.instruments['physical_adwin'].Get_FPar(39)
        
        self.get_frequency = lambda x : \
                self.physical_adwin.Get_FPar(x+40)
        self.get_counts = self.adwin.measure_counts
        self.set_gate_voltage = lambda x: self.adwin.set_dac_voltage(('gate',x))
        self.get_gate_voltage = lambda: self.adwin.get_dac_voltage('gate')
    
    def scan_to_frequency(self,f,stepsize=0.05, dwell_time=0.01, tolerance=0.3):
        print 'scan to frequency',f
        v=self.get_laser_voltage()
        succes=False
        cur_f=self.get_frequency(self.wm_channel)
        while ((v < self.max_v-0.3) and (v> self.min_v+0.3)):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break
            cur_f=self.get_frequency(self.wm_channel)
            self.set_laser_voltage(v)
            v=v+stepsize*np.sign(cur_f-f)*np.sign(self.v_step)

            qt.msleep(dwell_time)
            if abs(cur_f-f)<tolerance:
                succes=True
                break
        if not succes:
            print cur_f, f, v
            print 'WARNING: could not reach target frequency', f
        else:
            print 'current frequency:',cur_f
        return v

    def prepare_scan(self):

        if self.use_repump_during:
            self.set_repump_power(self.repump_power_during)
        
        if self.use_mw:
            self.mw.set_frequency(self.mw_frq)
            self.mw.set_power(self.mw_power)
            self.mw.set_pulm('off')
            self.mw.set_iq('off')
            self.mw.set_status('on')

    def finish_scan(self):

        if self.use_mw:
            self.mw.set_status('off')

        if self.use_repump_during:
            self.set_repump_power(0)

            
class YellowLaserScan(LabjackAdwinLaserScan):
    def __init__(self, name, labjack_dac_nr):
        LabjackAdwinLaserScan.__init__(self, name, labjack_dac_nr)
        self.set_laser_power = qt.instruments['YellowAOM'].set_power
        self.set_repump_power = qt.instruments['Velocity1AOM'].set_power
        self.set_nf_repump_power = qt.instruments['Velocity2AOM'].set_power
        
    def repump_pulse(self):
        qt.msleep(1) 
        self.set_laser_power(0)
        self.set_repump_power(self.repump_power)
        self.set_nf_repump_power(self.nf_repump_power)
        qt.msleep(self.repump_duration)
        self.set_repump_power(0)
        self.set_nf_repump_power(0)
        self.set_laser_power(self.laser_power)
        qt.msleep(1)
        
            
class RedLaserScan(LabjackAdwinLaserScan):
    def __init__(self, name, labjack_dac_nr):
        LabjackAdwinLaserScan.__init__(self, name,labjack_dac_nr)
        self.set_laser_power = qt.instruments['Velocity1AOM'].set_power
        self.set_yellow_repump_power = qt.instruments['YellowAOM'].set_power
        self.set_red_repump_power = qt.instruments['Velocity1AOM'].set_power
        self.set_repump_power = qt.instruments['GreenAOM'].set_power
            
    def repump_pulse(self):
        if self.yellow_repump:
            self.set_laser_power(0)
            self.set_red_repump_power(self.red_repump_power)
            self.set_yellow_repump_power(self.yellow_repump_power)
            qt.msleep(self.yellow_repump_duration)
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
          
def yellow_laser_scan(name):
    labjack_dac_nr=0 # 0 is coarse and 1 is fine for yellow
    m = YellowLaserScan(name, labjack_dac_nr)

    # Hardware setup
    m.wm_channel = 2
    m.frq_offset = 0
    m.frq_factor = 1
    m.counter_channel = 0    
   
    # MW setup
    m.use_mw = True
    m.mw_frq =  qt.cfgman['samples']['sil2']['ms-1_cntr_frq']
    m.mw_power = -10

    # repump setup
    m.repump_power=0e-9 # sets the power of the Matisse
    m.nf_repump_power=100e-9 # sets the power of the NF
    m.repump_duration=4.0 #seconds
    m.use_repump_during = False
    m.repump_power_during = 0.5e-6
      
    #Scan setup
    m.laser_power = 1.5e-9
    m.integration_time = 10 # ms
    m.min_v = -9
    m.max_v = 9
    m.v_step=-0.01
    
    m.start_frequency = 18 #GHz
    m.stop_frequency = 40 #GHz
    
    #Gate scan setup
    m.set_gate_to_zero_before_repump=False
    m.set_gate=False
    m.gate_start_voltage=0
    m.gate_stop_voltage=0
    m.gate_pts=1
    
    #strain lines
    m.plot_strain_lines=True
    
    try:
        m.prepare_scan()
        m.run_scan()
    finally:
        m.finish_scan()
    
def red_laser_scan(name):
    labjack_dac_channel=6 #6 is coarse, 7 is fine for NF1 LT1
                          #4 is coarse, 5 is fine fpr NF2 LT1
    m = RedLaserScan(name,labjack_dac_channel)
    
    # Hardware setup
    m.wm_channel = 6 # 6 for nf 1, 7 for nf2
    m.frq_offset = 0
    m.frq_factor = 1
    m.counter_channel = 0

    # MW setup
    m.use_mw = False
    m.mw_frq =  qt.cfgman['samples']['hans-sil1']['ms-1_cntr_frq']
    m.mw_power = -12
    
    # repump setup
    m.yellow_repump=False
    m.yellow_repump_power=50e-9
    m.red_repump_power=0e-9
    m.yellow_repump_duration=4 #seconds
    m.repump_power = 0e-6 #GREEN!!
    m.use_repump_during = True
    m.repump_duration = 0.5 # seconds
    m.repump_power_during = 0.01e-6
    
    #Scan setup
    m.laser_power = 2e-9
    m.integration_time = 50 # ms
    m.min_v = -9.5
    m.max_v = 9.5
    m.v_step=0.015
    
    m.start_frequency = 38 #GHz
    m.stop_frequency = 60 #GHz    
    
    #Gate scan setup
    m.set_gate_to_zero_before_repump=False
    m.set_gate=False
    m.gate_start_voltage=0
    m.gate_stop_voltage=0
    m.gate_pts=1
    
    #strain lines
    m.plot_strain_lines=True
    
    try:
        m.prepare_scan()
        m.run_scan()
    finally:
        m.finish_scan()


if __name__=='__main__':
    stools.turn_off_all_lasers()
    red_laser_scan('red_scan_coarse_Hans_SIL1_Green')
    #yellow_laser_scan('yellow_33V')