import numpy as np
import ctypes
import inspect

from qt import instruments

from measurement.AWG_HW_sequencer import Sequence
import measurement.PQ_measurement_generator as pqm

import analysis.ssro

# constants
MW_pulse_mod_risetime = 20


Measurement = pqm.PQ_measurement

class SSROMeasurement(Measurement):
    def __init__(self, name, **kw):
        Measurement.__init__(self, name, mclass='SSRO')

        self.par_ms_state = '0'
        
        self.par_binsize = 15
        self.par_sp_duration = int(300e3)
        self.par_cr_duration = int(100e3)
        self.par_ro_duration = int(50e3)

        self.par_ro_axis = pqm.time_axis+pqm.repetition_axis

        self.par_sp_Ex_amplitude = 0.71
        self.par_sp_A_amplitude = 0.
        
        self.par_cr_Ex_amplitude = 0.75
        self.par_cr_A_amplitude = 0.3

        self.par_ro_Ex_amplitude = 0.71 
        self.par_ro_A_amplitude = 0.

        self.par_cr_threshold = 50
       
        self.ins_setup = instruments['TheSetup']
        self.ins_awg = instruments['AWG']
        self.ins_pq = instruments['PH_300']      

    def setup(self, reps, *arg, **kw):
        self.par_reps = reps

        if not self.generate_sequence(*arg, **kw):
            return False

        self.ins_setup.set_AOMonADwin(False)
        self.set_qtlab_counter_instrument(self.ins_pq)
        self.set_sequence_instrument(self.ins_awg)

        self.set_sweep(name = 'no_sweep', count = 1, incr_mode = pqm.EV_auto, 
                reset_mode = pqm.EV_auto, incr = 0, start = 0)

        self.set_repetitions(count=reps, incr_mode=pqm.EV_auto, 
                reset_mode=pqm.EV_auto)

        self.set_loop_order(pqm.loop_repeat_sweeps) 
        self.set_section_increment_event(pqm.EV_start)
        self.set_sequence_reset_event(pqm.EV_auto)
        self.set_abort_condition(pqm.EV_MA_3)

        self.set_conditional_mode(True)

        BaseResolution = float(self.ins_pq.get_BaseResolution())
        self.par_binsize_us = 2**self.par_binsize*BaseResolution*1e-6

        self.add_section(name = 'SpinPumpkin', 
                event_type     = pqm.EV_stop, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_sp_duration/BaseResolution/2**self.par_binsize*1000),
                mode           = pqm.time_axis,
                threshold_mode = 0,
                reset_mode     = pqm.EV_none)

        self.add_section(name = 'SpinRO', 
                event_type     = pqm.EV_stop, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_ro_duration/BaseResolution/2**self.par_binsize*1000),
                mode           = self.par_ro_axis,
                threshold_mode = 0,
                reset_mode     = pqm.EV_none)
        
        self.add_section(name = 'ChargeRO', 
                event_type     = pqm.EV_stop, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_cr_duration/BaseResolution/2**self.par_binsize*1000), 
                mode           = pqm.repetition_axis,
                threshold_min  = self.par_cr_threshold,
                threshold_mode = 1,
                reset_mode     = pqm.EV_none)

        self.initialize()

        return True
    
    def analyze(self, ms=0, **kw):
        return

    def measure(self, **kw):
        self.start()
        self.save(files=[inspect.stack()[0][1], ])


    def generate_sequence(self, do_program=True):
        seq = Sequence(self.name)
        
        # Light
        seq.add_channel('GreenLaser', 'ch2m1', cable_delay = 615, high = 1.0)
        seq.add_channel('ReadoutLaser', 'ch2',   high = 1.0, low = 0.0, 
                cable_delay = 665)
        seq.add_channel('PumpingLaser', 'ch1m2',   high = 0.8, low = 0.0, 
                cable_delay = 540)

        # PH data aquisition
        seq.add_channel('PH_start', 'ch2m2', cable_delay = 0)
        seq.add_channel('PH_sync', 'ch3m1', cable_delay = 0, high = 2.0)

        
        #######################################################################
        # creates two start pulses to compensate 
        # for PH bug (misses first 2 start pulses)

        ename = 'sync' 
        seq.add_element(ename)
        
        seq.add_pulse('PH_sync1', 'PH_start', ename, duration = 50)
        seq.add_pulse('PH_sync2', 'PH_start', ename, start = 500, duration = 50, 
                start_reference = 'PH_sync1', link_start_to = 'end')
        seq.add_pulse('PH_sync_wait', 'PH_start', ename, start = 500, 
                duration = 50, start_reference = 'PH_sync2', 
                link_start_to = 'end', amplitude = 0)
        #######################################################################
        
        
        seq.add_element('initialize')
        seq.add_pulse('green_initialize', 'GreenLaser', 'initialize', start = 0, duration = 10000)
        # seq.add_pulse('marker', 'PH_sync', 'initialize', start = 0, duration = 50)   
        
        
        seq.add_element('readout', goto_target = 'initialize')

        seq.add_pulse('wait_a', 'ReadoutLaser', 'readout', start =    0, duration =   500, 
                amplitude = 0)

        seq.add_pulse('sp', 'ReadoutLaser', 'readout', start = 0, duration = self.par_sp_duration, 
                amplitude = self.par_sp_Ex_amplitude, start_reference = 'wait_a', link_start_to = 'end')

        seq.add_pulse('sp_2', 'PumpingLaser', 'readout', start = 0, duration = 0, 
                amplitude = self.par_sp_A_amplitude, start_reference = 'sp', link_start_to = 'start', 
                duration_reference = 'sp', link_duration_to = 'duration')

        seq.add_pulse('ro',  'ReadoutLaser', 'readout', start = 6000, duration = self.par_ro_duration, 
            amplitude = self.par_ro_Ex_amplitude, start_reference = 'sp', link_start_to = 'end')
            
        seq.add_pulse('ro_2',  'PumpingLaser', 'readout', start = 0, duration = 0, 
            amplitude = self.par_ro_A_amplitude,  start_reference = 'ro',  link_start_to = 'start', 
            duration_reference = 'ro',  link_duration_to = 'duration')

        seq.add_pulse('cr2', 'ReadoutLaser', 'readout', start = 1000, duration = self.par_cr_duration, 
                amplitude = self.par_cr_Ex_amplitude, start_reference = 'ro', link_start_to = 'end')

        seq.add_pulse('cr2_2', 'PumpingLaser', 'readout', start = 0, duration = 0, 
                amplitude = self.par_cr_A_amplitude, start_reference = 'cr2', link_start_to = 'start', 
                duration_reference = 'cr2', link_duration_to = 'duration')

        seq.add_pulse('start_sp',  'PH_start', 'readout', start = -100, duration = 50, 
                start_reference = 'sp',  link_start_to = 'start')
        seq.add_pulse('start_ro',  'PH_start', 'readout', start = -100, duration = 50, 
                start_reference = 'ro',  link_start_to = 'start')
        seq.add_pulse('start_cr2', 'PH_start', 'readout', start = -100, duration = 50, 
                start_reference = 'cr2', link_start_to = 'start')

        seq.set_instrument(self.ins_awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        
        return True

class SpinPumpkinMeasurement(SSROMeasurement):
    def __init__(self, name):
        SSROMeasurement.__init__(self, name)

        self.mclass='SpinPumpkin'

        self.par_ro_axis = pqm.time_axis
        self.par_binsize = 14
        self.par_sp_duration = int(300e3)
        self.par_cr_duration = int(100e3)
        self.par_ro_duration = int(300e3)


def spin_pumpkin_both(name, reps=10000):
    m = SpinPumpkinMeasurement(name)
    
    m.par_cr_threshold = 50
    m.par_cr_Ex_amplitude = 0.75
    m.par_cr_A_amplitude = 0.3
    
    # first, relaxation under A excitation
    m.par_ms_state = '1'
    m.par_sp_Ex_amplitude = 0.71
    m.par_sp_A_amplitude = 0. 
    m.par_ro_Ex_amplitude = 0.
    m.par_ro_A_amplitude = 0.265
    
    if m.setup(int(reps), do_program=True):
       m.measure()

    # then relaxtion under Ex readout
    m.par_ms_state = '1'
    m.dataset_idx += 1
    m.par_sp_Ex_amplitude = 0.
    m.par_sp_A_amplitude = 0.265
    m.par_ro_Ex_amplitude = 0.71
    m.par_ro_A_amplitude = 0.
    
    if m.setup(int(reps), do_program=True):
       m.measure()


def ssro(name, reps=10000, do_ms0=True, do_ms1=True):
    m = SSROMeasurement(name)

    m.par_ro_Ex_amplitude = 0.71
    m.rar_ro_A_amplitude = 0.
    
    m.par_sp_duration = int(300e3)
    m.par_cr_duration = int(100e3)
    m.par_ro_duration = int(50e3)
    
    m.par_binsize = 15
    m.par_cr_threshold = 80

    m.par_cr_Ex_amplitude = 0.75
    m.par_cr_A_amplitude = 0.3
    
    # first, ms=0 
    if do_ms0:
        m.par_ms_state = '0'
        m.par_sp_Ex_amplitude = 0.
        m.par_sp_A_amplitude = 0.265
        
        if m.setup(int(reps), do_program=True):
           m.measure()

    # then ms=1
    if do_ms1:
        m.par_ms_state = '1'
        m.dataset_idx += 1
        m.par_sp_Ex_amplitude = 0.71
        m.par_sp_A_amplitude = 0. # 0.265
        
        if m.setup(int(reps), do_program=True):
           m.measure()


if __name__ == "__main__":
    print 'please use the functions'
    
