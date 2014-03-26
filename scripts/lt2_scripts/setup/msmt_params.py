#import types
#import qt

cfg={}

cfg['samples'] = {'current':'Hans_sil1'}
cfg['protocols'] = {'current':'Hans_sil1'}

cfg['protocols']['Hans_sil1'] = {}
cfg['protocols']['Hans_sil4'] = {}

print 'updating msmt params lt2 for {}'.format(cfg['samples']['current'])

###################################
### General settings for magnet ###
###################################
#Asummes a cylindrical magnet
cfg['magnet']={

'nm_per_step'       :   1.,     #Z-movement     
'radius'            :   5.,     #millimeters
'thickness'         :   4.,     #millimeters
'strength_constant' :   1.3}    #Tesla

##############################################################################
##############################################################################
### General Settings for Protocols
##############################################################################
##############################################################################

    ######################################
    ### General settings for AdwinSSRO ###
    ######################################

cfg['protocols']['AdwinSSRO']={
'AWG_done_DI_channel'       :       16,
'AWG_event_jump_DO_channel' :       6,
'AWG_start_DO_channel'      :       1,
'counter_channel'           :       1,
'cycle_duration'            :       300,
'green_off_amplitude'       :       0.0,
'green_repump_amplitude'    :       200e-6,
'green_repump_duration'     :       15,
'send_AWG_start'            :       0,
'sequence_wait_time'        :       1,
'wait_after_RO_pulse_duration':     3,
'wait_after_pulse_duration' :       3,
'cr_wait_after_pulse_duration':     2,
'wait_for_AWG_done'         :       0,
'green_off_voltage'         :       0,
'Ex_off_voltage'            :       0.,
'A_off_voltage'             :       -0.0,
'repump_off_voltage'        :       0,
'yellow_repump_amplitude'   :       50e-9,
'yellow_repump_duration'    :       500,
'yellow_CR_repump'          :       1,
'green_CR_repump'           :       1000,
'CR_probe_max_time'         :       1000000}

yellow=False
cfg['protocols']['AdwinSSRO']['yellow'] = yellow
if yellow:
    cfg['protocols']['AdwinSSRO']['repump_duration']  =  cfg['protocols']['AdwinSSRO']['yellow_repump_duration']
    cfg['protocols']['AdwinSSRO']['repump_amplitude'] =  cfg['protocols']['AdwinSSRO']['yellow_repump_amplitude']
    cfg['protocols']['AdwinSSRO']['CR_repump']        =  cfg['protocols']['AdwinSSRO']['yellow_CR_repump']
else:
    cfg['protocols']['AdwinSSRO']['repump_duration']  =  cfg['protocols']['AdwinSSRO']['green_repump_duration']
    cfg['protocols']['AdwinSSRO']['repump_amplitude'] =  cfg['protocols']['AdwinSSRO']['green_repump_amplitude']
    cfg['protocols']['AdwinSSRO']['CR_repump']        =  cfg['protocols']['AdwinSSRO']['green_CR_repump']

    ############################################
    ### General settings for AdwinSSRO+espin ###
    ############################################

cfg['protocols']['AdwinSSRO+espin'] = {
'send_AWG_start'        :     1,
'MW_pulse_mod_risetime' :     10e-9}

    ##########################################
    ### General settings for AdwinSSRO+MBI ###
    ##########################################

### General settings for AdwinSSRO+MBI
cfg['protocols']['AdwinSSRO+MBI'] = {
'send_AWG_start'                        :    1,
'AWG_wait_duration_before_MBI_MW_pulse' :    1e-6,
'AWG_wait_for_adwin_MBI_duration'       :    15e-6,
'AWG_wait_duration_before_shelving_pulse':   100e-9,
'nr_of_ROsequences'                     :    1,
'MW_pulse_mod_risetime'                 :    10e-9,
'AWG_to_adwin_ttl_trigger_duration'     :    5e-6,
'max_MBI_attempts'                      :    1,
'N_randomize_duration'                  :    50,
'Ex_N_randomize_amplitude'              :    20e-9,
'A_N_randomize_amplitude'               :    20e-9,
'repump_N_randomize_amplitude'          :    20e-9}





