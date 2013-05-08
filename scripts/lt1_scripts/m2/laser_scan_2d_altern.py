import numpy as np
import qt

import laser_scan_v2 as ls2
reload(ls2)

### set stuff

# basics
name = '2D_altern_'

# HW settings
outer_aom = Velocity2AOM
inner_aom = Velocity1AOM
inner_aom_name = 'Velocity1AOM'
outer_aom_pid = pidvelocity2
inner_dac_channel = 0 # must be equal to inner_aom

# msmt settings
outer_frqs = np.linspace(60, 60.4, 41)
inner_start_v = -0.1
inner_stop_v = -0.3
inner_pts = 201

pump_power = 5e-9
probe_power = 5e-9
pp_cycles = 5
probe_duration = 10 # 10us units
pump_duration = 10

stabilize_duration = 2 # seconds

#### msmt
for frq in outer_frqs:
    outer_aom_pid.set_setpoint(frq)
    qt.msleep(stabilize_duration)

    _name = name + 'pwr=%d+%d_t=%d+%d_cycles=%d_f=%.2f' \
            % (pump_power*1e9, probe_power*1e9, pump_duration*10, \
            probe_duration*10, pp_cycles, frq)

    m = ls2.LabjackAlternResonantCountingScan(
                _name, inner_dac_channel, inner_aom_name)

    m.pump_power = pump_power
    m.probe_power = probe_power
    m.pump_duration = pump_duration
    m.probe_duration = probe_duration
    m.pp_cycles = pp_cycles
    
    m.frq_offset = 470400
    m.frq_factor = 1.
    m.use_mw = False
    m.repump_power = 50e-6
    m.repump_duration = 1
    m.laser_power = 0.
    m.counter_channel = 0
    m.wm_channel = 1
    m.use_repump_during = False
    m.repump_power_during = 0.

    m.start_voltage = inner_start_v
    m.stop_voltage = inner_stop_v
    m.pts = inner_pts
    m.integration_time = 1000

    m.plot_strain_lines = False

    m.prepare_scan()
    m.run_scan()
    m.finish_scan()
