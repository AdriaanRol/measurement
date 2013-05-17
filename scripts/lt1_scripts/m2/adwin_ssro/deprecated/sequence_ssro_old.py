import numpy as np

import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.AWG_HW_sequencer_v2 import Sequence

chan_mw_pm = 'MW_pulsemod'
chan_mwI = 'MW_Imod'
chan_mwQ = 'MW_Qmod'
chan_RF  = 'RF'
chan_adwin_sync = 'adwin_sync'

class SequenceSSROMeasurement(m2.AdwinControlledMeasurement):

    mprefix = 'SequenceSSRO'
    max_SP_bins =    500
    max_RO_dim = 1000000


    def __init__(self, name, adwin, awg):
        m2.AdwinControlledMeasurement.__init__(self, name, adwin)
        
        self.awg = awg
        self.seq = Sequence(name)
        self.adwin_process = 'spincontrol' # FIXME this is more general
        self.params['measurement_type'] = self.mprefix
    
    def autoconfig(self):
        self.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
        self.params['send_AWG_start'] = 1
        self.params['wait_for_AWG_done'] = 0
        self.params['wait_after_pulse_duration'] = 1
        self.params['green_laser_DAC_channel'] = \
                self.adwin.get_dac_channels()['green_aom']
        self.params['Ex_laser_DAC_channel'] = \
                self.adwin.get_dac_channels()['velocity2_aom']
        self.params['A_laser_DAC_channel'] = \
                self.adwin.get_dac_channels()['velocity1_aom']

    def setup(self):
        self.mwsrc.set_iq('on')
        self.mwsrc.set_pulm('on')
        self.mwsrc.set_frequency(self.params['mw_frq'])
        self.mwsrc.set_power(self.params['mw_power'])
        self.mwsrc.set_status('on')

        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)
        self.green_aom.set_cur_controller('ADWIN')
        self.E_aom.set_cur_controller('ADWIN')
        self.A_aom.set_cur_controller('ADWIN')
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)

    def sequence(self):
        pass
    
    def generate_sequence(self, do_program=True):
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_mw_pm = 'MW_pulsemod'

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

    def run(self):
        self.awg.set_runmode('SEQ')
        self.awg.start()

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

        self.adwin_process_params['Ex_CR_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_CR_amplitude'])
        self.adwin_process_params['A_CR_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_CR_amplitude'])
        self.adwin_process_params['Ex_SP_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_SP_amplitude'])
        self.adwin_process_params['A_SP_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_SP_amplitude'])
        self.adwin_process_params['Ex_RO_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_RO_amplitude'])
        self.adwin_process_params['A_RO_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_RO_amplitude'])
        self.adwin_process_params['green_repump_voltage'] = \
                self.green_aom.power_to_voltage(
                        self.params['green_repump_amplitude'])
        self.adwin_process_params['green_off_voltage'] = 0.0

        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort')
        
        CR_counts = 0
        while self.adwin_process_running():
            
            if self.keystroke('abort') != '':
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
            
            reps_completed = self.adwin_var('completed_reps')
            CR_counts = self.adwin_var('total_CR_counts') - CR_counts
            cts = self.adwin_var('last_CR_counts')
            trh = self.adwin_var('CR_threshold')
            
            print('completed %s / %s readout repetitions, %s CR counts/s' % \
                    (reps_completed, self.params['RO_repetitions'], CR_counts))
            print('threshold: %s cts, last CR check: %s cts' % (trh, cts))
            
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['RO_repetitions']))

    
    def finish(self):
        m2.AdwinControlledMeasurement.finish(self)

        self.awg.stop()
        self.awg.set_runmode('CONT')

        self.mwsrc.set_status('off')
        self.mwsrc.set_iq('off')
        self.mwsrc.set_pulm('off')

        qt.instruments['counters'].set_is_running(True)
        self.green_aom.set_power(20e-6)
        self.E_aom.set_power(0)
        self.A_aom.set_power(0)

    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', 1),
                    ('CR_after', 1),
                    ('SP_hist', 1),
                    ('RO_data', self.params['pts'] * self.params['RO_duration']),
                    ('statistics', 10),
                    ('ssro_results', self.params['pts'] * self.params['RO_duration']),
                    'completed_reps',
                    'total_CR_counts',
                    'CR_threshold',
                    'last_CR_counts' ])
        
