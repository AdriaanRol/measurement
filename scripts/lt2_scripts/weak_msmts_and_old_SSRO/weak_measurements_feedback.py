import qt
import numpy as np
import ctypes
import inspect
import time as dtime
import msvcrt
import math
from measurement.lib.measurement import Measurement 
from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels_lt2 as awgcfg
from measurement.lib.sequence import common as commonseq
from analysis.lib.spin import pulse_calibration_fitandplot_lib as lde_calibration
from analysis.lib.spin import spin_control
from measurement.lib.config import experiment_lt2 as exp
from measurement.lib.sequence import MBI_seq as MBIseq
from measurement.lib import ssro_MBI_feedback as MBIfb

def theta_to_tau(theta):
    tau = (217)*theta/(np.pi/2.)
    return tau
def tau_to_theta(tau):
    theta = (np.pi/2.)*(tau+12.)/229. 
    return theta

def angle_rot_back(theta):
    theta=theta/2.
    phi=0.5*np.arcsin((2*np.sin(2*theta))/(1+np.sin(2*theta)**2))
    return phi*2

def WM_feedback(lt1 = False, name = 'SIL9_lt2_undo_msmnt_tau50ns_postselected_RO2us_phase',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,sweep_phase=False,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 7, reps=3000):

    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBIfb.MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    
    par=np.linspace(min_par,max_par,nr_of_datapoints)
    
    m.MBI_mod_freq = MBIfb.get_freq(m,'-1')*np.ones(nr_of_datapoints)
    m.weak_RO_duration=weak_RO_duration
    MW_line='0-1'

    if sweep_phase:
        RO_phase=par
        RO_amp=1
        tau_first = tau*np.ones(nr_of_datapoints)
        par_name='phase (degree)'
    else:
        RO_phase=0*np.ones(nr_of_datapoints)
        RO_amp=0
        tau_first = par
        par_name='tau(ns)'
    if undo_msmnt:
        tau_second = tau_first
    else:    
        tau_second = theta_to_tau(angle_rot_back(tau_to_theta(tau_first)))
        

    #tau_second = tau_first
    tau_final=217.*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt={}
    m.MWdic_secondmsmnt={}
    m.MWdic_finalmsmnt={}

    # Settings of first msmnt
    #RF for initial state
    m.MWdic_firstmsmnt['RF_pulse_amp'] = m.pulsedic['RF_pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['RF_pulse_len'] = m.pulsedic['RF_pi2_len']*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['RF_phase'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['RF_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    #(first) weak measurement properties
    m.MWdic_firstmsmnt['CORPSE_amp'] = m.pulsedic['CORPSE_nsel_amp']*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['CORPSE_frabi']=m.pulsedic['CORPSE_nsel_frabi']*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['nr_of_MW_pulses'] = 1*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['tau'] = tau_first
    m.MWdic_firstmsmnt['weak']=True*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['phase']=270.*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['finalwait_dur']=2000.*np.ones(nr_of_datapoints) 
    m.MWdic_firstmsmnt['MW_mod_freq'] = MBIfb.get_freq(m,MW_line)*np.ones(nr_of_datapoints)
    m.MWdic_firstmsmnt['freq'] = MBIfb.get_freq(m,MW_line)*np.ones(nr_of_datapoints) 


    # Settings of second msmnt
    # No RF for second
    m.MWdic_secondmsmnt['RF_pulse_amp'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF_pulse_len'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF_phase'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    #(second) weak measurement properties
    m.MWdic_secondmsmnt['CORPSE_amp'] = m.pulsedic['CORPSE_nsel_amp']*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['CORPSE_frabi']=m.pulsedic['CORPSE_nsel_frabi']*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['nr_of_MW_pulses'] = 1*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['tau'] = tau_second
    m.MWdic_secondmsmnt['weak']=True*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['phase']=270.*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['finalwait_dur']=2000.*np.ones(nr_of_datapoints) 
    m.MWdic_secondmsmnt['MW_mod_freq'] = MBIfb.get_freq(m,MW_line)*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['freq'] = MBIfb.get_freq(m,MW_line)*np.ones(nr_of_datapoints) 

    #RF after
    #m.MWdic_secondmsmnt['RF2_pulse_amp'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF2_pulse_len'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF2_phase'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF2_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    #m.MWdic_secondmsmnt['RF3_pulse_amp'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF3_pulse_len'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF3_phase'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_secondmsmnt['RF3_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)


   # Settings of final msmnt
    #RF for initial state
    m.MWdic_finalmsmnt['RF_basisrot_amp'] = RO_amp*m.pulsedic['RF_pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['RF_basisrot_len'] = m.pulsedic['RF_pi2_len']*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['RO_phase'] = RO_phase#exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['RF_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)

    #if you want RF right before the two CORPSE (probabily not):
    m.MWdic_finalmsmnt['RF_pulse_amp'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['RF_pulse_len'] = 0*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['RF_phase'] = 0*np.ones(nr_of_datapoints)
      
    #(final) weak measurement properties
    m.MWdic_finalmsmnt['CORPSE_amp'] =m.pulsedic['CORPSE_nsel_amp']*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['CORPSE_frabi']=m.pulsedic['CORPSE_nsel_frabi']*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['nr_of_MW_pulses'] = 1*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['tau'] = tau_final#(1.)*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['weak']=True*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['phase']=90.*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['finalwait_dur']=2000.*np.ones(nr_of_datapoints) #MBIcfg['wait_time_before_MBI_pulse']
    m.MWdic_finalmsmnt['MW_mod_freq'] = MBIfb.get_freq(m,MW_line)*np.ones(nr_of_datapoints)
    m.MWdic_finalmsmnt['freq'] = MBIfb.get_freq(m,MW_line)*np.ones(nr_of_datapoints)


    #set laser powers
    m.Ex_final_RO_amplitude = m.ssrodic['Ex_RO_amplitude']
    m.A_final_RO_amplitude = 0.
    m.Ex_RO_amplitude =5e-9# m.ssrodic['Ex_RO_amplitude']
    m.A_RO_amplitude = 0.
    m.RO_duration =weak_RO_duration# m.MBIdic['weak_RO_duration']
    m.final_RO_duration = m.ssrodic['RO_duration']
    
    m.par['sweep_par'] = par
    m.par['sweep_par_name'] = par_name
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)
    

    m.start_measurement (MBIseq.WM_feedback)
    #dp = MBIfb.get_datapath()
    #path = lde_calibration.find_newest_data (dp, string=name)
    #spin_control.plot_data_MBI(path)





def optimize():
    NewfocusAOM.set_power(0e-9)
    MatisseAOM.set_power(0e-9)
    GreenAOM.set_power(20e-6)
    qt.msleep(5)
    optimiz0r.optimize(cnt=1,cycles=2,int_time=30)
    qt.msleep(5)




#for n in [4, 6, 8, 10, 15, 25, 35, 50, 75, 100]:
'''
for n in [50]:

    fname = 'SIL10_lt2_feedback_sweep_phase_ROdur='+str(n)+'us_segmRO'
    WM_feedback(lt1 = False, name = fname,
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=n,
        sweep_phase=True,undo_msmnt=False,par_name='tau (ns)',
        nr_of_datapoints = 11, reps=1000)

    print n
'''
for n in [25, 35, 50, 75, 100]:   
    fname = 'SIL10_lt2_feedback_Z_ROdur='+str(n)+'us_segmRO_SN=noClick'
    WM_feedback(lt1 = False, name = fname,
        min_par = 1, max_par = 50,tau=50,weak_RO_duration=n,
        sweep_phase=False,undo_msmnt=False,par_name='tau (ns)',
        nr_of_datapoints = 2, reps=5000)



'''
#[4, 6, 8, 10, 15, 25, 35, 50, 75, 100]
for n in [75, 100]:   
    fname = 'SIL10_lt2_feedback_phase_ROdur='+str(n)+'us_segmRO_SN=noClick'
    WM_feedback(lt1 = False, name = fname,
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=n,
        sweep_phase=True,undo_msmnt=False,par_name='phase (deg)',
        nr_of_datapoints = 11, reps=1000)
'''
'''
WM_feedback(lt1 = False, name = 'SIL10_lt2_feedback_sweep_phase_ROdur=100us_segmRO',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=100,
        sweep_phase=True,undo_msmnt=False,par_name='tau (ns)',
        nr_of_datapoints = 11, reps=1000)




WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt',
        min_par = 50, max_par = 50.001,tau=50,weak_RO_duration=2,
        sweep_phase=False,undo_msmnt=True,par_name='tau (ns)',
        nr_of_datapoints = 2, reps=25000)
optimize()

WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_1',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)
optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_2',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)


optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_3',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)
optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_4',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)
optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_5',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)
optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_6',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)
optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_7',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)
optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_phase_8',
        min_par = 1, max_par = 360,tau=50,weak_RO_duration=2,
        sweep_phase=True,undo_msmnt=True,par_name='phase (degree)',
        nr_of_datapoints = 11, reps=10000)
optimize()
WM_feedback (lt1 = False, name = 'SIL9_lt2_RO2us_5nW_tau1=50ns_ROafterclick_lookatfirstmsmnt_2',
        min_par = 50, max_par = 50.001,tau=50,weak_RO_duration=2,
        sweep_phase=False,undo_msmnt=True,par_name='tau (ns)',
        nr_of_datapoints = 2, reps=25000)
'''