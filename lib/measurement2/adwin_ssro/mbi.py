"""
Measurement class that uses the lt1_MBI.bas measurement program on the adwin.
(please see the corresponding flow diagram for how the adwin code works).

check the _prepare and _run functions for comments on the measurement
parameters.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
General note on parameters:

this is based on class 
measurement.lib.measurement2.measurement.MeasurementParameters
(see the measurement.lib.measurement2.measurement for how the current
measurement class works)

in short:
if m is the instance of the measurement class, it automatically has a 
parameters collection called m.params. each element in there is automatically
saved at the end of the measurement as an attribute of the main group in the
data file (save anything in the parameters you like!)

an AdwinControlledMeasurement has an additional parameter collection, in which
the params that are passed to the calling parameters of the corresponding
adwin method are stored. they are copied from m.params automatically based
on the process specs in measurement.lib.config.adwins, so just set everything
in m.params (provided the process is specified correctly in the config!)

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
The idea of the inheriting classes here is that they only specify the AWG
sequences used for a particular application of the MBI program.
the module-level functions that execute a measurement just set the particular
measurement parameters.

"""

import numpy as np
import qt
import hdf5_data as h5
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.AWG_HW_sequencer_v2 import Sequence

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import sequence

class MBIMeasurement(sequence.SequenceSSRO):
    mprefix = 'MBIMeasurement'
    adwin_process = 'MBI'
    
    def _MBI_seq_element(self, el_name, jump_target, goto_target):
        
        for i in range(self.params['MBI_steps']):
            name = el_name + '-' + str(i)
            jmp = jump_target if (i == self.params['MBI_steps']-1) \
                    else (el_name + '-' + str(i+1))

            self.seq.add_element(name = name,
                trigger_wait = True, 
                event_jump_target = jmp, 
                goto_target = goto_target)

            self.seq.add_pulse('wait', 
                channel = self.chan_RF, 
                element=name,
                start=0, 
                duration = self.params['AWG_wait_duration_before_MBI_MW_pulse'], 
                amplitude = 0)
            
            self.seq.add_IQmod_pulse(name='MBI_pulse', channel=(self.chan_mwI,self.chan_mwQ),
                element = name,
                start=0, 
                duration = self.params['AWG_MBI_MW_pulse_duration'],
                amplitude = self.params['AWG_MBI_MW_pulse_amp'], 
                frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
                start_reference='wait', 
                link_start_to='end')
            
            self.seq.clone_channel(self.chan_mw_pm, self.chan_mwI, name,
                start = -self.params['MW_pulse_mod_risetime'],
                duration = 2 * self.params['MW_pulse_mod_risetime'], 
                link_start_to = 'start', 
                link_duration_to = 'duration', 
                amplitude = 2.0)

            self.seq.add_pulse('MBI_done_trigger', 
                self.chan_adwin_sync, 
                element = name,
                duration = self.params['AWG_to_adwin_ttl_trigger_duration'] \
                        + self.params['AWG_wait_for_adwin_MBI_duration'][i], 
                amplitude = 2,
                start = 0,
                start_reference = 'MBI_pulse-I',
                link_start_to = 'end')
                
    def _N_RO_seq_element(self, el_name, goto_target, iii, last_i):
    
        ## The sequence element for the nitrogen readout. 
        print 20
        # Goes to first MBI_pulse after the last element for which i = last_i
        if iii == last_i:
            self.seq.add_element(name = el_name, 
                trigger_wait = True, goto_target = goto_target)
        else:
            self.seq.add_element(name = el_name, 
                trigger_wait = True) 
        print 21
        last = self._readout_pulse(el_name = el_name, 
                    pulse_name = 'N_RO_pulse', 
                    link_to = '', 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])
        print 22
        self.seq.add_pulse(name='seq_done',
                    channel = self.chan_adwin_sync,
                    element = el_name,
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')
               
    def _shelving_pulse(self, el_name, pulse_name, ssbmod_frq):

        self.seq.add_pulse('wait_before'+pulse_name, channel = self.chan_RF, 
                element = el_name, 
                start = 0, 
                duration = self.params['AWG_wait_duration_before_shelving_pulse'], 
                amplitude = 0)
        
        self.seq.add_IQmod_pulse(name = pulse_name, 
                channel=(self.chan_mwI,self.chan_mwQ),
                element = el_name,
                start=0, 
                duration = self.params['AWG_shelving_pulse_duration'],
                amplitude = self.params['AWG_shelving_pulse_amp'], 
                frequency = ssbmod_frq,
                start_reference = 'wait_before'+pulse_name, 
                link_start_to='end')
       
        self.seq.clone_channel(self.chan_mw_pm, self.chan_mwI, el_name,
                start = -self.params['MW_pulse_mod_risetime'],
                duration = 2 * self.params['MW_pulse_mod_risetime'], 
                link_start_to = 'start', 
                link_duration_to = 'duration',
                amplitude = 2.0)

        self.seq.add_pulse('wait_after'+pulse_name, 
                channel = self.chan_RF, element = el_name, start = 0, 
                duration = 15, amplitude = 0, start_reference=pulse_name+'-I',
                link_start_to = 'end')
        
        last='wait_after'+pulse_name
        
        return last 

    def _readout_pulse(self, el_name, pulse_name, link_to, ssbmod_frq):

        self.seq.add_IQmod_pulse(name = pulse_name,
                channel = (self.chan_mwI,self.chan_mwQ),
                element = el_name,
                start = 0, 
                duration = self.params['AWG_RO_MW_pulse_duration'],
                amplitude = self.params['AWG_RO_MW_pulse_amp'],
                frequency = ssbmod_frq,
                start_reference = link_to, 
                link_start_to = 'end')
       
        self.seq.clone_channel(self.chan_mw_pm, self.chan_mwI, el_name,
                start = -self.params['MW_pulse_mod_risetime'],
                duration = 2 * self.params['MW_pulse_mod_risetime'], 
                link_start_to = 'start', 
                link_duration_to = 'duration',
                amplitude = 2.0)
        
        last = pulse_name+'-I'
        
        return last  

    def autoconfig(self): 
        
        self.params['sweep_length'] = self.params['pts']
        self.params['repetitions'] = \
                self.params['nr_of_ROsequences'] * \
                self.params['pts'] * \
                self.params['reps_per_ROsequence']
        
        # Calling autoconfig from sequence.SequenceSSRO and thus from ssro.IntegratedSSRO 
        # after defining self.params['repetitions'], since the autoconfig of IntegratedSSRO uses this parameter.  
        sequence.SequenceSSRO.autoconfig(self)
        
        self.adwin_process_params['Ex_MBI_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['Ex_MBI_amplitude'])
                    
            
    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()
                               
        qt.msleep(1)
        self.adwin.load_MBI()
        qt.msleep(1)
                             
        length = self.params['nr_of_ROsequences']        
        self.physical_adwin.Set_Data_Long(
                self.params['A_SP_durations'], 28, 1, length)
        self.physical_adwin.Set_Data_Long(
                self.params['E_RO_durations'], 29, 1, length)
        self.physical_adwin.Set_Data_Float(
                self.A_aom.power_to_voltage(self.params['A_SP_amplitudes']), 30, 1, length)
        self.physical_adwin.Set_Data_Float(
                self.E_aom.power_to_voltage(self.params['E_RO_amplitudes']), 31, 1, length)
        self.physical_adwin.Set_Data_Long(
                self.params['send_AWG_start'], 32, 1, length)
        self.physical_adwin.Set_Data_Long(
                self.params['sequence_wait_time'], 33, 1, length)
                
        self.start_adwin_process(stop_processes=['counter'], load=False)
        qt.msleep(1)
        self.start_keystroke_monitor('abort')
        
        while self.adwin_process_running():
            
            if self.keystroke('abort') != '':
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
                     
            reps_completed = self.adwin_var('completed_reps')
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['repetitions']))
            qt.msleep(1)
                     
        try:         
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
                     
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))
                     
    
    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        sweeps = self.params['pts'] * self.params['reps_per_ROsequence']
        
        self.save_adwin_data(name,
                [   ('CR_before', sweeps),
                    ('CR_after', sweeps),
                    ('MBI_attempts', sweeps),
                    ('statistics', 10),
                    ('ssro_results', reps), 
                    ('MBI_cycles', sweeps) ] )
        return

