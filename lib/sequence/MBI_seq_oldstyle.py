#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels_lt2 as awgcfg
from measurement.lib.config import experiment_lt2 as exp

awg = qt.instruments['AWG']


def MBI_element(seq,el_name,freq,jump_target,goto_target):   
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
            
    seq.add_pulse('MBI_pulse_I', channel = chan_mwI, element = el_name,
        start = 0, duration = MBIcfg['MBI_pulse_len'], amplitude = MBIcfg['MBI_pulse_amp'],
        shape = 'sine',frequency=freq,envelope='erf',start_reference = 'wait',link_start_to = 'end')
    seq.add_pulse('MBI_pulse_Q', channel = chan_mwQ, element = el_name,
        start = 0, duration = MBIcfg['MBI_pulse_len'], amplitude = MBIcfg['MBI_pulse_amp'],
        shape = 'sine',frequency=freq,envelope='erf',start_reference = 'wait',link_start_to = 'end')
    seq.add_pulse('pulse_mod2', channel = chan_mw_pm, element = el_name,
        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
        start_reference = 'MBI_pulse_I', link_start_to = 'start', 
        duration_reference = 'MBI_pulse_I', link_duration_to = 'duration',amplitude = 2.0)

    seq.add_pulse('wait_for_ADwin', channel = chan_mwI, element = el_name,
        start = 0, duration = wait_for_adwin_dur, amplitude = 0, start_reference = 'MBI_pulse_I',
        link_start_to = 'end', shape = 'rectangular')

def shelving_pulse(seq,pulse_name,freq,el_name):
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

    seq.add_pulse(pulse_name+'I', channel = chan_mwI, element = el_name,
            start = 0, duration =pulsescfg['shelving_len'], amplitude = pulsescfg['shelving_amp'], 
            start_reference = 'wait_before'+pulse_name, 
            link_start_to = 'end', shape = 'sine',envelope='erf',frequency=freq)  
    seq.add_pulse(pulse_name+'Q', channel = chan_mwQ, element = el_name,
            start = 0, duration =pulsescfg['shelving_len'], amplitude = pulsescfg['shelving_amp'], 
            start_reference = 'wait_before'+pulse_name, 
            link_start_to = 'end', shape = 'sine',envelope='erf',frequency=freq)
    seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I', link_start_to = 'start', duration_reference = pulse_name+'I', 
            link_duration_to = 'duration',amplitude = 2.0)
    seq.add_pulse('wait_after'+pulse_name, channel = chan_mwI, element = el_name,
                    start = 0, duration =15, amplitude = 0, start_reference = pulse_name+'I',
                    link_start_to = 'end', shape = 'rectangular')    
    last='wait_after'+pulse_name
    return last

def readout_pulse(seq, freq=2E6,pulse_name='', first='', el_name=''):
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
    
    seq.add_pulse(pulse_name+'I', channel = chan_mwI, element = el_name,
            start = 0, duration =pulsescfg['pi2pi_len'], amplitude = pulsescfg['pi2pi_amp'],
            start_reference = first, link_start_to = 'end', shape = 'sine',envelope='erf',frequency=freq)
    seq.add_pulse(pulse_name+'Q', channel = chan_mwQ, element = el_name,
            start = 0, duration =pulsescfg['pi2pi_len'], amplitude = pulsescfg['pi2pi_amp'],
            start_reference = first, link_start_to = 'end', shape = 'sine',envelope='erf',frequency=freq)

    seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I', link_start_to = 'start', 
            duration_reference = pulse_name+'I', link_duration_to = 'duration', 
            amplitude = 2.0)
    last = pulse_name+'I'
    return last

  
