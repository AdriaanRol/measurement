# control instrument for laser scan and frequency locking

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types
import ctypes
import time
from numpy import *
import qt
import matplotlib.pyplot as plt
import os
import ConfigParser

class Laser_scan(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=['measure', 'virtual'])

        self.add_parameter('StartVoltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-3,maxval=3)

        self.add_parameter('StepVoltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-3,maxval=3)

        self.add_parameter('ScanSteps',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=3,maxval=65536)

        self.add_parameter('ScanCount',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=1000)

#        self.add_parameter('ModulationPeriod',
#                           type=types.IntType,
#                           flags=Instrument.FLAG_GETSET,
#                           minval=1,maxval=1000)

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

        self.add_parameter('LaserInitialize',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('ScanBack',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('ScanBackTime',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='s',
                           minval=0.1,maxval=100)

        self.add_parameter('DCStarkShiftSweep',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('GateSweep',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('ModulateGate',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('DCStart',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10,maxval=10)

        self.add_parameter('DCStop',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10,maxval=10)

        self.add_parameter('DCstepsize',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10,maxval=10)

        self.add_parameter('PulseAOM',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('PulseDuration',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='microseconds',
                           minval=1,maxval=1e6)

        self.add_parameter('PowerLevelPulse',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='microWatt',
                           minval=0,maxval=1e3)

        self.add_parameter('PowerLevelOn',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='microWatt',
                           minval=0,maxval=1e3)

        self.add_parameter('PowerLevelScan',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='microWatt',
                           minval=0,maxval=1e3)

        self.add_parameter('WavemeterChannel',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=4)

        self.add_parameter('CounterChannel',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=5)

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

        self.add_parameter('ModeHopThreshold',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=10000)

        self.add_parameter('LaserOn',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('DCGate',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1,maxval=2)
        
        self.add_parameter('CurrentFrequency',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GET,
                           units='MHz')

        self.add_parameter('ScanVoltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-3,maxval=3)

        self.add_parameter('Gate1Voltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=2)

        self.add_parameter('Gate2Voltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10,maxval=10)

        self.add_parameter('LockFrequency',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('ScanRangeCenter',
                           type=types.FloatType,
                           flags=Instrument.FLAG_SET,
                           units = 'GHz',
                           minval = -300, maxval = 300)

        self.add_parameter('LockFrequencyDeviation',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GET,
                           units='MHz')

        self.add_parameter('FrequencySetpoint',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='GHz')

        self.add_parameter('FrequencyStep',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='MHz')

        self.add_parameter('PiezoVoltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=100)

        self.add_parameter('TraceIndex',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET)
        
        self.add_parameter('ScanIndex',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET)
        
        self.add_parameter('TraceFinished',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('MWOn',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('AutoOptimizeXY',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('AutoOptimizeZ',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('OptimizeInterval',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('Comments',
                           type=types.StringType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('MWfrequency',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz',
                           minval=9e3,maxval=6e9)

        self.add_parameter('MWpower',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='dBm',
                           minval=-145,maxval=30)

#        self.add_parameter('UsePicoharp',
#                           type=types.BooleanType,
#                           flags=Instrument.FLAG_GETSET)

        self.add_function('start_scan')
        self.add_function('pause_scan')
        self.add_function('abort_scan')
        self.add_function('SkipToNext')
        self.add_function('PulseAOM_manual')

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }


    


        self._StartVoltage               = 3.0
        self._StepVoltage                = -.001
        self._ScanSteps                  = 6000
        self._ScanCount                  = 10
        self._ModulationPeriod           = 1000
        self._ScanIndex                  = 0
        self._trace_finished             = -1
        self._InitialWait                = 1.0
        self._IntegrationTime            = 20
        self._LaserInitialize            = False
        self._ScanBack                   = True
        self._ScanBackTime               = 1.0
        self._DCStarkShiftSweep          = False
        self._GateSweep                  = False
        self._ModulateGate               = False
        self._DCStart                    = -10
        self._DCStop                     = 10
        self._DCstepsize                 = 1
        self._PulseAOM                   = True
        self._PulseDuration              = 10000
        self._PowerLevelPulse            = 50
        self._PowerLevelScan             = 0
        self._PowerLevelOn               = 250

        self._WavemeterChannel           = 2
        self._CounterChannel             = 5
        self._FrequencyAveraging         = 10
        self._FrequencyInterpolationStep = 10
        self._FrequencyReference         = 470400
        self._ModeHopThreshold           = 1000
        self._DCGate                     = 1
        self._CurrentFrequency           = 0
        self._ScanVoltage                = 0.0
        self._PiezoVoltage               = 50
        self._Gate1Voltage               = 0.0
        self._Gate2Voltage               = 0.0
        self._LockFrequency              = False
        self._LockFrequencyDeviation     = 0.0
        self._FrequencySetpoint          = 470400
        self._FrequencyStep              = 100
        self._AutoOptimizeXY             = False
        self._AutoOptimizeZ              = False
        self._OptimizeInterval           = 5
        self._Comments = ''
        self._UsePicoharp                = False
        
        self._OptimizeCounter            = 5
        self._OptimizeRepetitions        = 3
        self._StarkSweepRepetitions      = 3
        self._reuse_path                 = False
        self._save_index                 = 0

        

        self._deviation_record = zeros(100,dtype = float)
        self._deviation_counter = 0

        self._frequency = array(zeros(self._ScanSteps,float))
        self._counts    = array(zeros(self._ScanSteps,int))

        self._current_frequency_trace = array([[0,0]])
        self._current_counts_trace = array([[0,0]])
        self._current_scan_trace = array([[0,0]])
        self._frequency_traces = [self._current_frequency_trace]
        self._counts_traces = [self._current_counts_trace]
        self._scan_traces = [self._current_scan_trace]
        self._trace_index = 0

        self._mode = 0      # 0: wavelength trace
                            # 1: laser frequency lock
                            # 2: laser scan running
                            # 3: laser scan paused
                            # 4: laser scan stop
                            # 5: gate sweep running
                            # 6: gate sweep paused
                            # 7: gate sweep stop


        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self._ins_ADwin = qt.instruments['ADwin']
        self._ins_Laser = qt.instruments['NewfocusLaser']
        self._ins_Wavemeter = qt.instruments['wavemeter']
        self._ins_Setup = qt.instruments['TheSetup']
        self._ins_MW = qt.instruments['SMB100']

        self.load_cfg()
        self.get_LaserOn()
        self.set_is_running(True)
        self.get_MWOn()
        self.get_MWfrequency()
        self.get_MWpower()

    def set_reuse_path(self,val):
        self._reuse_path = val

    def set_path(self,val):
        self.path = val


    def set_save_index(self,val):
        self._save_index = val

    def load_cfg(self):
        config = ConfigParser.SafeConfigParser()
        config.read(qt.config['setup_cfg'])
        if config.has_section('LaserScan') == False:
            self.save_cfg()
            config.read(qt.config['setup_cfg'])
        self._StartVoltage = config.getfloat('LaserScan','StartVoltage')
        self._StepVoltage = config.getfloat('LaserScan','StepVoltage')
        self._ScanSteps = config.getint('LaserScan','ScanSteps')
        self._ScanCount = config.getint('LaserScan','ScanCount')
        self._ModulationPeriod = config.getint('LaserScan','ModulationPeriod')
        self._InitialWait = config.getfloat('LaserScan','InitialWait')
        self._IntegrationTime = config.getint('LaserScan','IntegrationTime')
        self._LaserInitialize = config.getboolean('LaserScan','LaserInitialize')
        self._ScanBack = config.getboolean('LaserScan','ScanBack')
        self._ScanBackTime = config.getfloat('LaserScan','ScanBackTime')
        self._DCStarkShiftSweep = config.getboolean('LaserScan','DCStarkShiftSweep')
        self._GateSweep = config.getboolean('LaserScan','GateSweep')
        self._ModulateGate = config.getboolean('LaserScan','ModulateGate')
        self._DCStart = config.getfloat('LaserScan','DCStart')
        self._DCStop = config.getfloat('LaserScan','DCStop')
        self._DCstepsize = config.getfloat('LaserScan','DCstepsize')
        self._PulseAOM = config.getboolean('LaserScan','PulseAOM')
        self._PulseDuration = config.getint('LaserScan','PulseDuration')
        self._PowerLevelPulse = config.getfloat('LaserScan','PowerLevelPulse')
        self._PowerLevelScan = config.getfloat('LaserScan','PowerLevelScan')
        self._PowerLevelOn = config.getfloat('LaserScan','PowerLevelOn')
        self._WavemeterChannel = config.getint('LaserScan','WavemeterChannel')
        self._CounterChannel = config.getint('LaserScan','CounterChannel')
        self._FrequencyAveraging = config.getint('LaserScan','FrequencyAveraging')
        self._FrequencyInterpolationStep = config.getint('LaserScan','FrequencyInterpolationStep')
        self._FrequencyReference = config.getfloat('LaserScan','FrequencyReference')
        self._ModeHopThreshold = config.getint('LaserScan','ModeHopThreshold')
        self._DCGate = config.getint('LaserScan','DCGate')
#        self._CurrentFrequency = config.getfloat('LaserScan','CurrentFrequency')
        self._ScanVoltage = config.getfloat('LaserScan','ScanVoltage')
        self._PiezoVoltage = config.getfloat('LaserScan','PiezoVoltage')
        self._Gate1Voltage = config.getfloat('LaserScan','Gate1Voltage')
        self._Gate2Voltage = config.getfloat('LaserScan','Gate2Voltage')
        self._FrequencySetpoint = config.getfloat('LaserScan','FrequencySetpoint')
        self._FrequencyStep = config.getint('LaserScan','FrequencySteo')
        self._AutoOptimizeXY = config.getboolean('LaserScan','AutoOptimizeXY')
        self._AutoOptimizeZ = config.getboolean('LaserScan','AutoOptimizeZ')
        self._OptimizeInterval = config.getint('LaserScan','OptimizeInterval')
        self._MWpower = config.getfloat('LaserScan','MWpower')
        self._ins_MW.set_power(self._MWpower)
        self._MWfrequency = config.getfloat('LaserScan','MWfrequency')
        self._ins_MW.set_frequency(self._MWfrequency)
        self._Comments = config.get('LaserScan','Comments')
        self._OptimizeCounter = config.getint('LaserScan','OptimizeCounter')
        self._OptimizeRepetitions = config.getint('LaserScan','OptimizeRepetitions')
        self._StarkSweepRepetitions = config.getint('LaserScan','StarkSweepRepetitions')
        
    def save_cfg(self):
        config = ConfigParser.SafeConfigParser()
        config.read(qt.config['setup_cfg'])
        if config.has_section('LaserScan') == False:
            config.add_section('LaserScan')
        config.set('LaserScan','StartVoltage',str(self._StartVoltage))
        config.set('LaserScan','StepVoltage',str(self._StepVoltage))
        config.set('LaserScan','ScanSteps',str(self._ScanSteps))
        config.set('LaserScan','ScanCount',str(self._ScanCount))
        config.set('LaserScan','ModulationPeriod',str(self._ModulationPeriod))
        config.set('LaserScan','InitialWait',str(self._InitialWait))
        config.set('LaserScan','IntegrationTime',str(self._IntegrationTime))
        config.set('LaserScan','LaserInitialize',str(self._LaserInitialize))
        config.set('LaserScan','ScanBack',str(self._ScanBack))
        config.set('LaserScan','ScanBackTime',str(self._ScanBackTime))
        config.set('LaserScan','DCStarkShiftSweep',str(self._DCStarkShiftSweep))
        config.set('LaserScan','GateSweep',str(self._GateSweep))
        config.set('LaserScan','ModulateGate',str(self._ModulateGate))
        config.set('LaserScan','DCStart',str(self._DCStart))
        config.set('LaserScan','DCStop',str(self._DCStop))
        config.set('LaserScan','DCstepsize',str(self._DCstepsize))
        config.set('LaserScan','PulseAOM',str(self._PulseAOM))
        config.set('LaserScan','PulseDuration',str(self._PulseDuration))
        config.set('LaserScan','PowerLevelPulse',str(self._PowerLevelPulse))
        config.set('LaserScan','PowerLevelScan',str(self._PowerLevelScan))
        config.set('LaserScan','PowerLevelOn',str(self._PowerLevelOn))
        config.set('LaserScan','WavemeterChannel',str(self._WavemeterChannel))
        config.set('LaserScan','CounterChannel',str(self._CounterChannel))
        config.set('LaserScan','FrequencyAveraging',str(self._FrequencyAveraging))
        config.set('LaserScan','FrequencyInterpolationStep',str(self._FrequencyInterpolationStep))
        config.set('LaserScan','FrequencyReference',str(self._FrequencyReference))
        config.set('LaserScan','ModeHopThreshold',str(self._ModeHopThreshold))
        config.set('LaserScan','DCGate',str(self._DCGate))
#        config.set('LaserScan','CurrentFrequency',str(self._CurrentFrequency))
        config.set('LaserScan','ScanVoltage',str(self._ScanVoltage))
        config.set('LaserScan','PiezoVoltage',str(self._PiezoVoltage))
        config.set('LaserScan','Gate1Voltage',str(self._Gate1Voltage))
        config.set('LaserScan','Gate2Voltage',str(self._Gate2Voltage))
        config.set('LaserScan','FrequencySetpoint',str(self._FrequencySetpoint))
        config.set('LaserScan','FrequencySteo',str(self._FrequencyStep))
        config.set('LaserScan','AutoOptimizeXY',str(self._AutoOptimizeXY))
        config.set('LaserScan','AutoOptimizeZ',str(self._AutoOptimizeZ))
        config.set('LaserScan','OptimizeInterval',str(self._OptimizeInterval))
        config.set('LaserScan','MWpower',str(self.get_MWpower()))
        config.set('LaserScan','MWfrequency',str(self.get_MWfrequency()))
        config.set('LaserScan','Comments','\''+self._Comments+'\'')
        config.set('LaserScan','OptimizeCounter',str(self._OptimizeCounter))
        config.set('LaserScan','OptimizeRepetitions',str(self._OptimizeRepetitions))
        config.set('LaserScan','StarkSweepRepetitions',str(self._StarkSweepRepetitions))
        with open(qt.config['setup_cfg'], 'wb') as configfile:
            config.write(configfile)

    def do_get_Comments(self):
        return self._Comments

    def do_set_Comments(self, val):
        self._Comments = val

    def do_get_TraceIndex(self):
        return self._trace_index

    def do_set_TraceIndex(self, val):
        self._trace_index = val

    def do_get_TraceFinished(self):
        return self._trace_finished

    def do_set_TraceFinished(self, val):
        self._trace_finished = val

    def do_get_ScanIndex(self):
        return self._ScanIndex

    def do_set_ScanIndex(self, val):
        self._ScanIndex = val

#    def do_get_ModulationPeriod(self):
#        return self._ModulationPeriod

#    def do_set_ModulationPeriod(self, val):
#        self._ModulationPeriod = val

    def do_get_StartVoltage(self):
        return self._StartVoltage

    def do_set_StartVoltage(self, val):
        self._StartVoltage = val

    def do_get_StepVoltage(self):
        return self._StepVoltage

    def do_set_StepVoltage(self, val):
        self._StepVoltage = val

    def do_get_ScanSteps(self):
        return self._ScanSteps

    def do_set_ScanSteps(self, val):
        self._ScanSteps = val

    def do_get_ScanCount(self):
        return self._ScanCount

    def do_set_ScanCount(self, val):
        self._ScanCount = val

    def do_get_InitialWait(self):
        return self._InitialWait

    def do_set_InitialWait(self, val):
        self._InitialWait = val

    def do_get_IntegrationTime(self):
        return self._IntegrationTime

    def do_set_IntegrationTime(self, val):
        self._IntegrationTime = val

    def do_get_LaserInitialize(self):
        return self._LaserInitialize

    def do_set_LaserInitialize(self, val):
        self._LaserInitialize = val

    def do_get_ScanBack(self):
        return self._ScanBack

    def do_set_ScanBack(self, val):
        self._ScanBack = val

    def do_get_ScanBackTime(self):
        return self._ScanBackTime

    def do_set_ScanBackTime(self, val):
        self._ScanBackTime = val

    def do_get_DCStarkShiftSweep(self):
        return self._DCStarkShiftSweep

    def do_set_DCStarkShiftSweep(self, val):
        self._DCStarkShiftSweep = val

    def do_get_GateSweep(self):
        return self._GateSweep

    def do_set_GateSweep(self, val):
        self._GateSweep = val

    def do_get_ModulateGate(self):
        return self._ModulateGate

    def do_set_ModulateGate(self, val):
        self._ModulateGate = val

    def do_get_DCStart(self):
        return self._DCStart

    def do_set_DCStart(self, val):
        self._DCStart = val

    def do_get_DCStop(self):
        return self._DCStop

    def do_set_DCStop(self, val):
        self._DCStop = val

    def do_get_DCstepsize(self):
        return self._DCstepsize

    def do_set_DCstepsize(self, val):
        self._DCstepsize = val

    def do_get_PulseAOM(self):
        return self._PulseAOM

    def do_set_PulseAOM(self, val):
        self._PulseAOM = val

    def do_get_AutoOptimizeXY(self):
        return self._AutoOptimizeXY

    def do_set_AutoOptimizeXY(self, val):
        self._AutoOptimizeXY = val

    def do_get_AutoOptimizeZ(self):
        return self._AutoOptimizeZ

    def do_set_AutoOptimizeZ(self, val):
        self._AutoOptimizeZ = val

#    def do_get_UsePicoharp(self):
#        return self._UsePicoharp

#    def do_set_UsePicoharp(self, val):
#        self._UsePicoharp = val

    def do_get_OptimizeInterval(self):
        return self._OptimizeInterval

    def do_set_OptimizeInterval(self, val):
        self._OptimizeInterval = val

    def do_get_PulseDuration(self):
        return self._PulseDuration

    def do_set_PulseDuration(self, val):
        self._PulseDuration = val

    def do_get_PowerLevelPulse(self):
        return self._PowerLevelPulse

    def do_set_PowerLevelPulse(self, val):
        self._PowerLevelPulse = val

    def do_get_PowerLevelOn(self):
        return self._PowerLevelOn

    def do_set_PowerLevelOn(self, val):
        self._PowerLevelOn = val

    def do_get_PowerLevelScan(self):
        return self._PowerLevelScan

    def do_set_PowerLevelScan(self, val):
        self._PowerLevelScan = val

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

    def do_get_ModeHopThreshold(self):
        return self._ModeHopThreshold

    def do_set_ModeHopThreshold(self, val):
        self._ModeHopThreshold = val

    def do_get_LaserOn(self):
        if self._ins_Laser.get_output() == 'on':
            self._LaserOn = True
        else:
            self._LaserOn = False
        return self._LaserOn

    def do_set_LaserOn(self, val):
        if val == True:
            self._ins_Laser.set_output('on')
        else:
            self.set_LockFrequency(False)
            self._ins_Laser.set_output('off')
        self._LaserOn = val

    def do_get_MWOn(self):
        if self._ins_MW.get_status() == 'on':
            self._MWOn = True
        else:
            self._MWOn = False
        return self._MWOn

    def do_set_MWOn(self, val):
        if val == True:
            self._ins_MW.set_status('on')
        else:
            self._ins_MW.set_status('off')
        self._MWOn = val

    def do_set_ScanRangeCenter(self, val):
        self.set_ScanVoltage(0)
        self.set_PiezoVoltage(50)
        self._ins_Laser.set_wavelength(637.09115-val*0.00135)

    def do_get_MWfrequency(self):
        self._MWfrequency = self._ins_MW.get_frequency()
        return self._MWfrequency

    def do_set_MWfrequency(self, val):
        self._ins_MW.set_frequency(val)
        self._MWfrequency = val

    def do_get_MWpower(self):
        self._MWpower = self._ins_MW.get_power()
        return self._MWpower

    def do_set_MWpower(self, val):
        self._ins_MW.set_power(val)
        self._MWpower = val

    def do_get_DCGate(self):
        return self._DCGate

    def do_set_DCGate(self, val):
        self._DCGate = val

    def do_get_CurrentFrequency(self):
        self._CurrentFrequency = self._ins_Wavemeter.Get_Frequency(self._WavemeterChannel)*1000
        return self._CurrentFrequency

    def do_get_ScanVoltage(self):
        return self._ScanVoltage

    def do_set_ScanVoltage(self, val):
        self._ins_ADwin.Set_DAC_Voltage(5,val)
        self._ScanVoltage = val

    def do_get_Gate1Voltage(self):
        return self._Gate1Voltage

    def do_set_Gate1Voltage(self, val):
        self._Gate1Voltage = val
        if self._ModulateGate == False:
            self._ins_ADwin.Set_DAC_Voltage(3,val)
        else:
            self._ins_ADwin.Set_Par(80,self._ModulationPeriod)
            self._ins_ADwin.Set_FPar(79,self._Gate1Voltage)
            self._ins_ADwin.Set_FPar(80,self._Gate2Voltage)
            self._ins_ADwin.Stop_Process(5)
            self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\gatemodulation.tb5')
            self._ins_ADwin.Start_Process(5)

    def do_get_Gate2Voltage(self):
        return self._Gate2Voltage

    def do_set_Gate2Voltage(self, val):
        self._Gate2Voltage = val
        if self._ModulateGate == False:
            self._ins_ADwin.Set_DAC_Voltage(6,val)
        else:
            self._ins_ADwin.Set_Par(80,self._ModulationPeriod)
            self._ins_ADwin.Set_FPar(79,self._Gate1Voltage)
            self._ins_ADwin.Set_FPar(80,self._Gate2Voltage)
            self._ins_ADwin.Stop_Process(5)
            self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\gatemodulation.tb5')
            self._ins_ADwin.Start_Process(5)

    def do_get_PiezoVoltage(self):
        return self._PiezoVoltage

    def do_set_PiezoVoltage(self, val):
        self._ins_Laser.set_piezo_voltage(val)
        self._PiezoVoltage = val

    def do_get_LockFrequency(self):
        return self._LockFrequency

    def do_set_LockFrequency(self, val):
        if (val == True) and (self._mode == 0):
            self._mode = 1
            self._LockFrequency = True
            self.set_is_running(True)

        if (val == False) and (self._mode == 1):
            self._mode = 0
            self._LockFrequency = False
            
    def do_get_LockFrequencyDeviation(self):
        return self._LockFrequencyDeviation

    def do_get_FrequencySetpoint(self):
        return self._FrequencySetpoint

    def do_set_FrequencySetpoint(self, val):
        self._FrequencySetpoint = val

    def do_get_FrequencyStep(self):
        return self._FrequencyStep

    def do_set_FrequencyStep(self, val):
        self._FrequencyStep = val

    def PulseAOM_manual(self):
        self._ins_ADwin.Pulse_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelPulse),self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelScan), self._PulseDuration)
        
    def SkipToNext(self):
        self._ins_ADwin.Stop_Process(5)

    def SaveSettings(self):
        settings=open(self.path+'settings.txt', 'w')
        settings.write('Comments:\n%s\n\n\n' %(self._Comments))
        if self._GateSweep == True:
            settings.write('Gatesweep-Measurement\n')
            if self._ModulateGate == True:
                settings.write(' - using gate-modulation between positive and negative bias\n')
            settings.write('sweeping gate %s from %s V to %s V in steps of %s V\n'%(self._DCGate, self._DCStart, self._DCStop, self._DCstepsize))
            settings.write('rel. laser frequency: %s GHz\n'%(self._FrequencySetpoint - self._FrequencyReference))
#            settings.write('laser frequency reference: %s GHz\n'%(self._FrequencyReference))
            settings.write('scan repetitions: %s\n'%self._ScanCount)

        elif self._DCStarkShiftSweep == True:
            settings.write('DC Starkshift-Measurement\n')
            settings.write('sweeping laser voltage from %s V by %s steps of %s V\n'%(self._StartVoltage, self._ScanSteps, self._StepVoltage))
            settings.write('sweeping gate %s from %s V to %s V in steps of %s V\n'%(self._DCGate, self._DCStart, self._DCStop, self._DCstepsize))
        else:
            settings.write('Laserscan-Measurement\n')
            settings.write('scan repetitions: %s\n'%self._ScanCount)
            settings.write('sweeping laser voltage from %s V by %s steps of %s V\n'%(self._StartVoltage, self._ScanSteps, self._StepVoltage))

        settings.write('\n')
        settings.write('integration time: %s ms\n'%self._IntegrationTime)
        settings.write('initial wait: %s s\n'%self._InitialWait)
        settings.write('initialize laser before scan: %s\n'%self._LaserInitialize)
        settings.write('scan back laser after each scan: %s\n'%self._ScanBack)
        settings.write('scan back time: %s s\n'%self._ScanBackTime)
        settings.write('\n')
        settings.write('pulse AOM: %s\n'%self._PulseAOM)
        settings.write('pulse duration: %s microseconds\n'%self._PulseDuration)
        settings.write('power level pulse: %s microWatt\n'%self._PowerLevelPulse)
        settings.write('power level scan: %s microWatt\n'%self._PowerLevelScan)
        settings.write('\n')
        settings.write('wavemeter channel: %s\n'%self._WavemeterChannel)
        settings.write('counter channel: %s\n'%self._CounterChannel)
        settings.write('\n')
        settings.write('frequency averaging: %s data points\n'%self._FrequencyAveraging)
        settings.write('frequency interpolation step: %s MHz\n'%self._FrequencyInterpolationStep)
        settings.write('frequency reference: %s GHz\n'%self._FrequencyReference)
        settings.write('modehop threshold: %s MHz\n'%self._ModeHopThreshold)
        settings.write('\n')
        settings.write('piezo voltage: %s V\n'%self._PiezoVoltage)
        settings.write('gate 1 voltage: %s V\n'%self._Gate1Voltage)
        settings.write('gate 2 voltage: %s V\n'%self._Gate2Voltage)
        settings.write('\n')
        settings.write('optimize interval: %s scans\n'%self._OptimizeInterval)
        settings.write('AutoOptimize XY: %s\n'%self._AutoOptimizeXY)
        settings.write('AutoOptimize Z: %s\n'%self._AutoOptimizeZ)
        settings.write('\n')
        settings.write('MW status: %s\n'%self.get_MWOn())
        settings.write('MW frequency: %s GHz\n'%(self.get_MWfrequency()/1e9) )
        settings.write('MW power: %s dBm\n'%self.get_MWpower())

        settings.write('\n')
        settings.write('Attocube scanner X position: %s micrometer\n'%(qt.instruments['ADwin_pos'].get_X_position()))
        settings.write('Attocube scanner Y position: %s micrometer\n'%(qt.instruments['ADwin_pos'].get_Y_position()))
        settings.write('Attocube scanner Z position: %s micrometer\n'%(qt.instruments['ADwin_pos'].get_Z_position()))
        settings.write('Temperature Sensor A: %s K\n'%(qt.instruments['TemperatureController'].get_kelvinA()))
        settings.write('Temperature Sensor B: %s K\n'%(qt.instruments['TemperatureController'].get_kelvinB()))
        settings.close()
            

    def start_single_gatesweep(self):
        if float(self._ScanIndex) / self._OptimizeInterval  == self._ScanIndex / self._OptimizeInterval:
            if self._AutoOptimizeXY == True:
                self._ins_Setup.OptimizeXY()
            if self._AutoOptimizeZ == True:
                self._ins_Setup.OptimizeZ()

        if self._PulseAOM == True:
            self._ins_ADwin.Pulse_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelPulse),
                    self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelScan), self._PulseDuration)
        else:
            self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelScan))

        time.sleep(0.1)

        self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\python_laser_scan.tb5')

        time.sleep(0.1)

        self._ins_ADwin.Set_Par(1,1)    # DC Gate Sweep
        self._ins_ADwin.Set_Par(2,self._DCGate)    # Gate number
        if self._ModulateGate == True:
            self._ins_ADwin.Set_Par(3,1)    # Modulation mode (0 = off)
        else:
            self._ins_ADwin.Set_Par(3,0)    # Modulation mode (0 = off)
        self._ins_ADwin.Set_FPar(5,self._DCStart)
        self._ins_ADwin.Set_FPar(6,self._DCstepsize)
        self._ins_ADwin.Set_Par(6,self._ScanSteps)
        self._ins_ADwin.Set_Par(5,self._IntegrationTime)
        self._ins_ADwin.Set_Par(7,self._CounterChannel)
        self._ins_ADwin.Set_Par(8,0)    # initialize index
        self._ins_ADwin.Set_Par(9,1)    # acquire data

        print ('Starting gatesweep %s / %s' %(self._ScanIndex+1,self._ScanCount))

        self._trace_index = 0
        self._ins_ADwin.Start_Process(5)
        self.set_sampling_interval(100)
        self.set_is_running(True)
        return True

    def start_single_scan(self):
        print('start single scan')
        if float(self._ScanIndex) / self._OptimizeInterval  == self._ScanIndex / self._OptimizeInterval:
            if (self._CounterChannel <5):
                self._ins_Setup.Newfocus_Laser_Block()
                time.sleep(2)
                self._ins_Setup.Channel_A_Unblock()
                self._ins_Setup.Channel_B_Unblock()
            for opt_ctr in arange(0,self._OptimizeRepetitions):
                if self._AutoOptimizeXY == True:
                    print('optimizing XY...')
                    self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelOn))
                    self._ins_Setup.OptimizeXY(counter = self._OptimizeCounter)
                    self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelScan))
                if self._AutoOptimizeZ == True:
                    print('optimizing Z...')
                    self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelOn))
                    self._ins_Setup.OptimizeZ(counter = self._OptimizeCounter)
                    self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelScan))
            if (self._CounterChannel < 5):
                self._ins_Setup.Channel_A_Block()
                self._ins_Setup.Channel_B_Block()
                time.sleep(2)
                self._ins_Setup.Newfocus_Laser_Unblock()
        if self._DCStarkShiftSweep == True:
            Voltage = self._DCStart + int(self._ScanIndex/self._StarkSweepRepetitions)*self._DCstepsize
            print('setting voltage: %.3f' % Voltage)
            if self._ModulateGate == False:
                if self._DCGate == 1:
                    self._ins_ADwin.Set_DAC_Voltage(3,Voltage)
                    self._ins_ADwin.Set_DAC_Voltage(6,self.get_Gate2Voltage())
                    self._Gate1Voltage = Voltage
                elif self._DCGate == 2:
                    self._ins_ADwin.Set_DAC_Voltage(6,Voltage)
                    self._ins_ADwin.Set_DAC_Voltage(3,self.get_Gate1Voltage())
                    self._Gate2Voltage = Voltage
            else:
                self._ins_ADwin.Set_Par(80,self._ModulationPeriod)
                if self._DCGate == 1:
                    self._ins_ADwin.Set_FPar(79,Voltage)
                    self._ins_ADwin.Set_FPar(80,self._Gate2Voltage)
                    self._Gate1Voltage = Voltage
                elif self._DCGate == 2:
                    self._ins_ADwin.Set_FPar(79,self._Gate1Voltage)
                    self._ins_ADwin.Set_FPar(80,Voltage)
                    self._Gate2Voltage = Voltage
        else:
            if self._ModulateGate == True:
                self._ins_ADwin.Set_Par(80,self._ModulationPeriod)
                self._ins_ADwin.Set_FPar(79,self._Gate1Voltage)
                self._ins_ADwin.Set_FPar(80,self._Gate2Voltage)

        time.sleep(0.1)
        if self._PulseAOM == True:
            self._ins_ADwin.Pulse_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelPulse),
                    self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelScan), self._PulseDuration)
        else:
            self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelScan))

        time.sleep(0.1)
        self._ins_ADwin.Set_DAC_Voltage(5,self._StartVoltage)

        print('Initial wait...')
        time.sleep(self._InitialWait)

        self._ins_ADwin.Stop_Process(5)
        self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\python_laser_scan.tb5')

        self._ins_ADwin.Set_Par(1,0)    # Laser Sweep
        self._ins_ADwin.Set_FPar(5,self._StartVoltage)
        self._ins_ADwin.Set_FPar(6,self._StepVoltage)
        self._ins_ADwin.Set_Par(6,self._ScanSteps)
        self._ins_ADwin.Set_Par(5,self._IntegrationTime)
        self._ins_ADwin.Set_Par(7,self._CounterChannel)
        self._ins_ADwin.Set_Par(8,0)
        self._ins_ADwin.Set_Par(9,1) # store and display data
        if self._ModulateGate == True:
            self._ins_ADwin.Set_Par(3,1)    # Modulation mode (0 = off)
        else:
            self._ins_ADwin.Set_Par(3,0)    # Modulation mode (0 = off)

        print ('Starting laserscan %s / %s' %(self._ScanIndex+1,self._ScanCount))

        self._trace_index = 0
        self._ins_ADwin.Start_Process(5)
