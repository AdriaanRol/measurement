wm_channel_lt1_nf1 = 6
_setfrq = lambda x: labjack.set_bipolar_dac7(x)
_getfrq = lambda: labjack.get_bipolar_dac7()
_setfrq_coarse = lambda x: labjack.set_bipolar_dac6(x)
_getfrq_coarse = lambda: labjack.get_bipolar_dac6()
_getval = lambda: wavemeter.Get_Frequency(wm_channel_lt1_nf1)
pid_lt1_newfocus1 = qt.instruments.create('pid_lt1_newfocus1', 'pid_controller_v4', 
        set_ctrl_func=_setfrq, get_ctrl_func=_getfrq,
        set_ctrl_func_coarse=_setfrq_coarse, get_ctrl_func_coarse=_getfrq_coarse,
        get_val_func=_getval, get_stabilizor_func=get_frq_hene)