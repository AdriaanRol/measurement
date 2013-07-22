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
from measurement.lib import ssro_MBI as MBI

meas_name = 'SIL9_lt2_sweep_meas_strength_init+1_RO+1_no_sel'
fdrive=exp.sil9['MW_freq_center']-exp.sil9['MW_source_freq']+exp.sil9['hf_splitting']/2

def sweep_meas_strength (lt1 = False, name = meas_name,nr_of_MW_pulses=1,nr_of_datapoints = 2,
        reps=1500,RO_reps=1,do_shel=False,init_line='-1',RO_line='-1'):
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI.MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    m.nr_of_RO_steps = RO_reps

    print m.nr_of_RO_steps

    strength=np.linspace(0,90,nr_of_datapoints)
    m.do_shelv_pulse = do_shel
    m.do_incr_RO_steps = 0

    m.MBI_mod_freq = MBI.get_freq(m,init_line)*np.ones(nr_of_datapoints)
    m.MW_sel_mod_freq = MBI.get_freq(m,RO_line)*np.ones(nr_of_datapoints)
    m.MW_nsel_mod_freq = (MBI.get_freq(m,RO_line)-exp.sil9['hf_splitting']/2)*np.ones(nr_of_datapoints)

    m.MWdic={} 
    m.MWdic['meas_theta']=strength*np.ones(nr_of_datapoints)
    m.MWdic['CORPSE_nsel_frabi']=exp.pulses['CORPSE_nsel_frabi']*np.ones(nr_of_datapoints)
    m.MWdic['CORPSE_nsel_amp']=exp.pulses['CORPSE_nsel_amp']*np.ones(nr_of_datapoints)
    m.MWdic['CORPSE_freq'] = m.MW_nsel_mod_freq*np.ones(nr_of_datapoints)
    m.MWdic['sel_amp']=exp.pulses['sel_amp']*np.ones(nr_of_datapoints)
    m.MWdic['sel_frabi']=exp.pulses['sel_frabi']*np.ones(nr_of_datapoints)
    m.MWdic['RO_line'] = m.MW_sel_mod_freq*np.ones(nr_of_datapoints)


    print 'init on mI = ', init_line, m.MBI_mod_freq
    print 'pulses on mI = ', RO_line,  m.MWdic['RO_line']
    
    m.par['sweep_par'] = strength/90.
    m.par['sweep_par_name'] = 'measurement strength A.U.'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)
    
    m.load_MWseq_func = MBIseq.add_weak_meas
#    m.start_measurement (m.generate_MW_sweep_sequence)
    m.start_measurement (MBIseq.MW_sweep)
    dp = MBI.get_datapath()
    path = lde_calibration.find_newest_data (dp, string=name)
    spin_control.plot_data_MBI(path)