def RF_sweep(m,seq):
   
    
    MBIcfg=exp.MBIprotocol
    pulsescfg = exp.pulses    ####

    # vars for the channel names
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
    ####

    for i in np.arange(m.nr_of_datapoints):
        MBI_element(seq,el_name='MBI_pulse'+str(i),freq=m.MBI_mod_freq, 
               jump_target='spin_control'+str(i),
               goto_target='MBI_pulse'+str(i))

        if i == m.nr_of_datapoints-1:
            seq.add_element(name = 'spin_control'+str(i), 
                trigger_wait = True, goto_target = 'MBI_pulse0')
        else:
            seq.add_element(name = 'spin_control'+str(i), 
                trigger_wait = True)
        
        last = shelving_pulse(seq, pulse_name = 'shelving_pulse_'+str(i),
                    freq=m.MBI_mod_freq,el_name = 'spin_control'+str(i))
        
        seq.add_pulse('wait_before_RF', channel = chan_mwI, element = 'spin_control'+str(i),
                start = 0,start_reference=last,link_start_to='end', duration = 2000,
                amplitude = 0,shape='rectangular')
        last = 'wait_before_RF'

        seq.add_pulse('RF', channel = chan_RF, element = 'spin_control'+str(i),
                start = 0,start_reference=last,link_start_to='end', duration = m.RF_pulse_len[i],
                amplitude = m.RF_pulse_amp[i],shape='sine',frequency=m.RF_freq[i],envelope='erf')
        seq.add_pulse('wait_before_readout', channel = chan_mwI, element = 'spin_control'+str(i),
                start = 0, duration =1000., amplitude = 0, start_reference = 'RF',
                link_start_to = 'end', shape = 'rectangular')

        

        readout_pulse (seq, freq=m.RO_mod_freq,pulse_name = 'readout_pulse_'+str(i),
                first = 'wait_before_readout',el_name = 'spin_control'+str(i))          

        
    seq_wait_time = (2*m.MBIdic['wait_time_before_MBI_pulse']+
                                    m.MBIdic['MBI_pulse_len']+
                                    m.RF_pulse_len.max()+
                                    m.MBIdic['wait_time_before_shelv_pulse']+
                                    m.pulsedic['shelving_len']+5000)/1000


    return seq_wait_time



