import qt
from multiple_optimizer import multiple_optimizer
import numpy as np
import time
import types
from instrument import Instrument
import instrument_helper
import os
from lib import config

class lt2_ssro_optimizer(multiple_optimizer):

    def __init__(self,name,optimize_yellow=True):
        multiple_optimizer.__init__(self,name)
        ins_pars  = {'starts_min'         :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':100},
                    'cr_succes_min'       :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':0.6},
                    'cr_checks_min'       :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':100},
                    'threshold_probe'     :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':20},
                    'threshold_preselect' :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':20},
                    'variance_yellow_min' :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':50},
                    'threshold_init'      :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':15},
                    }
        
        instrument_helper.create_get_set(self,ins_pars)
        self.add_function('set_high_threshold')
        self.add_function('set_low_threshold')
        
        self._stepper_size=0.01
        self._last_optimizer=''
        self.plot_name='lt2_ssro_optimizer_plot'
        
        self._ins_adwin=qt.instruments['adwin']

        ##values
        self._get_value_f={
                't'             :    time.time,
                'cr_checks'     :    lambda: self._ins_adwin.get_singleshot_var('get_noof_cr_checks'),
                'probe_cts'     :    lambda: self._ins_adwin.get_singleshot_var('get_cr_check_counts'),
                'repumps'       :    lambda: self._ins_adwin.get_singleshot_var('get_cr_below_threshold_events'),
                'starts'        :    lambda: self._ins_adwin.get_singleshot_var('get_noof_repetitions'),
                }  
        self._values={}
        for key in self._get_value_f.keys():
            self._values[key]=0
        
        ##optimizers
        #pids
        
        pid='pidnewfocus'
        pid_ins=qt.instruments[pid]
        self.add_optimizer(pid+'_optimizer',
                          get_control_f=pid_ins.get_value,
                          set_control_f=lambda x: pid_ins.set_setpoint(x),
                          get_value_f= self._get_value_f['probe_cts'],
                          get_norm_f= self._get_value_f['cr_checks'],
                          plot_name=self.plot_name)
        #self.create_stepper_buttons(pid)
        pid='pidmatisse'
        pid_ins_n=qt.instruments[pid]
        self.add_optimizer(pid+'_optimizer',
                          get_control_f=pid_ins_n.get_value,
                          set_control_f=lambda x: pid_ins_n.set_setpoint(x),
                          get_value_f= self._get_value_f['probe_cts'],
                          get_norm_f= self._get_value_f['cr_checks'],
                          plot_name=self.plot_name)
        #self.create_stepper_buttons(pid)
        
        self._optimize_yellow=optimize_yellow
        if self._optimize_yellow:
            pid='pidyellow'
            pid_ins_y=qt.instruments[pid]
            self.add_optimizer(pid+'_optimizer',
                              get_control_f=pid_ins_y.get_value,
                              set_control_f=lambda x: pid_ins_y.set_setpoint(x),
                              get_value_f= self._get_value_f['probe_cts'],
                              get_norm_f= self._get_value_f['cr_checks'],
                              plot_name=self.plot_name)
            #self.create_stepper_buttons(pid)
        #gate
        #self.add_optimizer('gate_optimizer',
        #                  get_control_f=lambda:self._ins_adwin.get_dac_voltage('gate'),
        #                  set_conrol_f=lambda x: self._gate_scan_to_voltage(x),
        #                  get_value_f=self._get_value_f['probe_cts'],
        #                  plot_name=self.plot_name)
                # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
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

    def _gate_scan_to_voltage(self,voltage, stepsize=0.05, dwell_time=0.05):
        cur_v= self._ins_adwin.get_dac_voltage('gate')
        steps=int(abs(cur_v-voltage)/stepsize)
        for v in np.linspace(cur_v, voltage, steps):
            self._ins_adwin.set_dac_voltage(('gate',v))
            qt.msleep(dwell_time)
            
    def create_stepper_buttons(self,pid):
        ins_pid=qt.instruments[pid]
        fupname=pid+'_up'
        fdownname=pid+'_down'
        def f_up():
            ins_pid.set_setpoint(ins_pid.get_setpoint()+self._stepper_size)
        def f_down():
            ins_pid.set_setpoint(ins_pid.get_setpoint()-self._stepper_size)
        f_up.__name__= fupname  
        f_down.__name__= fdownname   
        setattr(self,fupname,f_up)
        setattr(self,fdownname,f_down)
        self.add_function(fupname)
        self.add_function(fdownname)
            
    def start(self):
        self._update_values()
        multiple_optimizer.start(self)        
    
    def _update_values(self):
        d_values={}
        for key,f_val in self._get_value_f.items():
            new_value=f_val()
            d_values[key]=new_value-self._values[key]
            self._values[key]=new_value      
        return d_values
        
    def _optimize(self,cur_optimizer):
        print 'optimizing:', cur_optimizer
        ins_opt=qt.instruments[cur_optimizer]
        self._is_waiting=True
        
        self.set_high_threshold()
        ins_opt.optimize()
        if ins_opt.get_last_max()>self.get_threshold_init:
            self.set_low_threshold()
        
        self._last_optimizer=cur_optimizer
        self.start_waiting(ins_opt.get_wait_time())
        return True
    
    def _check_treshold(self):
        if not self.get_is_running():
            return False
        if self._is_waiting:
            print 'waiting...'
            return True
            
        d_vals=self._update_values()
        print 'average cr:', float(d_vals['probe_cts'])/d_vals['cr_checks'], 'starts per sec:', d_vals['starts']/d_vals['t']
        
        if float(d_vals['probe_cts'])/d_vals['cr_checks'] > self.get_threshold_init():
            self.set_low_thresholds()
        
        if (d_vals['cr_checks']/d_vals['t'])<self.cr_checks_min:
            print 'too little cr checks:', d_vals['cr_checks']/d_vals['t']
            return True
        
        if (d_vals['starts']/d_vals['t'])>self.starts_min:
            print 'enough starts:', d_vals['starts']/d_vals['t']
            return True
         
        if (1-float(d_vals['repumps'])/d_vals['cr_checks'])>self.cr_succes_min:
            print 'cr succes fraction high enough:', \
                    (1-d_vals['repumps']/d_vals['cr_checks'])
            return True
        
        try:
            ins_opt=qt.instruments[self._last_optimizer]
            if ins_opt.get_variance()>self.get_variance_yellow_min() and self._optimize_yellow:
                return self._optimize('pidyellow')
        except:
            pass
        
        try_optimizers=[]
        min_value=0
        for opt in self.get_optimizers():
            ins_opt=qt.instruments[opt]
            if ins_opt.get_order_index() == 1:
                try_optimizers.append(opt)
                min_value=max(min_value,ins_opt.get_min_value())
        if float(d_vals['probe_cts'])/d_vals['cr_checks'] > min_value:
            try_optimizers=self.get_optimizers()[:]
        
        try:
            try_optimizers.remove(self._last_optimizer)
        except:
            pass
            
        if len(try_optimizers)>0:
            ri=np.random.randint(0,len(try_optimizers))
            cur_optimizer=try_optimizers[ri]
        else:
            print 'No optimizors found'
            return True
        
        return self._optimize(cur_optimizer)
        
    def set_high_threshold(self):
        #self._current_low_threshold_probe=self._ins_adwin.get_singleshot_var('set_CR_probe')
        #self._current_low_threshold_preselect=self._ins_adwin.get_singleshot_var('set_CR_preselect')
        self._ins_adwin.set_singleshot_var(set_CR_probe=1000,set_CR_preselect=1000)
     
    def set_low_threshold(self):
        self._ins_adwin.set_singleshot_var(set_CR_probe=self.get_threshold_probe(),
                                           set_CR_preselect=self.get_threshold_preselect())
        