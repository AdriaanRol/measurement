from ctypes import *
import os
from instrument_plugins._Spectrum_M2i2030.errors import errors as _spcm_errors
from instrument_plugins._Spectrum_M2i2030.regs import regs as _spcm_regs
from instrument import Instrument
import pickle
from time import sleep, time
import types
import logging
import numpy
import qt
import ctypes
from qt import *
from numpy import *
from data import Data

adwin_path = 'c:\\adwin'
program_path = 'D:\\measuring\\user\\ADwin_Codes'

class ADwin_Pro_II(Instrument): #1
    '''
    This is the driver for the Adwin Pro II

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'ADwin_Pro_II', 'address = <device no>')
    
    status:
     1) create this driver!=> is never finished
    TODO:
    '''

    def __init__(self, name, address): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument ADwin Pro II')
        Instrument.__init__(self, name, tags=['physical'])

        self._address = address

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)
        self._adwin32.e_Get_ADBFPar.restype = c_float
#        self.add_function('Set_DAC_Voltage')
        self.add_function('Set_Par')
        self.add_function('Set_FPar')
        self.add_function('Start_Process')
        self.add_function('Stop_Process')



    def _load_dll(self): #3
        print __name__ +' : Loading adwin32.dll'
        WINDIR=os.environ['WINDIR']
        self._adwin32 = windll.LoadLibrary(WINDIR+'\\adwin32')
        ErrorMsg=c_int32(0)
        ProcType = self._adwin32.e_ADProzessorTyp(self._address,ctypes.byref(ErrorMsg))
        if ProcType != 1011:
            logging.warning(__name__ + ' WARNING: ADwin Pro II with T11 processor expected. Processor type %s found'%ProcType)
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.ProcType: %s'%ErrorMsg.value)

        sleep(0.02)

    def Boot(self):
        ErrorMsg=c_int32(0)
        filename = adwin_path+'\\ADwin11.btl'
        self._adwin32.e_ADboot(filename,self._address,100000,0,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Boot: %s'%ErrorMsg.value)

    def Test_Version(self):
        ErrorMsg=c_int32(0)
        self._adwin32.e_ADTest_Version.restype = ctypes.c_short
        ret = self._adwin32.e_ADTest_Version(self._address, 0, ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.TestVersion: %s'%ErrorMsg.value)
        return ret

    def ProcessorType(self):
        ErrorMsg=c_int32(0)
        ret = self._adwin32.e_ADProzessorTyp(self._address, ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.ProzessorType: %s'%ErrorMsg.value)
        return ret

    def Workload(self):
        ErrorMsg=c_int32(0)
        ret = self._adwin32.e_AD_Workload(0, self._address, ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Workload: %s'%ErrorMsg.value)
        return ret

    def Free_Mem(self, Mem_Spec):
        ErrorMsg=c_int32(0)
        ret = self._adwin32.e_AD_Memory_all_byte(Mem_Spec, self._address, ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Free_Mem: %s'%ErrorMsg.value)
        return ret

    def Load(self, filename):
        ErrorMsg=c_int32(0)
        self._adwin32.e_ADBload(filename,self._address,0,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Load: %s'%ErrorMsg.value)

    def Get_Data_Length(self,index):
        ErrorMsg=c_int32(0)
        data = self._adwin32.e_GetDataLength(index,self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Get_Data_Length: %s'%ErrorMsg.value)
        return data

    def Get_Data_Long(self, index, start, count):
        ErrorMsg=c_int32(0)
        data = numpy.array(numpy.zeros(count), dtype = numpy.int32)
        success = self._adwin32.e_Get_Data(data.ctypes.data,2,index,start,count, self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Get_Data_Long: %s'%ErrorMsg.value)
        return data

    def Set_Data_Long(self, data=numpy.array, index=numpy.int32, 
            start=numpy.int32, count=numpy.int32):
        
        ErrorMsg=c_int32(0)
        success = self._adwin32.e_Set_Data(data.ctypes.data,2,index,start,
                count, self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Set_Data_Long: %s'%ErrorMsg.value)

    def Get_Data_Float(self, index, start, count):
        ErrorMsg=c_int32(0)
        data = numpy.array(numpy.zeros(count), dtype = numpy.single)
        success = self._adwin32.e_Get_Data(data.ctypes.data,5,index,start,count, self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Get_Data_Float: %s'%ErrorMsg.value)
        return data

    def Set_Data_Float(self, data=numpy.array, index=numpy.int32, 
            start=numpy.int32, count=numpy.int32):
        ErrorMsg=c_int32(0)        
        # Auto type conversion
        d=numpy.array(data,numpy.single)
        success = self._adwin32.e_Set_Data(d.ctypes.data,5,index,start,count,
                self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + \
                    ' : error in ADwin.Set_Data_Float: %s'%ErrorMsg.value)

    def Get_Par(self,index):
        ErrorMsg=c_int32(0)
        data = self._adwin32.e_Get_ADBPar(index,self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Get_Par: %s'%ErrorMsg.value)
      
        return data

    def Set_Par(self,index,value):
        ErrorMsg=c_int32(0)
        self._adwin32.e_Set_ADBPar(index,value,self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Set_Par: %s'%ErrorMsg.value)

    def Get_FPar(self,index):
        ErrorMsg=c_int32(0)
        data = single(self._adwin32.e_Get_ADBFPar(index,self._address,ctypes.byref(ErrorMsg)))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Get_FPar: %s'%ErrorMsg.value)
      
        return data

    def Set_FPar(self,index,value):
        ErrorMsg=c_int32(0)
        self._adwin32.e_Set_ADBFPar(index,c_float(value),self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Set_FPar: %s'%ErrorMsg.value)

    def Start_Process(self,index):
        ErrorMsg=c_int32(0)
        result = self._adwin32.e_ADB_Start(index,self._address,ctypes.byref(ErrorMsg))
        if result == 255:
            logging.warning(__name__ + ' : error in ADwin.Start_Process: %s'%ErrorMsg.value)

    def Stop_Process(self,index):
        ErrorMsg=c_int32(0)
        result = self._adwin32.e_ADB_Stop(index,self._address,ctypes.byref(ErrorMsg))
        if result == 255:
            logging.warning(__name__ + ' : error in ADwin.Stop_Process: %s'%ErrorMsg.value)

    def Process_Status(self,index):
        ErrorMsg=c_int32(0)
        par = c_int16(index-100)
        data = self._adwin32.e_Get_ADBPar(par,self._address,ctypes.byref(ErrorMsg))
        if ErrorMsg.value != 0:
            logging.warning(__name__ + ' : error in ADwin.Process_Status: %s'%ErrorMsg.value)

        return data

#    def Set_DAC_Voltage(self, DAC, Voltage):
#	print('I am here')
#        while self.Process_Status(6) > 0:
#            print('Set_DAC_Voltage: waiting for previous process to finish')
#            sleep(0.1)
#	print('I am there')
#        self.Set_Par(64,0)
#        self.Set_Par(63,DAC)
#        self.Set_FPar(63,Voltage)
#	print('Trying to load '+program_path+'\\universalDAC.tb6')
#        self.Load(program_path+'\\universalDAC.tb6')
#	print('done')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#
    def Get_Error_Text(self, ErrorCode):
        text = ctypes.create_string_buffer(256)
        Text = ctypes.byref(text)
        self._adwin32.ADGetErrorText(ErrorCode,Text,256)
        print(text.value)
        return text.value
#
#    def Pulse_DAC_Voltage(self, DAC, Voltage_pulse, Voltage_off, duration):   # duration in microseconds
#        while self.Process_Status(6) > 0:
#            print('Pulse_DAC_Voltage: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,DAC)
#        self.Set_Par(64,1)
#        self.Set_Par(65,duration)
#        self.Set_FPar(63,Voltage_off)
#        self.Set_FPar(64,Voltage_pulse)
#        self.Load(program_path+'\\universalDAC.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#    def Pulse_DO(self, DO, duration, module = 'DIO'):   # duration in units of 10ns
#        while self.Process_Status(6) > 0:
#            print('Pulse_DO: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,DO)
#        self.Set_Par(64,1)
#        self.Set_Par(65,duration)
#        if module == 'CPU':
#            self.Load(program_path+'\\universalCPU_DO.tb6')
#        else:
#            self.Load(program_path+'\\universalDO.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#    def Set_DO(self, DO, state, module = 'DIO'):
#        while self.Process_Status(6) > 0:
#            print('Set_DO: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,DO)
#        self.Set_Par(64,0)
#        self.Set_Par(65,state)
#        if module == 'CPU':
#            self.Load(program_path+'\\universalCPU_DO.tb6')
#        else:
#            self.Load(program_path+'\\universalDO.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#    def Get_DI(self, DI, module = 'DIO', RisingEdge = False):
#        while self.Process_Status(6) > 0:
#            print('Get_DI: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,DI)
#        if module == 'CPU':
#            self.Load(program_path+'\\universalCPU_DI.tb6')
#        else:
#            self.Load(program_path+'\\universalDI.tb6')
#            self.Set_Par(66,int(RisingEdge))
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#        if module == 'CPU':
#            return self.Get_Par(65)
#        else:
#            return int(self.Get_Par(65) & 2**DI == 2**DI)
#
#    def Get_ADC(self, ADC):
#        while self.Process_Status(6) > 0:
#            print('Get_ADC: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,ADC)
#        self.Load(program_path+'\\universalADC.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#        return self.Get_FPar(63)
#
#    def Get_CNT(self, t_int = 1000, channel = 5, initialize = True):
#        while self.Process_Status(6) > 0:
#            print('Get_CNT: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(24,t_int)
#        if channel < 5: 
#            self.Set_Par(11,2**(channel-1))
#        if channel == 5: 
#            self.Set_Par(11,3)
#        self.Set_Par(12,int(initialize))
#        self.Load(program_path+'\\universalCNT.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#        if channel < 5: 
#            return self.Get_Data_Long(28,1,4)[channel-1]
#        if channel == 5: 
#            cnt = self.Get_Data_Long(28,1,4)
#            return cnt[0]+cnt[1]
#        return 0
#
#    def Sweep_DAC_Voltage(self, DAC, U_Start, U_Stop, R_sweep):   # sweep rate in V/s
#        while self.Process_Status(6) > 0:
#            print('Sweep_DAC_Voltage: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,DAC)
#        self.Set_FPar(69,U_Start)
#        self.Set_FPar(64,U_Stop)
#        self.Set_FPar(65,R_sweep)
#        self.Load(program_path+'\\sweep_DAC.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#    def Sweep_DAC_Voltage_To(self, DAC, U_Stop, R_sweep):   # sweep rate in V/s
#        while self.Process_Status(6) > 0:
#            print('Sweep_DAC_Voltage_To: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,DAC)
#        self.Set_FPar(64,U_Stop)
#        self.Set_FPar(65,R_sweep)
#        self.Load(program_path+'\\sweep_DAC.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#    def Conf_DIO(self, mode):
#        while self.Process_Status(6) > 0:
#            print('Conf_DIO: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,mode)
#        self.Load(program_path+'\\CONF_DIO.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#    def Conf_CPU_DIO(self, DO0 = False, DO1 = False, RisingEdge0 = False, RisingEdge1 = False):
#        mode = int(DO0) + 2 * int(RisingEdge0) * (1-int(DO0)) + 16 * int(DO1) + 32 * int(RisingEdge1) * (1-int(DO1))
#        while self.Process_Status(6) > 0:
#            print('Conf_CPU_DIO: waiting for previous process to finish')
#            sleep(0.1)
#        self.Set_Par(63,mode)
#        self.Load(program_path+'\\CONF_CPU_DIO.tb6')
#        self.Start_Process(6)
#        while self.Process_Status(6) > 0:
#            sleep(0.01)
#
#    def program_path(self):
#        return program_path
