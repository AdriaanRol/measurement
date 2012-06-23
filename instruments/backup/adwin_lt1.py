# Virtual adwin instrument, adapted from rt2 to fit lt2, dec 2011 
import os
import types
import qt
import numpy as np
from instrument import Instrument
import time
from lib import config

class adwin_lt1(Instrument):
    def __init__(self, name, **kw):
        Instrument.__init__(self, name, tags=['virtual'])

        #import qt
        self.physical_adwin = qt.instruments['physical_adwin_lt1']
        #self.physical_adwin.Boot()

        self.ADWIN_DIR = 'D:\\measuring\\user\\ADwin_Codes\\adwin_gold_2\\'
        
        self.ADWIN_DEFAULT_PROCESSES = [ 'counter', 'set_dio', 'set_dac',
                'linescan' ]
        
        #FIXME: these adwin processes should be rewritten for adwin gold
        self.ADWIN_PROCESSES = {                
                
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
#                  
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
                            'set_cr_count_threshold' : 75,
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
                }

        self.ADWIN_DAC_OUTPUTS = {
                    'atto_x' : 1,
                    'atto_y' : 2,
                    'atto_z' : 8,
                    'green_aom': 4,
                    'newfocus_frq' : 5,
                    'newfocus_aom' : 6,
                    'matisse_aom' : 7,
                    'gate_1' : 3,
                }

        self._dac_voltages = {
                'atto_x' : 0,
                'atto_y' : 0,
                'atto_z' : 0,
                'green_aom' : 0,
                'newfocus_frq' : 0,
                'newfocus_aom' : 0,
                'matisse_aom' : 0,
                'gate_1' : 0,
                }
        
        if kw.get('init', False):
            self._load_programs()

        # the accessible functions
        # initialization
        self.add_function('boot')
        self.add_function('load_programs')
        
        ### processes
        # counter
        self.add_function('start_counter')
        self.add_function('stop_counter')
        self.add_function('is_counter_running')
        self.add_function('get_countrates')

        # linescanning
        self.add_function('start_linescan')
        self.add_function('stop_linescan')
        self.add_function('is_linescan_running')
        self.add_function('get_linescan_counts')
        self.add_function('get_linescan_px_clock')
        self.add_function('get_linescan_supplemental_data')

        # set outputs
        self.add_function('set_ttl')
        self.add_function('set_dac_voltage')
        self.add_function('get_dac_voltage')
# 
#         # advanced dac functions
#         self.add_function('move_to_xyz_U')
#         self.add_function('get_xyz_U')
        self.add_function('move_to_dac_voltage')

        # public adwin tools
        self.add_function('get_process_status')

        # Set max ADwin speed (mV/s)
        # #FIXME dont set this here
        # self.physical_adwin.Set_FPar(29,10000.0)

        # set up config file
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self.ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()

    ### config management
    def load_cfg(self, set_voltages=False):
        params = self.ins_cfg.get_all()
        if 'dac_voltages' in params:
            for d in params['dac_voltages']:
                if set_voltages:
                    self.set_dac_voltage((d, params['dac_voltages'][d]))
                else:
                    self._dac_voltages[d] = params['dac_voltages'][d]

    def save_cfg(self):
        self.ins_cfg['dac_voltages'] = self._dac_voltages

    ### end config management


    def boot(self):
        self.physical_adwin.Boot()
        self.load_programs()  
 
    def set_dac_voltage(self, (name, value), timeout=1):
        #print('setting DAC %s to %s V'%(name,value))
        p = self.ADWIN_PROCESSES['set_dac']
        _t0 = time.time()
        while (self.physical_adwin.Process_Status(p['index']) !=0):
            if time.time() > _t0+timeout:
                print 'timeout in ADwin: set_dac_voltage'
                return False
            time.sleep(.001)
        
        self.physical_adwin.Set_Par(p['par']['dac_no'], self.ADWIN_DAC_OUTPUTS[name])
        self.physical_adwin.Set_FPar(p['fpar']['dac_voltage'], value)
        self.physical_adwin.Start_Process(p['index'])
        self._dac_voltages[name] = value
        self.save_cfg()
    
    def get_dac_voltage(self, name):
        return self._dac_voltages[name]
    
    def get_dac_voltages(self, names):
        return [ self.get_dac_voltage(n) for n in names ]      
    
    def set_ttl(self, val):
        p = self.ADWIN_PROCESSES['set_dio']
        self.physical_adwin.Set_Par(p['par']['dio_no'], val[0])
        self.physical_adwin.Set_Par(p['par']['dio_val'], val[1])
        self.physical_adwin.Start_Process(p['index'])  
    
    def stop_process(self,process_nr):
        self.physical_adwin.Stop_Process(process_nr)

    def get_process_status(self, name):
        return self.physical_adwin.Process_Status(
                self.ADWIN_PROCESSES[name]['index'])

    def wait_for_process(self, name):
        while bool(self.get_process_status(name)):
            time.sleep(0.005)
        return

    def load_programs(self):
        for p in self.ADWIN_PROCESSES.keys():
            if p in self.ADWIN_DEFAULT_PROCESSES:
                print self.ADWIN_DIR + self.ADWIN_PROCESSES[p]['file']
                self.physical_adwin.Load(
                        self.ADWIN_DIR + self.ADWIN_PROCESSES[p]['file'])
                
    #FIXME: never tested            
