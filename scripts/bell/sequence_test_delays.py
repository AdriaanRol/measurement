from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import qt
import numpy as np


def pulse_defs_lt3(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)

    msmt.TIQ = pulse.SquarePulse(channel='MW_Imod',
        length = 10e-9, amplitude = 0)
    ### synchronizing, etc
    msmt.adwin_lt3_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2) #only used for calibrations!!

    ### LDE attempt
    msmt.eom_aom_pulse = pulselib.EOMAOMPulse('Eom Aom Pulse', 
        eom_channel = 'EOM_Matisse',
        aom_channel = 'EOM_AOM_Matisse',
        eom_pulse_duration = msmt.params_lt3['eom_pulse_duration'],
        eom_off_duration = msmt.params_lt3['eom_off_duration'],
        eom_off_amplitude = msmt.params_lt3['eom_off_amplitude'],
        eom_pulse_amplitude = msmt.params_lt3['eom_pulse_amplitude'],
        eom_overshoot_duration1 = msmt.params_lt3['eom_overshoot_duration1'],
        eom_overshoot1 = msmt.params_lt3['eom_overshoot1'],
        eom_overshoot_duration2 = msmt.params_lt3['eom_overshoot_duration2'],
        eom_overshoot2 = msmt.params_lt3['eom_overshoot2'],
        aom_risetime = msmt.params_lt3['aom_risetime'])
    
    msmt.short_eom_aom_pulse = pulselib.short_EOMAOMPulse('Eom Aom Pulse', 
        eom_channel = 'EOM_Matisse',
        aom_channel = 'EOM_AOM_Matisse',
        eom_off_duration = msmt.params_lt3['eom_off_duration'],
        eom_off_amplitude = msmt.params_lt3['eom_off_amplitude'],
        eom_off_2_amplitude  = 2.65, #msmt.params_lt3['eom_off_2_amplitude'],
        eom_overshoot_duration1 = msmt.params_lt3['eom_overshoot_duration1'],
        eom_overshoot1 = 0.0, #msmt.params_lt3['eom_overshoot1'],
        eom_overshoot_duration2 = msmt.params_lt3['eom_overshoot_duration2'],
        eom_overshoot2 = 0.0, #msmt.params_lt3['eom_overshoot2'],
        aom_risetime = msmt.params_lt3['aom_risetime'])    

    msmt.TH_sync = pulse.SquarePulse(channel = 'TH_sync', length = 50e-9, amplitude = 1.0)
    msmt.eom_trigger = pulse.SquarePulse(channel = 'EOM_trigger', length = 100e-9, amplitude = 0.0)
    msmt.SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
    msmt.empty_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 0.0)
    # msmt.yellow_pulse = pulse.SquarePulse(channel = 'AOM_Yellow', amplitude = 1.0)

    ### LDE attempt

    return True



#************************ Sequence elements LT3   ******************************

#### single elements
def _lt3_sequence_finished_element(msmt):  ### WE NEED THIS GUY
    """
    last element of a two-setup sequence. Sends a trigger to ADwin LT3.
    """
    e = element.Element('LT3_finished', pulsar = qt.pulsar)
    e.append(msmt.adwin_lt3_trigger_pulse)
    return e

