#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels_lt2 as awgcfg

awg = qt.instruments['AWG']

def XY8_cycles(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of decoupling-pulses per element
    
    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,
                      "amplitude": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state
                
                
                "duty_cycle_time": ...,            waiting time at the end of each element
                }
    '''
    seq = Sequence('XY8')
   
    
    # vars for the channel names
  
    superposition_pulse=False
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
        chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
    else:
        chan_mwI = 'MW_Imod' #ch1
        chan_mwQ = 'MW_Qmod' #ch3
        chan_mw_pm = 'MW_pulsemod' #is connected to ch1m
#FIXME: take this from a dictionary
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    pi = pulse_dict["Pi"]
    tau_sweep = sweep_param
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    istate_pulse = pulse_dict["init_state_pulse"]
    awgcfg.configure_sequence(seq,mw={chan_mwQ:{'high': pi["amplitude"]}})
    for i in np.arange(nr_of_datapoints):

        #create element for each datapoint and link last element to first
        if i == nr_of_datapoints-1:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True, goto_target = 'spin_control_1')
        else:
            seq.add_element(name = 'spin_control_'+str(i+1), 
                trigger_wait = True)

   
        tau=tau_sweep[i]

        seq.add_pulse('first_wait', channel = chan_mw_pm, 
                element = 'spin_control_'+str(i+1),start = 0, 
                duration = 50, amplitude = 0)

        seq.add_pulse('init_state_pulse' , channel = chan_mwI, element = 'spin_control_'+str(i+1),
            start_reference = 'first_wait', link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

        seq.add_pulse('init_state_pulse_mod', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'init_state_pulse', link_start_to = 'start', 
            duration_reference = 'init_state_pulse', link_duration_to = 'duration', 
            amplitude = 2.0)
        
        last = 'init_state_pulse'

        for j in np.arange(pulse_nr):
            if pulse_nr ==2:
                pulse_array = [1,2]
            else:
                pulse_array=[1,3,6,8]
            if np.mod(j,8)+1 in pulse_array:
                chan = chan_mwI
            else:
                chan = chan_mwQ

            if tau != 0:
                seq.add_pulse('wait_before' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                    start_reference = last, link_start_to='end',start = 0, 
                    duration = tau, amplitude = 0)
            else:
                seq.add_pulse('wait_before' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                    start_reference = last, link_start_to='end',start = 0, 
                    duration = 20, amplitude = 0)
           
            seq.add_pulse('pi' + str(j), channel = chan, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_before'+str(j), link_start_to = 'end', 
                duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)

            if tau !=0:
                seq.add_pulse('wait_after' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                    start_reference = 'pi'+str(j), link_start_to='end',start = 0, 
                    duration = tau, amplitude = 0)
            else:
                seq.add_pulse('wait_after' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                    start_reference = 'pi'+str(j), link_start_to='end',start = 0, 
                    duration = 20., amplitude = 0)
            
            last = 'wait_after'+str(j)
        
        seq.add_pulse('readout_pulse' , channel = chan_mwI, element = 'spin_control_'+str(i+1),
            start_reference = last, link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

        seq.add_pulse('readout_pulse_mod', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'readout_pulse', link_start_to = 'start', 
            duration_reference = 'init_state_pulse', link_duration_to = 'duration', 
            amplitude = 2.0)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start_reference = 'readout_pulse',link_start_to ='end', 
                duration = duty_cycle_time, amplitude = 0)

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()


    name= '%d XY8_cycles' % nr_of_XY8_cycles
    return {"seqname":name, "max_seq_time":max_seq_time}

def DEC_CORPSE(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a SE with CORPSE pulses
    
    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,
                      "amplitude": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state
                
                
                "duty_cycle_time": ...,            waiting time at the end of each element
                }
    '''
    seq = Sequence('SE')
    awgcfg.configure_sequence(seq,'mw')
    
    # vars for the channel names

    superposition_pulse=False
    
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
        chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
    else:
        chan_mwI = 'MW_Imod' #ch1
        chan_mwQ = 'MW_Qmod' #ch3
        chan_mw_pm = 'MW_pulsemod' #is connected to 
    
