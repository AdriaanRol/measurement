
if False:
    _setctrl_gate = lambda x: qt.instruments['ivvi_lt1'].set_dac4(x)
    _getval_gate = lambda: qt.instruments['physical_adwin_lt1'].Get_FPar(77)
    _getctrl_gate=  lambda: qt.instruments['ivvi_lt1'].get_dac4()
    pidgate = qt.instruments.create('pidgate', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_gate , get_val_func=_getval_gate , get_ctrl_func=_getctrl_gate, 
            ctrl_minval=900.0, ctrl_maxval=1200.0)

if True:
    _setctrl_yellow_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
    _getval_yellow_freq = lambda: qt.instruments['physical_adwin_lt1'].Get_FPar(78)
    _getctrl_yellow_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    pidgate = qt.instruments.create('pidyellowfrq', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_yellow_freq , get_val_func=_getval_yellow_freq , get_ctrl_func=_getctrl_yellow_freq, 
            ctrl_minval=20., ctrl_maxval=30.)