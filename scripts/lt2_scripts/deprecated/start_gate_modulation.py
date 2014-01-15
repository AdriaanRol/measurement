def start_gate_mod():
    Vpp = 5
    physical_adwin.Set_Par(12,adwin_lt2.get_dac_channels()['gate'])
    adwin_lt2.set_gate_modulation_var(gate_voltage = Vpp/2.)
    adwin_lt2.start_gate_modulation(load = True,
            modulation_on = 1)

start_gate_mod()