#################
### Hans sil1 ###
#################

    ###############################
    ### NV and field parameters ###
    ###############################



f_msm1_cntr = 2.014001e9            #Electron spin ms=-1 frquency
f_msp1_cntr = 3.741205e9            #Electron spin ms=+1 frequency

mw_freq  = 3.65e9    #MW source frequency
mw_power = 23        #MW power

zero_field_splitting = 2.87747e9    # As measured by Julia on 20140227 2.87747(5)e9

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.195e6        #calibrated 20140320/181319

cfg['samples']['Hans_sil1'] = {
'mw_frq'        :       mw_freq, 
'mw_power'      :       mw_power,
'ms-1_cntr_frq' :       f_msm1_cntr,
'ms+1_cntr_frq' :       f_msp1_cntr,
'zero_field_splitting': zero_field_splitting,
'g_factor'      :       2.8e6, #2.8 MHz/Gauss
'N_0-1_splitting_ms-1': N_frq,
'N_HF_frq'      :       N_HF_frq}

    #######################
    ### SSRO parameters ###
    #######################

cfg['protocols']['Hans_sil1']['AdwinSSRO'] = {
'SSRO_repetitions'  : 5000,
'SSRO_duration'     :  50,
'SSRO_stop_after_first_photon' : 0,
'A_CR_amplitude': 3e-9,
'A_RO_amplitude': 0,
'A_SP_amplitude': 3e-9,
'CR_duration' :  50,
'CR_preselect':  1000,
'CR_probe':      1000,
'CR_repump':     1000,
'Ex_CR_amplitude':  5e-9,
'Ex_RO_amplitude':  25e-9,
'Ex_SP_amplitude':  0e-9,
'SP_duration'        : 100,
'SP_filter_duration' : 0 }


    ##################################
    ### Integrated SSRO parameters ###
    ##################################

cfg['protocols']['Hans_sil1']['AdwinSSRO-integrated'] = {
'SSRO_duration' : 10}

    ########################
    ### Pulse parameters ###
    ########################

#f_0 = cfg['samples']['Hans_sil1']['ms-1_cntr_frq'] - cfg.get['samples']['Hans_sil1']['mw_frq']
f_mod_0     = cfg['samples']['Hans_sil1']['ms+1_cntr_frq'] - cfg['samples']['Hans_sil1']['mw_frq']
N_hf_split  = cfg['samples']['Hans_sil1']['N_HF_frq']
f_MBI = f_mod_0 - N_hf_split

cfg['protocols']['Hans_sil1']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'X_phase'                   :   90,
'Y_phase'                   :   0,

    ### Pi pulses, hard ###
'fast_pi_duration'          :   110e-9,
'fast_pi_amp'               :   0.857767, #140324
'fast_pi_mod_frq'           :   f_MBI,

    ### Pi/2 pulses, hard ###
'fast_pi2_duration'         :   60e-9,
'fast_pi2_amp'              :   0.777847, #140324
'fast_pi2_mod_frq'          :   f_MBI,

    ### MBI pulses ###
'AWG_MBI_MW_pulse_mod_frq'  :   f_MBI,
'AWG_MBI_MW_pulse_ssbmod_frq':  f_MBI,
'AWG_MBI_MW_pulse_amp'      :   0.03,
'AWG_MBI_MW_pulse_duration' :   2500e-9}
   
#    ### Corpse pulses ###
# cfg.set(branch+'CORPSE_pi2_amp',0.4)
# CORPSE_frq = 8.15e6
# cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

# cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
    
    ###########    
    ### MBI ###
    ###########

cfg['protocols']['Hans_sil1']['AdwinSSRO+MBI'] ={
    
    #Spin pump before MBI
'Ex_SP_amplitude'           :           10e-9,
'SP_E_duration'             :           300,

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           5e-9,
'MBI_duration'              :           4,

    #Repump after succesfull MBI
'repump_after_MBI_duration' :           300,
'repump_after_MBI_A_amplitude':         [15e-9],
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI paramters
'max_MBI_attempts'          :           100,
'MBI_threshold'             :           1,
'AWG_wait_duration_before_MBI_MW_pulse':50e-9,
'AWG_wait_for_adwin_MBI_duration':      15e-6,

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          15e-9}

    