#FIXME: take this from a dictionary
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    tau_sweep = sweep_param

    nr_of_datapoints = len(sweep_param)
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    CORPSE_pi = pulse_dict["CORPSE_pi"]
    CORPSE_pi2 = pulse_dict["CORPSE_pi2"]
    CORPSE_pi2_amp = CORPSE_pi2["amplitude"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]

    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]

    pulse_420_length = int(2.*CORPSE_pi["duration"]*(420./360.))
    pulse_300_length = int(2.*CORPSE_pi["duration"]*(300./360.))
    pulse_60_length = int(2.*CORPSE_pi["duration"]*(60./360.))

    pulse_384_length = int(2.*CORPSE_pi["duration"]*(384.3/360.))
    pulse_318_length = int(2.*CORPSE_pi["duration"]*(318.6/360.))
    pulse_24_length = int(2.*CORPSE_pi["duration"]*(24.3/360.))

    CORPSE_pi_length = pulse_420_length+pulse_300_length+pulse_60_length+2*time_between_CORPSE

    PM=1.
    
    for i in np.arange(nr_of_datapoints):
       
        #create element for each datapoint and link last element to first   
        el_name = 'SE'+str(i+1)
        if i == nr_of_datapoints-1:
            target= 'SE'+str(1)
        else:
            target='none'
        
        seq.add_element(name = el_name, 
            trigger_wait = True,goto_target=target)
        seq.add_pulse(name='first_wait', channel = chan_mwI, 
                element = el_name,start = 0, 
                duration = 75, amplitude = 0)
        seq.add_pulse('pulse_384', channel = chan_mwI, element = el_name,
                start = 0, start_reference = 'first_wait',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = CORPSE_pi2_amp, shape = 'rectangular')

        seq.add_pulse('pulse_mod_384', channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_384', link_start_to = 'start', 
                duration_reference = 'pulse_384', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_1', channel = chan_mwI, element = el_name,
                start = 0,start_reference = 'pulse_mod_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318', channel = chan_mwI, element = el_name,
            start = 0, start_reference = 'wait_1', link_start_to = 'end',
            duration = pulse_318_length, amplitude = -CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318', channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_318', link_start_to = 'start', 
                duration_reference = 'pulse_318', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_2', channel = chan_mwI, element = el_name,
                start = 0,start_reference = 'pulse_mod_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24', channel = chan_mwI, element = el_name,
            start = 0, start_reference = 'wait_2', link_start_to = 'end', 
            duration = pulse_24_length, amplitude = CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_24', channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_24', link_start_to = 'start', 
                duration_reference = 'pulse_24', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        last='pulse_24'
        tau_idx=0
        pulse_idx=0
        for j in np.arange(pulse_nr):
            if pulse_nr ==2:
                pulse_array = [1,2]
            else:
                pulse_array=[1,3,6,8]
            if np.mod(j,8)+1 in pulse_array:
                chan = chan_mwI
                pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
            else:
                chan = chan_mwQ
                pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
            cur_el_name=el_name
            tau_idx+=1
            if i != 0:
                ## tau1
                seq.add_pulse(name='tau1'+str(tau_idx),channel=chan,element=cur_el_name,
                        start=0,duration=tau_sweep[i],start_reference=last,link_start_to='end',amplitude=0.)
            else:

                seq.add_pulse(name='tau1'+str(tau_idx),channel=chan,element=cur_el_name,
                        start=0,duration=20,start_reference=last,link_start_to='end',amplitude=0.)
            last='tau1'+str(tau_idx)    
            ## pi pulse
            pulse_el_name=el_name

            seq.add_pulse('pulse_420'+str(pulse_idx) , channel = chan, element = pulse_el_name,
                start = 0, start_reference = last, link_start_to = 'end', 
                duration = pulse_420_length, amplitude = CORPSE_pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod_420'+str(pulse_idx) , channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_420'+str(pulse_idx) , link_start_to = 'start', 
                duration_reference = 'pulse_420'+str(pulse_idx), link_duration_to = 'duration', 
                amplitude = PM*2.0)
 
            seq.add_pulse('wait_1' +str(pulse_idx), channel = chan, element = pulse_el_name,
                start = 0,start_reference = 'pulse_mod_420'+str(pulse_idx),link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_300'+str(pulse_idx), channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'wait_1'+str(pulse_idx),link_start_to = 'end', 
                duration = pulse_300_length, amplitude = -1*CORPSE_pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_300'+str(pulse_idx) , channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_300'+str(pulse_idx) , link_start_to = 'start', 
                duration_reference = 'pulse_300'+str(pulse_idx), link_duration_to = 'duration', 
                amplitude = PM*2.0)
 
            seq.add_pulse('wait_2'+str(pulse_idx) , channel = chan, element = pulse_el_name,
                start = 0,start_reference = 'pulse_mod_300'+str(pulse_idx),link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_60'+str(pulse_idx ), channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'wait_2'+str(pulse_idx), link_start_to = 'end', 
                duration = pulse_60_length, amplitude = CORPSE_pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_60'+str(pulse_idx ), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_60'+str(pulse_idx ), link_start_to = 'start', 
                duration_reference = 'pulse_60'+str(pulse_idx), link_duration_to = 'duration', 
                amplitude = PM*2.0)

            last = 'pulse_60' +str(pulse_idx)

            pulse_idx+=1
            
            if i!=0:
                ## tau2
                seq.add_pulse(name='tau2'+str(tau_idx),channel=chan,element=cur_el_name,
                        start=0,start_reference=last,link_start_to='end',duration=tau_sweep[i],amplitude=0)
             
            else:        
                seq.add_pulse(name='tau2'+str(tau_idx),channel=chan,element=cur_el_name,
                        start=0,start_reference=last,link_start_to='end',duration=20,amplitude=0)
            last = 'tau2'+str(tau_idx)    
        ##Final readout pulse
        
        seq.add_pulse('pulse_384_ro' , channel = chan_mwI, element = cur_el_name,
                start = 0, start_reference = last,link_start_to = 'end', 
                duration = pulse_384_length, amplitude = CORPSE_pi2_amp, shape = 'rectangular')

        seq.add_pulse('pulse_mod_384_ro', channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_384_ro', link_start_to = 'start', 
                duration_reference = 'pulse_384_ro', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_1_ro', channel = chan_mwI, element = cur_el_name,
                start = 0,start_reference = 'pulse_mod_384_ro',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318_ro' , channel = chan_mwI, element = cur_el_name,
            start = 0, start_reference = 'wait_1_ro', link_start_to = 'end',
            duration = pulse_318_length, amplitude = -CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318_ro' , channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_318_ro' , link_start_to = 'start', 
                duration_reference = 'pulse_318_ro', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_2_ro' , channel = chan_mwI, element = cur_el_name,
                start = 0,start_reference = 'pulse_mod_318_ro',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24_ro', channel = chan_mwI, element = cur_el_name,
            start = 0, start_reference = 'wait_2_ro', link_start_to = 'end', 
            duration = pulse_24_length, amplitude = CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_24_ro', channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_24_ro', link_start_to = 'start', 
                duration_reference = 'pulse_24_ro', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = cur_el_name,
                start_reference = 'pulse_mod_24_ro',link_start_to ='end', 
                duration =duty_cycle_time, amplitude = 0)

    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    max_seq_time = seq.send_sequence()

    name= '%d XY8_cycles' % nr_of_XY8_cycles
    return {"seqname":name, "max_seq_time":max_seq_time}

def XY8_cycles_multiple_elements(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of decoupling-pulses per sweepparam
    every pulse is in a single element, tau is repeated to decrease number of points
    
    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,
                      "amplitude": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state
                
                
                "duty_cycle_time": ...,            waiting time at the end of each element
                "tau_el_length":...
                }
    '''
    seq = Sequence('XY8')
    awgcfg.configure_sequence(seq,'mw')
    
    # vars for the channel names
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
        chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
    else:
        chan_mwI = 'MW_Imod' #ch1
        chan_mwQ = 'MW_Qmod' #ch3
        chan_mw_pm = 'MW_pulsemod' #is connected to 
#FIXME: take this from a dictionary
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    pi = pulse_dict["Pi"]
    tau_sweep = sweep_param
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    istate_pulse = pulse_dict["init_state_pulse"]

    tau_len=pulse_dict["tau_el_length"]          # ns


# Start building sequence!
#
# First data point (not with repeated element, just to take first point of
# decoupling curve)

    
    el_name = 'first datapoint'+str(0)    
    seq.add_element(name = el_name,trigger_wait = True)

    seq.add_pulse(name='first_wait', channel = chan_mwI, element = el_name,start = 0, 
            duration = 990, amplitude = 0)
    
    
    seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
        start_reference = 'first_wait', link_start_to = 'end', start = 0, 
        duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')
    seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
        start_reference = 'Pi/2_pulse', link_start_to = 'start', 
        duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
        amplitude =2.0)
    
    seq.add_pulse(name='tau1',channel=chan_mwI,element=el_name,
                start=0, start_reference= 'Pi/2_pulse',link_start_to='end',
                duration=int((tau_sweep[0]*tau_len-istate_pulse['duration']/2-pi['duration']/2)),
                amplitude=0.)
    
    seq.add_pulse('pi' + str(1), channel = chan_mwI, element = el_name,
            start = 0, duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular',
            start_reference='tau1',link_start_to='end')
    seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'pi' + str(1), link_start_to = 'start', 
            duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
            amplitude = 2.0)
    
    seq.add_pulse(name='tau2',channel=chan_mwI,element=el_name,
                start=0, start_reference= 'pi' + str(1),link_start_to='end',
                duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),amplitude=0)

    last = 'tau2'
    tau_idx=3
    for j in np.arange(1,pulse_nr-1):
            if np.mod(j,8) in [0,2,5,7]:
                chan = chan_mwI
            else:
                chan = chan_mwQ
            if np.mod(int(j/8),2) == 0:
                do_min = 1
            else:
                do_min=-1
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                    start=0,start_reference = last, link_start_to='end',
                    duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),amplitude=0.)

            seq.add_pulse('pi' + str(j), channel = chan, element = el_name,
                start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                start_reference='tau'+str(tau_idx),link_start_to='end')
            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)

            tau_idx+=1
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                start=0,start_reference='pi' + str(j),link_start_to='end',
                duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),amplitude=0.)
            last='tau'+str(tau_idx)
            tau_idx+=1

    if pulse_nr ==4:
        chan = chan_mwQ
    else:
        chan = chan_mwI

    seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
           start=0,start_reference=last,link_start_to='end',
           duration=int((tau_sweep[0]*tau_len-pi['duration']/2)),
           amplitude=0.)
    seq.add_pulse('pi' + str(pulse_nr), channel = chan, element = el_name,
            start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
            start_reference='tau'+str(tau_idx),link_start_to='end')
    seq.add_pulse('pulse_mod' + str(pulse_nr), channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'pi' + str(pulse_nr), link_start_to = 'start', 
            duration_reference = 'pi'+str(pulse_nr), link_duration_to = 'duration', 
            amplitude = 2.0)
    tau_idx+=1
    seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                start=0, start_reference= 'pi' + str(pulse_nr),link_start_to='end',
                duration=int((tau_sweep[0]*tau_len-istate_pulse['duration']/2-pi['duration']/2)),amplitude=0)
    
    seq.add_pulse(name='readout_pulse' , channel = chan_mwI, element = el_name,
        start_reference = 'tau'+str(tau_idx), link_start_to = 'end', start = 0, 
        duration = istate_pulse["duration"], amplitude = -istate_pulse["amplitude"], shape = 'rectangular')
    seq.add_pulse(name='readout_pulse_mod', channel = chan_mw_pm, element = el_name,
        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
        start_reference = 'readout_pulse', link_start_to = 'start', 
        duration_reference = 'readout_pulse', link_duration_to = 'duration', 
        amplitude =2.0)

    seq.add_pulse('final_wait', channel = chan_mwI, element = el_name,
            start_reference = 'readout_pulse',link_start_to ='end',start = 0, 
            duration = 1000.+duty_cycle_time, amplitude = 0)

# Now for all other datapoints
#

    for i in np.arange(nr_of_datapoints-1):
        i=i+1
        pulse_idx = 0

        # calculate all delays (min el len = 960 pnts, elements multiple of 4)
        
        tau_rep_el = int(round((tau_sweep[i]*tau_len-750.)/tau_sweep[i]/4))*4
        firstlast_tau_res =int(round((750 + np.mod((tau_sweep[i]*tau_len-750.)/tau_sweep[i],4)*tau_sweep[i] - pi['duration']/2-istate_pulse['duration']/2)/2))*2  
        tau_res = int(round((750 + np.mod((tau_sweep[i]*tau_len-750.)/tau_sweep[i],4)*tau_sweep[i] - pi['duration']/2)/2))*2
        

        #create element for each datapoint and link last element to first   
        el_name = 'Pi_over2_'+str(i+1)
        seq.add_element(name = el_name,trigger_wait = True)
        seq.add_pulse(name='first_wait', channel = chan_mwI, element = el_name,start = 0, 
                duration = 960, amplitude = 0)
        seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
            start_reference = 'first_wait', link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')
        seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'Pi/2_pulse', link_start_to = 'start', 
            duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
            amplitude =2.0)

        seq.add_element(name='tau0'+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
        seq.add_pulse(name='tau0',channel=chan_mwI,element='tau0'+str(i+1),
                    start=0, duration=tau_rep_el,amplitude=0.)
        
        pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
        seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
        seq.add_pulse(name='wait',channel=chan_mwI,element=pulse_el_name,
                    start=0, duration=firstlast_tau_res,amplitude=0)
        seq.add_pulse('pi' + str(1), channel = chan_mwI, element = pulse_el_name,
                start = 0, duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular',
                start_reference='wait',link_start_to='end')
        seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(1), link_start_to = 'start', 
                duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
                amplitude = 2.0)
        seq.add_pulse(name='wait2',channel=chan_mwI,element=pulse_el_name,
                    start=0, start_reference= 'pi' + str(1),link_start_to='end',
                    duration=tau_res,amplitude=0)

        seq.add_element(name='tau1'+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
        seq.add_pulse(name='tau1',channel=chan_mwI,element='tau1'+str(i+1),
                    start=0, duration=tau_rep_el,
                    amplitude=0.)

        pulse_idx+=1
        tau_idx=2
        for j in np.arange(1,pulse_nr-1):
            if np.mod(j,8) in [0,2,5,7]:
                chan = chan_mwI
                pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
            else:
                chan = chan_mwQ
                pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
            if np.mod(int(j/8),2) == 0:
                do_min = 1
            else:
                do_min=-1
            ## tau1
            cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
            seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=cur_el_name,
                    start=0,duration=tau_rep_el,amplitude=0.)
            tau_idx+=1

            ## pi pulse
            seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
            
            seq.add_pulse(name='extra_wait'+str(j), channel = chan_mwI, 
                element = pulse_el_name,start = 0, 
                duration = tau_res, amplitude = 0)
            seq.add_pulse('pi' + str(j), channel = chan, element = pulse_el_name,
                start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                start_reference='extra_wait'+str(j),link_start_to='end')
            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)
            seq.add_pulse(name='extra_wait2'+str(j), channel = chan_mwI, 
                element = pulse_el_name,start = 0,start_reference='pi'+str(j),link_start_to='end', 
                duration = tau_res, amplitude = 0)
           
            pulse_idx+=1
            
            
            cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
            seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=cur_el_name,
                    start=0,duration=tau_rep_el,amplitude=0.)
            tau_idx+=1
                    
        ##Final  elements
        
        
        seq.add_element(name='tau'+str(tau_idx)+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
        seq.add_pulse(name='tau',channel=chan_mwI,element='tau'+str(tau_idx)+str(i+1),
                    start=0, duration=tau_rep_el,
                    amplitude=0.)
        tau_idx+=1
        
        if pulse_nr ==4:
            chan = chan_mwQ
            pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
        else:
            chan = chan_mwI
            pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
        
        seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
        seq.add_pulse(name='wait',channel=chan_mwI,element=pulse_el_name,
                    start=0, duration=tau_res,amplitude=0)
        seq.add_pulse('pi' + str(1), channel = chan, element = pulse_el_name,
                start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                start_reference='wait',link_start_to='end')
        seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(1), link_start_to = 'start', 
                duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
                amplitude = 2.0)
        extra_wait_time=100
        seq.add_pulse(name='wait2',channel=chan_mwI,element=pulse_el_name,
                    start=0, start_reference= 'pi' + str(1),link_start_to='end',
                    duration=firstlast_tau_res-extra_wait_time,amplitude=0)
        
        seq.add_element(name='tau'+str(tau_idx)+str(i+1),trigger_wait = False,repetitions=tau_sweep[i])
        seq.add_pulse(name='tau',channel=chan_mwI,element='tau'+str(tau_idx)+str(i+1),
                    start=0, duration=tau_rep_el,
                    amplitude=0.)
        tau_idx+=1

        # readout pulse
        el_name = 'readout'+str(i+1)
        if i == nr_of_datapoints-1:
            print 'going to nr 1'
            target= 'first datapoint'+str(0) 
        else:
            target='none'
    
        seq.add_element(name = el_name ,trigger_wait = False,goto_target=target)      
        seq.add_pulse(name='final_tau',channel=chan_mwI,element=el_name,
                    start=0, duration=extra_wait_time,
                    amplitude=0.)        
        seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
            start_reference = 'final_tau', link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = -istate_pulse["amplitude"], shape = 'rectangular')
        seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'Pi/2_pulse', link_start_to = 'start', 
            duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
            amplitude =2.0)

        seq.add_pulse('final_wait', channel = chan_mwI, element = el_name,
                start_reference = 'Pi/2_pulse',link_start_to ='end', start = 0,
                duration = 1000.+duty_cycle_time, amplitude = 0)
    
    print 'start to set AWG specs'
    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    a = seq.send_sequence()
    print 'done sending AWG sequence'
     
    tau_max = tau_len*(tau_sweep.max())
    max_seq_time = pulse_nr*(pi["duration"]+2*tau_max)+1000.+duty_cycle_time+50+2*istate_pulse["duration"]
    max_seq_time_us=max_seq_time*1e-3
    print 'max seq time %d us' % max_seq_time_us
    name= '%d XY8_cycles' % nr_of_XY8_cycles
    return {"seqname":name, "max_seq_time":max_seq_time_us}

def XY8_cycles_multiple_elements_tau(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of decoupling-pulses per sweepparam
    every pulse is in a single element, tau is repeated to decrease number of points
    
    sweep_param = numpy array with tau_el
    pulse_dict={
                "Pi":{"duration": ...,
                      "amplitude": ...},

                "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state
                
                "tau_reps":...          nr of times each tau is repeated
                "duty_cycle_time": ...,            waiting time at the end of each element
                "tau_el_length":...
                }
    '''
  
    seq = Sequence('XY8')
    awgcfg.configure_sequence(seq,'mw')
    
    # vars for the channel names
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
        chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
    else:
        chan_mwI = 'MW_Imod' #ch1
        chan_mwQ = 'MW_Qmod' #ch3
        chan_mw_pm = 'MW_pulsemod' #is connected to 
#FIXME: take this from a dictionary
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    pi = pulse_dict["Pi"]
    tau_len = sweep_param
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    istate_pulse = pulse_dict["init_state_pulse"]

    tau_sweep=pulse_dict["tau_rep_el"]          # ns


# Start building sequence!
#
# First data point (not with repeated element, just to take first point of
# decoupling curve)

    
    el_name = 'first datapoint'+str(0)    
    seq.add_element(name = el_name,trigger_wait = True)

    seq.add_pulse(name='first_wait', channel = chan_mwI, element = el_name,start = 0, 
            duration = 990, amplitude = 0)
    
    
    seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
        start_reference = 'first_wait', link_start_to = 'end', start = 0, 
        duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')
    seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
        start_reference = 'Pi/2_pulse', link_start_to = 'start', 
        duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
        amplitude =2.0)
    
    seq.add_pulse(name='tau1',channel=chan_mwI,element=el_name,
                start=0, start_reference= 'Pi/2_pulse',link_start_to='end',
                duration=int((tau_sweep*tau_len[0]-istate_pulse['duration']/2-pi['duration']/2)),
                amplitude=0.)
    
    seq.add_pulse('pi' + str(1), channel = chan_mwI, element = el_name,
            start = 0, duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular',
            start_reference='tau1',link_start_to='end')
    seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'pi' + str(1), link_start_to = 'start', 
            duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
            amplitude = 2.0)
    
    seq.add_pulse(name='tau2',channel=chan_mwI,element=el_name,
                start=0, start_reference= 'pi' + str(1),link_start_to='end',
                duration=int((tau_sweep*tau_len[0]-pi['duration']/2)),amplitude=0)

    last = 'tau2'
    tau_idx=3
    for j in np.arange(1,pulse_nr-1):
            if np.mod(j,8) in [0,2,5,7]:
                chan = chan_mwI
            else:
                chan = chan_mwQ
            if np.mod(int(j/8),2) == 0:
                do_min = 1
            else:
                do_min=-1
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                    start=0,start_reference = last, link_start_to='end',
                    duration=int((tau_sweep*tau_len[0]-pi['duration']/2)),amplitude=0.)

            seq.add_pulse('pi' + str(j), channel = chan, element = el_name,
                start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                start_reference='tau'+str(tau_idx),link_start_to='end')
            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)

            tau_idx+=1
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                start=0,start_reference='pi' + str(j),link_start_to='end',
                duration=int((tau_sweep*tau_len[0]-pi['duration']/2)),amplitude=0.)
            last='tau'+str(tau_idx)
            tau_idx+=1

    if pulse_nr ==4:
        chan = chan_mwQ
    else:
        chan = chan_mwI

    seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
           start=0,start_reference=last,link_start_to='end',
           duration=int((tau_sweep*tau_len[0]-pi['duration']/2)),
           amplitude=0.)
    seq.add_pulse('pi' + str(pulse_nr), channel = chan, element = el_name,
            start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
            start_reference='tau'+str(tau_idx),link_start_to='end')
    seq.add_pulse('pulse_mod' + str(pulse_nr), channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'pi' + str(pulse_nr), link_start_to = 'start', 
            duration_reference = 'pi'+str(pulse_nr), link_duration_to = 'duration', 
            amplitude = 2.0)
    tau_idx+=1
    seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=el_name,
                start=0, start_reference= 'pi' + str(pulse_nr),link_start_to='end',
                duration=int((tau_sweep*tau_len[0]-istate_pulse['duration']/2-pi['duration']/2)),amplitude=0)
    
    seq.add_pulse(name='readout_pulse' , channel = chan_mwI, element = el_name,
        start_reference = 'tau'+str(tau_idx), link_start_to = 'end', start = 0, 
        duration = istate_pulse["duration"], amplitude = -istate_pulse["amplitude"], shape = 'rectangular')
    seq.add_pulse(name='readout_pulse_mod', channel = chan_mw_pm, element = el_name,
        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
        start_reference = 'readout_pulse', link_start_to = 'start', 
        duration_reference = 'readout_pulse', link_duration_to = 'duration', 
        amplitude =2.0)

    seq.add_pulse('final_wait', channel = chan_mwI, element = el_name,
            start_reference = 'readout_pulse',link_start_to ='end',start = 0, 
            duration = 1000.+duty_cycle_time, amplitude = 0)

