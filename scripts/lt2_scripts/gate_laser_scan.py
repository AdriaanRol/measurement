import gobject
import qt
import laser_scan_v7 as ls

reload(ls)

class GateLaserScan():

    def __init__(self):
        pass

    def stop_measurement(self):
        self.m_running=False

    def measurement_cycle(self):
        
        if not self.m_running:
            return False
            
        self.ins_adwin.set_simple_counting()
        self.counters_lt2.set_is_running(True)
        self.green_aom_lt2.set_power(200e-6)
        qt.msleep(1)
        self.optimizor_lt2.optimize(cnt=1,cycles=2, int_time=50)

        for i in range(self.reps_per_point):
            dataname ='LT2'+str(int(ls.red_during*1E9))+\
                'nW'+'_mw_'+str(ls.mw)+'_'+str(int(ls.green_during*1E9))+'nW_green_'+\
                str(i)+'gate_+'+str(int(self.cur_gate_voltage))
            ls.laserscan(dataname=dataname, good_phase=1)
            qt.msleep(10)
            dataname ='LT2'+str(int(ls.red_during*1E9))+\
                'nW'+'_mw_'+str(ls.mw)+'_'+str(int(ls.green_during*1E9))+'nW_green_'+\
                str(i)+'gate_-'+str(int(self.cur_gate_voltage))
            ls.laserscan(dataname=dataname, good_phase=-1)
            qt.msleep(10)
        
        self.cur_gate_voltage =  self.cur_gate_voltage +  self.gate_step
        
        if  self.cur_gate_voltage >  self.gate_max:
            self.m_running=False
            return False
        
        self.ins_adwin.set_gate_modulation_var(gate_voltage=self.cur_gate_voltage/2.)

        return True
    
if __name__ == '__main__':
    gls=GateLaserScan()
    gls.wait_after_gate=40*60#s
    gls.cur_gate_voltage=18.0
    gls.gate_step=1.0 #Vpp
    gls.gate_max=20.0 #Vpp
    gls.reps_per_point=3

    gls.ins_adwin = qt.instruments['adwin']
    gls.counters_lt2 = qt.instruments['counters']
    gls.optimizor_lt2 = qt.instruments['optimiz0r']
    gls.green_aom_lt2 = qt.instruments['GreenAOM']
    gls.m_running=True
    gls.measurement_cycle()
    timer_id=gobject.timeout_add_seconds(gls.wait_after_gate,gls.measurement_cycle)
