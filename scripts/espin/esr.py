import qt
import msvcrt

##############
### Inputs ###
##############

name='ESR_SIL1_Hans_LT2'
steps    = 501        #101
mw_power = -3        #in dBm
green_power = 10e-6  #10e-6
int_time = 25        # in ms
reps = 10
#center_f =  2.088 # in GHz #Ms = -1
center_f =  1.25# in GHz #Ms = +1
range_f  =  0.25 # in GHz

#generate list of frequencies
f_list = linspace((center_f-range_f)*1e9, (center_f+range_f)*1e9, steps)

# Set source to use
ins_smb = qt.instruments['SMB100']
IQ_modulation = True #Does this source have IQ modulation?

# Set other instruments
ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

###############
### Run ESR ###
###############

counter = 1
MW_power = mw_power
ins_counters.set_is_running(0)

# create data object
qt.mstart()

if IQ_modulation:
    ins_smb.set_iq('off')

ins_smb.set_pulm('off')
ins_smb.set_power(MW_power)
ins_smb.set_status('on')

qt.msleep(0.2)
#ins_counters.set_is_running(0)
total_cnts = zeros(steps)
ins_aom.set_power(green_power)
stop_scan=False
for cur_rep in range(reps):

    print 'sweep %d/%d ...' % (cur_rep+1, reps)

    for i,cur_f in enumerate(f_list):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        ins_smb.set_frequency(cur_f)
        qt.msleep(0.1)

        total_cnts[i]+=ins_adwin.measure_counts(int_time)[counter-1]
        # qt.msleep(0.01)

    p_c = qt.Plot2D(f_list, total_cnts, 'bO-', name=name, clear=True)
    if stop_scan: break


ins_smb.set_status('off')

d = qt.Data(name=name)
d.add_coordinate('frequency [GHz]')
d.add_value('counts')
d.create_file()
filename=d.get_filepath()[:-4]

d.add_data_point(f_list, total_cnts)
d.close_file()
p_c = qt.Plot2D(d, 'bO-', coorddim=0, name=name, valdim=1, clear=True)
p_c.save_png(filename+'.png')

qt.mend()

ins_counters.set_is_running(1)
GreenAOM.set_power(30e-6)
