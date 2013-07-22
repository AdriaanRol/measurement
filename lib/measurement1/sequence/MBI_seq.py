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
        shape = 'cosine',frequency=freq,start_reference = 'wait',link_start_to = 'end')
    seq.add_pulse('MBI_pulse_Q', channel = chan_mwQ, element = el_name,
        start = 0, duration = MBIcfg['MBI_pulse_len'], amplitude = MBIcfg['MBI_pulse_amp'],
        shape = 'sine',frequency=freq,start_reference = 'wait',link_start_to = 'end')
    seq.add_pulse('pulse_mod2', channel = chan_mw_pm, element = el_name,
        start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
        start_reference = 'MBI_pulse_I', link_start_to = 'start', 
        duration_reference = 'MBI_pulse_I', link_duration_to = 'duration',amplitude = 2.0)

    seq.add_pulse('wait_for_ADwin', channel = chan_mwI, element = el_name,
        start = 0, duration = wait_for_adwin_dur, amplitude = 0, start_reference = 'MBI_pulse_I',
        link_start_to = 'end', shape = 'rectangular')
def shelving_pulse(seq,pulse_name,freq,el_name,first='',ret_time=False):
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
    if (first == ''):

        seq.add_pulse('wait_before'+pulse_name, channel = chan_mwI, element = el_name,
            start = 0, duration =MBIcfg['wait_time_before_shelv_pulse'], amplitude = 0, shape = 'rectangular')
        last='wait_before'+pulse_name
    else:
        last=first
    seq.add_pulse(pulse_name+'I', channel = chan_mwI, element = el_name,
            start = 0, duration =pulsescfg['shelving_len'], amplitude = pulsescfg['shelving_amp'], 
            start_reference = last, 
            link_start_to = 'end', shape = 'cosine',frequency=freq)  
    seq.add_pulse(pulse_name+'Q', channel = chan_mwQ, element = el_name,
            start = 0, duration =pulsescfg['shelving_len'], amplitude = pulsescfg['shelving_amp'], 
            start_reference = last, 
            link_start_to = 'end', shape = 'sine',frequency=freq)
    seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I', link_start_to = 'start', duration_reference = pulse_name+'I', 
            link_duration_to = 'duration',amplitude = 2.0)
    seq.add_pulse('wait_after'+pulse_name, channel = chan_mwI, element = el_name,
                    start = 0, duration =30, amplitude = 0, start_reference = pulse_name+'I',
                    link_start_to = 'end', shape = 'rectangular')    
    last='wait_after'+pulse_name
    seq_time=(MBIcfg['wait_time_before_shelv_pulse']+pulsescfg['shelving_len']+30)/1000.
    if ret_time:
        return last, seq_time
    else:
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
            start_reference = first, link_start_to = 'end', shape = 'cosine',frequency=freq)
    seq.add_pulse(pulse_name+'Q', channel = chan_mwQ, element = el_name,
            start = 0, duration =pulsescfg['pi2pi_len'], amplitude = pulsescfg['pi2pi_amp'],
            start_reference = first, link_start_to = 'end', shape = 'sine',frequency=freq)

    seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I', link_start_to = 'start', 
            duration_reference = pulse_name+'I', link_duration_to = 'duration', 
            amplitude = 2.0)
    last = pulse_name+'I'
    return last

def get_pulse_len(theta,caldict):

    a=caldict['a']
    A=caldict['A']
    f=caldict['f']
    phi=caldict['phi']
    len = (np.arccos((np.cos(theta*np.pi/180.)+1.-2.*a)/(2.*A))-phi*np.pi/180.)/f/np.pi/2.
    return len

