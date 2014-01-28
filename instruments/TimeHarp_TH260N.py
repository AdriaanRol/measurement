from ctypes import *
import os
from instrument import Instrument
import pickle
from time import sleep, time, strftime
import types
import logging
import numpy
import qt
from qt import *
from numpy import *
from measurement.lib.cython.hh_optimize import hht4

LIB_VERSION = "1.1"
DRIVER = 'th260lib'
MAXDEVNUM	  = 4		      # max num of USB devices
THMAXCHAN   = 2		      # max num of logical channels
MAXBINSTEPS	= 22	      # get actual number via TH_GetBaseResolution) !
MAXHISTLEN  = 5  	    # max number of histogram bins= 1024*2**MAXHISTLEN
MAXLENCODE  = 5	    	  # max length code histo mode
MAXHISTLEN_CONT	= 8192	# max number of histogram bins in continuous mode
MAXLENCODE_CONT	= 3	  	# max length code in continuous mode
TTREADMAX   = 131072    # 128K event records can be read in one chunk
MODE_HIST                   = 0
MODE_T2                     = 2
MODE_T3                     = 3
MODE_CONT                   = 8
MEASCTRL_SINGLESHOT_CTC     = 0 # default
MEASCTRL_C1_GATE		        = 1
MEASCTRL_C1_START_CTC_STOP  = 2
MEASCTRL_C1_START_C2_STOP   = 3

#continuous mode only
MEASCTRL_CONT_EXTTRIG       = 5
MESACTRL_CONT_CTCTRIG       = 6

EDGE_RISING                 = 1
EDGE_FALLING                = 0

FLAG_OVERFLOW               = 0x0001  #histo mode only
FLAG_FIFOFULL               = 0x0002  
FLAG_SYNC_LOST              = 0x0004  
FLAG_REF_LOST               = 0x0008  
FLAG_SYSERROR               = 0x0010  #hardware error, must contact support

SYNCDIVMIN                  = 1
SYNCDIVMAX                  = 8

DISCRMIN                    = -1200 	      # mV
DISCRMAX                    = 1200		    # mV 

CHANOFFSMIN                 = -99999	    # ps
CHANOFFSMAX                 = 99999		    # ps

OFFSETMIN                   =	0			      # ps
OFFSETMAX                   =	100000000      # ps 
ACQTMIN	                    = 1			      # ms
ACQTMAX	                    =	360000000	  # ms  (100*60*60*1000ms = 100h)

STOPCNTMIN                  = 1
STOPCNTMAX                  = 4294967295  # 32 bit is mem max

#The following are bitmasks for return values from GetWarnings()

WARNING_SYNC_RATE_ZERO      = 0x0001
WARNING_SYNC_RATE_TOO_LOW   = 0x0002
WARNING_SYNC_RATE_TOO_HIGH  = 0x0004

WARNING_INPT_RATE_ZERO      = 0x0010
WARNING_INPT_RATE_TOO_HIGH  = 0x0040

WARNING_INPT_RATE_RATIO     = 0x0100
WARNING_DIVIDER_GREATER_ONE = 0x0200
WARNING_TIME_SPAN_TOO_SMALL = 0x0400
WARNING_OFFSET_UNNECESSARY  = 0x0800
WARNING_DIVIDER_TOO_SMALL   = 0x1000
WARNING_COUNTS_DROPPED      = 0x2000

class TimeHarp_TH260N(Instrument): #1
    '''
    This is the driver for the TimeHarp 260 NANO Time Correlated Single Photon Counting module

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'TimeHarp_TH260N', DeviceIndex = [default:0] )
    
    status:
     1) Histogramming mode tested
    TODO:
     2) Test T2/T3 modes
    '''
    def __init__(self, name, DeviceIndex = 0): #2
        # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument TH260')
        Instrument.__init__(self, name, tags=['physical'])
        self.adwin = qt.instruments['adwin']

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)

        LibraryVersion = numpy.array([8*' '])
        self._TH260.TH260_GetLibraryVersion(LibraryVersion.ctypes.data)
        self.LibraryVersion = LibraryVersion
        if LibraryVersion[0][0:3] != LIB_VERSION:
            logging.warning(__name__ + ' : DLL Library supposed to be ver.'+LIB_VERSION+' but found ' + LibraryVersion[0] + 'instead.')
