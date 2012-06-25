import qt
import data
from measurement.measurement import Measurement
import measurement.PQ_measurement_generator_v2 as pqm
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence

name='ESR_SIL10'
start_f =   2.82
stop_f  =   2.99
steps   =   151
MW_power =  20
int_time = 30 # ms
channel = 0
reps = 50

#generate list of frequencies
f_list = linspace(start_f*1e9, stop_f*1e9, steps)

ins_smb = qt.instruments['SMB100']
ins_adwin = qt.instruments['adwin']

# create data object
qt.mstart()

ins_smb.set_iq('off')
ins_smb.set_pulm('off')
ins_smb.set_power(MW_power)
ins_smb.set_status('on')

qt.msleep(0.1)

total_cnts = zeros(steps)
for cur_rep in range(reps):
    for i,cur_f in enumerate(f_list):
        
        ins_smb.set_frequency(cur_f)
        qt.msleep(0.01)
        
        total_cnts[i]+=ins_adwin.measure_counts(int_time)[channel]
        # qt.msleep(0.01)

    p_c = qt.Plot2D(f_list, total_cnts, 'bO-', name='ESR', clear=True)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
    print cur_rep
ins_smb.set_status('off')

d = qt.Data(name='ESR')
d.add_coordinate('frequence [GHz]')
d.add_value('counts')
d.create_file()


d.add_data_point(f_list, total_cnts)
pqm.savez(name,freq=f_list,counts=total_cnts)
d.close_file()
p_c = qt.Plot2D(d, 'bO-', coorddim=0, valdim=1, name='ESR', clear=True)

qt.mend()
