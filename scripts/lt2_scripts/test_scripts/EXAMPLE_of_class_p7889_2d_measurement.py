import os
import qt
import numpy as np

from measurement.measurement_v2 import Measurement

DP = qt.instruments.get_instruments_by_type('FastCom_P7889')[0]
ADWIN = qt.instruments['adwin']

class P7889Measurement2D(Measurement):

    p7889_use_dma = False
    p7889_sweep_preset_number = 1
    p7889_number_of_cycles = 1
    p7889_number_of_sequences = 10000
    p7889_ROI_max = 120
    p7889_ROI_min = 6000
    p7889_range = 6000
    p7889_binwidth = 5

    ROI_min = 0
    ROI_max = 6000

    def __init__(self, name):
        Measurement.__init__(self, name, mclass='P7889_2D')        
    
    def setup(self):
        self._init_p7889()

    def _init_p7889(self):
        DP.set_binwidth(self.p7889_binwidth)
        DP.set_range(self.p7889_range)
        DP.set_ROI_min(self.p7889_ROI_max)
        DP.set_ROI_max(self.p7889_ROI_min)
        
        DP.set_starts_preset(True)
        DP.set_sweepmode_start_event_generation(True)
        DP.set_sweepmode_sequential(True)
        DP.set_sweepmode_wrap_around(False)
        DP.set_sweepmode_DMA(self.p7889_use_dma)
        DP.set_number_of_cycles(self.p7889_number_of_cycles)
        DP.set_number_of_sequences(self.p7889_number_of_sequences)
        DP.set_sweep_preset_number(self.p7889_sweep_preset_number)
        DP.set_starts_preset(True)

    def _get_p7889_data(self):
        return DP.get_2Ddata()

    def measure(self):
        DP.Start()
        qt.msleep(0.05)

    def save(self, timename='t (ns)', sweepname='sweep_value', ret=False):
        x,y,z = self.save_2D_data(timename, sweepname, ret=True)
        self.save_ROI_data(x,y,z, sweepname=sweepname)

        self.save_script()
        self.save_parameters()

        if ret:
            return x,y,z


    def save_2D_data(self, timename='t (ns)', sweepname='sweep_value', ret=False):
        x,y,z = self._get_p7889_data()
        xx, yy = np.meshgrid(x,y)
        
        d = qt.Data(name=self.save_filebase)
        d.add_coordinate(timename)
        d.add_coordinate(sweepname)
        d.add_value('counts')

        p = qt.plot3(d, name='2D_Histogram', clear=True)
        p.reset()

        d.create_file()
        
        for i,row in enumerate(z):
            d.add_data_point(xx[i,:], yy[i,:], row)
            d.new_block()        
        d.close_file()

        self.save_folder = d.get_dir()
        self.timestamp = d.get_time_name()[:6]
        self.save_filebase = d.get_time_name()

        # p.reset()
        # qt.msleep(0.1)
        p.save_png(os.path.join(self.save_folder, self.save_filebase))

        if ret:
            return x,y,z

    def save_ROI_data(self, x, y, z, sweepname='sweep_value'):
        roix = y
        roiy = z[:,self.ROI_min:self.ROI_max].sum(axis=1)
        np.savetxt(os.path.join(self.save_folder, 
            self.save_filebase+'_ROI_sum.dat'), np.vstack((roix,roiy)).T)

        p = qt.plot(roix, roiy, 'rO-', name='ROI_summed', clear=True,
                xlabel=sweepname, ylabel='counts', title='ROI summed')
        p.reset()
        
        h,ts = os.path.split(self.save_folder)
        h,date = os.path.split(h)

        p.set_plottitle(date+'/'+ts+': '+'ROI_summed')
        p.save_png(os.path.join(self.save_folder, self.save_filebase))

    def set_sweep_time_ns(self, val):
        self.p7889_range = val/0.1/2**self.p7889_binwidth

    def get_sweep_time_ns(self):
        return 0.1 * 2**self.p7889_binwidth * self.p7889_range


class P7889TestMeasurement2D(P7889Measurement2D):

    def __init__(self):
        P7889Measurement2D.__init__(self, 'testing')

        self.p7889_number_of_cycles = 10
        self.p7889_number_of_sequences = 100000
        self.ROI_min = 1200
        self.ROI_max = 4600

    def setup(self):
        P7889Measurement2D.setup(self)

        ADWIN.stop_p7889_Vsweep_triggered()
    
    def measure(self):
        P7889Measurement2D.measure(self)
        
        ADWIN.start_p7889_Vsweep_triggered(stop=True, load=True)

        while DP.get_server_running():
            qt.msleep(1)

        ADWIN.stop_p7889_Vsweep_triggered()



m = P7889TestMeasurement2D()
m.setup()
m.measure()
m.save()

