import time
import qt
import data
import gobject
import msvcrt
import numpy as np


#measurment name
mname='laserscan_SIL2_'

# measurement parameters
start_v = 1.5# 2.5#
stop_v = 0.# 1.0#-.2#
steps = 3001
pxtime = 15  #ms
green_during = 0.5e-6
green_before = 200e-6
red_during= 5e-9
f_offset = 470400 # GHz
mw = True # True
amp = True
mw_power = -12
mw_frq = 2.8286e9  #2.8286e9 #Lt2   2.8241e9  #LT1
LT2 = True
reps = 1

gate_phase_locking=1 #has no effect if measuring LT1 #SO LEAVE IT AT 1
good_phase=-1

# end measurement parameters

# plotting
do_smooth = True
plot_strain_lines=True

# This version of laserscan now includes an abort function. To abort the laser
# scan, press 'q'.

def power_ok():
    ret = True
    if mw and amp and mw_power > -20:
        ret=False
        max_idx = 30
        idx = 0
        while idx<max_idx:
            print 'Warning: power > -20 dBm, hit c to continue' 
            qt.msleep(1)
            idx += 1
            if msvcrt.kbhit():
                kbchar=msvcrt.getch()
                if kbchar == "q":
                    print 'Quiting laser scan'
                    break
                if kbchar == "c":
                    print 'Continuing laser scan'
                    ret = True
                    break
    return ret

abort_check_time = 1000 #ms

def check_for_abort(ins_laser_scan):
    if msvcrt.kbhit() and msvcrt.getch() == "q" :
        global do_smooth, plot_strain_lines
        do_smooth = False
        plot_strain_lines=False
        ins_laser_scan.abort_scan()

        return False
    return True

def rolling_avg(xvals, length=10):
    new = np.zeros(len(xvals))
    for i,x in enumerate(xvals):
        _length = length
        if i < length:
            _length = i
        elif i > len(xvals)-length:
            _length = len(xvals)-i
        
        idxs = range(i-_length,i+_length)
        try:
            new[i] = sum([ xvals[idx] for idx in idxs ])/2./_length
        except ZeroDivisionError:
            print ' error in rolling average for i=' ,i,'length:',_length
            new[i]=xvals[i]
    return new


