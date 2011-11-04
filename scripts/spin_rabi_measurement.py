import numpy as np
import ctypes
import inspect

from qt import instruments

from measurement.AWG_HW_sequencer import Sequence
import measurement.PQ_measurement_generator as pqm

# constants
MW_pulse_mod_risetime = 20

Measurement = pqm.PQ_measurement

class SpinRabiMeasurement(Measurement):
    def __init__(self, name, **kw):
        Measurement.__init__(self, name, mclass='SpinRabi', **kw)

        self.f = 2.830e9
        self.power = 5.
        
        # two modes:
        # - 'I+Q' makes two square pulses with independent amplitudes
        # - 'SSB' (single side band) does an image rejection modulation
        #   on the I and Q channels via the AWG, with modulation frq f_ssbmod
        #   and amplitude amplitude_ssbmod
        self.mode = 'I+Q'
        self.amplitude_i = 1.8
        self.amplitude_q = 0. 

        self.amplitude_ssbmod = 1.8
        self.f_ssbmod = 0.

        # setup specific instruments
        self.ins_setup = instruments['TheSetup']
        self.ins_awg = instruments['AWG']
        self.ins_pq = instruments['PH_300']
        self.ins_mw = instruments['SMB100']

    def setup(self, lstart, lstop, lsteps, reps, *arg, **kw):
        self.reset()

        if not self.generate_sequence(lstart, lstop, lsteps, *arg, **kw):
            return False

        self.ins_setup.set_AOMonADwin(False)
        self.set_qtlab_counter_instrument(self.ins_pq)
        self.set_sequence_instrument(self.ins_awg)

        self.set_sweep(name='MW burst duration', count=lsteps,
                incr_mode=pqm.EV_auto, reset_mode=pqm.EV_auto, 
                incr=(lstop-lstart+1)/lsteps, start = lstart)
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

        return True

    def measure(self, **kw):
        self.start()
        self.save(files=[inspect.stack()[0][1], ])

    def generate_sequence(self, lstart, lstop, lsteps, do_program=True):
        seq = Sequence(self.name)
        
        # MWs
        seq.add_channel('MW_pulsemod', 'ch4m2', high=2.0, cable_delay = 120)
        seq.add_channel('MW_Imod', 'ch3', high=2.25, low=-2.25, 
                cable_delay = 120)
        seq.add_channel('MW_Qmod', 'ch4', high=2.25, low=-2.25, 
                cable_delay = 120)

        # Light
        seq.add_channel('AOM_green', 'ch2m1', cable_delay = 615, high = 0.5)

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
        for i, pulselength in enumerate(np.linspace(lstart, lstop, lsteps)):
        
            ###################################################################
            # the actual rabi sequence and readout
            
            ename = 'rabiseq%d' % i
            kw = {} if i < lsteps-1 else {'goto_target': 'rabiseq0'}
            seq.add_element(ename, **kw)
            
            seq.add_pulse('wait_for_singlets', 'PH_start', ename, 
                duration = 1500, amplitude = 0)

            if self.mode == 'SSB':
                seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod', 'MW_Qmod'), 
                        element=ename, start = 0, duration = pulselength, 
                        start_reference = 'wait_for_singlets', 
                        link_start_to = 'end', frequency=self.f_ssbmod, 
                        amplitude=self.amplitude_ssbmod)
            
            elif self.mode == 'I+Q':
                seq.add_pulse('mwburst', 'MW_Imod', ename, start=0, 
                        duration=pulselength, start_reference='wait_for_singlets',
                        link_start_to = 'end', amplitude=self.amplitude_i)
                
                seq.add_pulse('mwburst', 'MW_Qmod', ename, start=0, 
                        duration=pulselength, start_reference='wait_for_singlets',
                        link_start_to = 'end', amplitude=self.amplitude_q)
            else:
                print 'Invalid mode for the sequence! Abort.'
                return False
            
            seq.clone_channel('MW_pulsemod', 'MW_Imod', ename, 
                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime, 
                link_start_to = 'start', link_duration_to = 'duration', 
                amplitude = 2.0)

            ref = 'mwburst' if self.mode == 'I+Q' else 'mwburst-I'
            #seq.add_pulse('readout', 'AOM_green', ename, start = 500, 
            #        duration = 1000, start_reference=ref, 
            #        link_start_to = 'end')

            seq.add_pulse('readout', 'AOM_green', ename, start = 500+lstop, 
                    duration = 1000, start_reference='wait_for_singlets', 
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


def rabi_vs_ssb_frq():
    setup = instruments['TheSetup']
    smb = instruments['SMB100']
    
    f0 = array([2838e6])
    fmod = array([1.634e6])
    for i in range(20):
        f0 = append(f0, f0[0] - (i+1)*5e6)
        fmod = append(fmod, fmod[0] + (i+1)*5e6)

    # print f0, fmod
    # return

    m = SpinRabiMeasurement('SIL9RT_fmod_sweep')    

    for i,f in enumerate(f0):
        setup.Default_Settings()
        setup.set_AOMonADwin(True)
        setup.set_PowerGreen(20e-6)
        
        setup.OptimizeZ()
        setup.OptimizeXY()
        setup.OptimizeZ()
        setup.OptimizeXY()

        setup.set_AOMonADwin(False)

        m.f = f
        m.mode = 'SSB'

        m.amplitude_ssbmod = 1.8
        m.f_ssbmod = fmod[i]
        m.power = 10

        ## calibrate source
        smb.set_frequency(f)
        smb.set_power(10)
        smb.perform_internal_adjustments()
        
        m.setup(100., 2600., 26, int(1e6), do_program=True)
        m.measure()

        m.dataset_idx += 1



def simplerabi():
    m = SpinRabiMeasurement('SIL9RT')
    
    m.f = 2.838e9
    m.mode = 'SSB'
    
    m.amplitude_ssbmod = 1.8
    m.f_ssbmod = 1.634e6

    #m.amplitude_i = 0. #1.8
    #m.amplitude_q = 1.8 #1.8

    m.power = 10
    if m.setup(100., 10100., 101, int(1e6), do_program=True):
       m.measure()


if __name__ == "__main__": 
    simplerabi()
    # rabi_vs_ssb_frq()

