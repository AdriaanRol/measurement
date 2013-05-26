
class MBIMeasurement(sequence.SequenceSSRO):
    mprefix = 'MBIMeasurement'        

    def __init__(self, name, adwin, awg):
        sequence.SequenceSSRO.__init__(self, name)
        
        self.adwin_process = 'MBI'

    
    def _MBI_seq_element(self, el_name, jump_target, goto_target):
        # wait_for_adwin_time = self.params['MBI_duration']*1000 + \
        #        self.params['wait_time_before_MBI_pulse'] - \
        #        self.params['MBI_pulse_len'] + 3000
        for i in range(self.params['MBI_steps']):
            name = el_name + '-' + str(i)
            jmp = jump_target if (i == self.params['MBI_steps']-1) \
                    else (el_name + '-' + str(i+1))

            self.seq.add_element(name = name,
                trigger_wait = True, 
                event_jump_target = jmp, 
                goto_target = goto_target)

            self.seq.add_pulse('wait', 
                channel = chan_RF, 
                element=name,
                start=0, 
                duration = self.params['AWG_wait_duration_before_MBI_MW_pulse'], 
                amplitude = 0)
            
            self.seq.add_IQmod_pulse(name='MBI_pulse', channel=(chan_mwI,chan_mwQ),
                element = name,
                start=0, 
                duration = self.params['AWG_MBI_MW_pulse_duration'],
                amplitude = self.params['AWG_MBI_MW_pulse_amp'], 
                frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
                start_reference='wait', 
                link_start_to='end')
            
            self.seq.clone_channel(chan_mw_pm, chan_mwI, name,
                start = -MW_pulse_mod_risetime,
                duration = 2 * MW_pulse_mod_risetime, 
                link_start_to = 'start', 
                link_duration_to = 'duration', 
                amplitude = 2.0)

            self.seq.add_pulse('MBI_done_trigger', 
                chan_adwin_sync, 
                element = name,
                duration = AWG_to_adwin_ttl_trigger_duration \
                        + self.params['AWG_wait_for_adwin_MBI_duration'][i], 
                amplitude = 2,
                start = 0,
                start_reference = 'MBI_pulse-I',
                link_start_to = 'end')

    def _shelving_pulse(self, el_name, pulse_name, ssbmod_frq):

        self.seq.add_pulse('wait_before'+pulse_name, channel = chan_RF, 
                element = el_name, 
                start = 0, 
                duration = self.params['AWG_wait_duration_before_shelving_pulse'], 
                amplitude = 0)
        
        self.seq.add_IQmod_pulse(name = pulse_name, 
                channel=(chan_mwI,chan_mwQ),
                element = el_name,
                start=0, 
                duration = self.params['AWG_shelving_pulse_duration'],
                amplitude = self.params['AWG_shelving_pulse_amp'], 
                frequency = ssbmod_frq,
                start_reference = 'wait_before'+pulse_name, 
                link_start_to='end')
       
        self.seq.clone_channel(chan_mw_pm, chan_mwI, el_name,
                start = -MW_pulse_mod_risetime,
                duration = 2 * MW_pulse_mod_risetime, 
                link_start_to = 'start', 
                link_duration_to = 'duration',
                amplitude = 2.0)

        self.seq.add_pulse('wait_after'+pulse_name, 
                channel = chan_RF, element = el_name, start = 0, 
                duration = 15, amplitude = 0, start_reference=pulse_name+'-I',
                link_start_to = 'end')
        
        last='wait_after'+pulse_name
        
        return last 

    def _CORPSE_unconditional_pi(self, el_name, pulse_name, link_to, start_delay, mod_frq):
        self.seq.add_IQmod_pulse(
                name = pulse_name + '-CORPSE420', 
                channel = (chan_mwI, chan_mwQ),
                element = el_name,
                start = start_delay, 
                duration = self.params['AWG_uncond_CORPSE420_duration'],
                amplitude = self.params['AWG_uncond_CORPSE_amp'], 
                frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                start_reference = link_to,
                link_start_to = 'end')
        
        self.seq.add_IQmod_pulse(
                name = pulse_name + '-CORPSE300', 
                channel = (chan_mwI, chan_mwQ),
                element = el_name,
                start = 10, 
                duration = self.params['AWG_uncond_CORPSE300_duration'],
                amplitude = -self.params['AWG_uncond_CORPSE_amp'], 
                frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                start_reference = pulse_name + '-CORPSE420-I',
                link_start_to='end')

        self.seq.add_IQmod_pulse(
                name = pulse_name + '-CORPSE60', 
                channel = (chan_mwI, chan_mwQ),
                element = el_name,
                start = 10, 
                duration = self.params['AWG_uncond_CORPSE60_duration'],
                amplitude = self.params['AWG_uncond_CORPSE_amp'], 
                frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                start_reference = pulse_name + '-CORPSE300-I',
                link_start_to='end')

        return pulse_name + '-CORPSE60-I'


    def _readout_pulse(self, el_name, pulse_name, link_to, ssbmod_frq):

        self.seq.add_IQmod_pulse(name = pulse_name,
                channel = (chan_mwI,chan_mwQ),
                element = el_name,
                start = 0, 
                duration = self.params['AWG_RO_MW_pulse_duration'],
                amplitude = self.params['AWG_RO_MW_pulse_amp'],
                frequency = ssbmod_frq,
                start_reference = link_to, 
                link_start_to = 'end')
       
        self.seq.clone_channel(chan_mw_pm, chan_mwI, el_name,
                start = -MW_pulse_mod_risetime,
                duration = 2 * MW_pulse_mod_risetime, 
                link_start_to = 'start', 
                link_duration_to = 'duration',
                amplitude = 2.0)
        
        last = pulse_name+'-I'
        
        return last


    def generate_sequence(self, do_program=True):
        awgcfg.configure_sequence(self.seq, 'adwin', 'mw', 'rf')

        self.sequence()
        
        self.seq.set_instrument(self.awg)
        self.seq.set_clock(1e9)
        self.seq.set_send_waveforms(do_program)
        self.seq.set_send_sequence(True)
        self.seq.set_program_channels(True)
        self.seq.set_start_sequence(False)
        self.seq.force_HW_sequencing(True)
        self.seq.send_sequence()

    def setup(self):
        # SequenceSSROMeasurement.setup(self)
        sequence.SequenceSSRO.setup(self)

        
        self.params['sweep_length'] = self.params['pts']
        self.params['repetitions'] = \
                self.params['nr_of_ROsequences'] * \
                self.params['pts'] * \
                self.params['reps_per_ROsequence']

        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)

        self.params['Ex_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.E_aom.get_pri_channel()]
        self.params['A_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.A_aom.get_pri_channel()]
        self.params['green_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.green_aom.get_pri_channel()]
    
    def run(self):
        
        # FIXME split up such that we can inherit
        
        self.awg.set_runmode('SEQ')
        self.awg.start()

        qt.msleep(10)

        while self.awg.get_state() != 'Waiting for trigger':
            print 'Waiting for AWG...'
            qt.msleep(1)
        
        # get adwin params
        for key,_val in adwins_cfg.config['adwin_lt1_processes']\
                [self.adwin_process]['params_long']:
                    try:
                        self.adwin_process_params[key] = self.params[key]
                    except:
                        logging.error("Cannot set adwin process variable '%s'" \
                                % key)
                        return False
        
        self.adwin_process_params['green_repump_voltage'] = \
                self.green_aom.power_to_voltage(
                        self.params['green_repump_amplitude'])
        
        self.adwin_process_params['green_off_voltage'] = 0.0        
        
        self.adwin_process_params['Ex_CR_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_CR_amplitude'])
        
        self.adwin_process_params['A_CR_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_CR_amplitude'])
        
        self.adwin_process_params['Ex_SP_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_SP_amplitude'])
        
        self.adwin_process_params['Ex_MBI_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_MBI_amplitude'])

        # FIXME still pretty ugly
        # this is actually tremendously ugly, but if we try to load a process
        # then no other process must be running
        for i in range(10):
            physical_adwin.Stop_Process(i+1)
            qt.msleep(0.1)
        
        qt.msleep(1)
        self.adwin.load_MBI()
        qt.msleep(1)
        
        length = self.params['nr_of_ROsequences']
        
        physical_adwin.Set_Data_Long(
                self.params['A_SP_durations'], 28, 1, length)
        physical_adwin.Set_Data_Long(
                self.params['E_RO_durations'], 29, 1, length)
        # physical_adwin.Set_Data_Float(
        #         self.params['A_SP_voltages'], 30, 1, length)
        # physical_adwin.Set_Data_Float(
        #         self.params['E_RO_voltages'], 31, 1, length)
        physical_adwin.Set_Data_Float(
                self.A_aom.power_to_voltage(self.params['A_SP_amplitudes']), 30, 1, length)
        physical_adwin.Set_Data_Float(
                self.E_aom.power_to_voltage(self.params['E_RO_amplitudes']), 31, 1, length)
        physical_adwin.Set_Data_Long(
                self.params['send_AWG_start'], 32, 1, length)
        physical_adwin.Set_Data_Long(
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
                    ('ssro_results', reps), ] )
        return