#################
### Hans sil4 ###
#################

    ###############################
    ### NV and field parameters ###
    ###############################

f_msm1_cntr = 2.014001e9            #Electron spin ms=-1 frquency
f_msp1_cntr = 3.741205e9            #Electron spin ms=+1 frequency

mw_freq  = 3.65e9    #MW source frequency
mw_power = 23        #MW power

zero_field_splitting = 2.87747e9    # As measured by Julia on 20140227 2.87747(5)e9

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.195e6        #calibrated 20140320/181319

cfg['samples']['Hans_sil4'] = {
'mw_frq'        :       mw_freq, 
'mw_power'      :       mw_power,
'ms-1_cntr_frq' :       f_msm1_cntr,
'ms+1_cntr_frq' :       f_msp1_cntr,
'zero_field_splitting': zero_field_splitting,
'g_factor'      :       2.8e6, #2.8 MHz/Gauss
'N_0-1_splitting_ms-1': N_frq,
'N_HF_frq'      :       N_HF_frq}

    #######################
    ### SSRO parameters ###
    #######################

cfg['protocols']['Hans_sil4']['AdwinSSRO'] = {
'SSRO_repetitions'  : 5000,
'SSRO_duration'     :  50,
'SSRO_stop_after_first_photon' : 0,
'A_CR_amplitude': 3e-9,
'A_RO_amplitude': 0,
'A_SP_amplitude': 3e-9,
'CR_duration' :  50,
'CR_preselect':  1000,
'CR_probe':      1000,
'CR_repump':     1000,
'Ex_CR_amplitude':  5e-9,
'Ex_RO_amplitude':  25e-9,
'Ex_SP_amplitude':  0e-9,
'SP_duration'        : 100,
'SP_filter_duration' : 0 }


    ##################################
    ### Integrated SSRO parameters ###
    ##################################

cfg['protocols']['Hans_sil4']['AdwinSSRO-integrated'] = {
'SSRO_duration' : 10}

    ########################
    ### Pulse parameters ###
    ########################

#f_0 = cfg['samples']['Hans_sil4']['ms-1_cntr_frq'] - cfg.get['samples']['Hans_sil4']['mw_frq']
f_mod_0     = cfg['samples']['Hans_sil4']['ms+1_cntr_frq'] - cfg['samples']['Hans_sil4']['mw_frq']
N_hf_split  = cfg['samples']['Hans_sil4']['N_HF_frq']
f_MBI = f_mod_0 - N_hf_split

cfg['protocols']['Hans_sil4']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'X_phase'                   :   90,
'Y_phase'                   :   0,

    ### Pi pulses, hard ###
'fast_pi_duration'          :   110e-9,
'fast_pi_amp'               :   0.857767, #140324
'fast_pi_mod_frq'           :   f_MBI,

    ### Pi/2 pulses, hard ###
'fast_pi2_duration'         :   60e-9,
'fast_pi2_amp'              :   0.777847, #140324
'fast_pi2_mod_frq'          :   f_MBI,

    ### MBI pulses ###
'AWG_MBI_MW_pulse_mod_frq'  :   f_MBI,
'AWG_MBI_MW_pulse_ssbmod_frq':  f_MBI,
'AWG_MBI_MW_pulse_amp'      :   0.03,
'AWG_MBI_MW_pulse_duration' :   2500e-9}
   
#    ### Corpse pulses ###
# cfg.set(branch+'CORPSE_pi2_amp',0.4)
# CORPSE_frq = 8.15e6
# cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

# cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
    
    ###########    
    ### MBI ###
    ###########

cfg['protocols']['Hans_sil4']['AdwinSSRO+MBI'] ={
    
    #Spin pump before MBI
'Ex_SP_amplitude'           :           10e-9,
'SP_E_duration'             :           300,

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           5e-9,
'MBI_duration'              :           4,

    #Repump after succesfull MBI
'repump_after_MBI_duration' :           300,
'repump_after_MBI_A_amplitude':         [15e-9],
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI paramters
'max_MBI_attempts'          :           100,
'MBI_threshold'             :           1,
'AWG_wait_duration_before_MBI_MW_pulse':50e-9,
'AWG_wait_for_adwin_MBI_duration':      15e-6,

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          15e-9}
############################
### END: save everything ###
############################




