#     def Pulse_DAC_Voltage(self, DAC, Voltage_pulse, Voltage_off, duration):
#         p = self.ADWIN_PROCESSES['dac_pulse']
#         while self.physical_adwin.Process_Status(p['index']) > 0:
#             print('Pulse_DAC_Voltage: waiting for previous process to finish')
#             sleep(0.1) 
#         self.physical_adwin.Set_Par(p['dac_no'],self.ADWIN_DAC_OUTPUTS[DAC])
#         self.physical_adwin.Set_Par(p['condition'],1)
#         self.physical_adwin.Set_Par(p['dur    #FIXME: never tested ation'],duration)
#         self.physical_adwin.Set_FPar(p['voltage off'],Voltage_off)
#         self.physical_adwin.Set_FPar(p['voltage on'],Voltage_pulse)
#         self.physical_adwin.Load(self.ADWIN_DIR +p['file'])
#         self.physical_adwin.Start_Process(p['index'])
#         while self.physical_adwin.Process_Status(p['index']) > 0:
#             time.sleep(0.01)     
   
   # counter
    def set_simple_counting(self, *arg, **kw):
        p = self.ADWIN_PROCESSES['counter']
        self.physical_adwin.Stop_Process(p['index'])
        self.physical_adwin.Load(
                self.ADWIN_DIR + p['file'])
        self.start_counter(*arg, **kw)
    
    def start_counter(self, int_time=1, avg_periods=100, single_run=0):
        p = self.ADWIN_PROCESSES['counter']
        self.physical_adwin.Set_Par(p['par']['set_integration_time'], int_time)
        self.physical_adwin.Set_Par(p['par']['set_avg_periods'], avg_periods)
        self.physical_adwin.Set_Par(p['par']['set_single_run'], single_run)
        self.physical_adwin.Start_Process(p['index'])

    def stop_counter(self):
        p = self.ADWIN_PROCESSES['counter']
        self.physical_adwin.Stop_Process(p['index'])

    def is_counter_running(self):
        return bool(self.get_process_status('counter'))

    def get_countrates(self):
        if self.is_counter_running():
            p = self.ADWIN_PROCESSES['counter']
            cr = []
            for i in p['par']['get_countrates']:
                cr.append(self.physical_adwin.Get_Par(i))
            return cr
    
    def get_last_counts(self):
        p = self.ADWIN_PROCESSES['counter']
        l = p['info']['counters']
        c = self.physical_adwin.Get_Data_Long(
            p['data_long']['get_last_counts'], 1, l)
        return c

    def measure_counts(self, int_time):
        p = self.ADWIN_PROCESSES['counter']
        self.stop_counter()
        self.start_counter(int_time, 1, 1)
        while self.is_counter_running():
            time.sleep(0.01)
        return self.get_last_counts()

    #FIXME: once tested 
    def set_resonant_counting(self, aom_dac='green_aom', aom_voltage= 7.,
             aom_duration=1, probe_duration=10, red_powers=[5e-9, 5e-9],
             red_aoms=['NewfocusAOM_lt1', 'MatisseAOM_lt1'], floating_average = 100):
        p = self.ADWIN_PROCESSES['resonant_counting']
        self.physical_adwin.Stop_Process(p['index'])
        self.physical_adwin.Load(
                self.ADWIN_DIR + p['file'])
        
        self.physical_adwin.Set_Par(p['par']['set_aom_dac'], 
                self.ADWIN_DAC_OUTPUTS[aom_dac])
        self.physical_adwin.Set_Par(p['par']['set_aom_duration'], aom_duration)
        self.physical_adwin.Set_Par(p['par']['set_probe_duration'], 
                probe_duration)
        self.physical_adwin.Set_FPar(p['fpar']['set_aom_voltage'], aom_voltage)
        self.physical_adwin.Set_FPar(p['fpar']['floating_average'], floating_average)
 
        time.sleep(1)
        for i,n in enumerate(red_aoms):
            qt.instruments[n].set_power(red_powers[i])
         
        self.physical_adwin.Start_Process(p['index'])


    # linescan
    def start_linescan(self, dac_names, start_voltages, stop_voltages, steps, 
            px_time, value='counts', scan_to_start=False, blocking=False, 
            abort_if_running=True):
        """
        Starts the multidimensional linescan on the adwin. 
        
        Arguments:
                
        dac_names : [ string ]
            array of the dac names
        start_voltages, stop_voltages: [ float ]
            arrays for the corresponding start/stop voltages
        steps : int
            no of steps between these two points, incl start and stop
        px_time : int
            time in ms how long to measure per step
        value = 'counts' : string id
            one of the following, to indicate what to measure:
            'counts' : let the adwin measure the counts per pixel
            'none' : adwin only steps
            'counts+suppl' : counts per pixel, plus adwin will record
                the value of FPar #2 as supplemental data

            in any case, the pixel clock will be incremented for each step.
        scan_to_start = False : bool
            if True, scan involved dacs to start first
            right now, with default settings of speed2px()

        blocking = False : bool
            if True, do not return until finished

        abort_if_running = True : bool
            if True, check if linescan is running, and if so, quit right away
        
        """
        if abort_if_running and self.is_linescan_running():
            return
               
        if scan_to_start:
            _steps,_pxtime = self.speed2px(dac_names, start_voltages)
            self.start_linescan(dac_names, self.get_dac_voltages(dac_names),
                    start_voltages, _steps, _pxtime, value='none', 
                    scan_to_start=False)
            while self.is_linescan_running():
                time.sleep(0.005)
            for i,n in enumerate(dac_names):
                self._dac_voltages[n] = start_voltages[i]
                self.save_cfg()
            
            # stabilize a bit, better for attocubes
            time.sleep(0.05)

        p = self.ADWIN_PROCESSES['linescan']
        dacs = [ self.ADWIN_DAC_OUTPUTS[n] for n in dac_names ]
        
        # set all the required input params for the adwin process
        # see the adwin process for details
        self.physical_adwin.Set_Par(p['par']['set_cnt_dacs'], len(dac_names))
        self.physical_adwin.Set_Par(p['par']['set_steps'], steps)
        self.physical_adwin.Set_FPar(p['fpar']['set_px_time'], px_time)
        
        self.physical_adwin.Set_Data_Long(np.array(dacs), p['data_long']\
                ['set_dac_numbers'],1,len(dac_names))
        self.physical_adwin.Set_Data_Float(start_voltages, 
                p['data_float']['set_start_voltages'], 1, len(dac_names))
        self.physical_adwin.Set_Data_Float(stop_voltages, 
                p['data_float']['set_stop_voltages'], 1, len(dac_names))

        # debug
        # print 'about to start ls', dacs, steps, px_time, start_voltages, stop_voltages
        
        # what the adwin does on each px is int-encoded
        px_actions = {
                'none' : 0,
                'counts' : 1,
                'counts+suppl' : 2,
                }
        self.physical_adwin.Set_Par(p['par']['set_px_action'],px_actions[value])
        self.physical_adwin.Start_Process(p['index'])
        
        if blocking:
            while self.is_linescan_running():
                time.sleep(0.005)
        
        # FIXME here we might lose the information about the current voltage,
        # if the scan is not finished properly
        for i,n in enumerate(dac_names):
            self._dac_voltages[n] = stop_voltages[i]
        self.save_cfg()

    def speed2px(self, dac_names, target_voltages, speed=5000, pxtime=5,
            minsteps=10):
        """
        Parameters:
        - dac_names : [ string ]
        - end_voltages : [ float ], one voltage per dac
        - speed : float, (mV/s)
        - pxtime : int, (ms)
        - minsteps : int, never return less than this number for steps
        """
        current_voltages = self.get_dac_voltages(dac_names)
        maxdiff = max([ abs(t-current_voltages[i]) for i,t in \
                enumerate(target_voltages) ])
        steps = int(1e6*maxdiff/(pxtime*speed)) # includes all unit conversions

        return max(steps, minsteps), pxtime

    def stop_linescan(self):
        p = self.ADWIN_PROCESSES['linescan']
        self.physical_adwin.Stop_Process(p['index'])

    def is_linescan_running(self):
        return bool(self.get_process_status('linescan'))

    def get_linescan_counts(self, steps):
        p = self.ADWIN_PROCESSES['linescan']
        c = []
        
        for i in p['data_long']['get_counts']:

            #disregard the first value (see adwin program)
            c.append(self.physical_adwin.Get_Data_Long(i, 1, steps+1)[1:])
        return c

    def get_linescan_supplemental_data(self, steps):
        p = self.ADWIN_PROCESSES['linescan']
        return self.physical_adwin.Get_Data_Float(
                p['data_float']['get_supplemental_data'], 1, steps+1)[1:]
        
    def get_linescan_px_clock(self):
        p = self.ADWIN_PROCESSES['linescan']
        return self.physical_adwin.Get_Par(p['par']['get_px_clock'])

    # end linescan            
   
    # FIXME too explicit. make that general. 
    def get_xyz_U(self):
        return self.get_dac_voltages(['atto_x','atto_y','atto_z'])

    def move_to_xyz_U(self, target_voltages, speed=5000, blocking=False):
        
        current_voltages = self.get_xyz_U()
        dac_names = ['atto_x','atto_y','atto_z']
        steps, pxtime = self.speed2px(dac_names, target_voltages, speed)
        
        self.start_linescan(dac_names, current_voltages, target_voltages,
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)
        
        return

    def move_to_dac_voltage(self, dac_name, target_voltage, speed=5000, 
            blocking=False):

        current_voltage = self.get_dac_voltage(dac_name)
        steps, pxtime = self.speed2px([dac_name], [target_voltage], speed)
        self.start_linescan([dac_name], [current_voltage], [target_voltage],
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)


    # TPQI
    def start_remote_tpqi_control(self, **kw):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        self.physical_adwin.Stop_Process(p['index'])
        
        for i in range(10):
            try:
               self.physical_adwin.Stop_Process(i)
            except:
                adwin_lt1.stop_remote_tpqi_control()
                pass

        self.physical_adwin.Load(
                        self.ADWIN_DIR + p['file'])

        
        green_aom_dac = kw.get('green_aom_dac', self.ADWIN_DAC_OUTPUTS['green_aom'])
        ex_aom_dac = kw.get('ex_aom_dac', self.ADWIN_DAC_OUTPUTS['matisse_aom'])
        a_aom_dac = kw.get('a_aom_dac', self.ADWIN_DAC_OUTPUTS['newfocus_aom'])
        repump_duration = kw.get('repump_duration', 10)
        probe_duration = kw.get('probe_duration', 100)
        

        cr_count_threshold = kw.get('cr_count_threshold', 10)
        counter = kw.get('counter', 1)
        green_aom_voltage = kw.get('green_aom_voltage', 0.8)
        ex_aom_voltage = kw.get('ex_aom_voltage', 0.8)
        a_aom_voltage = kw.get('a_aom_voltage', 0.8)

        self.physical_adwin.Set_Par(p['par']['set_green_aom_dac'], 
                green_aom_dac)
        self.physical_adwin.Set_Par(p['par']['set_ex_aom_dac'], 
                ex_aom_dac)
        self.physical_adwin.Set_Par(p['par']['set_a_aom_dac'], 
                a_aom_dac)
        self.physical_adwin.Set_Par(p['par']['set_repump_duration'], 
                repump_duration)
        self.physical_adwin.Set_Par(p['par']['set_probe_duration'], 
                probe_duration)
        self.physical_adwin.Set_Par(p['par']['set_cr_count_threshold'], 
                cr_count_threshold)
        self.physical_adwin.Set_Par(p['par']['set_counter'],
                counter)

        self.physical_adwin.Set_FPar(p['fpar']['set_green_aom_voltage'], 
                green_aom_voltage)
        self.physical_adwin.Set_FPar(p['fpar']['set_ex_aom_voltage'], 
                ex_aom_voltage)
        self.physical_adwin.Set_FPar(p['fpar']['set_a_aom_voltage'], 
                a_aom_voltage)

        self.physical_adwin.Start_Process(p['index'])

    def start_adwin_SSRO(self, **kw):
        p = self.ADWIN_PROCESSES['singleshot']
        self.physical_adwin.Stop_Process(p['index'])
        for i in range(10):
            try:
                if not(i==7):
                    self.physical_adwin.Stop_Process(i)
            except:
                pass

        self.physical_adwin.Load(
                        self.ADWIN_DIR + p['file'])

        params_long = np.zeros(p['params_long_length'], dtype = int)
        for i in range(len(p['params_long'])):
            val = kw.get(p['params_long'][i][0], p['params_long'][i][1])
            params_long[i] = val
        self.physical_adwin.Set_Data_Long(params_long, 
            p['params_long_index'], 1, p['params_long_length'])
            
        params_float = np.zeros(p['params_float_length'], dtype = float)
        for i in range(len(p['params_float'])):
            val = kw.get(p['params_float'][i][0], p['params_float'][i][1])
            params_float[i] = val
        self.physical_adwin.Set_Data_Float(params_float, 
            p['params_float_index'], 1, p['params_float_length'])
            
        self.physical_adwin.Start_Process(p['index'])

    def stop_remote_tpqi_control(self):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        self.physical_adwin.Stop_Process(p['index'])
    
    def remote_tpqi_control_set_cr_count_threshold(self,val):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        self.physical_adwin.Set_Par(p['par']['set_cr_count_threshold'], 
                val)

    def remote_tpqi_control_get_cr_check_counts(self):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        return self.physical_adwin.Get_Par(p['par']['get_cr_check_counts'])

    def remote_tpqi_control_get_cr_below_threshold_events(self):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        return self.physical_adwin.Get_Par(p['par']['get_cr_below_threshold_events'])

    def remote_tpqi_control_get_noof_cr_checks(self):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        return self.physical_adwin.Get_Par(p['par']['get_noof_cr_checks'])

    def remote_tpqi_control_get_repump_counts(self):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        return self.physical_adwin.Get_Par(p['par']['get_repump_counts'])

    def remote_tpqi_control_get_noof_trigger(self):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        return self.physical_adwin.Get_Par(p['par']['get_noof_triggers'])

    def remote_tpqi_control_get_noof_oks_sent(self):
        p = self.ADWIN_PROCESSES['remote_tpqi_control']
        return self.physical_adwin.Get_Par(p['par']['get_noof_oks_sent']) 