#        self.set_sampling_interval(self._IntegrationTime)
        self.set_sampling_interval(100)
        self.set_is_running(True)
        return True

    def end_single_gatesweep(self):
        counts    = self._ins_ADwin.Get_Data_Long(5,1,self._ScanSteps)

        if self._ModulateGate == 1:
            self._counts_a = zeros(int(self._ScanSteps/2))
            self._counts_b = zeros(int(self._ScanSteps/2))
            if (self._ScanIndex == 0):
                self._scan2D_a = zeros((self._ScanCount,int(self._ScanSteps/2)))
                self._scan2D_b = zeros((self._ScanCount,int(self._ScanSteps/2)))
            for j in range(int(self._ScanSteps/2)):
                self._counts_a[j] = counts[2 * j]
                self._counts_b[j] = counts[2 * j + 1]
            self._scan2D_a[self._ScanIndex] = self._counts_a
            self._scan2D_b[self._ScanIndex] = self._counts_b

            bias_a = arange(self._DCStart,self._DCStart+len(self._counts_a)*2*self._DCstepsize, self._DCstepsize)
            bias_b = (bias_a + self._DCstepsize) * (-1)

            result_a=open(self.path+'gatesweep'+str(self._ScanIndex)+'a.txt', 'w')
            result_b=open(self.path+'gatesweep'+str(self._ScanIndex)+'b.txt', 'w')
            for j in range(int(len(counts)/2)):
                result_a.write('%.2f\t%.2f\n' % (bias_a[j], self._counts_a[j]))
                result_b.write('%.2f\t%.2f\n' % (bias_b[j], self._counts_b[j]))
            result_a.close()
            result_b.close()
            
            fig = plt.figure()
            dat = fig.add_subplot(111)
