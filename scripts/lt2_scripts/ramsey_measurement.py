import numpy as np
import ctypes

from qt import instruments

from measurement.measurement import Measurement
from measurement.AWG_HW_sequencer import Sequence
import measurement.oldschool.PH_measurement_generator as pqm

# constants
MW_pulse_mod_risetime = 20

class RamseyMeasurementIQ(Measurement):
    def __init__(self, name, **kw):
        Measurement.__init__(self, 'RamseyIQ_'+name)

        self.f = 2.87925e9
        self.power = 5.
        
        # two modes:
        # - 'I+Q' makes two square pulses with independent amplitudes
        # - 'SSB' (single side band) does an image rejection modulation
        #   on the I and Q channels via the AWG, with modulation frq f_ssbmod
        #   and amplitude amplitude_ssbmod
        self.mode = 'I+Q'
        self.amplitude_i = 2.25
        self.amplitude_q = 2.25
        self.pi_2_duration = 25

        self.amplitude_ssbmod = 2.25
        self.f_ssbmod = 0.

        self.pq_dll = ctypes.windll.LoadLibrary(
                'd:/qtlab_cyclops/lt_scripts/tttr_nextgen.dll')
        
        self.ins_setup = instruments['TheSetup']
        self.ins_awg = instruments['AWG']
        self.ins_pq = instruments['PH_300']
        self.ins_mw = instruments['SMB100']

        self.ins_mw.set_iq('on')
        self.ins_mw.set_pulm('on')


    def setup(self, lstart, lstop, lsteps, reps, *arg, **kw):

        if not self.generate_sequence(lstart, lstop, lsteps, *arg, **kw):
            return False

        self.ins_setup.set_AOMonADwin(False)

        self.m = pqm.PH_measurement(self.name)
        self.m.set_counter_instrument(self.pq_dll)
        self.m.set_qtlab_counter_instrument(self.ins_pq)
        self.m.set_sequence_instrument(self.ins_awg)

        self.m.set_sweep(name='Ramsey wait time', count=lsteps,
                incr_mode=pqm.EV_auto, reset_mode=pqm.EV_auto, 
                incr=(lstop-lstart+1)/lsteps, start = lstart)
        self.m.set_repetitions(count=reps, incr_mode=pqm.EV_auto, 
                reset_mode=pqm.EV_auto)

        self.m.set_loop_order(pqm.loop_repeat_sweeps) 
        self.m.set_section_increment_event(pqm.EV_PH_start)
        self.m.set_section_reset_event(pqm.EV_auto)
        self.m.set_conditional_mode(False)

        self.m.add_section(name = 'SpinReadout', 
                event_type     = pqm.EV_PH_stop, 
                binsize        = 11,
                offset         = 0,
                duration       = 200,
                mode           = pqm.sweep_axis + pqm.time_axis,
                threshold      = -1,
                threshold_mode = -1,
                reset_mode     = pqm.EV_auto)
        self.m.add_MW('MW', self.ins_mw, frequency=self.f,
                power=self.power)

        self.m.add_ROI('readout', 'SpinReadout', 0, 61, axis=pqm.time_axis)
        self.m.initialize()

        return True

    def measure(self, **kw):
        self.m.start()
        self.m.save_data('SpinReadout', saveplot=True)

    def generate_sequence(self, lstart, lstop, lsteps, do_program=True):
        seq = Sequence(self.name)
        
        # MWs
        seq.add_channel('MW_pulsemod', 'ch4m2', high=2.0, cable_delay = 120)
        seq.add_channel('MW_Imod', 'ch3', high=2.25, low=-2.25, 
                cable_delay = 120)
        seq.add_channel('MW_Qmod', 'ch4', high=2.25, low=-2.25, 
                cable_delay = 120)

        # Light
        seq.add_channel('AOM_green', 'ch2m1', cable_delay = 623-50, high = 1.0)

        # PH data aquisition
        seq.add_channel('PH_start', 'ch2m2', cable_delay = 0)
        seq.add_channel('PH_MA1', 'ch3m1', cable_delay = 0, high = 2.0)

        
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
        
        
        # sweep the wait time
        for i, waittime in enumerate(np.linspace(lstart, lstop, lsteps)):
        
            ###################################################################
            # the actual rabi sequence and readout
            
            ename = 'ramseyseq%d' % i
            kw = {} if i < lsteps-1 else {'goto_target': 'ramseyseq0'}
            seq.add_element(ename, **kw)
            
            seq.add_pulse('wait_for_singlets', 'PH_start', ename, 
                duration = 1500, amplitude = 0)

            if self.mode == 'SSB':
                seq.add_IQmod_pulse(name='mwburst_1', channel=('MW_Imod', 'MW_Qmod'), 
                        element=ename, start = 0, duration = self.pi_2_duration, 
                        start_reference = 'wait_for_singlets', 
                        link_start_to = 'end', frequency=self.f_mod, 
                        amplitude=self.amplitude_mod)
                seq.add_pulse('ramsey_wait', 'PH_start', ename, 
                    duration = waittime, amplitude = 0, start = 0, 
                    link_start_to = 'end', start_reference = 'mwburst_1')
                seq.add_IQmod_pulse(name='mwburst_2', channel=('MW_Imod', 'MW_Qmod'), 
                        element=ename, start = 0, duration = self.pi_2_duration, 
                        start_reference = 'ramsey_wait', 
                        link_start_to = 'end', frequency=self.f_mod, 
                        amplitude=self.amplitude_mod)
            
            elif self.mode == 'I+Q':
                seq.add_pulse('mwburst_1', 'MW_Imod', ename, start=0, 
                        duration=self.pi_2_duration, start_reference='wait_for_singlets',
                        link_start_to = 'end', amplitude=self.amplitude_i)
                
                seq.add_pulse('mwburst_q_1', 'MW_Qmod', ename, start=0, 
                        duration=self.pi_2_duration, start_reference='wait_for_singlets',
                        link_start_to = 'end', amplitude=self.amplitude_q)

                seq.add_pulse('ramsey_wait', 'PH_start', ename, 
                    duration = waittime, amplitude = 0, start = 0, 
                    link_start_to = 'end', start_reference = 'mwburst_1')

                seq.add_pulse('mwburst_2', 'MW_Imod', ename, start=0, 
                        duration=self.pi_2_duration, 
                        start_reference='ramsey_wait', link_start_to = 'end', 
                        amplitude=self.amplitude_i)
                
                seq.add_pulse('mwburst_q_2', 'MW_Qmod', ename, start=0, 
                        duration=self.pi_2_duration, 
                        start_reference='ramsey_wait', link_start_to = 'end', 
                        amplitude=self.amplitude_q)
            else:
                print 'Invalid mode for the sequence! Abort.'
                return False
            
            seq.clone_channel('MW_pulsemod', 'MW_Imod', ename, 
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                link_start_to = 'start', link_duration_to = 'duration', 
                amplitude = 2.0)

            seq.add_pulse('readout', 'AOM_green', ename, start = 500, 
                    duration = 1000, start_reference = 'mwburst_2', 
                    link_start_to = 'end')

            seq.add_pulse('start_counting', 'PH_start', ename, start = -100, 
                    duration = 50, start_reference = 'readout', 
                    link_start_to = 'start')
            ###################################################################
        
        seq.set_instrument(self.ins_awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        
        return True


if __name__ == "__main__":
    m = RamseyMeasurementIQ('SIL2RT')
    
    m.f = 2.871e9
    m.mode = 'I+Q'
    m.amplitude_i = 2.25
    m.amplitude_q = 0
    m.pi_2_duration = 15

    m.power = 0
    if m.setup(10, 2000., 200, int(1e3), do_program=True):
       m.measure() 

    
