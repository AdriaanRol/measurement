import ctypes
import sys,os,time
import types
import gobject

from numpy import *

import qt
from instrument import Instrument

class laser_scan(Instrument):
    
    _data_update_interval = 100
    
    def __init__(self, name, address=None,
            laser='Velocity1', adwin='adwin',
            wavemeter='wavemeter', physical_adwin='physical_adwin',
            counters='counters'):
        
        Instrument.__init__(self, name, tags=['measure', 'virtual'])

        self._counter_was_running = False

        self.add_parameter('StartVoltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-3,maxval=3)

        self.add_parameter('StopVoltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-3,maxval=3)

        self.add_parameter('ScanSteps',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=3,maxval=65536)

        self.add_parameter('CurrentStep',
                           type=types.IntType,
                           flags=Instrument.FLAG_GET,
                           minval=0,maxval=65536)

        self.add_parameter('InitialWait',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='s',
                           minval=0,maxval=10)

        self.add_parameter('IntegrationTime',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='ms',
                           minval=1,maxval=1000)

        self.add_parameter('WavemeterChannel',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=4)

        self.add_parameter('CounterChannel',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0,maxval=4)
        self.add_parameter('FrequencyAveraging',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=100)

        self.add_parameter('FrequencyInterpolationStep',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=1000,
                           units='MHz')

        self.add_parameter('FrequencyReference',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=468000,maxval=472000,
                           units='GHz')

        self.add_parameter('PiezoVoltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=100)

        self.add_parameter('CurrentFrequency',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GET,
                           units='MHz')
        
        self.add_parameter('TraceFinished',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GET)

        self.add_function('start_scan')
        self.add_function('abort_scan')
        self.add_function('get_frequencies')
        self.add_function('get_counts')
        self.add_function('get_voltages')
        self.add_function('end_scan')

        self._StartVoltage               = 3.0
        self._StopVoltage                = -3.0
        self._ScanSteps                  = 101
        self._CurrentStep                = 0
        self._InitialWait                = 1.0
        self._IntegrationTime            = 20
        self._WavemeterChannel           = 3
        self._CounterChannel             = 0
        self._FrequencyAveraging         = 10
        self._FrequencyInterpolationStep = 10
        self._FrequencyReference         = 470400
        self._trace_finished             = False

        self._frequency = array(zeros(self._ScanSteps,float))
        self._counts    = array(zeros(self._ScanSteps,int))
        self._voltages  = linspace(self._StartVoltage, self._StopVoltage,
                self._ScanSteps)
        
        self._adwin = qt.instruments[adwin]
        self._counters = qt.instruments[counters]
        self._physical_adwin = qt.instruments[physical_adwin]
        self._ins_Laser = qt.instruments[laser]
        self._ins_Wavemeter = qt.instruments[wavemeter]
    
    def do_get_TraceFinished(self):
        return self._trace_finished

    def do_get_CurrentFrequency(self):
        self._CurrentFrequency = self._ins_Wavemeter.get_frequency(
                self._WavemeterChannel)*1000
        return self._CurrentFrequency

    def do_get_PiezoVoltage(self):
        return self._PiezoVoltage

    def do_set_PiezoVoltage(self, val):
        self._ins_Laser.set_piezo_voltage(val)
        self._PiezoVoltage = val

    def do_get_StartVoltage(self):
        return self._StartVoltage

    def do_set_StartVoltage(self, val):
        self._StartVoltage = val

    def do_get_StopVoltage(self):
        return self._StopVoltage

    def do_set_StopVoltage(self, val):
        self._StopVoltage = val

    def do_get_ScanSteps(self):
        return self._ScanSteps

    def do_set_ScanSteps(self, val):
        self._ScanSteps = val

    def do_get_CurrentStep(self):
        return self._CurrentStep

    def do_get_InitialWait(self):
        return self._InitialWait

    def do_set_InitialWait(self, val):
        self._InitialWait = val

    def do_get_IntegrationTime(self):
        return self._IntegrationTime

    def do_set_IntegrationTime(self, val):
        self._IntegrationTime = val

    def do_get_WavemeterChannel(self):
        return self._WavemeterChannel

    def do_set_WavemeterChannel(self, val):
        self._WavemeterChannel = val

    def do_get_CounterChannel(self):
        return self._CounterChannel

    def do_set_CounterChannel(self, val):
        self._CounterChannel = val

    def do_get_FrequencyAveraging(self):
        return self._FrequencyAveraging

    def do_set_FrequencyAveraging(self, val):
        self._FrequencyAveraging = val

    def do_get_FrequencyInterpolationStep(self):
        return self._FrequencyInterpolationStep

    def do_set_FrequencyInterpolationStep(self, val):
        self._FrequencyInterpolationStep = val

    def do_get_FrequencyReference(self):
        return self._FrequencyReference

    def do_set_FrequencyReference(self, val):
        self._FrequencyReference = val


    def start_scan(self):
        if self._adwin.is_counter_running(): 
            self._counters.set_is_running(False)
            self._counter_was_running = True
        self._CurrentStep= 0
        self._trace_finished = False
        self._ins_Wavemeter.set_active_channel(self._WavemeterChannel)

        self._frequency = array(zeros(self._ScanSteps,float))
        self._counts    = array(zeros(self._ScanSteps,int))
        self._voltages  = linspace(self._StartVoltage, self._StopVoltage,
                self._ScanSteps)

        gobject.timeout_add(int(self._IntegrationTime/4.),
                self._update_wm_frequency)
        gobject.timeout_add(self._data_update_interval,
                self._update_data)
        self._adwin.linescan(['velocity1_frq'], [self._StartVoltage],
                [self._StopVoltage], self._ScanSteps, self._IntegrationTime,
                value='counts+suppl')

    def end_scan(self, scan_back=True):
        if scan_back:
            self._adwin.linescan(['velocity1_frq'], [self._StopVoltage],
                    [self._StartVoltage], 100, 50, value='none')
        
        if self._counter_was_running:
            self._counters.set_is_running(True)
            self._counter_was_running = False

    def abort_scan(self):
        print 'Scan aborted'
        self._adwin.stop_linescan()  
    
    def get_voltages(self):
        return self._voltages

    def get_frequencies(self):
        return self._frequency

    def get_counts(self):
        return self._counts    
    
    def _update_wm_frequency(self):
        self._physical_adwin.Set_FPar(2, self.get_CurrentFrequency())

        if self._trace_finished:
            return False

        return True

    def _update_data(self):
        
        # doing it in this order ensures we don't miss data
        running = self._adwin.is_linescan_running()
        
        px = self._adwin.get_linescan_px_clock()
        self._frequency[:px] = self._adwin.get_linescan_supplemental_data(px)
        self._counts[:px] = self._adwin.get_linescan_counts(px)\
                [self._CounterChannel]

        self._CurrentStep = px
        self.get_CurrentStep()
        
        if running:
            return True
        else:
            self._trace_finished = True
            self.get_TraceFinished()

            # print self._frequency
            # print self._voltages
            # print self._counts

            return False

    
            