#            dat = dat.plot(bias_a, self._counts_a, 'r.')
            plt.xlabel('gate %s bias (V)'%self._DCGate)
            plt.ylabel('counts')
            plt.title('gatesweep scan #'+str(self._ScanIndex)+' (even)')
            fig.savefig(self.path+'gatesweep'+str(self._ScanIndex)+'a.png')

            fig = plt.figure()
            dat = fig.add_subplot(111)
#            dat = dat.plot(bias_b, self._counts_b, 'b.')
            plt.xlabel('gate %s bias (V)'%self._DCGate)
            plt.ylabel('counts')
            plt.title('gatesweep scan #'+str(self._ScanIndex)+' (odd)')
            fig.savefig(self.path+'gatesweep'+str(self._ScanIndex)+'b.png')
        else:
            if (self._ScanIndex == 0):
                self._scan2D = zeros((self._ScanCount,self._ScanSteps))
            self._counts = counts
            self._scan2D[self._ScanIndex] = counts
            bias = arange(self._DCStart,self._DCStart+len(counts)*self._DCstepsize, self._DCstepsize)

            result=open(self.path+'gatesweep'+str(self._ScanIndex)+'.txt', 'w')
            for j in range(len(counts)):
                result.write('%.2f\t%.2f\n' % (bias[j], counts[j]))
            result.close()

            fig = plt.figure()
            dat = fig.add_subplot(111)
            dat = dat.plot(bias, counts, 'r.')

            plt.xlabel('gate %s bias (V)'%self._DCGate)
            plt.ylabel('counts')
            plt.title('gatesweep scan #'+str(self._ScanIndex))
            fig.savefig(self.path+'gatesweep'+str(self._ScanIndex)+'.png')
            
        self.set_ScanIndex (self.get_ScanIndex()+1)
        if self._ScanIndex < self._ScanCount:
            self.start_single_gatesweep()
        else:
            self.end_gatesweep()

    def end_gatesweep(self):
        print ('Finishing gatesweep')
        if self._ModulateGate == 0:
            result=open(self.path+'gatesweep2D.txt', 'w')
            for j in range(self._ScanSteps):
                for k in range(self._ScanCount):
                    result.write('%.2f'%(self._scan2D[k][j]))
                    if k < self._ScanCount-1:
                        result.write('\t')
                result.write('\n')
            result.close()

            fig = plt.figure()
            dat = fig.add_subplot(111)
        
            plt.xlabel('scan number')
            x = linspace(0,self._ScanCount+1)
    
            y = linspace(self._DCStart,self._DCStop,self._ScanSteps+1)
            
