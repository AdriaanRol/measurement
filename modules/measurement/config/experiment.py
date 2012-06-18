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
        }

sil9 = {
        'Ex_opt_spinpumping_power' : 1e-3,
        'A_ttl_power' : 3.5e-3,
        'Ex_opt_CR_power' : 3e-3,
        'Ex_opt_RO_power' : 1e-3,
        '1253MHz_voltage' : 1.13,
        'selective_pi_duration' : 2000,
        'selective_pi_voltage' : 0.2,
        'hard_pi_voltage' : 1.13,
        'hard_pi_duration' : 400,
        'MBI_duration' : 300,
        'MBI_repump_duration' : 4000,
        'MBI_Ex_power' : 1e-3,
        'MBI_threshold' : 1,
        'Ex_opt_RO_duration' : 10000,
        'CR_threshold' : 30,

        'esr_n_splitting' : 2.18e6,
        'esr_c13_splitting' : 12.77e6,
        'N_quadrupole_splitting': 4.946e6,
        'esr_b_splitting' : 28.879e6,
        'esr_f0' : 37.531e6,

        'nmr_n_01_splitting' : 2.7623e6,
        'nmr_c13_splitting' : 12.77e6,

        'MW_base_power' : -10,
        'MW_base_frequency': 2.840e9,

        }


sil3_esr_f0 = 37.51e6
sil3_bsplit = 29.57e6
sil3_hfc13 = 12.796e6
sil3_hfn = 2.184e6
sil3_qn = 4.946e6

sil3 = {
        'Ex_opt_spinpumping_power' : 1e-3,
        'A_ttl_power' : 3e-3,
        'Ex_opt_CR_power' : 3e-3,
        'Ex_opt_RO_power' : 1e-3,
        '1253MHz_voltage' : 0.377,
        'selective_pi_duration' : 2400,
        'selective_pi_voltage' : 0.05,
        'hard_pi_voltage' : 0.9,
        'hard_pi_duration' : 170,
        'MBI_duration' : 300,
        'MBI_repump_duration' : 6000,
        'MBI_Ex_power' : 1e-3,
        'MBI_threshold' : 1,
        'Ex_opt_RO_duration' : 10000,
        'CR_threshold' : 30,

        'esr_n_splitting' : sil3_hfn,
        'esr_c13_splitting' : sil3_hfc13,
        'N_quadrupole_splitting': sil3_qn,
        'esr_b_splitting' : sil3_bsplit,
        'esr_f0' : sil3_esr_f0,

        'nmr_n_01_splitting' : sil3_qn - sil3_hfn,
        'nmr_c13_splitting' : sil3_hfc13,

        
        'n_pipulse' : {
            1. : 75500, },
        'c13_pipulse' : {
            1. : 19102, },

        'MW_base_power' : -10,
        'MW_base_frequency': 2.840e9,

        'states' : ['0,+1/2', '+1,+1/2', '0,-1/2', '+1,-1/2'],

        
        'basis_min1_esr_frqs' : [
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2 + sil3_hfn,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2 + sil3_hfn ],
        'basis_plus1_esr_frqs' : [
            sil3_esr_f0 + sil3_bsplit/2 + sil3_hfc13/2,
            sil3_esr_f0 + sil3_bsplit/2 + sil3_hfc13/2 - sil3_hfn,
            sil3_esr_f0 + sil3_bsplit/2 - sil3_hfc13/2,
            sil3_esr_f0 + sil3_bsplit/2 - sil3_hfc13/2 - sil3_hfn ],
        
        'state_esr_frqs' : [
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2 + sil3_hfn,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2 + sil3_hfn ],
        'probe_esr_frqs' : [
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2 + sil3_hfn,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2 + sil3_hfn,
            sil3_esr_f0 + sil3_bsplit/2 + sil3_hfc13/2,
            sil3_esr_f0 + sil3_bsplit/2 + sil3_hfc13/2 - sil3_hfn,
            sil3_esr_f0 + sil3_bsplit/2 - sil3_hfc13/2,
            sil3_esr_f0 + sil3_bsplit/2 - sil3_hfc13/2 - sil3_hfn ],
        'all_esr_frqs' : [
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2 - sil3_hfn,
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 - sil3_hfc13/2 + sil3_hfn,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2 - sil3_hfn,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2,
            sil3_esr_f0 - sil3_bsplit/2 + sil3_hfc13/2 + sil3_hfn,
            sil3_esr_f0 + sil3_bsplit/2 - sil3_hfc13/2 - sil3_hfn,
            sil3_esr_f0 + sil3_bsplit/2 - sil3_hfc13/2,
            sil3_esr_f0 + sil3_bsplit/2 - sil3_hfc13/2 + sil3_hfn,
            sil3_esr_f0 + sil3_bsplit/2 + sil3_hfc13/2 - sil3_hfn,
            sil3_esr_f0 + sil3_bsplit/2 + sil3_hfc13/2,
            sil3_esr_f0 + sil3_bsplit/2 + sil3_hfc13/2 + sil3_hfn ],

        'state_pi-twopi-amplitudes' : [0.382, 0.381, 0.399, 0.404, 0.421, 0.421, 0.422, 0.424],
        'state_hardpi_durations' : [168, 168, 173, 180],
        'all_esr_pi-twopi-amplitudes' : [0.377, 0.377, 0.377, 0.392, 0.395, 0.398, 0.411, 0.411, 0.411, 0.411, 0.411, 0.411],

        }

