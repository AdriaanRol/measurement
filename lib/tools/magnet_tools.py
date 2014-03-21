### A module for performing magnetic field calculations.
### Examples are conversions between fields and frequencies, 
### determining the magnet position and calculating the magnet 
### path to a desired magnetic field.

### Import the config manager and NV parameters
import qt
import numpy as np
cfg = qt.cfgman
execfile("lt2_scripts/setup/msmt_params.py")
current_NV  = cfg.get('samples/current')

### Import the NV and current esr parameters
ZFS         = cfg.get('samples/' + current_NV + '/zero_field_splitting')
g_factor    = cfg.get('samples/' + current_NV + '/g_factor')
current_f_msm1 = cfg.get('samples/' + current_NV + '/ms-1_cntr_frq')
current_f_msp1 = cfg.get('samples/' + current_NV + '/ms+1_cntr_frq')

### Import the magnet parameters
nm_per_step         = cfg.get('magnet/'+'nm_per_step')          
radius              = cfg.get('magnet/'+'radius')      
thickness           = cfg.get('magnet/'+'thickness')             
strength_constant   = cfg.get('magnet/'+'strength_constant')    

### Simple conversions
def convert_Bz_to_f(B_field):
    ''' Calculates the (ms=-1, ms=+1) frequencies
    for a given B_field input. Assumes the field is along Z
    '''
    freq_msm1 = ZFS - B_field * g_factor
    freq_msp1 = ZFS + B_field * g_factor    
    return freq_msm1, freq_msp1

def convert_f_to_Bz(freq=current_f_msm1):
    ''' Calculates the B_field (z-component only)
    for a given frequency (either ms=-1 or ms=+1). 
    Assumes a field along Z'''

    B_field = abs(ZFS-freq)/g_factor
    return B_field

def calc_ZFS(msm1_freq=current_f_msm1, msp1_freq=current_f_msp1):
    ''' calculate the average of the current ESR frequencies '''
    calculated_ZFS = (msm1_freq+msp1_freq)/2
    return calculated_ZFS

### Get the field vector values and magnet position
def get_B_field(msm1_freq=current_f_msm1, msp1_freq=current_f_msp1):
    ''' Returns the (Bz_field, Bx_field) for given given 
    ms=-1 and ms=0 frequencies (GHz)
    ''' 
    msm1_f = msm1_freq*1e9
    msp1_f = msp1_freq*1e9
    Bz = (msp1_f**2 - msm1_f**2)/(4.*ZFS*g_factor)
    Bx = (abs(msm1_f**2 - (ZFS-g_factor*Bz)**2 )**0.5)/g_factor
    return (Bz, Bx)

def get_magnet_position(msm1_freq=current_f_msm1, msp1_freq=current_f_msp1):
    ''' determines the magnet position (mm) for given msm1_freq 
    and msp1_freq (GHz)'''    
    pass

def get_field_at_position(distance):
    ''' returns the field (G) at input distance (mm)'''    
    B_field = 1e4* strength_constant/2. * ( (thickness+distance)/(radius**2 +(thickness+distance)**2)**0.5 \
            - distance/(radius**2 + distance**2)**0.5)
    return B_field

def get_field_gradient(distance):
    ''' returns the field (G) at input distance (mm)'''    
    return B_field

def get_all(freq_ms_m1, freq_ms_p1):
    '''function that returns all the magnetic field and magnet properties
    for the given ms=-1 and ms=0 frequencies'''
    pass

### Detemrine where to move

def steps_to_frequency():
    '''determine the steps needed to go to a certain frequency
    or field'''

def steps_to_field():
    '''determine the steps needed to go to a certain frequency
    or field'''














