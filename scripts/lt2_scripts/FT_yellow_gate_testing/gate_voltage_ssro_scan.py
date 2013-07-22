import msvcrt
import gobject

tresholds=20

def set_thresholds():
    print 'setting measuing thresholds'
    tuner.set_threshold_probe(tresholds)
    tuner.set_threshold_preselect(tresholds)
    tuner.set_read_interval(60)
    tuner.stop()
    qt.msleep(20)
    tuner.start()
    return False

aoms=['MatisseAOM','NewfocusAOM','YellowAOM','GreenAOM']
cw_powers=[exdict.ssroprotocol['Ex_CR_amplitude'],
           exdict.ssroprotocol['A_CR_amplitude'],
           exdict.ssroprotocol['yellow_repump_amplitude'],
           0]

gate_stepsize=2./45 #V
gate_final=1.5
gate_voltages=linspace(0,gate_final,int(gate_final/gate_stepsize))
std_name='ADwin_SSRO_FT_GV_'

pid_nf_step=0.4*2./3. #GHz
pid_nf2_step=0.4*2./3 #GHz
pidyellow_step=0.1*2./3 #GHz
opt_time_after_gate=300 #s

pidnewfocus.set_setpoint(57.8)
pidnewfocus2.set_setpoint(55)
pidyellow.set_setpoint(33.7)
stools.turn_off_lasers()   

for gv in gate_voltages:
    if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
    stools.gate_scan_to_voltage(gv)
    print 'setting gv', gv
    cur_name=std_name+str(gv)
    
    timer_id=gobject.timeout_add(int(opt_time_after_gate*1000),set_thresholds)
    tuner.set_read_interval(10)
    tuner.set_threshold_probe(1000)
    tuner.set_threshold_preselect(1000)
    tuner.stop()
    tuner.start()
    ssro.ssro_ADwin_Cal(reps=10000, Ex_p=30e-9, sweep_power=False, phase_lock=0, name=cur_name)
    
    pidnewfocus.set_setpoint(pidnewfocus.get_setpoint()+pid_nf_step)
    pidnewfocus2.set_setpoint(pidnewfocus2.get_setpoint()+pid_nf2_step)
    pidyellow.set_setpoint(pidyellow.get_setpoint()+pidyellow_step)
    
    stools.set_laser_powers(aoms,cw_powers)
    gobject.source_remove(timer_id)

stools.turn_off_lasers()    
tuner.stop()
stools.gate_scan_to_voltage(0)


