import msvcrt
import time
import qt
import os
import numpy as np
import measurement.lib.config.adwins as adwins_cfg

from tools import stools

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

    def repump_pulse(self, stabilizing_time=0.01):
        qt.msleep(stabilizing_time)
        self.set_repump_power(self.repump_power)
        qt.msleep(self.repump_duration)
        self.set_repump_power(0)
        qt.msleep(stabilizing_time)
    
    def scan_to_voltage(self, target_voltage, get_voltage_method, set_voltage_method, 
            voltage_step=0.01, dwell_time=0.01):
        steps = np.append(np.arange(get_voltage_method(), target_voltage, voltage_step), target_voltage)
        for s in steps:
            set_voltage_method(s)
            qt.msleep(dwell_time)
    
    def prepare_scan(self):
        pass

    def finish_scan(self):
        pass

    def scan_to_frequency(self, f, voltage_step=0.05, dwell_time=0.005, tolerance=0.3, power = 0, **kw):

        set_voltage = kw.pop('set_voltage', self.set_red_laser_voltage)
        get_voltage = kw.pop('get_voltage', self.get_red_laser_voltage)
        wm_channel = kw.pop('wm_channel', self.red_wm_channel)
        voltage_frequency_relation_sign = kw.pop('voltage_frequency_relation_sign', 
            self.red_voltage_frequency_relation_sign)
        set_power = kw.get('set_power', self.set_red_power)
        
        # print 'scan to frequency', f
        
        v = get_voltage()
        success = False

        set_power(power)

        while ((v < self.max_v - 0.3) and (v > self.min_v + 0.3)):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break
            
            cur_f = self.get_frequency(wm_channel)
            set_voltage(v)
            v = v + voltage_step * np.sign(f-cur_f) * voltage_frequency_relation_sign
            qt.msleep(dwell_time)
            
            if abs(cur_f-f) < tolerance:
                success = True
                break
        
        if not success:
            print 'WARNING: could not reach target frequency', f
        else:
            print 'current frequency:', cur_f

        set_power(0)
        
        return v
    
    def single_line_scan(self, start_f, stop_f, 
        voltage_step, integration_time_ms, power, **kw):

        stabilizing_time = kw.pop('stabilizing_time', 0.005)
        save = kw.pop('save', True)
        data = kw.pop('data', None)

        suffix = kw.pop('suffix', None)

        set_voltage = kw.get('set_voltage', self.set_red_laser_voltage)
        get_voltage = kw.get('get_voltage', self.get_red_laser_voltage)
        wm_channel = kw.get('wm_channel', self.red_wm_channel)
        voltage_frequency_relation_sign = kw.get('voltage_frequency_relation_sign', 
            self.red_voltage_frequency_relation_sign)
        set_power = kw.get('set_power', self.set_red_power)

        data_args = kw.get('data_args', [])

        data_obj_supplied = False
        if save:
            if data == None:
                data_obj_supplied = False

                data = qt.Data(name = self.mprefix + '_' + self.name + ('_{}'.format(suffix) if suffix != None else ''))
                data.add_coordinate('Voltage (V)')
                data.add_coordinate('Frequency (GHz)')
                data.add_coordinate('Counts [Hz]')

                plt_cts = qt.Plot2D(data, 'bO',
                    name='Laserscan_Counts' + ('_{}'.format(suffix) if suffix != None else ''), 
                    clear=True, coorddim=1, valdim=2, maxtraces=1)

                plt_frq = qt.Plot2D(data, 'rO',
                    name='Laserscan_Frequency' + ('_{}'.format(suffix) if suffix != None else ''), 
                    clear=True, coorddim=0, valdim=1, maxtraces=1)
            else:
                data_obj_supplied = True

        self.scan_to_frequency(start_f, **kw)
        
        v = get_voltage()

        set_power(power)
        while ((v < self.max_v - 0.3) and (v > self.min_v + 0.3)):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break

            set_voltage(v)
            qt.msleep(stabilizing_time)

            cur_f = self.get_frequency(wm_channel)
            if cur_f < 0:
                continue

            if (stop_f > start_f) and (cur_f > stop_f):
                break
            elif (stop_f <= start_f) and (cur_f < stop_f):
                break  

            cts = float(self.get_counts(integration_time_ms)[self.counter_channel]) / \
                (integration_time_ms*1e-3)

            v = v + voltage_step * np.sign(stop_f - cur_f) * voltage_frequency_relation_sign

            if save:
                if not data_obj_supplied:
                    data.add_data_point(v, cur_f, cts)
                else:
                    data.add_data_point(v, cur_f, cts, *data_args)

        set_power(0)

        if save and not data_obj_supplied:
            plt_cts.save_png()
            plt_frq.save_png()


