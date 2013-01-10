import numpy as np
import qt
import hdf5_data as h5
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.AWG_HW_sequencer_v2 import Sequence

import sequence_ssro as sssro

class MBIMeasurement(sssro.SequenceSSROMeasurement):

    mprefix = 'MBIMeasurement'
    
    def __init__(self, name, adwin, awg):
        sssro.SequenceSSROMeasurement.__init__(self, name, adwin, awg)
        
        self.adwin_process = 'MBI_multiple_RO'

    def _MBI_seq_element(self, el_name, ssbmod_frq, 
            jump_target, goto_target):
        
        chan_mw_pm = 'MW_pulsemod'
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'
        MW_pulse_mod_risetime = qt.cfgman['setup']['MW_pulsemod_risetime']

        wait_for_adwin_time = self.params['MBI_RO_duration']*1000 + \
                self.params['wait_time_before_MBI_pulse'] - \
                self.params['MBI_pulse_length'] + 3000

        self.seq.add_element(name=el_name,trigger_wait=True, 
                event_jump_target=jump_target, goto_target=goto_target)

        self.seq.add_pulse('wait', channel = chan_mwI, element=el_name,
                start=0, duration=self.params['wait_time_before_MBI_pulse'], 
                amplitude = 0)
        self.seq.add_IQmod_pulse(name='MBI_pulse', channel=(chan_mwI,chan_mwQ),
                element = el_name,
                start=0, duration=self.params['MBI_pulse_len'],
                amplitude=self.params['MBI_pulse_amp'], 
                frequency=ssbmod_frq,
                start_reference='wait', link_start_to='end')
        self.seq.clone_channel(chan_mw_pm, chan_mwI, el_name,
                start = -MW_pulse_mod_risetime,
                duration = 2 * MW_pulse_mod_risetime, 
                link_start_to = 'start', 
                link_duration_to = 'duration', 
                amplitude = 2.0) 
        seq.add_pulse('wait_for_ADwin', channel = chan_mwI, element = el_name,
                start = 0, duration = wait_for_adwin_time, amplitude = 0, 
                start_reference = 'MBI_pulse-I', 
                link_start_to='end', shape='rectangular')

    def _shelving_pulse(self, el_name, pulse_name, ssbmod_frq):
        chan_mw_pm = 'MW_pulsemod'
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'
        MW_pulse_mod_risetime = qt.cfgman['setup']['MW_pulsemod_risetime']
        
        seq.add_pulse('wait_before'+pulse_name, channel = chan_mwI, 
                element = el_name, start = 0, 
                duration=self.params['wait_time_before_shelving_pulse'], 
                amplitude = 0, shape = 'rectangular')
        self.seq.add_IQmod_pulse(name=pulse_name, channel=(chan_mwI,chan_mwQ),
                element = el_name,
                start=0, duration=self.params['shelving_pulse_len'],
                amplitude=self.params['shelving_pulse_amp'], 
                frequency=ssbmod_frq,
                start_reference='wait', link_start_to='end')
        self.seq.clone_channel(chan_mw_pm, chan_mwI, el_name,
                start = -MW_pulse_mod_risetime,
                duration = 2 * MW_pulse_mod_risetime, 
                link_start_to = 'start', 
                link_duration_to = 'duration',
                amplitude = 2.0)        
        seq.add_pulse('wait_after'+pulse_name, 
                channel = chan_mwI, element = el_name, start = 0, 
                duration = 15, amplitude = 0, start_reference=pulse_name+'-I',
                link_start_to = 'end', shape = 'rectangular')    
        last='wait_after'+pulse_name
        return last

    def _readout_pulse(self, el_name, pulse_name, link_to, ssbmod_frq):
        chan_mw_pm = 'MW_pulsemod'
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'
        MW_pulse_mod_risetime = qt.cfgman['setup']['MW_pulsemod_risetime']
        
        self.seq.add_IQmod_pulse(name = pulse_name,
                channel = (chan_mwI,chan_mwQ),
                element = el_name,
                start = 0, 
                duration = self.params['RO_pulse_len'],
                amplitude = self.params['RO_pulse_amp'],
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
        chan_mw_pm = 'MW_pulsemod'
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_RF  = 'RF'
        MW_pulse_mod_risetime = qt.cfgman['setup']['MW_pulsemod_risetime']

        awgcfg.configure_sequence(self.seq, 'adwin', 'mw', 'rf')

        self.sequence()
        
        self.seq.set_instrument(self.awg)
        self.seq.set_clock(1e9)
        self.seq.set_send_waveforms(do_program)
        self.seq.set_send_sequence(do_program)
        self.seq.set_program_channels(True)
        self.seq.set_start_sequence(False)
        self.seq.force_HW_sequencing(True)
        self.seq.send_sequence()

class NMRSweep(MBIMeasurement):

    mprefix = 'NMR'

    def sequence(self):
        
        for i in np.arange(self.params['pts']):
            self._MBI_seq_element(el_name='MBI_pulse'+str(i), 
                    ssbmod_frq = self.params['MBI_ssbmod_frq'], 
                    jump_target='spin_control'+str(i),
                    goto_target='MBI_pulse'+str(i))

            if i == self.params['pts'] - 1:
                seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True, goto_target = 'MBI_pulse0')
            else:
                seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True)
            
            last = self._shelving_pulse(pulse_name='shelving_pulse_'+str(i),
                    ssbmod_frq = self.params['MBI_ssbmod_frq'], 
                    el_name = 'spin_control'+str(i))
            
            seq.add_pulse('wait_before_RF', channel = chan_mwI, 
                    element = 'spin_control'+str(i),
                    start = 0, start_reference=last, link_start_to='end', 
                    duration = 2000, amplitude = 0)
            last = 'wait_before_RF'

            seq.add_pulse('RF', channel = chan_RF, 
                    element = 'spin_control'+str(i),
                    start = 0, 
                    start_reference = last,
                    link_start_to = 'end', 
                    duration = self.params['RF_pulse_len'][i],
                    amplitude = self.params['RF_pulse_amp'][i],
                    shape = 'sine', 
                    frequency = self.params['RF_frq'][i],
                    envelope='erf')
            
            seq.add_pulse('wait_before_readout', 
                    channel = chan_mwI, element = 'spin_control'+str(i),
                    start = 0, duration = 1000, amplitude = 0, 
                    start_reference = 'RF', link_start_to = 'end', 
                    shape = 'rectangular')

            self._readout_pulse(pulse_name = 'readout_pulse_'+str(i),
                    link_to = 'wait_before_readout', 
                    el_name = 'spin_control'+str(i), 
                    ssbmod_frq = self.params['RO_ssbmod_frq'])          

            
        self.params['sequence_wait_time'] = ( 
                2 * self.params['wait_time_before_MBI_pulse'] + \
                self.params['MBI_pulse_len'] + \
                self.params['RF_pulse_len'].max() + \
                self.params['wait_time_before_shelving_pulse'] + \
                self.params['shelving_pulse_len'] + 5000 ) / 1000
        
        return


### module functions
def _prepare(m):
    m.mwsrc = qt.instruments['SMB100']
    m.green_aom = qt.instruments['GreenAOM']
    m.E_aom = qt.instruments['MatisseAOM']
    m.A_aom = qt.instruments['NewfocusAOM']
    m.autoconfig()

def _run(m):
    m.setup()
    m.generate_sequence(do_program=True)
    #m.run()
    #m.save()
    #m.save_params()
    #m.save_stack(depth=3)
    #m.save_cfg_files()
    m.finish()

def nmr(name):
    m = NMRSweep(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    _run(m)


