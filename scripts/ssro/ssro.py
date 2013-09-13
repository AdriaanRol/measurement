"""
LT1 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import msvcrt

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

def calibration(name,yellow=False):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)

    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
        
    # parameters
    m.params['SSRO_repetitions'] = 5000
    
    #repump settings
    _set_repump_settings(m,yellow)
    
    # ms = 0 calibration
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitude'] = 5e-9
    
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 10e-9
    m.params['Ex_RO_amplitude'] = 5e-9

    m.run()
    m.save('ms1')
    m.finish()
    
def RO_optimal_power(name, yellow=False):
    m = ssro.AdwinSSRO('RO_saturation_power_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    
    #parameters
    m.params['SSRO_repetitions'] = 5000
    m.params['pts'] = 5
    pts = m.params['pts']

    #repump settings
    _set_repump_settings(m,yellow)
    
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitudes'] = np.arange(pts)*2e-9 + 2e-9

    for p in m.params['Ex_RO_amplitudes']:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
        print 'ms0 1/{}: P = {} '.format(pts, p)
        m.params['Ex_RO_amplitude'] = p
        m.run()
        m.save('ms0_P_%dnW' % (p*1e9))
        
    m.params['A_SP_amplitude'] = 0e-9
    m.params['Ex_SP_amplitude'] = 10e-9
    m.params['Ex_RO_amplitudes'] = np.arange(pts)*2e-9 + 2e-9

    for p in m.params['Ex_RO_amplitudes']:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
        print 'ms1 1/{}: P = {} '.format(pts, p)
        m.params['Ex_RO_amplitude'] = p
        m.run()
        m.save('ms1_P_%dnW' % (p*1e9))
   

    m.finish()

def RO_saturation_power(name, yellow=False):
    m = ssro.AdwinSSRO('RO_saturation_power_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['hans-sil4-default']['AdwinSSRO'])
    
    m.params['SSRO_repetitions'] = 5000
    m.params['pts'] = 10
    pts = m.params['pts']
    step = 1e-9

    #repump settings
    _set_repump_settings(m,yellow) 

    m.params['CR_preselect'] = 1000
    m.params['CR_probe'] = 10
    m.params['A_SP_amplitude'] = 5e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['Ex_RO_amplitudes'] = np.arange(pts) * step + step
    m.params['SSRO_duration'] = 100

    for i,p in enumerate(m.params['Ex_RO_amplitudes']):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
        
        print
        print '{}/{}: P = {} '.format(i+1, pts, p) 
        m.params['Ex_RO_amplitude'] = p
        m.run()
        m.save('P_{:.1f}_nW'.format(p*1e9))
        
    m.finish()

def SP_saturation_power(name, yellow=False):
    m = ssro.AdwinSSRO('SP_saturation_power_'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['hans-sil4-default']['AdwinSSRO'])
    
    m.params['SSRO_repetitions'] = 5000
    m.params['pts'] = 10
    pts = m.params['pts']
    step = 1e-9

    #repump settings
    _set_repump_settings(m,yellow) 

    m.params['CR_preselect'] = 1000
    m.params['CR_probe'] = 10
    m.params['A_CR_amplitude'] = 5e-9 
    m.params['E_CR_amplitude'] = 5e-9

    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 5e-9
    m.params['Ex_RO_amplitude'] = 0 
    m.params['SP_duration'] = 250
    m.params['A_RO_amplitudes'] = np.arange(pts) * step + step
    m.params['SSRO_duration'] = 100

    for i,p in enumerate(m.params['A_RO_amplitudes']):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
        
        print
        print '{}/{}: P = {} '.format(i+1, pts, p) 
        m.params['A_RO_amplitude'] = p
        m.run()
        m.save('P_{:.1f}_nW'.format(p*1e9))
        
    m.finish()

def threshold_calibration(name, yellow=False):

    max_rep = 8
    repetitions =  np.arange(max_rep)+1
    sweep_probes = [False, True]

    m = ssro.AdwinSSRO('SP_threshold_CR_50us_Ey_reps'+name)
    
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['hans-sil4-default']['AdwinSSRO'])
    
    m.params['SSRO_repetitions'] = 5000

    #repump settings
    _set_repump_settings(m,yellow) 

    m.params['A_CR_amplitude'] = 5e-9 
    m.params['E_CR_amplitude'] = 5e-9
    m.params['CR_duration'] = 50 

    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] =0.e-9
    m.params['Ex_RO_amplitude'] = 5.e-9 
    m.params['SP_duration'] = 50
    m.params['A_RO_amplitude'] = 0.e-9
    m.params['SSRO_duration'] = 100

    for r in repetitions:
        print '{}/{} repetitions'.format(r,max_rep)
        for t in sweep_probes:

            #sweep setting
            if t == True:
                m.params['pts'] = 11
                pts = m.params['pts']
                sweep_probe = True
                m.params['CR_preselects'] = np.ones(pts)*30
                m.params['CR_probes'] = [1,2,3,4,6,8,10,15,20,25,30]
            else:
                m.params['pts'] = 9
                pts = m.params['pts']
                sweep_probe = False              
                m.params['CR_preselects'] = np.linspace(5,45,pts) #np.ones(pts)*30 ### #np.ones(pts)*30#
                m.params['CR_probes'] = m.params['CR_preselects']### np.ones(pts)*30#

            if sweep_probe:
                pre = m.params['CR_preselects'][0]
                for i,pro in enumerate(m.params['CR_probes']):
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
                
                    print
                    print '{}/{}: pres. = {}, probe = {} '.format(i+1, pts, pre, pro) 
                    m.params['CR_preselect'] = pre
                    m.params['CR_probe'] = pro
                    m.run()
                    m.save('th_pres_{}_probe_{}_r_{}_sweepprobe_{}'.format(int(pre),int(pro),r,t))
                
            else:
                for i,pre in enumerate(m.params['CR_preselects']):
                    pro = pre #when sweeping preselect, we want this threshold also for probe
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
                
                    print
                    print '{}/{}: pres. = {}, probe = {} '.format(i+1, pts, pre, pro) 
                    m.params['CR_preselect'] = pre
                    m.params['CR_probe'] = pro 
                    m.run()
                    m.save('th_pres_{}_probe_{}_r_{}_sweepprobe_{}'.format(int(pre),int(pro),r,t))
            
    m.finish()



# def SP_RO_saturation_power(name, yellow=False):
#     m = ssro.AdwinSSRO('RO_saturation_power_'+name)
    
#     m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
#     m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])
    
#     #repump settings
#     _set_repump_settings(m,yellow)
    
#     m.params['Ex_SP_amplitude'] = 0.
#     m.params['Ex_RO_amplitudes'] = np.arange(20)*4e-9 + 2e-9

#     for p in m.params['Ex_RO_amplitudes']:
#         if (msvcrt.kbhit() and (msvcrt.getch() == 'c')): break
#         m.params['Ex_RO_amplitude'] = p
#         m.params['A_SP_amplitude'] = 0
#         m.run()
#         m.save('P_%dnW' % (p*1e9))
        
#     m.finish()
    
def _set_repump_settings(m,yellow):
    if yellow:
        qt.instruments['GreenAOM'].set_power(0)
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=1
        m.params['repump_after_repetitions']=100
    else:
        qt.instruments['YellowAOM'].set_power(0)
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']

if __name__ == '__main__':
    # RO_saturation_power('hans4_Ey_saturation')
    # SP_saturation_power('hans4_SP_saturation')
    threshold_calibration('hans_sil4_preselect')