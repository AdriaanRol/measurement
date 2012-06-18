AWG.stop()
AWG.set_runmode('CONT')

physical_adwin.Stop_Process(9)
adwin.set_simple_counting()
counters.set_is_running(True)

NewfocusAOM.set_power(0)
MatisseAOM.set_power(0)
GreenAOM.set_power(300e-6)

cnts_green = counters.get_cntr1_countrate()
cnts_green_thres = 290e5

qt.msleep(0.2)

if cnts_green < cnts_green_thres:
    print 'Counts below threshold'

    
