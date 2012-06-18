import numpy as np
import ctypes
import inspect

from qt import instruments

from measurement.measurement import Measurement
from measurement.AWG_HW_sequencer_v2 import Sequence
import measurement.PQ_measurement_generator_v2 as pqm

from measurement.config import awgchannels as awgcfg
from measurement.sequence import common as commonseq


Measurement = pqm.PQ_measurement

class RabiMeasurement(Measurement):
    def __init__(self,name,**kw):
        Measurement.__init__(self, name, mclass='Rabi')

        
        # in this version we keep the center frequency and sweep the
        # modulation frequency
        self.f_central = 2.8779e9
        
        self.amplitude_mod = 1.8 
        self.power = 15.

        self.mode = 'SSB'
        self.amplitude_i = 0.
        self.amplitude_q = 0. 

        self.amplitude_ssbmod = 0.8
        self.f_ssbmod = 0.
                
        self.ins_awg = instruments['AWG']
        self.ins_hh = instruments['HH_400']
        self.ins_mw = instruments['SMB100']
    
        self.MW_pulse_mod_risetime = 20

    def setup(self, PLstart, PLstop, PLsteps, reps, *arg, **kw):

        self.generate_sequence(PLstart, PLstop, PLsteps, *arg, **kw)

        self.set_qtlab_counter_instrument(self.ins_hh)
        self.set_sequence_instrument(self.ins_awg)

        self.set_sweep(name='MW burst time', count=PLsteps,
                incr_mode=pqm.EV_auto, reset_mode=pqm.EV_auto, 
                incr=(PLstop-PLstart)/PLsteps+1, start = PLstart)
        
        self.set_repetitions(count=reps, incr_mode=pqm.EV_auto, 
                reset_mode=pqm.EV_auto)

        self.set_loop_order(pqm.loop_repeat_sweeps) 
        self.set_section_increment_event(pqm.EV_sync)
        self.set_sequence_reset_event(pqm.EV_auto)
        self.set_conditional_mode(False)

        self.add_section(name = 'SpinReadout', 
                event_type     = pqm.EV_start, 
                binsize        = 13,
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

        # vars for the channel names
        chan_mwpulsemod = 'MW_pulsemod'
        chan_mwI = 'MW_Imod'
        chan_mwQ = 'MW_Qmod'
        chan_green = 'AOM_Green'
        chan_hhsync = 'HH_sync'
        
        basicscfg = {'AOM_Green': {'high': 0.8}}
        awgcfg.configure_sequence(seq, 'hydraharp', 'mw', basics=basicscfg)
        
        
        # sweep the pulse length
        for i, pulselength in enumerate(np.linspace(PLstart, PLstop, PLsteps)):
        
            ###################################################################
            # the actual rabi sequence and readout
            
            print pulselength
            ename = 'rabiseq%d' % i
            kw = {} if i < PLsteps-1 else {'goto_target': 'rabiseq0'}
            seq.add_element(ename, **kw)
            
            seq.add_pulse('wait_for_singlets', chan_hhsync, ename, 
                duration = 1500, amplitude = 0)

            if self.mode == 'SSB':
                seq.add_IQmod_pulse(name='mwburst', channel=(chan_mwI,chan_mwQ), 
                        element=ename, start = 0, duration = pulselength, 
                        start_reference = 'wait_for_singlets', 
                        link_start_to = 'end', frequency=self.f_ssbmod, 
                        amplitude=1)
            
            elif self.mode == 'I+Q':
                seq.add_pulse('mwburst', chan_mwI, ename, start=0, 
                        duration=pulselength, start_reference='wait_for_singlets',
                        link_start_to = 'end', amplitude=self.amplitude_i)
                
                seq.add_pulse('mwburst', chan_mwQ, ename, start=0, 
                        duration=pulselength, start_reference='wait_for_singlets',
                        link_start_to = 'end', amplitude=self.amplitude_q)
            else:
                print 'Invalid mode for the sequence! Abort.'
                return False
            
            seq.clone_channel(chan_mwpulsemod, chan_mwI, ename,
                start=-self.MW_pulse_mod_risetime, duration=2*self.MW_pulse_mod_risetime, 
                link_start_to = 'start', link_duration_to = 'duration', 
                amplitude = 2.0)

            ref = 'mwburst' if self.mode == 'I+Q' else 'mwburst-I'
            #seq.add_pulse('readout', 'AOM_green', ename, start = 500, 
            #        duration = 1000, start_reference=ref, 
            #        link_start_to = 'end')

            seq.add_pulse('readout', chan_green, ename, start = 500+PLstop, 
                    duration = 10000, start_reference='wait_for_singlets', 
                    link_start_to = 'end')

            seq.add_pulse('start_counting', chan_hhsync, ename, start = -100, 
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
    m = RabiMeasurement('SIL8LT')
    
    m.f_central = 2.8779e9
    m.f = m.f_central
    
    #### AMPLIFIER!!!    
    m.amplitude_mod = 0.1
    
    m.power = 15
    
    m.setup(0, 3, 2, int(1e2), do_program=True)
    m.measure()
    #m.generate_sequence(0,100,21)
    print 'your mother is a rabi'
