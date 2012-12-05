import qt
import data
import numpy as np
from measurement import Measurement
import PQ_measurement_generator_v2 as pqm
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence

class ESRMeasurement(Measurement):
    
    def __init__(self,name):
        Measurement.__init__(self,name,mclass='ESR')
        
    def setup(self,lt1=False):    
        
        self.int_time = 30       #in ms
        self.reps = 7
        self.mw_power_lt1 = -8 #in dBm
        self.mw_power_lt2 = -6   #in dBm

        if lt1:
            self.ins_green_aom=qt.instruments['GreenAOM_lt1']
            self.ins_smb = qt.instruments['SMB100_lt1']
            self.ins_adwin = qt.instruments['adwin_lt1']
            self.ins_counters = qt.instruments['counters_lt1']
            self.counter = 2
            self.MW_power = self.mw_power_lt1
            self.green_power = 25e-6
            name='ESR_SIL2_LT1'
            self.start_f = 2.81#2.815 #   2.853 #2.85 #  #in GHz
            self.stop_f  = 2.835#2.845#   2.864 #2.905 #   #in GHz
            self.steps   =   31
        else:
            self.ins_green_aom=qt.instruments['GreenAOM']
            self.ins_smb = qt.instruments['SMB100']
            self.ins_adwin = qt.instruments['adwin']
            self.ins_counters = qt.instruments['counters']
            self.counter = 1
            self.green_power=30e-6
            self.MW_power = self.mw_power_lt2
            name='ESR_SIL9_LT2'
            self.start_f = 2.815 #   2.853 #2.85 #  #in GHz
            self.stop_f  = 2.845#   2.864 #2.905 #   #in GHz
            self.steps   =   21
        
#generate list of frequencies
        self.f_list = np.linspace(self.start_f*1e9, self.stop_f*1e9, self.steps)
        self.ins_green_aom.set_power(self.green_power)
        qt.msleep(1)
    def measure(self,name):            
    
# create data object
        qt.mstart()

        self.ins_smb.set_iq('off')
        self.ins_smb.set_pulm('off')
        self.ins_smb.set_power(self.MW_power)
        self.ins_smb.set_status('on')

        qt.msleep(0.2)
        self.ins_counters.set_is_running(0)
        total_cnts = np.zeros(self.steps)
        for cur_rep in range(self.reps):
            for i,cur_f in enumerate(self.f_list):
                
                self.ins_smb.set_frequency(cur_f)
                qt.msleep(0.05)
                
                total_cnts[i]+=self.ins_adwin.measure_counts(self.int_time)[self.counter-1]
                # qt.msleep(0.01)

            p_c = qt.Plot2D(self.f_list, total_cnts, 'bO-', name='ESR', clear=True)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
            print cur_rep
        self.ins_smb.set_status('off')

        d = qt.Data(name=name)
        d.add_coordinate('frequency [GHz]')
        d.add_value('counts')
        d.create_file()

        filename=d.get_filepath()[:-4]

        d.add_data_point(self.f_list, total_cnts)
        pqm.savez(filename,freq=self.f_list,counts=total_cnts)
        d.close_file()
        #p_c = qt.Plot2D(d, 'bO-', coorddim=0, name='ESR', valdim=1, clear=True)
        p_c.save_png(filename+'.png')
        p_c.clear()
        p_c.quit()

        qt.mend()

        self.ins_counters.set_is_running(1)
def measure_esr(lt1=False):
    name='ESR'
    m = ESRMeasurement(name)
    m.setup(lt1)
    m.measure(name)