#            dat = dat.pcolor(x, y, transpose(self._scan2D), cmap = 'gray')
            
            plt.ylabel('gate voltage (V)')
            plt.title('gate sweep, %s ms step time'%(self._IntegrationTime))
            
            #plt.show()
            fig.savefig(self.path+'gatesweep2D.png')
        else:
            result_a=open(self.path+'gatesweep2D_a.txt', 'w')
            result_b=open(self.path+'gatesweep2D_b.txt', 'w')
            for j in range(int(self._ScanSteps/2)):
                for k in range(self._ScanCount):
                    result_a.write('%.2f'%(self._scan2D_a[k][j]))
                    result_b.write('%.2f'%(self._scan2D_b[k][j]))
                    if k < self._ScanCount-1:
                        result_a.write('\t')
                        result_b.write('\t')
                result_a.write('\n')
                result_b.write('\n')
            result_a.close()
            result_b.close()

            fig = plt.figure()
            dat = fig.add_subplot(111)
        
            plt.xlabel('scan number')
            x = linspace(0,self._ScanCount+1)
    
            y = linspace(self._DCStart,self._DCStop,int(self._ScanSteps/2)+1)
            
#            dat = dat.pcolor(x, y, transpose(self._scan2D), cmap = 'gray')
            
            plt.ylabel('gate voltage (V)')
            plt.title('gate sweep (even), %s ms step time'%(self._IntegrationTime))
            
            #plt.show()
            fig.savefig(self.path+'gatesweep2D_a.png')

            fig = plt.figure()
            dat = fig.add_subplot(111)
        
            plt.xlabel('scan number')
            x = linspace(0,self._ScanCount+1)
    
            y = linspace(0-self._DCStart,0-self._DCStop,int(self._ScanSteps/2)+1)
            
