#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
import msvcrt
from measurement.AWG_HW_sequencer_v2 import Sequence

from measurement.config import awgchannels_lt2 as awgcfg
from measurement.sequence import common as commonseq


name = 'SIL9_LT2'

nr_of_datapoints =          41      #max nr_of_datapoints should be < 10000
repetitions_per_datapoint = 1000

min_pulse_nr =              1    #in ns
max_pulse_nr =              41    #in ns

min_pulse_amp =             0.46
max_pulse_amp =             0.52
nr_of_pulses=               1

min_time =                  5
max_time =                  1000

f_drive =                   2.8283E9#2.85877E9#2.854E9         #in Hz
pi_pulse_length =           62
pi_over_two_length =        31
time_between_pulses =       10#476/2
mwpower_lt1 =               0               #in dBm
mwpower_lt2 =               20              #in dBm
f_mw = f_drive #- 30E6
amplitude_ssbmod = 0.48 #do not exceed 0.8, weird stuff happens: ask Wolfgang 

##########CORPSE############
pulse_420_length   =   145 # ns
pulse_300_length   =   103
pulse_60_length    =   21
time_between_CORPSE = 0 #ns

duty_cycle_time     = 5000 # ns, wait time at the end of each sequence element

max_seq_time = (pulse_420_length+pulse_300_length + pulse_60_length + 3*time_between_CORPSE + time_between_pulses)*max_pulse_nr+duty_cycle_time

pulse_nr = np.linspace(min_pulse_nr,max_pulse_nr,nr_of_datapoints)
amplitude = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
time=np.linspace(min_time,max_time,nr_of_datapoints)
lt1 = False

awg = qt.instruments['AWG']

def Multiple_Pi_pulses(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of Pi-pulses per element
    
    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,"amplitude": ...},
                "istate_pulse": {"duration":... , "amplitude":...}, First pulse to create init state
                "time_between_pulses": ...,
                "duty_cycle_time": ...,                             waiting time at the end of each element
                }
    '''
    seq = Sequence('spin_control')
    awgcfg.configure_sequence(seq,'mw')
    
    # vars for the channel names
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
    superposition_pulse=False
    
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
    
#FIXME: take this from a dictionary
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    pulse_nr = sweep_param

    pi = pulse_dict["Pi"]
    time_between_pulses = pulse_dict["time_between_pulses"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    istate_pulse = pulse_dict["init_state_pulse"]
    
    for i in np.arange(nr_of_datapoints):

        #create element for each datapoint and link last element to first
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        
        for j in np.arange(pulse_nr[i]):
  
            if j == 0:
                if init_state_pulse["Do_Pulse"]: 
                    seq.add_pulse('first_wait', channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1),start = 0, 
                        duration = 50, amplitude = 0)

                    seq.add_pulse('init_state_pulse' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                        start_reference = 'first_wait', link_start_to = 'end', start = 0, 
                        duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

                    seq.add_pulse('init_state_pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                        start_reference = 'init_state_pulse' + str(j), link_start_to = 'start', 
                        duration_reference = 'init_state_pulse'+str(j), link_duration_to = 'duration', 
                        amplitude = 2.0)

                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                        start_reference = 'init_state_pulse' + str(j), link_start_to='end',start = 0, 
                        duration = time_between_pulses, amplitude = 0)
                else:
                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = 50, amplitude = 0)
               
            else:
    
                seq.add_pulse('wait' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference = last,link_start_to ='end', 
                    duration = time_between_pulses, amplitude = 0)
            
            
            seq.add_pulse('pi' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait'+str(j), link_start_to = 'end', 
                duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)

        
            last = 'pi'+str(j)
        
        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start_reference = last,link_start_to ='end', 
                duration = duty_cycle_time, amplitude = 0)

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()

def Pi_Pulse_amp(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a fixed number of Pi pulses 
    and sweeps their amplitude
    
    sweep_param = numpy array with amplitude of Pi-pulses
    pulse_dict={
                "Pi":{"duration": ...},
                "Pi_2":   {"duration":..., "amplitude"...},
                "istate_pulse": {"duration":... , "amplitude":...,  First pulse to create init state
                                "Do_Pulse": Boolean},
                "time_between_pulses": ...,
                "nr_of_pulses":..,
                "duty_cycle_time": ...,                             waiting time at the end of each element
                }
    '''
    
    seq = Sequence('spin_control')
    awgcfg.configure_sequence(seq,'mw')
    # vars for the channel names
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
    
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
    
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10
    
    nr_of_datapoints = len(sweep_param)
    amplitude = sweep_param

    pi = pulse_dict["Pi"]
    istate_pulse = pulse_dict["init_state_pulse"]
    time_between_pulses = pulse_dict["time_between_pulses"]
    nr_of_pulses = pulse_dict["nr_of_pulses"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]

    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        for j in np.arange(nr_of_pulses):

            if j == 0:
                if init_state_pulse["Do_Pulse"]: 
                    seq.add_pulse('first_wait', channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1),start = 0, 
                        duration = 50, amplitude = 0)

                    seq.add_pulse('init_state_pulse' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                        start_reference = 'first_wait', link_start_to = 'end', start = 0, 
                        duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

                    seq.add_pulse('init_state_pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                        start_reference = 'init_state_pulse' + str(j), link_start_to = 'start', 
                        duration_reference = 'init_state_pulse'+str(j), link_duration_to = 'duration', 
                        amplitude = 2.0)

                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                        start_reference = 'init_state_pulse' + str(j), link_start_to='end',start = 0, 
                        duration = time_between_pulses, amplitude = 0)
                else:
                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = 50, amplitude = 0)
            else:
                seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = 50, amplitude = 0)
    
            seq.add_pulse('pi' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
               start = 0, start_reference = 'wait'+str(j), link_start_to = 'end',
               duration = pi["duration"], amplitude = amplitude[i], shape = 'rectangular')

            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
               start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
               start_reference = 'pi' + str(j), link_start_to = 'start', 
               duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
               amplitude = 2.0)
            
            last = 'pulse_mod'+str(j)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
            start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0)


    
    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()

