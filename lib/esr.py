import qt
import data
import numpy as np
from measurement import Measurement
import PQ_measurement_generator_v2 as pqm
import msvcrt, time, os
from analysis.lib.fitting import fit, common
from analysis.lib.spin import pulse_calibration_fitandplot_lib, spin_control
# from measurement.AWG_HW_sequencer_v2 import Sequence

class ESRMeasurement(Measurement):
    
    def __init__(self,name):
        Measurement.__init__(self,name,mclass='ESR')
        
    def setup(self,lt1=False):    
        
        self.int_time = 30       #in ms
        self.reps = 10
        self.mw_power_lt1 = -12 #in dBm
        self.mw_power_lt2 = -12   #in dBm

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
            self.stop_f  = 2.835#   2.864 #2.905 #   #in GHz
            self.steps   =   41
        
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

        return total_cnts, self.f_list

    def get_latest_data(self, name, datapath = ''):
        
        meas_folder = r'D:\measuring\data'
        currdate = time.strftime('%Y%m%d')
        
        if datapath == '':
            df = os.path.join(meas_folder, currdate)
        else:
            df = datapath
        
        right_dirs = list()

        if os.path.isdir(df):
            for k in os.listdir(df):
                if name in k:
                    right_dirs.append(k)
            
            if len(right_dirs) > 0:
                latest_dir = os.path.join(df,right_dirs[len(right_dirs)-1])
            else:
                print 'No measurements containing %s in %s'%(name, df)
            
            print '\nAnalyzing data in %s'%latest_dir

        else:
            print 'Folder %s does not exist'%df
            latest_dir = False

        return latest_dir

    def num2str(self, num, precision): 
        return "%0.*f" % (precision, num)




    def fit_ESR(self, name, datapath = '', fit_data = True, save = True, f_dip = 2.828E9):

        if datapath == '':
            datapath = os.path.join(r'D:\measuring\data', 
                    self.get_latest_data(name))
        else:
            datapath = datapath
        
        ###########################################
        ######## MEASUREMENT SPECS ################
        ###########################################
        files = os.listdir(datapath)
        
        for k in files:
            if (name in k) and ('.npz' in k):
                data_file = k
        
        data = np.load(os.path.join(datapath,data_file))
        
        mw_freq = data['freq']
        counts = data['counts']
        data.close()

        f_dip_guess = f_dip
        offset_guess = counts.max()
        dip_depth_guess = offset_guess - counts.min()
        width_guess = 5e-3

        if fit_data:
            
            fit_result=fit.fit1d(mw_freq/1E9, counts, common.fit_gauss, 
                offset_guess, dip_depth_guess, f_dip_guess/1E9,width_guess,
                do_plot = False, do_print = False, newfig = False,ret=True)
            
            x0 = fit_result['params_dict']['x0']
            a = fit_result['params_dict']['a']
            A = fit_result['params_dict']['A']
            sigma = fit_result['params_dict']['sigma']
            #s0 = fit_result[0]['params_dict']['s0']

            x = np.linspace(mw_freq.min(), mw_freq.max(), 501)
            fit_curve = np.zeros(len(x))
            
            fit_curve = np.exp(-(((x/1E9)-x0)/sigma)**2)
            fit_curve = a*np.ones(len(x)) + A*fit_curve

        plot1 = qt.Plot2D(mw_freq/1E9, counts, '-ok', x/1E9, fit_curve, '-r',name='ESR',clear=True) 
        plot1.set_xlabel('MW frequency (GHz)')
        plot1.set_ylabel('Integrated counts')
        plot1.set_plottitle('MW frequency sweep')
        if save:
            plot1.save_png(datapath+'\\histogram_integrated.png')

        data.close()
        #plot1.clear()
        #plot1.quit()

        if save:
            #Save a dat file for use in e.g. Origin with the dark esr data.
            curr_date = '#'+time.ctime()+'\n'
            col_names = '#Col0: MW freq (GHz)\tCol1: Integrated counts\n'
            col_vals = str()
            for k in range(len(counts)):
                col_vals += self.num2str(mw_freq[k]/1E9,10)+'\t'+self.num2str(counts[k],0)+'\n'
            fo = open(datapath+'\\mw_f_calibration_integrated_histogram.dat', "w")
            for item in [curr_date, col_names, col_vals]:
                fo.writelines(item)
            fo.close()

        return x0*1E9


def measure_esr(lt1=False,name='ESR'):
    name='ESR'
    m = ESRMeasurement(name)
    m.setup(lt1)
    counts, frequency = m.measure(name)
    
    f_dip = frequency[np.where(counts == counts.min())]
    f_fit = m.fit_ESR(name, datapath = '', f_dip = f_dip)

    return f_fit
