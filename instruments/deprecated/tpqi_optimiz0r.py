import os
import types
from numpy import *
import gobject
import qt
import plot as plt
from instrument import Instrument
from analysis import fit, common
from lib import config
import time

class tpqi_optimiz0r(Instrument):


    def __init__(self, name, get_matisse_freq_func=None, **kw):
        Instrument.__init__(self, name)
        
        #instruments
        self._ins_adwin=qt.instruments['adwin']
        self._ins_adwin_lt1=qt.instruments['adwin_lt1']
        self._ins_pidmatisse=qt.instruments['pidmatisse']
        self._ins_pidnewfocus=qt.instruments['pidnewfocus']
        self._ins_pidnewfocus_lt1=qt.instruments['pidnewfocus_lt1']
        self._func_matisse_freq=get_matisse_freq_func
             
        self.add_parameter('read_interval',
                type=types.FloatType,
                unit='s',
                flags=Instrument.FLAG_GETSET)        
        
        self.add_parameter('tpqi_per_sec_min',
                type=types.FloatType,
                unit='/s',
                flags=Instrument.FLAG_GETSET)   
        self.add_parameter('cr_checks_per_sec_min',
                type=types.FloatType,
                unit='/s',
                flags=Instrument.FLAG_GETSET)    
        self.add_parameter('fraction_failed_min',
                type=types.FloatType,
                unit='%',
                flags=Instrument.FLAG_GETSET)  
                
        
        
        self.add_parameter('is_running',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)
        
        self.add_function('start')        
        self.add_function('stop')
        self.add_function('optimize_matisse')
        self.add_function('optimize_newfocus')
        self.add_function('optimize_gate')
        
        self.set_is_running(False)
        self.set_read_interval(1.0)
        self.set_tpqi_per_sec_min(300) #if the tpqi starts per second are more than this, no optimisation is done
        self.set_cr_checks_per_sec_min(100) #if the number of cr_checks per second on a setup is less than this, no optimisation is done on that setup
        self.set_fraction_failed_min(0.1) #if the fraction of failed cr checks is less than this, no optimisation is done on that setup
        
        
        self._prev_raw_values=zeros(9)
        self._get_input_values()

        
        # override from config       
        cfg_fn = os.path.abspath(
                os.path.join(qt.config['ins_cfg_path'], name+'.cfg'))
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()

    def get_all_cfg(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self.get_parameter_names():
            value = self.get(param)
            self.ins_cfg[param] = value

    #--------------get_set        
    def do_get_is_running(self):
        return self._is_running

    def do_set_is_running(self, val):
        self._is_running = val
        
    def do_get_read_interval(self):
        return self._read_interval

    def do_set_read_interval(self, val):
        self._read_interval = val
        
    def do_get_tpqi_per_sec_min(self):
        return self._tpqi_per_sec_min

    def do_set_tpqi_per_sec_min(self, val):
        self._tpqi_per_sec_min = val

    def do_get_cr_checks_per_sec_min(self):
        return self._cr_checks_per_sec_min

    def do_set_cr_checks_per_sec_min(self, val):
        self._cr_checks_per_sec_min = val

    def do_get_fraction_failed_min(self):
        return self._fraction_failed_min

    def do_set_fraction_failed_min(self, val):
        self._fraction_failed_min = val    
        
    #------------end get set        
               
    #--------------------------------------- public functions
    def start(self,init_only=False,**kw):
    
        #pars init can be changed during start
        self._par_nf_wait_time = kw.get('nf_wait_time',0.6) #s
        self._par_nf_stepsize = kw.get('nf_stepsize',0.02) #GHz
        self._par_min_setpoint_nf_lt2 = kw.get('min_setpoint_nf_lt2',65.5) #GHz
        self._par_max_setpoint_nf_lt2 = kw.get('max_setpoint_nf_lt2',66.5) #GHz
        self._par_min_setpoint_nf_lt1 = kw.get('min_setpoint_nf_lt1',66.4) #GHz
        self._par_max_setpoint_nf_lt1 = kw.get('max_setpoint_nf_lt1',67.0) #GHz
        
        self._par_mat_wait_time = kw.get('mat_wait_time',1) #s
        self._par_mat_stepsize = kw.get('mat_stepsize',0.02) #GHz
        self._par_mat_scan_range = kw.get('mat_scan_range',0.2) #GHz
        self._par_min_setpoint_mat = kw.get('min_setpoint_mat',62.3) #GHz
        self._par_max_setpoint_mat = kw.get('max_setpoint_mat',63.3) #GHz
        
        self._par_min_gate_voltage = kw.get('min_gate_voltage',4.0) #V
        self._par_max_gate_voltage = kw.get('max_gate_voltage',6.0) #V     
        
        self._par_gate_wait_time = kw.get('gate_wait_time',40) #s

        self._par_max_waiting_for_values = kw.get('max_waiting_for_values',6) # if zero cr checks are performed for this time, the program is stopped. in units of 60 sec
    
        
        self._plt=plt.plot() 
        self._optimize_running=False
        self._wait_running=0
        self._get_input_values()
        if not(init_only):
            self.set_is_running(True)
            gobject.timeout_add(int(self._read_interval*1e3), self._check_threshold)
    
    def stop(self):
        self.set_is_running(False)


    #--------------------------------------- private functions    
        
    def _check_threshold(self):
        #print 'Threshold check'

        if not self._is_running:
            return False
        
        lt1_optimize = False
        lt2_optimize = False
        
        dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = self._get_input_values()
        print 'dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts'
        print dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts

        if(tpqi_starts/dt < self._tpqi_per_sec_min):
            if ((cr_checks_lt1/dt > self._cr_checks_per_sec_min) and (cr_failed_lt1/cr_checks_lt1 > self._fraction_failed_min)):
                print 'Optimize LT1'
                lt1_optimize = True
            if ((cr_checks_lt2/dt > self._cr_checks_per_sec_min) and (cr_failed_lt2/cr_checks_lt2 > self._fraction_failed_min)):
                print 'Optimize LT2'
                lt2_optimize = True
            
        if (lt1_optimize or lt2_optimize):    
            self._optimize(lt1_optimize, lt2_optimize)
            #debug
            #self.stop()
        
        return True

    def _get_input_values(self):
        self._raw_values=zeros(9)    
        self._raw_values+=[time.time(),
                         self._ins_adwin_lt1.remote_tpqi_control_get_noof_cr_checks(),
                         self._ins_adwin_lt1.remote_tpqi_control_get_cr_check_counts(),
                         self._ins_adwin_lt1.remote_tpqi_control_get_cr_below_threshold_events(),
                         self._ins_adwin.remote_tpqi_control_get_noof_cr_checks(),
                         self._ins_adwin.remote_tpqi_control_get_cr_check_counts(),
                         self._ins_adwin.remote_tpqi_control_get_cr_below_threshold_events(),
                         self._ins_adwin.remote_tpqi_control_get_noof_tpqi_starts(),
                         self._ins_adwin.remote_tpqi_control_get_noof_tailcts()]
        
        diff=self._raw_values-self._prev_raw_values
        dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = diff[0], diff[1], diff[2], diff[3], diff[4], diff[5], diff[6], diff[7], diff[8]
        self._prev_raw_values =  array(self._raw_values)

        if (cr_checks_lt1 <= 0 and cr_checks_lt2 <= 0 and dt >= 0.09): 
            print 'no cr checks, waiting 10 s, wait index:' ,  self._wait_running
            self._wait_running = self._wait_running + 1
            qt.msleep(10) #wait for the next measurement cycle to begin
            if(self._wait_running > self._par_max_waiting_for_values):
                print 'Waiting time for cr_checks exceeded, quitting...'
                self.stop()
                return 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
            else:    
                return self._get_input_values()
        else:
            self._wait_running = 0       
        
        return  dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts

        
    def _optimize(self,lt1_optimize, lt2_optimize):
        #debug
        #self.stop()
        #return
        
        if lt1_optimize:
            if(self.optimize_newfocus(1,+1)): return
            if(self.optimize_newfocus(1,-1)): return
        if lt2_optimize:
            if(self.optimize_newfocus(2,+1)): return
            if(self.optimize_newfocus(2,-1)): return
        
        optimum_lt1,optimum_lt2 = self.optimize_matisse(lt1_optimize, lt2_optimize)
        
        if optimum_lt1 > 0: return

        if ((lt2_optimize) and (optimum_lt2 > 0)): self.optimize_gate(optimum_lt2)

        
    def optimize_newfocus(self,setup,direction):
        print 'Optimizing Newfocus LT', setup, 'direction', direction  
        
        ins_pid = self._ins_pidnewfocus_lt1 if setup==1 else self._ins_pidnewfocus
        
        self._get_input_values()
        qt.msleep(self._par_nf_wait_time)
        cr_checks=zeros(3)
        cr_cts=zeros(3)
        cr_failed=zeros(3)
        dt, cr_checks[1], cr_cts[1], cr_failed[1], cr_checks[2], cr_cts[2], cr_failed[2], tpqi_starts, tail_cts = self._get_input_values()
        
        current_setpoint=ins_pid.get_setpoint()
        
        i=0
        while(self._par_min_setpoint_nf_lt2 < current_setpoint < self._par_max_setpoint_nf_lt2):
            i=i+1
            print 'newfocus lt2 optimize up', i
            prev_dt, prev_cr_checks_lt2, prev_cr_cts_lt2, prev_tpqi_starts, prev_tail_cts = dt, cr_checks[setup], cr_cts[setup], tpqi_starts, tail_cts
            current_setpoint = current_setpoint + direction*self._par_nf_stepsize
            self.ins_pid.set_setpoint(current_setpoint)
            qt.msleep(self._par_nf_wait_time)
            dt, cr_checks[1], cr_cts[1], cr_failed[1], cr_checks[2], cr_cts[2], cr_failed[2], tpqi_starts, tail_cts = self._get_input_values()
            if ((cr_checks[setup]/dt < self._cr_checks_per_sec_min) or \
                    (cr_cts[setup]/cr_checks[setup] < prev_cr_cts[setup]/prev_cr_checks[setup]) or \
                    False):#(tail_cts/tpqi_starts < prev_tail_cts/prev_tpqi_starts)): 
                break 

        current_setpoint = current_setpoint - direction*self._par_nf_stepsize
        ins_pid.set_setpoint(current_setpoint)
        
        if i>1: return True
        
        return False

    def optimize_matisse(self,lt1_optimize, lt2_optimize):
        print 'Optimizing Matisse'
        #scan the matise in the preset range around the current setpoint, find optima for lt1 and lt2 cr counts
        optimum_lt1=-1.0
        optimum_lt2=-1.0
        
        initial_setpoint = self._ins_pidmatisse.get_setpoint()
        
        self._get_input_values()
        qt.msleep(self._par_mat_wait_time)
        dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = self._get_input_values()
        
        initial_cr_cts_per_check_lt1=-1.0
        if cr_checks_lt1>0: initial_cr_cts_per_check_lt1=cr_cts_lt1/cr_checks_lt1
        initial_cr_cts_per_check_lt2=-1.0
        if cr_checks_lt2>0: initial_cr_cts_per_check_lt2=cr_cts_lt2/cr_checks_lt2
        
        lt1_cts_per_check=[]
        lt2_cts_per_check=[]
        
        freq_scan_min = max(self._par_min_setpoint_mat,initial_setpoint - self._par_mat_scan_range/2.)
        freq_scan_max = min(self._par_max_setpoint_mat, initial_setpoint + self._par_mat_scan_range/2.)
        self._ins_pidmatisse.set_setpoint(freq_scan_min)
        qt.msleep(6.*self._par_mat_wait_time)
        self._get_input_values()
        for freq in linspace(freq_scan_min, freq_scan_max, int((freq_scan_max - freq_scan_min) / self._par_mat_stepsize)):
            self._ins_pidmatisse.set_setpoint(freq)
            qt.msleep(self._par_mat_wait_time*.5)
            cur_freq=freq
            if not(self._func_matisse_freq == None): cur_freq = (self._func_matisse_freq() - self._ins_pidmatisse.get_value_offset())* self._ins_pidmatisse.get_value_factor()
            qt.msleep(self._par_mat_wait_time*.5)
            dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = self._get_input_values()
            if cr_checks_lt1>0: lt1_cts_per_check.append((cr_cts_lt1/cr_checks_lt1,cur_freq))
            if cr_checks_lt2>0: lt2_cts_per_check.append((cr_cts_lt2/cr_checks_lt2,cur_freq))
            
        print 'Initial cr_cts_per_check: lt1:',initial_cr_cts_per_check_lt1, 'lt2:', initial_cr_cts_per_check_lt2
        #print 'Scan: lt1:', lt1_cts_per_check ,'lt2:', lt2_cts_per_check
        self._ins_pidmatisse.set_setpoint(initial_setpoint)
        
        if ((lt1_optimize) and (len(lt1_cts_per_check)>0) and (max(lt1_cts_per_check)[0] >=  initial_cr_cts_per_check_lt1)):
            #if self._par_fit:
            #    print 'Fitting not yet implemented'
            #    pass
            #    #a, xc, k = copysign(max(y), V_max + V_min), copysign(.5, V_max + V_min), copysign(5., V_max + V_min)
            #    #fitres = fit.fit1d(x,y, common.fit_AOM_powerdependence, a, xc, k, do_print=True, do_plot=False, ret=True)
            optimum_lt1=max(lt1_cts_per_check)[1]
            print 'Setting new setpoint matisse:', optimum_lt1
            self._ins_pidmatisse.set_setpoint(optimum_lt1)
        
        if ((lt2_optimize) and (len(lt2_cts_per_check)>0) and (max(lt2_cts_per_check)[0] >=  initial_cr_cts_per_check_lt2)):
            optimum_lt2=max(lt2_cts_per_check)[1]
        
        self._plt.clear()
        self._plt=plt.plot(lt2_cts_per_check)
        self._plt=plt.plot(lt1_cts_per_check)
        qt.msleep(4.*self._par_mat_wait_time)

        return optimum_lt1, optimum_lt2

    def optimize_gate(self,optimum_lt2):
        print 'Optimizing Gate'
        gate_change = (self._ins_pidmatisse.get_setpoint()-optimum_lt2)/ 0.03 * 0.2 #gate V should be changed approx ~ 0.2 V for every 30 MHz detuning
        new_gate_voltage = self._ins_adwin.get_gate_modulation_voltage()*2.0 + gate_change
        if (self._par_min_gate_voltage < new_gate_voltage < self._par_max_gate_voltage):
            print'Changeing gate voltage to:',new_gate_voltage, '(',gate_change,')'
            self._ins_adwin.set_gate_modulation_voltage(new_gate_voltage/2.0)
            qt.msleep(self._par_gate_wait_time)

#things to check: - time.sleep, newfoci up/down, matisse freq scan
#things to change: give instr wavementer function on startup, only allow for gate/matisse every x mins
