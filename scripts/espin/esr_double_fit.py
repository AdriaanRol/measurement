import qt
import msvcrt
from analysis.lib.fitting import fit as fit
from analysis.lib.fitting import fit,esr
from numpy import array

name_gen='ESR_SIL1_Hans_LT2'
steps   = 71  #101
mw_power = -3    #in dBm
green_power = 50e-6  #10e-6
int_time = 50 #30        # in ms
reps = 30
center_f_list =  [3.727] # in GHz #Ms = -1 #Ms = +1
range_f  =  0.050 # in GHz

f0 = [0,0]
u_f0 = [0,0]
#generate list of frequencies
for ii in range(size(center_f_list)): # so that it runs twice
    center_f = center_f_list[ii]

    f_list = linspace((center_f-range_f)*1e9, (center_f+range_f)*1e9, steps)

    name = name_gen + '_' + str(ii)

    ins_smb = qt.instruments['SMB100']
    ins_adwin = qt.instruments['adwin']
    ins_counters = qt.instruments['counters']
    ins_aom = qt.instruments['GreenAOM']

    counter = 1
    MW_power = mw_power
    ins_counters.set_is_running(0)

    # create data object
    qt.mstart()

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
    d.add_value('Counts fitted')

    d.create_file()
    filename=d.get_filepath()[:-4]



    # now try to fit it

    x = f_list*1e-6
    y = total_cnts
    guess_width = 6 #0.2e-3
    guess_amplitude = 1/2.0*(total_cnts[1]+total_cnts[-1])

    
    total_cts_list = array(total_cnts)
    val, idx = min((val, idx) for (idx, val) in enumerate(total_cts_list))
    
    guess_ctr = f_list[idx]*1e-6

    print guess_ctr

    x_axis = x*1e6

    fit_result = fit.fit1d(x, y, esr.fit_ESR_gauss, center_f,
        guess_amplitude, guess_width, guess_ctr,
    #     # (2, guess_splitN), 
    #     # (2, guess_splitC),
    #     # (2, guess_splitB),
    #     #(3, guess_splitN), 
        do_print=False, ret=True, do_plot = True, fixed=[4])

    fd = zeros(len(x_axis))  

    if type(fit_result) != type(False):
        fd = fit_result['fitfunc'](x_axis*1e-6)
    else:
        print 'could not fit curve!'

    d.add_data_point(f_list, total_cnts,fd)
    p_c = qt.Plot2D(d, 'bO-', coorddim=0, name=name, valdim=1, clear=True)
    p_c.add_data(d, coorddim=0, valdim=2)
    qt.msleep(0.15)
    p_c.save_png(filename+'.png')
    d.close_file()

    qt.mend()

    ins_counters.set_is_running(1)
    GreenAOM.set_power(2e-6)

    print fit_result['params_dict']['x0']

    f0[ii] = fit_result['params_dict']['x0']
    u_f0[ii] = fit_result['error_dict']['x0']
    
    if ii == 1:
        print 'Calculated center frequency for ms = -1 is: ' + str(round(f0[0]*1e-3,5)) +'+/-'+ str(round(u_f0[0]*1e-3,2)) + ' GHz'

        expected_Dgs = (f0[0]+f0[1])/2
        error_Dgs = (u_f0[0]+u_f0[1])/2

        B_field = (expected_Dgs-f0[0])/2.8

        print 'Calculated center frequency for ms = +1 is: ' +str(round(f0[1]*1e-3,5)) +'+/-' +str(round(u_f0[1]*1e-3,2))+ ' GHz'

        print 'Calculated ground state splitting is: ' + str(round(expected_Dgs*1e-3,5)) +'+/-'+ str(round(error_Dgs,2))+ ' MHz'
        print 'Calculated magnetic field is: ' + str(round(B_field,1)) + ' G'