def Weak_strong_meas(lt1 = False, name = 'SIL9_lt2_RF2',
        min_tau = 1., max_tau = 217., nr_of_pulses=1,nr_of_datapoints = 11, reps=2000,RO_reps=2,
        do_shel=True,CORPSE=True,init_line='minY',MW_line='0-1',RO_rot='X'):

    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    
    m = MBI.MBI(name)
    m.setup (lt1)

    reps_per_datap = reps
    m.nr_of_datapoints = nr_of_datapoints
    m.nr_of_RO_steps = RO_reps
    print m.nr_of_RO_steps
    tau=np.linspace(min_tau,max_tau,nr_of_datapoints)
    #tau=np.insert(tau,0,0)
    #theta = 
    m.do_shelv_pulse = do_shel*np.ones(RO_reps)
    m.do_shelv_pulse[RO_reps-1]=0
    print m.do_shelv_pulse
    postselect_pulse=True
    m.do_incr_RO_steps = 0
    
    m.MBI_mod_freq = MBI.get_freq(m,'-1')*np.ones(nr_of_datapoints)
    if RO_rot=='Z':
        do_rot=0
    else:
        do_rot=1
    if RO_rot=='Y':
        RO_phase=90
    else:
        RO_phase=0

    if init_line =='-1':
        rf1amp=0
        rf1len= m.pulsedic['RF_pi2_len']
        rf1phase=0.
    if init_line=='0':
        rf1amp= m.pulsedic['RF_pi_amp']
        rf1len= m.pulsedic['RF_pi_len']
        rf1phase=0.
    if init_line=='X':
        rf1amp= m.pulsedic['RF_pi2_amp']
        rf1len= m.pulsedic['RF_pi2_len']
        rf1phase=90.
    if init_line=='minX':
        rf1amp= m.pulsedic['RF_pi2_amp']
        rf1len= m.pulsedic['RF_pi2_len']
        rf1phase=270. 
    if init_line=='minY':
        rf1amp= m.pulsedic['RF_pi2_amp']
        rf1len= m.pulsedic['RF_pi2_len']
        rf1phase=0.
    if init_line=='Y':
        rf1amp= m.pulsedic['RF_pi2_amp']
        rf1len= m.pulsedic['RF_pi2_len']
        rf1phase=180.

    # first pi/2 pulse
    m.MWdic_last={}
    m.MWdic={}
    m.MWdic_last['nr_of_MW_pulses'] = 1*np.ones(nr_of_datapoints)
    m.MWdic_last['MW_pulse_amp'] = m.pulsedic['pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic_last['MW_pulse_len'] = m.pulsedic['pi2_len']*np.ones(nr_of_datapoints)
    m.MWdic_last['tau'] = tau#(1.)*np.ones(nr_of_datapoints)
    m.MWdic_last['weak']=True*np.ones(nr_of_datapoints)
    m.MWdic_last['phase']=90.*np.ones(nr_of_datapoints)
    m.MWdic_last['finalwait_dur']=2000.*np.ones(nr_of_datapoints) #MBIcfg['wait_time_before_MBI_pulse']
    m.MWdic_last['MW_mod_freq'] = MBI.get_freq(m,MW_line)*np.ones(nr_of_datapoints)  

    #RF
    m.MWdic_last['RF_pulse_amp'] = rf1amp*np.ones(nr_of_datapoints)
    m.MWdic_last['RF_pulse_len'] = rf1len*np.ones(nr_of_datapoints)
    m.MWdic_last['RF_phase'] = rf1phase*np.ones(nr_of_datapoints)
    m.MWdic_last['RF_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    m.MWdic['RF_pulse_amp'] = 0*np.ones(nr_of_datapoints)
    m.MWdic['RF_pulse_len'] = 0*np.ones(nr_of_datapoints)
    m.MWdic['RF_freq'] = 0*exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    m.MWdic['RF_phase'] = 0*np.ones(nr_of_datapoints)
    #m.MWdic_last['final_shelving']=True*np.ones(nr_of_datapoints)

    #m.pulsedic['RF_pi2_len'] = basisrot
    # second RF (basis rot)
    m.MWdic_last['RF2_pulse_amp'] = do_rot*m.pulsedic['RF_pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic_last['RF2_pulse_len'] = m.pulsedic['RF_pi2_len']*np.ones(nr_of_datapoints)
    m.MWdic_last['RF2_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    m.MWdic_last['RF2_phase'] =RO_phase+102.-tau*180*exp.sil9['hf_splitting']*1e-9 #NOTE 1 -> tau and RO_phase!!!
    #m.MWdic_last['RF2_phase'] =((101+180)-15*180*exp.sil9['hf_splitting']*1e-9)*np.ones(nr_of_datapoints)
    # third RF (other basis rot)
    
    m.MWdic_last['RF3_pulse_amp'] = do_rot*m.pulsedic['RF_pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic_last['RF3_pulse_len'] = m.pulsedic['RF_pi2_len']*np.ones(nr_of_datapoints)#basisrot
    m.MWdic_last['RF3_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    m.MWdic_last['RF3_phase'] = RO_phase+17.-tau*180*exp.sil9['hf_splitting']*1e-9##NOTE 1 -> tau and RO_phase!!!
    
    # Second pi/2 pulse
    m.MWdic['nr_of_MW_pulses'] = 1*np.ones(nr_of_datapoints)
    m.MWdic['MW_pulse_amp'] = m.pulsedic['pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic['MW_pulse_len'] = m.pulsedic['pi2_len']*np.ones(nr_of_datapoints)
    m.MWdic['tau'] = 217*np.ones(nr_of_datapoints)
    m.MWdic['phase']=90.*np.ones(nr_of_datapoints)
    m.MWdic['finalwait_dur']=2000.*np.ones(nr_of_datapoints) #MBIcfg['wait_time_before_MBI_pulse']
    m.MWdic['MW_mod_freq'] = MBI.get_freq(m,MW_line)*np.ones(nr_of_datapoints)  
    m.MBI_mod_freq = MBI.get_freq(m,'-1')*np.ones(nr_of_datapoints)

    # in case of CORPSE pulses
    m.MWdic['CORPSE_amp'] = m.pulsedic['CORPSE_nsel_amp']*np.ones(nr_of_datapoints)
    m.MWdic['CORPSE_frabi']=m.pulsedic['CORPSE_nsel_frabi']*np.ones(nr_of_datapoints)
    m.MWdic_last['CORPSE_amp']= m.MWdic['CORPSE_amp']
    m.MWdic_last['CORPSE_frabi'] =  m.MWdic['CORPSE_frabi']
    m.MWdic['freq']=m.MWdic_last['MW_mod_freq']
    m.MWdic_last['freq']=m.MWdic['freq']
    #set laser powers
    m.Ex_final_RO_amplitude = m.ssrodic['Ex_RO_amplitude']
    m.A_final_RO_amplitude = 0.
    m.Ex_RO_amplitude = m.ssrodic['Ex_RO_amplitude']
    m.A_RO_amplitude = 0.
    m.RO_duration = m.MBIdic['weak_RO_duration']
    m.final_RO_duration = m.ssrodic['RO_duration']

    print 'init on mI = ', '-1', m.MBI_mod_freq
    print 'RO on mI = ', MW_line, m.MWdic['MW_mod_freq']
    
    m.par['sweep_par'] = tau
    m.par['sweep_par_name'] = 'tau (ns)'
    m.par['RO_repetitions'] = int(len(m.par['sweep_par'])*reps_per_datap)
    
    #STRONG READOUT!!!!
    # second RF (basis rot)
    m.MWdic['RF2_pulse_amp'] = 0*m.pulsedic['RF_pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic['RF2_pulse_len'] = 0*m.pulsedic['RF_pi2_len']*np.ones(nr_of_datapoints)
    m.MWdic['RF2_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    m.MWdic['RF2_phase'] = np.ones(nr_of_datapoints)
    # third RF (other basis rot)
    #If RF3 is commented out: no pi pulses after strong readout
    #m.MWdic['RF3_pulse_amp'] = 0*m.pulsedic['RF_pi2_amp']*np.ones(nr_of_datapoints)
    m.MWdic['RF3_pulse_len'] = m.pulsedic['RF_pi2_len']*np.ones(nr_of_datapoints)
    m.MWdic['RF3_freq'] = exp.sil9['mI_m1_freq']*np.ones(nr_of_datapoints)
    m.MWdic['RF3_phase'] = np.ones(nr_of_datapoints)

    if CORPSE:
        m.load_MWseq_func=MBIseq.ramsey_CORPSE
        m.load_MWseq_func_last=MBIseq.ramsey_CORPSE

#if postselect_pulse:
#            m.load_MWseq_func_last=MBIseq.MBI_element
    else:    
        m.load_MWseq_func=MBIseq.ramsey
        m.load_MWseq_func_last=MBIseq.ramsey
    m.start_measurement (MBIseq.MW_sweep)
    #dp = MBI.get_datapath()
    #path = lde_calibration.find_newest_data (dp, string=name)
    #spin_control.plot_data_MBI(path)

#p1=np.linspace(0,300,6)
#p2=np.linspace(0,300,6)


#coeffA = np.array ([-1, -0.5, 0., 0.5, 1])

#coeffA = np.array ([1000,1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500])

#for n in coeffA:
#    print '##########################'
#    print n
#    nome = 'SIL9_lt2_phaseRF2_lenRF1='+str(n)+'ns'
#    Weak_strong_meas(name = nome, lenRF = n)

def optimize():
    NewfocusAOM.set_power(0e-9)
    MatisseAOM.set_power(0e-9)
    GreenAOM.set_power(20e-6)
    qt.msleep(5)
    optimiz0r.optimize(cnt=1,cycles=2,int_time=30)
    qt.msleep(5)


Weak_strong_meas (name='SIL9_lt2_rotY_weak3us_initminy',reps=10000,RO_rot='Y',init_line='minY')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotX_weak3us_initminy',reps=10000,RO_rot='X',init_line='minY')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotZ_weak3us_initminy',reps=10000,RO_rot='Z',init_line='minY')
optimize()
ssro.ssro_ADwin_Cal(reps=10000,Ex_p=30e-9,sweep_power=False,lt1=False, phase_lock = 0,name='ADwin_SSRO')
Weak_strong_meas (name='SIL9_lt2_rotY_weak3us_initmImin1',reps=10000,RO_rot='Y',init_line='-1')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotX_weak3us_initmImin1',reps=10000,RO_rot='X',init_line='-1')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotZ_weak3us_initmImin1',reps=10000,RO_rot='Z',init_line='-1')

ssro.ssro_ADwin_Cal(reps=10000,Ex_p=30e-9,sweep_power=False,lt1=False, phase_lock = 0,name='ADwin_SSRO')

Weak_strong_meas (name='SIL9_lt2_rotY_weak3us_initmI0',reps=10000,RO_rot='Y',init_line='0')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotX_weak3us_initmI0',reps=10000,RO_rot='X',init_line='0')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotZ_weak3us_initmI0',reps=10000,RO_rot='Z',init_line='0')
ssro.ssro_ADwin_Cal(reps=10000,Ex_p=30e-9,sweep_power=False,lt1=False, phase_lock = 0,name='ADwin_SSRO')
optimize()

Weak_strong_meas (name='SIL9_lt2_rotY_weak3us_initX',reps=10000,RO_rot='Y',init_line='X')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotX_weak3us_initX',reps=10000,RO_rot='X',init_line='X')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotZ_weak3us_initX',reps=10000,RO_rot='Z',init_line='X')
ssro.ssro_ADwin_Cal(reps=10000,Ex_p=30e-9,sweep_power=False,lt1=False, phase_lock = 0,name='ADwin_SSRO')
optimize()

Weak_strong_meas (name='SIL9_lt2_rotY_weak3us_initminX',reps=10000,RO_rot='Y',init_line='minX')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotX_weak3us_initminX',reps=10000,RO_rot='X',init_line='minX')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotZ_weak3us_initminX',reps=10000,RO_rot='Z',init_line='minX')
ssro.ssro_ADwin_Cal(reps=10000,Ex_p=30e-9,sweep_power=False,lt1=False, phase_lock = 0,name='ADwin_SSRO')
optimize()

Weak_strong_meas (name='SIL9_lt2_rotY_weak3us_initY',reps=10000,RO_rot='Y',init_line='Y')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotX_weak3us_initY',reps=10000,RO_rot='X',init_line='Y')
optimize()
Weak_strong_meas (name='SIL9_lt2_rotZ_weak3us_initY',reps=10000,RO_rot='Z',init_line='Y')
ssro.ssro_ADwin_Cal(reps=10000,Ex_p=30e-9,sweep_power=False,lt1=False, phase_lock = 0,name='ADwin_SSRO')
optimize()

'''
for i in np.arange(6):
    phase1 = p1[i]
    for j in np.arange(6):
        phase2=p2[j]
        n='p1_'+str(phase1)+'_p2_'+str(phase2)
        Weak_strong_meas(lt1 = False, name = 'SIL9_lt2_ws_meas_basisroty'+n, min_tau = 1., max_tau = 214., 
        nr_of_pulses=1,nr_of_datapoints = 11, reps=750,RO_reps=2,do_shel=True,CORPSE=True,init_line='-1',
        MW_line='0-1',phase1=phase1,phase2=phase2)
'''
   


