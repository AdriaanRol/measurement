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
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    pi = pulse_dict["Pi"]
    tau_sweep = sweep_param
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
            if np.mod(j,8)+1 in [1,3,6,8]:
                chan = chan_mwI
            else:
                chan = chan_mwQ

            seq.add_pulse('wait_before' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                start_reference = last, link_start_to='end',start = 0, 
                duration = tau, amplitude = 0)
           
            seq.add_pulse('pi' + str(j), channel = chan, element = 'spin_control_'+str(i+1),
                start = 0, start_reference = 'wait_before'+str(j), link_start_to = 'end', 
                duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular')

            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)

            seq.add_pulse('wait_after' + str(j), channel = chan_mw_pm, element = 'spin_control_'+str(i+1), 
                start_reference = 'pi'+str(j), link_start_to='end',start = 0, 
                duration = tau, amplitude = 0)
            
            last = 'wait_after'+str(j)
        
        seq.add_pulse('readout_pulse' , channel = chan_mwI, element = 'spin_control_'+str(i+1),
            start_reference = last, link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = -istate_pulse["amplitude"], shape = 'rectangular')

        seq.add_pulse('init_state_pulse_mod', channel = chan_mw_pm, element = 'spin_control_'+str(i+1),
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
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
    
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
    nr_of_XY8_cycles =  pulse_dict["nr_of_XY8_cycles"]
    pulse_nr = 8*nr_of_XY8_cycles

    pi = pulse_dict["Pi"]
    tau_sweep = sweep_param
    duty_cycle_time = pulse_dict["duty_cycle_time"]
    istate_pulse = pulse_dict["init_state_pulse"]

    tau_len=pulse_dict["tau_el_length"]          # ns

    for i in np.arange(nr_of_datapoints):
       
        #create element for each datapoint and link last element to first   
        el_name = 'Pi_over2_'+str(i+1)
        seq.add_element(name = el_name, 
            trigger_wait = True)
        seq.add_pulse(name='first_wait', channel = chan_mw_pm, 
                element = el_name,start = 0, 
                duration = 960, amplitude = 0)
        seq.add_pulse(name='Pi/2_pulse' , channel = chan_mwI, element = el_name,
            start_reference = 'first_wait', link_start_to = 'end', start = 0, 
            duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')

        seq.add_pulse(name='Pi/2_pulse_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'Pi/2_pulse', link_start_to = 'start', 
            duration_reference = 'Pi/2_pulse', link_duration_to = 'duration', 
            amplitude = 2.0)

        pulse_idx = 0
        tau_idx=0
        for j in np.arange(pulse_nr):
            if np.mod(j,8)+1 in [1,3,6,8]:
                chan = chan_mwI
                pulse_el_name = 'X'+str(pulse_idx)+'_'+str(i+1)
            else:
                chan = chan_mwQ
                pulse_el_name = 'Y'+str(pulse_idx)+'_'+str(i+1)
            
            ## tau1
            cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
            seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mw_pm,element=cur_el_name,
                        start=0,duration=tau_len-int(1000./tau_sweep[i]/2.))
            tau_idx+=1

            ## pi pulse
            seq.add_element(name=pulse_el_name,trigger_wait = False,repetitions=1)
            
            seq.add_pulse(name='extra_wait'+str(j), channel = chan_mw_pm, 
                element = pulse_el_name,start = 0, 
                duration = 500.-int(pi["duration"]/2), amplitude = 0)
            seq.add_pulse('pi' + str(j), channel = chan, element = pulse_el_name,
                start = 0, duration = pi["duration"], amplitude = pi["amplitude"], shape = 'rectangular',
                start_reference='extra_wait'+str(j),link_start_to='end')
            seq.add_pulse('pulse_mod' + str(j), channel = chan_mw_pm, element = pulse_el_name,
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                start_reference = 'pi' + str(j), link_start_to = 'start', 
                duration_reference = 'pi'+str(j), link_duration_to = 'duration', 
                amplitude = 2.0)
            seq.add_pulse(name='extra_wait_2'+str(j), channel = chan_mw_pm, 
                element = pulse_el_name,start = 0, 
                duration = 500.-int(pi["duration"]/2), amplitude = 0,start_reference='pi'+str(j),link_start_to='end')
            pulse_idx+=1
            
            ## tau2
            cur_el_name='tau'+str(tau_idx)+'_'+str(i+1)
            seq.add_element(name=cur_el_name,trigger_wait = False,repetitions=tau_sweep[i])
            seq.add_pulse(name='tau'+str(tau_idx),channel=chan_mw_pm,element=cur_el_name,
                        start=0,duration=tau_len-int(1000./tau_sweep[i]/2.))
            tau_idx+=1
                    
        ##Final readout pulse
        cur_el_name = 'readout'+str(i+1)
        if i == nr_of_datapoints-1:
            print 'going to nr 1'
            target= 'Pi_over2_'+str(1)
        else:
            target='none'
        seq.add_element(name = cur_el_name ,trigger_wait = False,goto_target=target)
        seq.add_pulse('readout_pulse' , channel = chan_mwI, element = cur_el_name,
            start = 0, duration = istate_pulse["duration"], amplitude = istate_pulse["amplitude"], shape = 'rectangular')
        seq.add_pulse('Pi/2_pulse_mod', channel = chan_mw_pm, element = cur_el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = 'readout_pulse', link_start_to = 'start', 
            duration_reference = 'readout_pulse', link_duration_to = 'duration', 
            amplitude = 2.0)

        seq.add_pulse('final_wait', channel = chan_mw_pm, element = cur_el_name,
                start_reference = 'readout_pulse',link_start_to ='end', 
                duration = duty_cycle_time, amplitude = 0)
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
    max_seq_time = pulse_nr*(pi["duration"]+2*tau_max)+duty_cycle_time+50+2*istate_pulse["duration"]
    print 'max seq time %d' % max_seq_time
    name= '%d XY8_cycles' % nr_of_XY8_cycles
    return {"seqname":name, "max_seq_time":max_seq_time}