#            dat = dat.pcolor(x, y, transpose(self._scan2D), cmap = 'gray')
            
            plt.ylabel('gate voltage (V)')
            plt.title('gate sweep (odd), %s ms step time'%(self._IntegrationTime))
            
            #plt.show()
            fig.savefig(self.path+'\\gatesweep2D_a.png')

        self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\simple_counting.tb4')
        self._ins_ADwin.Set_Par(24,100)
        self._ins_ADwin.Start_Process(4)
        self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelOn))
        self._mode = 0
        print ('Gate sweep finished')
        self.set_sampling_interval(100)
        self.set_is_running(True)
        #self.SaveSettings()
        return True

    def end_single_scan(self):
       
        counts    = self._ins_ADwin.Get_Data_Long(5,1,self._ScanSteps)
        frequency = self._ins_ADwin.Get_Data_Float(6,1,self._ScanSteps)

        #for i in range(1,self._ScanSteps-1):
        #    if frequency[i] == 0:
        #        k = 0
        #        while frequency[i+k] == 0:
        #            k += 1
        #
        #        if frequency[i-1]==0:
        #            frequency[i-1] = frequency[i+k+1]

        #        if frequency[i+k+1] == 0:
        #            frequency[i+k+1] = frequency[i-1]

        #        for l in range(i, i+k):
        #            frequency[l] = frequency[i-1]+(frequency[i+k+1]-frequency[i-1])/(k+1)*(l-i+1)



        self._ins_ADwin.Set_Par(9,0) # don't store and display data
        if (self._ScanBack == 1):
            self._ins_ADwin.Set_FPar(5,self._StartVoltage+self._ScanSteps*self._StepVoltage)
            self._ins_ADwin.Set_FPar(6,-(self._StepVoltage*self._ScanSteps/self._ScanBackTime/100))
            self._ins_ADwin.Set_Par(6,ctypes.c_int(int(self._ScanBackTime*100)))
            self._ins_ADwin.Set_Par(5,10)

            print('Scanning back')
            self._ins_ADwin.Start_Process(5)
            while (self._ins_ADwin.Process_Status(5) > 0):
                time.sleep(.1)

        if self._ModulateGate == True:
            self._ins_ADwin.Set_Par(80,self._ModulationPeriod)
            self._ins_ADwin.Set_FPar(79,self._Gate1Voltage)
            self._ins_ADwin.Set_FPar(80,self._Gate2Voltage)
            self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\gatemodulation.tb5')
            self._ins_ADwin.Start_Process(5)
    
        frequency = frequency*1000000-self._FrequencyReference*1000

        # Identify modehops:
        ModeHopCount = 0
        ModeHopList = arange(0)
        for k in arange(0,self._ScanSteps-1):
            if abs(frequency[k+1]-frequency[k])>self._ModeHopThreshold:
                #print('Modehop at index %s: %s MHz to %s MHz'%(k,frequency[k],frequency[k+1]))
                ModeHopList = append(ModeHopList,k)
                ModeHopCount += 1

        # Do frequency-smoothing only for ranges between modehops:
        if self._FrequencyAveraging > 1:
            frequency_temp = array(zeros(self._ScanSteps,float))

            for k in arange(0,ModeHopList.size+1):
                if k == ModeHopList.size:
                    m = self._ScanSteps
                else:
                    m = ModeHopList[k]+1
                if k == 0:
                    l = 0
                else:
                    l = ModeHopList[k-1]+1
    
                if m-l < self._FrequencyAveraging:
                    for n in arange(l,m):
                        frequency_temp[n] = 0
                else:
                    for n in arange(l,m-self._FrequencyAveraging+1):
                        if (n >= self._FrequencyAveraging/2) and (n < self._ScanSteps - self._FrequencyAveraging/2):
                            for o in arange(0, self._FrequencyAveraging):
                                frequency_temp[n] += frequency[n+o-self._FrequencyAveraging/2] / self._FrequencyAveraging
                        else:
                            frequency_temp[n] = frequency[n]

            frequency = frequency_temp


        # Distribute counts over linear frequency array:
        min_freq = min(frequency)
        if min_freq == 0:
            for k in arange(0, self._ScanSteps):
                if (frequency[k] > 0) and ((min_freq == 0) or (frequency[k] < min_freq)):
                    min_freq = frequency[k]

        max_freq = max(frequency)
        if max_freq == 0:
            for k in arange(0, self._ScanSteps):
                if (frequency[k] < 0) and ((max_freq == 0) or (frequency[k] > max_freq)):
                    max_freq = frequency[k]
        max_freq = int(max_freq)
        min_freq = int(min_freq)

        interpol_size = (max_freq - min_freq)/self._FrequencyInterpolationStep+1
        interpol_cts = zeros(interpol_size)
        interpol_frq = arange(0, interpol_size) * self._FrequencyInterpolationStep + min_freq
        interpol_weight = zeros(interpol_size)
    
        for n in arange(0,self._ScanSteps):
            if frequency[n] != 0:
                index = int((frequency[n]-min_freq)/self._FrequencyInterpolationStep)
                interpol_cts[index] += counts[n]
                interpol_weight[index] += 1
            
        for n in arange(0,interpol_size):
            if interpol_weight[n] > 0:
                interpol_cts[n] = interpol_cts[n] / interpol_weight[n]

        for n in arange(1,interpol_size-1):
            if interpol_weight[n] == 0:
                interpol_cts[n] = (interpol_cts[n-1] + interpol_cts[n+1])/2     # to prevent empty bins due to frequency rounding
                                                                                # but scan steps should be smaller than interpolation size
    #NOTE: If the interpolation step is much smaller than the scan step, 
    #then this procedure will give you data divided by an integer number!  
    #If you see this problem, you need to increase the interpolation step or decrease the frequency step.

    
        if (self._ScanIndex == 0):
            self._scan2D = zeros((self._ScanCount,interpol_size))
            self._interpol_size_2D = interpol_size
            self._base2D = interpol_frq[0]
        offset = (interpol_frq[0]-self._base2D)/self._FrequencyInterpolationStep
        fitted_data = zeros(self._interpol_size_2D)
        if offset >= 0:
            if self._interpol_size_2D - offset < interpol_size:
                for n in arange(0,self._interpol_size_2D-offset):
                    fitted_data[n+offset] = interpol_cts[n]
            else:
                for n in arange(0,interpol_size):
                    fitted_data[n+offset] = interpol_cts[n]
        else:
            if self._interpol_size_2D + offset < interpol_size:
                for n in arange(0,self._interpol_size_2D+offset):
                    fitted_data[n] = interpol_cts[n+offset]
            else:
                for n in arange(0,interpol_size):
                    fitted_data[n] = interpol_cts[n+offset]
            
        self._counts = counts
        self._frequency = frequency
        self._scan2D[self._ScanIndex] = fitted_data

        if self._reuse_path == False:
            result=open(self.path+'scan'+str(self._ScanIndex)+'.txt', 'w')
        else:
            result=open(self.path+'scan'+str(self._save_index)+'_'+str(self._ScanIndex)+'.txt', 'w')

        for j in range(len(interpol_cts)):