def MW_sweep (m, seq):
   
    
    MBIcfg=exp.MBIprotocol
    pulsescfg = exp.pulses    ####

    # vars for the channel names
    
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
    ####
    RO_steps_for_dp=1
    for i in np.arange(m.nr_of_datapoints):
        MBI_element(seq,el_name='MBI_pulse'+str(i),freq=m.MBI_mod_freq[i], 
               jump_target='spin_control_'+str(i)+'RO_step_0',
               goto_target='MBI_pulse'+str(i))

        for k in np.arange(RO_steps_for_dp):
            el_name = 'spin_control_'+str(i)+'RO_step_'+str(k)
            if k == RO_steps_for_dp-1:
                m.reps=1
            else:
                m.reps=RO_steps_for_dp-1
            if (k==0) or (k==RO_steps_for_dp-1):
                if (i == m.nr_of_datapoints-1) and (k==RO_steps_for_dp-1):
                    seq.add_element(name = el_name, 
                    trigger_wait = True, goto_target = 'MBI_pulse0')
                elif (m.reps==1) :
                    seq.add_element(name = el_name,
                        trigger_wait = True)
                else:
                    seq.add_element(name = el_name, event_jump_target='spin_control_'+str(i)+'RO_step_'+str(RO_steps_for_dp-1),
                            goto_target='spin_control_'+str(i)+'RO_step_'+str(k), trigger_wait = True)
                if m.do_shelv_pulse:
                    last = shelving_pulse(seq,'shelving_pulse',m.MBI_mod_freq[i],el_name)

                for j in np.arange(m.nr_of_MW_pulses):

                    if (j ==0) and (m.do_shelv_pulse == False):
                        seq.add_pulse('wait'+str(j), channel = chan_mw_pm, element = el_name,
                            start = 0, duration = MBIcfg['wait_time_before_MBI_pulse'], amplitude = 0)
                    else:
                        seq.add_pulse('wait'+str(j), channel = chan_mw_pm, element = el_name,
                            start = 0, duration = 20, start_reference=last,link_start_to='end',amplitude = 0)
                    if (k==RO_steps_for_dp-1):
                        seq.add_pulse('MW_pulse_I'+str(j),channel=chan_mwI,element=el_name,start=0,
                            start_reference= 'wait'+str(j),link_start_to='end',
                            duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                            shape='sine',envelope='erf',frequency=m.MW_mod_freq[i])
                        seq.add_pulse('MW_pulse_Q'+str(j),channel=chan_mwQ,element=el_name,start=0,
                            start_reference= 'wait'+str(j),link_start_to='end',
                            duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                            shape='sine',envelope='erf',frequency=m.MW_mod_freq[i])
                        seq.add_pulse('MW_pulse_mod'+str(j),channel=chan_mw_pm,element=el_name,
                            start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
                            start_reference='MW_pulse_I'+str(j),link_start_to='start',
                            duration_reference='MW_pulse_I'+str(j),link_duration_to='duration', amplitude=2.0)
                        last= 'MW_pulse_I'+str(j)
                    else:
                        seq.add_pulse('MW_pulse_I'+str(j),channel=chan_mwI,element=el_name,start=0,
                            start_reference= 'wait'+str(j),link_start_to='end',
                            duration=m.MW1_pulse_len[i], amplitude = m.MW1_pulse_amp[i],
                            shape='sine',envelope='erf',frequency=m.MW1_mod_freq[i])
                        seq.add_pulse('MW_pulse_Q'+str(j),channel=chan_mwQ,element=el_name,start=0,
                            start_reference= 'wait'+str(j),link_start_to='end',
                            duration=m.MW1_pulse_len[i], amplitude = m.MW1_pulse_amp[i],
                            shape='sine',envelope='erf',frequency=m.MW1_mod_freq[i])
                        seq.add_pulse('MW_pulse_mod'+str(j),channel=chan_mw_pm,element=el_name,
                            start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
                            start_reference='MW_pulse_I'+str(j),link_start_to='start',
                            duration_reference='MW_pulse_I'+str(j),link_duration_to='duration', amplitude=2.0)
                        last= 'MW_pulse_I'+str(j)


                seq.add_pulse('final_wait', channel = chan_mwI, element = el_name,
                        start = 0, duration =MBIcfg['wait_time_before_MBI_pulse'], amplitude = 0, start_reference = last,
                        link_start_to = 'end', shape = 'rectangular')
        
        if m.do_incr_RO_steps:
            RO_steps_for_dp = RO_steps_for_dp + m.incr_RO_steps
        else:
            RO_steps_for_dp = m.nr_of_RO_steps
        
    sequence_wait_time = (2*m.MBIdic['wait_time_before_MBI_pulse']+ 
                           m.nr_of_MW_pulses*(m.MW_pulse_len.max()+20)+1000)/1000
  
    return sequence_wait_time





