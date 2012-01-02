# Virtual adwin instrument, adapted from rt2 to fit lt2, dec 2011 

import types
import qt
import numpy as np
from instrument import Instrument

class adwin_lt2(Instrument):
    def __init__(self, name):
        Instrument.__init__(self, name, tags=['virtual'])

        #import qt
        self.physical_adwin = qt.instruments['physical_adwin']
        self._ins_ADwin_pos = qt.instruments['ADwin_pos']
        #self.physical_adwin.Boot()

        self.ADWIN_DIR = 'D:\\measuring\\user\\ADwin_Codes\\'
        self.ADWIN_PROCESSES = { 
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
                        },
                    'data_long' : {
                        'set_dac_numbers' : 200,
                        'get_counts' : [11,12, 13],
                        },
                    'data_float' : {
                        'set_start_voltages' : 199,
                        'set_stop_voltages' : 198,
                        },
                    },
                
                'counter' : {
                    'index' : 1, 
                    'file' : 'CountFloatingAvg100ms.TB1',
                    'par' : {
                        'get_countrates' : [41, 42, 43, 44],
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
                        }
                    },
                
                'set_dio' :  {
                    'index' : 4, 
                    'file' : 'Set_TTL_Outputs_LTsetup2.TB4',
                    'par' : {
                        'dio_no' : 61,
                        'dio_val' : 62,
                        },
                    },
                }

        
        self._load_programs()

        # the accessible functions
        # initialization
        self.add_function('boot')
        
        # processes
        self.add_function('start_counter')
        self.add_function('stop_counter')
        self.add_function('is_counter_running')
        self.add_function('get_countrates')

        self.add_function('start_linescan')
        self.add_function('stop_linescan')
        self.add_function('is_linescan_running')
        self.add_function('get_linescan_counts')
        self.add_function('get_linescan_px_clock')

        self.add_function('set_ttl')
        self.add_function('move_abs_xyz')
        self.add_function('get_xyz_pos')
        self.add_function('get_xyz_U')
        self.add_function('set_dac_voltage')

        # tools
        self.add_function('get_process_status')


    def boot(self):
        self.physical_adwin.Boot()
        self._load_programs()

        
    # counter
    def start_counter(self):
        p = self.ADWIN_PROCESSES['counter']
        self.physical_adwin.Start_Process(p['index'])

    def stop_counter(self):
        p = self.ADWIN_PROCESSES['counter']
        self.physical_adwin.Stop_Process(p['index'])

    def is_counter_running(self):
        p = self.ADWIN_PROCESSES['counter']
        return bool(self.get_process_status(p['index']))

    def get_countrates(self):
        p = self.ADWIN_PROCESSES['counter']
        cr = []
        for i in p['par']['get_countrates']:
            cr.append(self.physical_adwin.Get_Par(i))
        return cr


    # linescan
    def start_linescan(self, dacs, start_voltages, stop_voltages, steps, 
            px_time, value='counts'):
        """Starts the multidimensional linescan on the adwin. Arguments:
        dacs:
            array of the dac numbers
        start_voltages, stop_voltages:
            arrays for the corresponding start/stop voltages
        steps:
            no of steps between these two points, incl start and stop
        px_time:
            time in ms how long to measure per step
        value = 'counts'
            one of the following, to indicate what to measure:
            'counts' : let the adwin measure the counts per pixel
            'none' : adwin only steps

            in any case, the pixel clock will be incremented for each step.
        """

        p = self.ADWIN_PROCESSES['linescan']

        # set all the required input params for the adwin process
        # see the adwin process for details
        self.physical_adwin.Set_Par(p['par']['set_cnt_dacs'], len(dacs))
        self.physical_adwin.Set_Par(p['par']['set_steps'], steps)
        self.physical_adwin.Set_FPar(p['fpar']['set_px_time'], px_time)
        self.physical_adwin.Set_Data_Long(dacs, p['data_long']\
                ['set_dac_numbers'],1, len(dacs))


        self.physical_adwin.Set_Data_Float(start_voltages, 
                p['data_float']['set_start_voltages'], 1, len(dacs))
        self.physical_adwin.Set_Data_Float(stop_voltages, 
                p['data_float']['set_stop_voltages'], 1, len(dacs))
    
        # what the adwin does on each px is int-encoded
        px_actions = {
                'none' : 0,
                'counts' : 1,
                }
        self.physical_adwin.Set_Par(p['par']['set_px_action'],px_actions[value])

        #Move to initial position
        #FIXME we already have the voltages, just set them
        start_v=[1,2,3]
        for i in [1,2,3]:
            if i in dacs:
                start_v[i-1]=start_voltages[dacs.tolist().index(i)]
            else:
                start_v[i-1]=self.physical_adwin.Get_Data_Float(1,1,3)[i-1]
        start_pos=[1,2,3]       
        start_pos[0]=self._ins_ADwin_pos.U_to_pos_x(start_v[0])
        start_pos[1]=self._ins_ADwin_pos.U_to_pos_y(start_v[1])
        start_pos[2]=self._ins_ADwin_pos.U_to_pos_z(start_v[2])
        print start_pos
        self.move_abs_xyz(start_pos[0],start_pos[1],start_pos[2])
        while self.physical_adwin.Process_Status(10):
            time.sleep(0.05)
        # end FIXME

        self.physical_adwin.Start_Process(p['index'])
    

    def stop_linescan(self):
        p = self.ADWIN_PROCESSES['linescan']
        self.physical_adwin.Stop_Process(p['index'])

    def is_linescan_running(self):
        return bool(self.get_process_status('linescan'))

    
    # FIXME: remove fake values
    def get_linescan_counts(self, steps):
        p = self.ADWIN_PROCESSES['linescan']
        c = []
        cfake=[]
        
        for i in p['data_long']['get_counts']:
            fakevals=np.linspace(-2,2,steps)
            cfake.append(np.sinc(fakevals))
        
            #disregard the first value (see adwin program)
            c.append(self.physical_adwin.Get_Data_Long(i, 1, steps+1)[1:])
    
        return c

    def get_linescan_px_clock(self):
        p = self.ADWIN_PROCESSES['linescan']
        return self.physical_adwin.Get_Par(p['par']['get_px_clock'])

    
    def set_dac_voltage(self, value):
        p = self.ADWIN_PROCESSES['set_dac']
        self.physical_adwin.Set_Par(p['par']['dac_no'], value[0])
        self.physical_adwin.Set_FPar(p['fpar']['dac_voltage'], value[1])
        self.physical_adwin.Start_Process(p['index'])
        
    def set_ttl(self, val):
        p = self.ADWIN_PROCESSES['set_dio']

        self.physical_adwin.Set_Par(p['par']['dio_no'], val[0])
        self.physical_adwin.Set_Par(p['par']['dio_val'], val[1])
        self.physical_adwin.Start_Process(p['index'])  
    
    
    def get_process_status(self, name):
        return self.physical_adwin.Process_Status(
                self.ADWIN_PROCESSES[name]['index'])

    def _load_programs(self):
        for p in self.ADWIN_PROCESSES.keys():
            self.physical_adwin.Load(
                    self.ADWIN_DIR + self.ADWIN_PROCESSES[p]['file'])
        
    # FIXME this is already in MOS (at least the conversion)
    def get_xyz_pos(self):
        v=[1,2,3]
        for i in [1,2,3]:
            v[i-1]=self.physical_adwin.Get_Data_Float(1,1,3)[i-1]
        pos=[1,2,3]     
        pos[0]=self._ins_ADwin_pos.U_to_pos_x(v[0])
        pos[1]=self._ins_ADwin_pos.U_to_pos_y(v[1])
        pos[2]=self._ins_ADwin_pos.U_to_pos_z(v[2])
        return pos

    def get_xyz_U(self):
        v=[1,2,3]
        for i in [1,2,3]:
            v[i-1]=self.physical_adwin.Get_Data_Float(1,1,3)[i-1]
            return v

    def move_abs_xyz(self, x, y,z):
        self._ins_ADwin_pos.set_X_position(x)
        self._ins_ADwin_pos.set_Y_position(y)
        self._ins_ADwin_pos.set_Z_position(z)
        self._ins_ADwin_pos.move_abs_xyz(x,y,z)
        return

    # end FIXME 

