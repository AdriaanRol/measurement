#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels_lt2 as awgcfg
from measurement.config import experiment_lt2 as exp

awg = qt.instruments['AWG']


def MBI_element(seq,el_name,jump_target,goto_target):   
    MBIcfg=exp.MBIprotocol
    #FIXME: do this in the measurement class
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
   
    if exp.lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'

    if exp.lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10
   
    wait_for_adwin_dur = (1000*MBIcfg['MBI_RO_duration']+MBIcfg['wait_time_before_MBI_pulse']-MBIcfg['MBI_pulse_len'])+3000.
    seq.add_element(name=el_name,trigger_wait=True, event_jump_target=jump_target,goto_target=goto_target)

    seq.add_pulse('wait', channel = chan_mwI, element =el_name,
        start = 0, duration = MBIcfg['wait_time_before_MBI_pulse'], amplitude = 0)
            
    seq.add_pulse('MBI_pulse', channel = chan_mwI, element = el_name,
        start = 0, duration = MBIcfg['MBI_pulse_len'], amplitude = MBIcfg['MBI_pulse_amp'],
        shape = 'rectangular',start_reference = 'wait',link_start_to = 'end')
    seq.add_pulse('pulse_mod2', channel = chan_mw_pm, element = el_name,
        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
        start_reference = 'MBI_pulse', link_start_to = 'start', 
        duration_reference = 'MBI_pulse', link_duration_to = 'duration',amplitude = 2.0)

    seq.add_pulse('wait_for_ADwin', channel = chan_mwI, element = el_name,
        start = 0, duration = wait_for_adwin_dur, amplitude = 0, start_reference = 'MBI_pulse',
        link_start_to = 'end', shape = 'rectangular')

def shelving_pulse(seq,pulse_name,el_name):
    MBIcfg=exp.MBIprotocol
    pulsescfg = exp.pulses
    #FIXME: do this in the measurement class
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
   
    if exp.lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'

    if exp.lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10
    
    seq.add_pulse('wait_before'+pulse_name, channel = chan_mwI, element = el_name,
            start = 0, duration =MBIcfg['wait_time_before_shelv_pulse'], amplitude = 0, shape = 'rectangular')

    seq.add_pulse(pulse_name, channel = chan_mwI, element = el_name,
            start = 0, duration =pulsescfg['shelving_len'], amplitude = pulsescfg['shelving_amp'], 
            start_reference = 'wait_before'+pulse_name, link_start_to = 'end', shape = 'rectangular')           
    seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name, link_start_to = 'start', duration_reference = pulse_name, 
            link_duration_to = 'duration',amplitude = 2.0)
    seq.add_pulse('wait_after'+pulse_name, channel = chan_mwI, element = el_name,
                    start = 0, duration =15, amplitude = 0, start_reference = pulse_name,
                    link_start_to = 'end', shape = 'rectangular')    
    last='wait_after'+pulse_name
    return last

def readout_pulse (seq, pulse_name, first, el_name):
    MBIcfg=exp.MBIprotocol
    pulsescfg = exp.pulses

        #FIXME: do this in the measurement class
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1
   
    if exp.lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'

    if exp.lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10
    seq.add_pulse(pulse_name, channel = chan_mwI, element = el_name,
            start = 0, duration =pulsescfg['pi2pi_len'], amplitude = pulsescfg['pi2pi_amp'],
            start_reference = first, link_start_to = 'end', shape = 'rectangular')

    seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name, link_start_to = 'start', 
            duration_reference = pulse_name, link_duration_to = 'duration', 
            amplitude = 2.0)
    last = pulse_name
    return last

  


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