### class MBIMeasurement
class MBITest(MBIMeasurement):
    mprefix = 'MBITest'

    def sequence(self):

        for i in np.arange(self.params['pts']):
            
            self._MBI_seq_element(el_name='MBI_pulse'+str(i),
                    jump_target='spin_control'+str(i),
                    goto_target='MBI_pulse'+str(i))
            
            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True, goto_target = 'MBI_pulse0')
            else:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True)

            self.seq.add_pulse(name='wait',
                    channel = chan_mwI,
                    element = 'spin_control'+str(i),
                    amplitude = 0,
                    duration = 1000,
                    start = 0)

            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control'+str(i),
                    duration = AWG_to_adwin_ttl_trigger_duration,
                    amplitude = 2,
                    start = 0,
                    start_reference='wait',
                    link_start_to='end')

        return
    
### class MBITest



class CORPSETest(MBIMeasurement):
    mprefix = 'MBICORPSETest'

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

            # waiting time before RF pulse
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, #start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
            
            # # This is a rotation pi.# around the Y axis, so we need a phase 180
            self.seq.add_pulse('RF_pulse-1-'+str(i), channel=chan_RF,
                    element = 'spin_control'+str(i),
                    start = 0, start_reference = last, link_start_to='end', 
                    duration = int(self.params['AWG_RF_p2pulse_duration']),
                    amplitude = self.params['AWG_RF_p2pulse_amp'],
                    shape ='cosine',
                    phase = 180,
                    frequency = self.params['AWG_RF_p2pulse_frq'],
                    envelope='erf',
                    envelope_risetime=200)
            last = 'RF_pulse-1-'+str(i)


            self.seq.add_pulse('wait_before_RO', channel=chan_RF,
                    element = 'spin_control'+str(i),
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 50,
                    amplitude = 0)
            last = 'wait_before_RO'

            self.seq.add_IQmod_pulse('CORPSE420-'+str(i), 
                    channel = (chan_mwI, chan_mwQ),
                    element = 'spin_control'+str(i),
                    start = 10, 
                    duration = int(self.params['AWG_uncond_CORPSE420_durations'][i]),
                    amplitude = self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE420-'+str(i)+'-I'
        
            self.seq.add_IQmod_pulse(
                    name = 'CORPSE300-'+str(i), 
                    channel = (chan_mwI, chan_mwQ),
                    element = 'spin_control'+str(i),
                    start = 10, 
                    duration = int(self.params['AWG_uncond_CORPSE300_durations'][i]),
                    amplitude = -self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE300-'+str(i)+'-I'

            self.seq.add_IQmod_pulse(
                    name = 'CORPSE60-'+str(i), 
                    channel = (chan_mwI, chan_mwQ),
                    element = 'spin_control'+str(i),
                    start = 10, 
                    duration = int(self.params['AWG_uncond_CORPSE60_durations'][i]),
                    amplitude = self.params['AWG_uncond_CORPSE_amp'], 
                    frequency = self.params['AWG_uncond_CORPSE_mod_frq'],
                    start_reference = last,
                    link_start_to='end')
            last = 'CORPSE60-'+str(i)+'-I'

            # for j in range(self.params['MW_pulse_multiplicity']):
            #     self.seq.add_IQmod_pulse(name = 'RO_pulse-'+str(j),
            #             channel = (chan_mwI,chan_mwQ),
            #             element = 'spin_control'+str(i),
            #             start = self.params['MW_pulse_delay'], 
            #             duration = 10,#int(self.params['AWG_RO_MW_pulse_durations'][i]),
            #             amplitude = 0,#self.params['AWG_RO_MW_pulse_amps'][i],
            #             frequency = self.params['AWG_RO_MW_pulse_ssbmod_frqs'][i],
            #             start_reference = last,
            #             link_start_to = 'end')
            #     last = 'RO_pulse-'+str(j)+'-I'

            self.seq.clone_channel(chan_mw_pm, chan_mwI, 'spin_control'+str(i),
                    start = -MW_pulse_mod_risetime,
                    duration = 2 * MW_pulse_mod_risetime, 
                    link_start_to = 'start', 
                    link_duration_to = 'duration',
                    amplitude = 2.0)

            # make sure PM is low at the beginning
            self.seq.add_pulse('delay_start', chan_mw_pm, 'spin_control'+str(i),
                    start=-5, duration=5, amplitude=0,
                    start_reference = last,#'RO_pulse-0-I',
                    link_start_to='start')

            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference= last,#'RO_pulse-'+str(j)+'-I',
                    link_start_to='end')
            
### class CORPSETest

class ElectronRamsey(MBIMeasurement):
    mprefix = 'MBIElectronRamsey'

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

            self.seq.add_pulse('wait_before_RO', channel=chan_RF,
                    element = 'spin_control'+str(i),
                    start = 0, # start_reference=last, link_start_to='end', 
                    duration = 500,
                    amplitude = 0)
            last = 'wait_before_RO'

            j = 0
            self.seq.add_IQmod_pulse(name = 'RO_pulse-'+str(j),
                    channel = (chan_mwI,chan_mwQ),
                    element = 'spin_control'+str(i),
                    start = 0, 
                    duration = int(self.params['AWG_pi2-1_MW_pulse_duration']),
                    amplitude = self.params['AWG_pi2-1_MW_pulse_amp'],
                    frequency = self.params['AWG_pi2-1_MW_pulse_ssbmod_frq'],
                    start_reference = last,
                    link_start_to = 'end')
            last = 'RO_pulse-'+str(j)+'-I'

            self.seq.add_pulse('ramsey_delay', channel=chan_RF,
                    element = 'spin_control'+str(i),
                    start = -int(self.params['AWG_pi2-1_MW_pulse_duration'])/2, 
                    start_reference=last, 
                    link_start_to='end', 
                    duration = int(self.params['AWG_interpulse_delays'][i]),
                    amplitude = 0)
            last = 'ramsey_delay'
 
            j = 1
            self.seq.add_IQmod_pulse(name = 'RO_pulse-'+str(j),
                    channel = (chan_mwI,chan_mwQ),
                    element = 'spin_control'+str(i),
                    start = -int(self.params['AWG_pi2-2_MW_pulse_duration'])/2, 
                    duration = int(self.params['AWG_pi2-2_MW_pulse_duration']),
                    amplitude = self.params['AWG_pi2-2_MW_pulse_amp'],
                    frequency = self.params['AWG_pi2-2_MW_pulse_ssbmod_frq'],
                    phase = self.params['AWG_pi2-2_MW_pulse_phases'][i],
                    start_reference = last,
                    link_start_to = 'end')
            last = 'RO_pulse-'+str(j)+'-I'

            self.seq.clone_channel(chan_mw_pm, chan_mwI, 'spin_control'+str(i),
                    start = -MW_pulse_mod_risetime,
                    duration = 2 * MW_pulse_mod_risetime, 
                    link_start_to = 'start', 
                    link_duration_to = 'duration',
                    amplitude = 2.0)

            # make sure PM is low at the beginning
            self.seq.add_pulse('delay_start', chan_mw_pm, 'spin_control'+str(i),
                    start=-5, duration=5, amplitude=0,
                    start_reference='RO_pulse-0-I',
                    link_start_to='start')

            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference='RO_pulse-'+str(j)+'-I',
                    link_start_to='end')

        return
            