class ScanLT1(LaserFrequencyScan):

    def __init__(self, name='LT1'):
        LaserFrequencyScan.__init__(self, name)
        
        self.adwin = qt.instruments['adwin_lt1']
        self.physical_adwin=qt.instruments['physical_adwin']
        self.mw = qt.instruments['SMB100_lt1']
        self.labjack= qt.instruments['labjack']

        red_labjack_dac_nr = 6
        self.set_red_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(red_labjack_dac_nr)](x)
        self.get_red_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(red_labjack_dac_nr)]()
        self.set_red_power = qt.instruments['NewfocusAOM_lt1'].set_power

        yellow_labjack_dac_nr = 0
        self.set_yellow_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(yellow_labjack_dac_nr)](x)
        self.get_yellow_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(yellow_labjack_dac_nr)]()
        self.set_yellow_power = qt.instruments['YellowAOM_lt1'].set_power

        self.set_repump_power = qt.instruments['GreenAOM_lt1'].set_power

        self.get_frequency = lambda x : self.physical_adwin.Get_FPar(x+40)
        self.get_counts = self.adwin.measure_counts
        self.counter_channel = 0
        
        self.red_voltage_frequency_relation_sign = -1
        self.red_wm_channel = 6

        self.yellow_voltage_frequency_relation_sign = 1
        self.yellow_wm_channel = 2

        self.max_v = 9.
        self.min_v = -9.

    def yellow_scan(self, start_f, stop_f, power=0.5e-9, **kw):
        voltage_step = kw.pop('voltage_step', 0.01)

        self.single_line_scan(start_f, stop_f,
            voltage_step = voltage_step, 
            integration_time_ms=50, 
            power=power,
            suffix = 'yellow', 
            set_voltage = self.set_yellow_laser_voltage,
            get_voltage = self.get_yellow_laser_voltage,
            wm_channel = self.yellow_wm_channel,
            voltage_frequency_relation_sign = self.yellow_voltage_frequency_relation_sign,
            set_power = self.set_yellow_power,
            **kw)

    def yellow_ionization_scan(self, start_f, stop_f, power=50e-9, **kw):
        self.single_line_scan(start_f, stop_f,
            voltage_step=0.02, integration_time_ms=5, power=power,
            suffix = 'yellow', 
            set_voltage = self.set_yellow_laser_voltage,
            get_voltage = self.get_yellow_laser_voltage,
            wm_channel = self.yellow_wm_channel,
            voltage_frequency_relation_sign = self.yellow_voltage_frequency_relation_sign,
            set_power = self.set_yellow_power,
            save = False)

    def red_scan(self, start_f, stop_f, power=0.5e-9, **kw):
        voltage_step = kw.pop('voltage_step', 0.005)
        integration_time_ms = kw.pop('integration_time_ms', 50)
        
        self.single_line_scan(start_f, stop_f, voltage_step, integration_time_ms, power, **kw)\

    def red_inonization_scan(self, start_f, stop_f, power=40e-9, **kw):
        voltage_step = kw.pop('voltage_step', 0.02)
        integration_time_ms = kw.pop('integration_time_ms', 20)
        _save=kw.pop('save', False)        
        
        self.single_line_scan(start_f, stop_f, voltage_step, integration_time_ms, power, 
            save=False, **kw)    

    def yellow_red(self, y_start, y_stop, y_power, r_start, r_stop, r_step, r_int, r_power, **kw):
        red_data = kw.pop('red_data', None)
        yellow_data = kw.pop('yellow_data', None)

        print 'ionization scan yellow...'
        self.yellow_ionization_scan(y_stop, y_start)

        print 'red scan...'
        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power=r_power, 
            data = red_data,
            **kw)
        
        print 'ionization scan red...'
        self.red_inonization_scan(r_stop, r_start)
        
        print 'yellow scan...'
        self.yellow_scan(y_start, y_stop, y_power,
            data = yellow_data,
            **kw)


    def spectral_diffusion(self, y_start, y_stop, y_power, r_start, r_stop, r_step, r_int, r_power, **kw):
        red_data = kw.pop('red_data', None)
        yellow_data = kw.pop('yellow_data', None)

        print 'green repump pulse'
        qt.msleep(1)
        self.set_repump_power(10e-6)
        qt.msleep(0.5)
        self.set_repump_power(0)
        qt.msleep(1)

        print 'red scan...'
        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power=r_power, 
            data = red_data,
            **kw)
        
        print 'ionization scan red...'
        self.red_inonization_scan(r_stop, r_start)
        
        print 'yellow scan...'
        self.yellow_scan(y_start, y_stop, y_power,
            data = yellow_data,
            **kw)
        

    def oldschool_red_scan(self, r_start, r_stop, r_step, r_int, r_power, **kw):
        red_data = kw.pop('red_data', None)

        print 'green repump pulse'
        qt.msleep(1)
        self.set_repump_power(100e-6)
        qt.msleep(1)
        self.set_repump_power(0)
        qt.msleep(1)

        print 'red scan...'
        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power = r_power, 
            data = red_data,
            **kw)
        
