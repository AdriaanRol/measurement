from ctypes import *
import os
from instrument import Instrument
import pickle
from time import sleep, time
import types
import logging
import numpy
import qt
from qt import *
from numpy import *
from data import Data

class Attocube_ANC350(Instrument): #1
    '''
    This is the driver for the Attocube ANC_350 controller

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'Attocube_ANC350')
    
    status:
     1) create this driver!=> is never finished
    TODO:
    '''

    def __init__(self, name): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument ANC_350')
        Instrument.__init__(self, name, tags=['physical'])

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)

#        self.add_parameter('Wavelength', flags = Instrument.FLAG_GET, type=types.FloatType)
#        self.add_parameter('Frequency', flags = Instrument.FLAG_GET, type=types.FloatType)

    def _load_dll(self): #3
        print __name__ +' : Loading hvpositionerv2.dll'
        path = os.getcwd()
        os.chdir(os.path.split(qt.config['anc350_dll'])[0])
        self._attodll = windll.LoadLibrary(qt.config['anc350_dll'])
        os.chdir(path)
        #self._wlmData.GetWavelengthNum.restype = c_double
        #self._wlmData.GetFrequencyNum.restype = c_double
        #self._wlmData.GetTemperature.restype = c_double
        self._device = c_int(0)
        status = self._attodll.PositionerConnect(0,byref(self._device))
        sleep(0.02)

    def PositionerGetPosition(self,axis):
        Position = c_int(0)
        self._attodll.PositionerGetPosition(self._device,c_int(axis),byref(Position))
        return Position.value

    def PositionerGetReference(self,axis):
        Position = c_int(0)
        Valid = c_int(0)
        self._attodll.PositionerGetReference(self._device,c_int(axis),byref(Position),byref(Valid))
        return Position.value, Valid.value

    def PositionerResetPosition(self,axis):
        self._attodll.PositionerResetPosition(self._device,c_int(axis))

    def PositionerGetStatus(self,axis):
        Status = c_int(0)
        self._attodll.PositionerGetStatus(self._device,c_int(axis),byref(Status))
        return Status.value

    def PositionerSetOutput(self,status):
        self._attodll.PositionerSetOutput(self._device,c_int(status))

    def PositionerDcInEnable(self,axis,status):
        self._attodll.PositionerDcInEnable(self._device,c_int(axis),c_int(status))

    def PositionerAcInEnable(self,axis,status):
        self._attodll.PositionerAcInEnable(self._device,c_int(axis),c_int(status))

    def PositionerIntEnable(self,axis,status):
        self._attodll.PositionerIntEnable(self._device,c_int(axis),c_int(status))

    def PositionerBandwidthLimitEnable(self,axis,status):
        self._attodll.PositionerBandwidthLimitEnable(self._device,c_int(axis),c_int(status))

    def PositionerGetDcInEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetDcInEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def PositionerGetAcInEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetAcInEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def PositionerGetIntEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetIntEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def PositionerGetBandwidthLimitEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetBandwidthLimitEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def PositionerCapMeasurement(self,axis):
        Capacity = c_int(0)
        self._attodll.PositionerCapMeasure(self._device,c_int(axis),byref(Capacity))
        return Capacity.value

    def PositionerMoveAbsolute(self,axis,position,rotCount):
        self._attodll.PositionerMoveAbsolute(self._device,c_int(axis),c_int(position),c_int(rotCount))

    def PositionerMoveRelative(self,axis,distance,rotCount):
        self._attodll.PositionerMoveRelative(self._device,c_int(axis),c_int(distance),c_int(rotCount))

    def PositionerMoveReference(self,axis):
        self._attodll.PositionerMoveReference(self._device,c_int(axis))

    def PositionerStopDetection(self,axis,status):
        self._attodll.PositionerStopDetection(self._device,c_int(axis),c_int(status))

    def PositionerSetStopDetectionSticky(self,axis,status):
        self._attodll.PositionerMoveReference(self._device,c_int(axis),c_int(status))

    def PositionerClearStopDetection(self,axis):
        self._attodll.PositionerClearStopDetection(self._device,c_int(axis))

    def PositionerSetTargetGround(self,axis,status):
        self._attodll.PositionerSetTargetGround(self._device,c_int(axis),c_int(status))

    def PositionerAmplitudeControl(self,axis,mode):
        self._attodll.PositionerAmplitudeControl(self._device,c_int(axis),c_int(mode))

    def PositionerAmplitude(self,axis,amplitude):
        self._attodll.PositionerAmplitude(self._device,c_int(axis),c_int(amplitude))

    def PositionerGetAmplitude(self,axis):
        Amplitude = c_int(0)
        self._attodll.PositionerGetAmplitude(self._device,c_int(axis),byref(Amplitude))
        return Amplitude.value

    def PositionerGetSpeed(self,axis):
        Speed = c_int(0)
        self._attodll.PositionerGetSpeed(self._device,c_int(axis),byref(Speed))
        return Speed.value

    def PositionerGetStepwidth(self,axis):
        Stepwidth = c_int(0)
        self._attodll.PositionerGetStepwidth(self._device,c_int(axis),byref(Stepwidth))
        return Stepwidth.value

    def PositionerMoveSingleStep(self,axis,dir):
        self._attodll.PositionerMoveSingleStep(self._device,c_int(axis),c_int(dir))

    def PositionerMoveContinuous(self,axis,dir):
        self._attodll.PositionerMoveContinuous(self._device,c_int(axis),c_int(dir))

    def PositionerStopMoving(self,axis):
        self._attodll.PositionerStopMoving(self._device,c_int(axis))

    def PositionerStepCount(self,axis,stepCount):
        self._attodll.PositionerMoveContinuous(self._device,c_int(axis),c_int(stepCount))

    def PositionerFrequency(self,axis,frequency):
        self._attodll.PositionerFrequency(self._device,c_int(axis),c_int(frequency))

    def PositionerGetFrequency(self,axis):
        Frequency = c_int(0)
        self._attodll.PositionerGetFrequency(self._device,c_int(axis),byref(Frequency))
        return Frequency.value

    def PositionerDCLevel(self,axis,level):
        self._attodll.PositionerDCLevel(self._device,c_int(axis),c_int(level))


