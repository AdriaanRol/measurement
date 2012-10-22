physical_adwin.Stop_Process(9)
adwin.set_simple_counting()
counters.set_is_running(True)

NewfocusAOM.set_power(0)
MatisseAOM.set_power(0)
GreenAOM.set_power(200e-6)

AWG.stop()
AWG.set_runmode('CONT')

cnts_green = counters.get_cntr1_countrate()
cnts_green_thres = 300e5

qt.msleep(0.2)

if cnts_green < cnts_green_thres:
    print 'Counts below threshold'
else
    iter = 0
    n_reps = 20
    GreenAOM.set_power(0)
    newfocus_cur_value = pidnewfocus.get_setpoint()
    setpoint_values = range(newfocus_cur_value-0.2,newfocus_cur_value+0.2,0.02)
    resonant_counts = zeros([1,setpoint_values.size])

    counts = 0

    for value in setpoint_values:
        for k in range(0,n_reps)
            counts_old = counters.get_cntr1_countrate() 
            counts = counts + counts_old
            qt.msleep(0.1)
        resonant_counts[0,iter] = counts/n_reps
        iter = iter+1
        qt.msleep(2)
    setpoint_maxrescounts = setpoint_values[resonant_counts == max(resonant_counts)]
    

    
