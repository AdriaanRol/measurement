#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels_lt2 as awgcfg

awg = qt.instruments['AWG']


def Rabi(sweep_param,pulse_dict,lt1 = False,do_program=True):
#FIXME: import this from a mwseq_general script with rabi, ramsey, SE.

    seq = Sequence('spin_control')
    awgcfg.configure_sequence(seq,'mw')
    # vars for the channel names
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
    
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod' #ch1
        chan_mwQ = 'MW_Qmod' #ch3
    
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    pi = pulse_dict["Pi"]
    length = sweep_param
    nr_of_datapoints = len(sweep_param)

    for i in np.arange(len(length)):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        seq.add_pulse('wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0, duration = 100, amplitude = 0)

        if length[i] != 0:
            seq.add_pulse('mwburst', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                    start = 0, duration = length[i], amplitude = pi["amplitude"], start_reference = 'wait',
                    link_start_to = 'end', shape = 'rectangular')

            seq.add_pulse('pulse_mod', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'mwburst', link_start_to = 'start', 
                duration_reference = 'mwburst', link_duration_to = 'duration', 
                amplitude = 2.0)
 

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()
    print 'Longest sequence element: %d us'%max_seq_time


    name = 'Rabi'
    return {"seqname":name, "max_seq_time":max_seq_time}

def Multiple_Pi_pulses(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of Pi-pulses per element
    
    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,
                      "amplitude": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state
                
                "time_between_pulses": ...,
                
                "duty_cycle_time": ...,            waiting time at the end of each element
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
                if istate_pulse["Do_Pulse"]: 
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
    max_seq_time = seq.send_sequence()

    name= 'Multiple_Pi_pulses'
    return {"seqname":name, "max_seq_time":max_seq_time}

def Pi_Pulse_amp(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a fixed number of Pi pulses 
    and sweeps their amplitude
    
    sweep_param = numpy array with amplitude of Pi-pulses
    pulse_dict={
                "Pi":{"duration": ...},
                
                "Pi_2":   {"duration":..., 
                           "amplitude"...},
                
                "istate_pulse": {"duration":... , 
                                 "amplitude":...,       First pulse to create init state
                                 "Do_Pulse": Boolean},
                "time_between_pulses": ...,
                
                "nr_of_pulses":..,
                
                "duty_cycle_time": ...,                 waiting time at the end of each element
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
                if istate_pulse["Do_Pulse"]: 
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
                        start_reference=last, link_start_to='end',
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
    max_seq_time = seq.send_sequence()
    print 'Longest sequence element: %d us'%max_seq_time
    name = str(nr_of_pulses) + 'Pi_Pulse_amp'

    return {"seqname":name, "max_seq_time":max_seq_time}


def Multiple_DSC_Pulses(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of CORPSE-pulses per element
    
    A CORPSE Pi-pulse consists of 3 pulses along the x, -x and x direction
    along rotation angles of 420, 300 and 60 degrees.

    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,
                      "amplitude": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state

                "time_between_pulses": ...,        wait time between each CORPSE-pulse
                
                "time_between_CORPSE": ...,        wait time between the indivudeal pulses inside the CORPSE pulse
                
                "duty_cycle_time": ...,            wait time at the end of each element
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
                if istate_pulse["Do_Pulse"]: 
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
    max_seq_time = seq.send_sequence()


    name = 'Multiple_CORPSE_pulses'
    return {"seqname":name, "max_seq_time":max_seq_time}

def DSC_pulse_amp(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a fixed number of CORPSE pulses 
    and sweeps their amplitude
    
    sweep_param = numpy array with amplitude of CORPSE-pulses
    pulse_dict={
                "Pi":{"duration": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...,       First pulse to create init state
                                 "Do_Pulse": Boolean},

                "time_between_pulses": ...,             wait time between the CORPSE-pulses
                
                "time_between_CORPSE":...,              wait time between each individual pulse inside the CORPSE pulse sequence
                
                "duty_cycle_time": ...,                 wait time at the end of each element
                
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
                if istate_pulse["Do_Pulse"]: 
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
                        duration = time_between_pulses, amplitude = 0,
                        start_reference=last,link_start_to='end')

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
    max_seq_time = seq.send_sequence()

    name = str(nr_of_pulses) + 'CORPSE_pulse_amp'
    return {"seqname":name, "max_seq_time":max_seq_time}

def DSC_Pulse_time(sweep_param,pulse_dict,do_program=True):
    '''
    This sequence consists of a fixed number of CORPSE pulses 
    and sweeps the time between the individual pulses in the CORPSE pulse sequence
    
    sweep_param = numpy array with time between each pulse in the CORPSE pulses sequence
    pulse_dict={
                "Pi":{"duration": ..., 
                      "amplitude":... ,},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...,      First pulse to create init state
                                 "Do_Pulse": Boolean},
                
                "time_between_pulses": ...,            wait time between the CORPSE-pulses
                
                "duty_cycle_time": ...,                wait time at the end of each element
                
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

    pi = pulse_dict["Pi"]
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
                if istate_pulse["Do_Pulse"]: 
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
    max_seq_time = seq.send_sequence()

    name = str(nr_of_pulses) + 'CORPSE_Pulse_time'
    return {"seqname":name, "max_seq_time":max_seq_time}

def DSC_pi_over_two_pulse_amp(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a fixed number of CORPSE pulses 
    and sweeps their amplitude
    
    sweep_param = numpy array with amplitude of CORPSE-pulses
    pulse_dict={
                "Pi":{"duration": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...,       First pulse to create init state
                                 "Do_Pulse": Boolean},

                "time_between_pulses": ...,             wait time between the CORPSE-pulses
                
                "time_between_CORPSE":...,              wait time between each individual pulse inside the CORPSE pulse sequence
                
                "duty_cycle_time": ...,                 wait time at the end of each element
                
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

    pulse_384_length = int(2.*pi["duration"]*(384.3/360.))
    pulse_318_length = int(2.*pi["duration"]*(318.6/360.))
    pulse_24_length = int(2.*pi["duration"]*(24.3/360.))


    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        
    
        for j in np.arange(nr_of_pulses):
        
            if j == 0:
                if istate_pulse["Do_Pulse"]: 
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
                        duration = time_between_pulses, amplitude = 0,
                        start_reference=last,link_start_to='end')

            seq.add_pulse('pulse_384' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait'+str(j),link_start_to = 'end', 
                duration = pulse_384_length, amplitude = amplitude[i], shape = 'rectangular')

            seq.add_pulse('pulse_mod_384' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_384' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_384'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)
 
            seq.add_pulse('wait_1' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference = 'pulse_mod_384'+str(j),link_start_to ='end', 
                    duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_318' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_1'+str(j), link_start_to = 'end',
                duration = pulse_318_length, amplitude = -amplitude[i],shape = 'rectangular')

            seq.add_pulse('pulse_mod_318' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_318' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_318'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)
 
            seq.add_pulse('wait_2' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start = 0,start_reference = 'pulse_mod_318'+str(j),link_start_to ='end', 
                    duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_24' + str(j), channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_2'+str(j), link_start_to = 'end', 
                duration = pulse_24_length, amplitude = amplitude[i],shape = 'rectangular')

            seq.add_pulse('pulse_mod_24' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                    start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                    start_reference = 'pulse_24' + str(j), link_start_to = 'start', 
                    duration_reference = 'pulse_24'+str(j), link_duration_to = 'duration', 
                    amplitude = 2.0)

            last = 'pulse_24'+str(j)
        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
            start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0) 



    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()

    name = str(nr_of_pulses) + 'CORPSE_pulse_amp'
    return {"seqname":name, "max_seq_time":max_seq_time}

def SE_DSC(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    SE with CORPSE pulses, sweep second tau.
    
    
    sweep_param = numpy array with amplitude of CORPSE-pulses
    pulse_dict={
                "Pi":{"duration": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...,       First pulse to create init state
                                 "Do_Pulse": Boolean},

                "time_between_pulses": ...,             wait time between the CORPSE-pulses
                
                "time_between_CORPSE":...,              wait time between each individual pulse inside the CORPSE pulse sequence
                
                "duty_cycle_time": ...,                 wait time at the end of each element
                
                "nr_of_pulses": ...,
                "tau1":...,
                "CORPSE":{"pi":..,"pi_over_two":..,}
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
    MW_pulsemod_amplitude=2.0
    nr_of_datapoints = len(sweep_param)

    pi = pulse_dict["Pi"]
    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    nr_of_pulses = pulse_dict["nr_of_pulses"]

    pulse_420_length = int(2.*pi["duration"]*(420./360.))
    pulse_300_length = int(2.*pi["duration"]*(300./360.))
    pulse_60_length = int(2.*pi["duration"]*(60./360.))

    pulse_384_length = int(2.*pi["duration"]*(384.3/360.))
    pulse_318_length = int(2.*pi["duration"]*(318.6/360.))
    pulse_24_length = int(2.*pi["duration"]*(24.3/360.))
    
    tau1 =  pulse_dict["tau1"]
    CORPSE_pi_amp = pulse_dict["CORPSE"]["pi"]
    CORPSE_pi_over_two_amp = pulse_dict["CORPSE"]["pi_over_two"]

    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)


        seq.add_pulse('first_wait', channel = chan_mw_pm, 
            element = 'spin_control_'+str(i+1),start = 0, 
            duration = 50, amplitude = 0)

        ## pi/2 Pulse
        seq.add_pulse('pulse_384', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'first_wait',link_start_to = 'end', 
                duration = pulse_384_length, 
                amplitude = CORPSE_pi_over_two_amp, shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_384', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_384',link_duration_to='duration',start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_384', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_1', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_1', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -CORPSE_pi_over_two_amp,shape = 'rectangular')
        
        seq.add_pulse('pulse_mod_318', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_318',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_318', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_2', link_start_to = 'end', 
                duration = pulse_24_length, 
                amplitude = CORPSE_pi_over_two_amp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_24', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_24',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_24', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)

        last = 'pulse_24'


        ### First wait time
        seq.add_pulse('tau_1', channel = chan_mw_pm, 
                element = 'spin_control_'+str(i+1),start = 0,
                start_reference= last  ,link_start_to = 'end', 
                duration = tau1, amplitude = 0)


        ### Pi pulse
        seq.add_pulse('pulse_420', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_1',link_start_to = 'end', 
                duration = pulse_420_length, 
                amplitude = CORPSE_pi_amp, shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_420', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_420',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_420', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_3', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_420',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_300', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_3', link_start_to = 'end',
                duration = pulse_300_length, 
                amplitude = -CORPSE_pi_amp,shape = 'rectangular')
        
        seq.add_pulse('pulse_mod_300', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_300',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_300', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_4', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_300',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_60', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_4', link_start_to = 'end', 
                duration = pulse_60_length, 
                amplitude = CORPSE_pi_amp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_60', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_60',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_60', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)

        last = 'pulse_60'
        #Second wait time
        seq.add_pulse('tau_2', channel = chan_mw_pm, 
                element = 'spin_control_'+str(i+1),start = 0,
                start_reference= last  ,link_start_to = 'end', 
                duration = sweep_param[i], amplitude = 0)
        
        #Final Pi over 2
        seq.add_pulse('pulse_384_2', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_2',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = CORPSE_pi_over_two_amp, 
                shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_384_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_384_2', link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_384_2', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_5', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_384_2',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318_2', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_5', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -CORPSE_pi_over_two_amp,shape = 'rectangular')
        
        seq.add_pulse('pulse_mod_318_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference = 'pulse_318_2',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_318_2', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_6', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_318_2',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24_2', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_6', link_start_to = 'end', 
                duration = pulse_24_length,  
                amplitude = CORPSE_pi_over_two_amp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_24_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_24_2',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_24_2', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
    
    
        last='pulse_24_2' 
  
        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0) 



    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()

    name = str(nr_of_pulses) + 'CORPSE_pulse_amp'
    return {"seqname":name, "max_seq_time":max_seq_time}


def SE_DSC_phase(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    SE with CORPSE pulses, sweep second tau.
    
    
    sweep_param = numpy array with amplitude of CORPSE-pulses
    pulse_dict={
                "Pi":{"duration": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...,       First pulse to create init state
                                 "Do_Pulse": Boolean},

                "time_between_pulses": ...,             wait time between the CORPSE-pulses
                
                "time_between_CORPSE":...,              wait time between each individual pulse inside the CORPSE pulse sequence
                
                "duty_cycle_time": ...,                 wait time at the end of each element
                
                "nr_of_pulses": ...,
                "tau1":...,
                "CORPSE":{"pi":..,"pi_over_two":..,}
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
    MW_pulsemod_amplitude=2.0
    nr_of_datapoints = len(sweep_param)

    pi = pulse_dict["Pi"]
    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    nr_of_pulses = pulse_dict["nr_of_pulses"]

    pulse_420_length = int(2.*pi["duration"]*(420./360.))
    pulse_300_length = int(2.*pi["duration"]*(300./360.))
    pulse_60_length = int(2.*pi["duration"]*(60./360.))

    pulse_384_length = int(2.*pi["duration"]*(384.3/360.))
    pulse_318_length = int(2.*pi["duration"]*(318.6/360.))
    pulse_24_length = int(2.*pi["duration"]*(24.3/360.))
    
    tau =  pulse_dict["tau"]
    CORPSE_pi_amp = pulse_dict["CORPSE"]["pi"]
    CORPSE_pi_over_two_amp = pulse_dict["CORPSE"]["pi_over_two"]
    basis_rot_angle=sweep_param

    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)


        seq.add_pulse('first_wait', channel = chan_mw_pm, 
            element = 'spin_control_'+str(i+1),start = 0, 
            duration = 50, amplitude = 0)

        ## pi/2 Pulse
        seq.add_pulse('pulse_384', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'first_wait',link_start_to = 'end', 
                duration = pulse_384_length, 
                amplitude = CORPSE_pi_over_two_amp, shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_384', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_384',link_duration_to='duration',start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_384', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_1', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_1', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -CORPSE_pi_over_two_amp,shape = 'rectangular')
        
        seq.add_pulse('pulse_mod_318', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_318',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_318', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_2', link_start_to = 'end', 
                duration = pulse_24_length, 
                amplitude = CORPSE_pi_over_two_amp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_24', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_24',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_24', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)

        last = 'pulse_24'


        ### First wait time
        seq.add_pulse('tau_1', channel = chan_mw_pm, 
                element = 'spin_control_'+str(i+1),start = 0,
                start_reference= last  ,link_start_to = 'end', 
                duration = tau, amplitude = 0)


        ### Pi pulse
        seq.add_pulse('pulse_420', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_1',link_start_to = 'end', 
                duration = pulse_420_length, 
                amplitude = CORPSE_pi_amp, shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_420', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_420',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_420', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_3', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_420',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_300', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_3', link_start_to = 'end',
                duration = pulse_300_length, 
                amplitude = -CORPSE_pi_amp,shape = 'rectangular')
        
        seq.add_pulse('pulse_mod_300', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_300',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_300', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_4', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_300',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_60', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_4', link_start_to = 'end', 
                duration = pulse_60_length, 
                amplitude = CORPSE_pi_amp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_60', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_60',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_60', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)

        last = 'pulse_60'
        #Second wait time
        seq.add_pulse('tau_2', channel = chan_mw_pm, 
                element = 'spin_control_'+str(i+1),start = 0,
                start_reference= last  ,link_start_to = 'end', 
                duration = tau, amplitude = 0)
        
        Iamp = np.cos(np.pi*basis_rot_angle[i]/180.)*CORPSE_pi_over_two_amp
        Qamp = np.sin(np.pi*basis_rot_angle[i]/180.)*CORPSE_pi_over_two_amp
        #Final Pi over 2
        seq.add_pulse('pulse_384_2_I', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_2',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = Iamp, 
                shape = 'rectangular')
        seq.add_pulse('pulse_384_2_Q', channel = chan_mwQ, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_2',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = Qamp, 
                shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_384_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = max(pulse_300_length+\
                    2*MW_pulse_mod_risetime,
                    pulse_384_length+\
                    2*MW_pulse_mod_risetime), 
                duration_reference='pulse_384_2_I', link_duration_to='duration',
                start = min(-MW_pulse_mod_risetime,
                    (pulse_384_length-pulse_384_length)/2 - \
                    MW_pulse_mod_risetime),
                start_reference = 'pulse_384_2_I', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_5', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_384_2_I',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318_2_I', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_5', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -Iamp,shape = 'rectangular')
        seq.add_pulse('pulse_318_2_Q', channel = chan_mwQ, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_5', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -Qamp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = max(pulse_300_length+\
                    2*MW_pulse_mod_risetime,
                    pulse_318_length+\
                    2*MW_pulse_mod_risetime), 
                duration_reference = 'pulse_318_2_I',link_duration_to='duration',
                start = min(-MW_pulse_mod_risetime,
                    (pulse_318_length-pulse_318_length)/2 - \
                    MW_pulse_mod_risetime),
                start_reference = 'pulse_318_2_I', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_6', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_318_2_I',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24_2_I', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_6', link_start_to = 'end', 
                duration = pulse_24_length,  
                amplitude = Iamp,shape = 'rectangular')
        seq.add_pulse('pulse_24_2_Q', channel = chan_mwQ, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_6', link_start_to = 'end', 
                duration = pulse_24_length,  
                amplitude = Qamp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_24_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = max(pulse_300_length+\
                    2*MW_pulse_mod_risetime,
                    pulse_24_length+\
                    2*MW_pulse_mod_risetime), 
                duration_reference='pulse_24_2_I',link_duration_to='duration',
                start =min(-MW_pulse_mod_risetime,
                    (pulse_24_length-pulse_24_length)/2 - \
                    MW_pulse_mod_risetime),
                start_reference = 'pulse_24_2_I', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
    
    
        last='pulse_24_2_I' 
  
        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0) 



    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()

    name = str(nr_of_pulses) + 'CORPSE_pulse_amp'
    return {"seqname":name, "max_seq_time":max_seq_time}


def SE_DSC_check_sweep_first_pi_over_two(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    SE with CORPSE pulses, sweep second tau.
    
    
    sweep_param = numpy array with amplitude of CORPSE-pulses
    pulse_dict={
                "Pi":{"duration": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...,       First pulse to create init state
                                 "Do_Pulse": Boolean},

                "time_between_pulses": ...,             wait time between the CORPSE-pulses
                
                "time_between_CORPSE":...,              wait time between each individual pulse inside the CORPSE pulse sequence
                
                "duty_cycle_time": ...,                 wait time at the end of each element
                
                "nr_of_pulses": ...,
                "tau1":...,
                "CORPSE":{"pi":..,"pi_over_two":..,}
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
    MW_pulsemod_amplitude=2.0
    nr_of_datapoints = len(sweep_param)

    pi = pulse_dict["Pi"]
    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    nr_of_pulses = pulse_dict["nr_of_pulses"]

    pulse_420_length = int(2.*pi["duration"]*(420./360.))
    pulse_300_length = int(2.*pi["duration"]*(300./360.))
    pulse_60_length = int(2.*pi["duration"]*(60./360.))

    pulse_384_length = int(2.*pi["duration"]*(384.3/360.))
    pulse_318_length = int(2.*pi["duration"]*(318.6/360.))
    pulse_24_length = int(2.*pi["duration"]*(24.3/360.))
    basis_rot_angle = 0
    tau =  pulse_dict["tau"]

    

    for i in np.arange(nr_of_datapoints):
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

        CORPSE_pi_over_two_amp = sweep_param[i]
        seq.add_pulse('first_wait', channel = chan_mw_pm, 
            element = 'spin_control_'+str(i+1),start = 0, 
            duration = 50, amplitude = 0)

        ## pi/2 Pulse
        seq.add_pulse('pulse_384', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'first_wait',link_start_to = 'end', 
                duration = pulse_384_length, 
                amplitude = CORPSE_pi_over_two_amp, shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_384', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_384',link_duration_to='duration',start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_384', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_1', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_1', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -CORPSE_pi_over_two_amp,shape = 'rectangular')
        
        seq.add_pulse('pulse_mod_318', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_318',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_318', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_2', link_start_to = 'end', 
                duration = pulse_24_length, 
                amplitude = CORPSE_pi_over_two_amp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_24', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_24',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_24', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)

        last = 'pulse_24'


        ### First wait time
        seq.add_pulse('tau_1', channel = chan_mw_pm, 
                element = 'spin_control_'+str(i+1),start = 0,
                start_reference= last  ,link_start_to = 'end', 
                duration = tau, amplitude = 0)

        if np.mod(i,2)==0:
            CORPSE_pi_amp=0
        else:
            CORPSE_pi_amp = pulse_dict["CORPSE"]["pi"]
        ### Pi pulse
        seq.add_pulse('pulse_420', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_1',link_start_to = 'end', 
                duration = pulse_420_length, 
                amplitude = CORPSE_pi_amp, shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_420', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_420',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_420', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_3', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_420',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_300', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_3', link_start_to = 'end',
                duration = pulse_300_length, 
                amplitude = -CORPSE_pi_amp,shape = 'rectangular')
        
        seq.add_pulse('pulse_mod_300', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_300',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_300', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_4', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_300',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_60', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_4', link_start_to = 'end', 
                duration = pulse_60_length, 
                amplitude = CORPSE_pi_amp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_60', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = 2*MW_pulse_mod_risetime, 
                duration_reference='pulse_60',link_duration_to='duration',
                start = -MW_pulse_mod_risetime,
                start_reference = 'pulse_60', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)

        last = 'pulse_60'
        #Second wait time
        seq.add_pulse('tau_2', channel = chan_mw_pm, 
                element = 'spin_control_'+str(i+1),start = 0,
                start_reference= last  ,link_start_to = 'end', 
                duration = tau, amplitude = 0)
        
        Iamp = np.cos(np.pi*basis_rot_angle/180.)*CORPSE_pi_over_two_amp
        Qamp = np.sin(np.pi*basis_rot_angle/180.)*CORPSE_pi_over_two_amp

        Iamp=0
        Qamp=0
        #Final Pi over 2
        seq.add_pulse('pulse_384_2_I', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_2',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = Iamp, 
                shape = 'rectangular')
        seq.add_pulse('pulse_384_2_Q', channel = chan_mwQ, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'tau_2',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = Qamp, 
                shape = 'rectangular')
  
        seq.add_pulse('pulse_mod_384_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = max(pulse_300_length+\
                    2*MW_pulse_mod_risetime,
                    pulse_384_length+\
                    2*MW_pulse_mod_risetime), 
                duration_reference='pulse_384_2_I', link_duration_to='duration',
                start = min(-MW_pulse_mod_risetime,
                    (pulse_384_length-pulse_384_length)/2 - \
                    MW_pulse_mod_risetime),
                start_reference = 'pulse_384_2_I', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
                 
        seq.add_pulse('wait_5', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_384_2_I',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318_2_I', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_5', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -Iamp,shape = 'rectangular')
        seq.add_pulse('pulse_318_2_Q', channel = chan_mwQ, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_5', link_start_to = 'end',
                duration = pulse_318_length, 
                amplitude = -Qamp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = max(pulse_300_length+\
                    2*MW_pulse_mod_risetime,
                    pulse_318_length+\
                    2*MW_pulse_mod_risetime), 
                duration_reference = 'pulse_318_2_I',link_duration_to='duration',
                start = min(-MW_pulse_mod_risetime,
                    (pulse_318_length-pulse_318_length)/2 - \
                    MW_pulse_mod_risetime),
                start_reference = 'pulse_318_2_I', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
 
        seq.add_pulse('wait_6', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start = 0,start_reference = 'pulse_318_2_I',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24_2_I', channel = chan_mwI, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_6', link_start_to = 'end', 
                duration = pulse_24_length,  
                amplitude = Iamp,shape = 'rectangular')
        seq.add_pulse('pulse_24_2_Q', channel = chan_mwQ, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_6', link_start_to = 'end', 
                duration = pulse_24_length,  
                amplitude = Qamp,shape = 'rectangular')
       
        seq.add_pulse('pulse_mod_24_2', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                duration = max(pulse_300_length+\
                    2*MW_pulse_mod_risetime,
                    pulse_24_length+\
                    2*MW_pulse_mod_risetime), 
                duration_reference='pulse_24_2_I',link_duration_to='duration',
                start =min(-MW_pulse_mod_risetime,
                    (pulse_24_length-pulse_24_length)/2 - \
                    MW_pulse_mod_risetime),
                start_reference = 'pulse_24_2_I', link_start_to = 'start', 
                amplitude = MW_pulsemod_amplitude)
    
    
        last='pulse_24_2_I' 
  
        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start_reference = last,link_start_to ='end', duration = duty_cycle_time, amplitude = 0) 



    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()

    name = str(nr_of_pulses) + 'CORPSE_pulse_amp'
    return {"seqname":name, "max_seq_time":max_seq_time}