#        print ('HydraHarp DLL version %s loaded...'%str(LibraryVersion))

        self.add_parameter('Range', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('Offset', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=OFFSETMIN, maxval=OFFSETMAX)
        self.add_parameter('SyncDiv', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=SYNCDIVMIN, maxval=SYNCDIVMAX)
        self.add_parameter('ResolutionPS', flags = Instrument.FLAG_GET, type=types.FloatType)
        self.add_parameter('BaseResolutionPS', flags = Instrument.FLAG_GET, type=types.FloatType)
        self.add_parameter('MaxBinSteps', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('SyncEdgeTrg', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=DISCRMIN, maxval=DISCRMAX)

        self.add_parameter('SyncChannelOffset', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=CHANOFFSMIN, maxval=CHANOFFSMAX)
        self.add_parameter('InputEdgeTrg', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=DISCRMIN, maxval=DISCRMAX)

        self.add_parameter('InputChannelOffset', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=CHANOFFSMIN, maxval=CHANOFFSMAX)
        self.add_parameter('HistoLen', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=0, maxval=MAXLENCODE)
        self.add_parameter('InputEdgeTrg0', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('InputEdgeTrg1', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('CountRate0', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('CountRate1', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('ElapsedMeasTimePS', flags = Instrument.FLAG_GET, type=types.FloatType)
        self.add_parameter('DeviceIndex', flags = Instrument.FLAG_SET, type=types.IntType)

        self.add_parameter('MeasRunning', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flags', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('Flag_Overflow', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_FifoFull', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_RefLost', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_SyncLost', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_SystemError', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('NumOfInputChannels', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('Channel', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('Binning', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=0, maxval=MAXBINSTEPS-1)
        
        self.add_function('start_histogram_mode')
        self.add_function('start_T2_mode')
        self.add_function('start_T3_mode')
        self.add_function('ClearHistMem')
        self.add_function('StartMeas')
        self.add_function('StopMeas')
        self.add_function('OpenDevice')
        self.add_function('CloseDevice')
        # self.add_function('get_T3_pulsed_events')

        self._do_set_DeviceIndex(DeviceIndex)
        self.OpenDevice()
        qt.msleep(1)
        if self.start_histogram_mode():

            self.Model = numpy.array([16*' '])
            self.PartNo = numpy.array([8*' '])
            self.SerialNo = numpy.array([8*' '])
            self.Version = numpy.array([16*' '])
            
            success = self._TH260.TH260_GetHardwareInfo(self.DevIdx, 
                self.Model.ctypes.data, self.PartNo.ctypes.data, self.Version.ctypes.data)
            if success != 0:
                logging.warning(__name__ + ' : error getting hardware info')
                self.get_ErrorString(success)
     #       print ('HydraHarp model %s'%self.Model)            
     #       print ('HydraHarp part no. %s'%self.PartNo)            
            success = self._TH260.TH260_GetSerialNumber(self.DevIdx, 
                self.SerialNo.ctypes.data)
            if success != 0:
                logging.warning(__name__ + ' : error getting serial number')
                self.get_ErrorString(success)
     #       print ('HydraHarp serial no. %s'%self.SerialNo)            

            self._do_get_NumOfInputChannels()
            
            self._do_set_SyncEdgeTrg(200)

            self._do_set_SyncChannelOffset(0)

            self._do_set_Channel(0)
            self._do_set_InputEdgeTrg(200)
            self._do_set_InputChannelOffset(0)
            
            self._do_set_Channel(1)
            self._do_set_InputEdgeTrg(200)
            self._do_set_InputChannelOffset(0)
           
            self._do_set_SyncDiv(1)
            self._do_set_Binning(8)
            self._do_set_HistoLen(MAXLENCODE)
            self._do_set_Offset(0)
            self.set_StopOverflow(0,STOPCNTMAX)
            self._do_get_BaseResolutionPS()
            self._do_get_MaxBinSteps()
            self._do_get_ResolutionPS()
        else:
            logging.error('TH260 device could not be initialized.')
            self.CloseDevice()

    def _load_dll(self): #3
#        print __name__ +' : Loading THLib.dll'
        WINDIR=os.environ['WINDIR']
        self._TH260 = windll.LoadLibrary(WINDIR+'\\system32\\'+DRIVER)
        sleep(0.02)

    def _do_set_DeviceIndex(self,val):
        self.DevIdx = val


    def _do_set_Channel(self,val):
	if val < self.NumOfInputChannels:
            self.Channel = val
        else:
            logging.warning('Error: Channel Index out of range')

    def start_histogram_mode(self):
        success = self._TH260.TH260_Initialize(self.DevIdx, MODE_HIST)
        if success != 0:
            logging.warning(__name__ + ' : Histogramming mode could not be started')
            self.get_ErrorString(success)
            return False
        return True

    def start_T2_mode(self):
        success = self._TH260.TH260_Initialize(self.DevIdx, MODE_T2)
        if success != 0:
            logging.warning(__name__ + ' : T2 mode could not be started')
            self.get_ErrorString(success)

    def start_T3_mode(self):
        success = self._TH260.TH260_Initialize(self.DevIdx, MODE_T3)
        if success != 0:
            logging.warning(__name__ + ' : T3 mode could not be started')
            self.get_ErrorString(success)

    def _do_get_NumOfInputChannels(self):
        nchannels = c_int(0)
        success = self._TH260.TH260_GetNumOfInputChannels(self.DevIdx, byref(nchannels))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetNomOfInputChannels')
            self.get_ErrorString(success)
        self.NumOfInputChannels = int(nchannels.value)
        return self.NumOfInputChannels
       
    def _do_get_MaxBinSteps(self):
        resolution = c_double(0)
        binsteps = c_int(0)
        success = self._TH260.TH260_GetBaseResolution(self.DevIdx, byref(resolution), byref(binsteps))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetBaseResolution')
            self.get_ErrorString(success)
        self.MaxBinSteps = binsteps.value
        self.BaseResolutionPS = resolution.value
        return self.MaxBinSteps

    def _do_get_BaseResolutionPS(self):
        resolution = c_double(0)
        binsteps = c_int(0)
        success = self._TH260.TH260_GetBaseResolution(self.DevIdx, byref(resolution), byref(binsteps))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetBaseResolution')
            self.get_ErrorString(success)
        self.BaseResolution = binsteps.value
        self.BaseResolutionPS = resolution.value
        return self.BaseResolutionPS

    def _do_get_ResolutionPS(self):
        resolution = c_double(0)
        success = self._TH260.TH260_GetResolution(self.DevIdx,byref(resolution))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetResolution')
            self.get_ErrorString(success)
        self.ResolutionPS = resolution.value
        return self.ResolutionPS

    def get_CountRate(self):
        cntrate = c_int(0)
        success = self._TH260.TH260_GetCountRate(self.DevIdx, self.Channel, byref(cntrate))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetCountRate')
            self.get_ErrorString(success)
        return cntrate.value

    def get_SyncRate(self):
        syncrate = c_int(0)
        success = self._TH260.TH260_GetSyncRate(self.DevIdx, byref(syncrate))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetSyncRate')
            self.get_ErrorString(success)
        return syncrate.value

    def _do_get_CountRate0(self):
        temp = self.Channel
        self.Channel = 0
        CountRate = self.get_CountRate()
        self.Channel = temp
        return CountRate

    def _do_get_CountRate1(self):
        temp = self.Channel
        self.Channel = 1
        CountRate = self.get_CountRate()
        self.Channel = temp
        return CountRate

    def _do_set_InputEdgeTrg0(self, value,**kw):
        temp = self.Channel
        self.Channel = 0
        self.set_InputEdgeTrg(value,**kw)
        self.Channel = temp

    def _do_set_InputEdgeTrg1(self, value,**kw):
        temp = self.Channel
        self.Channel = 1
        self.set_InputEdgeTrg(value,**kw)
        self.Channel = temp

    def set_EdgeTrg(self, value, **kw):
        self._do_set_SyncEdgeTrg(value, **kw)
        self._do_set_InputEdgeTrg0(value,**kw)
        self._do_set_InputEdgeTrg1(value,**kw)

    def _do_set_InputEdgeTrg(self, value, edge=EDGE_RISING):
        success = self._TH260.TH260_SetInputEdgeTrg(self.DevIdx, self.Channel, value, edge)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetInputEdgeTrg')
            self.get_ErrorString(success)

    def _do_set_SyncEdgeTrg(self, value, edge=EDGE_RISING):
        success = self._TH260.TH260_SetSyncEdgeTrg(self.DevIdx, value, edge)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetSyncEdgeTrg')
            self.get_ErrorString(success)

    def _do_set_InputChannelOffset(self, value):
        success = self._TH260.TH260_SetInputChannelOffset(self.DevIdx, self.Channel, value)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetInputChannelOffset')
            self.get_ErrorString(success)

    def _do_set_SyncChannelOffset(self, value):
        success = self._TH260.TH260_SetSyncChannelOffset(self.DevIdx, value)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetSyncChannelOffset')
            self.get_ErrorString(success)

    def _do_set_SyncDiv(self, div):
        success = self._TH260.TH260_SetSyncDiv(self.DevIdx, div)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetSyncDiv')
            self.get_ErrorString(success)

    def set_StopOverflow(self, stop_ovfl, stopcount):
        if (stopcount < STOPCNTMIN) | (stopcount > STOPCNTMAX):
            logging.warning(__name__ + ' : error in TH_SetStopOverflow: stopcount out of range')
        else:         
            success = self._TH260.TH260_SetStopOverflow(self.DevIdx, stop_ovfl, stopcount)
            if success < 0:
                logging.warning(__name__ + ' : error in TH_SetStopOverflow')
                self.get_ErrorString(success)

    def _do_set_Binning(self, value):
        success = self._TH260.TH260_SetBinning(self.DevIdx, value)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetBinning')
            self.get_ErrorString(success)

    def _do_set_Offset(self, offset):
        success = self._TH260.TH260_SetOffset(self.DevIdx, offset)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetOffset')
            self.get_ErrorString(success)

    def _do_set_Range(self, binsize):  # binsize in 2^n times base resolution (4ps)
        self.set_Binning(binsize+2)

    def _do_set_HistoLen(self, lencode):
        actuallen = c_int(0)
        success = self._TH260.TH260_SetHistoLen(self.DevIdx, lencode, byref(actuallen))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetHistoLen')
            self.get_ErrorString(success)
	actuallen = int(actuallen.value)
        self.HistogramLength = actuallen

    def ClearHistMem(self):
        success = self._TH260.TH260_ClearHistMem(self.DevIdx)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_ClearHistMem')
            self.get_ErrorString(success)

    def StartMeas(self,aquisition_time_ms):
        if (aquisition_time_ms < ACQTMIN) | (aquisition_time_ms > ACQTMAX):
            logging.warning(__name__ + ' : error in TH_StartMeas: acquisition time out of range')
        else:         
            success = self._TH260.TH260_StartMeas(self.DevIdx, aquisition_time_ms)
            if success < 0:
                logging.warning(__name__ + ' : error in TH_StartMeas')
                self.get_ErrorString(success)

    def StopMeas(self):
        success = self._TH260.TH260_StopMeas(self.DevIdx)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_StopMeas')
            self.get_ErrorString(success)

    def OpenDevice(self):
        SerialNr = numpy.array([8*' '])
#        print ('Opening HydraHarp Device no. %s'%self.DevIdx)            
        success = self._TH260.TH260_OpenDevice(self.DevIdx, SerialNr.ctypes.data)
        self.SerialNr = SerialNr
#        print ('HydraHarp serial no. %s'%self.SerialNr)            
        if success != 0:
            logging.warning(__name__ + ' : OpenDevice failed, check that HydraHarp software is not running.')
            self.get_ErrorString(success)
            return False
        return True

    def CloseDevice(self):
        success = self._TH260.TH260_CloseDevice(self.DevIdx)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_CloseDevice')
            self.get_ErrorString(success)
            return False
        return True

    def _do_get_MeasRunning(self):
        running = c_int(0)
        success = self._TH260.TH260_CTCStatus(self.DevIdx, byref(running))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_CTCStatus')
            self.get_ErrorString(success)
        return (running.value == 0)

    def _do_get_Flags(self):
        Flags = c_int(0)
        success = self._TH260.TH260_GetFlags(self.DevIdx, byref(Flags))
        #print success
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetFlags')
            self.get_ErrorString(success)
        return Flags.value
        
    def _do_get_Flag_Overflow(self):
        return self._do_get_Flags() & FLAG_OVERFLOW == FLAG_OVERFLOW
        
    def _do_get_Flag_FifoFull(self):
        return self._do_get_Flags() & FLAG_FIFOFULL == FLAG_FIFOFULL
        
    def _do_get_Flag_SyncLost(self):
        return self._do_get_Flags() & FLAG_SYNC_LOST == FLAG_SYNC_LOST
        
    def _do_get_Flag_RefLost(self):
        return self._do_get_Flags() & FLAG_REF_LOST == FLAG_REF_LOST
        
    def _do_get_Flag_SystemError(self):
        return self._do_get_Flags() & FLAG_SYSERROR == FLAG_SYSERROR
        
    def _do_get_ElapsedMeasTimePS(self):
        elapsed = c_double(0)
        success = self._TH260.TH260_GetElapsedMeasTime(self.DevIdx, byref(elapsed))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetElapsedMeasTime')
            self.get_ErrorString(success)
        return elapsed.value

    def get_Histogram(self, channel, clear=0):
        data = numpy.array(numpy.zeros(self.HistogramLength), dtype = numpy.uint32)
        success = self._TH260.TH260_GetHistogram(self.DevIdx,data.ctypes.data,channel,clear)
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetHistogram')
            self.get_ErrorString(success)
        return data
 
    def get_Block(self):
        return self.get_Histogram(0,0)

    def get_Warnings(self):
        Warnings = c_int(0)
        success = self._TH260.TH260_GetWarnings(self.DevIdx, byref(Warnings))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_GetWarnings')
            self.get_ErrorString(success)
        return Warnings.value
        
    def get_WarningsText(self, warnings):
        if warnings > 0:
            WarningsText = numpy.array([16384*' '])
            if self._TH260.TH260_GetWarningsText(self.DevIdx, 
                WarningsText.ctypes.data, warnings) != 0:
                logging.warning(__name__ + ' : error in TH_GetWarningsText')
            return WarningsText[0][0:WarningsText[0].index('\x00')]
        else: 
            return 0
            
    def get_TTTR_Data(self,count = TTREADMAX):
        data = numpy.array(numpy.zeros(TTREADMAX), dtype = numpy.uint32)
        length = c_int(0)
        success = self._TH260.TH260_ReadFiFo(self.DevIdx,data.ctypes.data,count, byref(length))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_ReadFiFo')
            self.get_ErrorString(success)
        return length.value, data
        
        
    def set_MarkerEdgesRising(self,me0,me1,me2,me3):
        success = self._TH260.TH260_SetMarkerEdges(self.DevIdx, int(me0), int(me1), int(me2), int(me3))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetMarkerEdges')
            self.get_ErrorString(success)
            
    def set_MarkerEnable(self,me0,me1,me2,me3):
        success = self._TH260.TH260_SetMarkerEnable(self.DevIdx, int(me0), int(me1), int(me2), int(me3))
        if success < 0:
            logging.warning(__name__ + ' : error in TH_SetMarkerEnable')
            self.get_ErrorString(success)
            
    def get_ErrorString(self, errorcode):
        ErrorString = numpy.array([40*' '])
        if self._TH260.TH260_GetErrorString(ErrorString.ctypes.data, errorcode) != 0:
            logging.warning(__name__ + ' : error in TH_GetErrorString')
        print(ErrorString)
        return ErrorString