# Now for all other datapoints
#

    for i in np.arange(nr_of_datapoints-1):
        i=i+1
        pulse_idx = 0
        #create element for each datapoint and link last element to first   
        el_name = 'Pi_over2_'+str(i+1)
        seq.add_element(name = el_name,trigger_wait = True)
        seq.add_pulse(name='first_wait', channel = chan_mwI, element = el_name,start = 0, 
                duration = 960, amplitude = 0)
        seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
            start_reference = 'first_wait', link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')
        seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'Pi/2_pulse', link_start_to = 'start', 
            duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
            amplitude =2.0)

        seq.add_element(name='tau0'+str(i+1),trigger_wait = False,repetitions=tau_sweep)
        seq.add_pulse(name='tau0',channel=chan_mwI,element='tau0'+str(i+1),
                    start=0, duration=int(round((tau_sweep*tau_len[i]-750.)/tau_sweep)),
                    amplitude=0.)
        
        pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
        seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
        seq.add_pulse(name='wait',channel=chan_mwI,element=pulse_el_name,
                    start=0, duration=750-int(round((istate_pulse['duration']/2+pi['duration']/2))),amplitude=0)
        seq.add_pulse('pi' + str(1), channel = chan_mwI, element = pulse_el_name,
                start = 0, duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular',
                start_reference='wait',link_start_to='end')
        seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(1), link_start_to = 'start', 
                duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
                amplitude = 2.0)
        seq.add_pulse(name='wait2',channel=chan_mwI,element=pulse_el_name,
                    start=0, start_reference= 'pi' + str(1),link_start_to='end',
                    duration=750-int(round((pi['duration']/2))),amplitude=0)

        seq.add_element(name='tau1'+str(i+1),trigger_wait = False,repetitions=tau_sweep)
        seq.add_pulse(name='tau1',channel=chan_mwI,element='tau1'+str(i+1),
                    start=0, duration=int(round((tau_sweep*tau_len[i]-750.)/tau_sweep)),
                    amplitude=0.)

        pulse_idx+=1
        tau_idx=2
        for j in np.arange(1,pulse_nr-1):
            if np.mod(j,8) in [0,2,5,7]:
                chan = chan_mwI
                pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
            else:
                chan = chan_mwQ
                pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
            if np.mod(int(j/8),2) == 0:
                do_min = 1
            else:
                do_min=-1
            ## tau1
            cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
            seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep)
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=cur_el_name,
                    start=0,duration=int(round((tau_sweep*tau_len[i]-750.)/tau_sweep)),amplitude=0.)
            tau_idx+=1

            ## pi pulse
            seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
            
            seq.add_pulse(name='extra_wait'+str(j), channel = chan_mwI, 
                element = pulse_el_name,start = 0, 
                duration = 750.-int(round(pi["duration"]/2)), amplitude = 0)
            seq.add_pulse('pi' + str(j), channel = chan, element = pulse_el_name,
                start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                start_reference='extra_wait'+str(j),link_start_to='end')
            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)
            seq.add_pulse(name='extra_wait2'+str(j), channel = chan_mwI, 
                element = pulse_el_name,start = 0,start_reference='pi'+str(j),link_start_to='end', 
                duration = 750.-int(round(pi["duration"]/2)), amplitude = 0)
           
            pulse_idx+=1
            
            
            cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
            seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep)
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mwI,element=cur_el_name,
                    start=0,duration=int(round((tau_sweep*tau_len[i]-750.)/tau_sweep)),amplitude=0.)
            tau_idx+=1
                    
        ##Final  elements
        
        
        seq.add_element(name='tau'+str(tau_idx)+str(i+1),trigger_wait = False,repetitions=tau_sweep)
        seq.add_pulse(name='tau',channel=chan_mwI,element='tau'+str(tau_idx)+str(i+1),
                    start=0, duration=int(round((tau_sweep*tau_len[i]-750.)/tau_sweep)),
                    amplitude=0.)
        tau_idx+=1
        
        if pulse_nr ==4:
            chan = chan_mwQ
            pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
        else:
            chan = chan_mwI
            pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
        
        seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
        seq.add_pulse(name='wait',channel=chan_mwI,element=pulse_el_name,
                    start=0, duration=750-int(round((pi['duration']/2))),amplitude=0)
        seq.add_pulse('pi' + str(1), channel = chan, element = pulse_el_name,
                start = 0, duration = pi["duration"], amplitude = do_min*pi["amplitude"], shape = 'rectangular',
                start_reference='wait',link_start_to='end')
        seq.add_pulse('pulse_mod' + str(1), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(1), link_start_to = 'start', 
                duration_reference = 'pi'+str(1), link_duration_to = 'duration', 
                amplitude = 2.0)
        extra_wait_time=100
        seq.add_pulse(name='wait2',channel=chan_mwI,element=pulse_el_name,
                    start=0, start_reference= 'pi' + str(1),link_start_to='end',
                    duration=750-int(round((istate_pulse['duration']/2+pi['duration']/2)))-extra_wait_time,amplitude=0)
        
        seq.add_element(name='tau'+str(tau_idx)+str(i+1),trigger_wait = False,repetitions=tau_sweep)
        seq.add_pulse(name='tau',channel=chan_mwI,element='tau'+str(tau_idx)+str(i+1),
                    start=0, duration=int(round((tau_sweep*tau_len[i]-750.)/tau_sweep)),
                    amplitude=0.)
        tau_idx+=1

        # readout pulse
        el_name = 'readout'+str(i+1)
        if i == nr_of_datapoints-1:
            print 'going to nr 1'
            target= 'first datapoint'+str(0) 
        else:
            target='none'
    
        seq.add_element(name = el_name ,trigger_wait = False,goto_target=target)      
        seq.add_pulse(name='final_tau',channel=chan_mwI,element=el_name,
                    start=0, duration=extra_wait_time,
                    amplitude=0.)        
        seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
            start_reference = 'final_tau', link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = -istate_pulse["amplitude"], shape = 'rectangular')
        seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'Pi/2_pulse', link_start_to = 'start', 
            duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
            amplitude =2.0)

        seq.add_pulse('final_wait', channel = chan_mwI, element = el_name,
                start_reference = 'Pi/2_pulse',link_start_to ='end', start = 0,
                duration = 1000.+duty_cycle_time, amplitude = 0)
    
    print 'start to set AWG specs'
    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    a = seq.send_sequence()
    print 'done sending AWG sequence'
     
    tau_max = tau_sweep*(tau_len.max())
    max_seq_time = pulse_nr*(pi["duration"]+2*tau_max)+1000.+duty_cycle_time+50+2*istate_pulse["duration"]
    max_seq_time_us=max_seq_time*1e-3
    print 'max seq time %d us' % max_seq_time_us
    name= '%d XY8_cycles' % nr_of_XY8_cycles
    return {"seqname":name, "max_seq_time":max_seq_time_us} 


