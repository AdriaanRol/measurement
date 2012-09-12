def all_red_on():
    NewfocusAOM.set_cur_controller('ADWIN')
    NewfocusAOM_lt1.set_cur_controller('ADWIN')
    NewfocusAOM.apply_voltage(NewfocusAOM.get_V_min())
    MatisseAOM.apply_voltage(MatisseAOM.get_V_max())
    NewfocusAOM_lt1.apply_voltage(NewfocusAOM_lt1.get_V_min())
    MatisseAOM_lt1.apply_voltage(MatisseAOM_lt1.get_V_max())