def get_rabi_len(theta,CORPSE_frabi):
    thetarad = theta*np.pi/180.
    theta1 = np.mod(thetarad/2.-np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi
    theta2 = np.mod(-2.*np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi
    theta3 = np.mod(thetarad/2.-np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi
    
    MW1_dur = theta1/CORPSE_frabi/360.
    MW2_dur = theta2/CORPSE_frabi/360.
    MW3_dur = theta3/CORPSE_frabi/360.
    return MW1_dur, MW2_dur
def loadData (fname):

    data = {}
    i = 0
    with open(fname) as inf:
        N = []
        RO = []
        ROcorr = []
        errRO = []
        for line in inf:
            li = line.strip()
            if not li.startswith("#"):
                parts = line.split()
                N.append(float(parts[0]))
                RO.append(float(parts [1]))
                ROcorr.append(float(parts[2]))
                errRO.append(float(parts[3]))
                i = i+1
        data = {'x_axis': N, 'rawRO': RO, 'corrRO': ROcorr, 'errRO': errRO}
    return data

'''
def get_pulse_len (theta, calibFile  = r'D:/measuring/data/20130110/173403_MBI_CORPSE_init0_drive_halfway_0_and_+1/SSRO_readout.dat'):
    
    p = (1+np.cos(theta*np.pi/180.))/2.
    a = loadData(calibFile)
    x = a['x_axis']
    y = a['corrRO']
    diff = y-p
    diffAbs = abs(diff)
    ind = diffAbs.argmin()
    if ((diff[ind]>0) and (diff[ind-1]<0)):
        y1 = y[ind-1]
        y2 = y[ind]
        x1 = x[ind-1]
        x2 = x[ind]
    else:
        y1 = y[ind]
        y2 = y[ind+1]
        x1 = x[ind]
        x2 = x[ind]+1
    m = (y2-y1)/(x2-x1)
    q = y2-m*x2
    len = (p - q)/m
    return len
'''








def CORPSE_pulse(seq, d,ret_last=False):
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
   
    if ('phase' in d.keys()):
        phase=d['phase']
    else:
        phase=0
    theta = d['theta']
    CORPSE_frabi= d['CORPSE_frabi']
    CORPSE_amp = d['CORPSE_amp']
    freq= d['freq'],
    if ('pulse_name' in d.keys()):
        pulse_name=d['pulse_name']
    else:
        pulse_name='CORPSE'
    first=d['first']
    el_name=d['el_name']

    thetarad = theta*np.pi/180.
    theta1 = np.mod(thetarad/2.-np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi+360.
    theta2 = np.mod(-2.*np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi
    theta3 = np.mod(thetarad/2.-np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi+360.
    
    MW1_dur = int(theta1/CORPSE_frabi/360.)
    MW2_dur = int(theta2/CORPSE_frabi/360.)
    MW3_dur = int(theta3/CORPSE_frabi/360.)
    if (d['theta'] ==0):
        CORPSE_amp = 0
        
    #MW1_dura=int(get_pulse_len(theta1,CORPSE_cal))
    #MW2_dura=int(get_pulse_len(theta2,CORPSE_cal))
    #MW3_dura=int(get_pulse_len(theta3,CORPSE_cal))
    #CORPSE_cal = d['CORPSE_cal']
    #print type(MW1_dura)
    #print MW1_dur-MW1_dura
    #print MW2_dur-MW2_dura
    #print MW3_dur-MW3_dura
    #Pulse 1
    seq.add_pulse(pulse_name+'I1', channel = chan_mwI, element = el_name,
            start = 0, duration =MW1_dur, amplitude = CORPSE_amp,
            start_reference = first, link_start_to = 'end', shape = 'cosine',frequency=freq,phase=phase)
    seq.add_pulse(pulse_name+'Q1', channel = chan_mwQ, element = el_name,
            start = 0, duration =MW1_dur, amplitude = CORPSE_amp,
            start_reference = first, link_start_to = 'end', shape = 'sine',frequency=freq,phase=phase)
    seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I1', link_start_to = 'start', 
            duration_reference = pulse_name+'I1', link_duration_to = 'duration', 
            amplitude = 2.0)
    seq.add_pulse(pulse_name+'wait_time1', channel = chan_mwI, element = el_name,
            start = 0, duration =pulsescfg['time_between_CORPSE'], amplitude = 0.0,
            start_reference = pulse_name+'I1', link_start_to = 'end')

    last=pulse_name+'wait_time1'
   #Pulse 2
    seq.add_pulse(pulse_name+'I2', channel = chan_mwI, element = el_name,
            start = 0, duration =MW2_dur, amplitude = -CORPSE_amp,
            start_reference = last, link_start_to = 'end', shape = 'cosine',frequency=freq,phase=phase)
    seq.add_pulse(pulse_name+'Q2', channel = chan_mwQ, element = el_name,
            start = 0, duration =MW2_dur, amplitude = -CORPSE_amp,
            start_reference = last, link_start_to = 'end', shape = 'sine',frequency=freq,phase=phase)
    seq.add_pulse(pulse_name+'_mod2', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I2', link_start_to = 'start', 
            duration_reference = pulse_name+'I2', link_duration_to = 'duration', 
            amplitude =2.0)
    seq.add_pulse(pulse_name+'wait_time2', channel = chan_mwI, element = el_name,
            start = 0, duration =pulsescfg['time_between_CORPSE'], amplitude = 0.0,
            start_reference = pulse_name+'I2', link_start_to = 'end')
    
    last=pulse_name+'wait_time2'
   #Pulse 3
    seq.add_pulse(pulse_name+'I3', channel = chan_mwI, element = el_name,
            start = 0, duration =MW3_dur, amplitude =CORPSE_amp,
            start_reference = last, link_start_to = 'end', shape = 'cosine',frequency=freq,phase=phase)
    seq.add_pulse(pulse_name+'Q3', channel = chan_mwQ, element = el_name,
            start = 0, duration =MW3_dur, amplitude = CORPSE_amp,
            start_reference = last, link_start_to = 'end', shape = 'sine',frequency=freq,phase=phase)

    seq.add_pulse(pulse_name+'_mod3', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I3', link_start_to = 'start', 
            duration_reference = pulse_name+'I3', link_duration_to = 'duration', 
            amplitude = 2.0)
    
    
    last = pulse_name+'I3'
    total_len= MW1_dur+MW2_dur+MW3_dur+3*(pulsescfg['time_between_CORPSE'])
    if ret_last:
        return last , total_len
    else:
        return total_len
  
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
        
        if m.do_shel:
            last = shelving_pulse(seq, pulse_name = 'shelving_pulse_'+str(i),
                    freq=m.MBI_mod_freq,el_name = 'spin_control'+str(i))
        else:
            seq.add_pulse('first_wait', channel = chan_mwI, element = 'spin_control'+str(i),
                start = 0, duration =100., amplitude = 0, shape = 'rectangular')
            last='first_wait'

        seq.add_pulse('wait_before_RF', channel = chan_mwI, element = 'spin_control'+str(i),
                start = 0,start_reference=last,link_start_to='end', duration = 2000,
                amplitude = 0,shape='rectangular')
        last = 'wait_before_RF'

        seq.add_pulse('RF', channel = chan_RF, element = 'spin_control'+str(i),
                start = 0,start_reference=last,link_start_to='end', duration = m.RF_pulse_len[i],
                amplitude = m.RF_pulse_amp[i],shape='sine',frequency=m.RF_freq[i],
                envelope='erf',envelope_risetime=500.)
        seq.add_pulse('wait_before_readout', channel = chan_mwI, element = 'spin_control'+str(i),
                start = 0, duration =2000., amplitude = 0, start_reference = 'RF',
                link_start_to = 'end', shape = 'rectangular')

        last='wait_before_readout'
        d={}
        d['first']=last
        d['nr_of_CORPSE_pulses']=1
        d['pulse_name']='CORPSE1'
        d['time_between_pulses']=5.
        d['theta']=90
        d['phase']=0
        d['tau']=m.projective_ramsey_time
        d['CORPSE_frabi']=m.CORPSE_frabi
        d['CORPSE_amp']=m.CORPSE_amp
        d['freq'] = m.RO_freq
        d['el_name']='spin_control'+str(i)

        last,Ctime1 = CORPSE_pulse(seq, d,ret_last=True)
        seq.add_pulse('tau', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = d['tau'], start_reference=last,link_start_to='end',amplitude = 0)
        d['first']='tau'
        d['pulse_name']='CORPSE2'
        d['phase']=90

    
        last,Ctime2 = CORPSE_pulse(seq, d,ret_last=True)     

        
    seq_wait_time = (2*m.MBIdic['wait_time_before_MBI_pulse']+
                                    m.MBIdic['MBI_pulse_len']+
                                    m.RF_pulse_len.max()+
                                    m.MBIdic['wait_time_before_shelv_pulse']+
                                    m.pulsedic['shelving_len']+Ctime1+Ctime2+5000)/1000


    return seq_wait_time

def add_N_MW_pulses(seq,d,ret_last=False):
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
    
    if ('phase' in d.keys()):
        phase=d['phase']
    else:
        phase=0
    if 'pulse_name' in d.keys():
        pname=d['pulse_name']
    else:
        pname=''
    last = d['first']
    for j in np.arange(d['nr_of_MW_pulses']):
        
        seq.add_pulse(pname+'MW_pulse_I'+str(j),channel=chan_mwI,element=d['el_name'],start=0,
            start_reference= last,link_start_to='end',
            duration=d['MW_pulse_len'], amplitude = d['MW_pulse_amp'],
            shape='cosine',frequency=d['MW_mod_freq'],phase=phase)
        seq.add_pulse(pname+'MW_pulse_Q'+str(j),channel=chan_mwQ,element=d['el_name'],start=0,
            start_reference= last,link_start_to='end',
            duration=d['MW_pulse_len'], amplitude = d['MW_pulse_amp'],
            shape='sine',frequency=d['MW_mod_freq'],phase=phase)
        seq.add_pulse(pname+'MW_pulse_mod'+str(j),channel=chan_mw_pm,element=d['el_name'],
            start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
            start_reference=pname+'MW_pulse_I'+str(j),link_start_to='start',
            duration_reference=pname+'MW_pulse_I'+str(j),link_duration_to='duration', amplitude=2.0)
        seq.add_pulse(pname+'wait'+str(j), channel = chan_mw_pm, element = d['el_name'],
                start = 0, start_reference=pname+'MW_pulse_I'+str(j),link_start_to='end',
                duration = d['time_between_pulses'], amplitude = 0)

        last= pname+'wait'+str(j)

    
    sequence_wait_time = (d['nr_of_MW_pulses']*(d['time_between_pulses']+d['MW_pulse_len']+20)+1000)/1000
    if ret_last:
        return last,sequence_wait_time
    else:
        return sequence_wait_time
def add_N_CORPSE_pulses(seq,d,ret_last=False):
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
    if 'pulse_name' in d.keys():
        pname=d['pulse_name']
    else:
        pname=''
    for j in np.arange(d['nr_of_CORPSE_pulses']):

        if (j ==0) and (d['do_shelv_pulse'] == False):
            seq.add_pulse(pname+'wait'+str(j), channel = chan_mw_pm, element = d['el_name'],
                start = 0, duration = MBIcfg['wait_time_before_MBI_pulse'], amplitude = 0)
        else:
            seq.add_pulse(pname+'wait'+str(j), channel = chan_mw_pm, element = d['el_name'],
                start = 0, duration = 20, start_reference=d['first'],link_start_to='end',amplitude = 0)
        last=pname+'wait'+str(j)
        d['first']=last
        d['pulse_name']='CORPSE'+str(j)
        last,Ctime = CORPSE_pulse(seq, d,ret_last=True)


    seq.add_pulse(pname+'final_wait', channel = chan_mwI, element = d['el_name'],
            start = 0, duration =d['finalwait_dur'], amplitude = 0, start_reference = last,
            link_start_to = 'end', shape = 'rectangular')

    last=pname+'final_wait'
    
    sequence_wait_time = (MBIcfg['wait_time_before_MBI_pulse']+d['finalwait_dur']+ 
                           d['nr_of_CORPSE_pulses']*(Ctime+20)+1000)/1000
    if ret_last:
        return last,sequence_wait_time
    else:
        return sequence_wait_time
def add_weak_meas(seq,d):
    
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
    seq.add_pulse('wait', channel = chan_mw_pm, element = d['el_name'],
                  start = 0, duration = 20, start_reference=d['first'],link_start_to='end',amplitude = 0)
    last='wait'
    maxtime=[]
    
    strength=d['meas_theta']
    pd={}
    pd['theta']=(90-strength)
    
    pd['CORPSE_frabi']=d['CORPSE_nsel_frabi']
    pd['CORPSE_amp']=d['CORPSE_nsel_amp']
    pd['freq']= d['CORPSE_freq']
    pd['first']=last
    pd['el_name']=d['el_name']
    pd['do_shelv_pulse']=d['do_shelv_pulse']
    pd['pulse_name']='sel'+'final_wait'
    pd['nr_of_CORPSE_pulses']=1
    pd['finalwait_dur']=20.
    pd['CORPSE_cal']=pulsescfg['CORPSE_cal']
    last,time1 = add_N_CORPSE_pulses(seq,pd,ret_last=True)
    
    
    pd={}
    pd['first']=last
   
    pd['el_name']=d['el_name']
    pd['MW_pulse_amp']=d['sel_amp']*0
    pd['MW_pulse_len']=2*strength/d['sel_frabi']/360.
    pd['MW_mod_freq'] =d['RO_line']
    pd['nr_of_MW_pulses']=1
    pd['do_shelv_pulse']=True
    time2 = add_N_MW_pulses(seq,pd)
    
    
    maxtime.append(time1+time2)
    
    return max(maxtime)

def ramsey(seq,d,ret_last=False):
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
    if 'pulse_name' in d.keys():
        pname=d['pulse_name']
    else:
        pname=''


    if (d['do_shelv_pulse'] == False):
        seq.add_pulse(pname+'wait', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = MBIcfg['wait_time_before_MBI_pulse'], amplitude = 0)
        last=pname+'wait'
        RF_shel_len = MBIcfg['wait_time_before_MBI_pulse']
    else:
        seq.add_pulse(pname+'wait_RF', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = 2000, start_reference=d['first'],link_start_to='end',amplitude = 0)
        seq.add_pulse(pname+'RF', channel = chan_RF, element = d['el_name'],
                start = 0,start_reference=pname+'wait_RF',link_start_to='end', duration = d['RF_pulse_len'],
                amplitude = d['RF_pulse_amp'],shape='sine',frequency=d['RF_freq'],envelope='erf')
        seq.add_pulse(pname+'wait_RF_2', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = 2000, start_reference=pname+'RF',link_start_to='end',amplitude = 0)
        last=pname+'wait_RF_2'
        RF_shel_len = d['RF_pulse_len']+2*100
    d['first']=last
    d['pulse_name']='MW1'
    d['time_between_pulses']=0.
    phasesecondpulse=d['phase']
    d['phase']=0
    last,Ctime1 = add_N_MW_pulses(seq, d,ret_last=True)
    seq.add_pulse('tau', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = d['tau'], start_reference=last,link_start_to='end',amplitude = 0)
    d['first']='tau'
    d['pulse_name']='MW2'
    d['phase']=phasesecondpulse
    if (d['tau']==0) and (d['weak']):
        d['MW_pulse_amp']=0
        d['MW_pulse_len']=0
    d['time_between_pulses']=1000.
    last,Ctime =  add_N_MW_pulses(seq, d,ret_last=True)
    if not 'RF2_pulse_amp' in d.keys():
        d['RF2_pulse_amp'] = 0
        d['RF2_pulse_len'] = 0
    seq.add_pulse(pname+'wait_RF2', channel = chan_mw_pm, element = d['el_name'],
                    start = 0, duration = 2000, start_reference=last,link_start_to='end',amplitude = 0)
    seq.add_pulse(pname+'RF2', channel = chan_RF, element = d['el_name'],
                start = 0,start_reference=pname+'wait_RF2',link_start_to='end', duration = d['RF2_pulse_len'],
                amplitude = d['RF2_pulse_amp'],shape='sine',frequency=d['RF2_freq'],envelope='erf',phase=d['RF2_phase'])
    seq.add_pulse(pname+'wait_RF2_2', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = 2000, start_reference=pname+'RF',link_start_to='end',amplitude = 0)
    
    seq.add_pulse(pname+'final_wait', channel = chan_mwI, element = d['el_name'],
            start = 0, duration =d['finalwait_dur'], amplitude = 0, start_reference = pname+'wait_RF2_2',
            link_start_to = 'end', shape = 'rectangular')

    last=pname+'final_wait'
    
    sequence_wait_time = (RF_shel_len+d['RF2_pulse_len']+d['finalwait_dur']+ 
                           (2*Ctime+20)+d['tau']+9000)/1000
    if ret_last:
        return last,sequence_wait_time
    else:
        return sequence_wait_time
def ramsey_CORPSE(seq,d,ret_last=False):
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
    if 'pulse_name' in d.keys():
        pname=d['pulse_name']
    else:
        pname=''


    if (d['do_shelv_pulse'] == False):
        if d['first']=='':
            seq.add_pulse(pname+'wait', channel = chan_mw_pm, element = d['el_name'],
                start = 0, duration = MBIcfg['wait_time_before_MBI_pulse'], amplitude = 0)
        else:
            seq.add_pulse(pname+'wait', channel = chan_mw_pm, element = d['el_name'],
                start = 0, duration = MBIcfg['wait_time_before_MBI_pulse'], 
                amplitude = 0,link_start_to='end',start_reference=d['first'])
        last=pname+'wait'
        RF_shel_len = MBIcfg['wait_time_before_MBI_pulse']
    else:
        seq.add_pulse(pname+'wait_RF', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = 2000, start_reference=d['first'],link_start_to='end',amplitude = 0)
        seq.add_pulse(pname+'RF', channel = chan_RF, element = d['el_name'],
                start = 0,start_reference=pname+'wait_RF',link_start_to='end', duration = d['RF_pulse_len'],
                amplitude = d['RF_pulse_amp'],shape='sine',frequency=d['RF_freq'],envelope='erf',
            envelope_risetime=500.,phase=d['RF_phase'])
        seq.add_pulse(pname+'wait_RF_2', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = 2000, start_reference=pname+'RF',link_start_to='end',amplitude = 0)
        last=pname+'wait_RF_2'
        RF_shel_len = d['RF_pulse_len']+2*100 + 4000

    d['first']=last
    d['nr_of_CORPSE_pulses']=1
    d['pulse_name']='CORPSE1'
    d['time_between_pulses']=5.
    d['theta']=90
    phasesecondpulse=d['phase']
    d['phase']=0
    

    last,Ctime1 = CORPSE_pulse(seq, d,ret_last=True)
    seq.add_pulse('tau', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = d['tau'], start_reference=last,link_start_to='end',amplitude = 0)
    if (d['tau']==0) and (d['weak']):
        d['theta']=0
    d['first']='tau'
    d['pulse_name']='CORPSE2'
    d['phase']=phasesecondpulse

    last,Ctime = CORPSE_pulse(seq, d,ret_last=True)
    RF2_len = 0
    RF3_len = 0
    
   
    if 'RF2_pulse_amp' in d.keys():
        seq.add_pulse(pname+'wait_RF2', channel = chan_mw_pm, element = d['el_name'],
                        start = 0, duration = 2000, start_reference=last,link_start_to='end',amplitude = 0)
        seq.add_pulse(pname+'RF2', channel = chan_RF, element = d['el_name'],
                    start = 0,start_reference=pname+'wait_RF2',link_start_to='end', duration = d['RF2_pulse_len'],
                    amplitude = d['RF2_pulse_amp'],shape='sine',frequency=d['RF2_freq'],envelope='erf',
            envelope_risetime=500.,phase=np.mod(d['RF2_phase'],360))
        seq.add_pulse(pname+'wait_RF2_2', channel = chan_mw_pm, element = d['el_name'],
                start = 0, duration = 2000, start_reference=pname+'RF2',link_start_to='end',amplitude = 0)
        RF2_len = d['RF2_pulse_len'] + 4000
        last=pname+'wait_RF2_2'
    Ctime3=0.    
    if 'RF3_pulse_amp' in d.keys():
        seq.add_pulse(pname+'wait_before_RF3', channel = chan_mw_pm, element = d['el_name'],
                start = 0, duration = 20., start_reference=last,link_start_to='end',amplitude = 0)
        last = pname+'wait_before_RF3'

        d['theta']=180.
        d['first']=last
        d['phase']=0
        d['pulse_name']='CORPSE3'
        last,Ctime3 = CORPSE_pulse(seq, d,ret_last=True)
        seq.add_pulse(pname+'wait_RF3', channel = chan_mw_pm, element = d['el_name'],
            start = 0, duration = 2000, start_reference=last,link_start_to='end',amplitude = 0)
        seq.add_pulse(pname+'RF3', channel = chan_RF, element = d['el_name'],
            start = 0,start_reference=pname+'wait_RF3',link_start_to='end', duration = d['RF3_pulse_len'],
            amplitude = d['RF3_pulse_amp'],shape='sine',frequency=d['RF3_freq'],envelope='erf',
            envelope_risetime=500.,phase=np.mod(d['RF3_phase'],360))
        seq.add_pulse(pname+'wait_RF3_2', channel = chan_mw_pm, element = d['el_name'],
                start = 0, duration = 2000, start_reference=pname+'RF3',link_start_to='end',amplitude = 0)
        RF3_len = Ctime3+d['RF3_pulse_len'] + 4000
        last=pname+'wait_RF3_2'
        print 'tau'
        print d['tau']
        print 'phase'
    if 'final_shelving' in d.keys():
        last = shelving_pulse(seq,'shelving_pulse3',d['MW_mod_freq'],d['el_name'],first=last)
    seq.add_pulse(pname+'final_wait', channel = chan_mwI, element = d['el_name'],
            start = 0, duration =d['finalwait_dur'], amplitude = 0, start_reference = last,
            link_start_to = 'end', shape = 'rectangular')

    last=pname+'final_wait'
    
    sequence_wait_time = (RF_shel_len+RF2_len+RF3_len+d['finalwait_dur']+(Ctime+Ctime1+Ctime3+20)+d['tau']+1000)/1000
    if ret_last:
        return last,sequence_wait_time
    else:
        return sequence_wait_time

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
    RO_steps_for_dp=m.nr_of_RO_steps
    seq_t_array=[]
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
                if m.do_shelv_pulse[k]:
                    last = shelving_pulse(seq,'shelving_pulse',m.MBI_mod_freq[i],el_name)
                else:
                    seq.add_pulse('firstwait',channel=chan_mwI,element=el_name,start=0,
                        duration=20., amplitude = 0)
                    last='firstwait'

                d={}
                d['el_name']=el_name
                d['do_shelv_pulse']=m.do_shelv_pulse[k]
                d['first']=last
                d['pulse_name']='pulse'
                
                
                if (k==RO_steps_for_dp-1):
                    d['weak']=False
                    for param_key in m.MWdic.keys():
                        if (type(m.MWdic[param_key])==np.ndarray):
                            d[param_key]=m.MWdic[param_key][i]
                        else:
                            d[param_key]=m.MWdic[param_key]
                    
                    sequence_wait_time=m.load_MWseq_func(seq,d)
                    seq_t_array.append(sequence_wait_time)
                else:
                    d['weak']=True
                    for param_key in m.MWdic_last.keys():
                        d[param_key]=m.MWdic_last[param_key][i]
                    
                    sequence_wait_time = m.load_MWseq_func_last(seq,d)
                    seq_t_array.append(sequence_wait_time)
        if m.do_incr_RO_steps:
            RO_steps_for_dp = RO_steps_for_dp + m.incr_RO_steps
        else:
            RO_steps_for_dp = m.nr_of_RO_steps
        
   
    return max(seq_t_array)
def WM_feedback(m, seq):
    
    
    MBIcfg=exp.MBIprotocol
    pulsescfg = exp.pulses
    ssrocfg=exp.ssroprotocol####

    # vars for the channel names
    
    chan_mw_pm = 'MW_pulsemod' #is connected to ch1m1

    if exp.lt1:
        chan_mwI = 'MW_Imod_lt1'
        chan_mwQ = 'MW_Qmod_lt1'
    else:
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'
        chan_ADwintrig='adwin_sync'
 
    if exp.lt1:
        MW_pulse_mod_risetime = 10
    else:
        MW_pulse_mod_risetime = 10
    ####
    seq_t_array=[]
    for i in np.arange(m.nr_of_datapoints):

        MBI_element(seq,el_name='MBI_pulse'+str(i),freq=m.MBI_mod_freq[i], 
               jump_target='first_msmnt_'+str(i),
               goto_target='MBI_pulse'+str(i))
    
        
        # add element for first msmnt
        el_name = 'first_msmnt_'+str(i)
        seq.add_element(name = el_name, 
                    trigger_wait = True, goto_target = 'second_msmnt'+str(i),
                    event_jump_target='basis_rot'+str(i))
        last,shel_time = shelving_pulse(seq,'shelving_pulse',m.MBI_mod_freq[i],el_name,ret_time=True)
        d={}
        d['el_name']=el_name
        d['do_shelv_pulse']=True
        d['first']=last
        d['pulse_name']='pulse'
        for param_key in m.MWdic_firstmsmnt.keys():
                        if (type(m.MWdic_firstmsmnt[param_key])==np.ndarray):
                            d[param_key]=m.MWdic_firstmsmnt[param_key][i]
                        else:
                            d[param_key]=m.MWdic_firstmsmnt[param_key]
        phase=0
        pulse_name='rabi'

        last,time = ramsey_CORPSE(seq,d,ret_last=True)
        '''
        seq.add_pulse(pulse_name+'I1', channel = chan_mwI, element = el_name,
            start = 0, duration =m.MWdic_firstmsmnt['CORPSE_amp'][i], amplitude = .86,
            start_reference = last, link_start_to = 'end', shape = 'cosine',frequency=m.MBI_mod_freq[i],phase=phase)
        seq.add_pulse(pulse_name+'Q1', channel = chan_mwQ, element = el_name,
            start = 0, duration= m.MWdic_firstmsmnt['CORPSE_amp'][i], amplitude = .86,
            start_reference = last, link_start_to = 'end', shape = 'sine',frequency=m.MBI_mod_freq[i],phase=phase)
        seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I1', link_start_to = 'start', 
            duration_reference = pulse_name+'I1', link_duration_to = 'duration', 
            amplitude = 2.0)
        last=pulse_name+ 'I1'
        time=m.MWdic_firstmsmnt['CORPSE_amp'][i]/1000.
        '''
        seq.add_pulse('wait_for_RO', channel = chan_mw_pm, element = el_name,
            start = 0, duration = 1000., amplitude = 0,
            start_reference=last,link_start_to='end')
    
        seq.add_pulse('ADwin_trigger', channel = chan_ADwintrig, element = el_name,
            start = 0, duration = 5000., amplitude = 1,
            start_reference='wait_for_RO',link_start_to='end')
        seq.add_pulse('wait_for_RO2', channel = chan_mw_pm, element = el_name,
            start = 0, duration = m.weak_RO_duration*1000.+5000, amplitude = 0,
            start_reference='ADwin_trigger',link_start_to='end')
    
        
        seq_t_array.append(time+shel_time)


        # add element for second msmnt
        el_name = 'second_msmnt'+str(i)
        seq.add_element(name = el_name, 
                    trigger_wait = False, goto_target = 'final_msmnt'+str(i))

        d={}
        d['el_name']=el_name
        d['do_shelv_pulse']=False
        d['first']=''
        d['pulse_name']='pulse'
        for param_key in m.MWdic_secondmsmnt.keys():
                        if (type(m.MWdic_secondmsmnt[param_key])==np.ndarray):
                            d[param_key]=m.MWdic_secondmsmnt[param_key][i]
                        else:
                            d[param_key]=m.MWdic_secondmsmnt[param_key]
        '''
        seq.add_pulse('wait_for_RO', channel = chan_mw_pm, element = el_name,
            start = 0, duration = 1000, amplitude = 0)
        last='wait_for_RO'
        seq.add_pulse(pulse_name+'I1', channel = chan_mwI, element = el_name,
            start = 0, duration =m.MWdic_secondmsmnt['CORPSE_amp'][i], amplitude = .86,
            start_reference = last, link_start_to = 'end', shape = 'cosine',frequency=m.MBI_mod_freq[i],phase=phase)
        seq.add_pulse(pulse_name+'Q1', channel = chan_mwQ, element = el_name,
            start = 0, duration= m.MWdic_secondmsmnt['CORPSE_amp'][i], amplitude = .86,
            start_reference = last, link_start_to = 'end', shape = 'sine',frequency=m.MBI_mod_freq[i],phase=phase)
        seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I1', link_start_to = 'start', 
            duration_reference = pulse_name+'I1', link_duration_to = 'duration', 
            amplitude = 2.0)
        last=pulse_name+ 'I1'
        time=(1000+m.MWdic_secondmsmnt['CORPSE_amp'][i])/1000.
        '''
        seq.add_pulse('wait_first', channel = chan_mw_pm, element = el_name,
            start = 0, duration =  1000., amplitude = 0) 
        d['first']='wait_first'
        last,time=ramsey_CORPSE(seq,d,ret_last=True)
        
        seq.add_pulse('wait_for_RO', channel = chan_mw_pm, element = el_name,
            start = 0, duration = 1000., amplitude = 0,
            start_reference=last,link_start_to='end')
    
        seq.add_pulse('ADwin_trigger', channel = chan_ADwintrig, element = el_name,
            start = 0, duration = 5000., amplitude = 1,
            start_reference='wait_for_RO',link_start_to='end')
        seq.add_pulse('wait_for_RO2', channel = chan_mw_pm, element = el_name,
            start = 0, duration = m.weak_RO_duration*1000.+5000, amplitude = 0,
            start_reference='ADwin_trigger',link_start_to='end')
        
        seq_t_array.append(time)
        
        
        # add element for basisrotation
        el_name='basis_rot'+str(i)
        seq.add_element(name = el_name, trigger_wait = False)        

        seq.add_pulse('wait_first', channel = chan_mw_pm, element = el_name,
            start = 0, duration =  1000., amplitude = 0) 
        
        Cdict={}

        Cdict['first']='wait_first'
        Cdict['pulse_name']='CORPSE_basisrot'
        Cdict['theta']=180
        Cdict['el_name']=el_name   
        Cdict['CORPSE_frabi']=m.MWdic_finalmsmnt['CORPSE_frabi'][i]
        Cdict['CORPSE_amp']=m.MWdic_finalmsmnt['CORPSE_amp'][i]
        Cdict['freq']=m.MWdic_finalmsmnt['freq'][i]

        last,Ctime1 = CORPSE_pulse(seq, Cdict,ret_last=True)
    
        seq.add_pulse('wait_first_after_CORPSE', channel = chan_mw_pm, element = el_name,
            start = 0, duration =  1000., amplitude = 0,start_reference=last,link_start_to='end')
        seq.add_pulse('RF_basisrot', channel = chan_RF, element =  el_name,
                start = 0,start_reference='wait_first_after_CORPSE',
                link_start_to='end', duration = m.MWdic_finalmsmnt['RF_basisrot_len'][i],
                amplitude = m.MWdic_finalmsmnt['RF_basisrot_amp'][i],shape='sine',frequency=m.MWdic_finalmsmnt['RF_freq'][i],
                envelope='erf', phase=m.MWdic_finalmsmnt['RO_phase'][i]) 
        
        #add element to wait for SP (1us duration, repeat many times to avoid many datapoints in AWG)
        el_name='wait_for_SP'+str(i)
        seq.add_element(name = el_name, trigger_wait = False,repetitions=ssrocfg['SP_A_duration']+10)
        seq.add_pulse('wait_for_SP', channel = chan_mw_pm, element = el_name,
            start = 0, duration =  1000., amplitude = 0) 
        
        #add element for final msmnt
        el_name = 'final_msmnt_'+str(i)
        if i == m.nr_of_datapoints-1:
            seq.add_element(name = el_name, 
                    trigger_wait = False, goto_target = 'MBI_pulse0')
        else:
            seq.add_element(name = el_name, 
                    trigger_wait = False)        
        
        d={}
        d['el_name']=el_name
        d['do_shelv_pulse']=False
        d['first']=''
        d['pulse_name']='pulse'
        for param_key in m.MWdic_finalmsmnt.keys():
                        if (type(m.MWdic_finalmsmnt[param_key])==np.ndarray):
                            d[param_key]=m.MWdic_finalmsmnt[param_key][i]
                        else:
                            d[param_key]=m.MWdic_finalmsmnt[param_key]      

 
        last,time=ramsey_CORPSE(seq,d,ret_last=True)        

        seq.add_pulse('wait_for_RO', channel = chan_mw_pm, element = el_name,
            start = 0, duration = 1000., amplitude = 0,
            start_reference=last,link_start_to='end')
    
        seq.add_pulse('ADwin_trigger', channel = chan_ADwintrig, element = el_name,
            start = 0, duration = 5000., amplitude = 1,
            start_reference='wait_for_RO',link_start_to='end')
        seq.add_pulse('wait_for_RO2', channel = chan_mw_pm, element = el_name,
            start = 0, duration = ssrocfg['RO_duration']*1000., amplitude = 0,
            start_reference='ADwin_trigger',link_start_to='end')
        
        '''
        seq.add_pulse('wait_for_RO', channel = chan_mw_pm, element = el_name,
            start = 0, duration = 1000, amplitude = 0)
        last='wait_for_RO'
        seq.add_pulse(pulse_name+'I1', channel = chan_mwI, element = el_name,
            start = 0, duration =m.MWdic_finalmsmnt['CORPSE_amp'][i], amplitude = .86,
            start_reference = last, link_start_to = 'end', shape = 'cosine',frequency=m.MBI_mod_freq[i],phase=phase)
        seq.add_pulse(pulse_name+'Q1', channel = chan_mwQ, element = el_name,
            start = 0, duration= m.MWdic_finalmsmnt['CORPSE_amp'][i], amplitude = .86,
            start_reference = last, link_start_to = 'end', shape = 'sine',frequency=m.MBI_mod_freq[i],phase=phase)
        seq.add_pulse(pulse_name+'_mod', channel = chan_mw_pm, element = el_name,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
            start_reference = pulse_name+'I1', link_start_to = 'start', 
            duration_reference = pulse_name+'I1', link_duration_to = 'duration', 
            amplitude = 2.0)
        last=pulse_name+ 'I1'
        time=(1000+m.MWdic_finalmsmnt['CORPSE_amp'][i])/1000.
        '''
        seq_t_array.append(time)


    print seq_t_array
    print max(seq_t_array)
    return max(seq_t_array)

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
        last,shel_time = shelving_pulse(seq, pulse_name = 'shelving_pulse_'+str(i),
                    freq=m.MBI_mod_freq,el_name = el_name,ret_time=True)
        
        seq.add_pulse('wait_before_RF', channel = chan_mwI, element = el_name,
                start = 0,start_reference=last,link_start_to='end', duration = 1000,
                amplitude = 0,shape='rectangular')
        last = 'wait_before_RF'
        seq.add_pulse('RF', channel = chan_RF, element =  el_name,
                start = 0,start_reference=last,link_start_to='end', duration = pulsescfg['RF_pi2_len'],
                amplitude = pulsescfg['RF_pi2_amp'],shape='sine',frequency=m.RF_freq[i],envelope='erf',phase=0)
        seq.add_pulse('wait_before_readout', channel = chan_mwI, element =  el_name,
                start = 0, duration =1000., amplitude = 0, start_reference = 'RF',
                link_start_to = 'end', shape = 'rectangular')
        last='wait_before_readout'
        if m.do_MW_pulse_after_RF:
            seq.add_pulse('MW_pulse_I'+str(i),channel=chan_mwI,element=el_name,start=0,
                           start_reference= last,link_start_to='end',
                           duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                           shape='cosine',frequency=m.RO_mod_freq)
            seq.add_pulse('MW_pulse_Q'+str(i),channel=chan_mwQ,element=el_name,start=0,
                           start_reference= last,link_start_to='end',
                           duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                           shape='sine',frequency=m.RO_mod_freq)
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
                           shape='cosine',frequency=m.RO_mod_freq)
            seq.add_pulse('MW_pulse_Q'+str(i),channel=chan_mwQ,element=el_name,start=0,
                           link_start_to='end', start_reference=last,
                           duration=m.MW_pulse_len[i], amplitude = m.MW_pulse_amp[i],
                           shape='sine',frequency=m.RO_mod_freq)
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
                duration = pulsescfg['RF_pi2_len'],amplitude = 0*pulsescfg['RF_pi2_amp'],
                shape='sine',frequency=m.RF_freq[i],envelope='erf',phase=m.RF_phase[i])
        seq.add_pulse('wait_after_RF', channel = chan_mwI, element = el_name,
                start = 0,start_reference='RF',link_start_to='end', duration = 2000,
                amplitude = 0,shape='rectangular')
        

        '''
        readout_pulse (seq, freq=m.RO_mod_freq,pulse_name = 'readout_pulse_'+str(i),
                first = 'wait_before_readout',el_name = el_name)    
        '''
        el_name='wait_for_SP'+str(i)
        seq.add_element(name=el_name,trigger_wait=False,repetitions=exp.ssroprotocol['SP_A_duration']+5)
        seq.add_pulse('wait_time', channel = chan_mwI, element = el_name,
                start = 0, duration =1000., amplitude = 0, shape = 'rectangular')
        el_name='readout_pulse'+str(i)
        if i == m.nr_of_datapoints-1:
            seq.add_element(name = el_name, trigger_wait = m.RO_element_do_trigger, goto_target = 'MBI_pulse0')
        else:
            seq.add_element(name = el_name, trigger_wait=m.RO_element_do_trigger)

        seq.add_pulse('wait_before_readout', channel = chan_mwI, element = el_name,
                start = 0, duration =1000., amplitude = 0, shape = 'rectangular')    
        last='wait_before_readout'
        d={}
        d['el_name']=el_name
        d['do_shelv_pulse']=False
        d['first']='wait_before_readout'
        d['pulse_name']='RO_ramsey'
        d['tau']=exp.pulses['tau_strong_meas']
        d['phase'] = 90
        d['weak']=0
        d['CORPSE_frabi']=exp.pulses['CORPSE_nsel_frabi']
        d['CORPSE_amp']=exp.pulses['CORPSE_nsel_amp']
        d['freq']=m.RO_mod_freq
        d['finalwait_dur']=10
        last,time = ramsey_CORPSE(seq,d,ret_last=True)
        '''
        seq.add_pulse('MW_pulse_I_2'+str(i),channel=chan_mwI,element=el_name,start=0,
            start_reference= last,link_start_to='end',
            duration=m.RF_phase[i]/2., amplitude = m.MW_pulse_amp[i],
            shape='cosine',frequency=m.MW_mod_freq[i])
        seq.add_pulse('MW_pulse_Q_2'+str(i),channel=chan_mwQ,element=el_name,start=0,
            start_reference= last,link_start_to='end',
            duration=m.RF_phase[i]/2., amplitude = m.MW_pulse_amp[i],
            shape='sine',frequency=m.MW_mod_freq[i])
        seq.add_pulse('MW_pulse_mod_2'+str(i),channel=chan_mw_pm,element=el_name,
            start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
            start_reference='MW_pulse_I_2'+str(i),link_start_to='start',
            duration_reference='MW_pulse_I_2'+str(i),link_duration_to='duration', amplitude=2.0)
        time=max(m.RF_phase)/1000.
        '''
    seq_wait_time = ((2*pulsescfg['RF_pi2_len']+2*max(m.MW_pulse_len))/1000)+7+shel_time+time+m.rep_wait_el

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

### weak measurement sequences

def sweep_meas_strength (m, seq):
   
    
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
    RO_steps_for_dp=m.nr_of_RO_steps
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

         
                j=1
                if (m.do_shelv_pulse == False):
                    seq.add_pulse('wait'+str(j), channel = chan_mw_pm, element = el_name,
                        start = 0, duration = MBIcfg['wait_time_before_MBI_pulse'], amplitude = 0)
                else:
                    seq.add_pulse('wait'+str(j), channel = chan_mw_pm, element = el_name,
                        start = 0, duration = 20, start_reference=last,link_start_to='end',amplitude = 0)
                if (k==RO_steps_for_dp-1):

                    d={}
                    d['el_name']=el_name
                    d['do_shelv_pulse']=m.do_shelv_pulse
                    d['first']=last
                    d['pulse_name']='pulse'
                    seq_t_array=[]
                    
                    if (k==RO_steps_for_dp-1):
                        for param_key in m.MWdic.keys():
                            d[param_key]=m.MWdic[param_key][i]

                    else:
                        for param_key in m.MWdic.keys():
                            d[param_key]=m.MWdic_last[param_key][i]
                    
                    sequence_wait_time=m.load_weakmeas_func(seq,d)
                    seq_t_array.append(sequence_wait_time)
                
                    seq.add_pulse('MW_pulse_I_nsel'+str(j),channel=chan_mwI,element=el_name,start=0,
                        start_reference= 'wait'+str(j),link_start_to='end',
                        duration=m.MW_nsel_pulse_len[i], amplitude = m.MW_nsel_pulse_amp[i],
                        shape='cosine',frequency=m.MW_nsel_mod_freq[i])
                    seq.add_pulse('MW_pulse_Q_nsel'+str(j),channel=chan_mwQ,element=el_name,start=0,
                        start_reference= 'wait'+str(j),link_start_to='end',
                        duration=m.MW_nsel_pulse_len[i], amplitude = m.MW_nsel_pulse_amp[i],
                        shape='sine',frequency=m.MW_nsel_mod_freq[i])
                    seq.add_pulse('MW_pulse_mod_nsel'+str(j),channel=chan_mw_pm,element=el_name,
                        start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
                        start_reference='MW_pulse_I_nsel'+str(j),link_start_to='start',
                        duration_reference='MW_pulse_I_nsel'+str(j),link_duration_to='duration', amplitude=2.0)
                    
                    seq.add_pulse('wait_after_first_MW'+str(j),channel=chan_mwI,element=el_name,start=0,
                        start_reference= 'MW_pulse_I_nsel'+str(j),link_start_to='end',
                        duration=50, amplitude = 0.)
                    
                    seq.add_pulse('MW_pulse_I_sel'+str(j),channel=chan_mwI,element=el_name,start=0,
                        start_reference= 'wait_after_first_MW'+str(j),link_start_to='end',
                        duration=m.MW_sel_pulse_len[i], amplitude = m.MW_sel_pulse_amp[i],
                        shape='cosine',frequency=m.MW_sel_mod_freq[i],phase=m.MW_sel_phase[i])
                    seq.add_pulse('MW_pulse_Q_sel'+str(j),channel=chan_mwQ,element=el_name,start=0,
                        start_reference= 'wait_after_first_MW'+str(j),link_start_to='end',
                        duration=m.MW_sel_pulse_len[i], amplitude = m.MW_sel_pulse_amp[i],
                        shape='sine',frequency=m.MW_sel_mod_freq[i],phase=m.MW_sel_phase[i])
                    seq.add_pulse('MW_pulse_mod_sel'+str(j),channel=chan_mw_pm,element=el_name,
                        start=-MW_pulse_mod_risetime, duration = 2*MW_pulse_mod_risetime,
                        start_reference='MW_pulse_I_sel'+str(j),link_start_to='start',
                        duration_reference='MW_pulse_I_sel'+str(j),link_duration_to='duration', amplitude=2.0)

                    
                    last= 'MW_pulse_I_sel'+str(j)
                else:
                    seq.add_pulse('MW_pulse_I'+str(j),channel=chan_mwI,element=el_name,start=0,
                        start_reference= 'wait'+str(j),link_start_to='end',
                        duration=m.MW1_pulse_len[i], amplitude = m.MW1_pulse_amp[i],
                        shape='cosine',frequency=m.MW1_mod_freq[i])
                    seq.add_pulse('MW_pulse_Q'+str(j),channel=chan_mwQ,element=el_name,start=0,
                        start_reference= 'wait'+str(j),link_start_to='end',
                        duration=m.MW1_pulse_len[i], amplitude = m.MW1_pulse_amp[i],
                        shape='sine',frequency=m.MW1_mod_freq[i])
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
                           m.nr_of_MW_pulses*(m.MW_nsel_pulse_len.max()+m.MW_sel_pulse_len.max()+50)+1000)/1000
  
    return sequence_wait_time