#            if interpol_cts[j]>0:
            result.write('%.2f\t%.2f\n' % (interpol_frq[j], interpol_cts[j]))
        result.close()

        
        if self._reuse_path == False:
            result=open(self.path+'scan'+str(self._ScanIndex)+'_raw.txt', 'w')
        else:
            result=open(self.path+'scan'+str(self._save_index)+'_'+str(self._ScanIndex)+'_raw.txt', 'w')

        for j in arange(0,self._ScanSteps-1):
            result.write('%.2f\t%.2f\n' % (frequency[j], counts[j]))
        result.close()

        if self._reuse_path == False:
            result=open(self.path+'scan'+str(self._ScanIndex)+'_parameters.txt', 'w')
        else:
            result=open(self.path+'scan'+str(self._save_index)+'_'+str(self._ScanIndex)+'_parameters.txt', 'w')
        result.write('# position x[mu_m], y[mu_m], z[mu_m]\n')
        result.write('%.2f\t%.2f\t%.2f\n\n' % (qt.instruments['ADwin_pos'].get_X_position(),qt.instruments['ADwin_pos'].get_Y_position(),qt.instruments['ADwin_pos'].get_Z_position()))
        result.write('# temperature SensorA [K], SensorB [K], LabTemperature [K]\n')
        result.write('%.3f\t%.3f\t%.3f\n\n' % (qt.instruments['TemperatureController'].get_kelvinA(),qt.instruments['TemperatureController'].get_kelvinB(),qt.instruments['wavemeter'].get_temperature()+273.15))
        if self._ModulateGate == True:
            result.write('# bias Gate1 [V], Gate2 [V] (modulated +V/-V with %s mu_s period)\n'%(self._ModulationPeriod))
        else:
            result.write('# DC bias Gate1 [V], Gate2 [V]\n')
        result.write('%.3f\t%.3f\n' % (self.get_Gate1Voltage(),self.get_Gate2Voltage()))
        result.write('# time\n')
        result.write(time.strftime('%H%M%S', time.localtime()))


        result.close()