def single_red_scan():
    m = ScanLT1()

    SMB100_lt1.set_power(-5)
    SMB100_lt1.set_frequency(2.8265e9)
    SMB100_lt1.set_iq('off')
    SMB100_lt1.set_pulm('off')
    SMB100_lt1.set_status('on')

    m.yellow_red(20, 25, 0.2e-9, 60, 70, 0.01, 20, 1e-9)
    # m.oldschool_red_scan(35, 60, 0.01, 20, 1e-9)

    SMB100_lt1.set_status('off')

def repeated_red_scans(**kw):
    pts = 100
    m = ScanLT1()

    spectral_diffusion = kw.pop('spectral_diffusion', False)

    SMB100_lt1.set_power(-5)
    SMB100_lt1.set_frequency(2.8265e9)
    SMB100_lt1.set_iq('off')
    SMB100_lt1.set_pulm('off')
    SMB100_lt1.set_status('on')

    red_data = qt.Data(name = 'LaserScansYellowRepump_LT1_Red')
    red_data.add_coordinate('Voltage (V)')
    red_data.add_coordinate('Frequency (GHz)')
    red_data.add_coordinate('Counts (Hz)')
    red_data.add_coordinate('index')
    red_data.add_coordinate('start time')
    red_data.create_file()

    yellow_data = qt.Data(name = 'LaserScansYellowRepump_LT1_Yellow')
    yellow_data.add_coordinate('Voltage (V)')
    yellow_data.add_coordinate('Frequency (GHz)')
    yellow_data.add_coordinate('Counts (Hz)')
    yellow_data.add_coordinate('index')
    yellow_data.add_coordinate('start time')
    yellow_data.create_file()

    plt_red_cts = qt.Plot2D(red_data, 'bO',
        name='Laserscan_Counts', 
        clear=True, coorddim=1, valdim=2, maxtraces=5, traceofs=5000)

    plt_red_frq = qt.Plot2D(red_data, 'rO',
        name='Laserscan_Frequency', 
        clear=True, coorddim=0, valdim=1, maxtraces=1)

    plot3d_red = qt.Plot3D(red_data, name='Laserscan_Counts_Reps', 
        clear=True, coorddims=(1,3), valdim=2)

    plt_yellow_cts = qt.Plot2D(yellow_data, 'bO',
        name='Laserscan_Counts_Y', 
        clear=True, coorddim=1, valdim=2, maxtraces=5, traceofs=5000)

    plt_yellow_frq = qt.Plot2D(yellow_data, 'rO',
        name='Laserscan_Frequency_Y', 
        clear=True, coorddim=0, valdim=1, maxtraces=1)

    plot3d_yellow = qt.Plot3D(yellow_data, name='Laserscan_Counts_Reps_Y', 
        clear=True, coorddims=(1,3), valdim=2)

    
    t0 = time.time()
    for i in range(pts):
        if (msvcrt.kbhit() and msvcrt.getch()=='x'): 
            break

        # tpulse = 10
        # print "{} seconds of red power...".format(tpulse)
        # stools.apply_awg_voltage('AWG', 'ch4_marker1', 0.52)
        # qt.msleep(tpulse)
        # stools.apply_awg_voltage('AWG', 'ch4_marker1', 0.02)
        
        if spectral_diffusion:
            m.spectral_diffusion(20, 25, 0.2e-9, 58, 65, 0.01, 20, 1e-9, 
                red_data = red_data, 
                yellow_data = yellow_data,
                data_args=[i, time.time()-t0])

        else:
            m.yellow_red(20, 25, 0.2e-9, 58, 65, 0.01, 20, 1e-9, 
                red_data = red_data, 
                yellow_data = yellow_data,
                data_args=[i, time.time()-t0])
        
        red_data.new_block()
        yellow_data.new_block()
        plot3d_red.update()
        plot3d_yellow.update()

    SMB100_lt1.set_status('off')
    red_data.close_file()
    yellow_data.close_file()
    plot3d_red.save_png()
    plot3d_yellow.save_png()

if __name__ == '__main__':
    single_red_scan()
    # repeated_red_scans()
    # repeated_red_scans(spectral_diffusion=True)

