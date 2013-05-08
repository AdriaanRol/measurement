physical_adwin.Stop_Process(9)
adwin.set_resonant_counting(red_powers = [200e-9,50e-9])
counters.set_is_running(True)

#NewfocusAOM.set_power(0)
#MatisseAOM.set_power(0)
#GreenAOM.set_power(200e-6)

AWG.stop()
AWG.set_runmode('CONT')

#cnts_green = counters.get_cntr1_countrate()
#cnts_green_thres = 300e5

#qt.msleep(0.2)

#if cnts_green < cnts_green_thres:
#    print 'Counts below threshold'

   