# Same sequences with CORPSE


def XY8_cycles_multiple_elements_CORPSE(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of CORPSE decoupling-pulses per sweepparam
    every pulse is in a single element, tau is repeated to decrease number of points
    
    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "CORPSE_pi":{"duration":,"amplitude":,}
                "time_between_CORPSE":..,
                "duty_cycle_time": ...,            waiting time at the end of each element
                "tau_el_length":...
                }
    '''
    seq = Sequence('XY8')
    awgcfg.configure_sequence(seq,'mw')
    
    # vars for the channel names
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
        chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
    else:
        chan_mwI = 'MW_Imod' #ch1
        chan_mwQ = 'MW_Qmod' #ch3
        chan_mw_pm = 'MW_pulsemod' #is connected to 
    
#FIXME: take this from a dictionary
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    CORPSE_pi = pulse_dict["CORPSE_pi"]
    CORPSE_pi2 = pulse_dict["CORPSE_pi2"]
    CORPSE_pi2_amp = CORPSE_pi2["amplitude"]
    tau_sweep = sweep_param
    duty_cycle_time = pulse_dict["duty_cycle_time"]

    tau_len=pulse_dict["tau_el_length"]          # ns
    final_tau = pulse_dict["final_tau"]
    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]

    pulse_420_length = int(2.*CORPSE_pi["duration"]*(420./360.))
    pulse_300_length = int(2.*CORPSE_pi["duration"]*(300./360.))
    pulse_60_length = int(2.*CORPSE_pi["duration"]*(60./360.))

    pulse_384_length = int(2.*CORPSE_pi["duration"]*(384.3/360.))
    pulse_318_length = int(2.*CORPSE_pi["duration"]*(318.6/360.))
    pulse_24_length = int(2.*CORPSE_pi["duration"]*(24.3/360.))

    CORPSE_pi_length = pulse_420_length+pulse_300_length+pulse_60_length+2*time_between_CORPSE

    PM=1.

    for i in np.arange(nr_of_datapoints):
       
        #create element for each datapoint and link last element to first   
        el_name = 'Pi_over2_'+str(i+1)
        seq.add_element(name = el_name, 
            trigger_wait = True)
        seq.add_pulse(name='first_wait', channel = chan_mwI, 
                element = el_name,start = 0, 
                duration = 960, amplitude = 0)
        seq.add_pulse('pulse_384', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
                start = 0, start_reference = 'first_wait',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = CORPSE_pi2_amp, shape = 'rectangular')

        seq.add_pulse('pulse_mod_384', channel = chan_mw_pm, element = 'Pi_over2_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_384', link_start_to = 'start', 
                duration_reference = 'pulse_384', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_1', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
                start = 0,start_reference = 'pulse_mod_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
            start = 0, start_reference = 'wait_1', link_start_to = 'end',
            duration = pulse_318_length, amplitude = -CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318', channel = chan_mw_pm, element = 'Pi_over2_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_318', link_start_to = 'start', 
                duration_reference = 'pulse_318', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_2', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
                start = 0,start_reference = 'pulse_mod_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
            start = 0, start_reference = 'wait_2', link_start_to = 'end', 
            duration = pulse_24_length, amplitude = CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_24', channel = chan_mw_pm, element = 'Pi_over2_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_24', link_start_to = 'start', 
                duration_reference = 'pulse_24', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse(name='second_wait', channel = chan_mwI, 
                element = el_name,start = 0,start_reference='pulse_24',link_start_to='end', 
                duration = 50., amplitude = 0)

        pulse_idx = 0
        tau_idx=0
        for j in np.arange(pulse_nr):
            if pulse_nr ==2:
                pulse_array = [1,2]
            else:
                pulse_array=[1,3,6,8]
            if np.mod(j,8)+1 in pulse_array:
                chan = chan_mwI
                pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
            else:
                chan = chan_mwQ
                pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
            if i != 0:
                ## tau1
                cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
                seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mw_pm,element=cur_el_name,
                        start=0,duration=int((tau_sweep[i]*tau_len-500.)/tau_sweep[i]),amplitude=0.)
                
                tau_idx+=1

            ## pi pulse
            seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
            
            seq.add_pulse(name='extra_wait', channel = chan, 
                element = pulse_el_name,start = 0, 
                duration = 500.-int(CORPSE_pi_length/2), amplitude = 0)

            seq.add_pulse('pulse_420' , channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'extra_wait', link_start_to = 'end', 
                duration = pulse_420_length, amplitude = CORPSE_pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod_420' , channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_420' , link_start_to = 'start', 
                duration_reference = 'pulse_420', link_duration_to = 'duration', 
                amplitude = PM*2.0)
 
            seq.add_pulse('wait_1' , channel = chan, element = pulse_el_name,
                start = 0,start_reference = 'pulse_mod_420',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_300', channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'wait_1',link_start_to = 'end', 
                duration = pulse_300_length, amplitude = -1*CORPSE_pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_300' , channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_300' , link_start_to = 'start', 
                duration_reference = 'pulse_300', link_duration_to = 'duration', 
                amplitude = PM*2.0)
 
            seq.add_pulse('wait_2' , channel = chan, element = pulse_el_name,
                start = 0,start_reference = 'pulse_mod_300',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_60' , channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'wait_2', link_start_to = 'end', 
                duration = pulse_60_length, amplitude = CORPSE_pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_60' , channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_60' , link_start_to = 'start', 
                duration_reference = 'pulse_60', link_duration_to = 'duration', 
                amplitude = PM*2.0)

            seq.add_pulse(name='extra_wait_2', channel = chan, 
                element = pulse_el_name,start = 0, 
                duration = 500.-int(CORPSE_pi_length/2), amplitude = 0,start_reference='pulse_60',link_start_to='end')
            pulse_idx+=1
            
            if i!=0:
                ## tau2
                cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
                seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mw_pm,element=cur_el_name,
                        start=0,duration=int((tau_sweep[i]*tau_len-500.)/tau_sweep[i]),amplitude=0)
                tau_idx+=1
                    
        ##Final readout pulse
        cur_el_name = 'readout'+str(i+1)
        if i == nr_of_datapoints-1:
            print 'going to nr 1'
            target= 'Pi_over2_'+str(1)
        else:
            target='none'
        seq.add_element(name = cur_el_name ,trigger_wait = False,goto_target=target)
        seq.add_pulse('extra_wait', channel = chan_mwI, element = cur_el_name,
                start=0,duration=final_tau, amplitude = 0)
        seq.add_pulse('pulse_384' , channel = chan_mwI, element = cur_el_name,
                start = 0, start_reference = 'extra_wait',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = CORPSE_pi2_amp, shape = 'rectangular')

        seq.add_pulse('pulse_mod_384', channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_384', link_start_to = 'start', 
                duration_reference = 'pulse_384', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_1', channel = chan_mwI, element = cur_el_name,
                start = 0,start_reference = 'pulse_mod_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318' , channel = chan_mwI, element = cur_el_name,
            start = 0, start_reference = 'wait_1', link_start_to = 'end',
            duration = pulse_318_length, amplitude = -CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318' , channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_318' , link_start_to = 'start', 
                duration_reference = 'pulse_318', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('wait_2' , channel = chan_mwI, element = cur_el_name,
                start = 0,start_reference = 'pulse_mod_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24', channel = chan_mwI, element = cur_el_name,
            start = 0, start_reference = 'wait_2', link_start_to = 'end', 
            duration = pulse_24_length, amplitude = CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_24', channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_24', link_start_to = 'start', 
                duration_reference = 'pulse_24', link_duration_to = 'duration', 
                amplitude = PM*2.0)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = cur_el_name,
                start_reference = 'pulse_mod_24',link_start_to ='end', 
                duration = 1000.+duty_cycle_time, amplitude = 0)

    print 'start to set AWG specs'
    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    a = seq.send_sequence()
    print 'done sending AWG sequence'
     
    tau_max = tau_len*(tau_sweep.max())
    max_seq_time = pulse_nr*(CORPSE_pi_length+2*tau_max)+1000.+duty_cycle_time+50+2*istate_pulse["duration"]
    print 'max seq time %d' % max_seq_time
    name= '%d XY8_cycles' % nr_of_XY8_cycles
    return {"seqname":name, "max_seq_time":max_seq_time}



def XY8_cycles_multiple_elements_tau_CORPSE(sweep_param,pulse_dict,lt1 = False,do_program=True):
    '''
    This sequence consists of a number of CORPSE decoupling-pulses per sweepparam
    every pulse is in a single element, tau is repeated to decrease number of points
    
    sweep_param = numpy array with number of Pi-pulses per element
    pulse_dict={
                "Pi":{"duration": ...,
                      "amplitude": ...},
                "CORPSE_pi":{"duration":,"amplitude":,}
                "istate_pulse": {"duration":... , 
                                 "amplitude":...}, First pulse to create init state
                
                "time_between_CORPSE":..,
                "tau_reps":...          nr of times each tau is repeated
                "final_tau":
                "sweep_tau_len":    boolean if true: sweep tau_len, else sweep final_tau
                "duty_cycle_time": ...,            waiting time at the end of each element
                "tau_el_length":...
                }
    '''
    seq = Sequence('XY8')
    awgcfg.configure_sequence(seq,'mw')
    
    # vars for the channel names
    if lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
        chan_mw_pm = 'MW_pulsemod_lt1' #is connected to ch3m2
    else:
        chan_mwI = 'MW_Imod' #ch1
        chan_mwQ = 'MW_Qmod' #ch3
        chan_mw_pm = 'MW_pulsemod' #is connected to 
    
#FIXME: take this from a dictionary
    if lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10

    nr_of_datapoints = len(sweep_param)
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    CORPSE_pi = pulse_dict["CORPSE_pi"]
    CORPSE_pi2 = pulse_dict["CORPSE_pi2"]
    CORPSE_pi2_amp = CORPSE_pi2["amplitude"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    istate_pulse = pulse_dict["init_state_pulse"]

    sweep_tau_len = pulse_dict["sweep_tau_len"]
    tau_reps = pulse_dict["tau_reps"]
    final_tau = pulse_dict["final_tau"]    
    time_between_CORPSE = pulse_dict["time_between_CORPSE"]
    duty_cycle_time = pulse_dict["duty_cycle_time"]

    pulse_420_length = int(2.*CORPSE_pi["duration"]*(420./360.))
    pulse_300_length = int(2.*CORPSE_pi["duration"]*(300./360.))
    pulse_60_length = int(2.*CORPSE_pi["duration"]*(60./360.))

    pulse_384_length = int(2.*CORPSE_pi["duration"]*(384.3/360.))
    pulse_318_length = int(2.*CORPSE_pi["duration"]*(318.6/360.))
    pulse_24_length = int(2.*CORPSE_pi["duration"]*(24.3/360.))

    CORPSE_pi_length = pulse_420_length+pulse_300_length+pulse_60_length + 2*time_between_CORPSE
    
     
    for i in np.arange(nr_of_datapoints):
        if sweep_tau_len:
            tau_len = sweep_param[i]
            point_nr=i
            
        else:
            tau_len = 5000. # not used 
            point_nr= 0
            final_tau=sweep_param[i]
        #create element for each datapoint and link last element to first   
        el_name = 'Pi_over2_'+str(i+1)
        seq.add_element(name = el_name, trigger_wait = True)
        seq.add_pulse(name='first_wait', channel = chan_mwI, 
                element = el_name,start = 0, 
                duration = 960, amplitude = 0)
        seq.add_pulse('pulse_384', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
                start = 0, start_reference = 'first_wait',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = CORPSE_pi2_amp, shape = 'rectangular')

        seq.add_pulse('pulse_mod_384' , channel = chan_mw_pm, element = 'Pi_over2_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_384', link_start_to = 'start', 
                duration_reference = 'pulse_384', link_duration_to = 'duration', 
                amplitude = 2.0)

        seq.add_pulse('wait_1', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
                start = 0,start_reference = 'pulse_mod_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318' , channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
            start = 0, start_reference = 'wait_1', link_start_to = 'end',
            duration = pulse_318_length, amplitude = -CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318' , channel = chan_mw_pm, element = 'Pi_over2_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_318' , link_start_to = 'start', 
                duration_reference = 'pulse_318', link_duration_to = 'duration', 
                amplitude = 2.0)

        seq.add_pulse('wait_2', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
                start = 0,start_reference = 'pulse_mod_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24', channel = chan_mwI, element = 'Pi_over2_'+str(i+1),
            start = 0, start_reference = 'wait_2', link_start_to = 'end', 
            duration = pulse_24_length, amplitude = CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_24' , channel = chan_mw_pm, element = 'Pi_over2_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_24', link_start_to = 'start', 
                duration_reference = 'pulse_24', link_duration_to = 'duration', 
                amplitude = 2.0)
        seq.add_pulse(name='second_wait', channel = chan_mwI, 
                element = el_name,start = 0,link_start_to='end',start_reference='pulse_24', 
                duration = 50, amplitude = 0)

        pulse_idx = 0
        tau_idx=0
        for j in np.arange(pulse_nr):
            if pulse_nr ==2:
                pulse_array = [1,2]
            else:
                pulse_array=[1,3,6,8]
            if np.mod(j,8)+1 in pulse_array:
                chan = chan_mwI
                pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
            else:
                chan = chan_mwQ
                pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
            if point_nr != 0:
                ## tau1
                cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
                seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_reps)
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mw_pm,element=cur_el_name,
                        start=0,duration=int((tau_reps*tau_len-500.)/tau_reps),amplitude=0.)
                tau_idx+=1

            ## pi pulse
            seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
            
            seq.add_pulse(name='extra_wait', channel = chan, 
                element = pulse_el_name,start = 0, 
                duration = 500.-int(CORPSE_pi_length/2), amplitude = 0)

            seq.add_pulse('pulse_420', channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'extra_wait', link_start_to = 'end', 
                duration = pulse_420_length, amplitude = CORPSE_pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod_420' , channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_420' , link_start_to = 'start', 
                duration_reference = 'pulse_420', link_duration_to = 'duration', 
                amplitude = 2.0)
 
            seq.add_pulse('wait_1', channel = chan, element = pulse_el_name,
                start = 0,start_reference = 'pulse_mod_420',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_300', channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'wait_1',link_start_to = 'end', 
                duration = pulse_300_length, amplitude = -1*CORPSE_pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_300', channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_300', link_start_to = 'start', 
                duration_reference = 'pulse_300', link_duration_to = 'duration', 
                amplitude = 2.0)
 
            seq.add_pulse('wait_2', channel = chan, element = pulse_el_name,
                start = 0,start_reference = 'pulse_mod_300',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

            seq.add_pulse('pulse_60', channel = chan, element = pulse_el_name,
                start = 0, start_reference = 'wait_2', link_start_to = 'end', 
                duration = pulse_60_length, amplitude = CORPSE_pi["amplitude"],shape = 'rectangular')

            seq.add_pulse('pulse_mod_60', channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_60', link_start_to = 'start', 
                duration_reference = 'pulse_60', link_duration_to = 'duration', 
                amplitude = 2.0)

            seq.add_pulse(name='extra_wait_2', channel = chan, 
                element = pulse_el_name,start = 0, 
                duration = 500.-int(CORPSE_pi_length/2), amplitude = 0,start_reference='pulse_60',link_start_to='end')
            pulse_idx+=1
            
            if point_nr!=0:
                ## tau2
                cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
                seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_reps)
                seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mw_pm,element=cur_el_name,
                        start=0,duration=int((tau_reps*tau_len-500.)/tau_reps),amplitude=0.)
                tau_idx+=1
                    
        ##Final readout pulse
        cur_el_name = 'readout'+str(i+1)
        if i == nr_of_datapoints-1:
            target= 'Pi_over2_'+str(1)
        else:
            target='none'
        
        seq.add_element(name = cur_el_name ,trigger_wait = False,goto_target=target)
        seq.add_pulse('extra_wait', channel = chan, element = cur_el_name,
                start=0,duration=final_tau, amplitude = 0)

        seq.add_pulse('pulse_384' , channel = chan_mwI, element = cur_el_name,
                start = 0, start_reference = 'extra_wait',link_start_to = 'end', 
                duration = pulse_384_length, amplitude = CORPSE_pi2_amp, shape = 'rectangular')

        seq.add_pulse('pulse_mod_384' , channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_384' , link_start_to = 'start', 
                duration_reference = 'pulse_384', link_duration_to = 'duration', 
                amplitude = 2.0)

        seq.add_pulse('wait_1' , channel = chan_mwI, element = cur_el_name,
                start = 0,start_reference = 'pulse_mod_384',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_318' , channel = chan_mwI, element = cur_el_name,
            start = 0, start_reference = 'wait_1', link_start_to = 'end',
            duration = pulse_318_length, amplitude = -CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_318' , channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_318' , link_start_to = 'start', 
                duration_reference = 'pulse_318', link_duration_to = 'duration', 
                amplitude = 2.0)

        seq.add_pulse('wait_2' , channel = chan_mwI, element = cur_el_name,
                start = 0,start_reference = 'pulse_mod_318',link_start_to ='end', 
                duration = time_between_CORPSE, amplitude = 0)

        seq.add_pulse('pulse_24' , channel = chan_mwI, element = cur_el_name,
            start = 0, start_reference = 'wait_2', link_start_to = 'end', 
            duration = pulse_24_length, amplitude = CORPSE_pi2_amp,shape = 'rectangular')

        seq.add_pulse('pulse_mod_24' , channel = chan_mw_pm, element = cur_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pulse_24' , link_start_to = 'start', 
                duration_reference = 'pulse_24', link_duration_to = 'duration', 
                amplitude = 2.0)
        seq.add_pulse('final_wait', channel = chan_mw_pm, element = cur_el_name,
                start_reference = 'pulse_24' ,link_start_to ='end', 
                duration = 1000.+duty_cycle_time, amplitude = 0)

    print 'start to set AWG specs'
    seq.set_instrument(awg)
    seq.set_clock(1e9)
    seq.set_send_waveforms(do_program)
    seq.set_send_sequence(do_program)
    seq.set_program_channels(True)
    seq.set_start_sequence(False)
    seq.force_HW_sequencing(True)
    a = seq.send_sequence()
    print 'done sending AWG sequence'
     
    tau_max = tau_len*(tau_reps)
    max_seq_time = pulse_nr*(CORPSE_pi_length+2*tau_max)+1000.+duty_cycle_time+50+2*istate_pulse["duration"]
    print 'max seq time %d' % max_seq_time
    name= '%d XY8_cycles' % nr_of_XY8_cycles
    return {"seqname":name, "max_seq_time":max_seq_time}
