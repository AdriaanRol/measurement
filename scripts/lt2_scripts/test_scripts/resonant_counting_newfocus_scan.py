import qt
import data
from measurement.measurement import Measurement
import measurement.PQ_measurement_generator_v2 as pqm
import msvcrt

name = "nfscan_SIL2_LT1"
pidnewfocus_yeah = qt.instruments['pidnewfocus_lt1']
#ins_adwin = qt.instruments['adwin_lt1']

counter=2
int_time=100

#qt.mstart()
#ins_adwin.set_resonant_counting()

def newf_scan(start,stop,steps):
    freq = linspace(start,stop,steps)
    total_cnts = []
    for f in freq:
        pidnewfocus_yeah.set_setpoint(f)
        qt.msleep(0.5)
        #total_cnts.append(ins_adwin.measure_counts(int_time)[counter-1])
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break

    #d = qt.Data(name=name)
    #d.add_coordinate('frequency [GHz]')
    #d.add_value('counts')
    #d.create_file()

    #filename=d.get_filepath()[:-4]

    #d.add_data_point(freq, total_cnts)
    #pqm.savez(filename,freq=freq,counts=total_cnts)
    #d.close_file()
    #p_c = qt.Plot2D(d, 'bO-', coorddim=0, name=name, valdim=1, clear=True)
    #p_c.save_png(filename+'.png')


    #qt.mend()
