import numpy as np
import ctypes
import inspect
import time

from qt import instruments

from measurement.AWG_HW_sequencer_v2 import Sequence
import measurement.PQ_measurement_generator_v2 as pqm

from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq


# constants
MW_pulse_mod_risetime = 20


exaom = instruments['MatisseAOM']
aaom = instruments['NewfocusAOM']
wm = instruments['wavemeter']

Measurement = pqm.PQ_measurement

class SSROMeasurement(Measurement):
    def __init__(self, name, **kw):
        Measurement.__init__(self, name, mclass='SSRO_preselect')

        self.par_ms_state = '0'
        
        self.par_binsize = 17
        self.par_sp_duration = int(300e3)
        self.par_sp_filter_duration = int(50e3)     # last part of sp pulse: condition on 0 photons to increase initialization fidelity
        self.par_cr_duration = int(100e3)
        self.par_ro_duration = int(50e3)

        self.par_ro_axis = pqm.time_axis+pqm.repetition_axis

        self.par_sp_Ex_amplitude = 0.71
        self.par_sp_A_amplitude = 0.
        
        self.par_cr_Ex_amplitude =  0.75
        self.par_cr_A_amplitude =  0.3

        self.par_ro_Ex_amplitude =  0.71 
        self.par_ro_A_amplitude = 0.

        self.par_ro_spinfilter_duration = int(50e3)
        self.par_ro_spinfilter = 0

        self.par_cr_threshold = 0 #20 #thresholding cr is no longer necc. since we do conditional repump
       
#        self.ins_setup = instruments['TheSetup']
        self.ins_awg = instruments['AWG']
        self.ins_pq = instruments['HH_400']      

        self.par_ADwin_CR_threshold    = 15 # will goto init if CR counts smaller
        self.par_ADwin_probe_duration  = 10
        self.par_ADwin_probe_threshold = 15 # will be happy to continue if larger
        self.par_ADwin_AOM_duration    = 10
        self.fpar_ADwin_AOM_voltage    = 3
    
    def setup(self, reps, *arg, **kw):
        self.reset()
        self.par_reps = reps

        if not self.generate_sequence(*arg, **kw):
            return False

#        self.ins_setup.set_AOMonADwin(True)
        self.set_qtlab_counter_instrument(self.ins_pq)
        self.set_sequence_instrument(self.ins_awg)

        self.set_sweep(name = 'no_sweep', count = 1, incr_mode = pqm.EV_auto, 
                reset_mode = pqm.EV_auto, incr = 0, start = 0)

        self.set_repetitions(count=reps, incr_mode=pqm.EV_auto, 
                reset_mode=pqm.EV_auto)

        self.set_loop_order(pqm.loop_repeat_sweeps) 
        self.set_section_increment_event(pqm.EV_sync)