#################
### Hans sil4 ###
#################

# branch='samples/Hans_sil4/'

# f_msm1_cntr = 1.99074e9#2.000052e9#1.642e9
# f_msp1_cntr = 3.7641e9#3.7541e9#4.218e9    #calibrated
# N_frq = 7.13429e6           #not calibrated
# N_HF_frq = 2.16042e6

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)

# branch='protocols/Hans_sil4-default/AdwinSSRO/'

# cfg.set(branch+'A_CR_amplitude', 40e-9)
# cfg.set(branch+'A_RO_amplitude' , 0)
# cfg.set(branch+'A_SP_amplitude', 63e-9)#70e-9)
# cfg.set(branch+'CR_duration' , 100)
# cfg.set(branch+'CR_preselect', 100)
# cfg.set(branch+'CR_probe', 100)
# cfg.set(branch+'CR_repump', 1000)
# cfg.set(branch+'Ex_CR_amplitude', 20e-9) #10e-9
# cfg.set(branch+'Ex_RO_amplitude', 20e-9) #10e-9
# cfg.set(branch+'Ex_SP_amplitude', 0e-9)
# cfg.set(branch+'SP_duration', 150) #300
# cfg.set(branch+'SP_filter_duration', 0)
# cfg.set(branch+'SSRO_duration', 168) #93
# cfg.set(branch+'SSRO_repetitions', 5000)
# cfg.set(branch+'SSRO_stop_after_first_photon', 0)
# cfg.set(branch+'mw_frq',2.2e9) #Probably Redundant, better to read out from AWG
# cfg.set(branch+'mw_power',20)
# cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

# branch='protocols/Hans_sil4-default/AdwinSSRO-integrated/'
# cfg.set(branch+'SSRO_duration', 117)

#     #Pulses, not yet calibrated.
# branch='protocols/Hans_sil4-default/pulses/'
# f0 = cfg['samples']['Hans_sil4']['ms-1_cntr_frq'] - cfg['protocols']['Hans_sil4-default']['AdwinSSRO']['mw_frq']
# cfg.set(branch+'MW_modulation_frequency', f0)
# cfg.set(branch+'Pi_pulse_duration', 80e-9)#40e-9)
# cfg.set(branch+'Pi_pulse_amp',  0.530)#0.6296)

# #Lines added to implement different phase pulses in decoupling sequence
# cfg.set(branch+'X_phase',  90)
# cfg.set(branch+'Y_phase',  0)

# #cfg.set(branch+'CORPSE_pi2_amp',0.4)
# #CORPSE_frq = 8.15e6
# #cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
# #cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
# #cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

# #cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
# #cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
# #cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)

##############
### sil 10 ###
##############

# branch='samples/sil10/'

# f_msm1_cntr = 2.828855e9
# f_msp1_cntr = 2.925884e9    #not calibrated
# N_frq = 7.13429e6           #not calibrated
# N_HF_frq = 2.16042e6

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)

# branch='protocols/sil10-default/AdwinSSRO/'

# cfg.set(branch+'A_CR_amplitude', 40e-9)
# cfg.set(branch+'A_RO_amplitude' , 0)
# cfg.set(branch+'A_SP_amplitude', 40e-9)
# cfg.set(branch+'CR_duration' , 50)
# cfg.set(branch+'CR_preselect', 15)
# cfg.set(branch+'CR_probe', 2)
# cfg.set(branch+'CR_repump', 1000)
# cfg.set(branch+'Ex_CR_amplitude', 6e-9)
# cfg.set(branch+'Ex_RO_amplitude', 8e-9)
# cfg.set(branch+'Ex_SP_amplitude', 0e-9)
# cfg.set(branch+'SP_duration', 250)
# cfg.set(branch+'SP_filter_duration', 0)
# cfg.set(branch+'SSRO_duration', 50)
# cfg.set(branch+'SSRO_repetitions', 5000)
# cfg.set(branch+'SSRO_stop_after_first_photon', 0)
# cfg.set(branch+'mw_frq',2.8e9) #-100e6)  #Probably Redundant, better to read out from AWG
# cfg.set(branch+'mw_power',20)
# cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