def Nucl_Ramsey(m,seq):
   
    
    MBIcfg=exp.MBIprotocol
    pulsescfg = exp.pulses    ####

    # vars for the channel names
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
    ####

    for i in np.arange(m.nr_of_datapoints):
        MBI_element(seq,el_name='MBI_pulse'+str(i),freq=m.MBI_mod_freq, 
               jump_target='Pi2_pulse_first'+str(i),
               goto_target='MBI_pulse'+str(i))

        el_name='Pi2_pulse_first'+str(i)
        seq.add_element(el_name,trigger_wait=True)
        last = shelving_pulse(seq, pulse_name = 'shelving_pulse_'+str(i),
                    freq=m.MBI_mod_freq,el_name = el_name)
        
        seq.add_pulse('wait_before_RF', channel = chan_mwI, element = el_name,
                start = 0,start_reference=last,link_start_to='end', duration = 1000,
                amplitude = 0,shape='rectangular')
        last = 'wait_before_RF'
        seq.add_pulse('RF', channel = chan_RF, element =  el_name,
                start = 0,start_reference=last,link_start_to='end', duration = pulsescfg['RF_pi2_len'],
                amplitude = pulsescfg['RF_pi2_amp'],shape='sine',frequency=m.RF_freq[i],envelope='erf')
        seq.add_pulse('wait_before_readout', channel = chan_mwI, element =  el_name,
                start = 0, duration =1000., amplitude = 0, start_reference = 'RF',
                link_start_to = 'end', shape = 'rectangular')
        last='wait_before_readout'
        if m.do_MW_pulse_after_RF:
            seq.add_pulse('MW_pulse_I'+str(i),channel=chan_mwI,element=el_name,start=0,
                           start_reference= last,link_start_to='end',
                           duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                           shape='sine',envelope='erf',frequency=m.MW_mod_freq[i])
            seq.add_pulse('MW_pulse_Q'+str(i),channel=chan_mwQ,element=el_name,start=0,
                           start_reference= last,link_start_to='end',
                           duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                           shape='sine',envelope='erf',frequency=m.MW_mod_freq[i])
            seq.add_pulse('MW_pulse_mod'+str(i),channel=chan_mw_pm,element=el_name,
                           start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
                           start_reference='MW_pulse_I'+str(i),link_start_to='start',
                           duration_reference='MW_pulse_I'+str(i),link_duration_to='duration', amplitude=2.0)
        
        el_name='waiting_time'+str(i)
        seq.add_element(name=el_name,trigger_wait=False,repetitions=m.rep_wait_el)
        seq.add_pulse('wait_time', channel = chan_mwI, element = el_name,
                start = 0, duration =1000., amplitude = 0, shape = 'rectangular')
        
        el_name='Pi2_pulse_second'+str(i)
        seq.add_element(name = el_name, trigger_wait=False)
        seq.add_pulse('first_wait', channel = chan_mwI, element = el_name,
                start = 0, duration =10., amplitude = 0, shape = 'rectangular')
        last='first_wait'
        if m.do_MW_pulse_after_RF:
            seq.add_pulse('MW_pulse_I'+str(i),channel=chan_mwI,element=el_name,start=0,
                           link_start_to='end',start_reference=last,
                           duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                           shape='sine',envelope='erf',frequency=m.MW_mod_freq[i])
            seq.add_pulse('MW_pulse_Q'+str(i),channel=chan_mwQ,element=el_name,start=0,
                           link_start_to='end', start_reference=last,
                           duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                           shape='sine',envelope='erf',frequency=m.MW_mod_freq[i])
            seq.add_pulse('MW_pulse_mod'+str(i),channel=chan_mw_pm,element=el_name,
                           start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
                           start_reference='MW_pulse_I'+str(i),link_start_to='start',
                           duration_reference='MW_pulse_I'+str(i),link_duration_to='duration', amplitude=2.0)
            last = 'MW_pulse_I'+str(i)
        seq.add_pulse('wait_before_readout', channel = chan_mwI, element = el_name,
                start = 0,start_reference=last,link_start_to='end',
                duration =1000., amplitude = 0, shape = 'rectangular')
        seq.add_pulse('RF', channel = chan_RF, element = el_name, start = 0,
                start_reference='wait_before_readout',link_start_to='end', 
                duration = pulsescfg['RF_pi2_len'],amplitude = pulsescfg['RF_pi2_amp'],
                shape='sine',frequency=m.RF_freq[i],envelope='erf',phase=m.RF_phase[i])
        seq.add_pulse('wait_after_RF', channel = chan_mwI, element = el_name,
                start = 0,start_reference='RF',link_start_to='end', duration = 2000,
                amplitude = 0,shape='rectangular')
        
        el_name='readout_pulse'+str(i)
        if i == m.nr_of_datapoints-1:
            seq.add_element(name = el_name, trigger_wait = True, goto_target = 'MBI_pulse0')
        else:
            seq.add_element(name = el_name, trigger_wait=True)

        seq.add_pulse('wait_before_readout', channel = chan_mwI, element = el_name,
                start = 0, duration =1000., amplitude = 0, shape = 'rectangular')    
        readout_pulse (seq, freq=m.RO_mod_freq,pulse_name = 'readout_pulse_'+str(i),
                first = 'wait_before_readout',el_name = el_name)    
        
    seq_wait_time = (pulsescfg['RF_pi2_len']/1000)+7


    return seq_wait_time



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

