config = {}

config['adwin_lt2_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'gate' : 4,
        'newfocus_frq' : 5,
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
                },
            'fpar' : {
                'set_aom_voltage' : 30,
                'floating_average': 11, #floating average time (ms)
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
        
        #gate modulation
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
                    }
                },

        
        # remote TPQI adwin control
        'remote_tpqi_control' : {
                'index' : 9,
                'file' : 'conditional_repump_lt1_and_lt2_tpqi.TB9',
                'par' : {
                    'set_noof_tailcts' : 19,
                    'set_green_aom_dac' : 26,
                    'set_repump_duration' : 27, # in units of 1us
                    'set_probe_duration' : 28, # in units of 1us
                    'set_cr_time_limit' : 29, # in units of 1us
                    'set_ex_aom_dac' : 30,
                    'set_a_aom_dac' : 31,
                    'set_cr_count_threshold_probe' : 68,
                    'set_cr_count_threshold_prepare' : 75,
                    'set_counter' : 78,
                    'get_cr_check_counts' : 70,
                    'get_cr_below_threshold_events' : 71,
                    'get_noof_cr_checks' : 72,
                    'get_noof_tpqi_starts' : 73,
                    'get_noof_tpqi_stops' : 74,
                    'get_repump_counts' : 76,
                    'get_lt1_oks' : 77,
                    'get_noof_triggers_sent' : 80
                    },
                'fpar' : {
                    'set_green_aom_voltage' : 30,
                    'set_ex_aom_voltage' : 31,
                    'set_a_aom_voltage' : 32,
                    'set_green_aom_voltage_zero' : 33,
                    },
                },
        
        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt2.TB9',
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
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10]
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
                    ['A_RO_voltage'         , 0.8]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                },
        
        'spincontrol' : {  #with conditional repump, resonant
                'index' : 9,
                'file' : 'spincontrol_lt2.TB9',
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
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['RO_repetitions'              ,1000],
                    ['RO_duration'                 ,  50],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10]
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
                    ['A_RO_voltage'         , 0.8]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                },
        
        'spinmanipulation' : { #oldskool, with green
                'index' : 9,
                'file' : 'spinmanipulation_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   4],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,   1],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   1],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   5],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10],
                    ['green_readout_duration'      ,   1],
                    ['datapoints'                  ,  10]
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
                    ['green_readout_voltage', 0.8]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                },

        'lde' : {
                'index' : 9,
                'file' : 'lde_control_lt2_v1.TB9',
                'params_long' : [
                    ('counter_channel'          , 1),
                    ('green_laser_DAC_channel'  , 7),
                    ('Ex_laser_DAC_channel'     , 6),
                    ('A_laser_DAC_channel'      , 8),
                    ('CR_duration'              , 50),
                    ('CR_preselect'             , 10),
                    ('CR_probe'                 , 10),
                    ('green_repump_duration'    , 5),
                    ('wait_before_SSRO'         , 1),
                    ('SSRO_duration'            , 20),
                    ('max_LDE_duration'         , 1000),
                    ('AWG_start_DO_channel'     , 1),
                    ('PLU_arm_DO_channel'       , 100),
                    ('remote_CR_DO_channel'     , 16),
                    ('remote_CR_done_DI_bit'    , 2**8),
                    ('remote_SSRO_DO_channel'   , 17),
                    ('PLU_success_DI_bit'       , 2**18),
                    ('PLU_state_DI_bit'         , 2**14),
                    ('SSRO_duration_lt1'        , 20),
                    ('CR_duration_lt1'          , 50),
                    ],
                'params_long_index' : 20,
                'params_long_length' : 20,
                'params_float' : [
                    ('green_repump_voltage'     , 0.8),
                    ('green_off_voltage'        , 0.8),
                    ('Ex_CR_voltage'            , 0.8),
                    ('A_CR_voltage'             , 0.8),
                    ('Ex_RO_voltage'            , 0.8),
                    ('A_RO_voltage'             , 0.8),
                    ],
                'params_float_index' : 21,
                'params_float_length' : 6,
                'par' : {
                    'set_CR_preselect'          : 75,
                    'set_CR_probe'              : 68,
                    'get_seq_LT1_PSB_counts'    : 69,
                    'get_probe_counts'          : 70,
                    'get_below_threshold_events': 71,
                    'get_noof_CR_checks'        : 72,
                    'get_noof_seq_starts'       : 73,
                    'get_noof_seq_timeouts'     : 74,                    
                    'get_repumping_counts'      : 76,
                    'get_noof_LT1_CR_OKs'       : 77,
                    'get_seq_LT2_PSB_counts'    : 79,
                    'get_noof_LT1_CR_triggers'  : 80,
                    'get_noof_SSROs'            : 67,
                    'get_noof_PLU_markers'      : 65,
                    'get_noof_LT1_SSRO_triggers': 61,
                    },
                'data_long' : {
                    'CR_hist_first'             : 7,
                    'CR_hist'                   : 8,
                    'SSRO_counts'               : 22,
                    'CR_after_SSRO'             : 23,
                    'PLU_state'                 : 24,
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
        'newfocus_frq' : 5,
        'newfocus_aom' : 6,
        'matisse_aom' : 7,
        'gate_1' : 3,
        }

config['adwin_lt1_dios'] = {

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
        
        'gate_modulation' :  {
            'index' : 7, 
            'file' : 'gate_modulation.TB7',
            'par' : {
                'modulation_on' : 14,
                'dac_channel' : 12,
                'modulation_period' : 13, #half period ms
                },
            'fpar' : {
                'modulation_voltage' : 12,
                },
            },
                  
#                'dac_pulse' : {
#                     'index' : 6,
#                     'file' : 'lt1_universalDAC.tb6',
#                     'par'  : {
#                         'dac_no': 63,
#                         'condition':64, #not sure what this is, value is always 1?
#                         'duration' : 65,
#                         },
#                     'fpar' :{
#                         'voltage off': 63,
#                         'voltage on': 64,
#                         }

        # remote TPQI adwin control
        'remote_tpqi_control' : {
                'index' : 9,
                'file' : 'lt1_remote_conditional_repump.TB9',
                'par' : {
                    'set_green_aom_dac' : 26,
                    'set_repump_duration' : 27, # in units of 1us
                    'set_probe_duration' : 28, # in units of 1us
                    'set_ex_aom_dac' : 30,
                    'set_a_aom_dac' : 31,
                    'set_cr_count_threshold_probe' : 68,
                    'set_cr_count_threshold_prepare' : 75,
                    'set_counter' : 78,
                    'get_cr_check_counts' : 70,
                    'get_cr_below_threshold_events' : 71,
                    'get_noof_cr_checks' : 72,
                    'get_repump_counts' : 76,
                    'get_noof_oks_sent' : 77,
                    'get_noof_triggers' : 79,
                    },
                'fpar' : {
                    'set_green_aom_voltage' : 30,
                    'set_ex_aom_voltage' : 31,
                    'set_a_aom_voltage' : 32,
                    },
                },
        
        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt1.TB9',
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
                    ['cycle_duration'              , 300]
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
                    ['A_RO_voltage'         , 0.8]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                },

        'spincontrol' : {  #with conditional repump, resonant
                'index' : 9,
                'file' : 'spincontrol_lt1.TB9',
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
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['RO_repetitions'              ,1000],
                    ['RO_duration'                 ,  50],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
                    ['CR_probe'                    ,  10]
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
                    ['A_RO_voltage'         , 0.8]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                },

        'lde' : {
                'index' : 9,
                'file' : 'lde_control_lt1_v1.TB9',
                'params_long': [
                    ('counter_channel'              , 1),
                    ('green_laser_DAC_channel'      , 7),
                    ('Ex_laser_DAC_channel'         , 6),
                    ('A_laser_DAC_channel'          , 8),
                    ('CR_duration'                  , 50),
                    ('CR_preselect'                 , 10),
                    ('CR_probe'                     , 10),
                    ('green_repump_duration'        , 5),
                    ('remote_CR_DI_channel'         , 10),
                    ('remote_CR_done_DO_channel'    , 1),
                    ('remote_SSRO_DI_channel'       , 9),
                    ('SSRO_duration'                , 20),
                    ],
                'params_long_index' : 20,
                'params_long_length' : 12,
                'params_float' : [
                    ('green_repump_voltage' , 0.8),
                    ('green_off_voltage'    , 0.),
                    ('Ex_CR_voltage'        , 0.8),
                    ('A_CR_voltage'         , 0.8),
                    ('Ex_RO_voltage'        , 0.8),
                    ('A_RO_voltage'         , 0.),
                    ],
                'params_float_index' : 21,
                'params_float_length' : 6,
                'par' : {
                    'set_CR_preselect'          : 75,
                    'set_CR_probe'              : 68,
                    'get_probe_counts'          : 70,
                    'get_below_threshold_events': 71,
                    'get_noof_CR_checks'        : 72,
                    'get_repumping_counts'      : 76,
                    'get_noof_LT1_CR_OKs'       : 77,
                    'get_noof_CR_triggers'      : 79,
                    'get_noof_SSROs'            : 67,
                    'get_noof_SSRO_triggers'    : 65,
                    },
                'data_long' : {
                    'CR_hist_first'             : 7,
                    'CR_hist'                   : 8,
                    'SSRO_counts'               : 22,
                    'CR_after_SSRO'             : 23,
                    },
                },

                
        }


