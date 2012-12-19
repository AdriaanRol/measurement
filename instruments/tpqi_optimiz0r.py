import os
import types
from numpy import *
import gobject
import qt
import plot as plt
from instrument import Instrument
from analysis.lib.fitting import fit, common
from lib import config
import time
import msvcrt

class tpqi_optimiz0r(Instrument):


    def __init__(self, name, **kw):
        Instrument.__init__(self, name)
        
        #instruments
        self._ins_adwin=qt.instruments['adwin']
        self._ins_adwin_lt1=qt.instruments['adwin_lt1']
        self._ins_pidmatisse=qt.instruments['pidmatisse']
        self._ins_pidnewfocus=qt.instruments['pidnewfocus']
        self._ins_pidnewfocus_lt1=qt.instruments['pidnewfocus_lt1']
             
        self.add_parameter('read_interval',
                type=types.FloatType,
                unit='s',
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('is_running',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)
        
        self.add_function('start')        
        self.add_function('stop')
        self.add_function('optimize_matisse')
        self.add_function('optimize_newfocus_steps')
        self.add_function('optimize_newfocus_steps')
        self.add_function('optimize_gate')
        self.add_function('set_single_setting')
        self.add_function('get_single_setting')
        
        self.set_is_running(False)
        self.set_read_interval(60) #s
        self._settings={ 'nf_wait_time': 0.6, #s
                            'nf_stepsize' : 0.01, #GHz
                            'min_setpoint_nf_lt2' : 66.8, #GHz #NOTE
                            'max_setpoint_nf_lt2' : 67.2, #GHz #NOTE
                            'min_setpoint_nf_lt1' : 65.7, #GHz #NOTE
                            'max_setpoint_nf_lt1' : 66.3, #GHz #NOTE
                            'nf_scan_range' : 0.1,

                            'mat_wait_time' : 1, #s
                            'mat_stepsize' : 0.02, #GHz
                            'mat_scan_range' : 0.3, #GHz
                            'min_setpoint_mat' : 62.3, #GHz #NOTE
                            'max_setpoint_mat' : 63.1, #GHz #NOTE
                             
                            'min_gate_voltage' : 17.5, #V #NOTE
                            'max_gate_voltage' : 19.5, #V #NOTE  
                            
                            'optimize_nf_wait_time' : 20, #s
                            'optimize_mat_wait_time' : 20, #s
                            'optimize_gate_wait_time' : 120, #s
                                
                            'tpqi_per_sec_min' : 75, # Threshold  #NOTE 
                            'fraction_failed_min' : 0.9,
                            'cr_checks_per_sec_min': 100,
                            
                            'nf_optimize_threshold_lt1' : 22,#NOTE
                            'nf_optimize_threshold_lt2' : 5, #NOTE
                            'mat_optimize_threshold_lt1' : 10, #NOTE
                            'mat_optimize_threshold_lt2' : 1.8, #NOTE

                            'max_waiting_for_values' : 10, #the program is stopped email sent. in units of 10 sec
                            'max_waiting_reset_gate' : 6, #the gate is reset to the middelemost value when it is higher than the middle value, when waiting for values longer than this in units of 10 s 
                            'max_opt_failed' : 10, #program is stopped, email is sent

                            'send_email' : False,

                            'lt1_opt' : True,
                            'lt2_opt' : True,
                            'opt_nf'  : True,
                            'opt_gate' : True,

                            'gate_factor': 2., # Volts per GHz detuned #NOTE
        }
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
        
    def get_single_setting(self, setting):
        try:
            return self._settings[setting]
        except KeyError:
            print 'unknown setting', setting
            return None
        
    
    def _gss(self, setting):
        return self.get_single_setting(setting)
        
    def set_single_setting(self, setting, val):
        try:
            cur_val=self._settings[setting]
            self._settings[setting] = val
        except KeyError:
            print 'unknown setting', setting
        
    #------------end get set        
               
    #--------------------------------------- public functions

    def init_freq_settings(self):
        
        self._settings['min_setpoint_nf_lt1']=\
                self._ins_pidnewfocus_lt1.get_setpoint()-0.2
        self._settings['max_setpoint_nf_lt1']=\
                self._ins_pidnewfocus_lt1.get_setpoint()+0.2

        self._settings['min_setpoint_nf_lt2']=\
                self._ins_pidnewfocus.get_setpoint()-0.2
        self._settings['max_setpoint_nf_lt2']=\
                self._ins_pidnewfocus.get_setpoint()+0.2

        self._settings['min_setpoint_mat']=\
                self._ins_pidmatisse.get_setpoint()-0.4
        self._settings['max_setpoint_mat']=\
                self._ins_pidmatisse.get_setpoint()+0.4

        self._settings['min_gate_voltage']=\
                self._ins_adwin.get_gate_modulation_var('gate_voltage')*2.0-1.5
        self._settings['max_gate_voltage']=\
                min(self._ins_adwin.get_gate_modulation_var('gate_voltage')*2.0+1.5,20)


    def start(self,init_only=False,**kw):
    
        #pars init can be changed during start
        for key in kw:
            self.set_single_setting(key,kw[key])
        
        self._stop_pressed=False
        self._prev_raw_values=zeros(9)
        self._plt=plt.plot() 
        self._optimize_running=False
        self._wait_index=0
        self._opt_failed_idx=0
        self._lt2_pos_opt=False
        self._get_input_values()
        if not(init_only):
            self.set_is_running(True)
            self._timer=gobject.timeout_add(int(self._read_interval*1e3),\
                    self._check_threshold)
    
    def stop(self):
        self._stop_pressed=True
        self.set_is_running(False)


    #--------------------------------------- private functions    
        
    def _check_threshold(self):
        #print 'Threshold check'

        if not self._is_running:
            return False
        
        lt1_optimize = False
        lt2_optimize = False
        
        dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2,\
                cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = self._get_input_values()

        #print 'dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts'
        #print dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts
        print 'starts avg' , tpqi_starts/dt , '\n'

        if(tpqi_starts/dt < self._gss('tpqi_per_sec_min')):
            if ((cr_checks_lt1/dt > self._gss('cr_checks_per_sec_min')) and \
                    (cr_failed_lt1/cr_checks_lt1 > self._gss('fraction_failed_min'))):
                print 'Optimize LT1'
                lt1_optimize = True
            if ((cr_checks_lt2/dt > self._gss('cr_checks_per_sec_min')) and \
                    (cr_failed_lt2/cr_checks_lt2 > self._gss('fraction_failed_min'))):
                print 'Optimize LT2'
                lt2_optimize = True
                
        if not(self._gss('lt1_opt')):lt1_optimize=False
        if not(self._gss('lt2_opt')):lt2_optimize=False
        
        if (lt1_optimize or lt2_optimize):    
            wait_time_after_optimize = self._optimize(lt1_optimize, lt2_optimize,cr_lt1=1.*cr_cts_lt1/cr_checks_lt1,cr_lt2=1.*cr_cts_lt2/cr_checks_lt2)
            self._wait_after_optimize(wait_time_after_optimize)
            #debug
            #self.stop()
        
        return True

    def _get_input_values(self):
        self._raw_values=zeros(9)    
        self._raw_values+=[time.time(),
                         self._ins_adwin_lt1.get_remote_tpqi_control_var('get_noof_cr_checks') if self._gss('lt1_opt') else 1,
                         self._ins_adwin_lt1.get_remote_tpqi_control_var('get_cr_check_counts') if self._gss('lt1_opt') else 1,
                         self._ins_adwin_lt1.get_remote_tpqi_control_var('get_cr_below_threshold_events') if self._gss('lt1_opt') else 1,
                         self._ins_adwin.get_remote_tpqi_control_var('get_noof_cr_checks') if self._gss('lt2_opt') else 1,
                         self._ins_adwin.get_remote_tpqi_control_var('get_cr_check_counts') if self._gss('lt2_opt') else 1,
                         self._ins_adwin.get_remote_tpqi_control_var('get_cr_below_threshold_events') if self._gss('lt2_opt') else 1,
                         self._ins_adwin.get_remote_tpqi_control_var('get_noof_tpqi_starts') if self._gss('lt2_opt') else 1,
                         1]#self._ins_adwin.get_remote_tpqi_control_var('get_noof_tailcts')]
        
        diff=self._raw_values-self._prev_raw_values
        dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2,\
                cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts\
                = diff[0], diff[1], diff[2], diff[3], diff[4], \
                diff[5], diff[6], diff[7], diff[8]
        self._prev_raw_values =  array(self._raw_values)

        if (cr_checks_lt1 <= 0 and cr_checks_lt2 <= 0 and dt >= 0.2): 
            print 'no cr checks, waiting 10 s, press q to quit. wait index:' ,  self._wait_index
            self._wait_index = self._wait_index + 1
            qt.msleep(10) #wait for the next measurement cycle to begin
            if (self._wait_index > self._gss('max_waiting_reset_gate')):
                self._lt2_pos_opt=True
            if (self._wait_index > self._gss('max_waiting_for_values')) or \
                            (not(self.get_is_running())) or \
                            (msvcrt.kbhit() and msvcrt.getch() == 'q'):
                self._send_mail('Waiting time for cr_checks exceeded or q pressed')
                self.stop()
                return 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
            else:    
                return self._get_input_values()
        else:
            self._wait_index = 0       
        
        return  dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2, cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts

        
    def _optimize(self,lt1_optimize, lt2_optimize, cr_lt1=100, cr_lt2=100):
        #debug
        #self.stop()
        #return
        if lt2_optimize and self._lt2_pos_opt:
            self._lt2_pos_opt=False
            self.reset_gate()
            return self._gss('optimize_gate_wait_time')
        #if lt1_optimize:
        #    if(self.optimize_newfocus_steps(1,+1)): return
        #    if(self.optimize_newfocus_steps(1,-1)): return
        #if lt2_optimize:
        #    if(self.optimize_newfocus_steps(2,+1)): return
        #    if(self.optimize_newfocus_steps(2,-1)): return
        if self._gss('opt_nf') and random.random()>0.5:
            print 'Optimizing NF'
            if lt2_optimize and cr_lt2>self._gss('mat_optimize_threshold_lt2'):
                 print 'NF LT2'
                 optimum_lt1,optimum_lt2 = self.optimize_newfocus(2)
                 if optimum_lt2 > 0: return self._gss('optimize_nf_wait_time')
            if lt1_optimize and cr_lt1>self._gss('mat_optimize_threshold_lt1'):
                 print 'NF LT1'
                 optimum_lt1,optimum_lt2 = self.optimize_newfocus(1)
                 #if optimum_lt1 > 0: return self._gss('optimize_nf_wait_time')

             
        optimum_lt1,optimum_lt2 = self.optimize_matisse(lt1_optimize, lt2_optimize)
        if ((lt2_optimize) and (optimum_lt2 > 0)):
            self.optimize_gate(optimum_lt2)
            return self._gss('optimize_gate_wait_time')
        else:
            return self._gss('optimize_mat_wait_time')

        if not((optimum_lt2 > 0) or (optimum_lt1 > 0)): 
            self._opt_failed_idx+=1
        else:
            self._opt_failed_idx=0

        if (self._opt_failed_idx > self._gss('max_opt_failed')): 
            self.stop()
            self._send_mail('maximum optimisations failed')
        
        return self._gss('optimize_nf_wait_time')

    def _send_mail(self,reason):
        subject= 'Warning from TPQI/LDE Optimiz0r!'
        message = 'Warning from TPQI/LDE Optimiz0r: \n'+\
                      ' Reason: %s'%(reason) + '\n' + \
                      'Please help me!!!\n xxx LT2'
            #recipients  = ['B.J.Hensen@tudelft.nl', 'h.bernien@tudelft.nl', 'w.pfaff@tudelft.nl', 'M.S.Blok@tudelft.nl']
        recipients  = 'B.J.Hensen@tudelft.nl'
        print message
        if self._gss('send_email'):
            print 'Attempting to send email'
            if qt.instruments['gmailer'].send_email(recipients,subject,message):
        	    print 'Warning email message sent'

    def _wait_after_optimize(self,wait_time):
        gobject.source_remove(self._timer)
        self.set_is_running(False)
        gobject.timeout_add(int(wait_time*1e3), self._continue_after_wait)
        
    def _continue_after_wait(self):
        if not(self._stop_pressed):
            self.set_is_running(True)
            self._timer= gobject.timeout_add(int(self._read_interval*1e3), self._check_threshold)
    
    def optimize_newfocus(self,setup,do_optimize=True,do_plot=True):
        ins_pid = self._ins_pidnewfocus_lt1 if setup==1 else self._ins_pidnewfocus
        min_setpoint=self._gss('min_setpoint_nf_lt1') if setup==1 else self._gss('min_setpoint_nf_lt2')
        max_setpoint=self._gss('max_setpoint_nf_lt1') if setup==1 else self._gss('max_setpoint_nf_lt2')
        optimum_lt1=-1.0
        optimum_lt2=-1.0
        
        self._get_input_values()
        qt.msleep(self._gss('nf_wait_time'))
        dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2,\
                cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = self._get_input_values()
        
        initial_cr_cts_per_check_lt1=-1.0
        if cr_checks_lt1>0: initial_cr_cts_per_check_lt1=cr_cts_lt1/cr_checks_lt1
        initial_cr_cts_per_check_lt2=-1.0
        if cr_checks_lt2>0: initial_cr_cts_per_check_lt2=cr_cts_lt2/cr_checks_lt2
        print 'initial values:',initial_cr_cts_per_check_lt1, initial_cr_cts_per_check_lt2 
        lt1_cts_per_check, lt2_cts_per_check, tail_cts_per_tpqi =  self.optimize_scan(ins_pid,
                                                                   min_setpoint,
                                                                   max_setpoint,
                                                                   self._gss('nf_scan_range'),
                                                                   self._gss('nf_stepsize'),
                                                                   self._gss('nf_wait_time'))
        if do_plot:
            self._plt.clear()
            if len(lt2_cts_per_check)>0: self._plt=plt.plot(lt2_cts_per_check)
            if len(lt1_cts_per_check)>0: self._plt=plt.plot(lt1_cts_per_check)
            if len(tail_cts_per_tpqi)>0: self._plt=plt.plot(tail_cts_per_tpqi)

        if ((setup==1) and do_optimize and (len(lt1_cts_per_check)>4) and \
                (max(lt1_cts_per_check)[0] >=  initial_cr_cts_per_check_lt1) and\
                (max(lt1_cts_per_check)[0] >= self._gss('nf_optimize_threshold_lt1'))):
            optimum_lt1=max(lt1_cts_per_check)[1]
            print 'Setting new setpoint newfocus lt1:', optimum_lt1
            ins_pid.set_setpoint(optimum_lt1)
        
        if ((setup==2) and do_optimize and (len(lt2_cts_per_check)>4) and \
                (max(lt2_cts_per_check)[0] >=  initial_cr_cts_per_check_lt2)) and \
                (max(lt2_cts_per_check)[0] >= self._gss('nf_optimize_threshold_lt2')):
            optimum_lt2=max(lt2_cts_per_check)[1]
            print 'Setting new setpoint newfocus lt2:', optimum_lt2
            ins_pid.set_setpoint(optimum_lt2)
        
        qt.msleep(self._gss('nf_wait_time'))

        return optimum_lt1, optimum_lt2

    
    def optimize_newfocus_steps(self,setup,direction):
        print 'Optimizing Newfocus LT', setup, 'direction', direction  
        
        ins_pid = self._ins_pidnewfocus_lt1 if setup==1 else self._ins_pidnewfocus
        min_setpoint=self._gss('min_setpoint_nf_lt1') if setup==1 else self._gss('min_setpoint_nf_lt2')
        max_setpoint=self._gss('max_setpoint_nf_lt1') if setup==1 else self._gss('max_setpoint_nf_lt2')
        self._get_input_values()
        qt.msleep(self._gss('nf_wait_time'))
        cr_checks=zeros(3)
        cr_cts=zeros(3)
        cr_failed=zeros(3)
        dt, cr_checks[1], cr_cts[1], cr_failed[1], cr_checks[2], cr_cts[2],\
                cr_failed[2], tpqi_starts, tail_cts = self._get_input_values()
        
        current_setpoint=ins_pid.get_setpoint()
        
        i=0
        while(min_setpoint < current_setpoint < max_setpoint):
            i=i+1
            print 'newfocus lt2 optimize up', i
            prev_dt, prev_cr_checks_lt2, prev_cr_cts_lt2, prev_tpqi_starts, \
                    prev_tail_cts = dt, cr_checks[setup], cr_cts[setup], tpqi_starts, tail_cts
            current_setpoint = current_setpoint + direction*self._gss('nf_stepsize')
            self.ins_pid.set_setpoint(current_setpoint)
            qt.msleep(2*self._gss('nf_wait_time'))
            self._get_input_values()
            qt.msleep(self._gss('nf_wait_time'))
            dt, cr_checks[1], cr_cts[1], cr_failed[1], cr_checks[2], cr_cts[2],\
                    cr_failed[2], tpqi_starts, tail_cts = self._get_input_values()
            if ((cr_checks[setup]/dt < self._gss('cr_checks_per_sec_min')) or \
                    (cr_cts[setup]/cr_checks[setup] < prev_cr_cts[setup]/prev_cr_checks[setup]) or \
                    False):#(tail_cts/tpqi_starts < prev_tail_cts/prev_tpqi_starts)): 
                break 

        current_setpoint = current_setpoint - direction*self._gss('nf_stepsize')
        ins_pid.set_setpoint(current_setpoint)
        
        if i>1: return True
        
        return False
    
    def optimize_scan(self,ins_pid,min_setpoint,max_setpoint,\
                      scan_range,stepsize,wait_time,do_plot=True):
    
        lt1_cts_per_check=[]
        lt2_cts_per_check=[]
        tail_cts_per_tpqi=[]
        
        initial_setpoint = ins_pid.get_setpoint()
        freq_scan_min = max(min_setpoint,initial_setpoint - scan_range/2.)
        freq_scan_max = min(max_setpoint, initial_setpoint + scan_range/2.)
        
        steps=int((freq_scan_max - freq_scan_min) / stepsize)
        print initial_setpoint,freq_scan_min, freq_scan_max, steps
        udrange=append(linspace(initial_setpoint,freq_scan_min,int(steps/2.)),
                linspace(freq_scan_min, freq_scan_max, steps))
        udrange=append(udrange,linspace(freq_scan_max,initial_setpoint,int(steps/2.)))
        self._get_input_values()
        for freq in udrange:
            ins_pid.set_setpoint(freq)
            qt.msleep(wait_time*.5)
            cur_freq=freq
            cur_freq = ins_pid.get_value()
            qt.msleep(wait_time*.5)
            dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2,\
                    cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = self._get_input_values()
            if cr_checks_lt1>0: lt1_cts_per_check.append((cr_cts_lt1/cr_checks_lt1,cur_freq))
            if cr_checks_lt2>0: lt2_cts_per_check.append((cr_cts_lt2/cr_checks_lt2,cur_freq))
            if tpqi_starts>0: tail_cts_per_tpqi.append((tail_cts/tpqi_starts,cur_freq))
        
        return lt1_cts_per_check, lt2_cts_per_check, tail_cts_per_tpqi

    def optimize_matisse(self,lt1_optimize, lt2_optimize, do_plot=True):
        print 'Optimizing Matisse'
        #scan the matise in the preset range around the current setpoint, find optima for lt1 and lt2 cr counts
        optimum_lt1=-1.0
        optimum_lt2=-1.0
        
        self._get_input_values()
        qt.msleep(self._gss('mat_wait_time'))
        dt, cr_checks_lt1, cr_cts_lt1, cr_failed_lt1, cr_checks_lt2,\
                cr_cts_lt2, cr_failed_lt2, tpqi_starts, tail_cts = self._get_input_values()
        
        initial_cr_cts_per_check_lt1=-1.0
        if cr_checks_lt1>0: initial_cr_cts_per_check_lt1=cr_cts_lt1/cr_checks_lt1
        initial_cr_cts_per_check_lt2=-1.0
        if cr_checks_lt2>0: initial_cr_cts_per_check_lt2=cr_cts_lt2/cr_checks_lt2
        print 'initial values:',initial_cr_cts_per_check_lt1, initial_cr_cts_per_check_lt2
        lt1_cts_per_check, lt2_cts_per_check, tail_cts_per_tpqi =  self.optimize_scan(self._ins_pidmatisse,
                                                                   self._gss('min_setpoint_mat'),
                                                                   self._gss('max_setpoint_mat'),
                                                                   self._gss('mat_scan_range'),
                                                                   self._gss('mat_stepsize'),
                                                                   self._gss('mat_wait_time'))
    
        if do_plot:
            self._plt.clear()
            if len(lt2_cts_per_check)>0: self._plt=plt.plot(lt2_cts_per_check)
            if len(lt1_cts_per_check)>0: self._plt=plt.plot(lt1_cts_per_check)

        if ((lt1_optimize) and (len(lt1_cts_per_check)>0) and \
                (max(lt1_cts_per_check)[0] >=  initial_cr_cts_per_check_lt1) and \
                (max(lt1_cts_per_check)[0]>= self._gss('mat_optimize_threshold_lt1'))):
            #if self._par_fit:
            #    print 'Fitting not yet implemented'
            #    pass
            #    #a, xc, k = copysign(max(y), V_max + V_min), copysign(.5, V_max + V_min), copysign(5., V_max + V_min)
            #    #fitres = fit.fit1d(x,y, common.fit_AOM_powerdependence, a, xc, k, do_print=True, do_plot=False, ret=True)
            optimum_lt1=max(lt1_cts_per_check)[1]
            print 'Setting new setpoint matisse:', optimum_lt1
            self._ins_pidmatisse.set_setpoint(optimum_lt1)
        
        if ((lt2_optimize) and (len(lt2_cts_per_check)>0) and \
                (max(lt2_cts_per_check)[0] >=  initial_cr_cts_per_check_lt2)) and \
                (max(lt2_cts_per_check)[0]>= self._gss('mat_optimize_threshold_lt2')):
            optimum_lt2=max(lt2_cts_per_check)[1]
        
        qt.msleep(self._gss('mat_wait_time'))

        return optimum_lt1, optimum_lt2

    def optimize_gate(self,optimum_lt2):
        if not(self._gss('opt_gate')):
            print 'Setting new setpoint matisse (LT2):', optimum_lt2
            self._ins_pidmatisse.set_setpoint(optimum_lt2)
            return
        print 'Optimizing Gate'
        gate_change = (self._ins_pidmatisse.get_setpoint()-optimum_lt2)*self._gss('gate_factor') 
        new_gate_voltage = self._ins_adwin.get_gate_modulation_var('gate_voltage')*2.0 + gate_change
        if (self._gss('min_gate_voltage') < new_gate_voltage < self._gss('max_gate_voltage')):
            print'Changeing gate voltage to:',new_gate_voltage, '(',gate_change,')'
            self._ins_adwin.set_gate_modulation_var(gate_voltage=new_gate_voltage/2.0)
        else: print 'New gate voltage',new_gate_voltage, 'outside range'

    def reset_gate(self):
        if not(self._gss('opt_gate')):
            return
        cur_gate_voltage=self._ins_adwin.get_gate_modulation_var('gate_voltage')*2.0
        new_gate_voltage= (self._gss('min_gate_voltage')+self._gss('min_gate_voltage'))/2.-0.2     
        if cur_gate_voltage > new_gate_voltage+0.4:
            print 'resetting gate voltage to halfway range:', new_gate_voltage, 'V'
            self._ins_adwin.set_gate_modulation_var(gate_voltage=new_gate_voltage/2.0)