#        self.set_sequence_reset_event(pqm.EV_MA_1+pqm.EV_auto)
        self.set_sequence_reset_event(pqm.EV_auto)
        self.set_abort_condition(pqm.EV_MA_3)

        self.set_conditional_mode(True)

        #BaseResolution = float(self.ins_pq.get_BaseResolution())
        BaseResolution = float(self.ins_pq.get_ResolutionPS())
        self.par_binsize_us = 2**self.par_binsize*BaseResolution*1e-6

        self.add_section(name = 'SpinPumpkin', 
                event_type     = pqm.EV_start, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_sp_duration/BaseResolution/2**self.par_binsize*1000),
                mode           = pqm.time_axis,
                threshold_mode = 0,
                reset_mode     = pqm.EV_none)
        
        self.add_section(name = 'SpinFilter', 
                event_type     = pqm.EV_start, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_sp_filter_duration/BaseResolution/2**self.par_binsize*1000),
                mode           = pqm.time_axis,
                threshold_max  = 0,
                threshold_mode = 2,
                reset_mode     = pqm.EV_none)
        
        self.add_section(name = 'SpinRO', 
                event_type     = pqm.EV_start, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_ro_duration/BaseResolution/2**self.par_binsize*1000),
                mode           = self.par_ro_axis,
                threshold_mode = 0,
                reset_mode     = pqm.EV_none)
        
        if self.par_ro_spinfilter:
            self.add_section(name = 'ROSpinFilter', 
                event_type     = pqm.EV_start, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_ro_spinfilter_duration/BaseResolution/2**self.par_binsize*1000),
                mode           = pqm.time_axis,
                threshold_max  = 0,
                threshold_mode = 2,
                reset_mode     = pqm.EV_none)

        
        self.add_section(name = 'ChargeRO', 
                event_type     = pqm.EV_start, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_cr_duration/BaseResolution/2**self.par_binsize*1000), 
                mode           = pqm.repetition_axis,
                threshold_min  = self.par_cr_threshold,
                threshold_mode = 1,
                reset_mode     = pqm.EV_none)

        self.add_section(name = 'MultiChannelTest', 
                event_type     = pqm.EV_MA_1, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_cr_duration/BaseResolution/2**self.par_binsize*1000), 
                mode           = pqm.repetition_axis+pqm.link_to_previous,
                threshold_min  = 0,
                threshold_mode = 0,
                reset_mode     = pqm.EV_none)

        self.add_ADwin_code('conditional repump', 
                'D:\\measuring\\user\\ADwin_Codes\\conditional_repump.tb9', 9, 
                [[78,1], [26,7],[27,self.par_ADwin_AOM_duration],[28,self.par_ADwin_probe_duration],
                [75, self.par_ADwin_CR_threshold],[76,self.par_ADwin_probe_threshold]], 
                [[30,self.fpar_ADwin_AOM_voltage]], [1], [])

        self.add_ADwin_save_par('repump events',70)
        self.add_ADwin_save_par('below CR threshold events',71)
        self.add_ADwin_save_par('total repetitions',72)

        self.initialize()

        return True
    
    def analyze(self, ms=0, **kw):
        return

    def measure(self, **kw):
        self.start()
        self.save(files=[inspect.stack()[0][1], ])


    def generate_sequence(self, do_program=True):
        seq = Sequence(self.name)

        # vars for the channel names
#        chan_mwpulsemod = 'MW_pulsemod'
#        chan_mwI = 'MW_Imod'
#        chan_mwQ = 'MW_Qmod'
        chan_green = 'AOM_Green'
        chan_hhsync = 'HH_sync' # historically PH_start
        chan_hh_ma1 = 'HH_MA1'  # historically PH_sync
        chan_exlaser = 'AOM_Matisse'
        chan_alaser = 'AOM_Newfocus'
        chan_adwinsync = 'ADwin_sync'

        awgcfg.configure_sequence(seq, 'basics', 'hydraharp', #'mw', 
                ssro={ chan_alaser: {'high': self.par_cr_A_amplitude } } )
        
#        commonseq.phsync_element(seq)
#        seq.add_element('hhsync')
#        seq.add_pulse('hhsync1', chan_hhsync, 'hhsync', start = 0, 
#            duration = 50)
#        seq.add_pulse('hhsync2', chan_hhsync, 'hhsync', start = 100, 
#            duration = 50)
#        seq.add_pulse('hhsync3', chan_hhsync, 'hhsync', start = 200, 
#            duration = 50)
        
        
        seq.add_element('initialize')
        seq.add_pulse('green_initialize', chan_green, 'initialize', start = 0, duration = 10000)
                
        seq.add_element('preselect', event_jump_target = 'wait_for_ADwin')
        
        seq.add_pulse('cr1', chan_exlaser, 'preselect', duration = self.par_cr_duration, 
                amplitude = self.par_cr_Ex_amplitude)

        seq.add_pulse('cr1_2', chan_alaser, 'preselect', start = 0, duration = 0, 
                amplitude = self.par_cr_A_amplitude, start_reference = 'cr1', link_start_to = 'start', 
                duration_reference = 'cr1', link_duration_to = 'duration')

        seq.add_pulse('ADwin_ionization_probe', chan_adwinsync, 'preselect', start = 0, 
            duration = -20000, start_reference = 'cr1', link_start_to = 'start', 
            duration_reference = 'cr1', link_duration_to = 'duration')

        seq.add_element('readout', goto_target = 'readout', event_jump_target = 'wait_for_ADwin')