#        fig = plt.figure()
#        dat = fig.add_subplot(111)
##        dat = dat.plot(frequency/1000, counts, 'r.')
#        dat = dat.plot(interpol_frq/1000.0, interpol_cts, 'r.')

#        plt.xlabel('rel. frequency (GHz)')
#        plt.ylabel('counts')
#        plt.title('PLE scan #'+str(self._ScanIndex))

#        fig.savefig(self.path+'scan'+str(self._ScanIndex)+'.png')
            
        self.set_ScanIndex (self.get_ScanIndex()+1)
        if self._ScanIndex < self._ScanCount:
            self.start_single_scan()
        else:
            self.end_scan()


    # public functions
    def start_scan(self):
        self.save_cfg()
        if self._mode > 1:
            return False

        self.set_is_running(False)


        self._ins_Setup.set_PowermeterPosition('out')
        self._ins_Setup.Millennia_Laser_Unblock()
        if (self._CounterChannel == 5):
            self._ins_Setup.Newfocus_Laser_Unblock()
        else:
            self._ins_Setup.Channel_A_Block()
            self._ins_Setup.Channel_B_Block()
            time.sleep(3)
            self._ins_Setup.Newfocus_Laser_Unblock()
        self._ins_Setup.set_AOMonADwin(True)

        if self._reuse_path == False:
            self.path = qt.config['datadir'] + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_Laserscan\\'
            if not os.path.isdir(self.path):
                os.makedirs(self.path)
        self.SaveSettings()

        if self._GateSweep == True:
            if (self._LockFrequency == False):
                print('Warning - laser frequency not locked')
#                self._mode = 0
#                return False
            self._mode = 5
            self._ins_ADwin.Stop_Process(4)
            self.set_ScanSteps(int((self._DCStop-self._DCStart)/self._DCstepsize + 1))
            self.set_ScanIndex (0)
            self.set_TraceFinished(-1)
            self.start_single_gatesweep()
            return True

        else:
            self.set_LockFrequency(False)
            self._mode = 2

            self._ins_ADwin.Stop_Process(4)
            if (self._LaserInitialize == 1):
                self._ins_ADwin.Set_DAC_Voltage(5,0)
                self._ins_Laser.set_piezo_voltage(50)

            if (self._DCStarkShiftSweep == 1):
                self.set_ScanCount(int((self._DCStop-self._DCStart)/self._DCstepsize + 1)*self._StarkSweepRepetitions)
