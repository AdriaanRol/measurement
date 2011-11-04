import numpy as np
import ctypes
import inspect

from qt import instruments

from measurement.measurement import Measurement
from measurement.AWG_HW_sequencer import Sequence
import measurement.PQ_measurement_generator as pqm

# constants
MW_pulse_mod_risetime = 20

Measurement = pqm.PQ_measurement

class DarkESRMeasurement(Measurement):
    def __init__(self, name, **kw):
        Measurement.__init__(self, name, mclass='DarkESR')

        self.pipulse = 800
        
        # in this version we keep the center frequency and sweep the
        # modulation frequency
        self.f_central = 2830e6
        
        self.amplitude_mod = 1.8 
        self.power = 5.
        
        self.ins_setup = instruments['TheSetup']
        self.ins_awg = instruments['AWG']
        self.ins_pq = instruments['PH_300']
        self.ins_mw = instruments['SMB100']

    def setup(self, fstart, fstop, fsteps, reps, *arg, **kw):

        self.generate_sequence(fstart, fstop, fsteps, *arg, **kw)

        self.ins_setup.set_AOMonADwin(False)
        self.set_qtlab_counter_instrument(self.ins_pq)
        self.set_sequence_instrument(self.ins_awg)

        self.set_sweep(name='MW frequency', count=fsteps,
                incr_mode=pqm.EV_auto, reset_mode=pqm.EV_auto, 
                incr=(fstop-fstart+1)/fsteps, start = fstart)
        
        self.set_repetitions(count=reps, incr_mode=pqm.EV_auto, 
                reset_mode=pqm.EV_auto)

        self.set_loop_order(pqm.loop_repeat_sweeps) 
        self.set_section_increment_event(pqm.EV_start)
        self.set_sequence_reset_event(pqm.EV_auto)
        self.set_conditional_mode(False)

        self.add_section(name = 'SpinReadout', 
                event_type     = pqm.EV_stop, 
                binsize        = 11,
                offset         = 0,
                duration       = 200,
                mode           = pqm.sweep_axis + pqm.time_axis,
                threshold_mode = 0,
                reset_mode     = pqm.EV_auto)
        
        self.add_MW('MW', self.ins_mw, frequency=self.f,
                power=self.power, iq_modulation='on', pulse_modulation='on')
        
        self.add_ROI('readout', 'SpinReadout', 0, 61, axis=pqm.time_axis)
        self.initialize()

    def measure(self, **kw):
        self.start()
        self.save(files=[inspect.stack()[0][1], ])

    def generate_sequence(self, fstart, fstop, fsteps, do_program=True):
        seq = Sequence(self.name)
        
        # MWs
        seq.add_channel('MW_pulsemod', 'ch4m2', high=2.0, cable_delay = 120)
        seq.add_channel('MW_Imod', 'ch3', high=2.25, low=-2.25, 
                cable_delay = 120)
        seq.add_channel('MW_Qmod', 'ch4', high=2.25, low=-2.25, 
                cable_delay = 120)

        # Light
        seq.add_channel('AOM_green', 'ch2m1', cable_delay = 615, high = 1.0)

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
        
        
        # sweep the pulse length
        for i, f_mod in enumerate(np.linspace(fstart, fstop, fsteps)):
        
            ###################################################################
            # the actual rabi sequence and readout
            
            ename = 'esrseq%d' % i
            kw = {} if i < fsteps-1 else {'goto_target': 'esrseq0'}
            seq.add_element(ename, **kw)
            
            seq.add_pulse('wait_for_singlets', 'PH_start', ename, 
                duration = 1000, amplitude = 0)

            seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod', 'MW_Qmod'), 
                    element=ename, start = 0, duration = self.pipulse, 
                    start_reference = 'wait_for_singlets', 
                    link_start_to = 'end', frequency=f_mod,
                    amplitude=self.amplitude_mod)

            seq.clone_channel('MW_pulsemod', 'MW_Imod', ename, 
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                link_start_to = 'start', link_duration_to = 'duration', 
                amplitude = 2.0)

            seq.add_pulse('readout', 'AOM_green', ename, start = 500, 
                    duration = 1000, start_reference = 'mwburst-I', 
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


if __name__ == "__main__":
    m = DarkESRMeasurement('SIL9RT')
    
    m.pipulse = 848
    m.f_central = 2.830e9
    m.f = m.f_central
    m.amplitude_mod = 1.8
    m.power = 10
    
    m.setup(0, 20e6, 51, int(1e6), do_program=True)
    m.measure()
    