### class ElectronRamsey

class ConditionalPrecession(MBIMeasurement):
    mprefix = 'CondPrec'

    def sequence(self):
        for i in np.arange(self.params['pts']):
            
            self._MBI_seq_element(el_name='MBI_pulse'+str(i),
                    jump_target='wait'+str(i),
                    goto_target='MBI_pulse'+str(i)+'-0')

            self.seq.add_element(name = 'wait'+str(i),
                    trigger_wait = True, 
                    repetitions = int(self.params['AWG_wait_before_RO_durations'][i]/1000.))
            
            self.seq.add_pulse('wait', channel=chan_RF,
                    element = 'wait'+str(i),
                    start = 0,
                    duration = 1000,
                    amplitude = 0)
            
            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = False, goto_target = 'MBI_pulse0-0')
            else:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = False)
                
            self.seq.add_IQmod_pulse(name = 'RO_pulse',
                    channel = (chan_mwI,chan_mwQ),
                    element = 'spin_control'+str(i),
                    start = 0, 
                    duration = self.params['AWG_RO_MW_pulse_duration'],
                    amplitude = self.params['AWG_RO_MW_pulse_amp'],
                    frequency = self.params['AWG_RO_MW_pulse_ssbmod_frq'],
                    link_start_to = 'end')
            
            self.seq.clone_channel(chan_mw_pm, chan_mwI, 'spin_control'+str(i),
                    start = -MW_pulse_mod_risetime,
                    duration = 2 * MW_pulse_mod_risetime, 
                    link_start_to = 'start', 
                    link_duration_to = 'duration',
                    amplitude = 2.0)
            
            # make sure PM is low at the beginning
            self.seq.add_pulse('delay_start', chan_mw_pm, 'spin_control'+str(i),
                    start=-5, duration=5, amplitude=0,
                    start_reference='RO_pulse-I',
                    link_start_to='start')


            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control'+str(i),
                    duration = AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference='RO_pulse-I',
                    link_start_to='end')

