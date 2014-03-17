"""
Experiment settings (voltages and the like), individual for different samples.

Units: 
    - In general, SI (Hz, Watts, ...)
    - powers for the AOM: microwatts
    - durations that are used by the AWG: ns (samples, actually),
      MUST BE INTEGERS!!!
"""

import numpy as np

hardware = {
        'MW_pulse_mod_risetime' : 20,
        'counter_channel':      1,
        'green_off_voltage':    0.08
        }

sil9 = {
        'MW_source_power':  20,
        'MW_source_freq': 2.79E9,
        'MW_freq_center':  2.82888E9,#2.8286995E9,#2.828952E9,#2.82907E9,#2.828854E9,#2.829283E9,
        'hf_splitting': 2.185E6,
        'mI_p1_freq':   2.766E6,
        'mI_m1_freq':   7.136E6,

        }


pulses ={
        'shelving_len':         80.,
        'shelving_amp':         0.78,
        'RF_pi_len':            32986,
        'RF_pi2_len':           18586.,
        'RF_pi_len_mI+1':       47500,
        'RF_pi2_len_mI+1':      23000,
        'RF_pi_amp':            .8,
        'RF_pi2_amp':            .8,
        'pi2pi_len' :           397.,
        'pi2pi_amp':            0.16,
        'pi2_len' :           35.,
        'pi2_amp':            0.91,
        'time_between_CORPSE':  1.,
        'CORPSE_nsel_amp':           0.675,
        'CORPSE_nsel_frabi':    5.6179e-3,
        'CORPSE_cal': {'a':.5,'A':.5,'f':7.545e-3,'phi':0,
            },
                        
        'sel_amp':              0.0625,
        'sel_frabi':            619e-6,
        'tau_strong_meas':      220,
        }
ssroprotocol = {
        'green_repump_duration':        10,
        'yellow_repump_duration':       1000,
        'CR_duration':                  200, #NOTE 60 for A1 readout
        'SP_E_duration':                100,    # ADwin time (us) 
        'SP_A_duration':                100,    # ADwin time (us) 
        'SP_filter_duration':           0,
        'sequence_wait_time':           1,
        'wait_after_pulse_duration':    3,
        'CR_preselect':                 20,
        'RO_duration':                  60,     # ADwin time (us) 
        'green_repump_amplitude':       100e-6,
        'yellow_repump_amplitude':      150e-9,
        'green_off_amplitude':          0e-6,
        'Ex_CR_amplitude':              30e-9, #OK
        'A_CR_amplitude':               40e-9,#NOTE 15 for A1 readout
        'Ex_SP_amplitude':              30e-9,
        'A_SP_amplitude':               80e-9, #OK: PREPARE IN MS = 0
        'Ex_RO_amplitude':              10e-9, #OK: READOUT MS = 0
        'A_RO_amplitude':               0e-9,
        'CR_probe':                     20,
        'repump_after_repetitions':     1,
        }

MBIprotocol={
        'wait_time_before_MBI_pulse':   3000,   # AWG time (ns)
        'wait_time_before_shelv_pulse': 3000,   # AWG time (ns)    
        'MBI_pulse_len':                2750,#2750,   # AWG time (ns) 
        'MBI_pulse_amp':                0.0184,#.0191,
        'MBI_RO_duration':              9,       # ADwin time (us) 
        'weak_RO_duration':             2,
        'wait_for_MBI_pulse':           6,       # AWG time (us)
        'AWG_start_DO_channel':         1,
        'AWG_done_DI_channel':          8,
        'AWG_event_jump_DO_channel':    6,
        'send_AWG_start':               1,
        'wait_for_AWG_done':            0,
        'cycle_duration':               300,
        'do_incr_RO_steps':             0,
        'incr_RO_steps':                1,
        'saveme' : True,
        }


current_sample = sil9
lt1 = False