### class SequenceSSROMeasurement

class DarkESR(SequenceSSROMeasurement):

    mprefix = 'DarkESR'

    def setup(self):
        SequenceSSROMeasurement.setup(self)

        self.params['sequence_wait_time'] = \
                int(np.ceil(self.params['pulse_length']/1e3)+10)
        self.params['RO_repetitions'] = \
                int(self.params['repetitions'] * self.params['pts'])
        self.params['sweep_length'] = self.params['pts']
    
    def sequence(self):
        
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_mw_pm = 'MW_pulsemod'

        # sweep the modulation freq
        for i, f in enumerate(
                np.linspace(self.params['ssbmod_frq_start'],
                    self.params['ssbmod_frq_stop'], 
                    self.params['pts']) ):

            ###################################################################
            ename = 'desrseq%d' % i
            kw = {} if i < self.params['pts']-1 \
                    else {'goto_target': 'desrseq0'}
            
            self.seq.add_element(ename, trigger_wait = True, **kw)

            self.seq.add_pulse('wait', channel = chan_mw_pm, element = ename,
                    start = 0, duration = 5000, amplitude = 0)
            
            self.seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod', 'MW_Qmod'),
                    element = ename, 
                    start = 0, 
                    duration = self.params['pulse_length'], 
                    start_reference = 'wait', 
                    link_start_to = 'end', 
                    frequency = f,
                    amplitude = self.params['ssbmod_amplitude'])

            self.seq.clone_channel(chan_mw_pm, chan_mwI, ename,
                    start = -self.params['MW_pulse_mod_risetime'],
                    duration = 2 * self.params['MW_pulse_mod_risetime'], 
                    link_start_to = 'start', 
                    link_duration_to = 'duration', 
                    amplitude = 2.0)
            ###################################################################

### class DarkESR

class ElectronRabi(SequenceSSROMeasurement):

    mprefix = 'ElectronRabi'
    
    def setup(self):
        SequenceSSROMeasurement.setup(self)

        self.params['sequence_wait_time'] = \
                int(np.ceil(self.params['pulse_length_stop']/1e3)+10)
        self.params['RO_repetitions'] = \
                int(self.params['repetitions'] * self.params['pts'])
        self.params['sweep_length'] = self.params['pts']

    def sequence(self):    
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_mw_pm = 'MW_pulsemod'

        for i, l in enumerate(
                np.linspace(self.params['pulse_length_start'],
                    self.params['pulse_length_stop'], 
                    self.params['pts']) ):

            ###################################################################
            ename = 'rabi_seq%d' % i
            kw = {} if i < self.params['pts']-1 \
                    else {'goto_target': 'rabi_seq0'}
            
            self.seq.add_element(ename, trigger_wait = True, **kw)

            self.seq.add_pulse('wait', channel = chan_mw_pm, element = ename,
                    start = 0, duration = 5000, amplitude = 0)

            self.seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod','MW_Qmod'),
                    element = ename, 
                    start = 0, 
                    duration = l, 
                    start_reference = 'wait', 
                    link_start_to = 'end', 
                    frequency = self.params['ssbmod_frq'],
                    amplitude = self.params['ssbmod_amplitude'])

            self.seq.clone_channel(chan_mw_pm, chan_mwI, ename,
                    start = -self.params['MW_pulse_mod_risetime'],
                    duration = 2 * self.params['MW_pulse_mod_risetime'], 
                    link_start_to = 'start', 
                    link_duration_to = 'duration', 
                    amplitude = 2.0)

            ###################################################################