### class ConditionalPrecession

class PostInitDarkESR(MBIMeasurement):
    mprefix = 'PostInitDarkESR'

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

            self.seq.add_pulse('wait_before_RO', channel=chan_RF,
                    element = 'spin_control'+str(i),
                    start = 0, # start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RO'

            self.seq.add_IQmod_pulse(name = 'RO_pulse',
                channel = (chan_mwI,chan_mwQ),
                element = 'spin_control'+str(i),
                start = 0, 
                duration = self.params['RO_MW_pulse_duration'],
                amplitude = self.params['RO_MW_pulse_amp'],
                frequency = self.params['RO_MW_pulse_ssbmod_frqs'][i],
                start_reference = last,
                link_start_to = 'end')
            
            self.seq.clone_channel(chan_mw_pm, chan_mwI, 'spin_control'+str(i),
                start = -MW_pulse_mod_risetime,
                duration = 2 * MW_pulse_mod_risetime, 
                link_start_to = 'start', 
                link_duration_to = 'duration',
                amplitude = 2.0)

            # make sure PM is low at the beginning
            self.seq.add_pulse('delay_start', chan_mw_pm, 'spin_control'+str(i),
                    start=-5, duration=5, amplitude=0,
                    start_reference='RO_pulse-I',
                    link_start_to='start')

            # delay at the end
            self.seq.add_pulse('delay_end', chan_mw_pm, 'spin_control'+str(i),
                    start=0, duration=0, amplitude=0,
                    start_reference='RO_pulse-I',
                    link_start_to='end')
            
            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control'+str(i),
                    duration = AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference='RO_pulse-I',
                    link_start_to='end')

