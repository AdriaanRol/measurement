##
# classes for nitrogen-spin manipulation after MBI
#
##

import numpy as np
import qt
import hdf5_data as h5

from measurement.lib.measurement2.adwin_ssro import mbi


class NMRSweep(mbi.MBIMeasurement):
    mprefix = 'NMR'
    
    def sequence(self):
        for i in np.arange(self.params['pts']):
           
            self._MBI_seq_element(el_name='MBI_pulse'+str(i),
                    jump_target='spin_control'+str(i),
                    goto_target='MBI_pulse'+str(i)+'-0')

            self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True)

            last = self._shelving_pulse(pulse_name='shelving_pulse_'+str(i),
                    ssbmod_frq = self.params['AWG_MBI_MW_pulse_ssbmod_frq'], 
                    el_name = 'spin_control'+str(i))
            
            self.seq.add_pulse('wait_before_RF', channel = self.chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
            
            self.seq.add_pulse('RF', channel = self.chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, 
                    start_reference = last,
                    link_start_to = 'end', 
                    duration = int(self.params['RF_pulse_len'][i]),
                    amplitude = self.params['RF_pulse_amp'][i],
                    shape = 'sine', 
                    frequency = self.params['RF_frq'][i],
                    envelope='erf',
                    envelope_risetime=200,
                    )
            
            # By varying 'wait_before_readout_reps', the total waiting time before readout can be varied 
            self.seq.add_element('wait_before_readout-'+str(i),
                    repetitions = self.params['wait_before_readout_reps'][i]) 

            self.seq.add_pulse('wait_before_readout', 
                    channel = self.chan_RF, element = 'wait_before_readout-'+str(i),
                    start = 0, duration = self.params['wait_before_readout_element'], 
                    amplitude = 0, 
                    #start_reference = 'RF', link_start_to = 'end', 
                    shape = 'rectangular')

            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control_pt2-'+str(i), goto_target = 'MBI_pulse0-0')
            else:
                self.seq.add_element(name = 'spin_control_pt2-'+str(i))

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+str(i),
                    link_to = '', #'wait_before_readout', 
                    el_name = 'spin_control_pt2-'+str(i), 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            
            self.seq.add_pulse(name='seq_done',
                    channel = self.chan_adwin_sync,
                    element = 'spin_control_pt2-'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

                   
class NMRTomoPi2(mbi.MBIMeasurement):
    
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
            
            # ############# RF Control Pulse ##########
            # # waiting time before RF pulse
            # self.seq.add_pulse('wait_before_RF', channel = self.chan_RF, 
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference=last, link_start_to='end', 
            #         duration = 2000, amplitude = 0)
            # last = 'wait_before_RF'
            # 
            # ## This is a rotation pi/2 onto the X axis, around the Y axis (phase 180)
            # self.seq.add_pulse('RF_pulse-1-'+n, channel=self.chan_RF,
            #         element = 'spin_control-'+n,
            #         start = 0, start_reference = last, link_start_to='end', 
            #         duration = int(self.params['AWG_RF_p2pulse_duration']),
            #         amplitude = self.params['AWG_RF_p2pulse_amp'],
            #         shape ='cosine',
            #         phase = 180,
            #         frequency = self.params['AWG_RF_p2pulse_frq'],
            #         envelope='erf',
            #         envelope_risetime=200)
            # last = 'RF_pulse-1-'+n
            ############# end RF Control pulse ##########

            
            ############ Tomography pulse ##########
            self.seq.add_pulse('wait_before_rotation_RF', channel = self.chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_p2pulse_duration'], 
                    start_reference=last, link_start_to='end', 
                    duration = 86110, amplitude = 0)
            last = 'wait_before_rotation_RF'
            
            # Basis rotation
            self.seq.add_pulse('Tomography_pulse-'+n, channel=self.chan_RF,
                    element = 'spin_control-'+n,
                    start =-int(l)/2, start_reference = last, link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Tomography_pulse-'+n
            ############ end Tomography pulse ##########

            ############ CORPSE pulse ##########
            #### waiting time 
            # The nitrogen phase evolves with a rate that depends on the state of the electron. 
            # For the electron in a superposition, the phase-dependent gates need to be timed 
            # such that for both electron state the nitrogen phase evolution is the same.  
            # The difference in hyperfine splitting for ms=0 and ms=-1 is 2.189e6 Hz. 
            # The waiting time should be n*2pi/2.189e6=n*2870.3ns.
            ####
            # waiting time covers Tomo part 1 + half CORPSE= ~23e3 + ~100
            
            self.seq.add_pulse('wait_before_CORPSE-'+n, channel = self.chan_RF, 
                    element = 'spin_control-'+n,
                    start = -int(l)/2,
                    start_reference =last, 
                    link_start_to='end', 
                    duration = 25833, amplitude = 0)
            last = 'wait_before_CORPSE-'+n        
            
            self.seq.add_IQmod_pulse('CORPSE420-'+n, 
                    channel = (self.chan_mwI, self.chan_mwQ),
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_uncond_CORPSE_total_duration']/2, 
                    duration = int(self.params['AWG_uncond_CORPSE420_duration']),
                    amplitude = self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE420-'+n+'-I'
           
            self.seq.add_IQmod_pulse(
                    name = 'CORPSE300-'+n, 
                    channel = (self.chan_mwI, self.chan_mwQ),
                    element = 'spin_control-'+n,
                    start = 10, 
                    duration = int(self.params['AWG_uncond_CORPSE300_duration']),
                    amplitude = -self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE300-'+n+'-I'

            self.seq.add_IQmod_pulse(
                    name = 'CORPSE60-'+n, 
                    channel = (self.chan_mwI, self.chan_mwQ),
                    element = 'spin_control-'+n,
                    start = 10, 
                    duration = int(self.params['AWG_uncond_CORPSE60_duration']),
                    amplitude = self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE60-'+n+'-I'
            ############ end CORPSE pulse ##########
            
            
            ############# Tomography pulse part 2 ##########
            # waiting time before RF pulse
            # waiting time covers half CORPSE + half Tomo part 2 = ~100 + ~23e3
            self.seq.add_pulse('wait_before_rotation_RF_2', channel = self.chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_uncond_CORPSE_total_duration']/2, 
                    start_reference=last, link_start_to='end', 
                    duration = 28703, 
                    amplitude = 0)
            last = 'wait_before_rotation_RF_2'
            
            # Basis rotation
            self.seq.add_pulse('Tomography_pulse_2-'+n, channel=self.chan_RF,
                    element = 'spin_control-'+n,
                    start =-int(l)/2, start_reference = last, link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Tomography_pulse_2-'+n
            ############ end Tomography pulse part 2 ##########   
            
            ############ Readout pulse ##########
            self.seq.add_pulse('wait_before_readout', 
                    channel = self.chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5000, 
                    amplitude = 0, 
                    start_reference = last, 
                    link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            ############ end Readout pulse ##########
       
            
            self.seq.clone_channel(self.chan_mw_pm, self.chan_mwI, 'spin_control-'+n,
                    start = -self.params['MW_pulse_mod_risetime'],
                    duration = 2 * self.params['MW_pulse_mod_risetime'], 
                    link_start_to = 'start', 
                    link_duration_to = 'duration',
                    amplitude = 2.0)

            # make sure PM is low at the beginning
            self.seq.add_pulse('delay_start', self.chan_mw_pm, 'spin_control-'+n,
                    start=-5, duration=5, amplitude=0,
                    start_reference='CORPSE420-'+n+'-I',
                    link_start_to='start')            
            
            self.seq.add_pulse(name='seq_done',
                    channel = self.chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

                    
class NMRDoubleRO(mbi.MBIMeasurement):                    
    #### The sequence for the double read out.                 
    def sequence(self):
        print 10
        for i in np.arange(self.params['pts']):
            self._MBI_seq_element(el_name='MBI_pulse-'+str(i),
                    jump_target='spin_control-'+str(i),
                    goto_target='MBI_pulse-'+str(i)+'-0')
            print 11
            ## The first sequence element after MBI. Contains nothing but an sequence done pulse. 
            self.seq.add_element(name = 'spin_control-'+str(i), 
                    trigger_wait = True)
            print 12       
            self.seq.add_pulse(name='seq_done',
                    channel = self.chan_adwin_sync,
                    element = 'spin_control-'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,)
                    #start_reference=last,
                    #link_start_to='end')
       
            print 13  
            ### Debugging: the script runs up to here, but then does not find / does not go into _N_RO_seq_element in mbi.     
            ## The second sequence element after MBI. Contains a CNOT and sequence done pulse. 
            # Goes to MBI_pulse after last element for which i = last_i

            self._N_RO_seq_element(el_name='N_RO-'+str(i),
                    goto_target='MBI_pulse-'+srt(i)+'-0',
                    iii = i,
                    last_i = self.params['pts']-1 )
            print 14
                                  
class NMRUncondTomo(mbi.MBIMeasurement):
    
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

            # #Pi over 2 pulse on the electron, to make a superposition
            # self.seq.add_IQmod_pulse(name = 'Pi2_pulse-'+n,
            #         channel = (chan_mwI,chan_mwQ),
            #         element = 'spin_control-'+n,
            #        start = 50, 
            #         duration = int(self.params['AWG_MW_hard_pi2_pulse_duration']),
            #         amplitude = self.params['AWG_shelving_pulse_amp'],
            #         frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            #         start_reference = last,
            #         link_start_to = 'end')
            # last = 'Pi2_pulse-'+n+'-I'  
                    
            ############ Tomography pulse part 1 ##########
            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_rotation_RF', channel = self.chan_RF, 
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_RF_p2pulse_duration']/2, 
                    start_reference=last, link_start_to='end', 
                    duration = 20000, amplitude = 0)
            last = 'wait_before_rotation_RF'
            
            # Basis rotation
            self.seq.add_pulse('Tomography_pulse_1-'+n, channel=self.chan_RF,
                    element = 'spin_control-'+n,
                    start =-int(l)/2, start_reference = last, link_start_to='end', 
                    duration = int(l),
                    phase = p,
                    amplitude = a,
                    shape ='cosine',
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'Tomography_pulse_1-'+n
            ############ end Tomography pulse part 1 ##########
            
            ############ CORPSE pulse ##########
            #### waiting time 
            # The nitrogen phase evolves with a rate that depends on the state of the electron. 
            # For the electron in a superposition, the phase-dependent gates need to be timed 
            # such that for both electron state the nitrogen phase evolution is the same.  
            # The difference in hyperfine splitting for ms=0 and ms=-1 is 2.189e6 Hz. 
            # The waiting time should be n*2pi/2.189e6=n*2870.3ns.
            ####
            # waiting time covers Tomo part 1 + half CORPSE= ~23e3 + ~100
            
            self.seq.add_pulse('wait_before_CORPSE-'+n, channel = self.chan_RF, 
                    element = 'spin_control-'+n,
                    start = -int(l)/2,
                    start_reference =last, 
                    link_start_to='end', 
                    duration = 25833, amplitude = 0)
            last = 'wait_before_CORPSE-'+n        
            
            self.seq.add_IQmod_pulse('CORPSE420-'+n, 
                    channel = (self.chan_mwI, self.chan_mwQ),
                    element = 'spin_control-'+n,
                    start = -self.params['AWG_uncond_CORPSE_total_duration']/2, 
                    duration = 0,#int(self.params['AWG_uncond_CORPSE420_duration']),
                    amplitude = 0,#self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE420-'+n+'-I'
           
            self.seq.add_IQmod_pulse(
                    name = 'CORPSE300-'+n, 
                    channel = (self.chan_mwI, self.chan_mwQ),
                    element = 'spin_control-'+n,
                    start = 10, 
                    duration = 0,#int(self.params['AWG_uncond_CORPSE300_duration']),
                    amplitude = 0,#-self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE300-'+n+'-I'

            self.seq.add_IQmod_pulse(
                    name = 'CORPSE60-'+n, 
                    channel = (self.chan_mwI, self.chan_mwQ),
                    element = 'spin_control-'+n,
                    start = 10, 
                    duration = 0,#int(self.params['AWG_uncond_CORPSE60_duration']),
                    amplitude = 0,#self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE60-'+n+'-I'
            ############ end CORPSE pulse ##########
            
 
            ############# Tomography pulse part 2 ##########
            # # waiting time before RF pulse
            # # waiting time covers half CORPSE + half Tomo part 2 = ~100 + ~23e3
            # self.seq.add_pulse('wait_before_rotation_RF', channel = self.chan_RF, 
            #         element = 'spin_control-'+n,
            #         start = -self.params['AWG_uncond_CORPSE_total_duration']/2, 
            #         start_reference=last, link_start_to='end', 
            #         duration = 25833, amplitude = 0)
            # last = 'wait_before_rotation_RF'
            
            # # Basis rotation
            # self.seq.add_pulse('Tomography_pulse_2-'+n, channel=self.chan_RF,
            #         element = 'spin_control-'+n,
            #         start =-int(l)/2, start_reference = last, link_start_to='end', 
            #         duration = int(l),
            #         phase = p,
            #         amplitude = a,
            #         shape ='cosine',
            #         frequency = self.params['AWG_RF_p2pulse_frq'],
            #         envelope='erf',
            #         envelope_risetime=200)
            # last = 'Tomography_pulse_2-'+n
            # ############ end Tomography pulse part 2 ##########
             

            ############ Readout pulse ##########
            self.seq.add_pulse('wait_before_readout', 
                    channel = self.chan_RF, element = 'spin_control-'+n,
                    start = 0, duration = 5000, 
                    amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+n,
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control-'+n, 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
            ############ end Readout pulse ##########
 
 
 
            self.seq.add_pulse(name='seq_done',
                    channel = self.chan_adwin_sync,
                    element = 'spin_control-'+n,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')

                    