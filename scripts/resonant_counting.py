import time

ADwin.Stop_Process(4)

TheSetup.set_AOMonADwin(True)

ADwin.Load('D:\\Lucio\\ADwin codes\\ADwin_Gold_II\\resonant_counting.tb4')
ADwin.Set_Par(63,4)     # green AOM DAC
ADwin.Set_Par(73,1)     # * 10microseconds AOM pulse duration
ADwin.Set_FPar(64,7)    # green AOM pulse voltage
ADwin.Set_Par(74,10)    # * 10microseconds counting duration

time.sleep(1)

ADwin.Start_Process(4)
AWG.set_ch2_offset(1)
AWG.set_ch1_marker2_low(1)