class NMRSweep(MBIMeasurement):
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
            
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
          
            self.seq.add_pulse('RF', channel = chan_RF, 
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
            
            self.seq.add_element('wait_before_readout-'+str(i),
                    repetitions = self.params['wait_before_readout_reps'][i]) 

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'wait_before_readout-'+str(i),
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
                    channel = chan_adwin_sync,
                    element = 'spin_control_pt2-'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')
        
        return

class CalibrateNPiPulse(MBIMeasurement):
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
            
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
          
            self.seq.add_pulse('RF', channel = chan_RF, 
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
            
            self.seq.add_element('wait_before_readout-'+str(i),
                    repetitions = self.params['wait_before_readout_reps'][i]) 

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'wait_before_readout-'+str(i),
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
                    channel = chan_adwin_sync,
                    element = 'spin_control_pt2-'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')
        
        return

class NMRRamsey(MBIMeasurement):
    mprefix = 'NMRRamsey'

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
            
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'
          
            self.seq.add_pulse('RF-1', channel = chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, 
                    start_reference = last,
                    link_start_to = 'end', 
                    duration = self.params['RF-1_pulse_len'],
                    amplitude = self.params['RF-1_pulse_amp'],
                    shape = 'sine', 
                    frequency = self.params['RF-1_frq'],
                    envelope='erf',
                    envelope_risetime=200,
                    )
            last = 'RF-1'
            
            self.seq.add_element('ramsey_delay-'+str(i),
                    repetitions = self.params['ramsey_delay_reps'][i])
            
            self.seq.add_pulse('ramsey_delay', channel=chan_RF,
                    element = 'ramsey_delay-'+str(i),
                    start = 0, 
                    #start_reference=last, 
                    #link_start_to='end', 
                    duration = int(self.params['AWG_interpulse_delay_element']),
                    amplitude = 0)
            last = 'ramsey_delay'

            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control_pt2-'+str(i),
                    goto_target = 'MBI_pulse0-0')
            else:
                self.seq.add_element(name = 'spin_control_pt2-'+str(i))

            self.seq.add_pulse('RF-2', channel = chan_RF, 
                    element = 'spin_control_pt2-'+str(i),
                    start = 0,  
                    duration = self.params['RF-2_pulse_len'],
                    amplitude = self.params['RF-2_pulse_amp'],
                    phase = self.params['RF-2_pulse_phases'][i],
                    shape = 'sine', 
                    frequency = self.params['RF-2_frq'],
                    envelope='erf',
                    envelope_risetime=200,
                    )
            last = 'RF-2'

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control_pt2-'+str(i),
                    start = 0, duration = 10000, amplitude = 0, 
                    start_reference = last, link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+str(i),
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control_pt2-'+str(i), 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])

            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control_pt2-'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')
        return

class NMRStepwiseRabi(MBIMeasurement):
    mprefix = 'NMRStepwiseRabi'

    def sequence(self):
        for i in np.arange(self.params['pts']):
            
            self._MBI_seq_element(el_name='MBI_pulse'+str(i),
                    jump_target='spin_control'+str(i),
                    goto_target='MBI_pulse'+str(i)+'-0')

            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control'+str(i),
                    trigger_wait = True) # , goto_target = 'MBI_pulse0-0')
            else:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True)
          
            last = self._shelving_pulse(pulse_name='shelving_pulse_'+str(i),
                    ssbmod_frq = self.params['AWG_MBI_MW_pulse_ssbmod_frq'], 
                    el_name = 'spin_control'+str(i))
            
            self.seq.add_pulse('wait_before_RF', channel = chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'

            self.seq.add_element('RF-'+str(i),
                    repetitions=self.params['RF_pulse_reps'][i])
          
            self.seq.add_pulse('RF', channel = chan_RF, 
                    element = 'RF-'+str(i),
                    start = 0, 
                    #start_reference = last,
                    #link_start_to = 'end', 
                    duration = self.params['RF_pulse_len'],
                    amplitude = self.params['RF_pulse_amp'],
                    shape = 'sine', 
                    frequency = self.params['RF_frq'],
                    envelope='erf',
                    envelope_risetime=200,
                    )

            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control_pt2-'+str(i),
                    goto_target = 'MBI_pulse0-0')
            else:
                self.seq.add_element(name = 'spin_control_pt2-'+str(i))

            self.seq.add_pulse('wait_before_readout', 
                    channel = chan_RF, element = 'spin_control_pt2-'+str(i),
                    start = 0, duration = 1000, amplitude = 0, 
                    # start_reference = 'RF', link_start_to = 'end', 
                    shape = 'rectangular')

            last = self._readout_pulse(pulse_name = 'readout_pulse_'+str(i),
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control_pt2-'+str(i), 
                    ssbmod_frq = self.params['AWG_RO_MW_pulse_ssbmod_frq'])

            self.seq.add_pulse(name='seq_done',
                    channel = chan_adwin_sync,
                    element = 'spin_control_pt2-'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference=last,
                    link_start_to='end')
        return

