from instrument import Instrument
import visa
import types
import logging
import re, qt
import math
import numpy as np
import msvcrt

#====================================================================
#USEFUL VALUES:
#====================================================================
#Positive x (i.e. set_relative_position(+x)) rotates towards positive 
#degrees. Negative x rotates towards negative degrees.

class NewportAgilisUC(Instrument):

    def __init__(self, name, address, ins_type='UC2'):
        Instrument.__init__(self, name)

        self._address = address
        self._visa = visa.instrument(self._address,
                        baud_rate=921600, data_bits=8, stop_bits=1,
                        parity=visa.no_parity, term_chars='\r')
        self._axes = (1,2) #this is the number of axes per channel          

        if ins_type == 'UC2':
            self._ins_type = ins_type
        elif ins_type == 'UC8':
            self._ins_type = ins_type
        else:
            raise ValueError('Unknown Agilis controller intrument type. \
                             Currently known types: UC2, UC8')
        #define the get and set functions of the positioner. order is 
        #according to the manual page 24.


        self.add_parameter('jog',
                flags=Instrument.FLAG_GETSET,
                type=types.IntType,
                channels=self._axes,
                minval=-4,maxval=4)

        self.add_parameter('position',
                flags=Instrument.FLAG_GET,
                type=types.FloatType,
                channels=self._axes)
 
        self.add_parameter('mode', 
                flags=Instrument.FLAG_SET,
                type=types.StringType,
                format_map={'L': 'Local', 'R': 'Remote'})

        self.add_parameter('move_to_limit',
                flags=Instrument.FLAG_SET,
                type=types.IntType,
                channels=self._axes)

        self.add_parameter('absolute_position',
                flags=Instrument.FLAG_SET,
                type=types.IntType,
                channels=self._axes)

        self.add_parameter('limit_status',
                flags=Instrument.FLAG_GET,
                type=types.StringType,
                channels=self._axes)

        self.add_parameter('relative_position',
                flags=Instrument.FLAG_SET,
                type=types.IntType,
                channels=self._axes)

        self.add_parameter('step_amplitude',
                flags=Instrument.FLAG_GETSET,
                type=types.IntType,
                channels=self._axes)

        self.add_parameter('error',
                flags=Instrument.FLAG_GET,
                type=types.StringType)

        self.add_parameter('noof_steps',
                flags=Instrument.FLAG_GET,
                type=types.IntType,
                channels=self._axes)

        self.add_parameter('status',
                flags=Instrument.FLAG_GET,
                type=types.StringType,
                channels=self._axes)

        self.add_parameter('firmware_version',
                flags=Instrument.FLAG_GET,
                type=types.StringType)

        self.add_parameter('current_channel',
                flags=Instrument.FLAG_GETSET,
                type=types.IntType,
                minval=1,maxval=4)

      
        #add functions to the QT instrument
        self.add_function('local')
        self.add_function('remote')
        self.add_function('reset')
        self.add_function('stop_moving')
        self.add_function('set_zero_position')

        #example convienience usage functions
        self.add_function('quick_scan')
        self.add_function('precise_scan')

              
        #last things
        self.remote()
        #set speeds to max
        for k in self._axes:
           self.do_set_step_amplitude(k,50)


    #added functions
    def local(self):
        self.set_mode('L')

    def remote(self):
        self.set_mode('R')
        
    
    def stop_moving(self, axis):
        """
        Stops the motion on the defined axis. Sets the state to ready.
        """
        self._visa.write('%dST'%axis)


    def set_zero_position(self, axis):
        """
        Resets the step counter to zero. See TP command for further details.
        """
        if axis in self._axes:
            self._visa.write('%dZP'%axis)
            print 'Zero position axis %d set to current position.'%axis


    def do_get_jog(self, channel): #OK!
        """
        Returns the speed during a jog session.
        """
        axis=channel
        jog_dict = {-4 : 'Negative direction, 666 steps/s at defined step amplitude.',
                    -3 : 'Negative direction, 1700 steps/s at max. step amplitude.',
                    -2 : 'Negative direction, 100 step/s at max. step amplitude.',
                    -1 : 'Negative direction, 5 steps/s at defined step amplitude.',
                    0 : 'No move, go to READY state.',
                    1 : 'Positive direction, 5 steps/s at defined step amplitude.',
                    2 : 'Positive direction, 100 steps/s at max. step amplitude.',
                    3 : 'Positive direction, 1700 steps/s at max. step amplitude.',
                    4 : 'Positive direction, 666 steps/s at defined step amplitude.'}
        try:
            [ch, rawans] = self._visa.ask_for_values('%dJA?'%axis)
            ans = jog_dict[rawans]
        except:
            logging.warning(self.get_name() +': '+ self.get_error())
            return -1
        return ans

    def do_set_current_channel(self,channel):
        """
        Sets the currently active channel. Only available for the UC8 type controller
        """
        if self._ins_type == 'UC8':
            self._visa.write('CC%d'%(channel))
        else:
            logging.warning(self.get_name()+': This function is only available for the UC8 type controller')

    def do_get_current_channel(self):
        """
        Sets the currently active channel. Only available for the UC8 type controller
        """
        if self._ins_type == 'UC8':
            ans = int(self._visa.ask_for_values('CC?')[0])
        else:
            logging.warning(self.get_name()+': This function is only available for the UC8 type controller')
            return False
        return ans

    def do_set_jog(self, jogmode, channel): #OK!
        """
        Starts a jog motion at a defined speed or returns jog mode. 
        Defined steps are steps with step amplitude defined by the SU command 
        (default 16). Max. amplitude steps are equivalent to step amplitude 50:
        -4  Negative direction, 666 steps/s at defined step amplitude.
        -3  Negative direction, 1700 steps/s at max. step amplitude.
        -2  Negative direction, 100 step/s at max. step amplitude.
        -1  Negative direction, 5 steps/s at defined step amplitude.
        0   No move, go to READY state.
        1   Positive direction, 5 steps/s at defined step amplitude.
        2   Positive direction, 100 steps/s at max. step amplitude.
        3   Positive direction, 1700 steps/s at max. step amplitude.
        4   Positive direction, 666 steps/s at defined step amplitude.
        """
        axis=channel
        self._visa.write('%dJA%d'%(axis,jogmode))

    def do_get_position(self, channel): #DON'T USE WITH PR100
        """
        The MA command functions properly only with devices that feature a limit switch
        like models AG-LS25, AG-M050L and AG-M100L.
        """
        axis=channel
        ans = self._visa.ask_for_values('%dMA'%axis)[0]
        return ans


    def do_set_mode(self, mode): #OK!
        """
        To set the controller to local mode use 'L'. 
        To go to remote mode, use 'R'.
        In local mode the pushbuttons on the controller are enabled and all 
        commands that configure or operate the controller are disabled. 
        """        
        self._visa.write('M'+str(mode))

    def do_set_move_to_limit(self, jogmode, channel): #DON'T USE WITH PR100
        """
        Starts a jog motion at a defined speed to the limit and stops 
        automatically when the limit is activated. See JA command for details.
        The MA command functions properly only with devices that feature a 
        limit switch like models AG-LS25, AG-M050L and AG-M100L.
        """
        axis=channel
        self._visa.write('%dMV%d'%(axis,jogmode))


    def do_get_absolute_position(self, channel): #DON'T USE WITH PR100
        """
        This command functions properly only with devices that feature a 
        limit switch like models AG-LS25, AG-M050L and AG-M100L.
        """
        axis=channel
        ans = self._visa.ask('%dPA?'%axis)
        return ans

    def do_set_absolute_position(self, target_position, channel): #DON'T USE WITH PR100
        """
        This command functions properly only with devices that feature a 
        limit switch like models AG-LS25, AG-M050L and AG-M100L.
        The execution of the command can last up to 2 minutes.
        """
        axis=channel
        self._visa.write('%dPA%d'%(axis, target_position))

    def do_get_limit_status(self): #OK!
        """
        PH0 No limit switch is active
        PH1 Limit switch of axis #1 is active, limit switch of axis #2 is not active
        PH2 Limit switch of axis #2 is active, limit switch of axis #1 is not active
        PH3 Limit switch of axis #1 and axis #2 are active
        """        
        self._visa.write('PH')
        rawans = self._visa.read_values()[0]
        status_dict = {0 : 'No limit switch is active',
                1 : 'Limit switch of axis #1 is active, limit switch of axis #2 is not active',
                2 : 'Limit switch of axis #2 is active, limit switch of axis #1 is not active',
                3 : 'Limit switch of axis #1 and axis #2 are active'}

        return status_dict[rawans]

    def do_set_relative_position(self, noof_steps, channel, verbose = False): #OK!
        """
        Starts a relative move of noof_steps steps with step amplitude defined 
        by the SU command (default 16).
        noof_steps: Signed integer, between -2,147,483,648 and 2,147,483,647
        """
        axis=channel
        self._visa.write('%dPR%d'%(axis,noof_steps))

        if verbose:
            print 'Adjusted position by %d'%noof_steps

    def reset(self): #OK!
        """
        Resets the controller. All temporary settings are reset to default 
        and the controller is in local mode.
        """        
        
        self._visa.write('RS')

    def do_get_step_amplitude(self, channel, direction = '+'): #OK!
        """
        Returns the step amplitude (step amplitude) in positive or negative direction. 
        If the parameter is positive, it will set the step amplitude in the 
        forward direction. If the parameter is negative, it will set the step 
        amplitude in the backward direction.
        direction = '+' or '-' for positive or negative direction
        """
        axis=channel
        [ch, ans] = self._visa.ask_for_values('%dSU%s?'%(axis,direction))
        return int(ans)

    def do_set_step_amplitude(self, step_amplitude, channel): #OK!
        """
        Sets the step amplitude (step amplitude) in positive or negative direction. 
        If the parameter is positive, it will set the step amplitude in the 
        forward direction. If the parameter is negative, it will set the step 
        amplitude in the backward direction.
        step_amplitude = Integer between -50 and 50 included, except zero
        """
        axis=channel
        self._visa.write('%dSU%d'%(axis,step_amplitude))

    def do_get_error(self): #OK!
        """
        Returns error of the previous command.
        """  
        rawans = self._visa.ask('TE')
        err_dict = {0 : 'No error', 
                    -1 : 'Unknown command',
                    -2 : 'Axis out of range (must be 1 or 2, or must not be specified)',
                    -3 : 'Wrong format for parameter nn (or must not be specified)',
                    -4 : 'Parameter nn out of range',
                    -5 : 'Not allowed in local mode',
                    -6 : 'Not allowed in current state'}
        
        try:
            ans = err_dict[int(rawans[2:len(rawans)])]
        except:
            ans = 'No error'

        return ans

    def do_get_noof_steps(self, channel): #OK!
        """
        The TP command provides only limited information about the actual 
        position of the device. In particular, an Agilis device can be at 
        very different positions even though a TP command may return the same
        result.

        Returns TPnn, where nn is the number of accumulated steps in forward 
        direction minus the number of steps in backward direction as Integer.
        """
        axis=channel
        self._visa.write('%dTP'%axis)
        [ch_nr, ans] = self._visa.read_values()

        return int(ans)

    def do_get_status(self, channel, return_type = 'cooked'): #OK!
        """
        Input:
        return_type : "raw" (returns 0,...,3) or any other (returns a string)

        Returns:
        0   Ready (not moving)
        1   Stepping (currently executing a PR command)
        2   Jogging (currently executing a JA command with command
            parameter different than 0).
        3   Moving to limit (currently executing MV, MA, PA commands)
        """
        axis=channel
        [ch, rawans] = self._visa.ask_for_values('%dTS'%axis)
        status_dict = {0 : 'Ready (not moving)',
                1 : 'Stepping (currently executing a PR command)',
                2 :  'Jogging (currently executing a JA command with command parameter different than 0).', 
                3 : 'Moving to limit (currently executing MV, MA, PA commands)'}

        if return_type == 'raw':
            ret = int(rawans)
        else:
            ret = status_dict[rawans]

        return ret

    def do_get_firmware_version(self): #OK!
        """
        Returns the firmware version of the controller.
        """
        ans = self._visa.ask('VE')
        return ans


    def get_visa(self):
        return self._visa
    

    def quick_scan(self,steps,axis):
        """
        Scans a axis at maximum step speed, by an approxiamete number of steps. 
        """
        print 'Moving quick axis', axis,'with', steps, 'steps'   
        self.set('jog%d'%axis,np.sign(steps)*3)
        qt.msleep(abs(steps)/float(1700))
        self.set('jog%d'%axis,0)

    def precise_scan(self,steps,axis):
        """
        Moves by a number of steps relative to the current position. 

        """
        print 'Moving precize axis', axis,'with', steps, 'steps'         
        self.set('relative_position%d'%axis,steps)
        qt.msleep(abs(steps)/float(700))
        return True