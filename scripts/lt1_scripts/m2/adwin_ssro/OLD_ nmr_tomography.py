import numpy as np
import qt
import hdf5_data as h5
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.AWG_HW_sequencer_v2 import Sequence

import mbi
reload(mbi)

chan_mw_pm = 'MW_pulsemod'
chan_mwI = 'MW_Imod'
chan_mwQ = 'MW_Qmod'
chan_RF  = 'RF'
chan_adwin_sync = 'adwin_sync'

physical_adwin = qt.instruments['physical_adwin']
MW_pulse_mod_risetime = qt.cfgman['setup']['MW_pulsemod_risetime']
AWG_to_adwin_ttl_trigger_duration = qt.cfgman['setup']['AWG_to_adwin_ttl_trigger_duration']

class NMRTomography(mbi.MBIMeasurement):
    
    def sequence(self):

        # measure in three bases: X,Y,Z
        # measure along X axis by rotating around -y
        # measure along Y axis by rotating around x.
        names = ['Z', 'X', 'Y']
        lengths = [0, self.params['AWG_RF_p2pulse_duration'], self.params['AWG_RF_p2pulse_duration']]
        phases = [0, 0, -90.] 
        amplitudes = [0, self.params['AWG_RF_p2pulse_amp'],self.params['AWG_RF_p2pulse_amp']]
        
        for n,l,p,a in zip(names, lengths, phases, amplitudes):
            self._MBI_seq_element(el_name='MBI_pulse-'+n,
                    jump_target='spin_control-'+n,
                    goto_target='MBI_pulse-'+n+'-0')
          
            if n == names[-1]:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True, goto_target = 'MBI_pulse-'+names[0]+'-0')
            else:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True)
            
            last = self._shelving_pulse(pulse_name = 'shelving_pulse-'+n,
                    el_name='spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
            
            # # Implement a Hadamard gate by XSqrtY. Do the Y first
            # # This is a rotation pi/2 around the Y axis, so we need a phase 180
            # # Now, turn it into a pi/2 pulse around -Y. phase 0. 
            self.seq.add_pulse('RF_pulse-1-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = 0, start_reference = last, link_start_to='end', 
                    duration = int(self.params['AWG_RF_p2pulse_duration']),
                    amplitude = self.params['AWG_RF_p2pulse_amp'],
                    shape ='cosine',
                    phase = -90,
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-1-'+n

            # # waiting time between RF pulse. 
            # self.seq.add_pulse('wait_between_RF', chafrom analysis.lib.math import error, tomographynnel = chan_RF, 
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference=last, link_start_to='end', 
            #         duration = 2000, amplitude = 0)
            # last = 'wait_between_RF'

            # # Now do the rotation around the X axis. This is a phase -90
            # self.seq.add_pulse('RF_pulse-2-'+n, channel=chan_RF,
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference = last, link_start_to='end', 
            #         duration = int(self.params['AWG_pipulse_duration']),
            #         amplitude = self.params['AWG_pipulse_amplitude'],
            #         shape ='cosine',
            #         phase = -90,
            #         frequency = self.params['AWG_pipulse_frq'],
            #         envelope='erf',
            #         envelope_risetime=200)
            # last = 'RF_pulse-2-'+n

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_rotation_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_p2pulse_duration'], 
                    start_reference=last, link_start_to='end', 
                    duration = 86110, amplitude = 0)
            last = 'wait_before_rotation_RF'
            
            # Basis rotation
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start =-int(l)/2, start_reference = last, link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5000, 
                    amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            
            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

        return

class NMRTomoHadamard(mbi.MBIMeasurement):
    
    def sequence(self):

        # measure in three bases: X,Y,Z
        # measure along X axis by rotating around -y
        # measure along Y axis by rotating around x.
        names = ['Z', 'X', 'Y']
        lengths = [0, self.params['AWG_RF_p2pulse_duration'], self.params['AWG_RF_p2pulse_duration']]
        phases = [0, 0, -90.] 
        amplitudes = [0, self.params['AWG_RF_p2pulse_amp'],self.params['AWG_RF_p2pulse_amp']]
        
        for n,l,p,a in zip(names, lengths, phases, amplitudes):
            self._MBI_seq_element(el_name='MBI_pulse-'+n,
                    jump_target='spin_control-'+n,
                    goto_target='MBI_pulse-'+n+'-0')
          
            if n == names[-1]:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True, goto_target = 'MBI_pulse-'+names[0]+'-0')
            else:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True)
            
            last = self._shelving_pulse(pulse_name = 'shelving_pulse-'+n,
                    el_name='spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
            
            # # Implement a Hadamard gate by a rotation around X, detuned by
            # frabi. 
            self.seq.add_pulse('RF_pulse-1-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = 0, start_reference = last, link_start_to='end', 
                    duration = int(self.params['AWG_RF_Hadamardpulse_duration']),
                    amplitude = self.params['AWG_RF_Hadamardpulse_amp'],
                    shape ='cosine',
                    phase = 180,#-90,
                    frequency = self.params['AWG_RF_Hadamardpulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-1-'+n

            # # Now do the rotation around the X axis. This is a phase -90
            # self.seq.add_pulse('RF_pulse-2-'+n, channel=chan_RF,
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference = last, link_start_to='end', 
            #         duration = int(self.params['AWG_pipulse_duration']),
            #         amplitude = self.params['AWG_pipulse_amplitude'],
            #         shape ='cosine',
            #         phase = -90,
            #         frequency = self.params['AWG_pipulse_frq'],
            #         envelope='erf',
            #         envelope_risetime=200)
            # last = 'RF_pulse-2-'+n

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_rotation_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -int(self.params['AWG_RF_Hadamardpulse_duration'])/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 86110, amplitude = 0)
            last = 'wait_before_rotation_RF'
            
            # Basis rotation
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -int(l)/2, 
                    start_reference = last, link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n
            
            #Introduce a waiting time before the CORPSE pulse
            self.seq.add_pulse('wait_before_CORPSE-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0,#self.params['AWG_Pi2_MW_pulse_duration']/2, 
                    start_reference =last,#'Pi2_pulse-'+n+'-I', 
                    link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_CORPSE-'+n        
            
            # Do a CORPSE pulse. All readout axes should now be 'the other way
            # around'.
            last = self._CORPSE_unconditional_pi(pulse_name = 'CORPSE_pulse-'+n,
                    el_name='spin_control-'+n, 
                    link_to = last,
                    mod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'],
                    start_delay = 0)

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5000, 
                    amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            
            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

        return



class CalibrateHadamard(mbi.MBIMeasurement):
    
    def sequence(self):

        # measure in three bases: X,Y,Z
        # measure along X axis by rotating around -y
        # measure along Y axis by rotating around x.
        names = ['Z', 'X', 'Y']
        lengths = [0, self.params['AWG_RF_p2pulse_duration'], self.params['AWG_RF_p2pulse_duration']]
        phases = [0, 0, -90.] 
        amplitudes = [0, self.params['AWG_RF_p2pulse_amp'],self.params['AWG_RF_p2pulse_amp']]
        
        for n,l,p,a in zip(names, lengths, phases, amplitudes):
            self._MBI_seq_element(el_name='MBI_pulse-'+n,
                    jump_target='spin_control-'+n,
                    goto_target='MBI_pulse-'+n+'-0')
          
            if n == names[-1]:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True, goto_target = 'MBI_pulse-'+names[0]+'-0')
            else:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True)
            
            last = self._shelving_pulse(pulse_name = 'shelving_pulse-'+n,
                    el_name='spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
            
            # # Implement a Hadamard gate by a rotation around X, detuned by
            # frabi. 
            self.seq.add_pulse('RF_pulse-1-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = 0, start_reference = last, link_start_to='end', 
                    duration = int(self.params['AWG_RF_Hadamardpulse_durations'][i]),
                    amplitude = self.params['AWG_RF_Hadamardpulse_amp'],
                    shape ='cosine',
                    phase = 180,#-90,
                    frequency = self.params['AWG_RF_Hadamardpulse_frqs'][i],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-1-'+n

            # # Now do the rotation around the X axis. This is a phase -90
            # self.seq.add_pulse('RF_pulse-2-'+n, channel=chan_RF,
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference = last, link_start_to='end', 
            #         duration = int(self.params['AWG_pipulse_duration']),
            #         amplitude = self.params['AWG_pipulse_amplitude'],
            #         shape ='cosine',
            #         phase = -90,
            #         frequency = self.params['AWG_pipulse_frq'],
            #         envelope='erf',
            #         envelope_risetime=200)
            # last = 'RF_pulse-2-'+n

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_rotation_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -int(self.params['AWG_RF_Hadamardpulse_durations'][i])/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 86110, amplitude = 0)
            last = 'wait_before_rotation_RF'
            
            # Basis rotation
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -int(l)/2, 
                    start_reference = last, link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n
            
            #Introduce a waiting time before the CORPSE pulse
            self.seq.add_pulse('wait_before_CORPSE-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0,#self.params['AWG_Pi2_MW_pulse_duration']/2, 
                    start_reference =last,#'Pi2_pulse-'+n+'-I', 
                    link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_CORPSE-'+n        
            
            # Do a CORPSE pulse. All readout axes should now be 'the other way
            # around'.
            last = self._CORPSE_unconditional_pi(pulse_name = 'CORPSE_pulse-'+n,
                    el_name='spin_control-'+n, 
                    link_to = last,
                    mod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'],
                    start_delay = 0)

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5000, 
                    amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            
            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

        return




class UncondPiOver2(mbi.MBIMeasurement):

    def sequence(self):

        # measure in three bases: X,Y,Z
        # measure along X axis by rotating around -y
        # measure along Y axis by rotating around x.
        names = ['Z', 'X', 'Y']
        lengths = [0, self.params['AWG_RF_p2pulse_duration'], self.params['AWG_RF_p2pulse_duration']]
        phases = [0, 0, -90.] 
        amplitudes = [0, self.params['AWG_RF_p2pulse_amp'],self.params['AWG_RF_p2pulse_amp']]

        for n,l,p,a in zip(names, lengths, phases, amplitudes):
            self._MBI_seq_element(el_name='MBI_pulse-'+n,
                    jump_target='spin_control-'+n,
                    goto_target='MBI_pulse-'+n+'-0')
          
            if n == names[-1]:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True, goto_target = 'MBI_pulse-'+names[0]+'-0')
            else:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True)
            
            #Pi over 2 pulse on the electron, to make a superposition
            # self.seq.add_IQmod_pulse(name = 'Pi2_pulse-'+n,
            #         channel = (chan_mwI,chan_mwQ),
            #         element = 'spin_control-'+n,
            #         start = 50, 
            #         duration = 0, ## int(self.params['AWG_Pi2_MW_pulse_duration']),
            #         amplitude = 0, ## self.params['AWG_Pi2_MW_pulse_amp'],
            #         frequency = self.params['AWG_Pi2_MW_pulse_ssbmod_frq'],
            #         start_reference = '',#last,
            #         link_start_to = 'end')
            # last = 'Pi2_pulse-'+n+'-I'            
            
            # waiting time before first RF pi over 2 pulse
            self.seq.add_pulse('wait_before_RF-1-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0, start_reference='',#last, 
                    link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF-1-'+n
                        
            #Do the first Pi over 2 gate
            self.seq.add_pulse('RF_pulse-1-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = 0, start_reference = last, 
                    link_start_to='end', 
                    duration = int(self.params['AWG_RF_p2pulse_duration']),
                    amplitude = self.params['AWG_RF_p2pulse_amp'],
                    shape ='cosine',
                    phase = -90,
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-1-'+n

            # Introduce the right amount of waiting time,
            #
            # In the BSM script this is the second timed waiting time
            # The start of this waiting time is the pi2 pulse (CNOT). 
            # The end is the CORPSE pulse.
            # The duration should be n*2pi/2.189e6=n*2870.3ns.
            # For n=30 this is 86110(.35) ns.
            # That is enough to cover Hadamard duration (~70us)
            # 
            # In the current script we do state tomography, and thus need to
            # do an RF basis rotation after the Hadamard. This requires a
            # different timing. (70e3/2+45e3/2=~60e3) Use n=27 -> 77499
            self.seq.add_pulse('wait_before_rotation_RF-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_p2pulse_duration']/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 106202,#77499+28703 , 
                    amplitude = 0)
            last = 'wait_before_rotation_RF-'+n
            

            # Basis rotation to read out basis for the population in ms=-1
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -int(l)/2, start_reference = last, 
                    link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n

            # Waiting time before CORPSE
            self.seq.add_pulse('wait_before_CORPSE-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -int(l)/2,#self.params['AWG_Pi2_MW_pulse_duration']/2, 
                    start_reference =last,#'Pi2_pulse-'+n+'-I', 
                    link_start_to='end', 
                    duration = 43055, amplitude = 0)
            last = 'wait_before_CORPSE-'+n        
            
            # Then let the waiting time last till the centre of the CORPSE. 
            # That is maybe risky since the CORPSE is composite. 
            # Also: maybe an error will occur since def _CORPSE_unc_pi asks
            # for ssbmod_frq. If it does: delete from _CORPSE etc, and also
            # from links to this pulse in other code.
            last = self._CORPSE_unconditional_pi(pulse_name = 'CORPSE_pulse-'+n,
                    el_name='spin_control-'+n, 
                    link_to = last,
                    mod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'],
                    start_delay = -self.params['AWG_uncond_CORPSE_total_duration']/2)

            # waiting time before RF pulse
            # This waiting time only gives an overall phase shift, so is not
            # important for the BSM. 
            # But for the state tomogrpahy I keep track of
            # it. include 15 periods of waiting time.
            self.seq.add_pulse('wait_before_RF-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start =  -self.params['AWG_uncond_CORPSE_total_duration']/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 43055, amplitude = 0)
            last = 'wait_before_RF-'+n
            
            self.seq.add_pulse('RF_pulse-2-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_p2pulse_duration']/2, 
                    start_reference = last, 
                    link_start_to='end', 
                    duration = int(self.params['AWG_RF_p2pulse_duration']),
                    amplitude = self.params['AWG_RF_p2pulse_amp'],
                    shape ='cosine',
                    phase = 180,
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-2-'+n   

            # waiting time before second RF Hadamard pulse
            # For the tomography we need the phase of this readout to match
            # that of last RF pulse.
            # Since I want to read out the state of the Nitrogen right after
            # the second Hadamard, the time in between should be
            # exactly 2pi*m, otherwise I read out something random. 
            self.seq.add_pulse('wait_before_rotation_RF-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_p2pulse_duration']/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 77499 , amplitude = 0)
            last = 'wait_before_rotation_RF-'+n
            
            # Basis rotation for the population now in ms=-1
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -int(l)/2, start_reference = last, 
                    link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n


            # Before read-out, my electron needs to be in ms=-1 again. Now
            # send it to ms=0.
            # self.seq.add_IQmod_pulse(name = 'Pi2_pulse-2-'+n,
            #         channel = (chan_mwI,chan_mwQ),
            #         element = 'spin_control-'+n,
            #         start = 50, 
            #         duration = 0, ## int(self.params['AWG_Pi2_MW_pulse_duration']),
            #         amplitude = 0, ## self.params['AWG_Pi2_MW_pulse_amp'],
            #         frequency = self.params['AWG_Pi2_MW_pulse_ssbmod_frq'],
            #         start_reference = '',#last,
            #         link_start_to = 'end')
            # last = 'Pi2_pulse-2-'+n+'-I'   


            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5523, 
                    amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            
            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

        return
## end Class UncondPi2


class UncondHadamard(mbi.MBIMeasurement):

    def sequence(self):

        # measure in three bases: X,Y,Z
        # measure along X axis by rotating around -y
        # measure along Y axis by rotating around x.
        names = ['Z', 'X', 'Y']
        lengths = [0, self.params['AWG_RF_p2pulse_duration'], self.params['AWG_RF_p2pulse_duration']]
        phases = [0, 0, -90.] 
        amplitudes = [0, self.params['AWG_RF_p2pulse_amp'],self.params['AWG_RF_p2pulse_amp']]

        for n,l,p,a in zip(names, lengths, phases, amplitudes):
            self._MBI_seq_element(el_name='MBI_pulse-'+n,
                    jump_target='spin_control-'+n,
                    goto_target='MBI_pulse-'+n+'-0')
          
            if n == names[-1]:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True, goto_target = 'MBI_pulse-'+names[0]+'-0')
            else:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True)
            
            #Pi over 2 pulse on the electron, to make a superposition
            # self.seq.add_IQmod_pulse(name = 'Pi2_pulse-'+n,
            #         channel = (chan_mwI,chan_mwQ),
            #         element = 'spin_control-'+n,
            #         start = 50, 
            #         duration = 0, ## int(self.params['AWG_Pi2_MW_pulse_duration']),
            #         amplitude = 0, ## self.params['AWG_Pi2_MW_pulse_amp'],
            #         frequency = self.params['AWG_Pi2_MW_pulse_ssbmod_frq'],
            #         start_reference = '',#last,
            #         link_start_to = 'end')
            # last = 'Pi2_pulse-'+n+'-I'            
            
            # waiting time before first RF Hadamard pulse
            self.seq.add_pulse('wait_before_RF-1-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0, start_reference='',#last, 
                    link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF-1-'+n
                        
            #Do the first Hadamard gate
            self.seq.add_pulse('RF_pulse-1-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = 0, start_reference = last, 
                    link_start_to='end', 
                    duration = int(self.params['AWG_RF_Hadamardpulse_duration']),
                    amplitude = self.params['AWG_RF_Hadamardpulse_amp'],
                    shape ='cosine',
                    phase = 180,
                    frequency = self.params['AWG_RF_Hadamardpulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-1-'+n

            # Introduce the right amount of waiting time,
            #
            # In the BSM script this is the second timed waiting time
            # The start of this waiting time is the pi2 pulse (CNOT). 
            # The end is the CORPSE pulse.
            # The duration should be n*2pi/2.189e6=n*2870.3ns.
            # For n=30 this is 86110(.35) ns.
            # That is enough to cover Hadamard duration (~70us)
            # 
            # In the current script we do state tomography, and thus need to
            # do an RF basis rotation after the Hadamard. This requires a
            # different timing. (70e3/2+45e3/2=~60e3) Use n=27 -> 77499
            self.seq.add_pulse('wait_before_rotation_RF-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_Hadamardpulse_duration']/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 106202,#77499+28703 , 
                    amplitude = 0)
            last = 'wait_before_rotation_RF-'+n
            

            # Basis rotation to read out basis for the population in ms=-1
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -int(l)/2, start_reference = last, 
                    link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n

            # Waiting time before CORPSE
            self.seq.add_pulse('wait_before_CORPSE-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -int(l)/2,#self.params['AWG_Pi2_MW_pulse_duration']/2, 
                    start_reference =last,#'Pi2_pulse-'+n+'-I', 
                    link_start_to='end', 
                    duration = 43055, amplitude = 0)
            last = 'wait_before_CORPSE-'+n        
            
            # Then let the waiting time last till the centre of the CORPSE. 
            # That is maybe risky since the CORPSE is composite. 
            # Also: maybe an error will occur since def _CORPSE_unc_pi asks
            # for ssbmod_frq. If it does: delete from _CORPSE etc, and also
            # from links to this pulse in other code.
            last = self._CORPSE_unconditional_pi(pulse_name = 'CORPSE_pulse-'+n,
                    el_name='spin_control-'+n, 
                    link_to = last,
                    mod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'],
                    start_delay = -self.params['AWG_uncond_CORPSE_total_duration']/2)

            # waiting time before RF pulse
            # This waiting time only gives an overall phase shift, so is not
            # important for the BSM. 
            # But for the state tomogrpahy I keep track of
            # it. include 15 periods of waiting time.
            self.seq.add_pulse('wait_before_RF-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start =  -self.params['AWG_uncond_CORPSE_total_duration']/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 43055, amplitude = 0)
            last = 'wait_before_RF-'+n
            
            self.seq.add_pulse('RF_pulse-2-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_Hadamardpulse_duration']/2, 
                    start_reference = last, 
                    link_start_to='end', 
                    duration = int(self.params['AWG_RF_Hadamardpulse_duration']),
                    amplitude = self.params['AWG_RF_Hadamardpulse_amp'],
                    shape ='cosine',
                    phase = 180,
                    frequency = self.params['AWG_RF_Hadamardpulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-2-'+n   

            # waiting time before second RF Hadamard pulse
            # For the tomography we need the phase of this readout to match
            # that of last RF pulse.
            # Since I want to read out the state of the Nitrogen right after
            # the second Hadamard, the time in between should be
            # exactly 2pi*m, otherwise I read out something random. 
            self.seq.add_pulse('wait_before_rotation_RF-'+n, channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_Hadamardpulse_duration']/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = 77499 , amplitude = 0)
            last = 'wait_before_rotation_RF-'+n
            
            # Basis rotation for the population now in ms=-1
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = -int(l)/2, start_reference = last, 
                    link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n


            # Before read-out, my electron needs to be in ms=-1 again. Now
            # send it to ms=0.
            # self.seq.add_IQmod_pulse(name = 'Pi2_pulse-2-'+n,
            #         channel = (chan_mwI,chan_mwQ),
            #         element = 'spin_control-'+n,
            #         start = 50, 
            #         duration = 0, ## int(self.params['AWG_Pi2_MW_pulse_duration']),
            #         amplitude = 0, ## self.params['AWG_Pi2_MW_pulse_amp'],
            #         frequency = self.params['AWG_Pi2_MW_pulse_ssbmod_frq'],
            #         start_reference = '',#last,
            #         link_start_to = 'end')
            # last = 'Pi2_pulse-2-'+n+'-I'   


            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5523, 
                    amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            
            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

        return
## end Class UncondHadamard

class CORPSEtest(mbi.MBIMeasurement):
    
    def sequence(self):

        # measure in three bases: X,Y,Z
        # measure along X axis by rotating around -y
        # measure along Y axis by rotating around x.
        names = ['Z', 'X', 'Y']
        lengths = [0, self.params['AWG_p2pulse_duration'], self.params['AWG_p2pulse_duration']]
        phases = [0, 0, -90.] 
        amplitudes = [0, self.params['AWG_p2pulse_amp'],self.params['AWG_p2pulse_amp']]
        
        for n,l,p,a in zip(names, lengths, phases, amplitudes):
            self._MBI_seq_element(el_name='MBI_pulse-'+n,
                    jump_target='spin_control-'+n,
                    goto_target='MBI_pulse-'+n+'-0')
          
            if n == names[-1]:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True, goto_target = 'MBI_pulse-'+names[0]+'-0')
            else:
                self.seq.add_element(name = 'spin_control-'+n, 
                    trigger_wait = True)
            
            # Do a CORPSE pulse instead of the shelving pulse to test it
            last = self._CORPSE_unconditional_pi(pulse_name = 'shelving_pulse-'+n,
                    el_name='spin_control-'+n, 
                    mod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'],
                    link_to='')

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
            
            # # Implement a Hadamard gate by XSqrtY. Do the Y first
            # # This is a rotation pi/2 around the Y axis, so we need a phase 180
            # # Now, turn it into a pi/2 pulse, around -Y. phase 0. 
            # self.seq.add_pulse('RF_pulse-1-'+n, channel=chan_RF,
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference = last, link_start_to='end', 
            #         duration = int(self.params['AWG_p2pulse_duration']),
            #         amplitude = self.params['AWG_p2pulse_amp'],
            #         shape ='cosine',
            #         phase = 0,
            #         frequency = self.params['AWG_p2pulse_frq'],
            #         envelope='erf',
            #         envelope_risetime=200)
            # last = 'RF_pulse-1-'+n

            # # waiting time between RF pulse. 
            # self.seq.add_pulse('wait_between_RF', channel = chan_RF, 
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference=last, link_start_to='end', 
            #         duration = 2000, amplitude = 0)
            # last = 'wait_between_RF'

            # Now do the rotation around the X axis. This is a phase -90
            # self.seq.add_pulse('RF_pulse-2-'+n, channel=chan_RF,
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference = last, link_start_to='end', 
            #         duration = int(self.params['AWG_pipulse_duration']),
            #         amplitude = self.params['AWG_pipulse_amplitude'],
            #         shape ='cosine',
            #         phase = -90,
            #         frequency = self.params['AWG_pipulse_frq'],
            #         envelope='erf',
            #         envelope_risetime=200)
            # last = 'RF_pulse-2-'+n

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_rotation_RF', channel = chan_RF, 
                    element = 'spin_control-'+n,
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_rotation_RF'
            
            # Basis rotation
            self.seq.add_pulse('Rotation_pulse-'+n, channel=chan_RF,
                    element = 'spin_control-'+n,
                    start = 0, start_reference = last, link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Rotation_pulse-'+n

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5000, 
                    amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            
            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

        return

def tomo(name):
    m = NMRTomography(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'bases'
    m.params['sweep_pts'] = np.arange(3)

    m.params['pts'] = 3 #This is just to trick the setup part

    m.program_AWG = True
    mbi._run(m)

def hadamard(name):
    m = NMRTomoHadamard(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    # Hadamard pulse
    m.params['N_rabi_frequency'] = 5.6e3#5.536e3
    m.params['AWG_RF_Hadamardpulse_duration'] = int(1./2/np.sqrt(2)/m.params['N_rabi_frequency']*1e9)
    m.params['AWG_RF_Hadamardpulse_amp'] = 1.
    m.params['AWG_RF_Hadamardpulse_frq'] = 7.135e6 + m.params['N_rabi_frequency']

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'bases'
    m.params['sweep_pts'] = np.arange(3)

    m.params['pts'] = 3 #This is just to trick the setup part

    m.program_AWG = True
    mbi._run(m)

def calhadamard(name):
    m = CalibrateHadamard(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)

    m.params['pts'] = 11 
    pts = m.params['pts']

    # Hadamard pulse
    m.params['N_rabi_frequencies'] = np.linspace(-1e3,1e3,pts) + 5.554e3#5.536e3
    m.params['AWG_RF_Hadamardpulse_durations'] = int(1./2/np.sqrt(2)/m.params['N_rabi_frequencies']*1e9)#np.linspace(-500,500,pts).astype(int)\
            
    m.params['AWG_RF_Hadamardpulse_amp'] = 1.
    m.params['AWG_RF_Hadamardpulse_frqs'] = 7.135e6 + m.params['N_rabi_frequencies']

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'Hadamard Pulse Duration (us)'
    m.params['sweep_pts'] = m.params['AWG_RF_Hadamardpulse_durations']/1e3

    

    m.program_AWG = True
    mbi._run(m)


def uncondpi2(name):

    m = UncondPiOver2(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)
    
    # Total CORPSE duration
    m.params['AWG_uncond_CORPSE_total_duration']= m.params['AWG_uncond_CORPSE60_duration'] \
            + m.params['AWG_uncond_CORPSE300_duration'] \
            + m.params['AWG_uncond_CORPSE420_duration'] \
            + int(20) #start delays

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'bases'
    m.params['sweep_pts'] = np.arange(3)

    m.params['pts'] = 3 #This is just to trick the setup part

    m.program_AWG = True
    mbi._run(m)

def uncondhadamard(name):

    m = UncondHadamard(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)
    
    # Hadamard pulse
    m.params['N_rabi_frequency'] = 5.6e3#5.536e3
    m.params['AWG_RF_Hadamardpulse_duration'] = int(1./2/np.sqrt(2)/m.params['N_rabi_frequency']*1e9)
    m.params['AWG_RF_Hadamardpulse_amp'] = 1.
    m.params['AWG_RF_Hadamardpulse_frq'] = 7.135e6 + m.params['N_rabi_frequency']

    # Total CORPSE duration
    m.params['AWG_uncond_CORPSE_total_duration']= m.params['AWG_uncond_CORPSE60_duration'] \
            + m.params['AWG_uncond_CORPSE300_duration'] \
            + m.params['AWG_uncond_CORPSE420_duration'] \
            + int(20) #start delays

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'bases'
    m.params['sweep_pts'] = np.arange(3)

    m.params['pts'] = 3 #This is just to trick the setup part

    m.program_AWG = True
    mbi._run(m)




def corpsetest(name):
    m = CORPSEtest(name, qt.instruments['adwin'], qt.instruments['AWG'])
    mbi._prepare(m)


    m.params['AWG_pipulse_amplitude'] = 1.
    m.params['AWG_pipulse_duration'] = 86e3
    m.params['AWG_pipulse_frq'] = 7.1383e6

    # rotation pulse
    m.params['AWG_p2pulse_duration'] = 43e3
    m.params['AWG_p2pulse_amp'] = 1.
    m.params['AWG_p2pulse_frq'] = 7.1383e6

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'bases'
    m.params['sweep_pts'] = np.arange(3)

    m.params['pts'] = 3 #This is just to trick the setup part

    m.program_AWG = True
    mbi._run(m)