### module functionsnp.linspace(200,5200,pts)
def _prepare(m):
    m.mwsrc = qt.instruments['SMB100']
    m.green_aom = qt.instruments['GreenAOM']
    m.E_aom = qt.instruments['Velocity2AOM']
    m.A_aom = qt.instruments['Velocity1AOM']
    
    # calculate, convert and copy some things automatically in order to avoid
    # redundencies in the parameter specifications 
    m.autoconfig()
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO+MBI'])
    
    # # general stuff for adwin SSRO
    # m.params['Ex_SP_amplitude'] = 5e-9
    # m.params['SP_E_duration'] = 100

    # # parameters for MBI
    # m.params['MBI_steps'] = 1 # how often to retry MBI before going to CR
    # m.params['MBI_duration'] = 5 # in adwin process cycles (us)

    # # the hard pi pulse that brings us back to ms=-1 after MBI
    # m.params['AWG_wait_duration_before_shelving_pulse'] = 100
    # m.params['AWG_shelving_pulse_duration'] = 64
    # m.params['AWG_shelving_pulse_amp'] = 0.9

    # # MBI MW pulse (CNOT)
    # m.params['AWG_MBI_MW_pulse_duration'] = 2500 # in ns
    # m.params['AWG_MBI_MW_pulse_amp'] = 0.0105
    # m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = 43.862e6 - 2.189e6#  + 2.187e6
    # m.params['Ex_MBI_amplitude'] = 2e-9
    # m.params['MBI_threshold'] = 1
    
    # the waiting time has to be long enough that the adwin can jump in case
    # of success, i.e. the adwin has to react before the sequence element
    # is finished. MBI RO duration + 10 works fine, shorter can cause the
    # AWG to miss the jump trigger (if it happens once, then we're scr*wed)
    # m.params['AWG_wait_for_adwin_MBI_duration'] = np.array([25000], dtype=int)
    # m.params['AWG_wait_duration_before_MBI_MW_pulse'] = 50
    m.params['wait_for_MBI_pulse'] = 3 # deprecated, but i'm not sure if i removed all references

    # m.params['wait_after_pulse_duration'] = 10
    # m.params['wait_after_RO_pulse_duration'] = 10
 
    # # MW settings
    # m.params['mw_frq'] = 2.80e9
    # m.params['mw_power'] = 20

    # # (RO) sequence parameters
    # # everything can be set individually for each RO iteration
    # m.params['nr_of_ROsequences'] = 1
    # m.params['A_SP_durations'] = np.array([5], dtype=int)
    # m.params['E_RO_durations'] = np.array([15], dtype=int)
    # m.params['A_SP_voltages'] = np.array([m.A_aom.power_to_voltage(0e-9)])
    # m.params['E_RO_voltages'] = np.array([m.E_aom.power_to_voltage(5e-9)])
    # m.params['send_AWG_start'] = np.array([1])
    # m.params['sequence_wait_time'] = np.array([0], dtype=int)

    # # Readout pulse (= CNOT). a rabi frq. of the hyperfine splitting/sqrt(3)
    # # rotates the resonant line by pi, direct neighbor lines by 2pi
    # m.params['AWG_RO_MW_pulse_duration'] = 396
    # m.params['AWG_RO_MW_pulse_amp'] = 0.0724# F = 0.941 +/- 0.004
    # m.params['AWG_RO_MW_pulse_ssbmod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq']

    #Hard pi over 2 pulse
    m.params['AWG_Pi2_MW_pulse_duration'] = 37
    m.params['AWG_Pi2_MW_pulse_amp'] = 0.9
    m.params['AWG_Pi2_MW_pulse_ssbmod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq']+ 2.189e6/2


    # # CORPSE pulse
    # m.params['AWG_uncond_CORPSE60_duration'] = 25
    # m.params['AWG_uncond_CORPSE300_duration'] = 97
    # m.params['AWG_uncond_CORPSE420_duration'] = 137
    # m.params['AWG_uncond_CORPSE_amp'] = 0.9
    # m.params['AWG_uncond_CORPSE_mod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq']+(2.189e6/2)

    # # RF Nitrogen pi pulse
    # m.params['AWG_RF_pipulse_duration'] = 90e3
    # m.params['AWG_RF_pipulse_amp'] = 1.
    # m.params['AWG_RF_pipulse_frq'] = 7.135e6
    # # RF Nitrogen pi over 2 pulse
    # m.params['AWG_RF_p2pulse_duration'] = 45e3
    # m.params['AWG_RF_p2pulse_amp'] = 1.
    # m.params['AWG_RF_p2pulse_frq'] = 7.135e6

    m.program_AWG = True

def _run(m):
    m.setup()
    m.generate_sequence(do_program=m.program_AWG)
    m.run()
    m.save()
    m.save_params()
    m.save_stack(depth=3)
    m.save_cfg_files()
    m.finish()

