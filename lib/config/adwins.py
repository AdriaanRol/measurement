config = {}
config['adwin_lt1_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 8,
        'green_aom': 4,
        'gate' : 5, #not yet connected
        'velocity1_aom' : 6,
        'velocity2_aom' : 7,
        'yellow_aom' : 3, 
        }

config['adwin_lt1_dios'] = {
        'awg_event' : 6,
        'awg_trigger' : 0,
        'awg_ch3m2' : 9,
        'lt1_zpl_wp' : 4,
        }

config['adwin_lt1_processes'] = {
        
        'init_data' :  {
            'index' : 5, 
            'file' : 'init_data.TB5',
            },


        'linescan' : {
            
            'index' : 2, 
            'file' : 'lt1_linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4, 
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },
        
        'counter' : {

            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1, 
            'file' : 'lt1_simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'resonant_counting' : {

             'doc' : '',
             'index' : 1,
             'file' : 'lt1_resonant_counting.TB1',
             'par' : {
                 'set_aom_dac' : 63,
                 'set_aom_duration' : 73,
                 'set_probe_duration' : 74,
                 },
             'fpar' : {
                 'set_aom_voltage' : 64,
                 'floating_average': 11, #floating average time (ms)
                 },
             'data_float' : {
                 'get_counts' : [41,42,43,44],
                 },
             },

        'set_dac' :  {
            'index' : 3, 
            'file' : 'lt1_set_dac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },
        
        'set_dio' :  {
            'index' : 4, 
            'file' : 'lt1_set_ttl_outputs.TB4',
            'par' : {
                'dio_no' : 61,
                'dio_val' : 62,
                },
            },

        'trigger_dio' : {
            'index' : 4,
            'file' : 'lt1_dio_trigger.tb4',
            'par' : {
                'dio_no' : 61,
                'startval' : 62, # where to start - 0 or 1
                'waittime' : 63, # length of the trigger pulse in units of 10 ns
            },
        },
        
        # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr.inc',
            'par' : {
                    'CR_preselect'   : 75,
                    'CR_probe'       : 68,
                    'CR_repump'      : 69,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts'  : 76, 
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'       , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },     
                },
# ADwin SSRO. This process can not run stand-alone and should be included in another adwin script/process
# For now all parameters are passed from the other ADwin script/process, this seems more flexible to me.
# Not sure if this function is then needed. - Machiel 30-12-'13'
        'ssro' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'SSRO.inc',
            'par' : {
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    },     
                },

        # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check_mod' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr.inc',
            'par' : {
                    'CR_preselect'              : 75,
                    'CR_probe'                  : 68,
                    'CR_repump'                 : 69,
                    'total_CR_counts'           : 70,
                    'noof_repumps'              : 71,
                    'noof_cr_checks'            : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts'             : 76,
                    'pos_mod_activate'          : 65,
                    'repump_mod_activate'       : 66,
                    'cr_mod_activate'           : 67,
                    'cur_pos_mod_dac'           : 64,
                    },
                    'fpar' : {
                    'repump_mod_err' : 78,
                    'cr_mod_err'     : 79,
                    'pos_mod_err'    : 64,

                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ['repump_mod_DAC_channel'      ,   7],
                    ['cr_mod_DAC_channel'          ,   8],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'           ,   0.8],
                    ['repump_off_voltage'       ,  0.07],
                    ['Ex_CR_voltage'            ,   0.8],
                    ['A_CR_voltage'             ,   0.8],
                    ['Ex_off_voltage'           ,   0.0],
                    ['A_off_voltage'            , -0.08],
                    ['repump_mod_control_offset',   0.0],
                    ['repump_mod_control_amp'   ,   0.0],
                    ['cr_mod_control_offset'    ,   0.0],
                    ['cr_mod_control_amp'       ,   0.0],
                    ['pos_mod_control_amp'      ,  0.03],
                    ['pos_mod_fb'               ,   0.1],
                    ['pos_mod_min_counts'       ,  300.]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                'data_float' : {
                    'atto_positions' : 16
                    }        
                },

        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt1.tb9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'par' : {
                    'completed_reps' : 73,
                    'ssro_counts' : 74,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ],
                'params_long_index'  : 20,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },                    
                },

        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['sweep_length'                ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    }, 
                },
                # one CR check followed by multiple times SP-AWG seg-SSRO
        'ssro_multiple_RO' : {
                'index' : 9,
                'file' : 'integrated_ssro_multiple_RO_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['sweep_length'                ,   1], 
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'process_time' : 80,
                    },
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    }, 
                },

        'MBI' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'MBI_lt1.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'MBI start': 78,
                    'ROseq_cntr': 80,

                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },        

        'teleportation' : {

                'info' : """
                    Teleportation master control. LT1 is local, LT2 is remote.
                    """,
                'index' : 9,
                'file' : 'lt1_teleportation_control.TB9',
                'params_long' : [           #Keep order!!!
                    ['counter_channel'              ,       1],
                    ['repump_laser_DAC_channel'     ,       3],
                    ['E_laser_DAC_channel'          ,       6],
                    ['A_laser_DAC_channel'          ,       7],
                    ['CR_duration'                  ,      50],
                    ['CR_threshold_preselect'       ,      30],
                    ['CR_threshold_probe'           ,      10],
                    ['repump_duration'              ,     100],
                    ['E_SP_duration'                ,      50],
                    ['SSRO_duration'                ,      20],
                    ['ADwin_lt2_trigger_do_channel' ,       2],
                    ['ADWin_lt2_di_channel'         ,       1],
                    ['AWG_lt1_trigger_do_channel'   ,       1],
                    ['AWG_lt1_di_channel'           ,       3],
                    ['PLU_arm_do_channel'           ,      10],
                    ['PLU_di_channel'               ,       2],
                    ['MBI_duration'                 ,       4],
                    ['CR_repump'                    ,    1000],
                    ['AWG_lt1_event_do_channel'     ,       3],
                    ['AWG_lt2_RO1_bit_channel'      ,       1],
                    ['AWG_lt2_RO2_bit_channel'      ,       0],
                    ['AWG_lt2_do_DD_bit_channel'    ,       2],
                    ['AWG_lt2_strobe_channel'       ,       9],
                    ['A_SP_duration'                ,       5],
                    ['do_sequences'                 ,       1],
                    ['CR_probe_max_time'            , 1000000],
                    ['MBI_threshold'                ,       1],
                    ['max_MBI_attempts'             ,       1],
                    ['N_randomize_duration'         ,      50],
                    ['wait_before_send_BSM_done'    ,      30],
                    ],
                'params_long_index'    : 20,
                'params_long_length'   : 40,
                'params_float' : [          
                    ['repump_voltage'               ,   0.0],
                    ['repump_off_voltage'           ,     0],
                    ['E_CR_voltage'                 ,   0.0],
                    ['A_CR_voltage'                 ,   0.0],
                    ['E_SP_voltage'                 ,   0.0],
                    ['A_SP_voltage'                 ,   0.0],
                    ['E_RO_voltage'                 ,   0.0],
                    ['A_RO_voltage'                 ,   0.0],       
                    ['E_off_voltage'                ,   0.0],
                    ['A_off_voltage'                ,   0.0],
                    ['E_N_randomize_voltage',           0.0],
                    ['A_N_randomize_voltage',           0.0],
                    ['repump_N_randomize_voltage',      0.0], 
                    ],
                'params_float_index'    : 21,
                'params_float_length'   : 10,
                'par' : {
                    'CR_preselect'  : 75,
                    'CR_probe'      : 68,
                    'completed_reps' : 77,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts' : 76, 
                    'noof_starts' : 78,
                    'kill_by_CR' : 50,
                    },
                'data_long' : {
                    'CR_hist_time_out' : 7,
                    'CR_hist_all' : 8,
                    'repump_hist_time_out' : 9,
                    'repump_hist_all' : 10,
                    'CR_after' : 23,
                    'statistics' : 28,
                    'SSRO1_results' : 24,
                    'SSRO2_results' : 26,
                    # 'PLU_Bell_states' : 25, we took that out for now (oct 7, 2013)
                    'CR_before' : 27,
                    'CR_probe_timer': 29,
                    'CR_probe_timer_all': 30,
                    'CR_timer_lt2': 31,
                    },
                },        
        }

