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
import qt
import numpy as np


class Master_of_magnet(Instrument):

    def __init__(self, name,  anc_ins='ANC300_LT2'):

        Instrument.__init__(self, name)
        self._anc_ins = qt.instruments[anc_ins]

        ### Axis modules <-> magnet scan axes
        self.Axis_config = {
        'X_axis': 5,
        'Y_axis': 6,
        'Z_axis': 4}

        self._anc_ins.Turn_off_AC_IN(self.Axis_config['X_axis'])
        self._anc_ins.Turn_off_AC_IN(self.Axis_config['Y_axis'])
        self._anc_ins.Turn_off_AC_IN(self.Axis_config['Z_axis'])

        self._anc_ins.Turn_off_DC_IN(self.Axis_config['X_axis'])
        self._anc_ins.Turn_off_DC_IN(self.Axis_config['Y_axis'])
        self._anc_ins.Turn_off_DC_IN(self.Axis_config['Z_axis'])

    def set_mode(self, axis, mode):
        ''' Sets the mode (string) of axis 'X_axis', 'Y_axis', 'Z_axis' or 'all' 
            to the following:
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
        if axis == 'all':
            for ax in ['X_axis', 'Y_axis', 'Z_axis']:
                axis_number = self.Axis_config[ax]
                self._anc_ins.SetMode(axis_number, mode)
        else:
            axis_number = self.Axis_config[axis]
            self._anc_ins.SetMode(axis_number, mode)

    def get_mode(self,axis):
        if axis == 'all':
            for ax in ['X_axis', 'Y_axis', 'Z_axis']:
                axis_number = self.Axis_config[ax]
                print ax+ ' '+ self._anc_ins.GetMode(axis_number)
        else:        
            axis_number = self.Axis_config[axis]
            return self._anc_ins.GetMode(axis_number)

    def get_axis_config(self):
        print 'X_axis = ' + str(self.Axis_config['X_axis'])
        print 'Y_axis = ' + str(self.Axis_config['Y_axis'])
        print 'Z_axis = ' + str(self.Axis_config['Z_axis'])
    
    # get/set scan/step paramaters
    def get_frequency(self, axis):
        ''' Get the stepper frequency''' 
        if axis == 'all':
            for ax in ['X_axis', 'Y_axis', 'Z_axis']:
                axis_number = self.Axis_config[axis]
                return self._anc_ins.GetFrequency(axis_number)

        else:
            axis_number = self.Axis_config[axis]
            return self._anc_ins.GetFrequency(axis_number)

    def set_frequency(self, axis, frequency):
        ''' Set the stepper frequency''' 
        self._anc_ins.SetFrequency(self.Axis_config[axis], frequency)
        print 'frequency of %s set to %d Hz' %(axis, frequency)

    def get_amplitude(self, axis):
        ''' Get the stepper amplitude''' 
        axis_number = self.Axis_config[axis]
        return self._anc_ins.GetAmplitude(axis_number)

    def set_amplitude(self, axis, amplitude):
        ''' Set the stepper amplitude''' 
        self._anc_ins.SetAmplitude(self.Axis_config[axis], amplitude)
        print 'amplitude of %s set to %d V' %(axis, amplitude)

    def get_offset(self, axis):
        ''' Get the scanner offset'''
        axis_number = self.Axis_config[axis]
        return self._anc_ins.GetOffset(axis_number)

    def set_offset(self, axis, offset):
        ''' Get the stepper offset''' 
        self._anc_ins.SetOffset(self.Axis_config[axis], offset)
        print 'offset of %s set to %d V' %(axis, offset)

    # Stepping and stopping.
    def step(self, axis, steps):  #TODO add a timer to stop the continious movement
        ''' Performs #steps along the given axis.
        axis    the axis to step. 
        steps   integer, positive values for positive steps, negative values for 
                negative steps. Valid inputs: +/- '1','2','3','4','5'... and 'c','-c' for continious
        '''
        axis_number = self.Axis_config[axis]
        
        if steps == 'c':
            self._anc_ins.StepUp(axis_number, steps)
        elif steps == '-c':
            self._anc_ins.StepDown(axis_number, 'c')    
        elif int(steps) > 0: 
            self._anc_ins.StepUp(axis_number, steps)
        elif int(steps) < 0: 
            self._anc_ins.StepDown(axis_number, abs(int(steps)))
        else:
            print 'Error: invalid input'
    

    def stop(self, axis):
        axis_number = self.Axis_config[axis]          
        self._anc_ins.Stop(axis_number)


    ## Methods to do magnetic field calculations
    def B_to_f(self, B_field):
        freq = 2.88e9 - B_field*2.8e6
        return freq

    def f_to_B(self, freq): 
        B_field = (2.88e9 - freq)/2.8e6
        return B_field

