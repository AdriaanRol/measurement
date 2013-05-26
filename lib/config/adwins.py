config = {}

config['adwin_lt2_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'gate' : 4,
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
                'dio_no' : 61,
                'dio_val' : 62,
                },
            },
         
        'init_data' :  {
            'index' : 5, 
            'file' : 'init_data.TB5',
            },
         
        # FIXME what does that do? still needed? name!?
        'DIO_test' :  {
            'index' : 6, 
            'file' : 'universalDI.TB6',
            'par' : {
                'output' : 65,
                'edge' : 66,
                },
            },

        # FIXME what does that do? still needed? name!?
        'universal_dac' : {
                'index' : 6,
                'file' : 'universalDAC.tb6', 
                },
        
        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
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
                    ['repump_after_repetitions'    ,  1]
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
                    ['A_off_voltage'        , -0.08]
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
                    'RO_data' : 25,
                    'statistics' : 26,
                    }, 
                },
                
        # ADwin single-shot readout
        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_duration'                 , 100],
                    ['sweep_length'                ,   1],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['repump_after_repetitions'    ,  1]
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['green_repump_voltage' , 0.8],
                    ['green_off_voltage'    , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_events_below_threshold' : 71,
                    'CR_events' : 72,                    
                    'CR_threshold' : 25,
                    'last_CR_counts' : 26,
                    },
				'data_long' : {
                    # 'CR_before' : 22,  # not used in the integrated ssro
                    # 'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'statistics' : 26,
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

        #gate modulation
        'check_trigger_from_lt1' : {
                'index' : 9,
                'file' : 'check_trigger_from_lt1.TB9',
                'par' : {},
                'fpar': {}
                },
        
        }

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
        }

config['adwin_lt1_processes'] = {
        
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

        'alternating_resonant_counting' : {
            'doc' : '',
            'index' : 1,
            'file' : 'lt1_alternating_resonant_counting.tb1',
            'par' : {
                'set_repump_aom_dac' : 30,
                'set_pump_aom_dac' : 31,
                'set_probe_aom_dac' : 32,
                'set_repump_duration' : 33,
                'set_pump_duration' : 34,
                'set_probe_duration' : 35,
                'set_pp_cycles' : 36,
                'set_floating_average' : 11,
                'set_single_shot' : 37,
                'set_prepump' : 38,
                'set_prepump_duration' : 39,
                },
            'fpar' : {
                'set_repump_aom_voltage' : 30,
                'set_pump_aom_voltage' : 31,
                'set_probe_aom_voltage' : 32,
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

        'gate_modulation' : {
            'index' : 7,
            'file' : 'gate_modulation.TB7',
            'par' : {
                'gate_dac' : 12,
                'modulation_period' : 13,
                'modulation_on' : 14,
                },
            'fpar': {
                'gate_voltage' : 12,
                },
            },
        
        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt1.tb9',
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_threshold' : 25,
                    'last_CR_counts' : 26,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
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
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'statistics' : 26,
                    },                    
                },

        'singleshot_altern_CR' : {
                'index' : 9,
                'file' : 'singleshot_lt1_altern_cr.tb9', 
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_threshold' : 25,
                    'last_CR_counts' : 26,
                    },
                'fpar' : {
                    'gate_voltage' : 26,
                    },
                'params_long' : [
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_pump_duration'            ,  50],
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
                    ['CR_probe_duration'           ,  50],
                    ['CR_pp_cycles'                ,   5],
                    ['CR_prepump_duration'         , 100],
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
                    ['yellow_repump_voltage', 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'statistics' : 26,
                    },
                },
        
        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt1.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_duration'                 , 100],
                    ['sweep_length'                ,   1],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['repump_after_repetitions'    ,   1],
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
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , 0.0]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_events_below_threshold' : 71,
                    'CR_events' : 72,                    
                    # 'CR_threshold' : 75,
                    # 'last_CR_counts' : 26,
                    },
				'data_long' : {
                    # 'CR_before' : 22,  # not used in the integrated ssro
                    # 'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'statistics' : 26,
                    }, 
                },

        'MBI' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'lt1_MBI.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['MBI_steps'                   ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 30,
                'params_float' : [
                    ['green_repump_voltage' , 0.8],
                    ['green_off_voltage'    , 0.0],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['Ex_MBI_voltage'       , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 6,
                'par' : {
                    'CR_preselect' : 75,
                    'CR_probe' : 68,
                    'completed_reps' : 73,

                    },
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'statistics' : 26,
                    'ssro_results' : 27,
                    },
                },
        }