def laserscan(dataname=mname, 
            start_v = start_v,
            stop_v = stop_v,
            steps = steps,
            pxtime = pxtime, #ms
            green_during = green_during,
            green_before = green_before,
            red_during= red_during,
            f_offset = f_offset, # GHz
            mw = mw, # True
            amp = amp,
            mw_power = mw_power,
            mw_frq = mw_frq,
            LT2 = LT2,
            gate_phase_locking=gate_phase_locking, #has no effect if measuring LT1 #SO LEAVE IT AT 1
            good_phase=good_phase,
            do_smooth = do_smooth,
            plot_strain_lines=plot_strain_lines):
    
    if LT2:
        ins_adwin = qt.instruments['adwin']
        ins_laser_scan = qt.instruments['laser_scan']
        ins_mw = qt.instruments['SMB100']
        ins_adwin.set_linescan_var(set_phase_locking_on=gate_phase_locking,
               set_gate_good_phase=good_phase)
        ins_green=qt.instruments['GreenAOM']
        ins_newfocus=qt.instruments['NewfocusAOM']

    else:
        ins_adwin = qt.instruments['adwin_lt1']
        ins_laser_scan = qt.instruments['laser_scan_lt1']
        ins_mw = qt.instruments['SMB100_lt1']
        ins_green=qt.instruments['GreenAOM_lt1']
        ins_newfocus=qt.instruments['NewfocusAOM_lt1']

    
    ins_laser_scan.set_StartVoltage(start_v)
    ins_laser_scan.set_StopVoltage(stop_v)
    ins_laser_scan.set_ScanSteps(steps)
    ins_laser_scan.set_IntegrationTime(pxtime)
    ins_running = True
    step = 0

    #_before_voltages = ins_adwin.get_dac_voltages(['green_aom','newfocus_aom'])
    #FIXME NEED A CONDITION FOR WHEN THE Newfocus IS ONE THE AWG.

    ins_green.set_power(green_before)
    qt.msleep(1)

    ins_newfocus.set_power(red_during)
    ins_green.set_power(green_during)
    
    #make sure microwaves are off 
    ins_mw.set_status('off')

    if mw:
        ins_mw.set_iq('off')
        ins_mw.set_pulm('off')
        ins_mw.set_power(mw_power)
        ins_mw.set_frequency(mw_frq)
        ins_mw.set_status('on')

    qt.mstart()
    qt.Data.set_filename_generator(data.DateTimeGenerator())
    d = qt.Data(name=dataname)
    d.add_coordinate('voltage [V]')
    d.add_value('frequency [GHz]')
    d.add_value('counts')
    d.create_file()

    p_f = qt.Plot2D(d, 'rO', name='frequency', coorddim=0, valdim=1, clear=True)
    p_c = qt.Plot2D(d, 'bO', name='counts', coorddim=1, valdim=2, clear=True)

    # go manually to initial position
    ins_adwin.set_dac_voltage(('newfocus_frq',start_v))
    qt.msleep(1)

    ins_laser_scan.start_scan()
    qt.msleep(1)
    timer_id=gobject.timeout_add(abort_check_time,check_for_abort,ins_laser_scan)

    while(ins_running):
      
        ins_running = not ins_laser_scan.get_TraceFinished()
        
        _step = ins_laser_scan.get_CurrentStep()

        qt.msleep(0.3)

        if _step > step:
            _v = ins_laser_scan.get_voltages()[step:_step]
            _f = ins_laser_scan.get_frequencies()[step:_step] - f_offset
            _c = ins_laser_scan.get_counts()[step:_step]
           
            # print _v,_f,_c
            _valid_elmnts=(_f>0)
            
            _v=_v[_valid_elmnts]
            _f=_f[_valid_elmnts]
            _c=_c[_valid_elmnts]

            if not(len(_v) == 0): 
                if len(_v) == 1:
                    _v = _v[0]
                    _f = _f[0]
                    _c = _c[0]                
                d.add_data_point(_v,_f,_c)

            step = _step
            p_f.update()
            p_c.update()

    ins_laser_scan.end_scan()
    gobject.source_remove(timer_id)
    #ins_adwin.set_dac_voltage(['green_aom',_before_voltages[0]])
    #ins_adwin.set_dac_voltage(['newfocus_aom',_before_voltages[1]])
    if mw:
        ins_mw.set_status('off')
    qt.mend()
   
    pfsave=p_f
    pcsave=p_c

    if do_smooth:            
        basepath = d.get_filepath()[:-4]
        ds = qt.Data()
        ds.set_filename_generator(data.IncrementalGenerator(basepath))
        ds.add_coordinate('voltage [V]')
        ds.add_value('smoothed frequency [GHz]')
        ds.add_value('counts')
        ds.create_file()

        p_fs = qt.Plot2D(ds, 'r-', name='frequency smoothed', coorddim=0, valdim=1, clear=True)
        p_cs = qt.Plot2D(ds, 'b-', name='counts smoothed', coorddim=1, valdim=2, clear=True)
         
        ds.add_data_point(d.get_data()[:,0], rolling_avg(d.get_data()[:,1]), 
                d.get_data()[:,2])

        ds.close_file()
        pfsave=p_fs
        pcsave=p_cs

    if plot_strain_lines:        
        try:
            from analysis import nvlevels
            Ey_line=float(raw_input('Ey line?')) #GHz
            Ex_line=float(raw_input('Ex line?')) #GHz
            lx,ly=nvlevels.get_ES_ExEy_plottable(Ex_line,Ey_line,max(d.get_data()[:,2]))
            pcsave.add(lx,ly)
        except ValueError:
            print 'Could not understand input for lines'
            pass

    pfsave.save_png()
    pcsave.save_png()

    d.close_file()
    qt.Data.set_filename_generator(data.DateTimeGenerator())

    if LT2:  
        ins_adwin.set_linescan_var(set_phase_locking_on=0,
           set_gate_good_phase=0)
    ins_newfocus.set_power(0)
    ins_green.set_power(green_before)


def main():
    if power_ok():
        for k in range(reps):
            print 'Repetition %s of %s'%(k,reps-1)
            setup='LT2' if LT2 else 'LT1'
            dataname = mname+','+setup+str(int(red_during*1E9))+\
            'nW'+'_mw_'+str(mw)+'_'+str(int(green_during*1E9))+'nW_green_'+\
            str(k)+'gate_phase'+str(gate_phase_locking)+','+str(good_phase)
            
            laserscan(dataname = dataname)
            if k!=reps-1:
                qt.msleep(3)
            
if __name__ == '__main__':
    main()

