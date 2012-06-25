import numpy as np
import ctypes
import inspect

from qt import instruments

from measurement.AWG_HW_sequencer import Sequence
import measurement.PQ_measurement_generator as pqm

setup = instruments['TheSetup']

# constants
MW_pulse_mod_risetime = 20

Measurement = pqm.PQ_measurement

class MBIMeasurement(Measurement):
    def __init__(self, name, **kw):
        Measurement.__init__(self, name, mclass='MBI')

        self.par_binsize = 14
        self.par_rro_reps = 10

        self.par_sp_duration = int(300e3) # much too long actually for SIL9
        self.par_sp_Ex_amplitude = 0.71 # 0.74
        self.par_sp_A_amplitude = 0.
        #self.sp_Ex_amplitude = 0.
        #self.sp_A_amplitude = 0.8
        
        self.par_repump_duration = 5000
        self.par_repump_Ex_amplitude = 0. # self.sp_Ex_amplitude
        self.par_repump_A_amplitude = 0.265 # self.sp_A_amplitude
        
        self.par_cr_duration = int(100e3)
        self.par_cr_threshold = 50
        self.par_cr_Ex_amplitude = 0.75
        self.par_cr_A_amplitude = 0.3

        self.par_mbi_duration = 400
        self.par_mbi_Ex_amplitude = 0.71
        self.par_mbi_A_amplitude = 0. #0.8
        self.par_mbi_threshold = 1
        
        self.par_probe_duration = 3000
        self.par_probe_Ex_amplitude = self.par_mbi_Ex_amplitude
        self.par_probe_A_amplitude = self.par_mbi_A_amplitude

        self.par_mw_power = 10
        self.par_mw_base_f = 2.830e9
        self.par_init_frequency = 16.665
        self.par_probe_frequency = self.par_init_frequency
        self.par_selective_pi = 899

        self.par_ADwin_CR_threshold    = 40 # will goto init if CR counts smaller
        self.par_ADwin_probe_duration  = 5
        self.par_ADwin_probe_threshold = 30 # will be happy to continue if larger
        self.par_ADwin_AOM_duration    = 2
       
        self.ins_setup = instruments['TheSetup']
        self.ins_awg = instruments['AWG']
        self.ins_pq = instruments['PH_300']
        self.ins_mw = instruments['SMB100']

    def setup(self, reps, *arg, **kw):
        self.par_reps = reps

        if not self.generate_sequence(*arg, **kw):
            return False

        self.ins_setup.set_AOMonADwin(True)
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

        self.add_section(name = 'MBI', 
                event_type     = pqm.EV_stop, 
                binsize        = self.par_binsize,
                offset         = 0,
                duration       = int(self.par_mbi_duration/BaseResolution/2**self.par_binsize*1000),
                mode           = pqm.repetition_axis,
                threshold_min  = self.par_mbi_threshold,
                threshold_mode = 1,
                reset_mode     = pqm.EV_none)

        for i in range(self.par_rro_reps):
            self.add_section(name = 'Probe-%d' % i, 
                    event_type     = pqm.EV_stop, 
                    binsize        = self.par_binsize,
                    offset         = 0,
                    duration       = int(self.par_probe_duration/BaseResolution/2**self.par_binsize*1000),
                    mode           = pqm.repetition_axis,
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

        self.add_MW('MW', self.ins_mw, frequency=self.par_mw_base_f,
                power=self.par_mw_power, iq_modulation='on', pulse_modulation='on')

        self.add_ADwin_code('conditional repump', 
                'D:\\Lucio\\ADwin codes\\ADwin_Gold_II\\conditional_repump.tb9', 9, 
                [[45,5], [63,4],[73,self.par_ADwin_AOM_duration],[74,self.par_ADwin_probe_duration],
                [75, self.par_ADwin_CR_threshold],[76,self.par_ADwin_probe_threshold]], 
                [[64,7]], [4], [4])

        self.add_ADwin_save_par('repump events',70)
        self.add_ADwin_save_par('below CR threshold events',71)
        self.add_ADwin_save_par('total repetitions',72)

        self.initialize()

        return True

    def measure(self, **kw):
        self.start()
        self.save(files=[inspect.stack()[0][1], ])

    def generate_sequence(self, do_program=True):
        seq = Sequence(self.name)
        
        # MWs
        seq.add_channel('MW_pulsemod', 'ch4m2', high=2.0, cable_delay = 120)
        seq.add_channel('MW_Imod', 'ch3', high=2.25, low=-2.25, 
                cable_delay = 120)
        seq.add_channel('MW_Qmod', 'ch4', high=2.25, low=-2.25, 
                cable_delay = 120)

        # Light
        seq.add_channel('GreenLaser', 'ch2m1', cable_delay = 615, high = 1.0)
        seq.add_channel('ReadoutLaser', 'ch2',   high = 1.0, low = 0.0, 
                cable_delay = 665)
        seq.add_channel('PumpingLaser', 'ch1m2',   high = 0.8, low = 0.0, 
                cable_delay = 540)

        # PH data aquisition
        seq.add_channel('PH_start', 'ch2m2', cable_delay = 0)
        seq.add_channel('PH_sync', 'ch3m1', cable_delay = 0, high = 2.0)
        seq.add_channel('ADwin_sync', 'ch3m2',   high = 2.0, low = 0.0, cable_delay = 0)

        
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
        
        
        seq.add_element('readout', goto_target = 'initialize', event_jump_target = 'wait_for_ADwin')

        seq.add_pulse('wait_a', 'ReadoutLaser', 'readout', start =    0, duration =   500, 
                amplitude = 0)

        seq.add_pulse('sp_Ex', 'ReadoutLaser', 'readout', start = 0, duration = self.par_sp_duration, 
                amplitude = self.par_sp_Ex_amplitude, start_reference = 'wait_a', link_start_to = 'end')

        seq.add_pulse('sp_A', 'PumpingLaser', 'readout', start = 0, duration = 0, 
                amplitude = self.par_sp_A_amplitude, start_reference = 'sp_Ex', link_start_to = 'start', 
                duration_reference = 'sp_Ex', link_duration_to = 'duration')

        seq.add_pulse('start_sp',  'PH_start', 'readout', start = -100, duration = 50, 
                start_reference = 'sp_Ex',  link_start_to = 'start')

        seq.add_IQmod_pulse('selective_pi_1', channel=('MW_Imod','MW_Qmod'), element='readout', 
                start = 5000, frequency=self.par_init_frequency,
                duration = self.par_selective_pi, start_reference = 'sp_Ex', 
                link_start_to = 'end', amplitude = 1.8)

        seq.add_pulse('mbi_Ex', 'ReadoutLaser', 'readout', start = 500, duration = self.par_mbi_duration, 
            amplitude = self.par_mbi_Ex_amplitude, start_reference = 'selective_pi_1-I', link_start_to = 'end')
            
        seq.add_pulse('mbi_A',  'PumpingLaser', 'readout', start = 0, duration = 0, 
            amplitude = self.par_mbi_A_amplitude,  start_reference = 'mbi_Ex',  link_start_to = 'start', 
            duration_reference = 'mbi_Ex',  link_duration_to = 'duration')

        seq.add_pulse('start_mbi',  'PH_start', 'readout', start = -100, duration = 50,
                start_reference = 'mbi_Ex',  link_start_to = 'start')

        seq.add_pulse('wait1-0', 'ReadoutLaser', 'readout', start = 0, duration = 5000, 
            amplitude = 0, start_reference = 'mbi_Ex', link_start_to = 'end')


        ### RRO ################################################################
        for i in range(self.par_rro_reps):
            suffix = '-%d' % (i+1); suffix_prev = '-%d' % (i)
                    
            seq.add_pulse('repump_Ex'+suffix,  'ReadoutLaser', 'readout', start =  0, duration = self.par_repump_duration,
                amplitude = self.par_repump_Ex_amplitude, start_reference = 'wait1'+suffix_prev, 
                link_start_to = 'end')

            seq.add_pulse('repump_A'+suffix,  'PumpingLaser', 'readout', start = 0, duration = 0, 
                amplitude = self.par_repump_A_amplitude,  start_reference = 'repump_Ex'+suffix,  link_start_to = 'start', 
                duration_reference = 'repump_Ex'+suffix,  link_duration_to = 'duration')

            seq.add_IQmod_pulse('selective_pi_probe'+suffix, channel=('MW_Imod','MW_Qmod'), element='readout', 
                    start = 500, duration = self.par_selective_pi, start_reference = 'repump_Ex'+suffix, 
                    link_start_to = 'end', amplitude = 1.8, frequency=self.par_probe_frequency)
            
            seq.add_pulse('probe_Ex'+suffix,  'ReadoutLaser', 'readout', start = 500, duration = self.par_probe_duration, 
                amplitude = self.par_probe_Ex_amplitude, start_reference = 'selective_pi_probe'+suffix+'-I', link_start_to = 'end')

            seq.add_pulse('probe_A'+suffix,  'PumpingLaser', 'readout', start = 0, duration = 0, 
                amplitude = self.par_probe_A_amplitude,  start_reference = 'probe_Ex'+suffix,  link_start_to = 'start', 
                duration_reference = 'probe_Ex'+suffix,  link_duration_to = 'duration')

            seq.add_pulse('start_probe'+suffix,  'PH_start', 'readout', start = -100, duration = 50, 
                start_reference = 'probe_Ex'+suffix,  link_start_to = 'start')
            
            seq.add_pulse('wait1'+suffix, 'ReadoutLaser', 'readout', start = 0, duration = 1000,
                amplitude = 0, start_reference = 'probe_Ex'+suffix, link_start_to = 'end')
        ########################################################################


        seq.add_pulse('cr_Ex', 'ReadoutLaser', 'readout', start = 1000, duration = self.par_cr_duration, 
                amplitude = self.par_cr_Ex_amplitude, start_reference = 'wait1'+suffix, link_start_to = 'end')

        seq.add_pulse('cr_A', 'PumpingLaser', 'readout', start = 0, duration = 0, 
                amplitude = self.par_cr_A_amplitude, start_reference = 'cr_Ex', link_start_to = 'start', 
                duration_reference = 'cr_Ex', link_duration_to = 'duration')

        seq.add_pulse('start_cr', 'PH_start', 'readout', start = -100, duration = 50, 
                start_reference = 'cr_Ex', link_start_to = 'start')


        seq.add_pulse('ADwin_ionization_probe', 'ADwin_sync', 'readout', start = 0, 
            duration = -20000, start_reference = 'cr_Ex', link_start_to = 'start', 
            duration_reference = 'cr_Ex', link_duration_to = 'duration')


        seq.add_element('wait_for_ADwin', trigger_wait = True, goto_target = 'initialize')
        seq.add_pulse('probe1', 'ReadoutLaser', 'wait_for_ADwin', start=0, duration = 1000, 
                amplitude = self.par_cr_Ex_amplitude)
        seq.add_pulse('probe2', 'PumpingLaser', 'wait_for_ADwin', start=-125, duration = 1000, 
                amplitude = self.par_cr_A_amplitude)


        seq.clone_channel('MW_pulsemod', 'MW_Imod', 'readout', 
            start = -MW_pulse_mod_risetime, duration = 2 * MW_pulse_mod_risetime, 
            link_start_to = 'start', link_duration_to = 'duration', amplitude = 2.0)


        seq.set_instrument(self.ins_awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        
        return True


def readoutall():

    f0 = 16.665e6
    s0 = 44.13e6
    s1 = 12.65e6
    s2 = 2.17e6

    f_probe = array([f0, f0+s2, f0+2*s2, f0+s1, f0+s1+s2, f0+s1+2*s2])
    f_probe = append(f_probe, f_probe+s0)

    #print f_probe
    #return

    m = MBIMeasurement('SIL9_firsttry_readall')
    m.setup(int(1e3), do_program=True)            

    
    for i,f in enumerate(f_probe):
        setup.Default_Settings()
        setup.set_PowerGreen(20e-6)
        
        setup.OptimizeZ()
        setup.OptimizeXY()
        setup.OptimizeZ()
        setup.OptimizeXY()

        m.par_probe_frequency = f
        m.generate_sequence()
        m.initialize()
        m.measure()

        m.dataset_idx += 1


if __name__ == "__main__":
    readoutall()