class PostInitDarkESR(MBIMeasurement):
    mprefix = 'PostInitDarkESR'

    def autoconfig(self):
        MBIMeasurement.autoconfig(self)
        
        # for the autoanalysis
        self.params['sweep_name'] = 'MW frq (MHz)'
        self.params['sweep_pts'] = (self.params['RO_MW_pulse_ssbmod_frqs'] +  self.params['mw_frq'])/1e6
    
    def sequence(self):        
        for i in np.arange(self.params['pts']):
            
            self._MBI_seq_element(el_name='MBI_pulse'+str(i),
                    jump_target='spin_control'+str(i),
                    goto_target='MBI_pulse'+str(i)+'-0')

            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True, goto_target = 'MBI_pulse0-0')
            else:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True)

            self.seq.add_pulse('wait_before_RO', channel=self.chan_RF,
                    element = 'spin_control'+str(i),
                    start = 0, # start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RO'

            self.seq.add_IQmod_pulse(name = 'RO_pulse',
                channel = (self.chan_mwI,self.chan_mwQ),
                element = 'spin_control'+str(i),
                start = 0, 
                duration = self.params['RO_MW_pulse_duration'],
                amplitude = self.params['RO_MW_pulse_amp'],
                frequency = self.params['RO_MW_pulse_ssbmod_frqs'][i],
                start_reference = last,
                link_start_to = 'end')
            
            self.seq.clone_channel(self.chan_mw_pm, self.chan_mwI, 'spin_control'+str(i),
                start = -self.params['MW_pulse_mod_risetime'],
                duration = 2 * self.params['MW_pulse_mod_risetime'], 
                link_start_to = 'start', 
                link_duration_to = 'duration',
                amplitude = 2.0)

            # make sure PM is low at the beginning
            self.seq.add_pulse('delay_start', self.chan_mw_pm, 'spin_control'+str(i),
                    start=-5, duration=5, amplitude=0,
                    start_reference='RO_pulse-I',
                    link_start_to='start')

            # delay at the end
            self.seq.add_pulse('delay_end', self.chan_mw_pm, 'spin_control'+str(i),
                    start=0, duration=0, amplitude=0,
                    start_reference='RO_pulse-I',
                    link_start_to='end')
            
            self.seq.add_pulse(name='seq_done',
                    channel = self.chan_adwin_sync,
                    element = 'spin_control'+str(i),
                    duration = self.params['AWG_to_adwin_ttl_trigger_duration'], 
                    amplitude = 2,
                    start = 0,
                    start_reference='RO_pulse-I',
                    link_start_to='end')

