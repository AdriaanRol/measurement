import qt
import data
from measurement.measurement import Measurement
import measurement.PQ_measurement_generator_v2 as pqm
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence

name='ESR_SIL2'
start_f =   2.80    #in GHz
stop_f  =   2.95    #in GHz
steps   =   51
mw_power_lt1 = -20  #in dBm
mw_power_lt2 = 10   #in dBm
int_time = 30       #in ms
reps = 15

lt1 = True

#generate list of frequencies
f_list = linspace(start_f*1e9, stop_f*1e9, steps)

if lt1:
    ins_smb = qt.instruments['SMB100_lt1']
    ins_adwin = qt.instruments['adwin_lt1']
    ins_counters = qt.instruments['counters_lt1']
    counter = 2
    MW_power = mw_power_lt1
else:
    ins_smb = qt.instruments['SMB100']
    ins_adwin = qt.instruments['adwin']
    ins_counters = qt.instruments['counters']
    counter = 1
    MW_power = mw_power_lt2

# create data object
qt.mstart()

ins_smb.set_iq('off')
ins_smb.set_pulm('off')
ins_smb.set_power(MW_power)
ins_smb.set_status('on')

qt.msleep(0.5)

total_cnts = zeros(steps)
for cur_rep in range(reps):
    for i,cur_f in enumerate(f_list):
        
        ins_smb.set_frequency(cur_f)
        qt.msleep(0.03)
        
        total_cnts[i]+=ins_adwin.measure_counts(int_time)[counter-1]
        # qt.msleep(0.01)

    p_c = qt.Plot2D(f_list, total_cnts, 'bO-', name='ESR', clear=True)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
    print cur_rep
ins_smb.set_status('off')

d = qt.Data(name='ESR')
d.add_coordinate('frequency [GHz]')
d.add_value('counts')
d.create_file()


d.add_data_point(f_list, total_cnts)
pqm.savez(name,freq=f_list,counts=total_cnts)
d.close_file()
p_c = qt.Plot2D(d, 'bO-', coorddim=0, valdim=1, name='ESR', clear=True)

qt.mend()

ins_counters.set_is_running(1)