def _lt3_dummy_element(msmt):   ### WE NEED THIS GUY
    """
    A 10us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('Dummy', pulsar = qt.pulsar)
    e.append(pulse.cp(msmt.T, length=10e-6))
    return e


def _lt3_LDE_element(msmt, **kw):  ### WE NEED THIS GUY
    """
    This element contains the LDE part for LT3, i.e., spin pumping and MW pulses
    for the LT3 NV and the optical pi pulses as well as all the markers for HH and PLU.
    """

    # variable parameters
    name = kw.pop('name', 'LDE_LT3')
    pi2_pulse_phase = kw.pop('pi2_pulse_phase', 0)
    if kw.pop('use_short_eom_pulse',False):
        eom_pulse=pulse.cp(msmt.short_eom_aom_pulse,
            aom_on=msmt.params_lt3['eom_aom_on'])
    else:
        eom_pulse=pulse.cp(msmt.eom_aom_pulse,
            eom_pulse_amplitude = kw.pop('eom_pulse_amplitude', msmt.params_lt3['eom_pulse_amplitude']),
            eom_off_amplitude = kw.pop('eom_off_amplitude', msmt.params_lt3['eom_off_amplitude']),
            aom_on=msmt.params_lt3['eom_aom_on'])

    ###
    e = element.Element(name, 
        pulsar = qt.pulsar, 
        global_time = True)
    e.add(pulse.cp(msmt.empty_pulse,
            amplitude = 0,
            length = msmt.params['LDE_element_length']))

    #1 SP
    e.add(pulse.cp(msmt.empty_pulse, 
            amplitude = 0, 
            length = msmt.params_lt3['initial_delay']), 
        name = 'initial delay')
    
    
    for i in range(msmt.params['opt_pi_pulses']):
        name = 'opt pi {}'.format(i+1)
        refpulse = 'opt pi {}'.format(i) if i > 0 else 'initial delay'
        start = msmt.params_lt3['opt_pulse_separation'] if i > 0 else msmt.params['wait_after_sp']
        refpoint = 'start' if i > 0 else 'end'

        e.add(eom_pulse,        
            name = name, 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)
        e.add(msmt.eom_trigger,
            name = name+'_trigger', 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)

    #5 HHsync
    syncpulse_name = e.add(msmt.TH_sync, refpulse = 'initial delay', refpoint = 'start', refpoint_new = 'end')

    ############

    if e.length() != msmt.params['LDE_element_length']:
        raise Exception('LDE element length'+e.name+' is not as specified - granylarity issue?')
    return e

    return e


def _lt3_calib_element(msmt, **kw):  ### WE NEED THIS GUY
    """
    This element should be used for calibration of the delay time of the AOMs and
    """

    # variable parameters
    name = kw.pop('name', 'calib_LT3')
    # name = kw.pop('name', 'LDE_LT3')
    #pi2_pulse_phase = kw.pop('pi2_pulse_phase', 0)
    if kw.pop('use_short_eom_pulse',False):
        eom_pulse=pulse.cp(msmt.short_eom_aom_pulse,
            aom_on=msmt.params_lt3['eom_aom_on'])
    else:
        eom_pulse=pulse.cp(msmt.eom_aom_pulse,
            eom_pulse_amplitude = msmt.params_lt3['eom_pulse_amplitude'],
            aom_on=msmt.params_lt3['eom_aom_on'])

    ###
    e = element.Element(name, 
        pulsar = qt.pulsar, 
        global_time = True)
    e.add(pulse.cp(msmt.SP_pulse,
            amplitude = 0,
            length = msmt.params['LDE_element_length']))

    #1 SP
    e.add(pulse.cp(msmt.SP_pulse, 
            amplitude = 0, 
            length = msmt.params_lt3['initial_delay']), 
        name = 'initial delay')
    
    e.add(pulse.cp(msmt.SP_pulse, 
            length = msmt.params['LDE_SP_duration'], 
            amplitude = 1.0), 
        name = 'spinpumping', 
        refpulse = 'initial delay')

    # e.add(pulse.cp(msmt.yellow_pulse, 
    #         length = msmt.params['LDE_SP_duration_yellow'], 
    #         amplitude = 1.0), 
    #     name = 'spinpumpingyellow', 
    #     refpulse = 'initial delay')

    
    for i in range(msmt.params['opt_pi_pulses']):
        name = 'opt pi {}'.format(i+1)
        refpulse = 'opt pi {}'.format(i) if i > 0 else 'spinpumping'
        start = msmt.params_lt3['opt_pulse_separation'] if i > 0 else msmt.params['wait_after_sp']
        refpoint = 'start' if i > 0 else 'end'

        e.add(eom_pulse,        
            name = name, 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)
        e.add(msmt.eom_trigger,
            name = name+'_trigger', 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)
    #4 MW pi/2
    if msmt.params_lt3['MW_during_LDE'] == 1 :
        e.add(pulse.cp(msmt.CORPSE_pi2, 
            phase = pi2_pulse_phase), 
            start = -msmt.params_lt3['MW_opt_puls1_separation'],
            refpulse = 'opt pi 1', 
            refpoint = 'start', 
            refpoint_new = 'end')
    #5 HHsync
    syncpulse_name = e.add(msmt.TH_sync, refpulse = 'opt pi 1', refpoint = 'start', refpoint_new = 'end')
    
    #6 plugate 1
    e.add(msmt.plu_gate, name = 'plu gate 1', 
        refpulse = 'opt pi 1',
        start = msmt.params_lt3['PLU_1_delay'])

    #8 MW pi
    if msmt.params_lt3['MW_during_LDE'] == 1:
        e.add(msmt.CORPSE_pi, 
            start = - msmt.params_lt3['MW_opt_puls2_separation'],
            refpulse = 'opt pi 2', 
            refpoint = 'start', 
            refpoint_new = 'end')
    
    #10 plugate 2
    e.add(msmt.plu_gate, 
        name = 'plu gate 2',
        refpulse = 'opt pi {}'.format(msmt.params['opt_pi_pulses']),
        start = msmt.params_lt3['PLU_2_delay']) 

    #11 plugate 3
    e.add(pulse.cp(msmt.plu_gate, 
            length = msmt.params_lt3['PLU_gate_3_duration']), 
        name = 'plu gate 3', 
        start = msmt.params_lt3['PLU_3_delay'], 
        refpulse = 'plu gate 2')
    
    #12 plugate 4
    e.add(msmt.plu_gate, name = 'plu gate 4', start = msmt.params_lt3['PLU_4_delay'],
            refpulse = 'plu gate 3')

    ############

    if e.length() != msmt.params['LDE_element_length']:
        raise Exception('LDE element length'+e.name+' is not as specified - granylarity issue?')
    return e

    return e



def _lt3_adwin_lt3_trigger_elt(msmt): #only used in calibration
    sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
    sync_elt.append(msmt.adwin_lt3_trigger_pulse)

    return sync_elt




def _lt3_final_id(msmt, name, time_offset, **kw):
    wait_length = msmt.params_lt3['CORPSE_pi2_wait_length'] + msmt.CORPSE_pi.length 
    final_id_elt = element.Element('second_id_elt-{}'.format(name), pulsar= qt.pulsar, 
                global_time = True, time_offset = time_offset)
    final_id_elt.append(pulse.cp(msmt.T, length =  wait_length)) 
    final_id_elt.append(pulse.cp(msmt.T, length =  100e-9 )) 

    return final_id_elt