#            self._ins_ADwin.Set_DAC_Voltage(6,self._GateB_Bias)
    
            self.set_ScanIndex (0)
            self.set_TraceFinished(-1)
            self.start_single_scan()
            return True

    def pause_scan(self):
        if self._mode == 2:
            self._ins_ADwin.Set_Par(4,1)
            self._ins_ADwin.Set_Par(9,0)
            self._mode = 3
        elif self._mode == 3:
            self._ins_ADwin.Set_Par(4,0)
            self._ins_ADwin.Set_Par(9,1)
            self._mode = 2
        elif self._mode == 5:
            self._ins_ADwin.Set_Par(4,1)
            self._ins_ADwin.Set_Par(9,0)
            self._mode = 6
        elif self._mode == 6:
            self._ins_ADwin.Set_Par(4,0)
            self._ins_ADwin.Set_Par(9,1)
            self._mode = 5
        return True

    def abort_scan(self):
        self._ins_ADwin.Set_Par(4,0)
        if (self._mode >= 2) and (self._mode <= 4):
            self.set_is_running(False)
            self._ins_ADwin.Stop_Process(5)
            self._ins_ADwin.Set_Par(9,0)
            self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\simple_counting.tb4')
            self._ins_ADwin.Start_Process(4)
            self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelOn))
            self._mode = 0
            print ('Laser scan aborted  ')
            if self._ModulateGate == True:
                self._ins_ADwin.Set_Par(80,self._ModulationPeriod)
                self._ins_ADwin.Set_FPar(79,self._Gate1Voltage)
                self._ins_ADwin.Set_FPar(80,self._Gate2Voltage)
                self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\gatemodulation.tb5')
                self._ins_ADwin.Start_Process(5)
            self.set_sampling_interval(100)
            self.set_is_running(True)
        if (self._mode == 5) or (self._mode == 6):
            self.set_is_running(False)
            self._ins_ADwin.Stop_Process(5)
            self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\simple_counting.tb4')
            self._ins_ADwin.Start_Process(4)
            self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelOn))
            self._mode = 0
            print ('Gate sweep aborted  ')
            self.set_sampling_interval(100)
            self.set_is_running(True)
        self._ins_Setup.Newfocus_Laser_Block()
        time.sleep(2)
        self._ins_Setup.Channel_A_Unblock()
        self._ins_Setup.Channel_B_Unblock()
        return True

    def end_scan(self):
        self._ins_Setup.Newfocus_Laser_Block()
        time.sleep(2)
        self._ins_Setup.Channel_A_Unblock()
        self._ins_Setup.Channel_B_Unblock()
        result=open(self.path+'scan2D.txt', 'w')
        for j in range(self._interpol_size_2D):
            for k in range(self._ScanCount):
                result.write('%.2f'%(self._scan2D[k][j]))
                if k < self._ScanCount-1:
                    result.write('\t')
            result.write('\n')
        result.close()


#        fig = plt.figure()
#        dat = fig.add_subplot(111)
#        
#        if (self._DCStarkShiftSweep == 0):
#            plt.xlabel('scan number')
#            x = linspace(0,self._ScanCount,self._ScanCount+1)
#        else:
#            plt.xlabel('gate voltage (V)')
#            x = linspace(self._DCStart,self._DCStop,self._ScanCount+1)
#
#        y = linspace(self._base2D/1000.0,(self._base2D+self._interpol_size_2D*self._FrequencyInterpolationStep)/1000.0,self._interpol_size_2D+1)
#        
#        dat = dat.pcolor(x, y, transpose(self._scan2D), cmap = 'gray')
#        
#        plt.ylabel('rel. frequency (GHz)')
#        plt.title('2D laser scan: %s MHz step size, %s ms step time'%(self._FrequencyInterpolationStep,self._IntegrationTime))
#        
#        #plt.show()
#        fig.savefig(self.path+'scan2D.png')

        self._ins_ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\simple_counting.tb4')
        self._ins_ADwin.Set_Par(24,100)
        self._ins_ADwin.Start_Process(4)
        self._ins_ADwin.Set_DAC_Voltage(4,self._ins_Setup.GreenAOMPowerToADwinVoltage(self._PowerLevelOn))
        self._mode = 0
        print ('Laser scan finished')
        #self.SaveSettings()
        self.set_sampling_interval(100)
        self.set_is_running(True)
        self._ins_ADwin.Set_Par(59,0)
        return True

    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)

    def _sampling_event(self):
        if not self._is_running:
            return False

        if (self._mode == 1) or (self._mode == 5):
            diff = self.get_CurrentFrequency() - self.get_FrequencySetpoint()
            setp = self.get_ScanVoltage()+diff*(0.01)
            self.set_ScanVoltage(setp)
            self._deviation_record[self._deviation_counter] = diff * 1000.0
            self._deviation_counter += 1
            if self._deviation_counter == 100:
                self._deviation_counter = 0

            deviation = 0
            for i in arange(0,100):
                deviation += (self._deviation_record[i])**2
            self._LockFrequencyDeviation = sqrt(deviation/100.0)   
        if (self._mode == 2) or (self._mode == 5):
            if (self._ins_ADwin.Process_Status(5) > 0):
                self._ins_ADwin.Set_FPar(7,self._ins_Wavemeter.Get_Frequency(self._WavemeterChannel))
            else:
                self.set_is_running(False)

            current_index = self._ins_ADwin.Get_Par(8)
#            print current_index
            if current_index > self._trace_index:
                counts    = self._ins_ADwin.Get_Data_Long(5,self._trace_index + 1,current_index - self._trace_index)
                frequency = self._ins_ADwin.Get_Data_Float(6,self._trace_index + 1,current_index - self._trace_index)

                if self._trace_index == 0:
                    self._current_frequency_trace = frequency
                    self._current_counts_trace = counts
                else:
                    self._current_frequency_trace = append(self._current_frequency_trace, frequency)
                    self._current_counts_trace    = append(self._current_counts_trace ,   counts)

                self.set_TraceIndex(current_index)

            if (self._ins_ADwin.Process_Status(5) == 0):
                if self._ScanIndex == 0:
                    self._frequency_traces = [self._current_frequency_trace]
                    self._counts_traces = [self._current_counts_trace]
                else:
                    self._frequency_traces.append(self._current_frequency_trace)
                    self._counts_traces.append(self._current_counts_trace)
                self.set_TraceFinished(self._ScanIndex)
                if self._mode == 2:
                    self.end_single_scan()
                else:
                    self.end_single_gatesweep()
            
        return True

    def data_frequency_trace(self,trace,start,length = 0):
        if self._trace_finished >= trace:
            if length == 0:
                start = 0
                length = len(self._frequency_traces[trace])
                print (' DF1 Length: %s'%length)
            return self._frequency_traces[trace][start:start+length].tolist()
        else:
            if length == 0:
                start = 0
                length = len(self._frequency_trace)
                print (' DF2 Length: %s'%length)
            return self._current_frequency_trace[start:start+length].tolist()

    def data_counts_trace(self,trace,start,length = 0):
        if self._trace_finished >= trace:
            if length == 0:
                start = 0
                length = len(self._counts_traces[trace])
                print (' DC1 Length: %s'%length)
            return self._counts_traces[trace][start:start+length].tolist()
        else:
            if length == 0:
                start = 0
                length = len(self._counts_trace)
                print (' DC2 Length: %s'%length)
            return self._current_counts_trace[start:start+length].tolist()

#    def current_data2D(self):
#        data = self._scan2D[0:max(2,self._trace_finished+1)][:]
#        data = data.tolist()
#        return data, range(0,max(2,self._trace_finished+1)), range(0, self._interpol_size_2D)

    def partial_data2D(self,trace,start,length = 0):
        if length == 0:
            start = 0
            length = len(self._scan2D[trace])
            print (' ** Length: %s'%length)
        data = zeros(length)
        return data.tolist()
        return self._scan2D[trace][start:start+length].tolist()

    def data2D_size(self):
        print (' **** Length: %s'%(len(self._scan2D[0])))
        return len(self._scan2D[0])

