import time

ADwin.Stop_Process(4)

ADwin.Load('D:\\Lucio\\ADwin codes\\ADwin_Gold_II\\simple_counting.tb4')
ADwin.Set_Par(24,100)     # counter
time.sleep(1)

ADwin.Start_Process(4)

