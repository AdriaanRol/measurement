### Instrument class to control the ANC300 attocube controller. NOTE that 
### the 6 axis controllers also have direct analog inputs through the adwin (e.g. for scanning).
### These can only be enabled/disabled here and care should be taken to limit 
### those input voltages seperately.

### Work in progress, Tim Taminiau

from instrument import Instrument
import visa
import types
import logging
import re
import math

class Attocube_ANC300(Instrument):

    def __init__(self, name, address):
        
        Instrument.__init__(self, name)

        self._address = address
        self._visa = visa.instrument(self._address,
                        baud_rate=9600, data_bits=8, stop_bits=1,
                        parity=visa.no_parity, term_chars='\r\n')

        self.Echo('off')
        self._visa.read()
    
    ### Auxilairy functions  

    def Read(self):
        return self._visa.read()
        
    def Close(self): #unknown function
        return self._visa.close()

    def Echo(self, state):
        self._visa.write('echo '+ state)

    def Help(self): #Does not yet return text in organized fashion
        
        ''' Gives the visa comments to communicate with the ANC300.
        These are used in the instrument Attocube_ANC300.py'''

        a = self._visa.ask('help')
        print a
        for ii in range(31):
            print self._visa.read()

    def GetSerial(self,axis):
        a = self._visa.ask('getser '+str(axis))
        b = self._visa.read()
        print b
        return a

    ### Set/get the mode of axis controllers. ###
    def SetMode(self, axis, mode):
        ''' Sets the mode (string) to the following:
        gnd     Disables all outputs and connects them to ground(chassis mass).
        
        stp     Stepping mode. AC-IN and DC-IN functionalities are not modified. 
                Offset is turned off.   
        
        inp     External scanning mode. AC-IN and DC-IN can be enabled for external scanning 
                using the Turn_on_AC_IN and Turn_on_DC_IN methods. Disables stepping and
                offset modes.

        off     Offset mode / scanning mode. AC-IN and DC-IN functionalities are
                not modified. Any stepping is turned off.

        stp+    Additive offset + stepping mode. Stepping waveforms are added to 
                the offset. AC-IN and DC-IN functionalities are not modified.

        stp-    Subtractive offset + stepping mode. Stepping
                waveforms are subtracted from an offset. AC-IN and DC-IN
                functionalities are not modified.         
        
        cap     Starts a capacitance measurement. The axis
                returns to gnd mode afterwards. It is not needed to switch to gnd
                mode before.
        '''
        self._visa.write('setm ' + str(axis) + ' ' + mode)
        print 'axis %d mode = %s' %(axis, mode)

    def GetMode(self,axis):
        a = self._visa.ask('getm '+str(axis))
        self._visa.read()
        return a

    ### Methods that query the status/paramaters

    def GetFrequency(self,axis):
        return self._visa.ask('getf '+str(axis))

    def GetAmplitude(self,axis):
        a = self._visa.ask('getv '+str(axis))
        self._visa.read()
        return a

    def GetOffset(self,axis):
        a = self._visa.ask('geta '+str(axis))
        self._visa.read()
        return a
           
    ### Methods that set the parameters. 

    def SetFrequency(self,axis,frequency):
        self._visa.write('setf '+ str(axis) + ' ' + str(frequency))
        print 'frequency of axis %d set to %d Hz' %(axis, frequency)
    
    def SetAmplitude(self,axis,amplitude):
        self._visa.write('setv '+ str(axis) + ' ' + str(amplitude))
        print 'amplitude on axis %d set to %d V' %(axis, amplitude)

    def SetOffset(self,axis,offset):
        self._visa.write('seta '+ str(axis) + ' ' + str(offset))
        print 'offset on axis %d set to %d V' %(axis, offset)

    ### Methods that set/get the AC/DC inputs ON/OFF. 

    def Get_AC_IN_Status(self,axis):
        self._visa.write('getaci '+ str(axis))
        a = self._visa.read()
        self._visa.read()
        return a

    def Get_DC_IN_Status(self,axis):
        self._visa.write('getdci '+ str(axis))
        a = self._visa.read()
        self._visa.read()
        return a

    def Turn_on_AC_IN(self,axis): ### NOT YET FUNCTIONAL, STILL FIX SYNTAX, CAREFULLY TEST ON 
        self._visa.write('setaci '+ str(axis) + ' [on]')
        print 'axis %d AC_IN: ON' %(axis)

    def Turn_off_AC_IN(self,axis):
        self._visa.write('setaci '+ str(axis) + ' [off]')
        print 'axis %d AC_IN: OFF' %(axis)

    def Turn_on_DC_IN(self,axis):
        self._visa.write('setdci '+ str(axis) + ' [on]')
        print 'axis %d DC_IN: ON' %(axis)

    def Turn_off_DC_IN(self,axis):
        self._visa.write('setdci '+ str(axis) + ' [off]')
        print 'axis %d DC_IN: OFF' %(axis)

    ### Methods that set/get the filter settings.

    def SetFilter(self,axis,filter):
        ''' Set the filter settings. The allowed filter values are
        for the ANM300 module: '16', '160' and 'off'.
        for the ANM200 module: '1.6', '16', '160', and '1600'. '''
        self._visa.write('setfil '+ str(axis) + ' ' + filter)
        self._visa.read()
        print 'filter for axis %d set to %s' %(axis, filter)
  
    def GetFilter(self,axis):
        a = self._visa.ask('getfil '+str(axis))
        self._visa.read()
        return a


    ### THE FOLLOWING METHODS HAVE NOT YET BEEN TESTED AS THEY NEED THE NEW ELECTRONICS
    ### Methods for realizing stepping    

    def StepUp(self, axis, steps):
        ''' Performs a single, multiple or continious steps along positive axis
        axis    integer, valid values 1-6
        steps   string, valid values '1','2','3','4','5'... or 'c' for continious
        '''
        Mode = self.GetMode()
        if Mode[7:10] == 'stp':
             self._visa.write('stepu '+ str(axis) + ' ' + steps)
        else:
            return 'error: ' + mode

    def StepDown(self, axis, steps):
        ''' Performs a single, multiple or continious steps along negative axis
        axis    integer, valid values 1-6
        steps   string, valid values '1','2','3','4','5'... or 'c' for continious
        '''
        Mode = self.GetMode()
        if Mode[7:10] == 'stp':
             self._visa.write('stepd '+ str(axis) + ' ' + steps)
        else:
            return 'error: ' + mode

    def Stop(self, axis):
        ''' Stop any motion on axis'''
        self._visa.write('stop '+ str(axis))
        print 'axis %d stopped' %(axis)

    def WaitForStepping(self, axis):
        ''' Tell to wait for stepping to finish,
        function unknown'''
        self._visa.write('stepw '+ str(axis))

    ### Methods to get/set input triggers, NOT fucntional.
    def GetUpTrigger(self,axis):
        a = self._visa.ask('gettu '+str(axis))
        #self._visa.read()
        return a

    def GetDownTrigger(self,axis):
        a = self._visa.ask('gettd '+str(axis))
        #self._visa.read()
        return a


    



       

