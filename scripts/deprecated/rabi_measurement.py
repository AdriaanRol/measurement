import numpy as np
import ctypes
import inspect

from qt import instruments

from measurement.measurement import Measurement
from measurement.AWG_HW_sequencer_v2 import Sequence
import measurement.PQ_measurement_generator_v2 as pqm

Measurement = pqm.PQ_measurement

class RabiMeasurement(Measurement):
    def __init__(self,name,**kw):
        Measurement.__init__(self, name, mclass='Rabi')

        
        # in this version we keep the center frequency and sweep the
        # modulation frequency
        self.f_central = 28769e6
        
        self.amplitude_mod = 1.8 
        self.power = 15.
                
        self.ins_awg = instruments['AWG']
        self.ins_hh = instruments['HH_400']
        self.ins_mw = instruments['SMB100']
    
        self.MW_pulse_mod_risetime = 20

    def setup(self, PLstart, PLstop, PLsteps, reps, *arg, **kw):

        self.generate_sequence(PLstart, PLstop, PLsteps, *arg, **kw)

        self.set_qtlab_counter_instrument(self.ins_hh)
        self.set_sequence_instrument(self.ins_awg)

        self.set_sweep(name='MW burst duration (ns)', count=PLsteps,
                incr_mode=pqm.EV_auto, reset_mode=pqm.EV_auto, 
                incr=(PLstop-PLstart+1)/PLsteps, start = PLstart)
        
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

    def generate_sequence(self, PLstart, PLstop, PLsteps, do_program=True):
        seq = Sequence(self.name)
        
        # MWs
        seq.add_channel('MW_pulsemod', 'ch1m1', high=2.0, cable_delay = 199)
        seq.add_channel('MW_Imod', 'ch1', high=0.9, low=-0.9, 
                cable_delay = 199)
        #seq.add_channel('MW_Qmod', 'ch4', high=0.9, low=-0.9, 
        #        cable_delay = 199)

        # Light
        seq.add_channel('AOM_green', 'ch2m1', cable_delay = 604, high = 0.5)

        # PH data aquisition
        seq.add_channel('PH_start', 'ch2m2', cable_delay = 0)
        seq.add_channel('PH_MA1', 'ch3m1', cable_delay = 0, high = 2.0)

        
        #######################################################################
        # creates two start pulses to compensate 
        # for PH bug (misses first 2 start pulses)

        #ename = 'sync' 
        #seq.add_element(ename)
        
        #seq.add_pulse('PH_sync1', 'PH_start', ename, duration = 50)
        #seq.add_pulse('PH_sync2', 'PH_start', ename, start = 500, duration = 50, 
        #        start_reference = 'PH_sync1', link_start_to = 'end')
        #seq.add_pulse('PH_sync_wait', 'PH_start', ename, start = 500, 
        #        duration = 50, start_reference = 'PH_sync2', 
        #        link_start_to = 'end', amplitude = 0)
        #######################################################################
        
        
        # sweep the pulse length
        for i, pulselength in enumerate(np.linspace(PLstart, PLstop, PLsteps)):

            ###################################################################
            # the actual rabi sequence and readout
            
            ename = 'rabiseq%d' % i
            kw = {} if i < PLsteps-1 else {'goto_target': 'rabiseq0'}
            seq.add_element(ename, **kw)
            
            seq.add_pulse('wait_for_singlets', 'PH_start', ename, 
                duration = 1000, amplitude = 0)

            seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod', 'MW_Qmod'), 
                    element=ename, start = 0, duration = pulselength, 
                    start_reference = 'wait_for_singlets', 
                    link_start_to = 'end', frequency=0,
                    amplitude=self.amplitude_mod)

            seq.clone_channel('MW_pulsemod', 'MW_Imod', ename, 
                start=-self.MW_pulse_mod_risetime, duration=2*self.MW_pulse_mod_risetime, 
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
    m = RabiMeasurement('SIL1LT')
    
    m.f_central = 2.8769e9
    m.f = m.f_central
    
    #### AMPLIFIER!!!    
    m.amplitude_mod = 0.1
    
    m.power = 10
    
    m.setup(0, 100e-9, 21, int(3e3), do_program=True)
    m.measure()
    print 'your mother is a rabi'