#        seq.add_pulse('Syncronize', chan_hh_ma1, 'readout', start = 0, 
#            duration = 500)

        seq.add_pulse('wait_a', chan_exlaser, 'readout', start = 1000, duration = 500, 
                amplitude = 0)

        seq.add_pulse('sp', chan_exlaser, 'readout', start = 0, duration = self.par_sp_duration, 
                amplitude = self.par_sp_Ex_amplitude, start_reference = 'wait_a', link_start_to = 'end')

        seq.add_pulse('sp_2', chan_alaser, 'readout', start = 0, duration = 0, 
                amplitude = self.par_sp_A_amplitude, start_reference = 'sp', link_start_to = 'start', 
                duration_reference = 'sp', link_duration_to = 'duration')

        seq.add_pulse('ro',  chan_exlaser, 'readout', start = 6000, duration = self.par_ro_duration, 
            amplitude = self.par_ro_Ex_amplitude, start_reference = 'sp', link_start_to = 'end')
            
        seq.add_pulse('ro_2',  chan_alaser, 'readout', start = 0, duration = 0, 
            amplitude = self.par_ro_A_amplitude,  start_reference = 'ro',  link_start_to = 'start', 
            duration_reference = 'ro',  link_duration_to = 'duration')

        seq.add_pulse('cr2', chan_exlaser, 'readout', start = 1000, duration = self.par_cr_duration, 
                amplitude = self.par_cr_Ex_amplitude, start_reference = 'ro', link_start_to = 'end')

        seq.add_pulse('cr2_2', chan_alaser, 'readout', start = 0, duration = 0, 
                amplitude = self.par_cr_A_amplitude, start_reference = 'cr2', link_start_to = 'start', 
                duration_reference = 'cr2', link_duration_to = 'duration')

        seq.add_pulse('Multichanneltest1', chan_hh_ma1, 'readout', start = 5000, 
            duration = 50, start_reference = 'cr2', link_start_to = 'start')
        
        seq.add_pulse('Multichanneltest2', chan_hh_ma1, 'readout', start = 25000, 
            duration = 50, start_reference = 'cr2', link_start_to = 'start')
        
        seq.add_pulse('Multichanneltest3', chan_hh_ma1, 'readout', start = 45000, 
            duration = 50, start_reference = 'cr2', link_start_to = 'start')
        

        seq.add_pulse('start_sp',  chan_hhsync, 'readout', start = -100, duration = 50, 
                start_reference = 'sp',  link_start_to = 'start')

        seq.add_pulse('start_sp_filter', chan_hhsync, 'readout', 
                start=-100-self.par_sp_filter_duration, duration = 50,
                start_reference='sp', link_start_to='end')

        if self.par_ro_spinfilter:
            seq.add_pulse('start_ro_sp_filter', chan_hhsync, 'readout', 
                    start=-100-self.par_ro_spinfilter_duration, duration = 50,
                    start_reference='ro', link_start_to='end')

        seq.add_pulse('start_ro',  chan_hhsync, 'readout', start = -100, duration = 50, 
                start_reference = 'ro',  link_start_to = 'start')
        seq.add_pulse('start_cr2', chan_hhsync, 'readout', start = -100, duration = 50, 
                start_reference = 'cr2', link_start_to = 'start')

        seq.add_pulse('ADwin_ionization_probe', chan_adwinsync, 'readout', start = 0, 
            duration = -20000, start_reference = 'cr2', link_start_to = 'start', 
            duration_reference = 'cr2', link_duration_to = 'duration')


        seq.add_element('wait_for_ADwin', trigger_wait = True, goto_target = 'readout')
        seq.add_pulse('probe1', chan_exlaser, 'wait_for_ADwin', start=0, duration = 1000, 
                amplitude = self.par_cr_Ex_amplitude)
        seq.add_pulse('probe2', chan_alaser, 'wait_for_ADwin', start=-125, duration = 1000, 
                amplitude = self.par_cr_A_amplitude)

        seq.set_instrument(self.ins_awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        self.ins_awg.set_event_jump_timing('SYNC')
        
        return True

class SpinPumpkinMeasurement(SSROMeasurement):
    def __init__(self, name):
        SSROMeasurement.__init__(self, name)

        self.mclass='SpinPumpkin'

        self.par_ro_axis = pqm.time_axis
        self.par_binsize = 14
        self.par_sp_duration = int(200e3)
        self.par_cr_duration = int(100e3)
        self.par_ro_duration = int(200e3)
        self.par_ro_spinfilter = 0


def spin_pumpkin_both(name, reps=10000):
    
    m = SpinPumpkinMeasurement(name)

    wm.set_active_channel(1)
    m.par_Ex_frq = wm.get_frequency(1)*1e3-470400
    wm.set_active_channel(2)
    m.par_A_frq = wm.get_frequency(2)*1e3-470400
    
    aamplitude = aaom.power_to_voltage(3e-3)

    m.par_cr_Ex_amplitude = exaom.power_to_voltage(3e-3)
    m.par_cr_A_amplitude = aamplitude
    
    # first, relaxation under A excitation
    m.par_ms_state = '1'
    m.par_sp_Ex_amplitude = exaom.power_to_voltage(1e-3)
    m.par_sp_A_amplitude = 0.
    m.par_ro_Ex_amplitude = 0.
    m.par_ro_A_amplitude = aamplitude
    
    if m.setup(int(reps), do_program=True):
        m.measure()

    # then relaxtion under Ex readout
    m.par_ms_state = '1'
    m.dataset_idx += 1
    m.par_sp_Ex_amplitude = 0.
    m.par_sp_A_amplitude = aamplitude
    m.par_ro_Ex_amplitude = exaom.power_to_voltage(1e-3)
    m.par_ro_A_amplitude = 0.
    
    if m.setup(int(reps), do_program=True):
       m.measure()

def spin_pumpkin_vs_power(name, reps=10000):
    
    m = SpinPumpkinMeasurement(name)
    m.par_cr_Ex_amplitude = 0.93
    m.par_cr_A_amplitude = 0.32

    amplitudes = linspace(0.5, 1., 11)

    for i,a in enumerate(amplitudes):
        m.par_ms_state = '0'
        m.par_sp_Ex_amplitude = 0.
        m.par_sp_A_amplitude = 0.32
        m.par_ro_Ex_amplitude = a
        m.par_ro_A_amplitude = 0.

        if m.setup(int(reps), do_program=True):
            m.measure()

        m.dataset_idx += 1


def ssro(name, reps=10000, do_ms0=True, do_ms1=True):
    debug_index = 0
    wm = instruments['wavemeter']
    debug_index += 1
    #print(debug_index)    
    m = SSROMeasurement(name)

    wm.set_active_channel(1)
    m.par_Ex_frq = wm.get_frequency(1)*1e3-470400
    wm.set_active_channel(3)
    m.par_A_frq = wm.get_frequency(2)*1e3-470400

    debug_index += 1
    #print(debug_index)    
    a_cr_amplitude = aaom.power_to_voltage(5e-9)
    a_sp_amplitude = aaom.power_to_voltage(5e-9)

    debug_index += 1
    #print(debug_index)    
    m.par_ro_Ex_amplitude = exaom.power_to_voltage(5e-9)
    m.par_ro_A_amplitude = 0.
    
    m.par_sp_duration = int(300e3)
    m.par_cr_duration = int(100e3)
    m.par_ro_duration = int(300e3)
    
    debug_index += 1
    #print(debug_index)    
    m.par_binsize = 17
    m.par_cr_Ex_amplitude = exaom.power_to_voltage(5e-9)
    m.par_cr_A_amplitude = a_cr_amplitude
    m.par_ADwin_CR_threshold    = 15 # will goto init if CR counts smaller
    m.par_ADwin_probe_duration  = 10
    m.par_ADwin_probe_threshold = 15 # will be happy to continue if larger
    m.par_ADwin_AOM_duration    = 10
    
    debug_index += 1
    #print(debug_index)    
    # first, ms=0 
    if do_ms0:
        debug_index += 1
        #print(debug_index)    
        m.par_ms_state = '0'
        m.par_sp_Ex_amplitude = 0.
        m.par_sp_A_amplitude = a_sp_amplitude
        
        if m.setup(int(reps), do_program=True):
            debug_index += 1
            #print(debug_index)    
            time.sleep(1)
            m.measure()
            debug_index += 1
            #print(debug_index)    

    # then ms=1
    if do_ms1:
        m.par_ms_state = '1'
        m.dataset_idx += 1
        m.par_sp_Ex_amplitude = exaom.power_to_voltage(5e-9)
        m.par_sp_A_amplitude = 0.
        
        if m.setup(int(reps), do_program=True):
            time.sleep(1)
            m.measure()

def ssro_vs_examplitude(name, reps=1000):
    wm = instruments['wavemeter']

    m = SSROMeasurement(name)

    wm.set_active_channel(1)
    m.par_Ex_frq = wm.get_frequency(1)*1e3-470400
    wm.set_active_channel(2)
    m.par_A_frq = wm.get_frequency(2)*1e3-470400

#    m.par_ro_Ex_amplitude = 0.77
    m.par_ro_Ex_amplitude = 0.77
    m.par_ro_A_amplitude = 0.
    aamplitude = aaom.power_to_voltage(5e-9) 
    
    m.par_sp_duration = int(300e3)
    m.par_cr_duration = int(100e3)
    m.par_ro_duration = int(50e3)
    
    m.par_binsize = 17

    m.par_cr_Ex_amplitude = exaom.power_to_voltage(5e-9)
    m.par_cr_A_amplitude = aamplitude

    for p in linspace(1, 10, 5)*1e-9:
        m.par_ro_Ex_power = p
        a = instruments['MatisseAOM'].power_to_voltage(p)
        m.par_ro_Ex_amplitude = a
        
        # first, ms=0 
        m.par_ms_state = '0'
        m.par_sp_Ex_amplitude = 0.
        m.par_sp_A_amplitude = aamplitude
        
        if m.setup(int(reps), do_program=True):
            time.sleep(1)
            m.measure()

        # then ms=1
        m.par_ms_state = '1'
        m.dataset_idx += 1
        m.par_sp_Ex_amplitude = exaom.power_to_voltage(5e-9)
        m.par_sp_A_amplitude = 0. # 0.35
        
        if m.setup(int(reps), do_program=True):
            time.sleep(1)
            m.measure()

        m.dataset_idx += 1

def ssro_vs_Aamplitude(name, reps=1000):
    wm = instruments['wavemeter']

    m = SSROMeasurement(name)

    wm.set_active_channel(1)
    m.par_Ex_frq = wm.get_frequency(1)*1e3-470400
    wm.set_active_channel(3)
    m.par_A_frq = wm.get_frequency(2)*1e3-470400

#    m.par_ro_Ex_amplitude = 0.77
    m.par_ro_Ex_amplitude = instruments['MatisseAOM'].power_to_voltage(5e-9)
    m.par_ro_A_amplitude = 0.
    aamplitude = aaom.power_to_voltage(5e-9) 
    
    m.par_sp_duration = int(300e3)
    m.par_cr_duration = int(100e3)
    m.par_ro_duration = int(50e3)
    
    m.par_binsize = 17

    m.par_cr_Ex_amplitude = exaom.power_to_voltage(5e-9)
    m.par_cr_A_amplitude = aamplitude
    
    self.fpar_ADwin_AOM_voltage    = instruments['GreenAOM'].power_to_voltage(200e-6)
    for p in linspace(1, 8, 7)*1e-9:
        m.par_ro_Ex_power = p
        a = instruments['NewfocusAOM'].power_to_voltage(p)
        
        
        # first, ms=0 
        m.par_ms_state = '0'
        m.par_sp_Ex_amplitude = 0.
        m.par_sp_A_amplitude = a 
        if m.setup(int(reps), do_program=True):
            time.sleep(1)
            m.measure()

        # then ms=1
        m.par_ms_state = '1'
        m.dataset_idx += 1
        m.par_sp_Ex_amplitude = exaom.power_to_voltage(50e-9)
        m.par_sp_A_amplitude = 0. # 0.35
        
        if m.setup(int(reps), do_program=True):
            time.sleep(1)
            m.measure()

        m.dataset_idx += 1

def ssro_vs_MWfreq(name, reps=1000):
    wm = instruments['wavemeter']
    ins_smb = qt.instruments['SMB100']

    m = SSROMeasurement(name)

    start_f =   5.#2.83
    stop_f  =   5.2#2.92
    steps   =   10
    MW_power =  15

    ins_smb.set_iq('off')
    ins_smb.set_pulm('off')
    ins_smb.set_power(MW_power)
    ins_smb.set_status('on')
    qt.msleep(0.1)
    
    wm.set_active_channel(1)
    m.par_Ex_frq = wm.get_frequency(1)*1e3-470400
    wm.set_active_channel(2)
    m.par_A_frq = wm.get_frequency(2)*1e3-470400

    m.par_sp_duration = int(300e3)
    m.par_cr_duration = int(100e3)
    m.par_ro_duration = int(50e3)
    
    m.par_binsize = 17
    
    aamplitude = aaom.power_to_voltage(5e-9) 
    examplitude = exaom.power_to_voltage(5e-9)
    
    m.par_cr_Ex_amplitude = examplitude
    m.par_cr_A_amplitude = aamplitude

    f_list = linspace(start_f*1e9, stop_f*1e9, steps)

    if not (m.setup(int(reps), do_program=True)):
        ins_smb.set_status('off')
        return False

    for MW_freq in f_list:

        ins_smb.set_frequency(MW_freq)
        m.par_MW_freq = MW_freq
        qt.msleep(0.01)
        # first and only, ms=0 
        m.par_ms_state = '0'
        m.par_sp_Ex_amplitude = 0.
        m.par_sp_A_amplitude = aamplitude
        m.par_ro_Ex_amplitude = examplitude

        time.sleep(1)
        m.measure()
   
        if not (m.setup(int(reps),do_program=False)):
            ins_smb.set_status('off')
            return False
        m.dataset_idx += 1

    ins_smb.set_status('off')

if __name__ == "__main__":
    #print 'please use the functions'
    #ssro('SIL10',1000)
    #spin_pumpkin_both('SIL3_pumping')
    #ssro_vs_Aamplitude('SIL10_fidvsApower_with_green')
    ssro_vs_MWfreq('SIL10_ssro_vs_MWfreq',500)


    #ssro_vs_examplitude('SIL10_vs_Ex_power')
    #spin_pumpkin_vs_power('SIL3calib')
    #ssro_vs_examplitude('SIL2fidvspower')
    #m=SSROMeasurement('test')
    #m.setup(1)
    #m.generate_sequence('test')