# branch='protocols/sil10-default/AdwinSSRO-integrated/'
# cfg.set(branch+'SSRO_duration', 40)

# ### sil 10 pulses ### !!!NOT CALIBRATED

# branch='protocols/sil10-default/pulses/'

# f0 = cfg['samples']['sil10']['ms-1_cntr_frq'] - cfg['protocols']['sil10-default']['AdwinSSRO']['mw_frq']
# cfg.set(branch+'MW_modulation_frequency', f0)
# cfg.set(branch+'Pi_pulse_duration', 50e-9)
# cfg.set(branch+'Pi_pulse_amp',  0.49)
# cfg.set(branch+'CORPSE_pi2_amp',0.4)
# CORPSE_frq = 8.15e6
# cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

# cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)



# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
# cfg.set('protoMW_pulse_frequencycols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

# cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
# cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
# cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)




# ### sil 15 ###
# branch='samples/sil15/'

# f_msm1_cntr = 2.828992e9
# f_msp1_cntr = 2.925693e9
# N_frq = 7.13429e6
# N_HF_frq = 2.193e6

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


# ### sil 1 ###
# branch='samples/sil1/'

# f_msm1_cntr = 2.829e9
# f_msp1_cntr = 2.925693e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)

# ### sil 5 ###
# branch='samples/sil5/'

# f_msm1_cntr = 2.829e9 #not calibrated
# f_msp1_cntr = 2.925747e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


### sil 7 ###
# branch='samples/sil7/'

# f_msm1_cntr = 2.829e9 #not calibrated
# f_msp1_cntr = 2.925871e9
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


### sil 11 ###
# branch='samples/sil11/'

# f_msm1_cntr = 2.829e9
# f_msp1_cntr = 2.926e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)



#### sil9 ###
#### sil9, AdwinSSRO ###
#
#
#### sil 9 ###
#branch='samples/sil9/'
#
#f_msm1_cntr = 2.828825e9
#f_msp1_cntr = 2.925884e9 #not calibrated
#N_frq = 7.13429e6 #not calibrated
#N_HF_frq = 2.189e6
#
#cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
#cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
#cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
#cfg.set(branch+'N_HF_frq', N_HF_frq)
#
#
#branch='protocols/sil9-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 10e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 40e-9)
#cfg.set(branch+'CR_duration' , 50)
#cfg.set(branch+'CR_preselect', 15)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 1000)
#cfg.set(branch+'Ex_CR_amplitude', 10e-9)
#cfg.set(branch+'Ex_RO_amplitude', 10e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'mw_frq',2.8e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil9, AdwinSSRO integrated ###
#branch='protocols/sil9-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 23)
#
## # MBI
#branch='protocols/sil9-default/AdwinSSRO+MBI/'
#cfg.set(branch+        'Ex_MBI_amplitude',              10e-9)
#cfg.set(branch+        'Ex_SP_amplitude',               10e-9)
#cfg.set(branch+        'MBI_duration',                  4)
#cfg.set(branch+        'MBI_steps',                     1)
#cfg.set(branch+        'MBI_threshold',                 1)
#cfg.set(branch+        'SP_E_duration',                 200)
#cfg.set(branch+        'repump_after_MBI_duration',     10)
#cfg.set(branch+        'repump_after_MBI_amplitude',    5e-9)
#cfg.set(branch+        'repump_after_E_RO_duration',    10)
#cfg.set(branch+        'repump_after_E_RO_amplitude',   5e-9)
#
## MBI pulse
#cfg.set(branch+        'AWG_wait_duration_before_MBI_MW_pulse',     50e-9)
#cfg.set(branch+        'AWG_wait_for_adwin_MBI_duration',           15e-6)
#
#
#### sil 9 pulses
#f0 = cfg['samples']['sil9']['ms-1_cntr_frq'] - cfg['protocols']['sil9-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil9-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.677)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
#finit = f0 - N_HF_frq
#fmIp1 = f0 + N_HF_frq
#
#cfg.set(branch+'mIm1_mod_frq',finit)
#cfg.set(branch+'mI0_mod_frq',f0)
#cfg.set(branch+'mIp1_mod_frq',fmIp1)
#
#CORPSE_frq = 8.15e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.438)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.474)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.69e-6)
#
##################NOT CALIBRATED!!
#
#cfg.set(branch+        'selective_pi_duration',     2500e-9)
#cfg.set(branch+        'selective_pi_amp',          0.011)
#cfg.set(branch+        'selective_pi_mod_frq',      finit)
#
#cfg.set(branch+        'pi2pi_mIm1_duration',        395e-9)
#cfg.set(branch+        'pi2pi_mIm1_amp',             0.0827)
#cfg.set(branch+        'pi2pi_mIm1_mod_frq',         finit)
#
#cfg.set(branch+        'AWG_MBI_MW_pulse_mod_frq',    finit)
#cfg.set(branch+        'AWG_MBI_MW_pulse_ssbmod_frq', finit)
#cfg.set(branch+        'AWG_MBI_MW_pulse_amp',        cfg.get(branch+        'selective_pi_amp'))
#cfg.set(branch+        'AWG_MBI_MW_pulse_duration',   cfg.get(branch+        'selective_pi_duration'))
#
#cfg.set(branch+        'AWG_shelving_pulse_duration', cfg.get(branch+        '8MHz_pi_duration'))
#cfg.set(branch+        'AWG_shelving_pulse_amp',     cfg.get(branch+        '8MHz_pi_amp'))
#