class RFHeating(SequenceSSROMeasurement):

    mprefix = 'RFHeating'
    
    def setup(self):
        SequenceSSROMeasurement.setup(self)

        self.params['sequence_wait_time'] = \
                int(np.ceil(self.params['pulse_element_length']*\
                self.params['pulse_repetitions'][-1])/1e3+11)
        self.params['RO_repetitions'] = \
                int(self.params['repetitions'] * self.params['pts'])
        self.params['sweep_length'] = self.params['pts']

    def sequence(self):
        for i, r in enumerate(self.params['pulse_repetitions']):

            ###################################################################
            ename = 'rabi_seq%d' % i
            kw = {} if i < self.params['pts']-1 \
                    else {'goto_target': 'rabi_seq0'}
            
            self.seq.add_element(ename, trigger_wait = True)

            self.seq.add_pulse('wait', chan_RF, ename,
                    start=0, duration=1000, amplitude=0,)

            self.seq.add_element(ename+'-pt2', 
                    repetitions=self.params['pulse_repetitions'][i], **kw)
           
            self.seq.add_pulse('RF', channel = chan_RF,
                    element = ename+'-pt2',
                    start = 0, 
                    # start_reference = 'wait',
                    # link_start_to = 'end', 
                    duration = self.params['pulse_element_length'],
                    amplitude = self.params['RF_amp'],
                    shape = 'sine', 
                    frequency = self.params['RF_frq'],
                    envelope='erf',
                    envelope_risetime=200,
                    )

            ###################################################################

def _prepare(m):
    m.mwsrc = qt.instruments['SMB100']
    m.green_aom = qt.instruments['GreenAOM']
    m.E_aom = qt.instruments['Velocity2AOM']
    m.A_aom = qt.instruments['Velocity1AOM']
    m.autoconfig()

    #m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    #m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])


def _run(m):
    m.setup()
    m.generate_sequence(do_program=True)
    m.run()
    m.save()
    m.save_params()
    m.save_stack(depth=3)
    m.save_cfg_files()
    m.finish()

def darkesr(name):
    m = DarkESR(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)
    
    m.params['mw_frq'] = 2.8e9
    m.params['ssbmod_frq_start'] = 40e6
    m.params['ssbmod_frq_stop'] = 48e6
    m.params['pts'] = 161
    m.params['mw_power'] = 20
    m.params['pulse_length'] = 1500 
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.01
    m.params['MW_pulse_mod_risetime'] = 2
    m.params['RO_duration'] = 25
    m.params['Ex_RO_amplitude'] = 2e-9
    m.params['CR_preselect'] = 30
    m.params['CR_probe'] = 30

    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 10e-9
    m.params['Ex_SP_amplitude'] = 0.

    m.params['sweep_name'] = 'MW frq (GHz)'
    m.params['sweep_pts'] = (np.linspace(m.params['ssbmod_frq_start'],
                    m.params['ssbmod_frq_stop'], m.params['pts']) + m.params['mw_frq'])*1e-9

    _run(m)

### def darkesr

def rabi(name):
    m = ElectronRabi(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    m.params['mw_frq'] = 2.8e9
    m.params['ssbmod_frq'] = 17.17e6
    m.params['pts'] = 21
    m.params['mw_power'] = 20
    m.params['pulse_length_start'] = 10
    m.params['pulse_length_stop'] = 10 + 5000
    m.params['repetitions'] = 1000
    m.params['ssbmod_amplitude'] = 0.007
    m.params['MW_pulse_mod_risetime'] = 3
    m.params['RO_duration'] = 12
    m.params['CR_preselect'] = 30
    m.params['CR_probe'] = 30
    m.params['Ex_RO_amplitude'] = 5e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse length (ns)'
    m.params['sweep_pts'] = np.linspace(m.params['pulse_length_start'],
                    m.params['pulse_length_stop'], m.params['pts'])
  
    _run(m)

### def rabi

def rfheating(name):
    m = RFHeating(name, qt.instruments['adwin'], qt.instruments['AWG'])
    _prepare(m)

    m.params['mw_frq'] = 2.82e9
    m.params['mw_power'] = -2
    
    pts = 21
    m.params['pts'] = pts
    m.params['pulse_element_length'] = 50000
    m.params['pulse_repetitions'] = np.arange(pts, dtype=int) + 1
    m.params['repetitions'] = 1000
    m.params['RO_duration'] = 15
    m.params['CR_preselect'] = 40
    m.params['CR_probe'] = 40
    m.params['Ex_RO_amplitude'] = 5e-9
    
    m.params['RF_amp'] = 1
    m.params['RF_frq'] = 4e6

    # for the autoanalysis
    m.params['sweep_name'] = 'RF duration (us)'
    m.params['sweep_pts'] = m.params['pulse_repetitions'] * 50

    _run(m)

### def rabi


### SCRIPT
# darkesr('SIL9_leftmostlines')
# rabi('SIL9_findpi')self._countrate['cntr1']
