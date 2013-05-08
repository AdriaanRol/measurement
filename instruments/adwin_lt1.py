# Virtual adwin instrument, adapted from rt2 to fit lt2, dec 2011 
import os
import types
import qt
import numpy as np
from instrument import Instrument
import time
from lib import config
from adwin import adwin
from measurement.lib.config import adwins as adwinscfg

class adwin_lt1(adwin):
    def __init__(self, name, physical_adwin='physical_adwin_lt1', **kw):
        adwin.__init__(self, name, 
                adwin = qt.instruments[physical_adwin], 
                processes = adwinscfg.config['adwin_lt1_processes'],
                default_processes = ['counter', 'set_dac', 'set_dio', 'linescan',
                    'DIO_test'], 
                dacs = adwinscfg.config['adwin_lt1_dacs'],
                tags = ['virtual'],
                process_subfolder = qt.config['adwin_lt1_subfolder'], **kw)

        # counting
        self.add_function('set_resonant_counting')

        # linescanning
        self.add_function('linescan')
        self.add_function('get_linescan_counts')
        self.add_function('get_linescan_px_clock')
        self.add_function('get_linescan_supplemental_data')

         # advanced dac functions
        self.add_function('move_to_xyz_U')
        self.add_function('get_xyz_U')
        self.add_function('move_to_dac_voltage')

        # public adwin tools
        self.add_function('get_process_status')

    def set_resonant_counting(self, aom_dac='green_aom', aom_voltage= 7.,
             aom_duration=1, probe_duration=10, red_powers=[5e-9, 5e-9],
             red_aoms=['NewfocusAOM_lt1', 'MatisseAOM_lt1'], floating_average = 100):
        
        for i,n in enumerate(red_aoms):
            qt.instruments[n].set_power(red_powers[i])

        self.start_resonant_counting(stop=True, load=True,
                set_aom_dac = self.dacs[aom_dac],
                set_aom_duration = aom_duration,
                set_probe_duration = probe_duration,
                set_aom_voltage = aom_voltage,
                floating_average = floating_average) 
    
    def set_altern_resonant_counting(self,
            repump_aom = 'green_aom',
            pump_aom = 'velocity1_aom',
            probe_aom = 'velocity2_aom',
            pump_aom_ins = 'Velocity1AOM',
            probe_aom_ins = 'Velocity2AOM',
            repump_duration = 5,
            pump_duration = 2,
            probe_duration = 2,
            repump_voltage = 7.,
            pump_power = 10e-9,
            probe_power = 10e-9,
            floating_average = 10,
            pp_cycles = 5,
            single_shot = 0,
            prepump = 1,
            prepump_duration = 10):

        self.start_alternating_resonant_counting(
                stop=True, load=True,
                set_repump_aom_dac = self.dacs[repump_aom],
                set_pump_aom_dac = self.dacs[pump_aom],
                set_probe_aom_dac = self.dacs[probe_aom],
                set_repump_duration = repump_duration,
                set_pump_duration = pump_duration,
                set_probe_duration = probe_duration,
                set_repump_aom_voltage = repump_voltage,
                set_pump_aom_voltage = \
                        qt.instruments[pump_aom_ins].power_to_voltage(
                            pump_power),
                set_probe_aom_voltage = \
                        qt.instruments[probe_aom_ins].power_to_voltage(
                            probe_power),
                set_floating_average = floating_average,
                set_pp_cycles = pp_cycles,
                set_single_shot = single_shot,
                set_prepump = prepump,
                set_prepump_duration = prepump_duration)

        
    # linescan
    def linescan(self, dac_names, start_voltages, stop_voltages, steps, 
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
            self.linescan(dac_names, self.get_dac_voltages(dac_names),
                    start_voltages, _steps, _pxtime, value='none', 
                    scan_to_start=False)
            while self.is_linescan_running():
                time.sleep(0.005)
            for i,n in enumerate(dac_names):
                self._dac_voltages[n] = start_voltages[i]
                self.save_cfg()
            
            # stabilize a bit, better for attocubes
            time.sleep(0.05)

        p = self.processes['linescan']
        dacs = [ self.dacs[n] for n in dac_names ]
        
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
        p = self.processes['linescan']
        self.physical_adwin.Stop_Process(p['index'])

    def is_linescan_running(self):
        return bool(self.get_process_status('linescan'))

    def get_linescan_counts(self, steps):
        p = self.processes['linescan']
        c = []
        
        for i in p['data_long']['get_counts']:

            #disregard the first value (see adwin program)
            c.append(self.physical_adwin.Get_Data_Long(i, 1, steps+1)[1:])
        return c

    def get_linescan_supplemental_data(self, steps):
        p = self.processes['linescan']
        return self.physical_adwin.Get_Data_Float(
                p['data_float']['get_supplemental_data'], 1, steps+1)[1:]
        
    def get_linescan_px_clock(self):
        p = self.processes['linescan']
        return self.physical_adwin.Get_Par(p['par']['get_px_clock'])

    # end linescan            
   
    def get_xyz_U(self):
        return self.get_dac_voltages(['atto_x','atto_y','atto_z'])

    def move_to_xyz_U(self, target_voltages, speed=5000, blocking=False):
        
        current_voltages = self.get_xyz_U()
        dac_names = ['atto_x','atto_y','atto_z']
        steps, pxtime = self.speed2px(dac_names, target_voltages, speed)
        
        self.linescan(dac_names, current_voltages, target_voltages,
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)
        
        return

    def move_to_dac_voltage(self, dac_name, target_voltage, speed=5000, 
            blocking=False):

        current_voltage = self.get_dac_voltage(dac_name)
        steps, pxtime = self.speed2px([dac_name], [target_voltage], speed)
        self.linescan([dac_name], [current_voltage], [target_voltage],
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)

    def measure_counts(self, int_time):
        self.start_counter(set_integration_time=int_time, set_avg_periods=1, set_single_run= 1)
        while self.is_counter_running():
            time.sleep(0.01)
        return self.get_last_counts()