sil2 = {
        'Ex_opt_spinpumping_power' : 3e-3,
        'A_ttl_power' : 3e-3,
        'Ex_opt_CR_power' : 3e-3,
        'Ex_opt_RO_power' : 0.5e-3,
        '1253MHz_voltage' : 0.848,
        'selective_pi_duration' : 2400,
        'selective_pi_voltage' : 0.1,
        'hard_pi_voltage' : 0.848,
        'hard_pi_duration' : 400,
        'MBI_duration' : 300,
        'MBI_repump_duration' : 6000,
        'MBI_Ex_power' : 3e-3,
        'MBI_threshold' : 1,
        'Ex_opt_RO_duration' : 10000,
        'CR_threshold' : 30,

        'esr_n_splitting' : 2.171e6,
        'N_quadrupole_splitting': 4.946e6,
        'esr_b_splitting' : 29.43e6,
        'esr_f0' : 27.31e6,

        'nmr_n_01_splitting' : 2.7624e6,

        'MW_base_power' : -10,
        'MW_base_frequency': 2.850e9,

        'states' : ['-1,-1', '-1,0', '-1,+1', '+1,-1', '+1,0', '+1,+1'],

        'state_esr_frqs' : [
            27.31e6 - 29.43e6/2 - 2.171e6,
            27.31e6 - 29.43e6/2,
            27.31e6 - 29.43e6/2 + 2.171e6,
            27.31e6 + 29.43e6/2 + 2.171e6,
            27.31e6 + 29.43e6/2,
            27.31e6 + 29.43e6/2 - 2.171e6],


        'state_pi-twopi-amplitudes' : [0.845, 0.848, 0.851, 0.939, 
            0.936, 0.933],
        'state_hardpi_durations' : [400, 400, 400, 400, 400, 400],

        'state_best-pi-amplitudes' : [0.794, 0.797, 0.800, 0.883, 
            0.880, 0.877],
        'state_best-pi-durations' : [421, 421, 421, 421, 421, 421],
        
        }


ssroprotocol = {
        'CR_duration' : 100000,
        'ADwin_CR_threshold' : 30,
        'ADwin_probe_duration' : 5,
        'ADwin_probe_threshold' : 20,
        'ADwin_AOM_duration' : 2,
        'spinpumping_duration' : 200000,
        'spinpumping_filter_duration' : 50000,
        }


current_sample = sil3