def test(name='Debugging'):
    m = MBITest(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    m.params['CR_preselect'] = 0
    m.params['CR_probe'] = 0

    # parameters for MBI
    m.params['MBI_duration'] = 3 # goes to the adwin, ergo us
    m.params['AWG_MBI_MW_pulse_duration'] = 1500 # in ns
    m.params['AWG_MBI_MW_pulse_amp'] = 0.3
    m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = 34.13e6
    m.params['Ex_MBI_amplitude'] = 2e-9
    m.params['MBI_threshold'] = 0
    m.params['AWG_wait_for_adwin_MBI_duration'] = 8000
    m.params['AWG_wait_time_before_MBI_MW_pulse'] = 0
    m.params['wait_for_MBI_pulse'] = 3 # deprecated

    # (RO) sequence parameters
    m.params['nr_of_ROsequences'] = 1
    m.params['A_SP_durations'] = np.array([5], dtype=int)
    m.params['E_RO_durations'] = np.array([20], dtype=int)
    m.params['A_SP_voltages'] = np.array([m.A_aom.power_to_voltage(5e-9)])
    m.params['E_RO_voltages'] = np.array([m.E_aom.power_to_voltage(2e-9)])
    m.params['send_AWG_start'] = np.array([1])
    m.params['sequence_wait_time'] = np.array([0], dtype=int)

    # MW settings
    m.params['mw_frq'] = 2.82e9
    m.params['mw_power'] = -8

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 5 

    m.program_AWG = True

    _run(m)

def esr(name):
    m = PostInitDarkESR(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # debugging Set MW pulse amp to 0 
    m.params['AWG_MBI_MW_pulse_amp'] = 0.01
    m.params['MBI_threshold'] = 1

    # ESR pulses
    m.params['RO_MW_pulse_duration'] = 2500
    m.params['RO_MW_pulse_amp'] = 0.01

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000
    m.params['pts'] = 31
    pts=m.params['pts']
    m.params['RO_MW_pulse_ssbmod_frqs'] = np.linspace(-4e6,4e6,pts) + \
            m.params['AWG_MBI_MW_pulse_ssbmod_frq'] + 2.189e6

    # for the autoanalysis
    m.params['sweep_name'] = 'MW frq (MHz)'
    m.params['sweep_pts'] = (m.params['RO_MW_pulse_ssbmod_frqs'] +  m.params['mw_frq'])/1e6

    m.program_AWG = True

    _run(m) 
### def esr

def condprec(name):
    m = ConditionalPrecession(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # ESR pulses
    m.params['AWG_RO_MW_pulse_duration'] = 1330
    m.params['AWG_RO_MW_pulse_amp'] = 0.6
    m.params['AWG_RO_MW_pulse_ssbmod_frq'] = 36.75e6

    # (RO) sequence parameters
    m.params['A_SP_durations'] = np.array([1], dtype=int)
    m.params['A_SP_voltages'] = np.array([m.A_aom.power_to_voltage(0e-9)])
   
    # measurement settings
    m.params['reps_per_ROsequence'] = 100
    m.params['pts'] = 25
    # time for CondPrec evolution
    m.params['AWG_wait_before_RO_durations'] = (np.linspace(1, 251, 25) * 1000).astype(int)

    _run(m)
### def condprec

def erabi(name):
    m = ElectronRabi(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Rabi    
    m.params['pts'] = 12
    pts = m.params['pts']
    
    m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = 21.167e6 - 2.187e6

    m.params['AWG_RO_MW_pulse_durations'] = np.linspace(10,160,pts)
    m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * (21.167e6-2.189e6)
    m.params['MW_pulse_multiplicity'] = 1
    m.params['MW_pulse_delay'] = 2000
     
    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = m.params['AWG_RO_MW_pulse_durations']

    m.program_AWG = True
    _run(m)
### def erabi

def corpsetest(name):
    m = CORPSETest(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Rabi    
    m.params['pts'] = 6#11
    pts = m.params['pts']
    
    #m.params['AWG_MBI_MW_pulse_ssbmod_frq'] = 40.793e6  # + 2.189e6

    m.params['AWG_uncond_CORPSE420_durations'] = np.ones(pts) * m.params['AWG_uncond_CORPSE420_duration'] #np.linspace(-5,+5,pts) + 
    m.params['AWG_uncond_CORPSE300_durations'] = np.linspace(-5,+5,pts)+ m.params['AWG_uncond_CORPSE300_duration']#  #np.ones(pts) *q
    m.params['AWG_uncond_CORPSE60_durations'] = np.ones(pts) *m.params['AWG_uncond_CORPSE60_duration']#np.linspace(-5,+5,pts) + 25##np.ones(pts) * 28#  #  #

    # m.params['AWG_RO_MW_pulse_durations'] = np.ones(pts) * 135
    # m.params['AWG_RO_MW_pulse_amps'] = np.ones(pts) * 0.9
    # m.params['AWG_RO_MW_pulse_ssbmod_frqs'] = np.ones(pts) * 40.793e6
    # m.params['MW_pulse_multiplicity'] = 1
    # m.params['MW_pulse_delay'] = 2000
     
    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'duration CORPSE 300'
    m.params['sweep_pts'] =  m.params['AWG_uncond_CORPSE300_durations']

    m.program_AWG = True
    _run(m)
### def corpsetest


def eramsey(name):
    m = ElectronRamsey(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Rabi    
    m.params['pts'] = 32 
    pts = m.params['pts']
    
    m.params['AWG_pi2-1_MW_pulse_duration'] = 198
    m.params['AWG_pi2-1_MW_pulse_amp'] = 0.139
    m.params['AWG_pi2-1_MW_pulse_ssbmod_frq'] = 42.952e6 - 2.184e6

    m.params['AWG_pi2-2_MW_pulse_duration'] = 198
    m.params['AWG_pi2-2_MW_pulse_amp'] = 0.139
    m.params['AWG_pi2-2_MW_pulse_ssbmod_frq'] = 42.952e6 - 2.184e6

    m.params['AWG_interpulse_delays'] = np.linspace(200,5200,pts)
    m.params['AWG_pi2-2_MW_pulse_phases'] = np.zeros(pts) # np.linspace(0, 4*360, pts)
     
    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'Interpulse delay (ns)'
    m.params['sweep_pts'] = m.params['AWG_interpulse_delays']

    m.program_AWG = True
    _run(m)
### def eramsey

def nmr(name):
    m = NMRSweep(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Sweep
    m.params['pts'] = 25
    pts = m.params['pts']

    m.params['RF_pulse_len'] = np.ones(pts) * 90e3
    m.params['RF_pulse_amp'] = np.ones(pts) * 1.
    m.params['RF_frq'] = np.linspace(7.12e6,7.16e6,pts) #np.ones(pts) * 7.1383e6 

    m.params['wait_before_readout_reps'] = np.ones(pts)#np.linspace(1,101,pts).astype(int)*10
    m.params['wait_before_readout_element'] = int(1e3)

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'RF pulse frq (MHz)'
    m.params['sweep_pts'] = m.params['RF_frq']/1e6

    m.program_AWG = True
    _run(m)

def nmrrabi(name):
    m = NMRSweep(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Sweep
    m.params['pts'] = 24
    pts = m.params['pts']

    m.params['RF_pulse_len'] = np.linspace(1e3, 601e3, pts).astype(int)
    m.params['RF_pulse_amp'] = np.ones(pts) * 1.
    m.params['RF_frq'] = np.ones(pts) * 7.135e6 # 6.5e6 #  7.1383e6

    m.params['wait_before_readout_reps'] = np.ones(pts)
    m.params['wait_before_readout_element'] = int(1e3)

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'RF pulse length (us)'
    m.params['sweep_pts'] = m.params['RF_pulse_len']/1e3

    m.program_AWG = True
    _run(m)

def calNpipulse(name):
    m = NMRSweep(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Sweep
    m.params['pts'] = 16
    pts = m.params['pts']

    m.params['RF_pulse_len'] = np.linspace(70e3, 110e3, pts).astype(int)
    m.params['RF_pulse_amp'] = np.ones(pts) * 1.
    m.params['RF_frq'] = np.ones(pts) * 7.1383e6

    m.params['wait_before_readout_reps'] = np.ones(pts)
    m.params['wait_before_readout_element'] = int(1e3)

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'RF pulse length (us)'
    m.params['sweep_pts'] = m.params['RF_pulse_len']/1e3

    m.program_AWG = True
    _run(m)

def nmrramsey(name):
    m = NMRRamsey(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Sweep
    m.params['pts'] = 16
    pts = m.params['pts']

    m.params['RF-1_pulse_len'] = 46e3
    m.params['RF-1_pulse_amp'] = 1.
    m.params['RF-1_frq'] = 7.1383e6

    m.params['RF-2_pulse_len'] = 46e3
    m.params['RF-2_pulse_amp'] = 1.
    m.params['RF-2_frq'] = 7.1383e6

    m.params['ramsey_delay_reps'] = (np.ones(pts)*50000).astype(int)  # (np.linspace(1,24,pts)*1000).astype(int)
    m.params['AWG_interpulse_delay_element'] = int(1e3)
    m.params['RF-2_pulse_phases'] = np.linspace(0,360,pts)

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'phase (deg)' # 'Ramsey pulse delay (us)'
    m.params['sweep_pts'] = m.params['RF-2_pulse_phases'] # m.params['ramsey_delay_reps']

    m.program_AWG = True
    _run(m)

def nmr_stepwise_rabi(name):
    m = NMRStepwiseRabi(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    # Sweep
    length = 1
    m.params['pts'] = 16
    pts = m.params['pts']

    m.params['RF_pulse_len'] = length
    m.params['RF_pulse_amp'] = 1
    m.params['RF_frq'] = 7e6 # 7.1383e6
    m.params['RF_pulse_reps'] = np.arange(pts,dtype=int)*50 + 1
    
    # Readout pulse 
    m.params['AWG_RO_MW_pulse_duration'] = 397
    m.params['AWG_RO_MW_pulse_amp'] = 0.130 # F = 0.941 +/- 0.004
    m.params['AWG_RO_MW_pulse_ssbmod_frq'] = m.params['AWG_MBI_MW_pulse_ssbmod_frq']

    # measurement settings
    m.params['reps_per_ROsequence'] = 1000

    # for the autoanalysis
    m.params['sweep_name'] = 'RF pulse length (us)'
    m.params['sweep_pts'] = m.params['RF_pulse_reps']

    m.program_AWG = True
    _run(m)

### def erabi


### script
# esr('SIL9')
# erabi('SIL9_testing')
# condprec('SIL9_testing')
#

#test()