config['adwin_lt2_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'yellow_aom_frq' : 4,
        'yellow_aom' : 5,
        'matisse_aom' : 6,
        'green_aom': 7,
        'newfocus_aom' : 8,
        }

config['adwin_lt2_dios'] = {

        }

config['adwin_lt2_processes'] = {
        
        'linescan' : {
        
            'index' : 2, 
            'file' : 'lt2_linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                'set_phase_locking_on' : 19,
                'set_gate_good_phase' : 18,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },
        
        'counter' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1, 
            'file' : 'simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'resonant_counting' : {
            'doc' : '',
            'index' : 1,
            'file' : 'resonant_counting.TB1',
            'par' : {
                'set_aom_dac' : 26,
                'set_aom_duration' : 27,
                'set_probe_duration' : 28,
                'set_gate_dac': 12, 
                },
            'fpar' : {
                'set_aom_voltage' : 30,
                'floating_average': 11, #floating average time (ms)
                'gate_voltage' : 12,
                },
            'data_float' : {
                'get_counts' : [41,42,43,44],
                },
            },
        
        'set_dac' :  {
            'index' : 3, 
            'file' : 'SetDac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },
        
        'set_dio' :  {
            'index' : 4, 
            'file' : 'Set_TTL_Outputs_LTsetup2.TB4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },
         
        'init_data' :  {
            'index' : 5, 
            'file' : 'init_data.TB5',
            },

       # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr_pro.inc',
            'par' : {
                    'CR_preselect'  : 75,
                    'CR_probe'      : 68,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts' : 76, 
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'       , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },     
                },
# ADwin SSRO. This process can not run stand-alone and should be included in another adwin script/process
# For now all parameters are passed from the other ADwin script/process, this seems more flexible to me.
# Not sure if this function is then needed. - Machiel 30-12-'13'
        'ssro' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'ssro_pro.inc',
            'par' : {
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    },     
                },

        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt2.tb9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'par' : {
                    'completed_reps' : 73,
                    'ssro_counts' : 74,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ],
                'params_long_index'  : 20,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },                    
                },
        
                # ADwin single-shot readout with yellow freq aom scan
        
        # ADwin conditional segmented SSRO
        'segmented_ssro' : {
                'index' : 9,
                'file' : 'ssro_segmented_RO_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['repump_after_repetitions'    ,  1],
                    ['CR_repump'                   ,  0],
                    ['segmented_RO_duration'        , 20],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['repump_voltage' , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08],
                    ['segmented_Ex_RO_voltage',0.1]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_threshold' : 25,
                    'last_CR_counts' : 26,
                    },
				'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    #'RO_data' : 25,
                    'statistics' : 26,
                    'segment_number' : 27,
                    'full_RO_data' : 28,
                    'segmented_RO_data' : 29,
                    }, 
                },
             
        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['sweep_length'                ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    }, 
                },
                # one CR check followed by multiple times SP-AWG seg-SSRO
        'ssro_multiple_RO' : {
                'index' : 9,
                'file' : 'integrated_ssro_multiple_RO_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['sweep_length'                ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    }, 
                },

        'MBI' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'MBI_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,

                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },        
                     
        'general_pulses_sweep' : { 
                'index' : 9,
                'file' : 'general_pulses_sweep.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   4],
                    ['dac1_channel'                ,   7],
                    ['dac2_channel'                ,   6],
                    ['dac3_channel'                ,   8],
                    ['max_element'                 ,   4],
                    ['cycle_duration'              , 300],
                    ['wait_after_pulse_duration'   ,   1],
                    ['max_sweep'                   ,  10],
                    ['sweep_channel'               ,   7],
                    ['do_sweep_duration'           ,   0],
                    ['sweep_element'               ,  10],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 11,
                'par' : {
                    'repetition_counter'      : 73,
                    'total_counts'            : 15,
                    },
                'data_float': {
                    'dac1_voltages'             : 21,
                    'dac2_voltages'             : 22,
                    'dac3_voltages'             : 23,
                    'sweep_voltages'            : 26,
                    },
                'data_long': {
                    'counter_on'                : 24,
                    'element_durations'         : 25,
                    'results'                   : 30,
                    'histogram'                 : 31,
                    'counter'                   : 32,
                    'sweep_durations'           : 27,
                    },
                },
       
        'general_pulses_repeat' : { 
                'index' : 9,
                'file' : 'general_pulses_repeat.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   4],
                    ['dac1_channel'                ,   7],
                    ['dac2_channel'                ,   6],
                    ['dac3_channel'                ,   8],
                    ['max_element'                 ,   4],
                    ['cycle_duration'              , 300],
                    ['wait_after_pulse_duration'   ,   1],
                    ['max_repetitions'             ,10000],
                    ['timed_element'               ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 11,
                'par' : {
                    'repetition_counter'      : 72,
                    'total_counts'            : 70,
                    },
                'data_float': {
                    'dac1_voltages'             : 21,
                    'dac2_voltages'             : 22,
                    'dac3_voltages'             : 23,
                    },
                'data_long': {
                    'counter_on'                : 24,
                    'element_durations'         : 25,
                    'results'                   : 30,
                    'histogram'                 : 31,
                    'first_count'               : 32,
                    },
                },
             
        'MBI_Multiple_RO' : {  #with conditional repump, resonant, MBI
                'index' : 9,
                'file' : 'MBI_Multiple_RO_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,   1],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_E_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['RO_repetitions'              ,1000],
                    ['RO_duration'                 ,  50],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['wait_for_MBI_pulse'          ,   4],
                    ['SP_A_duration'               , 300],
                    ['MBI_threshold'               , 0  ],
                    ['nr_of_RO_steps'              ,1],
                    ['do_incr_RO_steps'            ,0 ],
                    ['incr_RO_steps'               ,1],
                    ['wait_after_RO_pulse_duration',3 ],
                    ['final_RO_duration'           ,50]
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['green_repump_voltage' , 0.8],
                    ['green_off_voltage'    , 0.0],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_final_RO_voltage'  , 0.8],
                    ['A_final_RO_voltage'   , 0]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'set_phase_locking_on'      : 19,
                    'set_gate_good_phase'       : 18,}
                },
       
        'MBI_feedback' : {  #with conditional repump, resonant, MBI,and addaptive feedback
                'index' : 9,
                'file' : 'MBI_Feedback_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,   1],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_E_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['RO_repetitions'              ,1000],
                    ['RO_duration'                 ,  50],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['wait_for_MBI_pulse'          ,   4],
                    ['SP_A_duration'               , 300],
                    ['MBI_threshold'               , 0  ],
                    ['wait_after_RO_pulse_duration',3   ],
                    ['final_RO_duration'           , 48 ],
                    ['wait_before_final_SP'        , 1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 30,
                'params_float' : [
                    ['green_repump_voltage' , 0.8],
                    ['green_off_voltage'    , 0.0],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_final_RO_voltage'  , 0.8],
                    ['A_final_RO_voltage'   , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 15,
                'par' : {
                    'set_phase_locking_on'      : 19,
                    'set_gate_good_phase'       : 18,},
                
                'data_long' : {
                    'CR_before'                 : 22,
                    'SP'                        : 24,
                    'CR_after_SSRO'             : 23,
                    'PLU_state'                 : 24,
                    'statistics'                : 26,
                    'SN'                        : 30,
                    'FS'                        : 31,
                    'FF'                        : 32,
                    'FinalRO_SN'                : 35,
                    'FinalRO_FS'                : 36,
                    'FinalRO_FF'                : 37,
                    },
                },        
        #MBI + segmented RO (Can in the future be included with other adwin program - Machiel)
        
        'MBI_segmented_ssro' : {
                'index' : 9,
                'file' : 'ssro_MBI_segmented_RO_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['repump_after_repetitions'    ,  1],
                    ['CR_repump'                   ,  0],
                    ['AWG_event_jump_DO_channel'    ,6],
                    ['segmented_RO_duration'        , 20],
                    ['MBI_duration'                 ,9],
                    ['wait_for_MBI_pulse'           ,3],
                    ['MBI_threshold'                ,1 ],
                    ['sweep_length'                 ,1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 30,
                'params_float' : [
                    ['repump_voltage' , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08],
                    ['segmented_Ex_RO_voltage',0.1]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_threshold' : 25,
                    'last_CR_counts' : 26,
                    },
				'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    #'RO_data' : 25,
                    'statistics' : 26,
                    'segment_number' : 27,
                    'full_RO_data' : 28,
                    'segmented_RO_data' : 29,
                    }, 
                },

        'teleportation' : {
                'index' : 9,
                'file' : 'lt2_teleportation.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ey_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,  50],
                    ['CR_duration'                 ,  50],
                    ['CR_preselect'                ,  40],
                    ['teleportation_repetitions'   ,1000],
                    ['SSRO_lt2_duration'           ,  50],
                    ['CR_probe'                    ,  40],
                    ['CR_repump'                   ,1000],
                    ['Adwin_lt1_do_channel'        ,   8],
                    ['Adwin_lt1_di_channel'        ,  17],
                    ['AWG_lt2_di_channel'          ,  16],
                    ['freq_AOM_DAC_channel'        ,  4],
                    ['CR_probe_max_time'        , 1000000],
                    ],
                'params_long_index' : 20, 
                'params_long_length': 25,
                'params_float' : [
                    ['repump_voltage'              , 0.0],
                    ['repump_off_voltage'          , 0.0],
                    ['Ey_CR_voltage'               , 0.0],
                    ['A_CR_voltage'                , 0.0],
                    ['Ey_SP_voltage'               , 0.0],
                    ['A_SP_voltage'                , 0.0],
                    ['Ey_RO_voltage'               , 0.0],
                    ['A_RO_voltage'                , 0.0],
                    ['Ey_off_voltage'              , 0.0],
                    ['A_off_voltage'               , 0.0],
                    ['repump_freq_offset'          , 5.0],
                    ['repump_freq_amplitude'       , 4.0]  
                    ],
                'params_float_index' : 21,
                'params_float_length': 12,
                'par': {
                    'completed_reps' : 77,
                    'total_CR_counts': 70,
                    'get_noof_cr_checks' : 72,
                    'get_cr_below_threshold_events': 71,
                    'repump_counts': 76,
                    'noof_repumps': 66,
                    'kill_by_CR' : 50,
                    },
                'data_long' : {
                    'CR_before' : 22, 
                    'CR_after'  : 23,
                    'CR_hist'   : 24,
                    'repump_hist_time_out' : 9,
                    'repump_hist_all' : 10,
                    'SSRO_lt2_data' : 25,
                    'statistics'    : 26,
                    'CR_probe_timer' : 28,
                    'CR_hist_time_out' : 29,
                    },
                'data_float': {
                    'repump_freq_voltages'      : 19,
                    'repump_freq_counts'        : 27,
                    },
                },

        #gate modulation
        'check_trigger_from_lt1' : {
                'index' : 9,
                'file' : 'check_trigger_from_lt1.TB9',
                'par' : {},
                'fpar': {}
                },
        
        }

config['adwin_lt3_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'green_aom' : 4,
        'yellow_aom' : 5,
        'matisse_aom' : 6,
        'newfocus_aom': 7,
        'not_in_use' : 8,
        }

config['adwin_lt3_dios'] = {

        }

config['adwin_lt3_processes'] = {
        
        'linescan' : {
        
            'index' : 2, 
            'file' : 'linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                'set_phase_locking_on' : 19,
                'set_gate_good_phase' : 18,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },
        
        'counter' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1, 
            'file' : 'simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'set_dac' :  {
            'index' : 3, 
            'file' : 'SetDac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },
        
        'set_dio' :  {
            'index' : 4, 
            'file' : 'Set_TTL_Outputs.TB4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },
         
        'init_data' :  {
            'index' : 5, 
            'file' : 'init_data.TB5',
            },
        
 # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr.inc',
            'par' : {
                    'CR_preselect'  : 75,
                    'CR_probe'      : 68,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts' : 76, 
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'       , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },     
                },
        # ADwin SSRO. This process can not run stand-alone and should be included in another adwin script/process
        # For now all parameters are passed from the other ADwin script/process, this seems more flexible to me.
        # Not sure if this function is then needed. - Machiel 30-12-'13'
        'ssro' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'ssro_pro.inc',
            'par' : {
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    },     
                },

        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt3.tb9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'par' : {
                    'completed_reps' : 73,
                    'ssro_counts' : 74,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ],
                'params_long_index'  : 20,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },                    
                },

        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt3.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['sweep_length'                ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    }, 
                },
        


        }