### Specific protocol settings ###

### sil15 ###
### sil15, AdwinSSRO ###
#branch='protocols/sil15-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 20e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 12)
#cfg.set(branch+'CR_probe', 12)
#cfg.set(branch+'CR_repump', 100)
#cfg.set(branch+'Ex_CR_amplitude', 20e-9)
#cfg.set(branch+'Ex_RO_amplitude', 20e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.9e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil15, AdwinSSRO integrated ###
#branch='protocols/sil15-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#### sil 15 pulses
#f0 = cfg['samples']['sil15']['ms+1_cntr_frq'] - cfg['protocols']['sil15-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil15-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.677)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

# cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
# cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
# cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)

#CORPSE_frq = 8.035e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.605)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.639)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.75e-6)



### sil1 ###
### sil1, AdwinSSRO ###
#branch='protocols/sil1-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 20e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 12)
#cfg.set(branch+'CR_probe', 12)
#cfg.set(branch+'CR_repump', 100)
#cfg.set(branch+'Ex_CR_amplitude', 20e-9)
#cfg.set(branch+'Ex_RO_amplitude', 10e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.8e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil1, AdwinSSRO integrated ###
#branch='protocols/sil1-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#
#### sil5 ###
#### sil5, AdwinSSRO ###
#branch='protocols/sil5-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 20e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 30e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 15)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 1000)
#cfg.set(branch+'Ex_CR_amplitude', 10e-9)
#cfg.set(branch+'Ex_RO_amplitude', 5e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.9e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil5, AdwinSSRO integrated ###
#branch='protocols/sil5-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
## pulses
#f0 = cfg['samples']['sil5']['ms+1_cntr_frq'] - cfg['protocols']['sil5-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil5-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.545)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)
#
## cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
## cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
## cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)
#
#CORPSE_frq = 8.050e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.547)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.577)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.61e-6)
#
#### sil7 ###
#### sil7, AdwinSSRO ###
#branch='protocols/sil7-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 15e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 150)
#cfg.set(branch+'CR_preselect', 8)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 1000)
#cfg.set(branch+'Ex_CR_amplitude', 15e-9)
#cfg.set(branch+'Ex_RO_amplitude', 20e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.9e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil7, AdwinSSRO integrated ###
#branch='protocols/sil7-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#### sil 7 pulses
#f0 = cfg['samples']['sil7']['ms+1_cntr_frq'] - cfg['protocols']['sil7-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil7-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.677)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)
#
## cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
## cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
## cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)
#
#CORPSE_frq = 8.102e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.640)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.698)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.61e-6)
#
#
#
#
#
#### sil11 ###
#### sil11, AdwinSSRO ###
#branch='protocols/sil11-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 15e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 6)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 100)
#cfg.set(branch+'Ex_CR_amplitude', 10e-9)
#cfg.set(branch+'Ex_RO_amplitude', 10e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.8e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil11, AdwinSSRO integrated ###
#branch='protocols/sil11-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#