def Multiple_DSC_Pulses(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of CORPSE-pulses per element
    
    A CORPSE Pi-pulse consists of 3 pulses along the x, -x and x direction
    along rotation angles of 420, 300 and 60 degrees.

    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,"amplitude": ...},
                "istate_pulse": {"duration":... , "amplitude":...}, First pulse to create init state
                "time_between_pulses": ...,                         wait time between each CORPSE-pulse
                "time_between_CORPSE": ...,                         wait time between the indivudeal pulses inside the CORPSE pulse
                "duty_cycle_time": ...,                             waiting time at the end of each element
                }
    '''

    seq = Sequence('spin_control')
    awgcfg.configure_sequence(seq,'mw')
    # vars for the channel names
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
    superposition_pulse=False
    
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
    
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    pulse_nr = sweep_param

    pi = pulse_dict["Pi"]
    istate_pulse = pulse_dict["init_state_pulse"]
    time_between_pulses = pulse_dict["time_between_pulses"]
    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]

    pulse_420_length = int(2.*pi["duration"]*(420./360.))
    pulse_300_length = int(2.*pi["duration"]*(300./360.))
    pulse_60_length = int(2.*pi["duration"]*(60./360.))

    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        

        for j in np.arange(pulse_nr[i]):
  
            if j == 0:
                if init_state_pulse["Do_Pulse"]: 
                    seq.add_pulse('first_wait', channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1),start = 0, 
                        duration = 50, amplitude = 0)

                    seq.add_pulse('init_state_pulse' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                        start_reference = 'first_wait', link_start_to = 'end', start = 0, 
                        duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

                    seq.add_pulse('init_state_pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                        start_reference = 'init_state_pulse' + str(j), link_start_to = 'start', 
                        duration_reference = 'init_state_pulse'+str(j), link_duration_to = 'duration', 
                        amplitude = 2.0)

                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                        start_reference = 'init_state_pulse' + str(j), link_start_to='end',start = 0, 
                        duration = time_between_pulses, amplitude = 0)
                else:
                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = 50, amplitude = 0)
            else:
                seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = time_between_pulses, amplitude = 0)

    
            seq.add_pulse('pulse_420' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait'+str(j), link_start_to = 'end', 
                duration = pulse_420_length, amplitude = pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod_420' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_420' + str(j), link_start_to = 'start', 
                duration_reference = 'pulse_420'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)
 
            seq.add_pulse('wait_1' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_mod_420'+str(j),link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_300' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_1'+str(j),link_start_to = 'end', 
                duration = pulse_300_length, amplitude = -1*pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_300' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_300' + str(j), link_start_to = 'start', 
                duration_reference = 'pulse_300'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)
 
            seq.add_pulse('wait_2' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_mod_300'+str(j),link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_60' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_2'+str(j), link_start_to = 'end', 
                duration = pulse_60_length, amplitude = pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_60' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_60' + str(j), link_start_to = 'start', 
                duration_reference = 'pulse_60'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)

           
            last = 'pulse_60'+str(j)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
        start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0) 

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()

def DSC_pulses_amp(sweep_param,pulse_dict,lt1 = False,do_program=True,do_program=True):
    '''
    This sequence consists of a fixed number of CORPSE pulses 
    and sweeps their amplitude
    
    sweep_param = numpy array with amplitude of CORPSE-pulses
    pulse_dict={
                "Pi":{"duration": ...},
                "istate_pulse": {"duration":... , "amplitude":...,  First pulse to create init state
                                "Do_Pulse": Boolean},
                "time_between_pulses": ...,                         waiting time between the CORPSE-pulses
                "time_between_CORPSE":...,                          waiting time between each individual pulse inside the CORPSE pulse sequence
                "duty_cycle_time": ...,                             waiting time at the end of each element
                "nr_of_pulses": ...,
                }
    '''
    seq = Sequence('spin_control')
    awgcfg.configure_sequence(seq,'mw')
    # vars for the channel names
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
    
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
    
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    amplitude = sweep_param

    pi = pulse_dict["Pi"]
    istate_pulse = pulse_dict["init_state_pulse"]
    time_between_pulses = pulse_dict["time_between_pulses"]
    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    nr_of_pulses = pulse_dict["nr_of_pulses"]

    pulse_420_length = int(2.*pi["duration"]*(420./360.))
    pulse_300_length = int(2.*pi["duration"]*(300./360.))
    pulse_60_length = int(2.*pi["duration"]*(60./360.))


    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        
    
        for j in np.arange(nr_of_pulses):
        
            if j == 0:
                if init_state_pulse["Do_Pulse"]: 
                    seq.add_pulse('first_wait', channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1),start = 0, 
                        duration = 50, amplitude = 0)

                    seq.add_pulse('init_state_pulse' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                        start_reference = 'first_wait', link_start_to = 'end', start = 0, 
                        duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

                    seq.add_pulse('init_state_pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                            start_reference = 'init_state_pulse' + str(j), link_start_to = 'start', 
                            duration_reference = 'init_state_pulse'+str(j), link_duration_to = 'duration', 
                            amplitude = 2.0)

                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                            start_reference = 'init_state_pulse' + str(j), link_start_to='end',start = 0, 
                            duration = time_between_pulses, amplitude = 0)
                else:
                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = 50, amplitude = 0)
            else:
                seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = time_between_pulses, amplitude = 0)

            seq.add_pulse('pulse_420' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait'+str(j),link_start_to = 'end', 
                duration = pulse_420_length, amplitude = amplitude[i], shape = 'rectangular')

            seq.add_pulse('pulse_mod_420' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_420' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_420'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)
 
            seq.add_pulse('wait_1' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference = 'pulse_mod_420'+str(j),link_start_to ='end', 
                    duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_300' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_1'+str(j), link_start_to = 'end',
                duration = pulse_300_length, amplitude = -amplitude[i],shape = 'rectangular')

            seq.add_pulse('pulse_mod_300' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_300' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_300'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)
 
            seq.add_pulse('wait_2' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference = 'pulse_mod_300'+str(j),link_start_to ='end', 
                    duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_60' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_2'+str(j), link_start_to = 'end', 
                duration = pulse_60_length, amplitude = amplitude[i],shape = 'rectangular')

            seq.add_pulse('pulse_mod_60' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_60' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_60'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)

            last = 'Pulse_60'+str(j)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
            start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0) 



    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()




def DSC_Pulses_time(do_program=True):
        '''
    This sequence consists of a fixed number of CORPSE pulses 
    and sweeps the time between the individual pulses in the CORPSE pulse sequence
    
    sweep_param = numpy array with time between each pulse in the CORPSE pulses sequence
    pulse_dict={
                "Pi":{"duration": ..., "amplitude":... ,},
                "istate_pulse": {"duration":... , "amplitude":...,  First pulse to create init state
                                "Do_Pulse": Boolean},
                "time_between_pulses": ...,                         waiting time between the CORPSE-pulses
                "duty_cycle_time": ...,                             waiting time at the end of each element
                "nr_of_pulses": ...,
                }
    '''
    seq = Sequence('spin_control')
    awgcfg.configure_sequence(seq,'mw')
    # vars for the channel names
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
    
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
    
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    time_between_CORPSE = sweep_param

    pi = pulse_dict["Pi_pulse"]
    istate_pulse = pulse_dict["init_state_pulse"]
    time_between_pulses = pulse_dict["time_between_pulses"]

    duty_cycle_time = pulse_dict["duty_cycle_time"]
    nr_of_pulses = pulse_dict["nr_of_pulses"]

    pulse_420_length = int(2.*pi["duration"]*(420./360.))
    pulse_300_length = int(2.*pi["duration"]*(300./360.))
    pulse_60_length = int(2.*pi["duration"]*(60./360.))


    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        
    
        for j in np.arange(nr_of_pulses):
        
            if j == 0:
                if init_state_pulse["Do_Pulse"]: 
                    seq.add_pulse('first_wait', channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1),start = 0, 
                        duration = 50, amplitude = 0)

                    seq.add_pulse('init_state_pulse' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                        start_reference = 'first_wait', link_start_to = 'end', start = 0, 
                        duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

                    seq.add_pulse('init_state_pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                            start_reference = 'init_state_pulse' + str(j), link_start_to = 'start', 
                            duration_reference = 'init_state_pulse'+str(j), link_duration_to = 'duration', 
                            amplitude = 2.0)

                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                            start_reference = 'init_state_pulse' + str(j), link_start_to='end',start = 0, 
                            duration = time_between_pulses, amplitude = 0)
                else:
                    seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = 50, amplitude = 0)
            else:
                seq.add_pulse('wait' + str(j), channel = chan_mw_pm, 
                        element = 'spin_control_'+str(i+1), start = 0, 
                        duration = time_between_pulses, amplitude = 0)

            seq.add_pulse('pulse_420' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait'+str(j),link_start_to = 'end', 
                duration = pulse_420_length, amplitude = pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod_420' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_420' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_420'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)
 
            seq.add_pulse('wait_1' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference = 'pulse_mod_420'+str(j),link_start_to ='end', 
                    duration = time_between_CORPSE[i], amplitude = 0)

            seq.add_pulse('pulse_300' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_1'+str(j), link_start_to = 'end',
                duration = pulse_300_length, amplitude = -1*pi["duration"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_300' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_300' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_300'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)
 
            seq.add_pulse('wait_2' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference = 'pulse_mod_300'+str(j),link_start_to ='end', 
                    duration = time_between_CORPSE[i], amplitude = 0)

            seq.add_pulse('pulse_60' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_2'+str(j), link_start_to = 'end', 
                duration = pulse_60_length, amplitude = pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_60' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_60' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_60'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)

            last = 'Pulse_60'+str(j)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
            start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0) 



    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    seq.send_sequence()



def spin_control(name, data, par):
    par['green_repump_voltage'] = ins_green_aom.power_to_voltage(par['green_repump_amplitude'])
    par['green_off_voltage'] = 0.01#ins_green_aom.power_to_voltage(par['green_off_amplitude'])
    par['Ex_CR_voltage'] = ins_E_aom.power_to_voltage(par['Ex_CR_amplitude'])
    par['A_CR_voltage'] = ins_A_aom.power_to_voltage(par['A_CR_amplitude'])
    par['Ex_SP_voltage'] = ins_E_aom.power_to_voltage(par['Ex_SP_amplitude'])
    par['A_SP_voltage'] = ins_A_aom.power_to_voltage(par['A_SP_amplitude'])
    par['Ex_RO_voltage'] = ins_E_aom.power_to_voltage(par['Ex_RO_amplitude'])
    par['A_RO_voltage'] = ins_A_aom.power_to_voltage(par['A_RO_amplitude'])

    if  (par['SP_duration'] > max_SP_bins) or \
        (par['sweep_length']*par['RO_duration'] > max_RO_dim):
            print ('Error: maximum dimensions exceeded')
            return(-1)

    #print 'SP E amplitude: %s'%par['Ex_SP_voltage']
    #print 'SP A amplitude: %s'%par['A_SP_voltage']

    adwin.start_spincontrol(
        counter_channel = par['counter_channel'],
        green_laser_DAC_channel = par['green_laser_DAC_channel'],
        Ex_laser_DAC_channel = par['Ex_laser_DAC_channel'],
        A_laser_DAC_channel = par['A_laser_DAC_channel'],
        AWG_start_DO_channel = par['AWG_start_DO_channel'],
        AWG_done_DI_channel = par['AWG_done_DI_channel'],
        send_AWG_start = par['send_AWG_start'],
        wait_for_AWG_done = par['wait_for_AWG_done'],
        green_repump_duration = par['green_repump_duration'],
        CR_duration = par['CR_duration'],
        SP_duration = par['SP_duration'],
        SP_filter_duration = par['SP_filter_duration'],
        sequence_wait_time = par['sequence_wait_time'],
        wait_after_pulse_duration = par['wait_after_pulse_duration'],
        CR_preselect = par['CR_preselect'],
        RO_repetitions = par['RO_repetitions'],
        RO_duration = par['RO_duration'],
        sweep_length = par['sweep_length'],
        cycle_duration = par['cycle_duration'],
        green_repump_voltage = par['green_repump_voltage'],
        green_off_voltage = par['green_off_voltage'],
        Ex_CR_voltage = par['Ex_CR_voltage'],
        A_CR_voltage = par['A_CR_voltage'],
        Ex_SP_voltage = par['Ex_SP_voltage'],
        A_SP_voltage = par['A_SP_voltage'],
        Ex_RO_voltage = par['Ex_RO_voltage'],
        A_RO_voltage = par['A_RO_voltage'])
        
    if lt1:
        adwin_lt2.start_check_trigger_from_lt1()

    CR_counts = 0
    while (physical_adwin.Process_Status(9) == 1):
        reps_completed = physical_adwin.Get_Par(73)
        CR_counts = physical_adwin.Get_Par(70) - CR_counts
        cts = physical_adwin.Get_Par(26)
        trh = physical_adwin.Get_Par(25)
        print('completed %s / %s readout repetitions, %s CR counts/s'%(reps_completed,par['RO_repetitions'], CR_counts))
        print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break

        qt.msleep(2.5)
    physical_adwin.Stop_Process(9)
    
    if lt1:
        adwin_lt2.stop_check_trigger_from_lt1()

    reps_completed  = physical_adwin.Get_Par(73)
    print('completed %s / %s readout repetitions'%(reps_completed,par['RO_repetitions']))

    sweep_length = par['sweep_length']
    par_long   = physical_adwin.Get_Data_Long(20,1,25)
    par_float  = physical_adwin.Get_Data_Float(20,1,10)
    CR_before = physical_adwin.Get_Data_Long(22,1,1)
    CR_after  = physical_adwin.Get_Data_Long(23,1,1)
    SP_hist   = physical_adwin.Get_Data_Long(24,1,par['SP_duration'])
    RO_data   = physical_adwin.Get_Data_Long(25,1,
                    sweep_length * par['RO_duration'])
    RO_data = reshape(RO_data,(sweep_length,par['RO_duration']))
    SSRO_data   = physical_adwin.Get_Data_Long(27,1,
                    sweep_length * par['RO_duration'])
    SSRO_data = reshape(SSRO_data,(sweep_length,par['RO_duration']))
    statistics = physical_adwin.Get_Data_Long(26,1,10)

    sweep_index = arange(sweep_length)
    sp_time = arange(par['SP_duration'])*par['cycle_duration']*3.333
    ro_time = arange(par['RO_duration'])*par['cycle_duration']*3.333


    data.save()
    savdat={}
    savdat['counts']=CR_after
    data.save_dataset(name='ChargeRO_after', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=sp_time
    savdat['counts']=SP_hist
    data.save_dataset(name='SP_histogram', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=ro_time
    savdat['sweep_axis']=sweep_index
    savdat['counts']=RO_data
    savdat['SSRO_counts']=SSRO_data
    data.save_dataset(name='Spin_RO', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['par_long']=par_long
    savdat['par_float']=par_float
    data.save_dataset(name='parameters', do_plot=False, 
        data = savdat, idx_increment = False)
    
    ######################
    ###statistics file####
    ######################
    savdat={}
    savdat['completed_repetitions']=(reps_completed/sweep_length)
    savdat['total_repumps']=statistics[0]
    savdat['total_repump_counts']=statistics[1]
    savdat['noof_failed_CR_checks']=statistics[2]
    savdat['mw_center_freq']=f_mw
    savdat['mw_drive_freq']=f_drive
    savdat['mw_power']=mwpower
    savdat['min_pulse_nr']=min_pulse_nr
    savdat['max_pulse_nr']=max_pulse_nr
    savdat['min_pulse_amp']=min_pulse_amp
    savdat['max_pulse_amp']=max_pulse_amp
    savdat['min_time'] = min_time
    savdat['max_time'] = max_time
    savdat['noof_datapoints']=nr_of_datapoints
    
    data.save_dataset(name='statics_and_parameters', do_plot=False, 
        data = savdat, idx_increment = True)
   
    return 

def end_measurement():
    awg.stop()
    awg.set_runmode('CONT')
    adwin.set_simple_counting()
    counters.set_is_running(True)
    ins_green_aom.set_power(200e-6)   
    microwaves.set_status('off')
    microwaves.set_iq('off')
    microwaves.set_pulm('off')
    ins_E_aom.set_power(0)
    ins_A_aom.set_power(0)



def power_and_mw_ok():
    ret = True
    max_E_power = ins_E_aom.get_cal_a()
    max_A_power = ins_A_aom.get_cal_a()
    if (max_E_power < par['Ex_CR_amplitude']) or \
            (max_E_power < par['Ex_SP_amplitude']) or \
            (max_E_power < par['Ex_RO_amplitude']):
        print 'Trying to set too large value for E laser, quiting!'
        ret = False    
    if (max_A_power < par['A_CR_amplitude']) or \
            (max_A_power < par['A_SP_amplitude']) or \
            (max_A_power < par['A_RO_amplitude']):
        print 'Trying to set too large value for A laser, quiting'
        ret = False
    if mwpower > 0:
        print 'MW power > 0 dBm, are you sure you want to continue? Press q to quit, c to continue.'
        idx = 0
        max_idx = 5
        kb_hit = None
        while (idx<max_idx) and kb_hit == None:
            kb_hit = msvcrt.getch()
            if kb_hit == 'q':
                ret = False
            if kb_hit == 'c':
                ret = True
            qt.msleep(1)
            idx += 1
       
    return ret

def main():
    if power_and_mw_ok():
        counters.set_is_running(False)
        generate_DSC_sequence()
        awg.set_runmode('SEQ')
        awg.start()  
        while awg.get_state() != 'Waiting for trigger':
            qt.msleep(1)
        data = meas.Measurement(name,'41_CORPSE_pulses_62ns')
        microwaves.set_status('on')
        spin_control(name,data,par)
        end_measurement()
    else:
        print 'Measurement aborted.'


if __name__ == '__main__':
    main()


